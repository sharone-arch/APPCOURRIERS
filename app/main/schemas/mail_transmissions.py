from datetime import datetime
from app.main.schemas.courriers import MailSlim2
from app.main.schemas.departments import DepartmentSlim
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union

from app.main.schemas.externes import ExterneSlim2
from app.main.schemas.user import AddedBySlim


class MailTransmissionBase(BaseModel):
    mail_uuid: str
    note:str


class MailTransmissionCreate(MailTransmissionBase):
    pass

class MailTransmission(BaseModel):
    mail : MailSlim2
    from_entity:AddedBySlim
    to_entity:ExterneSlim2
    transmitted_by:AddedBySlim
    transmitted_at:datetime
    note:Optional[str]=None
    created_at: datetime
    updated_at:Optional[datetime]=None
    model_config = ConfigDict(from_attributes=True)


class MailTransmissionResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[MailTransmission]
    model_config = ConfigDict(from_attributes=True)
