from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.schemas.courriers import MailSlim2
from app.main.schemas.user import AddedBySlim


class MailNotificationBase(BaseModel):
    user_uuid: str
    mail_uuid: str
    message: str
    is_read: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class MailNotificationCreate(MailNotificationBase):
    pass


class MailNotificationUpdate(BaseModel):
    message: Optional[str] = None
    is_read: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class MailNotificationResponse(MailNotificationBase):
    uuid: str
    user: Optional[AddedBySlim] = None
    mail: Optional[MailSlim2] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MailNotificationResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[MailNotificationResponse]

    model_config = ConfigDict(from_attributes=True)
