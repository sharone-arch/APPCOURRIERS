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

class CRUDCanauxReceptionCourier(CRUDBase[models.CanauxReceptionCourier, schemas.CanauxReceptionCourierCreate, schemas.CanauxReceptionCourierUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        return db.query(models.CanauxReceptionCourier).filter(models.CanauxReceptionCourier.uuid == uuid,models.CanauxReceptionCourier.is_deleted==False).first()
    @classmethod
    def get_by_name(cls, db: Session, *, name: str):
        return db.query(models.CanauxReceptionCourier).filter(models.CanauxReceptionCourier.name == name,models.CanauxReceptionCourier.is_deleted==False).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.CanauxReceptionCourierCreate,added_by:str):
        new_canaux = models.CanauxReceptionCourier(
            uuid=str(uuid.uuid4()),
            name=obj_in.name,
            added_by=added_by,  # Initialement non supprimé
        )
        db.add(new_canaux)
        db.commit()
        db.refresh(new_canaux)
        return new_canaux

    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.CanauxReceptionCourierUpdate,added_by:str) -> models.CanauxReceptionCourier:
        canaux = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not canaux:
            raise HTTPException(status_code=404, detail=__(key="canaux-not-found"))
       
        canaux.name = obj_in.name if obj_in.name else canaux.name
        added_by = added_by
        db.flush()
        db.commit()
        db.refresh(canaux)
        return canaux

    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str) -> None:
        canaux = cls.get_by_uuid(db=db, uuid=uuid)
        if not canaux:
            raise HTTPException(status_code=404, detail=__(key="canaux-not-found"))
        canaux.is_deleted = True
        db.commit()
        
    
    @classmethod
    def delete(cls, db: Session, *, uuid: str) -> None:
        canaux = cls.get_by_uuid(db=db, uuid=uuid)
        if not canaux:
            raise HTTPException(status_code=404, detail=__(key="canaux-not-found"))
        db.delete
        db.commit()
        


    

    @classmethod
    def get_all(cls, db: Session) -> List[models.CanauxReceptionCourier]:
        return db.query(models.CanauxReceptionCourier).filter(models.CanauxReceptionCourier.is_deleted == False).all()

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

            record_query = db.query(models.CanauxReceptionCourier).filter(models.CanauxReceptionCourier.is_deleted == False)

            if keyword:
                record_query = record_query.filter(
                    or_(
                        models.CanauxReceptionCourier.name.ilike(f"%{keyword}%")
                    )
                )

            if order and order_field and hasattr(models.CanauxReceptionCourier, order_field):
                if order.lower() == "asc":
                    record_query = record_query.order_by(getattr(models.CanauxReceptionCourier, order_field).asc())
                else:
                    record_query = record_query.order_by(getattr(models.CanauxReceptionCourier, order_field).desc())
            total = record_query.count()
            record_query = record_query.offset((page - 1) * per_page).limit(per_page).all()

            return schemas.CanauxReceptionCourierList(
                total=total,
                pages=math.ceil(total / per_page),
                per_page=per_page,
                current_page=page,
                data=record_query
            )

canaux= CRUDCanauxReceptionCourier(models.CanauxReceptionCourier)