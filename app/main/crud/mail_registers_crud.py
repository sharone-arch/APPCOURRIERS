from datetime import datetime
import math
from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.main.core.i18n import __  # Pour les messages d'erreur traduits
from app.main.crud.base import CRUDBase
from app.main import models, schemas, crud  # Import des modules de modèles, schémas et autres CRUDs


class CRUDRegistresCourriers(
    CRUDBase[
        models.RegistresCourriers,
        schemas.RegistresCourriersBase,
        schemas.RegistresCourriersCreate
    ]
):
    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        # Recherche un registre par son UUID s'il n'est pas supprimé
        return db.query(models.RegistresCourriers).filter(
            models.RegistresCourriers.uuid == uuid,
            models.RegistresCourriers.is_deleted == False
        ).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.RegistresCourriersCreate, added_by: str):
        # Vérifier si le mail existe
        mail = crud.courriers.get_by_uuid(db=db, uuid=obj_in.mail_uuid)
        if not mail:
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))

        # Création d'un nouvel objet RegistresCourriers
        db_obj = models.RegistresCourriers(
            uuid=str(uuid.uuid4()),
            mail_uuid=obj_in.mail_uuid,
            register_type=obj_in.register_type,
            added_by=added_by
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
        # Requête de base : récupérer les enregistrements non supprimés
        record_query = db.query(models.RegistresCourriers).filter(
            models.RegistresCourriers.is_deleted == False
        )

        # Filtrer si un mot-clé est donné (par exemple sur le type d'enregistrement)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.RegistresCourriers.register_type.ilike('%' + str(keyword) + '%'),
                )
            )

        # Ordre des résultats
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.RegistresCourriers.created_at.asc())
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.RegistresCourriers.created_at.desc())

        # Total pour pagination
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.RegistresCourriersResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query.all()
        )


# Instanciation de la classe CRUD
registres_courriers = CRUDRegistresCourriers(models.RegistresCourriers)
