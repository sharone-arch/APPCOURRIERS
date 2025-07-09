from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime,Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum


class MailNotification(Base):
    __tablename__ = "mail_notifications"

    uuid = Column(String, primary_key=True)
    user_uuid = Column(String, ForeignKey("users.uuid"))
    mail_uuid = Column(String, ForeignKey("outgoing_mails.uuid"))

    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", foreign_keys=[user_uuid])
    mail = relationship("OutgoingMail", foreign_keys=[mail_uuid])
