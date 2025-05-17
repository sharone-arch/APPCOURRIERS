from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict
from typing import List, Optional

from sqlalchemy import DateTime
from app.main.models.users import UserRole
from app.main.schemas.user import UserCreate



class AddedBy(BaseModel):
    first_name:str
    last_name :str
    phone_number:str
    email:str
    second_phone_number:str
    address:str
    model_config = ConfigDict(from_attributes=True)




class ReceiverBase(BaseModel):
    first_name:str
    last_name :str
    phone_number:str
    email:str
    second_phone_number:str
    address:str
    model_config = ConfigDict(from_attributes=True)



    



class ReceiverCreate(ReceiverBase):
    pass

class ReceiverUpdate(BaseModel):
    uuid:str
    first_name:Optional[str]=None
    last_name:Optional[str]=None
    phone_number:Optional[str]=None
    email:Optional[str]=None
    second_phone_number:Optional[str]=None
    address:Optional[str]=None



class ReceiverUpdate(BaseModel):
    uuid:str
    first_name:Optional[str]=None
    last_name:Optional[str]=None
    phone_number:Optional[str]=None
    email:Optional[str]=None
    second_phone_number:Optional[str]=None
    address:Optional[str]=None


class ReceiverDelete(BaseModel):
    uuid: str



class ReceiverResponse(BaseModel):
    uuid:str
    first_name:Optional[str]=None
    last_name:Optional[str]=None
    phone_number:Optional[str]=None
    email:Optional[str]=None
    second_phone_number:Optional[str]=None
    address:Optional[str]=None
    added_by:UserCreate
    created_at: datetime
    updated_at:datetime
    model_config = ConfigDict(from_attributes=True)




class ReceiverResponse(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[ReceiverResponse]

    model_config = ConfigDict(from_attributes=True)


