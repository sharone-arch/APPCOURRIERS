from datetime import timedelta, datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.security import create_access_token, get_password_hash
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired


router = APIRouter(prefix="/senders", tags=["senders"])

@router.post("/create", response_model=schemas.Msg)
def create_sender(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.SenderCreate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    exist_email = crud.sender.get_by_email(db=db, email=obj_in.email)
    if exist_email:
        raise HTTPException(status_code=409, detail=__(key="email-already-used"))
    
    exist_phone = crud.sender.get_by_phone_number(db=db, phone_number=obj_in.phone_number)
    if exist_phone:
        raise HTTPException(status_code=409, detail=__(key="phone_number-already-used"))
    
    exist_second_phone_number = crud.sender.get_by_second_phone_number(db=db, second_phone_number=obj_in.second_phone_number)
    if exist_second_phone_number:
        raise HTTPException(status_code=409, detail=__(key="second-phone-number-already-used")) 
    
    if obj_in.avatar_uuid:
        avatar = crud.storage_crud.get_file_by_uuid(db=db, uuid=obj_in.avatar_uuid)
        if not avatar:
            raise HTTPException(status_code=404, detail=__(key="avatar-not-found"))

    crud.sender.create(db, obj_in=obj_in, added_by=current_user.uuid)
    return schemas.Msg(message=__(key="senders-created-successfully"))


@router.put("/update", response_model=schemas.Msg)
def update_sender(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.SenderUpdate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.sender.update(db=db, obj_in=obj_in, added_by=current_user.uuid)
    return schemas.Msg(message=__(key="senders-updated-successfully"))


@router.put("/soft-delete", response_model=schemas.Msg)
def soft_delete_sender(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.SenderDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.sender.soft_delete(db=db, uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="senders-deleted-successfully"))


@router.delete("/delete", response_model=schemas.Msg)
def delete_sender(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.SenderDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    crud.sender.delete(db=db, uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="senders-deleted-successfully"))


@router.get("/get_many", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 25,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    """
    get administrator with all data by passing filters
    """
    
    return crud.sender.get_many(
        db, 
        page, 
        per_page, 
    )
