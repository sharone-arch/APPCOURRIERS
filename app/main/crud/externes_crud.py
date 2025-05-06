import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models,schemas



class CRUDExternes(CRUDBase[models.Externe,schemas.ExterneBase,schemas.ExterneCreate]):

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str):
        return db.query(models.Externe).filter(models.Externe.uuid==uuid,models.Externe.is_deleted==False).first()
    
    @classmethod
    def get_by_name(cls,db:Session,*,name:str):
        return db.query(models.Externe).filter(models.Externe.name==name,models.Externe.is_deleted==False).first()
    

    @classmethod
    def get_by_email(cls,db:Session,*,email:str):
        return db.query(models.Externe).filter(models.Externe.email==email,models.Externe.is_deleted==False).first()
    
    @classmethod
    def get_by_phone_number(cls,db:Session,*,phone_number:str):
        return db.query(models.Externe).filter(models.Externe.phone_number==phone_number,models.Externe.is_deleted==False).first()
    

    @classmethod
    def create(cls,db:Session,*,obj_in:schemas.ExterneCreate,created_by:str):
        db_obj = models.Externe(
            uuid = str(uuid.uuid4()),
            name = obj_in.name,
            email = obj_in.email,
            phone_number = obj_in.phone_number,
            address = obj_in.address,
            type = obj_in.type,
            created_by = created_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    

    @classmethod
    def update(cls,db:Session,*,obj_in:schemas.ExterneCreate,created_by:str):
        db_obj = cls.get_by_uuid(db=db,uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="externe-not-found"))
        
        db_obj.name = obj_in.name if obj_in.name else db_obj.name
        db_obj.email = obj_in.email if obj_in.email else db_obj.email
        db_obj.phone_number = obj_in.phone_number if obj_in.phone_number else db_obj.phone_number
        db_obj.address = obj_in.address if obj_in.address else db_obj.address
        db_obj.type = obj_in.type if obj_in.type else db_obj.type
        created_by = created_by
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def soft_delete(cls,db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="externe-not-found"))
        db_obj.is_deleted = True
        db.commit()

    @classmethod
    def delete(cls,db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="externe-not-found"))
        db.delete(db_obj)
        db.commit()

    @classmethod
    def update_status(cls,db:Session,*,uuid:str,status:bool):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="externe-not-found"))
        db_obj.is_deleted = status
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
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
        record_query = db.query(models.Externe).filter(models.Externe.status.not_in([models.ExterneStatus.BLOCKED]))
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Externe.name.ilike('%' + str(keyword) + '%'),
                    models.Externe.email.ilike('%' + str(keyword) + '%'),
                    models.Externe.type.ilike('%' + str(keyword) + '%'),
                    models.Externe.phone_number.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.Externe.status == status)
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Externe.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Externe.date_added.desc())
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.ExterneResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
externe = CRUDExternes(models.Externe)