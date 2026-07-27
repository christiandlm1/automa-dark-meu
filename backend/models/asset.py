from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True) # image_background, video_background, logo, font, music
    category = Column(String, index=True)
    file_path = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    
    usage_count = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False)
    tags = Column(JSON, default=list)
    file_hash = Column(String, unique=True, index=True) # xxhash for duplicate prevention
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
