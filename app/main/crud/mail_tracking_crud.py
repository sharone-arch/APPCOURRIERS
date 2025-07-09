from datetime import datetime
import math
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import uuid

from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from app.main import models, schemas


class CRUDMailTracking(CRUDBase[models.MailTracking, schemas.MailTrackingBase, schemas.MailTrackingCreate]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        return db.query(models.MailTracking).filter(
            models.MailTracking.uuid == uuid,
            models.MailTracking.is_deleted == False
        ).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.MailTrackingCreate, updated_by_uuid: Optional[str] = None):
        # Vérification de l’existence du mail
        mail = db.query(models.Mail).filter(
            models.Mail.uuid == obj_in.mail_uuid
        ).first()

        if not mail:
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))

        # Création de l’objet
        db_obj = models.MailTracking(
            uuid=str(uuid.uuid4()),
            mail_uuid=obj_in.mail_uuid,
            status=obj_in.status,
            updated_by_uuid=updated_by_uuid,
            changed_at=datetime.now()
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def get_many(
        cls,
        db: Session,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = None,
        keyword: Optional[str] = None
    ):
        query = db.query(models.MailTracking).filter(
            models.MailTracking.is_deleted == False
        )

        if keyword:
            query = query.filter(
                or_(
                    models.MailTracking.status.ilike(f'%{keyword}%'),
                    models.MailTracking.mail_uuid.ilike(f'%{keyword}%')
                )
            )

        if order and order.lower() == "asc":
            query = query.order_by(models.MailTracking.created_at.asc())
        elif order and order.lower() == "desc":
            query = query.order_by(models.MailTracking.created_at.desc())

        total = query.count()
        records = query.offset((page - 1) * per_page).limit(per_page).all()

        return schemas.MailTrackingResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=records
        )


# Instance à utiliser
mail_tracking = CRUDMailTracking(models.MailTracking)
