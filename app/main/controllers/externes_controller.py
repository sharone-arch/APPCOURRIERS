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

router = APIRouter(prefix="/receivers", tags=["receivers"])


@router.post("/create",response_model=schemas.Msg)
async def create_receiver(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ExterneCreate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    exist_email = crud.externe.get_by_email(db=db,email=obj_in.email)
    if exist_email:
        raise HTTPException(status_code=409, detail=__(key="email-already-used"))
    exist_phone = crud.externe.get_by_phone_number(db=db,phone_number=obj_in.phone_number)
    if exist_phone:
        raise HTTPException(status_code=409, detail=__(key="phone_number-already-used"))
    crud.externe.create(db=db,obj_in=obj_in,created_by=current_user.uuid)
    return schemas.Msg(message=__(key="receiver-created-successfully"))

@router.put("/update",response_model=schemas.Msg)
async def update_receiver(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ExterneUpdate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.externe.update(db=db,obj_in=obj_in,created_by=current_user.uuid)
    return schemas.Msg(message=__(key="receiver-updated-successfully"))

@router.put("/soft-delete",response_model=schemas.Msg)
async def soft_delete(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ExterneDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.externe.soft_delete(db=db,uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="receiver-deleted-successfully"))

@router.delete("/delete-drop",response_model=schemas.Msg)
async def delete_drop(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ExterneDelete,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.externe.delete(db=db,uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="receiver-deleted-successfully"))

@router.put("/update-status",response_model=schemas.Msg)
async def update_status_receiver(
     *,
    db: Session = Depends(get_db),
    obj_in: schemas.UpdateStatus,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    crud.externe.update_status(db=db,uuid=obj_in.uuid,status=obj_in.status)
    return schemas.Msg(message=__(key="status-updated-successfully"))


@router.get("/get_all", response_model=None) # type: ignore
async def get_all_receiver(
    db: Session = Depends(get_db),
    page: int =  1,
    per_page: int = 25,
    order:str= Query(None,enum=["ASC","DESC"]),
    keyword: Optional[str] = None,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN","SENDER"]))
):
     return crud.externe.get_many(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        keyword=keyword,
    )


from fastapi import HTTPException

@router.get("/get_by_uuid", response_model=schemas.ExterneSlim)
async def get_data_by_uuid(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    data = crud.externe.get_by_uuid(db=db, uuid=uuid)
    if not data:
        raise HTTPException(status_code=404, detail="Externe non trouvé")
    return data
