from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from database import engine, Base, get_db
from models import Property
from tasks import scrape_portal_task

app = FastAPI(title="Medellín Real Estate Monitor")

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
    db: Session = Depends(get_db)
):
    query = db.query(Property)
    if source:
        query = query.filter(Property.source == source)
    
    # Order by active and then newest
    properties = query.order_by(Property.created_at.desc()).offset(skip).limit(limit).all()
    return properties

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
