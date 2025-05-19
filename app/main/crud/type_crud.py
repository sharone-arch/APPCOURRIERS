import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_           # Pour les filtres "OU" dans les requêtes
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __   # Pour la traduction / gestion des messages d'erreur
from app.main.core.security import generate_password, get_password_hash, verify_password
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase  # Base CRUD générique
from app.main import models, schemas
from app.main.core.mail import send_account_creation_email


class CRUDTypeCourriers(CRUDBase[models.TypeCourriers, schemas.TypeCourriersCreate, schemas.TypeCourriersUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        # Récupère un TypeCourriers non supprimé par UUID
        return db.query(models.TypeCourriers).filter(
            models.TypeCourriers.uuid == uuid,
            models.TypeCourriers.is_deleted == False
        ).first()

    @classmethod
    def get_by_name(cls, db: Session, *, name: str):
        # Récupère un TypeCourriers non supprimé par son nom
        return db.query(models.TypeCourriers).filter(
            models.TypeCourriers.name == name,
            models.TypeCourriers.is_deleted == False
        ).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.TypeCourriersCreate, created_by: str):
        # Crée un nouveau TypeCourriers avec un UUID unique
        new_Type = models.TypeCourriers(
            uuid=str(uuid.uuid4()),  # Génère un nouvel UUID
            name=obj_in.name,
            created_by=created_by,   # Enregistre qui a créé l'entrée
        )
        db.add(new_Type)            # Ajoute à la session SQLAlchemy
        db.commit()                 # Valide la transaction (insert en base)
        db.refresh(new_Type)        # Rafraîchit l'objet avec les données insérées (ex: timestamps)
        return new_Type             # Retourne l'objet créé

    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.TypeCourriersUpdate, created_by: str):
        # Met à jour un TypeCourriers existant via son UUID
        db_obj = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not db_obj:
            # Erreur 404 si le type courrier n'existe pas
            raise HTTPException(status_code=404, detail=__(key="type-courrier-not-found"))
        # Met à jour le nom seulement s'il est fourni dans obj_in
        db_obj.name = obj_in.name if obj_in.name else db_obj.name
        db.commit()                 # Valide la modification
        db.refresh(db_obj)          # Rafraîchit l'objet mis à jour
        return db_obj               # Retourne l'objet modifié

    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str) -> None:
        # Soft delete : met is_deleted à True au lieu de supprimer physiquement
        Type = cls.get_by_uuid(db=db, uuid=uuid)
        if not Type:
            raise HTTPException(status_code=404, detail=__(key="Type-not-found"))
        Type.is_deleted = True      # Marque comme supprimé
        db.commit()                 # Valide la mise à jour

    @classmethod
    def delete(cls, db: Session, *, uuid: str) -> None:
        # Suppression physique du TypeCourriers de la base
        Type = cls.get_by_uuid(db=db, uuid=uuid)
        if not Type:
            raise HTTPException(status_code=404, detail=__(key="Type-not-found"))
        db.delete(Type)             # Supprime l'objet
        db.commit()                 # Valide la suppression

    @classmethod
    def get_all(cls, db: Session) -> List[models.TypeCourriers]:
        # Récupère tous les TypeCourriers non supprimés
        return db.query(models.TypeCourriers).filter(
            models.TypeCourriers.is_deleted == False
        ).all()

    @classmethod
    def get_many(
        cls,
        db: Session,
        page: int = 1,
        per_page: int = 10,
        order: Optional[str] = None,
        keyword: Optional[str] = None
    ):
        # Recherche avec pagination, filtre par mot clé et tri optionnel
        record_query = db.query(models.TypeCourriers).filter(
            models.TypeCourriers.is_deleted == False
        )

        if keyword:
            # Filtre "OU" sur le nom avec insensibilité à la casse
            record_query = record_query.filter(
                or_(
                    models.TypeCourriers.name.ilike('%' + str(keyword) + '%')
                )
            )

        # Applique le tri sur la date d'ajout si demandé
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.TypeCourriers.date_added.asc())
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.TypeCourriers.date_added.desc())

        total = record_query.count()     # Nombre total d'éléments correspondant
        # Pagination (offset + limit)
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        # Retourne une réponse paginée avec le total, pages, page actuelle et la liste des données
        return schemas.TypeCourriersResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query,
        )


# Instance globale de la classe CRUD pour utiliser dans d'autres modules
type_couriers = CRUDTypeCourriers(models.TypeCourriers)
