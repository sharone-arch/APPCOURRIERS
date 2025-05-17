from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime,Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum


class CanauxReceptionCourier(Base):

    __tablename__ = "canaux_receptions"

    uuid = Column(String, primary_key=True,index=True, unique=True)
    name = Column(String, nullable=False)

    added_by = Column(String, ForeignKey("users.uuid"), nullable=False)
    creator = relationship("User", foreign_keys=[added_by])

    is_deleted = Column(Boolean, default=False)  # Soft delete flag
    

    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp
   