import math  # Pour les calculs mathématiques (ex: arrondi supérieur)
import bcrypt  # Pour le hashage (non utilisé dans ce code)
from fastapi import HTTPException  # Pour lever des erreurs HTTP dans FastAPI
from sqlalchemy import or_  # Pour faire des filtres OR dans les requêtes SQLAlchemy
import re  # Expressions régulières (non utilisé ici)
from typing import List, Optional, Union  # Types d’annotation
import uuid  # Générer des UUID uniques
from app.main.core.i18n import __  # Fonction d’internationalisation (messages traduits)
from sqlalchemy.orm import Session  # Gestion de session SQLAlchemy
from app.main.crud.base import CRUDBase  # Classe de base CRUD générique
from app.main import models, schemas  # Modèles SQLAlchemy et schémas Pydantic


class CRUDExternes(CRUDBase[models.Externe, schemas.ExterneBase, schemas.ExterneCreate]):
    # CRUD spécifique pour le modèle Externe, avec ses schémas associés

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        # Recherche un externe via son UUID, sans filtre sur is_deleted (à voir si c’est voulu)
        return db.query(models.Externe).filter(models.Externe.uuid == uuid).first()

    @classmethod
    def get_by_name(cls, db: Session, *, name: str):
        # Recherche un externe par son nom et qui n’est pas supprimé (is_deleted=False)
        return db.query(models.Externe).filter(
            models.Externe.name == name,
            models.Externe.is_deleted == False
        ).first()

    @classmethod
    def get_by_email(cls, db: Session, *, email: str):
        # Recherche un externe par email, uniquement ceux non supprimés
        return db.query(models.Externe).filter(
            models.Externe.email == email,
            models.Externe.is_deleted == False
        ).first()

    @classmethod
    def get_by_phone_number(cls, db: Session, *, phone_number: str):
        # Recherche un externe par numéro de téléphone, non supprimé
        return db.query(models.Externe).filter(
            models.Externe.phone_number == phone_number,
            models.Externe.is_deleted == False
        ).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.ExterneCreate, created_by: str):
        # Création d’un nouvel externe
        db_obj = models.Externe(
            uuid=str(uuid.uuid4()),  # Génération d’un UUID unique
            name=obj_in.name,
            email=obj_in.email,
            phone_number=obj_in.phone_number,
            address=obj_in.address,
            type=obj_in.type,
            created_by=created_by  # Enregistre qui a créé cet externe
        )
        db.add(db_obj)  # Ajoute à la session
        db.commit()  # Valide en base
        db.refresh(db_obj)  # Rafraîchit l’objet avec ses infos en base (ex: id)
        return db_obj  # Retourne l’objet créé

    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.ExterneCreate, created_by: str):
        # Mise à jour d’un externe existant via son UUID dans obj_in.uuid
        db_obj = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="externe-not-found"))

        # Mise à jour des champs uniquement s’ils sont fournis dans obj_in
        db_obj.name = obj_in.name if obj_in.name else db_obj.name
        db_obj.email = obj_in.email if obj_in.email else db_obj.email
        db_obj.phone_number = obj_in.phone_number if obj_in.phone_number else db_obj.phone_number
        db_obj.address = obj_in.address if obj_in.address else db_obj.address
        db_obj.type = obj_in.type if obj_in.type else db_obj.type

        # Note : la ligne "created_by = created_by" ne modifie rien, probablement à corriger si tu voulais mettre à jour la propriété
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str):
        # Suppression douce : on marque is_deleted = True
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="externe-not-found"))
        db_obj.is_deleted = True
        db.commit()

    @classmethod
    def delete(cls, db: Session, *, uuid: str):
        # Suppression définitive en base
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="externe-not-found"))
        db.delete(db_obj)
        db.commit()

    @classmethod
    def update_status(cls, db: Session, *, uuid: str, status: str):
        # Met à jour le statut d’un externe
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="externe-not-found"))
        db_obj.status = status
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def get_many(
        cls,
        db: Session,
        page: int = 1,
        per_page: int = 25,
        order: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ):
        # Recherche paginée des externes, avec filtres et tri possibles
        
        # Exclut les externes dont le statut est BLOCKED, et les supprimés
        record_query = db.query(models.Externe).filter(
            models.Externe.status.not_in([models.ExterneStatus.BLOCKED]),
            models.Externe.is_deleted == False
        )
        
        # Filtre par mot-clé sur plusieurs champs (nom, email, type, téléphone)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Externe.name.ilike(f'%{keyword}%'),
                    models.Externe.email.ilike(f'%{keyword}%'),
                    models.Externe.type.ilike(f'%{keyword}%'),
                    models.Externe.phone_number.ilike(f'%{keyword}%'),
                )
            )
        
        # Filtre par statut si fourni
        if status:
            record_query = record_query.filter(models.Externe.status == status)
        
        # Tri par date d’ajout ascendant ou descendant
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Externe.date_added.asc())
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Externe.date_added.desc())

        total = record_query.count()  # Nombre total d’éléments
        # Pagination : offset + limit
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        # Retourne un schéma avec les données paginées + infos de pagination
        return schemas.ExterneResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )


# Instanciation de la classe CRUD pour utilisation dans l’application
externe = CRUDExternes(models.Externe)
