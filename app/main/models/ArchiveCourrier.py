# models/archive_courrier.py

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.main.models.db.base_class import Base


class ArchiveCourrier(Base):
    __tablename__ = "archive_courrier"

    uuid = Column(String, primary_key=True)
    
    courrier_uuid = Column(String, ForeignKey("mails.uuid"), nullable=False)
    courrier = relationship("Mail", back_populates="archives", foreign_keys=[courrier_uuid])

    fichier_archive = Column(String, nullable=False)
    date_archivage = Column(DateTime, server_default=func.now())

    archive_par_uuid = Column(String, ForeignKey("users.uuid"), nullable=False)
    archiveur = relationship("User", foreign_keys=[archive_par_uuid])

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
