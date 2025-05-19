from datetime import datetime  # Pour manipuler les dates et heures
import math  # Pour faire des opérations mathématiques (ex: arrondir)
import bcrypt  # Pour le hachage sécurisé (non utilisé dans ce code)
from fastapi import BackgroundTasks, HTTPException  # Pour gérer les tâches en arrière-plan et lever des erreurs HTTP
from sqlalchemy import String, cast, or_  # Outils SQLAlchemy pour manipuler les requêtes SQL
import re  # Expressions régulières (non utilisé dans ce code)
from typing import List, Optional, Union  # Types optionnels et autres
import uuid  # Générer des identifiants uniques
from app.main.core.i18n import __  # Pour la gestion des traductions/messages internationaux
from sqlalchemy.orm import Session  # Session SQLAlchemy pour les transactions avec la base de données
from app.main.core.security import generate_random_courrier_code  # Fonction custom pour générer un code de courrier
from app.main.crud.base import CRUDBase  # Classe de base pour le CRUD (Create Read Update Delete)
from app.main import models, schemas, crud  # Import des modèles, schémas (pydantic) et fonctions CRUD
from app.main.core.mail import notify_admin_new_couriers, notify_receiver_new_mail  # Fonctions pour envoyer des mails
from functools import partial  # Pour créer des fonctions partiellement appliquées (non utilisé dans ce code)
from sqlalchemy.orm import joinedload  # Pour optimiser les requêtes SQL avec chargement des relations

# Définition de la classe CRUDCourriers héritant de CRUDBase avec les types Mail, MailBase, MailDelete
class CRUDCourriers(CRUDBase[models.Mail, schemas.MailBase, schemas.MailDelete]):

    # Méthode pour récupérer un mail via son uuid si il n'est pas supprimé
    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str):
        return db.query(models.Mail).filter(models.Mail.uuid == uuid, models.Mail.is_deleted == False).first()
    
    # Méthode pour récupérer tous les mails associés à un uuid avec chargement des documents liés
    @classmethod
    def get_all_mail_by_uuid(cls, db: Session, *, uuid: str):
        # Utilisation de joinedload pour optimiser la récupération des documents associés
        return db.query(models.Mail).options(joinedload(models.Mail.documents, models.MailDocument.is_deleted == False, models.Mail.uuid == uuid)).filter(models.Mail.is_deleted == False)
    
    # Méthode pour récupérer un mail selon son sujet (unique) et non supprimé
    @classmethod
    def get_by_subject(cls, db: Session, *, subject: str):
        return db.query(models.Mail).filter(models.Mail.subject == subject, models.Mail.is_deleted == False).first()
    
    # Méthode pour compter le nombre de mails créés aujourd'hui (format YYYYMMDD)
    @classmethod
    def get_daily_counter(cls, *, db: Session):
        today_str = datetime.now().strftime("%Y%m%d")  # Date actuelle formatée
        # On compte tous les mails non supprimés créés aujourd'hui (avec début created_at = today_str)
        count = db.query(models.Mail).filter(models.Mail.is_deleted == False, models.Mail.created_at.startswith(today_str)).count()
        return count + 1  # Retourne le compteur incrémenté pour le nouveau mail
    
    # Méthode pour créer un nouveau mail et envoyer des notifications
    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.MailCreate, sender_uuid: str, background_tasks: BackgroundTasks):
        number = generate_random_courrier_code()  # Génère un code unique pour le courrier
        print(f"Code du nouveau courrier {number}")  # Affiche le code généré dans la console

        # Création de l'objet Mail avec toutes les données fournies
        db_obj = models.Mail(
            uuid=str(uuid.uuid4()),  # Génère un UUID unique
            subject=obj_in.subject,
            content=obj_in.content,
            receiver_uuid=obj_in.receiver_uuid,
            document_uuid=obj_in.document_uuid,
            type_uuid=obj_in.type_uuid,
            nature_uuid=obj_in.nature_uuid,
            forme_uuid=obj_in.forme_uuid,
            canal_reception_uuid=obj_in.canal_reception_uuid,
            sender_uuid=sender_uuid,
            number=number
        )
        db.add(db_obj)  # Ajoute l'objet à la session de la base
        db.commit()  # Enregistre la transaction en base
        db.refresh(db_obj)  # Recharge l'objet depuis la base (actualise ses attributs)

        # Récupère les informations de l'expéditeur (sender)
        sender = db.query(models.Sender).filter(models.Sender.uuid == sender_uuid).first()
        if not sender:
            raise HTTPException(status_code=404, detail=__(key="sender-not-found"))  # Erreur si expéditeur non trouvé
        
        # Récupère les informations du destinataire (receiver)
        receiver = db.query(models.Externe).filter(models.Externe.uuid == obj_in.receiver_uuid).first()
        if not receiver:
            raise HTTPException(status_code=404, detail=__(key="receiver-not-found"))  # Erreur si destinataire non trouvé

        # Récupère tous les utilisateurs admins
        admins = crud.user.get_all_users(db=db)
        if not admins:
            raise HTTPException(status_code=404, detail=__(key="admins-not-found"))  # Erreur si aucun admin

        # Pour chaque admin, on ajoute une tâche en arrière-plan pour notifier la création du courrier
        for admin in admins:
            background_tasks.add_task(
                notify_admin_new_couriers,
                email_to=admin.email,
                name=f"{admin.first_name} {admin.last_name}",
                subject=obj_in.subject,
                content=obj_in.content,
                sender=f"{sender.first_name} {sender.last_name}"
            )

        # Ajoute aussi une tâche en arrière-plan pour notifier le destinataire
        background_tasks.add_task(
            notify_receiver_new_mail,
            email_to=receiver.email,
            name=receiver.name,
            subject=obj_in.subject,
            content=obj_in.content,
            sender=f"{sender.first_name} {sender.last_name}"
        )

        return db_obj  # Retourne l'objet créé

    # Méthode pour mettre à jour un mail existant
    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.MailUpdate, sender_uuid: str):
        db_obj = cls.get_by_uuid(db=db, uuid=obj_in.uuid)  # Recherche du mail à mettre à jour
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))  # Erreur si mail non trouvé

        # Mise à jour des champs si ils sont fournis, sinon conserve l'ancienne valeur
        db_obj.subject = obj_in.subject if obj_in.subject else db_obj.subject
        db_obj.content = obj_in.content if obj_in.content else db_obj.content
        db_obj.receiver_uuid = obj_in.receiver_uuid if obj_in.receiver_uuid else db_obj.receiver_uuid
        db_obj.type_uuid = obj_in.type_uuid if obj_in.type_uuid else db_obj.type_uuid
        db_obj.nature_uuid = obj_in.nature_uuid if obj_in.nature_uuid else db_obj.nature_uuid
        db_obj.forme_uuid = obj_in.forme_uuid if obj_in.forme_uuid else db_obj.forme_uuid
        db_obj.canal_reception_uuid = obj_in.canal_reception_uuid if obj_in.canal_reception_uuid else db_obj.canal_reception_uuid
        db_obj.document_uuid = obj_in.document_uuid if obj_in.document_uuid else db_obj.document_uuid
        sender_uuid = sender_uuid  # Pas d'action ici (variable locale non utilisée)
        db.commit()  # Sauvegarde les changements en base
        db.refresh(db_obj)  # Recharge l'objet mis à jour
        return db_obj  # Retourne l'objet mis à jour

    # Méthode pour faire une suppression "soft" (marquer comme supprimé)
    @classmethod
    def soft_delete(cls, db: Session, *, uuid: str):
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)  # Cherche le mail
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))  # Erreur si non trouvé
        db_obj.is_deleted = False  # *** Ici il y a une erreur logique : devrait être True pour marquer supprimé ***
        db.commit()  # Sauvegarde la suppression soft
    
    # Méthode pour suppression définitive (hard delete)
    @classmethod
    def delete(cls, db: Session, *, uuid: str):
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)  # Cherche le mail
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))  # Erreur si non trouvé
        db.delete(db_obj)  # Supprime définitivement
        db.commit()  # Sauvegarde

    # Méthode pour mettre à jour le statut d'un mail
    @classmethod
    def update_status(cls, db: Session, uuid: str, status: str):
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)  # Cherche le mail
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))  # Erreur si non trouvé
        db_obj.status = status  # Modifie le statut
        db.commit()  # Sauvegarde

    # Méthode pour apposer un cachet (= changer statut aussi)
    @classmethod
    def appose_cachet(cls, db: Session, uuid: str, status: str):
        db_obj = cls.get_by_uuid(db=db, uuid=uuid)  # Cherche le mail
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))  # Erreur si non trouvé
        db_obj.status = status  # Change le statut
        db.commit()  # Sauvegarde

    # Méthode pour récupérer plusieurs mails avec filtres, pagination et tri
    @classmethod
    def get_many(
        cls,
        db: Session,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ):
        record_query = db.query(models.Mail).filter(models.Mail.is_deleted == False)  # Base : mails non supprimés
        
        # Si un mot clé est fourni, filtre sur sujet, contenu, destinataire, numéro (avec insensibilité à la casse)
        if keyword:
            record_query = record_query.filter(
                or_(
                    cast(models.Mail.subject, String).ilike('%' + str(keyword) + '%'),
                    cast(models.Mail.content, String).ilike('%' + str(keyword) + '%'),
                    cast(models.Mail.receiver, String).ilike('%' + str(keyword) + '%'),
                    cast(models.Mail.number, String).ilike('%' + str(keyword) + '%'),
                )
            )
        
        # Si un statut est précisé, filtre sur ce statut
        if status:
            record_query = record_query.filter(models.Mail.status == status)
        
        # Tri selon ordre ascendant sur date d'ajout
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Mail.date_added.asc())
        # Tri selon ordre descendant sur date d'ajout
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Mail.date_added.desc())
        
        total = record_query.count()  # Nombre total d'éléments filtrés
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)  # Pagination
        
        # Retourne un schéma contenant la liste et les infos de pagination
        return schemas.MailResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )

    # Méthode pour récupérer les mails d'un expéditeur donné avec filtres, pagination et tri
    @classmethod
    def get_sender_mail(
        cls,
        db: Session,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        sender_uuid: Optional[str] = None
    ):
        # Recherche des mails non supprimés envoyés par sender_uuid
        record_query = db.query(models.Mail).filter(models.Mail.is_deleted == False, models.Mail.sender_uuid == sender_uuid)
        
        # Filtre si mot clé sur sujet ou contenu
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Mail.subject.ilike('%' + str(keyword) + '%'),
                    models.Mail.content.ilike('%' + str(keyword) + '%'),
                )
            )
        
        # Filtre selon statut si précisé
        if status:
            record_query = record_query.filter(models.Mail.status == status)
        
        # Tri ascendant
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Mail.date_added.asc())
        # Tri descendant
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Mail.date_added.desc())
        
        total = record_query.count()  # Total des résultats
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)  # Pagination
        
        # Retourne le schéma pour liste simplifiée de mails envoyés par un expéditeur
        return schemas.MailSlimSenderResponseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )

# Instanciation d'un objet CRUDCourriers lié au modèle 'courriers' (Attention, ici le modèle est 'Mail', il faut vérifier)
courriers = CRUDCourriers(models.courriers)
