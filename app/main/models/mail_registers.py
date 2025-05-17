from dataclasses import dataclass
from sqlite3 import Date
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum


class RegisterType(str,Enum):
    ARRIVEE = "ARRIVEE"
    DEPART = "DEPART"

class RegistresCourriers(Base):
    __tablename__ = "mail_registers"

    uuid = Column(String, primary_key=True, index=True)
    mail_uuid = Column(String, ForeignKey("mails.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    mail = relationship("Mail", foreign_keys=[mail_uuid])

    register_type = Column(String,default=RegisterType.ARRIVEE,nullable=True)
    number = Column(String,nullable=True)

    added_by = Column(String, ForeignKey("users.uuid"), nullable=False)
    creator = relationship("User", foreign_keys=[added_by])

    is_deleted = Column(Boolean,default=False)
    created_at = Column(DateTime, default=func.now())  # Date de création de l'enregistrement
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Date de la dernière mise à jour