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


router = APIRouter(prefix="/nature", tags=["nature"])
@router.post("/create", response_model=schemas.Msg)
def create_Nature_courrier(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.NatureCourriersCreate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    exist_name = crud.Nature.get_by_name(db=db, name=obj_in.name)
    if exist_name:
        raise HTTPException(status_code=409, detail=__(key="nature-already-exists"))

    crud.Nature.create(db, obj_in=obj_in, created_by=current_user.uuid)
    return schemas.Msg(message=__(key="naturecreated-successfully"))



@router.put("/update",response_model=schemas.NatureCourriersResponse)
def update_Nature(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.NatureCourriersUpdate,
    current_user : models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    return crud.Nature.update(db=db,obj_in=obj_in,created_by=current_user.uuid)



@router.put("/soft-delete", response_model=schemas.Msg)
def soft_delete_Nature(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.NatureCourriersDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.Nature.soft_delete(db=db, uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="nature-deleted-successfully"))


@router.delete("/delete", response_model=schemas.Msg)
def delete_Nature(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.NatureCourriersDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.Nature.delete(db=db, uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="nature-deleted-successfully"))


@router.get("/get_all", response_model=None) # type: ignore
def get_all_Nature(
    db: Session = Depends(get_db),
    page: int =  1,
    per_page: int = 10,
    order:str= Query(None,enum=["ASC","DESC"]),
    keyword: Optional[str] = None,
):
     return crud.Nature.get_many(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        keyword=keyword,
    )










