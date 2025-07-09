from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID


class OutgoingMailBase(BaseModel):
    reference: str
    entity_name: str
    action_name: str
    performed_by: str
    is_deleted: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class OutgoingMailCreate(OutgoingMailBase):
    pass


class OutgoingMailUpdate(BaseModel):
    uuid: UUID
    reference: Optional[str] = None
    entity_name: Optional[str] = None
    action_name: Optional[str] = None
    performed_by: Optional[str] = None
    is_deleted: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class OutgoingMailDelete(BaseModel):
    uuid: UUID


class OutgoingMail(OutgoingMailBase):  # Pour la réponse complète
    uuid: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OutgoingMailResponseList(BaseModel):
    total: int
    pages: int
    per_page: int
    current_page: int
    data: List[OutgoingMail]

    model_config = ConfigDict(from_attributes=True)
