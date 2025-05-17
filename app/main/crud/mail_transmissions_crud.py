from datetime import datetime
import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from app.main.core.security import generate_password, get_password_hash,verify_password
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models,schemas,crud
from app.main.core.mail import notify_receiver_new_mail, send_account_creation_email



class CRUDMailTransmission(CRUDBase[models.TransmissionsCourriers,schemas.MailTransmissionBase,schemas.MailTransmissionCreate]):

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str):
        return db.query(models.TransmissionsCourriers).filter(models.TransmissionsCourriers.uuid == uuid,models.TransmissionsCourriers.is_deleted==False).first()
    
    @classmethod
    def get_by_transmitted_at(cls,db:Session,*,transmitted_at:datetime):
        return db.query(models.TransmissionsCourriers).filter(models.TransmissionsCourriers.transmitted_at ==transmitted_at,models.TransmissionsCourriers.is_deleted==False).all()
    

    @classmethod
    def create(cls,db:Session,*,obj_in:schemas.MailTransmissionCreate,transmitted_by_uuid:str):
        mail = crud.courriers.get_by_uuid(db=db,uuid=obj_in.mail_uuid)
        if not mail:
            raise HTTPException(status_code=404,detail=__(key="mail-not-found"))
    
        receiver = crud.externe.get_by_uuid(db=db, uuid=mail.receiver_uuid)
        if not receiver:
            raise HTTPException(status_code=404, detail=__(key="receiver-not-found"))
        # 4. Récupération de l’expéditeur
        sender = crud.sender.get_by_uuid(db=db, uuid=mail.sender_uuid)
        if not sender:
            raise HTTPException(status_code=404, detail=__(key="sender-not-found"))
        
        db_obj = models.TransmissionsCourriers(
        uuid=str(uuid.uuid4()),
        mail_uuid=obj_in.mail_uuid,
        from_entity_uuid=mail.sender_uuid,  # Si `sender_uuid` correspond au user interne
        to_entity_uuid=mail.receiver_uuid,  # Si `receiver_uuid` est un externe
        transmitted_by_uuid=transmitted_by_uuid,
        note=obj_in.note
        )
        mail.is_transferred = True
        mail.sent_at = datetime.now()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        notify_receiver_new_mail(
        email_to=receiver.email,
        name=receiver.name,
        subject=mail.subject,
        content=mail.content,
        sender=f"{sender.first_name} {sender.last_name}"
    )
        return db_obj
    

    @classmethod
    def get_many(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        keyword:Optional[str]= None
    ):
        record_query = db.query(models.TransmissionsCourriers).filter(models.TransmissionsCourriers.is_deleted == False)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.TransmissionsCourriers.note.ilike('%' + str(keyword) + '%'),

                )
            )
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.TransmissionsCourriers.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.TransmissionsCourriers.date_added.desc())
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.MailTransmissionResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
    


mail_transmissions = CRUDMailTransmission(models.TransmissionsCourriers)