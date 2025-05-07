from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict
from typing import List, Optional

from sqlalchemy import DateTime
from app.main.models.users import UserRole
from app.main.schemas.user import AddedBy, UserCreate



class NatureCourriersSlim(BaseModel):
    uuid:str
    name:str
    model_config =ConfigDict(from_attributes=True)


class NatureCourriersBase(BaseModel):
    name:str


class NatureCourriersCreate(NatureCourriersBase):
    pass

class NatureCourriersUpdate(BaseModel):
    uuid:str
    name:Optional[str]=None

    
class NatureCourriersDelete(BaseModel):
    uuid: str

    
class NatureCourriersResponse(BaseModel):
    uuid:str
    name:str
    creator:AddedBy
    created_at: datetime
    updated_at:datetime
    model_config =ConfigDict(from_attributes=True)

class NatureCourriersResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[NatureCourriersResponse]

    model_config = ConfigDict(from_attributes=True)

