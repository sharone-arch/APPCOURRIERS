from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.main.schemas.user import AddedBy


class ExterneBase(BaseModel):
    name: str
    email: str
    phone_number: str
    adress: str
    type: str  # client, fournisseur, partenaire

class ExterneCreate(ExterneBase):
    pass

class ExterneUpdate(BaseModel):
    uuid: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    adress: Optional[str] = None
    type: Optional[str] = None  # client, fournisseur, partenaire

class UpdateStatus(BaseModel):
    uuid: str
    status:str

class ExterneDelete(BaseModel):
    uuid :str


class Externe(BaseModel):
    uuid:str
    name: str
    email: str
    phone_number: str
    adress: str
    type: str  # client, fournisseur, partenaire
    created_at: datetime
    updated_at:datetime
    creator:AddedBy
    model_config = ConfigDict(from_attributes=True)


class ExterneResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[Externe]
    model_config = ConfigDict(from_attributes=True)

