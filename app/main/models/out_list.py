from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.main.models.db.base_class import Base

class OutgoingMail(Base):
    __tablename__ = "outgoing_mails"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference = Column(String, unique=True, nullable=False)  # ex: "CR-20250630-9623"
    entity_name = Column(String, nullable=False)  # ex: "Bureau d'ordre"
    action_name = Column(String, nullable=False)  # ex: "Reception"
    performed_by = Column(String, nullable=False)  # nom de l'utilisateur
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
