from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.main.schemas.user import AddedBy


class CanauxReceptionCourierSlim(BaseModel):
    uuid: str
    name: str
    model_config = ConfigDict(from_attributes=True)


class CanauxReceptionBase(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)

class CanauxReceptionCreate(CanauxReceptionBase):
    pass

class CanauxReceptionUpdate(BaseModel):
    uuid: str
    name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class CanauxReceptionResponse(BaseModel):
    uuid: str
    name: str
    created_at: datetime
    updated_at: datetime
    creator : Optional[AddedBy] = None
    model_config = ConfigDict(from_attributes=True)


class CanauxReceptionDelete(BaseModel):
    uuid: str

class CanauxReceptionCourierDetail(CanauxReceptionResponse):
    creator: Optional[AddedBy] = None

class CanauxReceptionCourierList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[CanauxReceptionResponse]
    model_config = ConfigDict(from_attributes=True)
