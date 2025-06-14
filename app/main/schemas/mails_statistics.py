from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict

from app.main.schemas.courriers import MailSlim2
from app.main.schemas.user import AddedBySlim


class StatistiquesAutomatiquesBase(BaseModel):
    mail_uuid: str
    processing_time: Optional[int] = 0
    status_log: Optional[Any] = None  # JSON data, can be dict or list or None
    generated_at: Optional[datetime] = None
    added_by: str
    is_deleted: Optional[bool] = False


class StatistiquesAutomatiquesCreate(StatistiquesAutomatiquesBase):
    pass


class StatistiquesAutomatiques(StatistiquesAutomatiquesBase):
    uuid: str
    mail: MailSlim2
    creator: AddedBySlim
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class StatistiquesAutomatiquesResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[StatistiquesAutomatiques]

    model_config = ConfigDict(from_attributes=True)
