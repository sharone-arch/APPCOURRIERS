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



router = APIRouter(prefix="/type", tags=["type"])
@router.post("/create", response_model=schemas.Msg)
def create_Type_courrier(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.TypeCourriersCreate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    exist_name = crud.type_couriers.get_by_name(db=db, name=obj_in.name)
    if exist_name:
        raise HTTPException(status_code=409, detail=__(key="Type-courrier-already-exists"))

    crud.type_couriers.create(db, obj_in=obj_in, created_by=current_user.uuid)
    return schemas.Msg(message=__(key="type-courrier-created-successfully"))



@router.put("/update",response_model=schemas.Msg)
def update_Type(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas. TypeCourriersUpdate,
    current_user : models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    crud.type_couriers.update(db=db, obj_in=obj_in, created_by=current_user.uuid)
    return schemas.Msg(message=__(key="type-courrier-updated-successfully"))


@router.put("/soft-delete", response_model=schemas.Msg)
def soft_delete_Type(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.TypeCourriersDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.type_couriers.soft_delete(db=db, uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="Nature-courrier-deleted-successfully"))


@router.delete("/delete", response_model=schemas.Msg)
def delete_Type(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.TypeCourriersDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.type_couriers.delete(db=db, uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="Type-courrier-deleted-successfully"))


@router.get("/get_all", response_model=None)  # type: ignore
def get_all_type(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 10,
    order: str = Query(None, enum=["ASC", "DESC"]),
    keyword: Optional[str] = None,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN","SENDER"]))
):
    return crud.type_couriers.get_many(  # Correction : appeler la méthode de classe directement
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        keyword=keyword,
    )


