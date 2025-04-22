from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict
from typing import List, Optional

from sqlalchemy import DateTime
from app.main.models.users import UserRole
from app.main.schemas.user import UserCreate




class FormesCourierBase(BaseModel):
    name:str


class FormesCourierCreate(FormesCourierBase):
    pass

class FormesCourierUpdate(BaseModel):
    uuid:str
    name:Optional[str]=None
    
class FormesCourierResponse(BaseModel):
    uuid:str
    name:str
    created_by:UserCreate
    created_at: datetime
    updated_at:datetime
    model_config = ConfigDict(from_attributes=True)

class FormesCourierResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[FormesCourierResponse]

    model_config = ConfigDict(from_attributes=True)

