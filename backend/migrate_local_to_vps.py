import os
import sys

# Ensure backend directory is in sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import engine, SessionLocal
from models import Property
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

def migrate_data():
    # 1. Connect to LOCAL DB (Source)
    local_url = "postgresql://admin:secret@localhost:5432/realestate_db"
    local_engine = create_engine(local_url)
    LocalSession = sessionmaker(bind=local_engine)
    local_db = LocalSession()

    # 2. Connect to VPS DB (Target via tunnel)
    vps_url = "postgresql://admin:secret@localhost:5433/realestate_db"
    vps_engine = create_engine(vps_url)
    VpsSession = sessionmaker(bind=vps_engine)
    vps_db = VpsSession()

    try:
        # Fetch local monserrate properties
        print("Reading properties from LOCAL database...")
        local_properties = local_db.query(Property).filter(Property.source == "monserrate").all()
        print(f"Found {len(local_properties)} properties in local DB.")

        new_count = 0
        updated_count = 0

        for lp in local_properties:
            # Check if exists in VPS
            exists = vps_db.query(Property).filter(Property.link == lp.link).first()
            
            # Prepare data (exclude id which is serial)
            data = {c.name: getattr(lp, c.name) for c in Property.__table__.columns if c.name != 'id'}

            if exists:
                # Update existing on VPS
                for key, value in data.items():
                    setattr(exists, key, value)
                updated_count += 1
            else:
                # Create NEW on VPS
                new_prop = Property(**data)
                vps_db.add(new_prop)
                new_count += 1

        vps_db.commit()
        print(f"Migration completed:")
        print(f"  - New properties added: {new_count}")
        print(f"  - Existing properties updated: {updated_count}")

    except Exception as e:
        print(f"ERROR during migration: {e}")
        vps_db.rollback()
    finally:
        local_db.close()
        vps_db.close()

if __name__ == "__main__":
    migrate_data()
