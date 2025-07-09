from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.main.models.db.base_class import Base
from enum import Enum

class MailAction(Base):
    __tablename__ = "mail_actions"

    uuid = Column(String, primary_key=True)
    mail_uuid = Column(String, ForeignKey("mails.uuid"))
    actor_uuid = Column(String, ForeignKey("users.uuid"))  # Celui qui agit
    action_type = Column(String)  # "NOTE", "RETRANSFERT", "REPONSE"
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    mail = relationship("Mail", foreign_keys=[mail_uuid])
    actor = relationship("User", foreign_keys=[actor_uuid])
