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


class TransmissionsCourriers(Base):

    __tablename__ = "mail_transmissions"

    uuid = Column(String, primary_key=True, index=True)
    mail_uuid = Column(String, ForeignKey("mails.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    mail = relationship("Mail", foreign_keys=[mail_uuid])

    from_entity_uuid = Column(String, ForeignKey("users.uuid"), nullable=True)
    from_entity = relationship("User", foreign_keys=[from_entity_uuid])

    to_entity_uuid = Column(String, ForeignKey("externes.uuid"), nullable=True)
    to_entity = relationship("Externe", foreign_keys=[to_entity_uuid])

    transmitted_by_uuid = Column(String, ForeignKey("users.uuid"), nullable=True)
    transmitted_by = relationship("User", foreign_keys=[transmitted_by_uuid])

    transmitted_at = Column(DateTime, default=func.now())

    

    note = Column(String,nullable=True)
    is_deleted = Column(Boolean,default=False)
    created_at = Column(DateTime, default=func.now())  # Date de création de l'enregistrement
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Date de la dernière mise à jour