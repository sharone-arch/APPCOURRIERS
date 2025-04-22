from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict
from typing import List, Optional

from sqlalchemy import DateTime
from app.main.models.users import UserRole
from app.main.schemas.user import UserCreate




class NatureCourierBase(BaseModel):
    name:str


class NatureCourierCreate(NatureCourierBase):
    pass

class NatureCourierUpdate(BaseModel):
    uuid:str
    name:Optional[str]=None
    
class NatureCourierResponse(BaseModel):
    uuid:str
    name:str
    created_at: datetime
    updated_at:datetime
    model_config =ConfigDict(from_attributes=True)

class NatureCourierResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[NatureCourierResponse]

    model_config = ConfigDict(from_attributes=True)

