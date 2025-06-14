from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __

router = APIRouter(prefix="/registres_courriers", tags=["registres_courriers"])


@router.post("/", response_model=schemas.RegistresCourriers)
def create_registre(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.RegistresCourriersCreate,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN", "SUPER_ADMIN"]))
):
    """Créer un nouvel enregistrement de transmission"""
    db_obj = crud.registres_courriers.create(db=db, obj_in=obj_in)
    return db_obj


@router.get("/{uuid}", response_model=schemas.RegistresCourriers)
def get_registre(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN", "SUPER_ADMIN"]))
):
    db_obj = crud.registres_courriers.get(db=db, uuid=uuid)
    if not db_obj:
        raise HTTPException(status_code=404, detail=__("registre-not-found"))
    return db_obj


@router.put("/{uuid}", response_model=schemas.RegistresCourriers)
def update_registre(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    obj_in: schemas.RegistresCourriersBase,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN", "SUPER_ADMIN"]))
):
    db_obj = crud.registres_courriers.get(db=db, uuid=uuid)
    if not db_obj:
        raise HTTPException(status_code=404, detail=__("registre-not-found"))
    updated = crud.registres_courriers.update(db=db, db_obj=db_obj, obj_in=obj_in)
    return updated


@router.delete("/{uuid}", response_model=schemas.RegistresCourriers)
def delete_registre(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN", "SUPER_ADMIN"]))
):
    db_obj = crud.registres_courriers.get(db=db, uuid=uuid)
    if not db_obj:
        raise HTTPException(status_code=404, detail=__("registre-not-found"))
    deleted = crud.registres_courriers.soft_delete(db=db, db_obj=db_obj)
    return deleted


@router.get("/get_many", response_model=schemas.RegistresCourriersResponseList)
def get_registres(
    *,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    order: Optional[str] = Query(None, enum=["ASC", "DESC"]),
    keyword: Optional[str] = None,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN", "SUPER_ADMIN"]))
):
    return crud.registres_courriers.get_many(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        keyword=keyword
    )
