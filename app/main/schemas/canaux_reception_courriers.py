from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.main.schemas.user import AddedBy



class CanauxReceptionCourierBase(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)

class CanauxReceptionCourierCreate(CanauxReceptionCourierBase):
    pass

class CanauxReceptionCourierUpdate(BaseModel):
    uuid: str
    name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class CanauxReceptionCourierResponse(BaseModel):
    uuid: str
    name: str
    creator : Optional[AddedBy] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CanauxReceptionCourierDelete(BaseModel):
    uuid: str

class CanauxReceptionCourierDetail(CanauxReceptionCourierResponse):
    creator: Optional[AddedBy] = None

class CanauxReceptionCourierList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[CanauxReceptionCourierResponse]
    model_config = ConfigDict(from_attributes=True)
