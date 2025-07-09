from datetime import datetime
import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __  # Pour la traduction des messages d'erreur
from app.main.core.security import generate_password, get_password_hash, verify_password
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models, schemas, crud  # Import des modules de modèles, schémas et autres CRUDs
from app.main.core.mail import notify_receiver_new_mail, notify_receiver_new_mail_receiver



class CRUDMailTransmission(CRUDBase[models.TransmissionsCourriers, schemas.MailTransmissionBase, schemas.MailTransmissionCreate]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        # Recherche une transmission de courrier par son UUID uniquement si elle n’est pas supprimée
        return db.query(models.TransmissionsCourriers).filter(
            models.TransmissionsCourriers.uuid == uuid,
            models.TransmissionsCourriers.is_deleted == False
        ).first()
    
    @classmethod
    def get_by_transmitted_at(cls, db: Session, *, transmitted_at: datetime):
        # Recherche toutes les transmissions qui ont été faites à une date/heure précise et non supprimées
        return db.query(models.TransmissionsCourriers).filter(
            models.TransmissionsCourriers.transmitted_at == transmitted_at,
            models.TransmissionsCourriers.is_deleted == False
        ).all()
    

    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.MailTransmissionCreate, transmitted_by_uuid: str):
        # Récupérer le courrier correspondant à mail_uuid dans la transmission
        mail = crud.courriers.get_by_uuid(db=db, uuid=obj_in.mail_uuid)
        if not mail:
            # Si le courrier n’existe pas, lever une erreur 404
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))
    
        # Récupérer le destinataire (externe) du courrier
        receiver = crud.externe.get_by_uuid(db=db, uuid=mail.receiver_uuid)
        if not receiver:
            raise HTTPException(status_code=404, detail=__(key="receiver-not-found"))
        
        # Récupérer l’expéditeur (interne) du courrier
        sender = crud.sender.get_by_uuid(db=db, uuid=mail.sender_uuid)
        if not sender:
            raise HTTPException(status_code=404, detail=__(key="sender-not-found"))
        
        # Création d’un nouvel objet TransmissionCourriers avec un UUID unique
        db_obj = models.TransmissionsCourriers(
            uuid=str(uuid.uuid4()),  # Génération d’un UUID unique
            mail_uuid=obj_in.mail_uuid,  # Association à ce courrier
            from_entity_uuid=mail.sender_uuid,  # UUID de l’expéditeur
            to_entity_uuid=mail.receiver_uuid,  # UUID du destinataire
            transmitted_by_uuid=transmitted_by_uuid,  # UUID de l’utilisateur qui transmet
            note=obj_in.note  # Note facultative ajoutée à la transmission
        )
        # Marquer le courrier comme transféré
        mail.is_transferred = True
        # Mettre à jour la date d’envoi à maintenant
        mail.sent_at = datetime.now()
        # Ajouter la nouvelle transmission dans la session de la base
        db.add(db_obj)
        # Valider la transaction (INSERT en base)
        db.commit()
        # Rafraîchir l’objet pour récupérer les champs générés automatiquement
        db.refresh(db_obj)

        # Envoyer un email de notification au destinataire
        notify_receiver_new_mail(
            email_to=receiver.email,  # Email du destinataire
            name=receiver.name,       # Nom du destinataire
            subject=mail.subject,     # Sujet du courrier
            content=mail.content,     # Contenu du courrier
            sender=f"{sender.first_name} {sender.last_name}"  # Nom complet de l’expéditeur
        )
        # Retourner l’objet transmission créé
        return db_obj

    @classmethod
    def send_sender(cls, db: Session, *, obj_in: schemas.MailTransmissionCreate, transmitted_by_uuid: str):
        mail = crud.courriers.get_by_uuid(db=db, uuid=obj_in.mail_uuid)
        if not mail:
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))


        receiver = crud.externe.get_by_uuid(db=db, uuid=mail.receiver_uuid)
        if not receiver:
            raise HTTPException(status_code=404, detail=__(key="receiver-not-found"))


        sender = crud.sender.get_by_uuid(db=db, uuid=mail.sender_uuid)
        if not sender:
            raise HTTPException(status_code=404, detail=__(key="sender-not-found"))


        db_obj = models.TransmissionsCourriers(
            uuid=str(uuid.uuid4()),  # Génération d’un UUID unique
            mail_uuid=obj_in.mail_uuid,  # Association à ce courrier
            from_entity_uuid=mail.receiver_uuid,  # UUID de l’expéditeur
            to_entity_uuid=mail.sender_uuid,  # UUID du destinataire
            transmitted_by_uuid=transmitted_by_uuid,  # UUID de l’utilisateur qui transmet
            note=obj_in.note
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Envoyer un email de notification au destinataire
        notify_receiver_new_mail_receiver(
            email_to=receiver.email,  # Email du destinataire
            name=receiver.name,  # Nom du destinataire
            note=obj_in.note,
            receiver=f"{sender.first_name} {sender.last_name}"  # Nom complet de l’expéditeur
        )

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
        # Construire la requête de base pour récupérer les transmissions non supprimées
        record_query = db.query(models.TransmissionsCourriers).filter(
            models.TransmissionsCourriers.is_deleted == False
        )
        # Si un mot-clé est fourni, filtrer sur le champ note (avec insensibilité à la casse)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.TransmissionsCourriers.note.ilike('%' + str(keyword) + '%'),
                )
            )
        
        # Appliquer l’ordre sur la date d’ajout selon le paramètre `order`
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.TransmissionsCourriers.date_added.asc())
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.TransmissionsCourriers.date_added.desc())

        # Compter le nombre total de résultats pour la pagination
        total = record_query.count()
        # Appliquer l’offset et la limite pour la page demandée
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        # Retourner un objet de réponse avec métadonnées et liste des données
        return schemas.MailTransmissionResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )
    

# Instanciation de la classe CRUD pour être utilisée dans l’application
mail_transmissions = CRUDMailTransmission(models.TransmissionsCourriers)
