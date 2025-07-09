from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.main import crud, models, schemas
from app.main.core.i18n import __
from app.main.core.dependencies import get_db, TokenRequired

router = APIRouter(prefix="/mail_tracking", tags=["mail_tracking"])


@router.post("/", response_model=schemas.Msg)
def create_mail_tracking(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.MailTrackingCreate,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN", "SUPER_ADMIN", "BUREAU_ORDRE"]))
):
    """
    Créer un enregistrement de suivi de courrier.
    """
    crud.mail_tracking.create(
        db=db,
        obj_in=obj_in,
        updated_by_uuid=current_user.uuid
    )
    return {"message": __(key="mail-tracking-created")}


@router.get("/get_many", response_model=schemas.MailTrackingResponseList)
def get_mail_tracking_list(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: Optional[str] = Query(None, enum=["ASC", "DESC"]),
    keyword: Optional[str] = None
):
    """
    Récupérer une liste paginée des suivis de courrier.
    """
    return crud.mail_tracking.get_many(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        keyword=keyword
    )


@router.get("/{uuid}", response_model=schemas.MailTracking)
def get_mail_tracking_by_uuid(
    *,
    db: Session = Depends(get_db),
    uuid: str,
):
    """
    Récupérer un suivi de courrier par UUID.
    """
    record = crud.mail_tracking.get_by_uuid(db=db, uuid=uuid)
    if not record:
        raise HTTPException(status_code=404, detail=__(key="mail-tracking-not-found"))
    return record


@router.delete("/{uuid}", response_model=schemas.Msg)
def delete_mail_tracking(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN", "SUPER_ADMIN"]))
):
    """
    Supprimer (soft delete) un suivi de courrier.
    """
    record = crud.mail_tracking.get_by_uuid(db=db, uuid=uuid)
    if not record:
        raise HTTPException(status_code=404, detail=__(key="mail-tracking-not-found"))

    record.is_deleted = True
    record.updated_at = datetime.now()
    db.commit()
    return {"message": __(key="mail-tracking-deleted")}
