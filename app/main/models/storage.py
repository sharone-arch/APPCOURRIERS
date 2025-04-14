from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy import event
from app.main.models.db.base_class import Base
@dataclass
class Storage(Base):
    
    """ Storage Model for storing file related details in database"""

    __tablename__ = "storages"

    uuid: str = Column(String, primary_key=True, unique=True)
    file_name: str = Column(Text, default="", nullable=True)
    summary: Text = Column(Text, default="", nullable=True)
    cloudinary_file_name: str = Column(Text, default="", nullable=True)
    url: str = Column(Text, default="", nullable=True)
    mimetype: str = Column(Text, default="", nullable=True)
    format: str = Column(Text, default="", nullable=True)
    public_id: str = Column(Text, default="", nullable=True)
    version: int = Column(Integer, nullable=True)
    width: int = Column(Integer, default=0, nullable=True)
    height: int = Column(Integer, default=0, nullable=True)
    size: int = Column(Integer, default=0, nullable=True)
    thumbnail: any = Column(JSONB, default={}, nullable=True)
    medium: any = Column(JSONB, default={}, nullable=True)
    date_added: any = Column(DateTime, server_default=func.now())
    date_modified: any = Column(DateTime, server_default=func.now(), onupdate=func.now())


