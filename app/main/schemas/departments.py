from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.main.schemas.user import AddedBy

class ResponsableBase(BaseModel):
    first_name:str
    last_name:str
    email:str
    phone_number:str

class ResponsableCreate(ResponsableBase):
    pass

class Responsable(BaseModel):
    first_name:str
    last_name:str
    email:str
    phone_number:str
    creator:AddedBy
    model_config = ConfigDict(from_attributes=True)

class ResponsableSlim(BaseModel):
    first_name:str
    last_name:str
    model_config = ConfigDict(from_attributes=True)





class DepartmentsBase(BaseModel):
    name:str
    description:str
    email:str
    phone_number:str
    phone_number2:str

class DepartmentCreate(DepartmentsBase):
    pass

class DepartmentsUpdate(BaseModel):
    uuid:str
    name : Optional[str]=None
    description:Optional[str]=None
    email : Optional[str]=None
    phone_number:Optional[str]=None
    phone_number2 : Optional[str]=None

class Department(BaseModel):
    name:str
    description:str
    email:str
    phone_number:str
    phone_number2:str
    creator:AddedBy
    responsable:ResponsableSlim
    model_config = ConfigDict(from_attributes=True)


class DepartmentDelete(BaseModel):
    uuid:str

class DepartmentDetails(BaseModel):
    uuid:str


class DepartmentsResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[Department]

    model_config = ConfigDict(from_attributes=True)


