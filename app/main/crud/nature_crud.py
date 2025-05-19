import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __  # Gestion des traductions des messages
from app.main.core.security import generate_password, get_password_hash, verify_password
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models, schemas
from app.main.core.mail import send_account_creation_email  # Fonction d’envoi d’email (non utilisée ici)


class CRUDNatureCourriers(CRUDBase[models.NatureCourriers, schemas.NatureCourriersCreate, schemas.NatureCourriersUpdate]):
    
    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        # Récupérer une nature de courrier par son UUID, uniquement si elle n’est pas supprimée (soft delete)
        return db.query(models.NatureCourriers).filter(
            models.NatureCourriers.uuid == uuid,
            models.NatureCourriers.is_deleted == False
        ).first()
    
    @classmethod
    def get_by_name(cls, db: Session, *, name: str):
        # Récupérer une nature de courrier par son nom, uniquement si elle n’est pas supprimée
        return db.query(models.NatureCourriers).filter(
            models.NatureCourriers.name == name,
            models.NatureCourriers.is_deleted == False
        ).first()
    
    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.NatureCourriersCreate, created_by: str):
        # Créer un nouvel enregistrement NatureCourriers avec un UUID unique et le créateur
        new_Nature = models.NatureCourriers(
            uuid=str(uuid.uuid4()),  # Génération d’un UUID unique
            name=obj_in.name,        # Nom de la nature du courrier à créer
            created_by=created_by,   # Utilisateur qui a créé cette nature
        )
        # Ajouter dans la session de la base de données
        db.add(new_Nature)
        # Valider la transaction (INSERT)
        db.commit()
        # Rafraîchir pour récupérer l’objet complet avec ses attributs générés (ex: id)
        db.refresh(new_Nature)
        # Retourner l’objet créé
        return new_Nature
    

    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.NatureCourriersUpdate, created_by: str) -> models.NatureCourriers:
        # Récupérer la nature de courrier existante par UUID
        Nature = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not Nature:
            # Si inexistante, retourner une erreur 404
            raise HTTPException(status_code=404, detail=__(key="Nature-not-found"))
        # Mettre à jour le nom s’il est fourni, sinon garder l’ancien
        Nature.name = obj_in.name if obj_in.name else Nature.name
        # L’attribut created_by n’est pas modifié ici, cette ligne n'a pas d'effet utile (à vérifier)
        created_by = created_by  
        # Valider les modifications
        db.commit()
        # Rafraîchir l’objet pour avoir les données à jour
        db.refresh(Nature)
        # Retourner l’objet mis à jour
        return Nature
    
    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str) -> None:
        # Récupérer la nature à supprimer (soft delete)
        Nature = cls.get_by_uuid(db=db, uuid=uuid)
        if not Nature:
            # Erreur 404 si non trouvée
            raise HTTPException(status_code=404, detail=__(key="Nature-not-found"))
        # Marquer comme supprimée (flag is_deleted)
        Nature.is_deleted = True
        # Valider la suppression soft
        db.commit()

    @classmethod
    def delete(cls, db: Session, *, uuid: str) -> None:
        # Récupérer la nature à supprimer définitivement
        Nature = cls.get_by_uuid(db=db, uuid=uuid)
        if not Nature:
            raise HTTPException(status_code=404, detail=__(key="Nature-not-found"))
        # Suppression physique en base
        db.delete(Nature)
        # Valider la suppression
        db.commit()

    @classmethod
    def get_all(cls, db: Session) -> List[models.NatureCourriers]:
        # Récupérer toutes les natures non supprimées
        return db.query(models.NatureCourriers).filter(
            models.NatureCourriers.is_deleted == False
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
        # Base de la requête : natures non supprimées
        record_query = db.query(models.NatureCourriers).filter(
            models.NatureCourriers.is_deleted == False
        )
        
        # Si un mot-clé est donné, filtre sur le champ name insensible à la casse
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.NatureCourriers.name.ilike('%' + str(keyword) + '%')
                )
            )
        
        # Trier par date d’ajout si demandé en ascendant
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.NatureCourriers.date_added.asc())
        
        # Trier par date d’ajout si demandé en descendant
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.NatureCourriers.date_added.desc())
        
        # Compter le total pour pagination
        total = record_query.count()
        # Appliquer la pagination (offset + limit)
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)
        
        # Retourner la réponse avec total, pages et les données
        return schemas.NatureCourriersResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )
    
    
# Instancier la classe CRUD pour l’utiliser dans l’application
Nature = CRUDNatureCourriers(models.NatureCourriers)
