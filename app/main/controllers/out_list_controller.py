from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.main.core.dependencies import get_db, TokenRequired

from app.main import schemas, crud

router = APIRouter(prefix="/outgoing-mails", tags=["Outgoing Mails"])


@router.post("/", response_model=schemas.OutgoingMail, status_code=status.HTTP_201_CREATED)
def create_outgoing_mail(
    mail_in: schemas.OutgoingMailCreate,
    db: Session = Depends(get_db)
):
    return crud.outgoing_mail.create(db=db, obj_in=mail_in)


@router.get("/{uuid}", response_model=schemas.OutgoingMail)
def read_outgoing_mail(
    uuid: str,
    db: Session = Depends(get_db)
):
    mail = crud.outgoing_mail.get_by_uuid(db=db, uuid=uuid)
    if not mail:
        raise HTTPException(status_code=404, detail="Courrier départ introuvable")
    return mail


@router.put("/{uuid}", response_model=schemas.OutgoingMail)
def update_outgoing_mail(
    uuid: str,
    mail_in: schemas.OutgoingMailUpdate,
    db: Session = Depends(get_db)
):
    updated_mail = crud.outgoing_mail.update(db=db, uuid=uuid, obj_in=mail_in)
    if not updated_mail:
        raise HTTPException(status_code=404, detail="Courrier départ introuvable")
    return updated_mail


@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outgoing_mail(
    uuid: str,
    db: Session = Depends(get_db)
):
    success = crud.outgoing_mail.delete(db=db, uuid=uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Courrier départ introuvable")
    return {"detail": "Courrier départ supprimé avec succès"}


@router.get("/", response_model=schemas.OutgoingMailResponseList)
def list_outgoing_mails(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    order: str = Query("desc", pattern="^(asc|desc)$"),  # ✅ `pattern` remplace `regex`
    keyword: Optional[str] = Query(None),
):
    return crud.outgoing_mail.get_many(db=db, page=page, per_page=per_page, order=order, keyword=keyword)
