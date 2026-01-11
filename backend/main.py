from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
import json

from database import engine, Base, get_db
from models import Property, SavedSearch
from tasks import scrape_portal_task

app = FastAPI(title="Medellín Real Estate Monitor")

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
    
# CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*" # For dev simplicity
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Medellín Real Estate Monitor API is running"}

@app.get("/properties")
def get_properties(
    skip: int = 0, 
    limit: int = 100, 
    source: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_area: Optional[float] = None,
    max_area: Optional[float] = None,
    search: Optional[str] = None,
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

    # 4. Text Search (Title or Location)
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
    return properties

@app.put("/properties/{property_id}/status")
def update_property_status(property_id: int, status_update: PropertyStatusUpdate, db: Session = Depends(get_db)):
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

@app.get("/searches", response_model=List[SavedSearchOut])
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
def create_search(search: SavedSearchCreate, db: Session = Depends(get_db)):
    criteria_json = json.dumps(search.criteria)
    db_search = SavedSearch(name=search.name, criteria=criteria_json)
    db.add(db_search)
    db.commit()
    db.refresh(db_search)
    return {"id": db_search.id, "message": "Search saved"}

@app.delete("/searches/{search_id}")
def delete_search(search_id: int, db: Session = Depends(get_db)):
    db_search = db.query(SavedSearch).filter(SavedSearch.id == search_id).first()
    if not db_search:
        raise HTTPException(status_code=404, detail="Search not found")
    db.delete(db_search)
    db.commit()
    return {"message": "Search deleted"}

@app.post("/scrape/{portal_key}")
def trigger_scrape(portal_key: str):
    # Valid portals
    valid_portals = ["fincaraiz", "elcastillo", "santafe", "panda", "integridad", "protebienes", "lacastellana", "monserrate", "aportal"]
    if portal_key not in valid_portals:

        raise HTTPException(status_code=400, detail="Portal not supported")
    
    task = scrape_portal_task.delay(portal_key)
    return {"message": f"Scraping started for {portal_key}", "task_id": task.id}

@app.on_event("startup")
def startup():
    pass
