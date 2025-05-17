from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime,Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum

class Entite(str, Enum):
    EXPEDITEUR = "EXPEDITEUR"
    BUREAU_ORDRE = "BUREAU_ORDRE"  # ✅ Corrigé
    SECRETAIRE = "SECRETAIRE"
    DESTINATAIRE = "DESTINATAIRE"


class Actions(str,Enum):
    RECEPTION = "RECEPTION"
    DIFFUSION= "DIFFUSION"
    TRANSMISSION = "TRANSMISSION"    



class CourrierArrive(Base):
    __tablename__ = "courriers_arrivees"
    uuid = Column(String, primary_key=True,index=True, unique=True)
    entite = Column(String,nullable=False,default=Entite.BUREAU_ORDRE)
    action = Column(String,nullable=False,default=Actions.RECEPTION)
    mail_uuid = Column(String, ForeignKey("mails.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    mail = relationship("Mail", foreign_keys=[mail_uuid])

    added_by = Column(String, ForeignKey("users.uuid"), nullable=False)
    creator = relationship("User", foreign_keys=[added_by])

    is_deleted = Column(Boolean, default=False)  # Soft delete flag
    

    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp