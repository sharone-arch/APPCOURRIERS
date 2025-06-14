from datetime import datetime
import math
from fastapi import HTTPException
from sqlalchemy import or_
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from app.main.core.i18n import __  # Pour la traduction des messages d'erreur
from app.main.crud.base import CRUDBase
from app.main import models, schemas, crud  # Import des modèles, schémas, autres CRUD


class CRUDStatistiquesAutomatiques(CRUDBase[
    models.StatistiquesAutomatiques,
    schemas.StatistiquesAutomatiquesBase,
    schemas.StatistiquesAutomatiquesCreate
]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        # Recherche une statistique par UUID uniquement si elle n'est pas supprimée
        return db.query(models.StatistiquesAutomatiques).filter(
            models.StatistiquesAutomatiques.uuid == uuid,
            models.StatistiquesAutomatiques.is_deleted == False
        ).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.StatistiquesAutomatiquesCreate, added_by_uuid: str):
        # Vérifier que le mail existe
        mail = crud.courriers.get_by_uuid(db=db, uuid=obj_in.mail_uuid)
        if not mail:
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))

        # Créer une nouvelle statistique avec UUID unique
        db_obj = models.StatistiquesAutomatiques(
            uuid=str(uuid.uuid4()),
            mail_uuid=obj_in.mail_uuid,
            processing_time=obj_in.processing_time or 0,
            status_log=obj_in.status_log,
            generated_at=obj_in.generated_at,
            added_by=added_by_uuid,
            is_deleted=obj_in.is_deleted or False
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
        # Construire la requête pour récupérer les statistiques non supprimées
        record_query = db.query(models.StatistiquesAutomatiques).filter(
            models.StatistiquesAutomatiques.is_deleted == False
        )

        # Si un mot-clé est donné, filtrer sur status_log (converti en string) ou mail_uuid
        if keyword:
            keyword_like = f"%{keyword}%"
            record_query = record_query.filter(
                or_(
                    models.StatistiquesAutomatiques.mail_uuid.ilike(keyword_like),
                    # Postgres JSONB support: on pourrait filtrer par clé, sinon convertir en string.
                    # Exemple simple : cast to text et filtre LIKE (selon la DB)
                    models.StatistiquesAutomatiques.status_log.cast(String).ilike(keyword_like)
                )
            )

        # Ordre sur la date de création
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.StatistiquesAutomatiques.created_at.asc())
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.StatistiquesAutomatiques.created_at.desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.StatistiquesAutomatiquesResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query.all()
        )


# Instanciation pour utilisation dans l'app
statistiques_automatiques = CRUDStatistiquesAutomatiques(models.StatistiquesAutomatiques)
