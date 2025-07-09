# crud/crud_archive_courrier.py

from typing import Optional, List
from uuid import uuid4

from sqlalchemy.orm import Session
from app.main.models.ArchiveCourrier import ArchiveCourrier
from app.main.schemas.ArchiveCourrier import (
    ArchiveCourrierCreate,
    ArchiveCourrierUpdate,
)

class CRUDArchiveCourrier:

    def get(self, db: Session, uuid: str) -> Optional[ArchiveCourrier]:
        return db.query(ArchiveCourrier).filter(ArchiveCourrier.uuid == uuid).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 10) -> List[ArchiveCourrier]:
        return (
            db.query(ArchiveCourrier)
            .order_by(ArchiveCourrier.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_courrier_uuid(self, db: Session, courrier_uuid: str) -> List[ArchiveCourrier]:
        return (
            db.query(ArchiveCourrier)
            .filter(ArchiveCourrier.courrier_uuid == courrier_uuid)
            .order_by(ArchiveCourrier.created_at.desc())
            .all()
        )

    def create(self, db: Session, obj_in: ArchiveCourrierCreate) -> ArchiveCourrier:
        db_obj = ArchiveCourrier(
            uuid=str(uuid4()),
            courrier_uuid=obj_in.courrier_uuid,
            fichier_archive=obj_in.fichier_archive,
            archive_par_uuid=obj_in.archive_par_uuid,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: ArchiveCourrier,
        obj_in: ArchiveCourrierUpdate
    ) -> ArchiveCourrier:
        data = obj_in.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, uuid: str) -> Optional[ArchiveCourrier]:
        obj = self.get(db, uuid)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


archive_courrier = CRUDArchiveCourrier()
