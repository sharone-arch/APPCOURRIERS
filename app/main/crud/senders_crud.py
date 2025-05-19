import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __  # Gestion des traductions des messages d’erreur
from app.main.core.security import generate_password, get_password_hash, verify_password
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models, schemas
from app.main.core.mail import send_account_creation_email  # Fonction pour envoyer un email à la création du compte


class CRUDSender(CRUDBase[models.Sender, schemas.SenderCreate, schemas.SenderUpdate]):

    @classmethod
    def get_by_phone_number(cls, db: Session, *, phone_number: str) -> Union[models.User, None]:
        # Recherche un expéditeur via son numéro de téléphone principal
        return db.query(models.Sender).filter(models.Sender.phone_number == phone_number).first()
    
    @classmethod
    def get_by_second_phone_number(cls, db: Session, *, second_phone_number: str) -> Union[models.Sender, None]:
        # Recherche un expéditeur via son deuxième numéro de téléphone
        return db.query(models.Sender).filter(models.Sender.second_phone_number == second_phone_number).first()
    
    @classmethod
    def get_by_email(cls, db: Session, *, email: str) -> Union[models.Sender, None]:
        # Recherche un expéditeur via son email
        return db.query(models.Sender).filter(models.Sender.email == email).first()
    
    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        # Recherche un expéditeur par UUID uniquement s’il n’est pas supprimé (soft delete)
        return db.query(models.Sender).filter(
            models.Sender.uuid == uuid,
            models.Sender.is_deleted == False
        ).first()
    
    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.SenderCreate, added_by: str) -> models.Sender:
        # Création d’un nouvel expéditeur avec un UUID unique
        commond_uuid = str(uuid.uuid4())
        db_obj = models.Sender(
            uuid=commond_uuid,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            phone_number=obj_in.phone_number,
            email=obj_in.email,
            second_phone_number=obj_in.second_phone_number,
            address=obj_in.address,
            avatar_uuid=obj_in.avatar_uuid,
            added_by=added_by,  # Utilisateur qui ajoute cet expéditeur
        )
        # Ajouter dans la session
        db.add(db_obj)
        # Valider la transaction
        db.commit()
        # Rafraîchir l’objet pour récupérer les données générées
        db.refresh(db_obj)

        # Génération d’un mot de passe aléatoire de 8 caractères (à 8 caractères max, ici min et max 8)
        password: str = generate_password(8, 8)
        print(f"User password: {password}")

        # Création d’un utilisateur correspondant à cet expéditeur avec le même UUID
        new_user = models.User(
            uuid=commond_uuid,
            email=obj_in.email,
            phone_number=obj_in.phone_number,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            role=models.UserRole.SENDER,  # Rôle spécifique
            password_hash=get_password_hash(password)  # Hash du mot de passe généré
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Envoi de l’email contenant les infos de connexion avec le mot de passe généré
        send_account_creation_email(
            email_to=obj_in.email,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            password=password
        )

        # Retourner l’expéditeur créé
        return db_obj
    
    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.SenderUpdate, added_by: str):
        # Récupérer l’expéditeur à modifier
        sender = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not sender:
            # Si pas trouvé, retourner une erreur 404
            raise HTTPException(status_code=404, detail=__(key="sender-not-found"))
        
        # Mise à jour des champs s’ils sont fournis, sinon garder les valeurs existantes
        sender.first_name = obj_in.first_name if obj_in.first_name else sender.first_name
        sender.last_name = obj_in.last_name if obj_in.last_name else sender.last_name
        sender.phone_number = obj_in.phone_number if obj_in.phone_number else sender.phone_number
        sender.email = obj_in.email if obj_in.email else sender.email
        sender.second_phone_number = obj_in.second_phone_number if obj_in.second_phone_number else sender.second_phone_number
        sender.address = obj_in.address if obj_in.address else sender.address
        sender.avatar_uuid = obj_in.avatar_uuid if obj_in.avatar_uuid else sender.avatar_uuid

        # Cette ligne ne fait rien d’utile, car ‘added_by’ est local à cette méthode (peut être à corriger)
        added_by = added_by
        
        # Appliquer les changements à la session
        db.flush()
        # Valider les changements
        db.commit()
        # Rafraîchir l’objet mis à jour
        db.refresh(sender)

        # Retourner l’expéditeur mis à jour
        return sender
    
    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str):
        # Suppression soft : marquer l’expéditeur comme supprimé sans le retirer physiquement
        sender = cls.get_by_uuid(db=db, uuid=uuid)
        if not sender:
            # Erreur 404 si non trouvé
            raise HTTPException(status_code=404, detail=__(key="senders-deleted-successfully"))
        sender.is_deleted = True
        db.commit()
    
    @classmethod
    def delete(cls, db: Session, *, uuid: str) -> None:
        # Suppression physique de l’expéditeur
        sender = cls.get_by_uuid(db=db, uuid=uuid)
        if not sender:
            raise HTTPException(status_code=404, detail=__(key="senders-deleted-successfully"))
        db.delete(sender)
        db.commit()

    @classmethod
    def get_all(cls, db: Session) -> List[models.Sender]:
        # Retourner tous les expéditeurs non supprimés
        return db.query(models.Sender).filter(models.Sender.is_deleted == False).all()
    
    @classmethod
    def get_many(
        cls,
        db: Session,
        page: int = 1,
        per_page: int = 25,
        keyword: Optional[str] = None
    ):
        # Requête de base sur les expéditeurs non supprimés
        record_query = db.query(models.Sender).filter(models.Sender.is_deleted == False)

        # Si un mot-clé est donné, filtrer sur plusieurs champs avec un LIKE insensible à la casse
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Sender.last_name.ilike('%' + str(keyword) + '%'),
                    models.Sender.first_name.ilike('%' + str(keyword) + '%'),
                    models.Sender.email.ilike('%' + str(keyword) + '%'),
                    models.Sender.second_phone_number.ilike('%' + str(keyword) + '%'),
                    models.Sender.address.ilike('%' + str(keyword) + '%')
                )
            )

        # Comptage total pour pagination
        total = record_query.count()
        # Appliquer l’offset et la limite pour la pagination
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        # Retourner les résultats dans un schéma paginé
        return schemas.SenderResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )
    

# Instance de la classe CRUD pour l’utilisation dans l’application
sender = CRUDSender(models.Sender)
