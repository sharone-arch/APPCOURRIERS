from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict
from typing import List, Optional
from sqlalchemy import DateTime
from app.main.schemas.user import AddedBy, UserCreate


class TypeCourriersSlim(BaseModel):
    uuid:str
    name:str
    model_config = ConfigDict(from_attributes=True)

class TypeCourriersBase(BaseModel):
    name:str


class TypeCourriersCreate(TypeCourriersBase):
    pass

class TypeCourriersUpdate(BaseModel):
    uuid:str
    name:Optional[str]=None

class TypeCourriersDelete(BaseModel):
    uuid: str
    
class TypeCourriersResponse(BaseModel):
    uuid:str
    name:str
    creator:AddedBy
    created_at: datetime
    updated_at:datetime
    model_config = ConfigDict(from_attributes=True)

class TypeCourriersResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[TypeCourriersResponse]

    model_config = ConfigDict(from_attributes=True)

