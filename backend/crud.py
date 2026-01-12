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

def archive_stale_properties(db: Session, days: int = 3):
    """
    Mark properties as ARCHIVED if they haven't been seen in the last X days.
    """
    threshold = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
    
    # Update status to ARCHIVED for properties older than threshold
    # that are not already archived.
    count = db.query(Property).filter(
        Property.last_seen < threshold,
        Property.status != 'ARCHIVED'
    ).update(
        {Property.status: 'ARCHIVED', Property.active: False}, 
        synchronize_session=False
    )
    
    db.commit()
    return count
