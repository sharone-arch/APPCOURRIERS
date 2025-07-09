from datetime import datetime
import math
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Body, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.main import schemas, crud, models
from app.main.core.dependencies import get_db, TokenRequired
from app.main.core.i18n import __

router = APIRouter(prefix="/mail-actions", tags=["mail-actions"])


@router.post("/", response_model=schemas.MailAction, summary="Créer une action sur un courrier")
async def create_mail_action(
    payload: schemas.MailActionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN",]))
):
    return crud.mail_action.create(db=db, obj_in=payload)


@router.get("/{uuid}", response_model=schemas.MailAction, summary="Récupérer une action par UUID")
async def get_mail_action(
    uuid: str = Path(..., description="UUID de l'action"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN", "BUREAU_ORDRE", "SECRETAIRE"]))
):
    return crud.mail_action.get_by_uuid(db=db, uuid=uuid)


@router.put("/{uuid}", response_model=schemas.MailAction, summary="Mettre à jour une action")
async def update_mail_action(
    uuid: str,
    payload: schemas.MailActionUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    return crud.mail_action.update(db=db, uuid=uuid, obj_in=payload)


@router.delete("/{uuid}", summary="Supprimer une action")
async def delete_mail_action(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    return crud.mail_action.delete(db=db, uuid=uuid)


@router.get("/", response_model=schemas.MailActionResponseList, summary="Lister les actions avec pagination")
async def get_mail_actions(
    page: int = Query(1, ge=1, description="Numéro de la page"),
    per_page: int = Query(30, ge=1, le=100, description="Nombre d'actions par page"),
    order: str = Query("desc", description="Ordre de tri : asc ou desc"),
    keyword: Optional[str] = Query(None, description="Filtrer par mot-clé"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN", "SECRETAIRE"]))
):
    return crud.mail_action.get_many(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        keyword=keyword
    )


@router.get("/all", response_model=List[schemas.MailAction], summary="Récupérer toutes les actions (non paginées)")
async def get_all_mail_actions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    return crud.mail_action.get_all(db=db)
