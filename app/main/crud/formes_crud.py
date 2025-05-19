import math
import uuid
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from app.main import models, schemas


class CRUDFormesCourriers(CRUDBase[models.FormesCourriers, schemas.FormesCourriersCreate, schemas.FormesCourriersUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        # Récupérer une forme courrier par UUID uniquement si elle n’est pas supprimée
        return db.query(models.FormesCourriers).filter(
            models.FormesCourriers.uuid == uuid,
            models.FormesCourriers.is_deleted == False
        ).first()

    @classmethod
    def get_by_name(cls, db: Session, *, name: str):
        # Récupérer une forme courrier par nom, non supprimée
        return db.query(models.FormesCourriers).filter(
            models.FormesCourriers.name == name,
            models.FormesCourriers.is_deleted == False
        ).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.FormesCourriersCreate, added_by: str):
        # Créer une nouvelle forme courrier avec un UUID unique
        db_obj = models.FormesCourriers(
            uuid=str(uuid.uuid4()),
            name=obj_in.name,
            added_by=added_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.FormesCourriersUpdate, added_by: str) -> models.FormesCourriers:
        # Mettre à jour une forme courrier existante
        db_obj = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="Forme-not-found"))
        # Mise à jour du nom si fourni
        db_obj.name = obj_in.name if obj_in.name else db_obj.name
        # Optionnel : mettre à jour 'added_by' si tu veux garder trace de qui modifie
        # db_obj.added_by = added_by
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str) -> None:
        # Suppression douce : marque is_deleted = True
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="Forme-not-found"))
        db_obj.is_deleted = True
        db.commit()

    @classmethod
    def delete(cls, db: Session, *, uuid: str) -> None:
        # Suppression définitive de la forme courrier
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="Forme-not-found"))
        db.delete(db_obj)
        db.commit()

    @classmethod
    def get_all(cls, db: Session) -> List[models.FormesCourriers]:
        # Récupérer toutes les formes courrier non supprimées
        return db.query(models.FormesCourriers).filter(models.FormesCourriers.is_deleted == False).all()

    @classmethod
    def get_many(
        cls,
        *,
        db: Session,
        page: int = 1,
        per_page: int = 10,
        order: Optional[str] = None,
        order_field: Optional[str] = None,
        keyword: Optional[str] = None
    ):
        # Recherche paginée avec filtres et tri
        if page < 1:
            page = 1

        record_query = db.query(models.FormesCourriers).filter(models.FormesCourriers.is_deleted == False)

        # Filtrer par mot-clé sur le champ 'name'
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.FormesCourriers.name.ilike(f"%{keyword}%")
                )
            )

        # Trier si ordre et champ de tri valides
        if order and order_field and hasattr(models.FormesCourriers, order_field):
            col = getattr(models.FormesCourriers, order_field)
            if order.lower() == "asc":
                record_query = record_query.order_by(col.asc())
            else:
                record_query = record_query.order_by(col.desc())

        total = record_query.count()
        results = record_query.offset((page - 1) * per_page).limit(per_page).all()

        # Retourner la liste paginée avec méta infos dans un schéma Pydantic
        return schemas.FormesCourriersResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=results
        )


# Instanciation à utiliser dans l’application
formes_courriers = CRUDFormesCourriers(models.FormesCourriers)
