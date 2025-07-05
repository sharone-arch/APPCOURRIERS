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
    def get_daily_counter(cls,*,db:Session):
        today_str = datetime.now().strftime("%Y%m%d")
        # Exemple avec SQLAlchemy
        count = db.query(models.Mail).filter(models.Mail.is_deleted==False,models.Mail.created_at.startswith(today_str)).count()
        return count + 1


    @classmethod
    def create(cls, db: Session, *, obj_in:schemas.MailCreate, sender_uuid: str, background_tasks: BackgroundTasks):
        number = generate_random_courrier_code()
        common_uuid = str(uuid.uuid4())
        print(f"Code du nouveau courrier {number}")

        db_obj = models.Mail(
            uuid=common_uuid,
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
        db.add(db_obj)
        db.commit()
        db.flush()  # S'assurer que le Mail est inséré avant la relation

        new_transmission = models.CourrierArrive(
            uuid=str(uuid.uuid4()),
            entite=models.Entite.BUREAU_ORDRE,         # ✅ Utilisation correcte
            action=models.Actions.RECEPTION,           # ✅ Utilisation correcte
            mail_uuid=db_obj.uuid,
            added_by=sender_uuid
        )
        db.add(new_transmission)
        db.commit()
        db.refresh(new_transmission)

        sender = db.query(models.User).filter(models.User.uuid == sender_uuid).first()
        receiver = db.query(models.User).filter(models.User.uuid == obj_in.receiver_uuid).first()
        admins = crud.user.get_all_users(db=db)

        if sender and receiver and admins:
            for admin in admins:
                background_tasks.add_task(
                    notify_admin_new_couriers,
                    email_to=admin.email,
                    name=f"{admin.first_name} {admin.last_name}",
                    subject=obj_in.subject,
                    content=obj_in.content,
                    sender=f"{sender.first_name} {sender.last_name}"
                )

            background_tasks.add_task(
                notify_receiver_new_mail,
                email_to=receiver.email,
                name=f"{receiver.first_name} {receiver.last_name}",
                subject=obj_in.subject,
                content=obj_in.content,
                sender=f"{sender.first_name} {sender.last_name}"
            )

        return db_obj
    
    
    
    
    
    
    
    @classmethod
    def create_admin(cls, db: Session, *, obj_in:schemas.MailCreateAdmin, background_tasks: BackgroundTasks):
        number = generate_random_courrier_code()
        common_uuid = str(uuid.uuid4())
        print(f"Code du nouveau courrier {number}")

        db_obj = models.Mail(
            uuid=common_uuid,
            subject=obj_in.subject,
            content=obj_in.content,
            receiver_uuid=obj_in.receiver_uuid,
            document_uuid=obj_in.document_uuid,
            type_uuid=obj_in.type_uuid,
            nature_uuid=obj_in.nature_uuid,
            forme_uuid=obj_in.forme_uuid,
            canal_reception_uuid=obj_in.canal_reception_uuid,
            sender_uuid=obj_in.sender_uuid,
            number=number
        )
        db.add(db_obj)
        db.commit()
        db.flush()
        sender = db.query(models.User).filter(models.User.uuid == obj_in.sender_uuid).first()

        # Vérification du destinataire et envoi de notification
        receiver = db.query(models.User).filter(models.User.uuid == obj_in.receiver_uuid).first()
        if receiver and receiver.email:
            background_tasks.add_task(
                notify_receiver_new_mail,
                email_to=receiver.email,
                name=receiver.name,
                subject=obj_in.subject,
                content=obj_in.content,
                sender=f"{sender.first_name} {sender.last_name}" if sender else "Inconnu"
            )

        return db_obj
    
    
    @classmethod
    def update_admin(cls, db: Session, *, obj_in: schemas.MailUpdateAdmin):
        db_obj = cls.get_by_uuid(db=db, uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))

        # Mise à jour des champs du mail
        db_obj.subject = obj_in.subject if obj_in.subject else db_obj.subject
        db_obj.content = obj_in.content if obj_in.content else db_obj.content
        db_obj.receiver_uuid = obj_in.receiver_uuid if obj_in.receiver_uuid else db_obj.receiver_uuid
        db_obj.type_uuid = obj_in.type_uuid if obj_in.type_uuid else db_obj.type_uuid
        db_obj.nature_uuid = obj_in.nature_uuid if obj_in.nature_uuid else db_obj.nature_uuid
        db_obj.forme_uuid = obj_in.forme_uuid if obj_in.forme_uuid else db_obj.forme_uuid
        db_obj.canal_reception_uuid = obj_in.canal_reception_uuid if obj_in.canal_reception_uuid else db_obj.canal_reception_uuid
        db_obj.document_uuid = obj_in.document_uuid if obj_in.document_uuid else db_obj.document_uuid
        db_obj.sender_uuid = obj_in.sender_uuid if obj_in.sender_uuid else db_obj.sender_uuid
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    

    @classmethod
    def duplicate_mail(cls,db: Session, uuid_to_duplicate: str, sender_uuid: str):
        original_mail = db.query(models.Mail).filter(models.Mail.uuid == uuid_to_duplicate).first()
        if not original_mail:
            raise HTTPException(status_code=404, detail=__(key="mail-not-found"))
         # Marquer l'original comme duplicata
        original_mail.is_duplicate = True
        db.add(original_mail)
        db.commit()  # commit ici pour sauvegarder la modif sur l'original
        
        db_obj = models.Mail(
            uuid=str(uuid.uuid4()),
            subject=original_mail.subject,
            content=original_mail.content,
            receiver_uuid=original_mail.receiver_uuid,
            document_uuid=original_mail.document_uuid,
            type_uuid=original_mail.type_uuid,
            nature_uuid=original_mail.nature_uuid,
            forme_uuid=original_mail.forme_uuid,
            canal_reception_uuid=original_mail.canal_reception_uuid,
            sender_uuid=sender_uuid,  # l'expéditeur qui duplique le courrier
            number=original_mail.number,
            is_duplicate=True  # <-- ici tu marques que c'est une duplication
        )
        db.add(db_obj)
        db.commit()
        return db_obj
            # Récupérer le mail original
    


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

    @classmethod
    def get_receiver_mail(
            cls,
            db: Session,
            page: int = 1,
            per_page: int = 30,
            order: Optional[str] = None,
            status: Optional[str] = None,
            keyword: Optional[str] = None,
            receiver_uuid: Optional[str] = None
    ):
        # Recherche des mails non supprimés envoyés par sender_uuid
        record_query = db.query(models.Mail).filter(models.Mail.is_deleted == False,
                                                    models.Mail.receiver_uuid == receiver_uuid)

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



    @classmethod
    def get_mail_arrive(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        keyword:Optional[str]= None,
    ):
        record_query = db.query(models.CourrierArrive).filter(models.CourrierArrive.is_deleted == False)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.CourrierArrive.action.ilike('%' + str(keyword) + '%'),
                    models.CourrierArrive.entite.ilike('%' + str(keyword) + '%'),

                )
            )
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.CourrierArrive.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.CourrierArrive.date_added.desc())
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.CourrierArriveList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
    
    
courriers= CRUDCourriers(models.courriers)