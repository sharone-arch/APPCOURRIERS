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
    def update(cls, db: Session, *, uuid: str, obj_in: schemas.NatureCourriersUpdate) -> models.NatureCourriers:
        Nature = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not Nature:
            raise HTTPException(status_code=404, detail=__(key="Nature-not-found"))
        
        db.flush()
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
            *,
            db: Session,
            page: int = 1,
            per_page: int = 10,
            search: Optional[str] = None,
            sort_by: Optional[str] = None,
            order: Optional[str] = None
    ) -> schemas.NatureCourriersResponse:
        query = db.query(models.NatureCourriers).filter(models.NatureCourriers.is_deleted == False)
        
        if search:
            query = query.filter(or_(
                models.NatureCourriers.name.ilike(f"%{search}%"),
                models.NatureCourriers.uuid.ilike(f"%{search}%")
            ))
        
        total = query.count()
        pages = math.ceil(total / per_page)
        
        if sort_by and order:
            if order.lower() == "asc":
                query = query.order_by(getattr(models.NatureCourriers, sort_by).asc())
            else:
                query = query.order_by(getattr(models.NatureCourriers, sort_by).desc())
        
        data = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return schemas.NatureCourriersResponseList(
            total=total,
            pages=pages,
            per_page=per_page,
            current_page=page,
            data=data
        )
    
    
    
Nature=CRUDNatureCourriers(models.NatureCourriers)
    