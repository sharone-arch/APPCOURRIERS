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

router = APIRouter(prefix="/formes-courriers", tags=["formes_courriers"])
@router.post("/create", response_model=schemas.Msg)
def create_forme_courrier(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.FormesCourriersCreate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    exist_name = crud.formes_couriers.get_by_name(db=db, name=obj_in.name)
    if exist_name:
        raise HTTPException(status_code=409, detail=__(key="forme-courrier-already-exists"))

    crud.formes_couriers.create(db, obj_in=obj_in, added_by=current_user.uuid)
    return schemas.Msg(message=__(key="forme-courrier-created-successfully"))



@router.put("/update",response_model=schemas.FormesCourriersResponse)
def update_Forme(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.FormesCourriersUpdate,
    current_user : models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    added_by_uuid = current_user.uuid
    return crud.formes_couriers.update(db=db,obj_in=obj_in,added_by=current_user.uuid)


@router.put("/soft-delete", response_model=schemas.Msg)
def soft_delete_Forme(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.FormesCourriersDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.formes_couriers.soft_delete(db=db, uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="forme-courrier-deleted-successfully"))


@router.delete("/delete", response_model=schemas.Msg)
def delete_Forme(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.FormesCourriersDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.formes_couriers.delete(db=db, uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="forme-courrier-deleted-successfully"))


@router.get("/get_all", response_model=List[schemas.FormesCourriersResponse]) # type: ignore
def get_all_Formes(
    db: Session = Depends(get_db),
    page: int =  1,
    per_page: int = 30,
    order:str= Query(None,enum=["ASC","DESC"]),
    order_field: Optional[str] = None,
    keyword: Optional[str] = None,
):
     return crud.formes_couriers.get_many(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        order_field=order_field,
        keyword=keyword,
    )






