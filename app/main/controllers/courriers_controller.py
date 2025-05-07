from datetime import timedelta, datetime
import math
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.security import create_access_token, get_password_hash
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired



router = APIRouter(prefix="/mails", tags=["mails"])
@router.post("/create", response_model=schemas.Msg)
def create_mail(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.MailCreate,
    current_user: models.User = Depends(TokenRequired(roles=["SENDER"]))
):
    if obj_in.document_uuid:
        documents = crud.storage_crud.get_file_by_uuid(db=db,file_uuid=obj_in.document_uuid)
        if not documents:
            raise HTTPException(status_code=404,detail=__(key="document-not-found"))
    receiver = crud.externe.get_by_uuid(db=db,uuid=obj_in.uuid)
    if not receiver:
        raise HTTPException(status_code=404,detail=__(key="receiver-not-found"))
    type = crud.type_couriers.get_by_uuid(db=db,uuid=obj_in.type_uuid)
    if not type:
        raise HTTPException(status_code=404,detail=__(key="type-mail-not-found"))
    nature = crud.Nature.get_by_uuid(db=db,uuid=obj_in.nature_uuid)
    if not nature:
         raise HTTPException(status_code=404,detail=__(key="nature-mail-not-found"))
    forme = crud.formes_couriers.get_by_uuid(db=db,uuid=obj_in.nature_uuid)
    if not nature:
         raise HTTPException(status_code=404,detail=__(key="forme-mail-not-found"))
    canal_reception = crud.canaux.get_by_uuid(db=db,uuid=obj_in.canal_reception_uuid)
    if not canal_reception:
        raise HTTPException(status_code=404,detail=__(key="canal-mail-not-found"))
    crud.courriers.create(db=db,obj_in=obj_in,sender_uuid=current_user.uuid)
    return schemas.Msg(message=__(key="mail-send-successfully"))








# @router.put("/update",response_model=schemas.CourriersResponse)
# def update_canaux(
#     *,
#     db: Session = Depends(get_db),
#     obj_in:schemas.TypeCourriersUpdate,
#     current_user : models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
# ):
#     added_by_uuid = current_user.uuid
#     return crud.canaux(db=db,obj_in=obj_in,added_by_uuid=added_by_uuid)



# @router.put("/soft-delete", response_model=schemas.Msg)
# def soft_delete_Courriers(
#     *,
#     db: Session = Depends(get_db),
#     obj_in: schemas.CourriersDelete,
#     current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
# ):
#     crud.Courriers.soft_delete(db=db, uuid=obj_in.uuid)
#     return schemas.Msg(message=__(key="courrier-channel-deleted-successfully"))



# @router.delete("/delete", response_model=schemas.Msg)
# def delete_Courriers(
#     *,
#     db: Session = Depends(get_db),
#     obj_in: schemas.CourriersDelete,
#     current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
# ):
#     crud.Courriers.delete(db=db, uuid=obj_in.uuid)
#     return schemas.Msg(message=__(key="courrier-channel-deleted-successfully"))



# @router.get("/get_all_courriers", response_model=None)
# def get_all_Courriers(
#     *,
#     db: Session = Depends(get_db),
#     page: int =  1,
#     per_page: int = 30,
#     order:str= Query(None,enum=["ASC","DESC"]),
#     order_field: Optional[str] = None,
#     keyword: Optional[str] = None,
# ):
#     return crud.canaux.get_many(
#         db=db,
#         page=page,
#         per_page=per_page,
#         order=order,
#         order_field=order_field,
#         keyword=keyword,
#     )



   






