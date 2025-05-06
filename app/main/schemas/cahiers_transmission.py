from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union

from app.main.schemas.courriers import CourrierResponseSlim
from app.main.schemas.externes import ExterneInDB
from app.main.schemas.user import AddedBy


class CahierTransmissionBase(BaseModel):
    courrier_uuid: str
    remarques: Optional[str] = None

class CahierTransmissionCreate(CahierTransmissionBase):
    pass


class CahierTransmission(BaseModel):
    uuid : str
    courrier:CourrierResponseSlim
    remarques: Optional[str] = None
    date_transmission:datetime
    transmis_par:Optional[AddedBy]
    transmis_a:Optional[Union[ExterneInDB, dict]]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CahierTransmissionResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[CahierTransmission]
    model_config = ConfigDict(from_attributes=True)

