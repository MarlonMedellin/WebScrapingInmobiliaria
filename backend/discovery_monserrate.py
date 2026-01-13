import os
import sys

# Ensure backend directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Property

def check_db():
    db = SessionLocal()
    try:
        properties = db.query(Property).filter(Property.source == "monserrate").limit(20).all()
        print(f"Found {len(properties)} properties from monserrate.")
        for p in properties:
            print(f"ID: {p.id} | Title: {p.title}")
            print(f"  Link: {p.link}")
            print(f"  Area: {p.area} | Beds: {p.bedrooms} | Baths: {p.bathrooms}")
            print("-" * 40)
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure we connect to localhost:5433
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_PORT"] = "5433"
    check_db()
