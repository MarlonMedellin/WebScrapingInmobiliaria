from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from database import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    price = Column(Float, nullable=True) # Using Float for flexibility, or BigInteger
    location = Column(String, nullable=True)
    link = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # New fields
    area = Column(Float, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    
    # Metadata for tracking
    source = Column(String, default="fincaraiz")
    external_id = Column(String, nullable=True) # ID from the portal
    image_url = Column(String, nullable=True)

    
    # Tracking prices and status
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Property(id={self.id}, title={self.title}, price={self.price})>"
