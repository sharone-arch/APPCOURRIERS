import math
import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Union

from app.main.crud.base import CRUDBase
from app.main import models, schemas
from app.main.core.i18n import __


class CRUDCourriers(CRUDBase[models.Courriers, schemas.CourriersBaseCreate, schemas.CourriersBaseUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str) -> Union[models.Courriers, None]:
        return db.query(models.Courriers).filter(models.Courriers.uuid == uuid).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.CourriersBaseCreate, created_by: Union[str, None] = None) -> models.Courriers:
        new_courrier = models.Courriers(
            uuid=str(uuid.uuid4()),
            titre=obj_in.titre,
            date_arrivee=obj_in.date_arrivee,
            date_depart=obj_in.date_depart,
            contenu=obj_in.contenu,
            statut=obj_in.statut,
            canal_id=obj_in.canal_id,
            created_by=created_by
        )
        db.add(new_courrier)
        db.commit()
        db.refresh(new_courrier)
        return new_courrier

    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.CourriersBaseUpdate) -> models.Courriers:
        courrier = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not courrier:
            raise HTTPException(status_code=404, detail=__(key="courrier-not-found"))

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(courrier, field, value)

        db.commit()
        db.refresh(courrier)
        return courrier

    @classmethod
    def delete(cls, db: Session, *, uuid: str):
        courrier = cls.get_by_uuid(db=db, uuid=uuid)
        if not courrier:
            raise HTTPException(status_code=404, detail=__(key="courrier-not-found"))
        courrier.is_deleted = True
        db.commit()

    @classmethod
    def get_all(cls, db: Session):
        return db.query(models.Courriers).filter(models.Courriers.is_deleted == False).all()

    @classmethod
    def get_many(cls, db: Session, page: int = 1, per_page: int = 10):
        query = db.query(models.Courriers).filter(models.Courriers.is_deleted == False)

        total = query.count()
        records = query.offset((page - 1) * per_page).limit(per_page).all()

        return schemas.CourriersResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=records
        )


courriers = CRUDCourriers(models.Courriers)
