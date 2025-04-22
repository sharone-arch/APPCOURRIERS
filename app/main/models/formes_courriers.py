from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime,Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum


class FormesCourier(Base):
    __tablename__ = "formes_couriers"

    uuid = Column(String, primary_key=True, unique=True)
    name = Column(String, nullable=False)

    created_by = Column(String, ForeignKey('users.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=True)
    creator = relationship("User", foreign_keys=[created_by], uselist=False)
    is_deleted = Column(Boolean, default=False)
    

    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp
    