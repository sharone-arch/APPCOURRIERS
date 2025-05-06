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


class EntiteReception(str, Enum):
    BUREAU_ORDRE = "bureau d'ordre"
    SECRETAIRE = "secretaire"


class CourierType(str, Enum):
    INTERNE = "interne"
    EXTERNE = "externe"


class CourierStatus(str, Enum):
    RECU = "Reçu"
    EN_COURS = "En cours"
    TRAITE = "Traité"
    ARRIVE = "Arrivée"

class ActionsCouriers(str, Enum):
    DIFFUSION = "Diffusion"
    RECEPTION = "Réception"
    TRANMISSION = "Transmission"



class CourierInterne(Base):
    __tablename__ = "couriers_interne"

    uuid = Column(String, primary_key=True, index=True)
    titre = Column(String, nullable=False)
    date_arrivee = Column(DateTime, default=func.now())
    date_depart = Column(DateTime, nullable=True)
    contenu = Column(Text)
    action = Column(String, nullable=True,default=ActionsCouriers.RECEPTION)  # Action à effectuer sur le courrier

    document_uuid = Column(String, ForeignKey('storages.uuid', ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    document = relationship("Storage", foreign_keys=[document_uuid])

    expediteur_uuid = Column(String, ForeignKey("users.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    sender = relationship("User", foreign_keys=[expediteur_uuid])

   
    destinataire_uuid = Column(String,ForeignKey('departments.uuid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    destinataire = relationship("Department",foreign_keys=[destinataire_uuid]) 

    type_courrier_uuid = Column(String, ForeignKey('type_couriers.uuid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    type_courier = relationship("TypeCourriers", foreign_keys=[type_courrier_uuid])

    nature_courrier_uuid = Column(String, ForeignKey('nature_couriers.uuid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    nature_courrier = relationship("NatureCourriers", foreign_keys=[nature_courrier_uuid])

    canal_reception_uuid = Column(String, ForeignKey('canaux_receptions.uuid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    canal_reception = relationship("CanauxReceptionCourier", foreign_keys=[canal_reception_uuid])

    status = Column(String, nullable=False, default=CourierStatus.RECU)  # 'Reçu', 'En cours', 'Traité'
    is_deleted = Column(Boolean, default=False)  # Soft delete flag

    entite_reception = Column(String, index=True, nullable=False, default=EntiteReception.BUREAU_ORDRE)
    type = Column(String, index=True, nullable=False, default=CourierType.INTERNE)

    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp



class CourierExterne(Base):
    __tablename__ = "couriers_externe"

    uuid = Column(String, primary_key=True, index=True)
    titre = Column(String, nullable=False)
    date_arrivee = Column(DateTime, default=func.now())
    date_depart = Column(DateTime, nullable=True)
    contenu = Column(Text)
    action = Column(String, nullable=True,default=ActionsCouriers.RECEPTION)  # Action à effectuer sur le courrier

    document_uuid = Column(String, ForeignKey('storages.uuid', ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    document = relationship("Storage", foreign_keys=[document_uuid])

    expediteur_uuid = Column(String, ForeignKey("users.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    sender = relationship("User", foreign_keys=[expediteur_uuid])

   
    destinataire_uuid = Column(String,ForeignKey('externes.uuid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    destinataire = relationship("Externe",foreign_keys=[destinataire_uuid]) 

    type_courrier_uuid = Column(String, ForeignKey('type_couriers.uuid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    type_courier = relationship("TypeCourriers", foreign_keys=[type_courrier_uuid])

    nature_courrier_uuid = Column(String, ForeignKey('nature_couriers.uuid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    nature_courrier = relationship("NatureCourriers", foreign_keys=[nature_courrier_uuid])

    canal_reception_uuid = Column(String, ForeignKey('canaux_receptions.uuid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    canal_reception = relationship("CanauxReceptionCourier", foreign_keys=[canal_reception_uuid])

    status = Column(String, nullable=False, default=CourierStatus.RECU)  # 'Reçu', 'En cours', 'Traité'
    is_deleted = Column(Boolean, default=False)  # Soft delete flag

    entite_reception = Column(String, index=True, nullable=False, default=EntiteReception.BUREAU_ORDRE)
    type = Column(String, index=True, nullable=False, default=CourierType.INTERNE)

    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp



