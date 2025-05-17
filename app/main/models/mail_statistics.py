from dataclasses import dataclass
from sqlite3 import Date
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Text, DateTime, Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum


class StatistiquesAutomatiques(Base):

    __tablename__ = "mail_statistics"

    uuid = Column(String, primary_key=True, index=True)
    mail_uuid = Column(String, ForeignKey("mails.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    mail = relationship("Mail", foreign_keys=[mail_uuid])

    processing_time = Column(Integer, nullable=True, default=0)
    status_log = Column(JSON, nullable=True)  # Historique de statut au format JSON
    generated_at = Column(DateTime, nullable=True)  # Date de génération

    added_by = Column(String, ForeignKey("users.uuid"), nullable=False)
    creator = relationship("User", foreign_keys=[added_by])

    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())  # Date de création
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Dernière mise à jour