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


class CahierTransmission(Base):
    __tablename__ = "cahiers_transmission"

    uuid = Column(String, primary_key=True, index=True)
    courrier_uuid = Column(String, ForeignKey("courriers.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    courrier = relationship("Courrier", back_populates="cahiers_transmission")  # Relation Many-to-One avec Courrier
    date_transmission = Column(DateTime, default=func.now(), nullable=False)  # Date de transmission
    transmis_par = Column(String, nullable=False)  # Personne qui a transmis
    transmis_a = Column(String, nullable=False)  # Personne à qui c'est transmis
    remarques = Column(String, nullable=True)  # Remarques supplémentaires
    is_deleted = Column(Boolean,default=False)
    
    created_at = Column(DateTime, default=func.now())  # Date de création de l'enregistrement
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Date de la dernière mise à jour