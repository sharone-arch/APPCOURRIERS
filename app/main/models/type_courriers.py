from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime,Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum


class TypeCourriers(Base):
    __tablename__ = "type_couriers"

    uuid = Column(String, primary_key=True, unique=True)
    name = Column(String, nullable=False)

    created_by: str = Column(String, ForeignKey('users.uuid'), nullable=True)
    creator = relationship("User", foreign_keys=[created_by], uselist=False)

    is_deleted = Column(Boolean, default=False)
    

    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp
    