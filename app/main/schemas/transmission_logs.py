from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

from app.main.schemas.courriers import MailSlim2
from app.main.schemas.user import AddedBySlim  # Pour from_user, to_user, added_by


class RegistresCourriersBase(BaseModel):
    mail_uuid: str
    from_user_uuid: Optional[str] = None
    to_user_uuid: Optional[str] = None
    added_by: str
    note: Optional[str] = None
    is_deleted: Optional[bool] = False


class RegistresCourriersCreate(RegistresCourriersBase):
    pass


class RegistresCourriers(BaseModel):
    uuid: str
    mail: MailSlim2
    from_user: Optional[AddedBySlim] = None
    to_user: Optional[AddedBySlim] = None
    added_by: AddedBySlim
    note: Optional[str] = None
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RegistresCourriersResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[RegistresCourriers]

    model_config = ConfigDict(from_attributes=True)
