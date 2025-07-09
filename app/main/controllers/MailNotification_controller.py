from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.main import schemas, crud, models
from app.main.core.dependencies import get_db, TokenRequired

router = APIRouter(prefix="/mail-notifications", tags=["mail-notifications"])


@router.post("/", response_model=schemas.MailNotificationResponse)
async def create_mail_notification(
    payload: schemas.MailNotificationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired())
):
    return crud.mail_notification.create(db=db, obj_in=payload)


@router.get("/{uuid}", response_model=schemas.MailNotificationResponse)
async def get_mail_notification(
    uuid: str = Path(..., description="UUID de la notification"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired())
):
    return crud.mail_notification.get_by_uuid(db=db, uuid=uuid)


@router.put("/{uuid}", response_model=schemas.MailNotificationResponse)
async def update_mail_notification(
    uuid: str,
    payload: schemas.MailNotificationUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired())
):
    return crud.mail_notification.update(db=db, uuid=uuid, obj_in=payload)


@router.delete("/{uuid}")
async def delete_mail_notification(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired())
):
    return crud.mail_notification.delete(db=db, uuid=uuid)


@router.get("/", response_model=schemas.MailNotificationResponseList)
async def get_mail_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    order: str = Query("desc"),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired())
):
    return crud.mail_notification.get_many(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        keyword=keyword
    )


@router.get("/all", response_model=List[schemas.MailNotificationResponse])
async def get_all_mail_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired())
):
    return crud.mail_notification.get_all(db=db)
