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


class CRUDNatureCourriers(CRUDBase[models.NatureCourriers, schemas.NatureCourriersCreate, schemas.NatureCourriersUpdate]):
    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        return db.query(models. NatureCourriers).filter(models.NatureCourriers.uuid == uuid,models. NatureCourriers.is_deleted==False).first()
    
    @classmethod
    def get_by_name(cls, db: Session, *, name: str):
        return db.query(models. NatureCourriers).filter(models.NatureCourriers.name == name,models. NatureCourriers.is_deleted==False).first()
    
    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.NatureCourriersCreate,created_by:str):
        new_Nature = models.NatureCourriers(
            uuid=str(uuid.uuid4()),
            name=obj_in.name,
            created_by=created_by,  # Initialement non supprimé
        )
        db.add(new_Nature)
        db.commit()
        db.refresh(new_Nature)
        return new_Nature
    

    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.NatureCourriersUpdate,created_by:str) -> models.NatureCourriers:
        Nature = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not Nature:
            raise HTTPException(status_code=404, detail=__(key="Nature-not-found"))
        Nature.name = obj_in.name if obj_in.name else Nature.name
        created_by = created_by
        db.commit()
        db.refresh(Nature)
        return Nature
    
    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str) -> None:
        Nature = cls.get_by_uuid(db=db, uuid=uuid)
        if not Nature:
            raise HTTPException(status_code=404, detail=__(key="Nature-not-found"))
        Nature.is_deleted = True
        db.commit()

    @classmethod
    def delete(cls, db: Session, *, uuid: str) -> None:
        Nature = cls.get_by_uuid(db=db, uuid=uuid)
        if not Nature:
            raise HTTPException(status_code=404, detail=__(key="Nature-not-found"))
        db.delete(Nature)
        db.commit()

    @classmethod
    def get_all(cls, db: Session) -> List[models.NatureCourriers]:
        return db.query(models.NatureCourriers).filter(models.NatureCourriers.is_deleted == False).all()
    

    @classmethod
    def get_many(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 10,
        order:Optional[str] = None,
        keyword:Optional[str]= None
    ):
        record_query = db.query(models.NatureCourriers).filter(models.NatureCourriers.is_deleted == False)
        
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.NatureCourriers.name.ilike('%' + str(keyword) + '%')

                )
            )
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.NatureCourriers.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.NatureCourriers.date_added.desc())
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)
        
        return schemas.NatureCourriersResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
    
    
    
Nature=CRUDNatureCourriers(models.NatureCourriers)
    