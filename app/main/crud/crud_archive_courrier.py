from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.main.models.archive_courrier import ArchiveCourrier
from app.main.schemas.archive_courrier import (
    ArchiveCourrierCreate,
    ArchiveCourrierUpdate,
)


class CRUDArchiveCourrier:
    def get(self, db: Session, uuid: str) -> Optional[ArchiveCourrier]:
        return db.query(ArchiveCourrier).filter(ArchiveCourrier.uuid == uuid).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10,
    ) -> List[ArchiveCourrier]:
        return (
            db.query(ArchiveCourrier)
            .order_by(ArchiveCourrier.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_courrier(
        self, db: Session, courrier_uuid: str
    ) -> List[ArchiveCourrier]:
        return (
            db.query(ArchiveCourrier)
            .filter(ArchiveCourrier.courrier_uuid == courrier_uuid)
            .order_by(ArchiveCourrier.created_at.desc())
            .all()
        )

    def create(
        self, db: Session, obj_in: ArchiveCourrierCreate
    ) -> ArchiveCourrier:
        db_obj = ArchiveCourrier(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: ArchiveCourrier,
        obj_in: ArchiveCourrierUpdate,
    ) -> ArchiveCourrier:
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, uuid: str) -> Optional[ArchiveCourrier]:
        obj = db.query(ArchiveCourrier).filter(ArchiveCourrier.uuid == uuid).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj


archive_courrier = CRUDArchiveCourrier()
