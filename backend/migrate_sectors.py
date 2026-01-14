"""
Migration script to populate the 'sector' field for all existing properties.
This should be run once after adding the sector column to the database.
"""
import json
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Property, Base
from neighborhood_utils import auto_resolve_neighborhood

def load_neighborhood_map():
    """Load the neighborhood mapping from JSON file"""
    try:
        with open("neighborhood_map.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading neighborhood map: {e}")
        return {}

def migrate_sectors():
    """Populate sector field for all existing properties"""
    # Create tables if they don't exist (adds new column)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    nb_map = load_neighborhood_map()
    
    try:
        # Get all properties
        properties = db.query(Property).all()
        total = len(properties)
        updated = 0
        unclassified = 0
        
        print(f"Processing {total} properties...")
        
        for i, prop in enumerate(properties, 1):
            if i % 100 == 0:
                print(f"Progress: {i}/{total}")
            
            # Try to resolve sector from location first
            sector = auto_resolve_neighborhood(prop.location or "", nb_map)
            
            # If not found, try from title
            if not sector:
                sector = auto_resolve_neighborhood(prop.title or "", nb_map)
            
            # Assign "Sin Clasificar" if no match found
            if not sector:
                sector = "Sin Clasificar"
                unclassified += 1
            
            prop.sector = sector
            updated += 1
        
        # Commit all changes
        db.commit()
        print(f"\n✅ Migration complete!")
        print(f"   Total properties: {total}")
        print(f"   Updated: {updated}")
        print(f"   Unclassified: {unclassified}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_sectors()
