import math  # Import du module math pour des opérations mathématiques, mais ici il n’est pas utilisé
import bcrypt  # Import pour le hashage de mots de passe, non utilisé ici non plus
from fastapi import HTTPException  # Import de l’exception HTTP pour gérer les erreurs HTTP
from sqlalchemy import or_  # Import de la fonction OR pour les filtres SQL
import re  # Import des expressions régulières, non utilisé dans ce code
from typing import List, Optional, Union  # Types pour annotations (Optionnel, List, Union)
import uuid  # Pour générer des UUID uniques
from app.main.core.i18n import __  # Fonction d’internationalisation (traduction) des messages d’erreur
from sqlalchemy.orm import Session  # Pour manipuler la session de la base de données
from app.main.crud.base import CRUDBase  # Classe de base pour le CRUD
from app.main import models, schemas  # Import des modèles et schémas Pydantic


class CRUDDepartments(CRUDBase[models.Department, schemas.DepartmentCreate, schemas.DepartmentDelete]):
    # Cette classe hérite de CRUDBase et ajoute des méthodes spécifiques pour gérer les départements

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        # Recherche un département par son UUID et qui n’est pas supprimé (is_deleted == False)
        return db.query(models.Department).filter(
            models.Department.uuid == uuid,
            models.Department.is_deleted == False
        ).first()

    @classmethod
    def get_by_name(cls, db: Session, *, name: str):
        # Recherche un département par son nom et non supprimé
        return db.query(models.Department).filter(
            models.Department.name == name,
            models.Department.is_deleted == False
        ).first()

    @classmethod
    def get_by_email(cls, db: Session, *, email: str):
        # Recherche un département par son email et non supprimé
        return db.query(models.Department).filter(
            models.Department.email == email,
            models.Department.is_deleted == False
        ).first()

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.ResponsableCreate, departments: schemas.DepartmentCreate, created_by: str):
        # Création d’un responsable et d’un département associé
        obj_uuid = str(uuid.uuid4())  # Génère un UUID unique pour le responsable

        db_obj = models.Responsable(
            uuid=obj_uuid,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            email=obj_in.email,
            phone_number=obj_in.phone_number,
            created_by=created_by  # UUID ou identifiant de l’utilisateur qui crée
        )
        db.add(db_obj)  # Ajoute le responsable à la session
        db.commit()  # Valide la transaction en base
        db.refresh(db_obj)  # Rafraîchit l’objet pour récupérer les données mises à jour (ex: id auto généré)

        # Création d’un département lié à ce responsable
        obj_departments = models.Department(
            uuid=str(uuid.uuid4()),  # Génère un nouvel UUID pour le département
            name=departments.name,
            description=departments.description,
            email=departments.email,
            phone_number=departments.phone_number,
            phone_number2=departments.phone_number2,
            responsable_uuid=obj_uuid  # Lien avec le responsable créé
        )
        db.add(obj_departments)  # Ajoute le département à la session
        db.commit()  # Valide en base
        db.refresh(obj_departments)  # Rafraîchit l’objet département

        return db_obj  # Retourne le responsable créé (pas le département)

    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str):
        # Suppression douce (soft delete) : on ne supprime pas mais on marque is_deleted = True
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)  # Récupère le département par UUID
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="department-not-found"))  # Erreur si non trouvé
        db_obj.is_deleted = True  # Marque comme supprimé
        db.commit()  # Valide la modification

    @classmethod
    def delete(cls, db: Session, *, uuid: str):
        # Suppression définitive de la base
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)  # Recherche le département par UUID
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="department-not-found"))
        db.delete(db_obj)  # Supprime l’objet de la session
        db.commit()  # Valide la suppression en base

    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.DepartmentsUpdate, created_by: str):
        # Mise à jour des informations d’un département
        db_obj = cls.get_by_uuid(db=db, uuid=obj_in.uuid)  # Recherche le département par UUID
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="department-not-found"))
        
        # Mise à jour des champs uniquement si une nouvelle valeur est fournie
        db_obj.name = obj_in.name if obj_in.name else db_obj.name
        db_obj.description = obj_in.description if obj_in.description else db_obj.description
        db_obj.email = obj_in.email if obj_in.email else db_obj.email
        db_obj.phone_number = obj_in.phone_number if obj_in.phone_number else db_obj.phone_number
        db_obj.phone_number2 = obj_in.phone_number2 if obj_in.phone_number2 else db_obj.phone_number2
        
        db.commit()  # Valide les changements
        db.refresh(db_obj)  # Rafraîchit l’objet mis à jour
        return db_obj  # Retourne le département mis à jour


# Instanciation de la classe CRUD pour pouvoir l’utiliser ailleurs dans le code
departments = CRUDDepartments(models.Department)
