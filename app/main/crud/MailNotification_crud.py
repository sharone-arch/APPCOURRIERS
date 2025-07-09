import uuid
import math
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.main.crud.base import CRUDBase
from app.main import models, schemas


class CRUDMailNotification(CRUDBase[models.MailNotification, schemas.MailNotificationCreate, schemas.MailNotificationUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        notif = db.query(models.MailNotification).filter(models.MailNotification.uuid == uuid).first()
        if not notif:
            raise HTTPException(status_code=404, detail="Notification introuvable")
        return notif

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.MailNotificationCreate):
        db_obj = models.MailNotification(
            uuid=str(uuid.uuid4()),
            user_uuid=obj_in.user_uuid,
            mail_uuid=obj_in.mail_uuid,
            message=obj_in.message,
            is_read=obj_in.is_read or False,
            created_at=datetime.now()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def update(cls, db: Session, *, uuid: str, obj_in: schemas.MailNotificationUpdate):
        db_obj = cls.get_by_uuid(db, uuid=uuid)

        if obj_in.message is not None:
            db_obj.message = obj_in.message
        if obj_in.is_read is not None:
            db_obj.is_read = obj_in.is_read

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def delete(cls, db: Session, *, uuid: str):
        db_obj = cls.get_by_uuid(db, uuid=uuid)
        db.delete(db_obj)
        db.commit()
        return {"detail": "Supprimé avec succès"}

    @classmethod
    def get_all(cls, db: Session):
        return db.query(models.MailNotification).all()

    @classmethod
    def get_many(
        cls,
        *,
        db: Session,
        page: int = 1,
        per_page: int = 30,
        order: str = "desc",
        keyword: str = None
    ):
        query = db.query(models.MailNotification)

        if keyword:
            query = query.filter(
                or_(
                    models.MailNotification.message.ilike(f"%{keyword}%")
                )
            )

        if order.lower() == "asc":
            query = query.order_by(models.MailNotification.created_at.asc())
        else:
            query = query.order_by(models.MailNotification.created_at.desc())

        total = query.count()
        data = query.offset((page - 1) * per_page).limit(per_page).all()

        return schemas.MailNotificationResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=data
        )


# Instanciation de la classe
mail_notification = CRUDMailNotification(models.MailNotification)
