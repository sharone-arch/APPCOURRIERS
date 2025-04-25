from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime,Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum


class EntiteReception(str,Enum):

    BUREAU_ORDRE = "BUREAU_ORDRE"
    SECRETAIRE = "SECRETAIRE"



class Courriers(Base):

    __tablename__ = "couriers"

    uuid = Column(String,primary_key=True,index=True)
    titre = Column(String,nullable=False,index=True)
    date_arrivee = Column(DateTime, default=func.now())  # Account creation timestamp
    date_depart = Column(DateTime, nullable=True)  # Account creation timestamp
    contenu = Column(String,index=True,nullable=False)
    is_deleted = Column(Boolean, default=False)
    entite_reception = Column(String, index=True,nullable=False,default=EntiteReception.BUREAU_ORDRE)