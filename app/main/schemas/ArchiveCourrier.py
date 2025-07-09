from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.main.schemas.courriers import MailSlim2  # version allégée du mail
from app.main.schemas.user import AddedBySlim  # version allégée de l'utilisateur


class ArchiveCourrierBase(BaseModel):
    courrier_uuid: str
    fichier_archive: str
    archive_par_uuid: str

    model_config = ConfigDict(from_attributes=True)


class ArchiveCourrierCreate(ArchiveCourrierBase):
    pass


class ArchiveCourrierUpdate(BaseModel):
    fichier_archive: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ArchiveCourrier(ArchiveCourrierBase):
    uuid: str
    courrier: Optional[MailSlim2] = None
    archiveur: Optional[AddedBySlim] = None
    date_archivage: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ArchiveCourrierResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[ArchiveCourrier]

    model_config = ConfigDict(from_attributes=True)
