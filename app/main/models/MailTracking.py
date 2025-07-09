from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.main.models.db.base_class import Base

class MailTracking(Base):
    __tablename__ = "mail_tracking"

    uuid = Column(String, primary_key=True, index=True)
    
    # Liaison avec le courrier suivi
    mail_uuid = Column(String, ForeignKey("mails.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    mail = relationship("Mail", foreign_keys=[mail_uuid])

    # Utilisateur ayant modifié le statut
    updated_by_uuid = Column(String, ForeignKey("users.uuid"), nullable=True)
    updated_by = relationship("User", foreign_keys=[updated_by_uuid])

    # Statut du courrier
    status = Column(String, nullable=False)  # e.g., "reçu", "en_cours", "traité"

    # Date de changement de statut
    changed_at = Column(DateTime, default=func.now())

    # Métadonnées
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
