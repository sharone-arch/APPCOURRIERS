from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict
from typing import List, Optional

from sqlalchemy import DateTime
from app.main.models.users import UserRole
from app.main.schemas.file import FileSlim2
from app.main.schemas.user import AddedBy, UserCreate

class SenderBase(BaseModel):
    first_name:str
    last_name :str
    phone_number:str
    email:str
    second_phone_number:str
    address:str
    avatar_uuid : Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SenderCreate(SenderBase):
    pass

class SenderUpdate(BaseModel):
    uuid:str
    first_name:Optional[str]=None
    last_name:Optional[str]=None
    phone_number:Optional[str]=None
    email:Optional[str]=None
    second_phone_number:Optional[str]=None
    address:Optional[str]=None
    avatar_uuid : Optional[str] = None



class SenderDelete(BaseModel):
    uuid: str



class SenderResponse(BaseModel):
    uuid:str
    first_name:Optional[str]=None
    last_name:Optional[str]=None
    phone_number:Optional[str]=None
    email:Optional[str]=None
    second_phone_number:Optional[str]=None
    address:Optional[str]=None
    avatar : Optional[FileSlim2]=None
    creator:Optional[AddedBy]=None
    created_at: datetime
    updated_at:datetime
    model_config = ConfigDict(from_attributes=True)


    class SenderDelete(BaseModel):
        uuid: str




class SenderResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[SenderResponse]

    model_config = ConfigDict(from_attributes=True)

