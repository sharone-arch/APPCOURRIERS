import math
import bcrypt
from fastapi import HTTPException
from sqlalchemy import or_
import re
from typing import List, Optional, Union
import uuid
from app.main.core.i18n import __
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import models,schemas,crud
class CRUDCourriers(CRUDBase[models.Courriers, schemas.CourrierBase, schemas.CourierCreate]):

    @classmethod
    def get_by_uuid(cls, db: Session, *, uuid: str) : 
        return db.query(models.Courriers).filter(models.Courriers.uuid == uuid ,models.Courriers.is_deleted==False).first()
    
    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.CourierCreate,created_by:str):
        db_obj = Courriers(
            uuid=str(uuid.uuid4()),
            titre=obj_in.titre,
            document_uuid=obj_in.document_uuid if obj_in.document_uuid else None,
            contenu=obj_in.contenu,
            type_courrier_uuid=obj_in.type_courrier_uuid,
            nature_courrier_uuid=obj_in.nature_courrier_uuid,
            canal_reception_uuid=obj_in.canal_reception_uuid,
            created_by = created_by
        )
        if obj_in.destinataire_type == "Interne":
            departments = crud.departments.get_by_uuid(db=db,uuid=obj_in.destinataire_uuid).first()
            if not departments:
                raise HTTPException(status_code=404, detail=__(key="departments-not-found"))
            obj_in.destinataire_type = "interne"  # On assigne "interne" au destinataire
            obj_in.destinataire_uuid = departments.uuid  # L'UUID du département sélectionné

        elif obj_in.destinataire_type == "externe":
            # Gestion des destinataires externes (clients, fournisseurs, partenaires)
            externe = crud.externe.get_by_uuid(db=db, uuid=obj_in.destinataire_uuid).first()
            if not externe:
                raise HTTPException(status_code=404, detail=__(key="externe-not-found"))
            obj_in.destinataire_type = "externe"  # On assigne "externe" au destinataire
            obj_in.destinataire_uuid = externe.uuid  # L'UUID de l'externe sélectionné
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    

    @classmethod
    def update(cls, db: Session, *, obj_in: schemas.CourrierUdpdate,created_by:str):
        db_obj = cls.get_by_uuid(db=db,uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404, detail=__(key="courrier-not-found"))
        db_obj.titre = obj_in.titre if obj_in.titre else db_obj.titre
        db_obj.document_uuid = obj_in.document_uuid if obj_in.document_uuid else db_obj.document_uuid 
        db_obj.contenu = obj_in.contenu if obj_in.contenu else db_obj.contenu
        db_obj.type_courrier_uuid = obj_in.type_courrier_uuid if obj_in.type_courrier_uuid else db_obj.type_courrier_uuid
        db_obj.nature_courrier_uuid = obj_in.nature_courrier_uuid if obj_in.nature_courrier_uuid else db_obj.nature_courrier_uuid
        db_obj.canal_reception_uuid = obj_in.canal_reception_uuid if obj_in.canal_reception_uuid else db_obj.canal_reception_uuid
        created_by = created_by
        if obj_in.destinataire_type == "Interne":
            departments = crud.departments.get_by_uuid(db=db,uuid=obj_in.destinataire_uuid).first()
            if not departments:
                raise HTTPException(status_code=404, detail=__(key="departments-not-found"))
            obj_in.destinataire_type = "interne"  # On assigne "interne" au destinataire
            obj_in.destinataire_uuid = departments.uuid  # L'UUID du département sélectionné

        elif obj_in.destinataire_type == "externe":
            # Gestion des destinataires externes (clients, fournisseurs, partenaires)
            externe = crud.externe.get_by_uuid(db=db, uuid=obj_in.destinataire_uuid).first()
            if not externe:
                raise HTTPException(status_code=404, detail=__(key="externe-not-found"))
            obj_in.destinataire_type = "externe"  # On assigne "externe" au destinataire
            obj_in.destinataire_uuid = externe.uuid  # L'UUID de l'externe sélectionné
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
        db.refresh(db_obj)
        return db_obj
    
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
        record_query = db.query(models.Courriers).filter(models.Courriers.is_deleted == False)
        if keyword:
            record_query = record_query.filter(
                or_(
                    models.Courriers.titre.ilike('%' + str(keyword) + '%'),
                    models.Courriers.contenu.ilike('%' + str(keyword) + '%'),

                )
            )
        if status:
            record_query = record_query.filter(models.Courriers.status == status)
        
        if order and order.lower() == "asc":
            record_query = record_query.order_by(models.Courriers.date_added.asc())
        
        elif order and order.lower() == "desc":
            record_query = record_query.order_by(models.Courriers.date_added.desc())
        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.CourrierResponseList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )
    
Courriers= CRUDCourriers(models.courriers)