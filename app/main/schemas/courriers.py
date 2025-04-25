from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict
from typing import List, Optional
from app.main.models.users import UserRole




class CourriersBase(BaseModel):
    titre:str
    date_arrivee  : datetime
    date_depart : datetime
    contenu:str
    


class CourriersBaseCreate(CourriersBase): # type: ignore
    pass

class CourriersBaseUpdate(BaseModel):
    uuid:str
    titre:Optional[str]=None
    date_arrivee:Optional[datetime]=None
    date_depart:Optional[datetime]=None
    contenu:Optional[str]=None
   

class CourriersDelete(BaseModel):
    uuid: str

class CourriersResponse(BaseModel):
    uuid:str
    titre:str
    date_arrivee:str
    date_depart:datetime
    contenu:datetime
    model_config = ConfigDict(from_attributes=True)

class CourriersResponseList(BaseModel):
    total:int
    pages:int
    per_page:int
    current_page :int
    data : List[CourriersResponse]

    model_config = ConfigDict(from_attributes=True)

