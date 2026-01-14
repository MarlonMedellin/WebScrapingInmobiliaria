from fastapi import FastAPI, Depends, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
import json

from database import engine, Base, get_db
from models import Property, SavedSearch
from tasks import scrape_portal_task

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Medellín Real Estate Monitor")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Pydantic Models
class PropertyStatusUpdate(BaseModel):
    status: str

class SavedSearchCreate(BaseModel):
    name: str
    criteria: dict

class SavedSearchOut(BaseModel):
    id: int
    name: str
    criteria: dict
    
import os

# CORS Configuration
# Important: allow_origins cannot be ["*"] when allow_credentials is True
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
origins = [o.strip() for o in allowed_origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Security
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security

API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY", "dev-secret-key")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(header_value: str = Security(api_key_header)):
    if header_value == API_KEY:
        return header_value
    raise HTTPException(
        status_code=403, 
        detail="Could not validate credentials. Please provide a valid X-API-Key header."
    )

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Medellín Real Estate Monitor API is running"}

@app.get("/properties")
def get_properties(
    skip: int = 0, 
    limit: int = 500, 
    source: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_area: Optional[float] = None,
    max_area: Optional[float] = None,
    search: Optional[str] = None,
    neighborhood: Optional[str] = None,
    show_archived: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Property)
    
    # 0. Status Filter (Default: Hide Archived)
    if not show_archived:
        query = query.filter(Property.status != 'ARCHIVED')

    # 1. Source Filter
    if source:
        query = query.filter(Property.source == source)
    
    # 2. Price Range Filter
    if min_price is not None:
        query = query.filter(Property.price >= min_price)
    if max_price is not None:
        query = query.filter(Property.price <= max_price)

    # 3. Area Range Filter (ignore 0 or nulls if needed, but simple filter for now)
    if min_area is not None:
        query = query.filter(Property.area >= min_area)
    if max_area is not None:
        query = query.filter(Property.area <= max_area)

    # 4. Neighborhood Mapping Filter
    if neighborhood:
        # Cargar mapeo
        map_path = "neighborhood_map.json"
        try:
            with open(map_path, "r", encoding="utf-8") as f:
                nb_map = json.load(f)
            
            variants = nb_map.get(neighborhood, [neighborhood])
            # Crear filtros OR para cada variante buscando tanto en location como en title
            nb_filters = []
            for v in variants:
                nb_filters.append(Property.location.ilike(f"%{v}%"))
                nb_filters.append(Property.title.ilike(f"%{v}%"))
            
            query = query.filter(or_(*nb_filters))
        except Exception as e:
            print(f"Error filtering neighborhood: {e}")

    # 5. Text Search (Title or Location)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Property.title.ilike(search_term),
                Property.location.ilike(search_term),
                Property.description.ilike(search_term)
            )
        )
    
    # Order by status logic (NEW first), then date
    # Ideally: NEW/SEEN -> Date
    properties = query.order_by(Property.created_at.desc()).offset(skip).limit(limit).all()
    
    # Enrich with days_active and neighborhood_normalized
    from datetime import datetime, timezone
    from neighborhood_utils import auto_resolve_neighborhood
    
    # Load map once per request (or optimize to global)
    nb_map = {}
    try:
        with open("neighborhood_map.json", "r", encoding="utf-8") as f:
            nb_map = json.load(f)
    except:
        pass

    now = datetime.now(timezone.utc)
    
    results = []
    for p in properties:
        # Convert to dict to append extra fields
        # Using __dict__ copy to avoid SqlAlchemy state issues, but omitting internal SA state
        p_dict = {c.name: getattr(p, c.name) for c in p.__table__.columns}
        
        # Computed fields
        created_at = p.created_at
        if created_at.tzinfo is None:
             created_at = created_at.replace(tzinfo=timezone.utc)
             
        p_dict['days_active'] = (now - created_at).days if created_at else 0
        
        # Normalize Neighborhood
        # Try to resolve based on existing location string or title
        raw_loc = p.location or ""
        raw_title = p.title or ""
        resolved = auto_resolve_neighborhood(raw_loc, nb_map)
        if not resolved:
             resolved = auto_resolve_neighborhood(raw_title, nb_map)
             
        p_dict['neighborhood_normalized'] = resolved
        
        results.append(p_dict)
        
    return results

@app.get("/neighborhoods")
def get_neighborhood_map():
    """Retorna el mapeo de barrios para el dropdown del frontend."""
    try:
        with open("neighborhood_map.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

@app.get("/neighborhoods/discovered")
def get_discovered_neighborhoods():
    """Retorna la lista de barrios descubiertos por los scrapers."""
    try:
        with open("discovered_neighborhoods.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

@app.put("/properties/{property_id}/status")
def update_property_status(
    property_id: int, 
    status_update: PropertyStatusUpdate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Valid statuses
    valid_statuses = ["NEW", "SEEN", "ARCHIVED", "FAVORITE"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    prop.status = status_update.status
    db.commit()
    return {"id": prop.id, "status": prop.status}

# --- SAVED SEARCHES ---

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Returns total property counts grouped by source.
    """
    from sqlalchemy import func
    results = db.query(Property.source, func.count(Property.id)).group_by(Property.source).all()
    
    total = sum(count for source, count in results)
    by_source = {source: count for source, count in results if source}
    
    return {
        "total": total,
        "by_source": by_source
    }

@app.get("/saved_searches", response_model=List[SavedSearchOut])
def get_searches(db: Session = Depends(get_db)):
    searches = db.query(SavedSearch).all()
    # Parse JSON criteria for response
    results = []
    for s in searches:
        try:
            criteria_dict = json.loads(s.criteria)
        except:
            criteria_dict = {}
        results.append(SavedSearchOut(id=s.id, name=s.name, criteria=criteria_dict))
    return results

@app.post("/searches")
def create_search(
    search: SavedSearchCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    criteria_json = json.dumps(search.criteria)
    db_search = SavedSearch(name=search.name, criteria=criteria_json)
    db.add(db_search)
    db.commit()
    db.refresh(db_search)
    return {"id": db_search.id, "message": "Search saved"}

@app.delete("/searches/{search_id}")
def delete_search(
    search_id: int, 
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    db_search = db.query(SavedSearch).filter(SavedSearch.id == search_id).first()
    if not db_search:
        raise HTTPException(status_code=404, detail="Search not found")
    db.delete(db_search)
    db.commit()
    return {"message": "Search deleted"}

@app.post("/scrape/{portal_key}")
@limiter.limit("5/minute")
def trigger_scrape(
    request: Request,
    portal_key: str,
    api_key: str = Depends(get_api_key)
):
    # Valid portals
    valid_portals = ["fincaraiz", "elcastillo", "santafe", "panda", "integridad", "protebienes", "lacastellana", "monserrate", "aportal", "escalainmobiliaria", "suvivienda", "portofino", "nutibara", "laaldea", "ayura", "albertoalvarez", "conquistadores"]
    if portal_key not in valid_portals:

        raise HTTPException(status_code=400, detail="Portal not supported")
    
    task = scrape_portal_task.delay(portal_key)
    return {"message": f"Scraping started for {portal_key}", "task_id": task.id}

@app.on_event("startup")
def startup():
    pass
