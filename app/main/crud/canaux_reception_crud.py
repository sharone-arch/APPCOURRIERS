import math  # Pour des calculs mathématiques comme ceil (arrondi supérieur)
import bcrypt  # Pour gérer le hachage des mots de passe (non utilisé ici directement)
from fastapi import HTTPException  # Pour lever des exceptions HTTP (erreurs API)
from sqlalchemy import or_  # Pour faire des filtres SQL avec des OR
import re  # Expressions régulières (non utilisé ici)
from typing import List, Optional, Union  # Typage Python
import uuid  # Pour générer des UUID uniques
from app.main.core.i18n import __  # Fonction pour la traduction des messages
from app.main.core.security import generate_password, get_password_hash,verify_password  # Fonctions sécurité (pas utilisées ici)
from sqlalchemy.orm import Session  # Objet session pour manipuler la base
from app.main.crud.base import CRUDBase  # Classe de base pour CRUD
from app.main import models, schemas  # Modèles ORM et schémas Pydantic
from app.main.core.mail import send_account_creation_email  # Envoi email (non utilisé ici)


# Définition de la classe CRUD spécifique au modèle CanauxReceptionCourier
class CRUDCanauxReceptionCourier(CRUDBase[models.CanauxReceptionCourier, schemas.CanauxReceptionCreate, schemas.CanauxReceptionUpdate]):

    # Récupérer un canal via son UUID et non supprimé (is_deleted = False)
    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        return db.query(models.CanauxReceptionCourier)\
                 .filter(models.CanauxReceptionCourier.uuid == uuid, models.CanauxReceptionCourier.is_deleted==False)\
                 .first()

    # Récupérer un canal via son nom (name) et non supprimé
    @classmethod
    def get_by_name(cls, db: Session, *, name: str):
        return db.query(models.CanauxReceptionCourier)\
                 .filter(models.CanauxReceptionCourier.name == name, models.CanauxReceptionCourier.is_deleted==False)\
                 .first()

    # Créer un nouveau canal avec un UUID généré et ajouté par 'added_by'
    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.CanauxReceptionCreate, added_by: str):
        new_canaux = models.CanauxReceptionCourier(
            uuid=str(uuid.uuid4()),  # Génère un UUID unique au format string
            name=obj_in.name,  # Nom du canal depuis l'entrée utilisateur
            added_by=added_by,  # Utilisateur qui a ajouté ce canal
        )
        db.add(new_canaux)  # Ajoute le nouvel objet à la session DB
        db.commit()  # Valide la transaction dans la base
        db.refresh(new_canaux)  # Recharge l'objet pour récupérer les valeurs mises à jour (ex: id)
        return new_canaux  # Retourne l'objet créé

    # Mettre à jour un canal existant selon son UUID
    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.CanauxReceptionUpdate, added_by: str):
        canaux = cls.get_by_uuid(db=db, uuid=obj_in.uuid)  # Récupère le canal à mettre à jour
        if not canaux:  # Si le canal n'existe pas
            raise HTTPException(status_code=404, detail=__(key="canaux-not-found"))  # Erreur 404

        canaux.name = obj_in.name if obj_in.name else canaux.name  # Met à jour le nom si fourni
        added_by = added_by  # Cette ligne semble sans effet (peut-être à revoir)
        db.flush()  # Applique les changements à la session (sans commit)
        db.commit()  # Valide la transaction
        db.refresh(canaux)  # Recharge l'objet mis à jour
        return canaux  # Retourne le canal mis à jour

    # Suppression logique (soft delete) d'un canal en mettant is_deleted à True
    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str) -> None:
        canaux = cls.get_by_uuid(db=db, uuid=uuid)  # Trouve le canal
        if not canaux:  # Si pas trouvé
            raise HTTPException(status_code=404, detail=__(key="canaux-not-found"))  # Erreur 404
        canaux.is_deleted = True  # Marque comme supprimé
        db.commit()  # Valide

    # Suppression physique d'un canal dans la base (DELETE SQL)
    @classmethod
    def delete(cls, db: Session, *, uuid: str) -> None:
        canaux = cls.get_by_uuid(db=db, uuid=uuid)  # Cherche le canal
        if not canaux:
            raise HTTPException(status_code=404, detail=__(key="canaux-not-found"))  # Erreur 404
        db.delete  # Cette ligne devrait être db.delete(canaux) pour supprimer l'objet
        db.commit()  # Valide la suppression

    # Récupérer tous les canaux non supprimés
    @classmethod
    def get_all(cls, db: Session) -> List[models.CanauxReceptionCourier]:
        return db.query(models.CanauxReceptionCourier)\
                 .filter(models.CanauxReceptionCourier.is_deleted == False)\
                 .all()

    # Récupérer plusieurs canaux avec pagination, tri, et recherche par mot-clé
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
            if page < 1:  # S'assure que la page est au moins 1
                page = 1

            # Base de la requête : canaux non supprimés
            record_query = db.query(models.CanauxReceptionCourier).filter(models.CanauxReceptionCourier.is_deleted == False)

            # Si un mot-clé est donné, filtre par nom qui contient ce mot-clé (insensible à la casse)
            if keyword:
                record_query = record_query.filter(
                    or_(
                        models.CanauxReceptionCourier.name.ilike(f"%{keyword}%")
                    )
                )

            # Gestion du tri si order et order_field sont valides
            if order and order_field and hasattr(models.CanauxReceptionCourier, order_field):
                if order.lower() == "asc":
                    record_query = record_query.order_by(getattr(models.CanauxReceptionCourier, order_field).asc())
                else:
                    record_query = record_query.order_by(getattr(models.CanauxReceptionCourier, order_field).desc())

            total = record_query.count()  # Compte total des résultats (avant pagination)

            # Applique la pagination : offset + limit
            record_query = record_query.offset((page - 1) * per_page).limit(per_page).all()

            # Retourne un schéma personnalisé avec infos de pagination et données
            return schemas.CanauxReceptionCourierList(
                total=total,  # Nombre total de résultats
                pages=math.ceil(total / per_page),  # Nombre total de pages
                per_page=per_page,  # Nombre d'éléments par page
                current_page=page,  # Page courante
                data=record_query  # Liste des canaux récupérés
            )

# Instanciation (optionnelle ici) de la classe CRUD avec le modèle
canaux= CRUDCanauxReceptionCourier(models.CanauxReceptionCourier)
