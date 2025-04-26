from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime,Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum



class Sender(Base):

    __tablename__ = "senders"

    uuid = Column(String,primary_key=True,index=True)
    first_name = Column(String,nullable=False,index=True)
    last_name = Column(String,nullable=False,index=True)
    phone_number = Column(String,nullable=False,index=True)
    email = Column(String,nullable=False,index=True)
    second_phone_number = Column(String,nullable=True,index=True)
    address = Column(String,nullable=False,index=True)

    avatar_uuid = Column(String,ForeignKey("storages.uuid",ondelete="CASCADE",onupdate="CASCADE"),nullable=True)
    avatar = relationship("Storage",foreign_keys=[avatar_uuid])
    
    added_by = Column(String, ForeignKey("users.uuid",ondelete="CASCADE",onupdate="CASCADE"), nullable=False)
    creator = relationship("User", foreign_keys=[added_by])
    
    is_active = Column(Boolean,default=True)
    is_deleted = Column(Boolean,default=False)
    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp
   