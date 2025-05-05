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



class CRUDFormesCourriers(CRUDBase[models.FormesCourriers, schemas.FormesCourriersCreate, schemas.FormesCourriersUpdate]):
    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        return db.query(models.FormesCourriers).filter(models.FormesCourriers.uuid == uuid,models.FormesCourriers.is_deleted==False).first()
    @classmethod
    def get_by_name(cls, db: Session, *, name: str):
        return db.query(models.FormesCourriers).filter(models.FormesCourriers.name == name,models.FormesCourriers.is_deleted==False).first()
    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.FormesCourriersCreate,created_by:str):
        new_Forme = models.FormesCourriers(
            uuid=str(uuid.uuid4()),
            name=obj_in.name,
            created_by=created_by,  # Initialement non supprimé
        )
        db.add(new_Forme)
        db.commit()
        db.refresh(new_Forme)
        return new_Forme
    @classmethod
    def update(cls, db: Session, *, uuid: str, obj_in: schemas.FormesCourriersUpdate) -> models.FormesCourriers:
        Forme = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not Forme:
            raise HTTPException(status_code=404, detail=__(key="Forme-not-found"))
        
        db.flush()
        db.commit()
        db.refresh(Forme)
        return Forme
    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str) -> None:
        Forme = cls.get_by_uuid(db=db, uuid=uuid)
        if not Forme:
            raise HTTPException(status_code=404, detail=__(key="Forme-not-found"))
        Forme.is_deleted = True
        db.commit()
    @classmethod
    def delete(cls, db: Session, *, uuid: str) -> None:
        Forme = cls.get_by_uuid(db=db, uuid=uuid)
        if not Forme:
            raise HTTPException(status_code=404, detail=__(key="Forme-not-found"))
        db.delete(Forme)
        db.commit()

    @classmethod
    def get_all(cls, db: Session) -> List[models.FormesCourriers]:
        return db.query(models.FormesCourriers).filter(models.FormesCourriers.is_deleted == False).all()
    


    @classmethod
    def get_many(
            cls,
            *,
            db: Session,
            page: int = 1,
            per_page: int = 30,
            order: Optional[str] = None,
            order_field: Optional[str] = None,
            keyword: Optional[str] = None
        ):
            if page < 1:
                page = 1

            record_query = db.query(models.FormesCourriers).filter(models.FormesCourriers.is_deleted == False)

            if keyword:
                record_query = record_query.filter(
                    or_(
                        models.FormesCourriers.name.ilike(f"%{keyword}%")
                    )
                )

            if order and order_field and hasattr(models.FormesCourriers, order_field):
                if order.lower() == "asc":
                    record_query = record_query.order_by(getattr(models.FormesCourriers, order_field).asc())
                else:
                    record_query = record_query.order_by(getattr(models.FormesCourriers, order_field).desc())
            total = record_query.count()
            record_query = record_query.offset((page - 1) * per_page).limit(per_page).all()

            return schemas.FormesCourriersResponseList(
                total=total,
                pages=math.ceil(total / per_page),
                per_page=per_page,
                current_page=page,
                data=record_query
            )

Forme=CRUDFormesCourriers(models.FormesCourriers)
    
    