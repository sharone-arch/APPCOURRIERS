from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.main.schemas.courriers import MailSlim2
from app.main.schemas.user import AddedBySlim


class MailTrackingBase(BaseModel):
    mail_uuid: str
    status: str


class MailTrackingCreate(MailTrackingBase):
    pass


class MailTracking(BaseModel):
    mail: MailSlim2
    updated_by: Optional[AddedBySlim] = None
    status: str
    changed_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MailTrackingResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[MailTracking]

    model_config = ConfigDict(from_attributes=True)
