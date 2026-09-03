from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

Base = declarative_base()

class Watchlist(Base):
    __tablename__ = "watchlists"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False) # e.g. STOLEN_VEHICLE
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    entries = relationship("WatchlistEntry", back_populates="watchlist")

class WatchlistEntry(Base):
    __tablename__ = "watchlist_entries"
    id = Column(String, primary_key=True, default=generate_uuid)
    watchlist_id = Column(String, ForeignKey("watchlists.id"))
    entity_type = Column(String(50), default="VEHICLE")
    entity_value = Column(String(255), nullable=False) # License plate
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    watchlist = relationship("Watchlist", back_populates="entries")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True, default=generate_uuid)
    camera_id = Column(String) # We keep it as string for simplicity if camera UUIDs aren't strictly enforced in fallback
    watchlist_entry_id = Column(String, ForeignKey("watchlist_entries.id"))
    alert_type = Column(String(100), nullable=False)
    priority = Column(String(50), default="MEDIUM")
    status = Column(String(50), default="NEW") # NEW, ACKNOWLEDGED, RESOLVED
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    description = Column(Text)
    
    # Store evidence payload directly in alert for easy retrieval
    evidence = Column(JSON) 
    
    watchlist_entry = relationship("WatchlistEntry")
