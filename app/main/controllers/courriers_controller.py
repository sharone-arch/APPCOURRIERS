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



# router = APIRouter(prefix="/courriers", tags=["courriers"])
# @router.post("/create", response_model=schemas.Msg)
# def create_courrier_channel(
#     *,
#     db: Session = Depends(get_db),
#     obj_in: schemas.CourriersBaseCreate,
#     current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
# ):
#     exist_uuid = crud.Courriers.get_by_uuid(db=db, name=obj_in.uuid)
#     if exist_uuid:
#         raise HTTPException(status_code=409, detail=__(key="courrier-channel-already-exists"))

#     crud.Courriers.create(db, obj_in=obj_in, created_by=current_user.uuid)
#     return schemas.Msg(message=__(key="courrier-channel-created-successfully"))




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



   






