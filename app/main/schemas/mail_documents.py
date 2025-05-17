from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.main.schemas.file import FileSlim2
from app.main.schemas.user import AddedBy


class MailDocumentOut(BaseModel):
    uuid: str
    documents: Optional[FileSlim2]=None  # Relation vers Storage

    model_config = ConfigDict(from_attributes=True)