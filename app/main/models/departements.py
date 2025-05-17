from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime,Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum



class Department(Base):

    __tablename__ = "departments"

    uuid = Column(String, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    description = Column(String,nullable=True,index=True)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    phone_number2 = Column(String, nullable=False)

    created_by = Column(String, ForeignKey('users.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=True)
    creator = relationship("User", foreign_keys=[created_by])

    responsable_uuid = Column(String,ForeignKey("responsables.uuid",ondelete="CASCADE",onupdate="CASCADE"),nullable=True)
    responsable = relationship("Responsable",foreign_keys=[responsable_uuid])

    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp
    

   
   

class Responsable(Base):
    __tablename__ = "responsables"
    uuid = Column(String, primary_key=True, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp
    created_by = Column(String, ForeignKey('users.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=True)
    creator = relationship("User", foreign_keys=[created_by])

    
