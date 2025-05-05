from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union


from app.main.schemas.canaux_reception import CanauxReceptionCourierSlim
from app.main.schemas.externes import ExterneInDB
from app.main.schemas.file import FileSlim2
from app.main.schemas.nature import NatureCourriersSlim
from app.main.schemas.type import TypeCourriersSlim
from app.main.schemas.user import AddedBy

class CourrierBase(BaseModel):
    titre: str
    document_uuid : Optional[str] = None
    contenu: Optional[str] = None
    destinataire_type: str
    destinataire_uuid: str
    type_courrier_uuid: str
    nature_courrier_uuid: str
    canal_reception_uuid: str
   
class CourierCreate(CourrierBase):
    pass
class CourrierUdpdate(CourrierBase):
    uuid:str
    titre: Optional[str] = None
    document_uuid : Optional[str] = None
    contenu: Optional[str] = None
    destinataire_type: Optional[str] = None
    destinataire_uuid: Optional[str] = None
    type_courrier_uuid: Optional[str] = None
    nature_courrier_uuid: Optional[str] = None
    canal_reception_uuid: Optional[str] = None


class CourrierUpdateStatus(BaseModel):
    uuid : str
    status: str

class CourrierDelete(BaseModel):   
    uuid : str 



class CourrierResponse(BaseModel):
    uuid : str
    titre: str
    document:Optional[FileSlim2]=None
    sender: Optional[AddedBy] = None
    destinataire: Optional[Union[ExterneInDB, dict]]
    type_courier:Optional[TypeCourriersSlim]=None
    nature_courrier : Optional[NatureCourriersSlim] = None
    canal_reception:Optional[CanauxReceptionCourierSlim] = None
    status:str
    entite_reception:str
    destinataire_type:str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CourrierResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[CourrierResponse]
    model_config = ConfigDict(from_attributes=True)
