from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.main.schemas.file import FileSlim2


class CourrierBase(BaseModel):
    titre: str
    document_uuid : Optional[str] = None
    contenu: Optional[str] = None
    expediteur_uuid: int
    destinataire_type: str
    destinataire_uuid: str
    type_courrier_uuid: str
    nature_courrier_uuid: str
    canal_reception_uuid: str
   
class CourrierCreate(CourrierBase):
    titre: Optional[str] = None
    document_uuid : Optional[str] = None
    contenu: Optional[str] = None
    expediteur_uuid: Optional[str] = None
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
    sender: Optional[str] = None