import uuid
import math
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.main.crud.base import CRUDBase
from app.main import models, schemas
from typing import Optional


class CRUDOutgoingMail(CRUDBase[models.OutgoingMail, schemas.OutgoingMailCreate, schemas.OutgoingMailUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: uuid.UUID):
        mail = db.query(models.OutgoingMail).filter(models.OutgoingMail.uuid == uuid, models.OutgoingMail.is_deleted == False).first()
        if not mail:
            raise HTTPException(status_code=404, detail="Courrier départ introuvable")
        return mail

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.OutgoingMailCreate):
        db_obj = models.OutgoingMail(
            uuid=uuid.uuid4(),
            reference=obj_in.reference,
            entity_name=obj_in.entity_name,
            action_name=obj_in.action_name,
            performed_by=obj_in.performed_by,
            is_deleted=obj_in.is_deleted or False,
            created_at=datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def update(cls, db: Session, *, uuid: uuid.UUID, obj_in: schemas.OutgoingMailUpdate):
        db_obj = cls.get_by_uuid(db, uuid=uuid)

        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def delete(cls, db: Session, *, uuid: uuid.UUID):
        db_obj = cls.get_by_uuid(db, uuid=uuid)
        # Soft delete by setting is_deleted to True
        db_obj.is_deleted = True
        db.commit()
        return {"detail": "Courrier départ supprimé avec succès"}

    @classmethod
    def get_all(cls, db: Session):
        return db.query(models.OutgoingMail).filter(models.OutgoingMail.is_deleted == False).all()

    @classmethod
    def get_many(
        cls,
        *,
        db: Session,
        page: int = 1,
        per_page: int = 10,
        order: str = "desc",
        keyword: Optional[str] = None
    ):
        query = db.query(models.OutgoingMail).filter(models.OutgoingMail.is_deleted == False)

        if keyword:
            query = query.filter(
                or_(
                    models.OutgoingMail.reference.ilike(f"%{keyword}%"),
                    models.OutgoingMail.entity_name.ilike(f"%{keyword}%"),
                    models.OutgoingMail.action_name.ilike(f"%{keyword}%"),
                    models.OutgoingMail.performed_by.ilike(f"%{keyword}%")
                )
            )

        if order.lower() == "asc":
            query = query.order_by(models.OutgoingMail.created_at.asc())
        else:
            query = query.order_by(models.OutgoingMail.created_at.desc())

        total = query.count()
        data = query.offset((page - 1) * per_page).limit(per_page).all()

        return schemas.OutgoingMailResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=data
        )


# Instanciation
outgoing_mail = CRUDOutgoingMail(models.OutgoingMail)
