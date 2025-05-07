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


class MailStatus(str, Enum):
    RECU = "RECU"
    EN_TRAITEMENT = "EN_TRAITEMENT"
    TRAITE = "TRAITE"
    ARCHIVE = "ARCHIVE"

class Mail(Base):
    __tablename__ = "mails"

    uuid = Column(String, primary_key=True)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    received_at = Column(DateTime, server_default=func.now())
    sent_at = Column(DateTime, nullable=True)

    document_uuid = Column(String, ForeignKey("storages.uuid"), nullable=True)
    documents = relationship("Storage", foreign_keys=[document_uuid])
    
    sender_uuid = Column(String, ForeignKey("users.uuid"), nullable=True)
    sender = relationship("User", foreign_keys=[sender_uuid])

    receiver_uuid = Column(String, ForeignKey("externes.uuid"), nullable=True)
    receiver = relationship("Externe", foreign_keys=[receiver_uuid])

    type_uuid = Column(String, ForeignKey("type_couriers.uuid"), nullable=True)
    type = relationship("TypeCourriers", foreign_keys=[type_uuid])

    nature_uuid = Column(String, ForeignKey("nature_couriers.uuid"), nullable=True)
    nature = relationship("NatureCourriers", foreign_keys=[nature_uuid])


    forme_uuid = Column(String, ForeignKey("formes_couriers.uuid"), nullable=True)
    forme = relationship("FormesCourriers", foreign_keys=[forme_uuid])

    canal_reception_uuid = Column(String, ForeignKey("canaux_receptions.uuid"), nullable=True)
    canal_reception = relationship("CanauxReceptionCourier", foreign_keys=[canal_reception_uuid])

    status = Column(String,nullable=True, default=MailStatus.RECU)

    is_deleted = Column(Boolean,default=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

