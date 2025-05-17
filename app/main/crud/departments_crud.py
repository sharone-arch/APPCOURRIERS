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
from app.main import models,schemas


class CRUDDepartments(CRUDBase[models.Department,schemas.DepartmentCreate,schemas.DepartmentDelete]):

    @classmethod
    def get_by_uuid(cls,db:Session,*,uuid:str):
        return db.query(models.Department).filter(models.Department.uuid==uuid,models.Department.is_deleted==False).first()
    
    @classmethod
    def get_by_name(cls,db:Session,*,name:str):
        return db.query(models.Department).filter(models.Department.name==name,models.Department.is_deleted==False).first()
    @classmethod
    def get_by_email(cls,db:Session,*,email:str):
        return db.query(models.Department).filter(models.Department.email==email,models.Department.is_deleted==False).first()
    
    @classmethod
    def create(cls,db:Session,*,obj_in:schemas.ResponsableCreate,departments:schemas.DepartmentCreate,created_by:str):
        obj_uuid = str(uuid.uuid4())
        db_obj = models.Responsable(
            uuid = obj_uuid,
            first_name = obj_in.first_name,
            last_name = obj_in.last_name,
            email = obj_in.email,
            phone_number = obj_in.phone_number,
            created_by=created_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        obj_departments = models.Department(
            uuid = str(uuid.uuid4()),
            name = departments.name,
            description = departments.description,
            email = departments.email,
            phone_number = departments.phone_number,
            phone_number2=departments.phone_number2,
            responsable_uuid = obj_uuid

        )
        db.add(obj_departments)
        db.commit()
        db.refresh(obj_departments)
        
        return db_obj
    

    @classmethod
    def soft_delete(cls,db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="department-not-found"))
        db_obj.is_deleted = True
        db.commit()

    @classmethod
    def delete(cls,db:Session,*,uuid:str):
        db_obj = cls.get_by_uuid(db=db,uuid=uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="department-not-found"))
        db.delete(db_obj)
        db.commit()

    @classmethod
    def update(cls,db:Session,*,obj_in:schemas.DepartmentsUpdate,created_by:str):
        db_obj = cls.get_by_uuid(db=db,uuid=obj_in.uuid)
        if not db_obj:
            raise HTTPException(status_code=404,detail=__(key="department-not-found"))
        db_obj.name = obj_in.name if obj_in.name else db_obj.name
        db_obj.description = obj_in.description if obj_in.description else db_obj.description
        db_obj.email = obj_in.email if obj_in.email else db_obj.email
        db_obj.phone_number = obj_in.phone_number if obj_in.phone_number else db_obj.phone_number
        db_obj.phone_number2 = obj_in.phone_number2 if obj_in.phone_number2 else db_obj.phone_number2
        db.commit()
        db.refresh(db_obj)
        return db_obj



departments = CRUDDepartments(models.Department)
    





