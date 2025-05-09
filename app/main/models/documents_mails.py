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


class MailDocument(Base):
    __tablename__ = "mail_documents"

    uuid = Column(String, primary_key=True, index=True)

    mail_uuid = Column(String, ForeignKey("mails.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    mail = relationship("Mail", foreign_keys=[mail_uuid])
    document_uuid = Column(String, ForeignKey("storages.uuid"), nullable=True)
    documents = relationship("Storage", foreign_keys=[document_uuid])
    added_by = Column(String, ForeignKey("users.uuid"), nullable=False)
    creator = relationship("User", foreign_keys=[added_by])

    # mail = relationship("Mail", back_populates="documents")

    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())  # Date de création
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Dernière mise à jour