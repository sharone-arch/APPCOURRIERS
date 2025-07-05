from datetime import timedelta, datetime
import math
from typing import Any, List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.mail import notify_receiver_new_mail
from app.main.core.security import create_access_token, get_password_hash
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired



router = APIRouter(prefix="/mail_transmissions", tags=["mail_transmissions"])


@router.post("/send",response_model=schemas.Msg)
async def send_receiver_mail(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.MailTransmissionCreate,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN","SUPER_ADMIN"]))
):
    """Send a mail to a receiver"""
    crud.mail_transmissions.create(
        db=db,
        obj_in=obj_in,
        transmitted_by_uuid=current_user.uuid

    )
    return {"message": __(key="mail-transferred-successfully")}



@router.post("/send-sender-mail",response_model=schemas.Msg)
async def send_sender_mail(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.MailTransmissionCreate,
    current_user: models.User = Depends(TokenRequired(roles=["RECEIVER"]))
):
    """Send a mail to a receiver"""
    crud.mail_transmissions.send_sender(
        db=db,
        obj_in=obj_in,
        transmitted_by_uuid=current_user.uuid

    )
    return {"message": __(key="mail-transferred-successfully")}

@router.put("/received-by-office",response_model=schemas.Msg)
def receive_courrier(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.MailDetails,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    mail = crud.courriers.get_by_uuid(db=db,uuid=obj_in.uuid)
    if not mail:
        raise HTTPException(status_code=404, detail=__(key="mail-not-found"))
    mail.received_by_office = True
    db.commit()
    return {"message":__(key="mail-received")}


@router.put("/is_diffused",response_model=schemas.Msg)
def diffuse_courrier(
     *,
    db: Session = Depends(get_db),
    obj_in:schemas.MailDetails,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    mail = crud.courriers.get_by_uuid(db=db,uuid=obj_in.uuid)
    if not mail:
        raise HTTPException(status_code=404, detail=__(key="mail-not-found"))
    mail.is_diffused = True
    db.commit()
    return {"message":__(key="mail-diffused")}


@router.get("/get_many", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page:int = 30,
    order:str= Query(None,enum=["ASC","DESC"]),
    keyword:Optional[str]= None,
    # current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN"]))
):
    
    return crud.mail_transmissions.get_many(
        db, 
        page, 
        per_page, 
        order=order,
        keyword=keyword
    )