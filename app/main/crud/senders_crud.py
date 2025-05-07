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
from app.main import models,schemas
from app.main.core.mail import send_account_creation_email


class CRUDSender(CRUDBase[models. Sender, schemas.SenderCreate, schemas.SenderUpdate]):

    
    @classmethod
    def get_by_phone_number(cls, db: Session, *, phone_number: str) -> Union[models.User, None]:
        return db.query(models.Sender).filter(models.Sender.phone_number == phone_number).first()
    
     
    @classmethod
    def get_by_second_phone_number(cls, db: Session, *, second_phone_number: str) -> Union[models.Sender, None]:
        return db.query(models.Sender).filter(models.Sender.second_phone_number == second_phone_number).first()
    
    

    @classmethod
    def get_by_email(cls, db: Session, *, email: str) -> Union[models.Sender, None]:
        return db.query(models.Sender).filter(models.Sender.email == email).first()
    
    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        return db.query(models.Sender).filter(models.Sender.uuid == uuid, models.Sender.is_deleted==False).first()
    
    @classmethod
    def create(cls,db:Session,*,obj_in:schemas.SenderCreate,added_by:str)->models.Sender:
        commond_uuid = str(uuid.uuid4())
        db_obj = models.Sender(
            uuid = commond_uuid,
            first_name = obj_in.first_name,
            last_name = obj_in.last_name,
            phone_number = obj_in.phone_number,
            email = obj_in.email,
            second_phone_number = obj_in.second_phone_number,
            address = obj_in.address,
            avatar_uuid = obj_in.avatar_uuid,
            added_by = added_by,

        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        password: str = generate_password(8, 8)
        print(f"User password: {password}")
        new_user = models.User(
            uuid = commond_uuid, 
            email = obj_in.email,
            phone_number = obj_in.phone_number,
            first_name = obj_in.first_name,
            last_name = obj_in.last_name,
            role = models.UserRole.SENDER,
            password_hash=get_password_hash(password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        send_account_creation_email(email_to=obj_in.email, first_name=obj_in.first_name,last_name=obj_in.last_name,
                                    password=password)

        return db_obj
    
    @classmethod
    def update(cls, db: Session, *,  obj_in: schemas.SenderUpdate,added_by:str):
        sender = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not sender:
            raise HTTPException(status_code=404, detail=__(key="sender-not-found"))
        
        sender.first_name = obj_in.first_name if obj_in.first_name else sender.first_name
        sender.last_name = obj_in.last_name if obj_in.last_name else sender.last_name
        sender.phone_number = obj_in.phone_number if obj_in.phone_number else sender.phone_number
        sender.email = obj_in.email if obj_in.email else sender.email
        sender.second_phone_number = obj_in.second_phone_number if obj_in.second_phone_number else sender.second_phone_number
        sender.address = obj_in.address if obj_in.address else sender.address
        sender.avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else sender.avatar_uuid
        added_by = added_by
        
        db.flush()
        db.commit()
        db.refresh(sender)
        return sender
    

    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str):
        sender = cls.get_by_uuid(db=db, uuid=uuid)
        if not sender:
            raise HTTPException(status_code=404, detail=__(key="senders-deleted-successfully"))
        sender.is_deleted = True
        db.commit()


    @classmethod
    def delete(cls, db: Session, *, uuid: str) -> None:
        sender = cls.get_by_uuid(db=db, uuid=uuid)
        if not sender:
            raise HTTPException(status_code=404, detail=__(key="senders-deleted-successfully"))
        db.delete(sender)
        db.commit()

    @classmethod
    def get_all(cls, db: Session) -> List[models.Sender]:
        return db.query(models.Sender).filter(models.Sender.is_deleted == False).all()
    
    @classmethod
    def get_many(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 25,

    ):
        record_query = db.query(models.Sender).filter( models.Sender.is_deleted == False)

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.SenderResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
    

sender=CRUDSender(models.Sender)
