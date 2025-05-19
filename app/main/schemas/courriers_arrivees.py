from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.main.schemas.user import AddedBy
from app.main.schemas.courriers import MailSlim2

class CourrierArriveBase(BaseModel):
    uuid:str
    entite:str
    action:str
    mail:MailSlim2
    creator : Optional[AddedBy] = None
    created_at: datetime
    updated_at: Optional[datetime]=None
    model_config = ConfigDict(from_attributes=True)



class CourrierArriveList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[CourrierArriveBase]
    model_config = ConfigDict(from_attributes=True)
