from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.schemas.courriers import MailSlim2
from app.main.schemas.user import AddedBySlim


class MailActionBase(BaseModel):
    mail_uuid: str
    actor_uuid: str
    action_type: str  # Ex: "NOTE", "RETRANSFERT", "REPONSE"
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MailActionCreate(MailActionBase):
    pass


class MailActionUpdate(BaseModel):
    action_type: Optional[str] = None
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MailAction(MailActionBase):
    uuid: str
    mail: Optional[MailSlim2] = None
    actor: Optional[AddedBySlim] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MailActionResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[MailAction]

    model_config = ConfigDict(from_attributes=True)
