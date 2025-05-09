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



router = APIRouter(prefix="/mails", tags=["mails"])
@router.post("/create", response_model=schemas.Msg)
async def create_mail(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.MailCreate,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(TokenRequired(roles=["SENDER"]))
):
    if obj_in.document_uuid:
        document = crud.storage_crud.get_file_by_uuid(db=db, file_uuid=obj_in.document_uuid)
        if not document:
            raise HTTPException(status_code=404,detail=__(key="document-not-found"))
    receiver = crud.externe.get_by_uuid(db=db,uuid=obj_in.receiver_uuid)
    if not receiver:
        raise HTTPException(status_code=404,detail=__(key="receiver-not-found"))
    type = crud.type_couriers.get_by_uuid(db=db,uuid=obj_in.type_uuid)
    if not type:
        raise HTTPException(status_code=404,detail=__(key="type-courier-not-found"))
    nature = crud.Nature.get_by_uuid(db=db,uuid=obj_in.nature_uuid)
    if not nature:
         raise HTTPException(status_code=404,detail=__(key="nature-courier-not-found"))
    forme = crud.formes_couriers.get_by_uuid(db=db,uuid=obj_in.forme_uuid)
    if not forme:
         raise HTTPException(status_code=404,detail=__(key="forme-courier-not-found"))
    canal_reception = crud.canaux.get_by_uuid(db=db,uuid=obj_in.canal_reception_uuid)
    if not canal_reception:
        raise HTTPException(status_code=404,detail=__(key="canal-reception-not-found"))
    crud.courriers.create(db=db,obj_in=obj_in,sender_uuid=current_user.uuid,background_tasks=background_tasks)
    return schemas.Msg(message=__(key="mail-send-successfully"))


@router.put("/update",response_model=schemas.Msg)
async def update_mail(
     *,
    db: Session = Depends(get_db),
    obj_in: schemas.MailUpdate,
    current_user: models.User = Depends(TokenRequired(roles=["SENDER"]))
):
    if obj_in.document_uuid:
        document = crud.storage_crud.get_file_by_uuid(db=db, file_uuid=obj_in.document_uuid)
        if not document:
            raise HTTPException(status_code=404,detail=__(key="document-not-found"))
    receiver = crud.externe.get_by_uuid(db=db,uuid=obj_in.receiver_uuid)
    if not receiver:
        raise HTTPException(status_code=404,detail=__(key="receiver-not-found"))
    type = crud.type_couriers.get_by_uuid(db=db,uuid=obj_in.type_uuid)
    if not type:
        raise HTTPException(status_code=404,detail=__(key="type-courier-not-found"))
    nature = crud.Nature.get_by_uuid(db=db,uuid=obj_in.nature_uuid)
    if not nature:
         raise HTTPException(status_code=404,detail=__(key="nature-courier-not-found"))
    forme = crud.formes_couriers.get_by_uuid(db=db,uuid=obj_in.forme_uuid)
    if not forme:
         raise HTTPException(status_code=404,detail=__(key="forme-courier-not-found"))
    canal_reception = crud.canaux.get_by_uuid(db=db,uuid=obj_in.canal_reception_uuid)
    if not canal_reception:
        raise HTTPException(status_code=404,detail=__(key="canal-reception-not-found"))
    crud.courriers.update(db=db,obj_in=obj_in,sender_uuid=current_user.uuid)
    return schemas.Msg(message=__(key="mail-updated-successfully"))
    

@router.put("/soft-delete",response_model=schemas.Msg)
async def soft_delete_mail(
     *,
    db: Session = Depends(get_db),
    obj_in: schemas.MailDelete,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN","SUPER_ADMIN"]))
):
    crud.courriers.soft_delete(db=db,uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="mail-deleted-successfully"))

@router.delete("/drop",response_model=schemas.Msg)
async def drop_mail(
     *,
    db: Session = Depends(get_db),
    obj_in: schemas.MailDelete,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN","SUPER_ADMIN"]))
):
    crud.courriers.delete(db=db,uuid=obj_in.uuid)
    return schemas.Msg(message=__(key="mail-deleted-successfully"))


@router.get("/get_by_uuid", response_model=schemas.Mail)
async def get_mail_by_uuid(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN","SENDER"]))
):
    data = crud.courriers.get_by_uuid(db=db, uuid=uuid)
    if not data:
        raise HTTPException(status_code=404, detail=__(key="mail-not-found"))
    return data

@router.get("/get_many", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page:int = 30,
    order:str= Query(None,enum=["ASC","DESC"]),
    status:Optional[str] = None,
    keyword:Optional[str]= None,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN","ADMIN","SENDER"]))
):
    
    return crud.courriers.get_many(
        db, 
        page, 
        per_page, 
        order=order,
        status=status,
        keyword=keyword
    )


@router.get("/get-sender-mail", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page:int = 30,
    order:str= Query(None,enum=["ASC","DESC"]),
    status:Optional[str] = None,
    keyword:Optional[str]= None,
    current_user: models.User = Depends(TokenRequired(roles=["SENDER"]))
):
    
    return crud.courriers.get_sender_mail(
        db, 
        page, 
        per_page, 
        order=order,
        status=status,
        keyword=keyword,
        sender_uuid=current_user.uuid
    )

@router.put("/send-receiver-mail", response_model=schemas.Msg)
async def send_receiver_mail(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.MailDetails
):
    # 1. Récupération du courrier
    mail = crud.courriers.get_by_uuid(db=db, uuid=obj_in.uuid)
    if not mail:
        raise HTTPException(status_code=404, detail=__(key="mail-not-found"))
    # 2. Vérifier si déjà transféré
    if mail.is_transferred:
        raise HTTPException(status_code=400, detail=__(key="mail-is-already-send"))
    # 3. Récupération du destinataire
    receiver = crud.externe.get_by_uuid(db=db, uuid=mail.receiver_uuid)
    if not receiver:
        raise HTTPException(status_code=404, detail=__(key="receiver-not-found"))
    # 4. Récupération de l’expéditeur
    sender = crud.sender.get_by_uuid(db=db, uuid=mail.sender_uuid)
    if not sender:
        raise HTTPException(status_code=404, detail=__(key="sender-not-found"))

    # 5. Mise à jour de l'état
    mail.is_transferred = True
    mail.sent_at = datetime.now()
    db.commit()

    # 6. Envoi de la notification
    notify_receiver_new_mail(
        email_to=receiver.email,
        name=receiver.name,
        subject=mail.subject,
        content=mail.content,
        sender=f"{sender.first_name} {sender.last_name}"
    )

    return {"message": __(key="mail-transferred-successfully")}
