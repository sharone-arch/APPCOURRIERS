from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict
from typing import List, Optional

from sqlalchemy import DateTime
from app.main.models.users import UserRole
from app.main.schemas.user import AddedBy, UserCreate




class FormesCourriersBase(BaseModel):
    name:str


class FormesCourriersCreate(FormesCourriersBase):
    pass

class FormesCourriersUpdate(BaseModel):
    uuid:str
    name:Optional[str]=None

class FormesCourriersDelete(BaseModel):
    uuid: str

    
class FormesCourriersResponse(BaseModel):
    uuid:str
    name:str
    creator : Optional[AddedBy] = None
    created_at: datetime
    updated_at:datetime
    model_config = ConfigDict(from_attributes=True)

class FormesCourriersResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[FormesCourriersResponse]

    model_config = ConfigDict(from_attributes=True)

