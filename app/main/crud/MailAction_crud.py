import uuid
import math
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.main.crud.base import CRUDBase
from app.main import models, schemas


class CRUDMailAction(CRUDBase[models.MailAction, schemas.MailActionCreate, schemas.MailActionUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        action = db.query(models.MailAction).filter(models.MailAction.uuid == uuid).first()
        if not action:
            raise HTTPException(status_code=404, detail="Action introuvable")
        return action

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.MailActionCreate):
        db_obj = models.MailAction(
            uuid=str(uuid.uuid4()),
            mail_uuid=obj_in.mail_uuid,
            actor_uuid=obj_in.actor_uuid,
            action_type=obj_in.action_type,
            comment=obj_in.comment,
            created_at=datetime.now()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def update(cls, db: Session, *, uuid: str, obj_in: schemas.MailActionUpdate):
        db_obj = cls.get_by_uuid(db, uuid=uuid)

        if obj_in.comment is not None:
            db_obj.comment = obj_in.comment
        if obj_in.action_type is not None:
            db_obj.action_type = obj_in.action_type

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
        return db.query(models.MailAction).all()

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
        query = db.query(models.MailAction)

        if keyword:
            query = query.filter(
                or_(
                    models.MailAction.comment.ilike(f"%{keyword}%"),
                    models.MailAction.action_type.ilike(f"%{keyword}%")
                )
            )

        if order.lower() == "asc":
            query = query.order_by(models.MailAction.created_at.asc())
        else:
            query = query.order_by(models.MailAction.created_at.desc())

        total = query.count()
        data = query.offset((page - 1) * per_page).limit(per_page).all()

        return schemas.MailActionResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=data
        )


# Instanciation de la classe
mail_action = CRUDMailAction(models.MailAction)
