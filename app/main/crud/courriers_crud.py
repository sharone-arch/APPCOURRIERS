import math
import bcrypt
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models,schemas,crud
from app.main.core.mail import notify_couriers_interne,notify_couriers_externe
class CRUDCourriers(CRUDBase[models.Courriers, schemas.CourierExterne, schemas.CourierExterneSlim]):

    @classmethod
    def get_couriers_interne_by_uuid(cls, db: Session, *, uuid: str) : 
        return db.query(models.CourierInterne).filter(models.CourierInterne.uuid == uuid ,models.CourierInterne.is_deleted==False).first()
    

    @classmethod
    def get_couriers_externe_by_uuid(cls, db: Session, *, uuid: str) : 
        return db.query(models.CourierExterne).filter(models.CourierExterne.uuid == uuid ,models.CourierExterne.is_deleted==False).first()


    @classmethod
    def create(
        cls,
        db: Session,
        *,
        db_obj_in: schemas.CourierInterneCreate,
        obj_in: schemas.CourierExterneCreate,
        created_by: str,
        background_tasks: Optional[BackgroundTasks] = None
    ):
        # Création du courrier selon le type
        if obj_in.type == "Interne":
            new_courier = models.CourierInterne(
                uuid=str(uuid.uuid4()),
                titre=db_obj_in.titre,
                contenu=db_obj_in.contenu,
                document_uuid=db_obj_in.document_uuid if db_obj_in.document_uuid else None,
                destinataire_uuid=db_obj_in.destinataire_uuid,
                type_courrier_uuid=db_obj_in.type_courrier_uuid,
                nature_courrier_uuid=db_obj_in.nature_courrier_uuid,
                canal_reception_uuid=db_obj_in.canal_reception_uuid,
                created_by=created_by
            )
        else:
            new_courier = models.CourierExterne(
                uuid=str(uuid.uuid4()),
                titre=db_obj_in.titre,
                contenu=db_obj_in.contenu,
                document_uuid=db_obj_in.document_uuid if db_obj_in.document_uuid else None,
                destinataire_uuid=db_obj_in.destinataire_uuid,
                type_courrier_uuid=db_obj_in.type_courrier_uuid,
                nature_courrier_uuid=db_obj_in.nature_courrier_uuid,
                canal_reception_uuid=db_obj_in.canal_reception_uuid,
                created_by=created_by
            )

        db.add(new_courier)
        db.commit()
        db.refresh(new_courier)

        # Récupération des admins
        db_admins = db.query(models.User).filter(models.User.role.in_(["ADMIN", "SUPER_ADMIN"]),models.User.is_deleted == False).all()

        # Récupération de l'expéditeur
        sender_info = db.query(models.Sender).filter(models.Sender.uuid == created_by).first()
        if not sender_info:
            raise HTTPException(status_code=404, detail=__(key="expediteur-not-found"))

        sender_formatted = f"{sender_info.first_name} {sender_info.last_name} ({sender_info.phone_number})"

        # Récupération du destinataire selon le type
        if obj_in.type == "Interne":
            destinataire = db.query(models.Department).filter(models.Department.uuid == db_obj_in.destinataire_uuid).first()
            destinataire_email = destinataire.email if destinataire else None
            destinataire_nom = destinataire.name if destinataire else "Département inconnu"
        else:
            destinataire = db.query(models.Externe).filter(models.Externe.uuid == db_obj_in.destinataire_uuid).first()
            destinataire_email = destinataire.email if destinataire else None
            destinataire_nom = destinataire.name if destinataire else "Contact externe inconnu"

        # Envoi de mails aux admins
        for admin in db_admins:
            background_tasks.add_task(
                notify_couriers_interne if obj_in.type == "Interne" else notify_couriers_externe,
                email_to=admin.email,
                name=f"{admin.first_name} {admin.last_name}",
                titre=new_courier.titre,
                contenu=new_courier.contenu,
                sender=sender_formatted,
                receiver=destinataire_email or "N/A",
                type=obj_in.type,
            )

        # Notification directe au destinataire (interne ou externe)
        if destinataire_email:
            background_tasks.add_task(
                notify_couriers_interne if obj_in.type == "Interne" else notify_couriers_externe,
                email_to=destinataire_email,
                name=destinataire_nom,
                titre=new_courier.titre,
                contenu=new_courier.contenu,
                sender=sender_formatted,
                receiver=destinataire_email,
                type=obj_in.type,
            )

        return new_courier

            
        
    

    @classmethod
    def update(
        cls,
        db: Session,
        *,
        db_obj: Union[models.CourierInterne, models.CourierExterne],
        obj_in: Union[schemas.CourierInterneUpdate, schemas.CourierExterneUpdate]
    ):
        update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj



    @classmethod
    def soft_delete(cls,db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="courrier-not-found"))
        db_obj.is_deleted = False
        db.commit()
    
    @classmethod
    def delete(cls,db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="courrier-not-found"))
        db.delete(db_obj)
        db.commit()

    @classmethod
    def update_status(cls,db:Session,uuid:str,status:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="courrier-not-found"))
        db_obj.status = status
        db.commit()
        
    @classmethod
    def appose_cachet(cls,db:Session,uuid:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="courrier-not-found"))
        db_obj.status = models.CourierStatus.ARRIVE
        db.commit()

    
    @classmethod
    def get_many(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = None,
        status:Optional[str] = None,
        keyword:Optional[str]= None
    ):
        record_query = db.query(models.CourierExterne).filter(models.CourierExterne.is_deleted == False)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.CourierExterne.titre.ilike('%' + str(keyword) + '%'),
                    models.CourierExterne.contenu.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.CourierExterne.status == status)
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.CourierExterne.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.CourierExterne.date_added.desc())
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.CourrierExterneResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
courriers= CRUDCourriers(models.courriers)