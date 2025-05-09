from datetime import datetime
from app.main.schemas.departments import DepartmentSlim
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union


from app.main.schemas.canaux_reception import CanauxReceptionCourierSlim
from app.main.schemas.externes import ExterneInDB, ExterneSlim
from app.main.schemas.file import FileSlim2
from app.main.schemas.formes import FormesSlim
from app.main.schemas.mail_documents import MailDocumentOut
from app.main.schemas.nature import NatureCourriersSlim
from app.main.schemas.type import TypeCourriersSlim
from app.main.schemas.user import AddedBy


class MailBase(BaseModel):
    subject:str
    content:str
    document_uuid:Optional[str]=None
    receiver_uuid:str
    type_uuid:str
    nature_uuid:str
    forme_uuid:str
    canal_reception_uuid:str


class MailCreate(MailBase):
    pass

class MailUpdate(BaseModel):
    uuid : Optional[str]=None
    subject:Optional[str]=None
    content:Optional[str]=None
    document_uuid:Optional[str]=None
    receiver_uuid:Optional[str]=None
    type_uuid:Optional[str]=None
    nature_uuid:Optional[str]=None
    forme_uuid:Optional[str]=None
    canal_reception_uuid:Optional[str]=None


class Mail(BaseModel):
    uuid:str
    subject:str
    content:str
    number:str
    is_transferred: bool
    received_at:Optional[datetime]=None
    sent_at : Optional[datetime]=None
    documents: Optional[FileSlim2]=None
    receiver:Optional[ExterneSlim]=None
    type:Optional[TypeCourriersSlim]=None
    nature:Optional[NatureCourriersSlim]=None
    forme:Optional[FormesSlim]=None
    canal_reception:Optional[CanauxReceptionCourierSlim]=None
    sender : Optional[AddedBy]=None
    created_at: datetime
    updated_at: Optional[datetime]=None
    model_config = ConfigDict(from_attributes=True)


class MailResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[Mail]

    model_config = ConfigDict(from_attributes=True)



class MailSlimSender(BaseModel):
    uuid:str
    subject:str
    content:str
    number:str
    is_transferred:bool
    received_at:Optional[datetime]=None
    sent_at : Optional[datetime]=None
    documents: Optional[FileSlim2]=None
    receiver:Optional[ExterneSlim]=None
    type:Optional[TypeCourriersSlim]=None
    nature:Optional[NatureCourriersSlim]=None
    forme:Optional[FormesSlim]=None
    canal_reception:Optional[CanauxReceptionCourierSlim]=None
    created_at: datetime
    updated_at: Optional[str]=None
    model_config = ConfigDict(from_attributes=True)

class MailSlimSenderResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[MailSlimSender]

    model_config = ConfigDict(from_attributes=True)



class MailDelete(BaseModel):
    uuid :str

class MailUpdateStatus(BaseModel):
    uuid :str

class MailDetails(BaseModel):
    uuid : str




