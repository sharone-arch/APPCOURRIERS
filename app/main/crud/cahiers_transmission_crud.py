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
from app.main.core.mail import notify_admin_new_couriers



class CRUDCahierTransmission(CRUDBase[models.CahierTransmission,schemas.CahierTransmissionCreate,schemas.CahierTransmissionResponseList]):

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str):
        return db.query(models.CahierTransmission).filter(models.CahierTransmission.uuid==uuid,models.CahierTransmission.is_deleted==False)
    
    @classmethod
    def create(cls, db: Session, *, obj_in: schemas.CahierTransmissionCreate, transmis_par: str):
        # Récupération du courrier
        courrier = crud.courriers.get_by_uuid(db=db, uuid=obj_in.courrier_uuid)
        if not courrier:
            raise HTTPException(status_code=404, detail=__(key="courrier-not-found"))

        # Initialisation de la variable
        transmis_a = None

        # Déduction du destinataire
        if courrier.destinataire_type == "interne":
            department = crud.departments.get_by_uuid(db=db, uuid=courrier.destinataire_uuid).first()
            if not department:
                raise HTTPException(status_code=404, detail=__(key="departments-not-found"))
            transmis_a = department.uuid

        elif courrier.destinataire_type == "externe":
            externe = crud.externe.get_by_uuid(db=db, uuid=courrier.destinataire_uuid).first()
            if not externe:
                raise HTTPException(status_code=404, detail=__(key="externe-not-found"))
            transmis_a = externe.uuid

        else:
            raise HTTPException(status_code=400, detail="Type de destinataire invalide")

        # Création de l’enregistrement dans le Cahier de Transmission
        db_obj = models.CahierTransmission(
            uuid=str(uuid.uuid4()),
            courrier_uuid=obj_in.courrier_uuid,
            transmis_par=transmis_par,
            transmis_a=transmis_a,
            remarques=obj_in.remarques if obj_in.remarques else None
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
