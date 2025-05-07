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

class CRUDTypeCourriers(CRUDBase[models.TypeCourriers, schemas.TypeCourriersCreate, schemas.TypeCourriersUpdate]):
    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        return db.query(models.TypeCourriers).filter(models.TypeCourriers.uuid == uuid,models. TypeCourriers.is_deleted==False).first()
    @classmethod
    def get_by_name(cls, db: Session, *, name: str):
        return db.query(models. TypeCourriers).filter(models.TypeCourriers.name == name,models. TypeCourriers.is_deleted==False).first()
    
    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.TypeCourriersCreate,created_by:str):
        new_Type = models.TypeCourriers(
            uuid=str(uuid.uuid4()),
            name=obj_in.name,
            created_by=created_by,  # Initialement non supprimé
        )
        db.add( new_Type)
        db.commit()
        db.refresh( new_Type)
        return  new_Type
    

    @classmethod
    def update(cls, db: Session, *,  obj_in: schemas.TypeCourriersUpdate,created_by:str):
        db_obj = cls.get_by_uuid(db=db,uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="type-courrier-not-found"))
        db_obj.name = obj_in.name if obj_in.name else db_obj.name
        db.commit()
        db.refresh(db_obj)
        return db_obj

    
    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str) -> None:
        Type = cls.get_by_uuid(db=db, uuid=uuid)
        if not Type:
            raise HTTPException(status_code=404, detail=__(key="Type-not-found"))
        Type.is_deleted = True
        db.commit()

    @classmethod
    def delete(cls, db: Session, *, uuid: str) -> None:
        Type = cls.get_by_uuid(db=db, uuid=uuid)
        if not Type:
            raise HTTPException(status_code=404, detail=__(key="Type-not-found"))
        db.delete(type)
        db.commit()  

    
    @classmethod
    def get_all(cls, db: Session) -> List[models.TypeCourriers]:
        return db.query(models.TypeCourriers).filter(models.TypeCourriers.is_deleted == False).all()
    

    @classmethod
    def get_many(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 10,
        order:Optional[str] = None,
        keyword:Optional[str]= None
    ):
        record_query = db.query(models.TypeCourriers).filter(models.TypeCourriers.is_deleted == False)
        
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.TypeCourriers.name.ilike('%' + str(keyword) + '%')

                )
            )
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.TypeCourriers.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.TypeCourriers.date_added.desc())
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)
        
        return schemas.TypeCourriersResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
    
    
type_couriers = CRUDTypeCourriers(models.TypeCourriers)
    
    
    


