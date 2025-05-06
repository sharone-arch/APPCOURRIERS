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

router = APIRouter(prefix="/canaux-reception", tags=["canaux_reception"])

@router.post("/create", response_model=schemas.Msg)
def create_courrier_channel(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.CanauxReceptionCourierCreate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    exist_name = crud.canaux.get_by_name(db=db, name=obj_in.name)
    if exist_name:
        raise HTTPException(status_code=409, detail=__(key="courrier-channel-already-exists"))

    crud.canaux.create(db, obj_in=obj_in, added_by=current_user.uuid)
    return schemas.Msg(message=__(key="courrier-channel-created-successfully"))

@router.get("/get_all", response_model=List[schemas.CanauxReceptionCourierResponse]) # type: ignore
def get_all_Courriers(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    return crud.canaux.get_all(db=db)




@router.put("/update",response_model=schemas.CanauxReceptionCourierResponse)
def update_canaux(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.CanauxReceptionCourierUpdate,
    current_user : models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    
    return crud.canaux.update(db=db,obj_in=obj_in,added_by=current_user.uuid)


@router.put("/soft-delete", response_model=schemas.Msg)
def soft_delete_canaux(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.CanauxReceptionCourierDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.canaux.soft_delete(db=db, uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="courrier-channel-deleted-successfully"))



@router.delete("/delete", response_model=schemas.Msg)
def delete_canaux(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.CanauxReceptionCourierDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.canaux.delete(db=db, uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="courrier-channel-deleted-successfully"))

@router.get("/get_all_canaux-receptions", response_model=None)
def get_all_canaux_receptions(
    *,
    db: Session = Depends(get_db),
    page: int =  1,
    per_page: int = 30,
    order:str= Query(None,enum=["ASC","DESC"]),
    order_field: Optional[str] = None,
    keyword: Optional[str] = None,
):
    return crud.canaux.get_many(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        order_field=order_field,
        keyword=keyword,
    )



   