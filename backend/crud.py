from sqlalchemy.orm import Session
from models import Property
import datetime

def get_property_by_link(db: Session, link: str):
    return db.query(Property).filter(Property.link == link).first()

def create_property(db: Session, data: dict):
    db_property = Property(**data)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

def update_property_last_seen(db: Session, db_property: Property):
    db_property.last_seen = datetime.datetime.now(datetime.timezone.utc)
    db_property.active = True
    db.commit()
    db.refresh(db_property)

def update_property_price(db: Session, db_property: Property, new_price: str):
    # Here we could implement history tracking in another table if needed.
    # For now, just update.
    if db_property.price != new_price:
        # TODO: Log price change?
        db_property.price = new_price
    db.commit()
