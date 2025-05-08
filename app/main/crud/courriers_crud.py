import math
import bcrypt
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session
from app.main.core.security import generate_courier_code
from app.main.crud.base import CRUDBase
from app.main import models,schemas,crud
from app.main.core.mail import notify_admin_new_couriers,notify_receiver_new_mail
from functools import partial

class CRUDCourriers(CRUDBase[models.Mail, schemas.MailBase, schemas.MailDelete]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str) : 
        return db.query(models.Mail).filter(models.Mail.uuid == uuid ,models.Mail.is_deleted==False).first()
    

    @classmethod
    def get_by_subject(cls, db: Session, *, subject: str) : 
        return db.query(models.Mail).filter(models.Mail.subject == subject ,models.Mail.is_deleted==False).first()


    
    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.MailCreate, sender_uuid: str, background_tasks: BackgroundTasks):
        number = generate_courier_code(counter=1)
        db_obj = models.Mail(
            uuid=str(uuid.uuid4()),
            subject=obj_in.subject,
            content=obj_in.content,
            document_uuid=obj_in.document_uuid,
            receiver_uuid=obj_in.receiver_uuid,
            type_uuid=obj_in.type_uuid,
            nature_uuid=obj_in.nature_uuid,
            forme_uuid=obj_in.forme_uuid,
            canal_reception_uuid=obj_in.canal_reception_uuid,
            sender_uuid=sender_uuid,
            number = number
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Récupération des infos de l'expéditeur et du destinataire
        sender = db.query(models.Sender).filter(models.Sender.uuid == sender_uuid).first()
        if not sender:
            raise HTTPException(status_code=404,detail=__(key="sender-not-found"))
        receiver = db.query(models.Externe).filter(models.Externe.uuid == obj_in.receiver_uuid).first()
        if not receiver:
            raise HTTPException(status_code=404,detail=__(key="receiver-not-found"))

        admins = crud.user.get_all_users(db=db)
        if not admins:
            raise HTTPException(status_code=404,detail=__(key="admins-not-found"))

        # Notifications aux admins
        for admin in admins:
            background_tasks.add_task(
                notify_admin_new_couriers,
                email_to=admin.email,
                name=f"{admin.first_name} {admin.last_name}",
                subject=obj_in.subject,
                content=obj_in.content,
                sender=f"{sender.first_name} {sender.last_name}"
            )

        # Notification au destinataire
        background_tasks.add_task(
            notify_receiver_new_mail,
            email_to=receiver.email,
            name=receiver.name,
            subject=obj_in.subject,
            content=obj_in.content,
            sender=f"{sender.first_name} {sender.last_name}"
        )

        return db_obj



            
        
    

    @classmethod
    def update(cls,db: Session,*,obj_in:schemas.MailUpdate,sender_uuid:str):
        db_obj = cls.get_by_uuid(db=db,uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="mail-not-found"))
        db_obj.subject = obj_in.subject if obj_in.subject else db_obj.subject
        db_obj.content = obj_in.content if obj_in.content else db_obj.content
        db_obj.document_uuid = obj_in.document_uuid if obj_in.document_uuid else db_obj.document_uuid
        db_obj.receiver_uuid = obj_in.receiver_uuid if obj_in.receiver_uuid else db_obj.receiver_uuid
        db_obj.type_uuid = obj_in.type_uuid if obj_in.type_uuid else db_obj.type_uuid
        db_obj.nature_uuid = obj_in.nature_uuid if obj_in.nature_uuid else db_obj.nature_uuid
        db_obj.forme_uuid = obj_in.forme_uuid if obj_in.forme_uuid else db_obj.forme_uuid
        db_obj.canal_reception_uuid = obj_in.canal_reception_uuid if obj_in.canal_reception_uuid else db_obj.canal_reception_uuid
        sender_uuid = sender_uuid
        db.commit()
        db.refresh(db_obj)
        return db_obj
        



    @classmethod
    def soft_delete(cls,db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="mail-not-found"))
        db_obj.is_deleted = False
        db.commit()
    
    @classmethod
    def delete(cls,db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="mail-not-found"))
        db.delete(db_obj)
        db.commit()

    @classmethod
    def update_status(cls,db:Session,uuid:str,status:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="mail-not-found"))
        db_obj.status = status
        db.commit()
        
    @classmethod
    def appose_cachet(cls,db:Session,uuid:str,status:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="mail-not-found"))
        db_obj.status = status
        db.commit()

    
    @classmethod
    def get_many(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        status:Optional[str] = None,
        keyword:Optional[str]= None
    ):
        record_query = db.query(models.Mail).filter(models.Mail.is_deleted == False)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Mail.subject.ilike('%' + str(keyword) + '%'),
                    models.Mail.content.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.Mail.status == status)
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Mail.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Mail.date_added.desc())
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.MailResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    


    @classmethod
    def get_sender_mail(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        status:Optional[str] = None,
        keyword:Optional[str]= None,
        sender_uuid : Optional[str]=None
    ):
        record_query = db.query(models.Mail).filter(models.Mail.is_deleted == False,models.Mail.sender_uuid==sender_uuid)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Mail.subject.ilike('%' + str(keyword) + '%'),
                    models.Mail.content.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.Mail.status == status)
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Mail.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Mail.date_added.desc())
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.MailSlimSenderResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
courriers= CRUDCourriers(models.courriers)