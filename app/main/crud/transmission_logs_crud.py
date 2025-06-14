from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.main.models.transmission_logs import RegistresCourriers
from app.main.schemas.transmission_logs import RegistresCourriersCreate, RegistresCourriersBase


class RegistresCourriersCRUD:
    def get(self, db: Session, uuid: str) -> Optional[RegistresCourriers]:
        return db.query(RegistresCourriers).filter(
            RegistresCourriers.uuid == uuid,
            RegistresCourriers.is_deleted.is_(False) 
        ).first()

    def get_many(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[RegistresCourriers], int]:
        query = db.query(RegistresCourriers).filter(RegistresCourriers.is_deleted.is_(False))
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, db: Session, obj_in: RegistresCourriersCreate) -> RegistresCourriers:
        db_obj = RegistresCourriers(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: RegistresCourriers,
        obj_in: RegistresCourriersBase,
    ) -> RegistresCourriers:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db: Session, db_obj: RegistresCourriers) -> RegistresCourriers:
        db_obj.is_deleted = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


registres_courriers_crud = RegistresCourriersCRUD()
