from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.schemas.courriers import MailSlim2
from app.main.schemas.user import AddedBySlim


class RegistresCourriersBase(BaseModel):
    mail_uuid: str
    register_type: Optional[str] = "ARRIVEE"
    added_by: str
    is_deleted: Optional[bool] = False


class RegistresCourriersCreate(RegistresCourriersBase):
    pass


class RegistresCourriers(RegistresCourriersBase):
    uuid: str
    mail: MailSlim2
    creator: AddedBySlim
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
