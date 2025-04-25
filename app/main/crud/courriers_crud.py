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



class CRUDCourriers(CRUDBase[models.Courriers, schemas.CourriersBaseCreate, schemas.CourriersBaseUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str) : 
        return db.query(models.Courriers).filter(models.Courriers.uuid == uuid ,models.Courriers.is_deleted==False).first()
    
    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.CourriersBaseCreate,created_by:str):
        new_courrier = models.Courriers(
            uuid=str(uuid.uuid4()),
            titre=obj_in.titre,
            date_arrivee=obj_in.date_arrivee,
            date_depart=obj_in.date_depart,
            contenu=obj_in.contenu,
            created_by=created_by,
        )
        db.add(new_courrier)
        db.commit()
        db.refresh(new_courrier)
        return new_courrier

    @classmethod
    def update(cls, db: Session, *, uuid: str, obj_in: schemas.CourriersBaseUpdate) -> models.courriers:
        Courriers = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not Courriers:
            raise HTTPException(status_code=404, detail=__(key="courriers-not-found"))
       
        db.flush()
        db.commit()
        db.refresh(Courriers)
        return Courriers

    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str) -> None:
        Courriers = cls.get_by_uuid(db=db, uuid=uuid)
        if not Courriers:
            raise HTTPException(status_code=404, detail=__(key="courriers-not-found"))
        Courriers.is_deleted = True
        db.commit()
        
    
    @classmethod
    def delete(cls, db: Session, *, uuid: str) -> None:
        Courriers = cls.get_by_uuid(db=db, uuid=uuid)
        if not Courriers:
            raise HTTPException(status_code=404, detail=__(key="courriers-not-found"))
        db.delete
        db.commit()
        


    

    @classmethod
    def get_all(cls, db: Session) -> List[ models.Courriers]:
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

            record_query = db.query(models.courriers).filter(models.Courriers.is_deleted == False)

            if keyword:
                record_query = record_query.filter(
                    or_(
                        models.CanauxReceptionCourier.name.ilike(f"%{keyword}%")
                    )
                )

            if order and order_field and hasattr(models.courriers, order_field):
                if order.lower() == "asc":
                    record_query = record_query.order_by(getattr(models.courriers, order_field).asc())
                else:
                    record_query = record_query.order_by(getattr(models.courriers, order_field).desc())
            total = record_query.count()
            record_query = record_query.offset((page - 1) * per_page).limit(per_page).all()

            return schemas.CourriersResponseList(
                total=total,
                pages=math.ceil(total / per_page),
                per_page=per_page,
                current_page=page,
                data=record_query
            )

Courriers= CRUDCourriers(models.courriers)