from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __

router = APIRouter(prefix="/mail_registers", tags=["mail_registers"])


@router.post("/add", response_model=schemas.Msg)
async def add_register_entry(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.RegistresCourriersCreate,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN", "SUPER_ADMIN"]))
):
    """Ajouter une entrée dans le registre des courriers"""
    crud.registres_courriers.create(
        db=db,
        obj_in=obj_in,
        added_by=current_user.uuid
    )
    return {"message": __(key="register-added-successfully")}


@router.get("/get_many", response_model=schemas.RegistresCourriersResponseList)
def get_register_entries(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: Optional[str] = Query(None, enum=["ASC", "DESC"]),
    keyword: Optional[str] = None,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    """Récupérer la liste des entrées de registre"""
    return crud.registres_courriers.get_many(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        keyword=keyword
    )


@router.get("/get/{uuid}", response_model=schemas.RegistresCourriers)
def get_register_by_uuid(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    """Récupérer une entrée spécifique du registre par UUID"""
    register = crud.registres_courriers.get_by_uuid(db=db, uuid=uuid)
    if not register:
        raise HTTPException(status_code=404, detail=__(key="register-not-found"))
    return register
