from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime,Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum

class ExterneType(str, Enum):
    CLIENT = "client"
    FOURNISSEUR = "fournisseur"
    PARTENAIRE = "partenaire"

class ExterneStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "locked"


class Externe(Base):  # client, fournisseur ou partenaire
    __tablename__ = "externes"

    uuid = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone_number  = Column(String, nullable=True)
    adress = Column(String, nullable=True)
    type = Column(String,default=ExterneType.CLIENT,nullable=False)  # client, fournisseur, partenaire
    created_by = Column(String, ForeignKey('users.uuid',ondelete="CASCADE",onupdate="CASCADE"), nullable=True)
    creator = relationship("User", foreign_keys=[created_by])
    status = Column(Boolean, default=ExterneStatus.ACTIVE)  # pour gérer l'activation/désactivation

    is_deleted = Column(Boolean, default=False)  # pour gérer la suppression logique
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
