# routers/archive_courrier.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __

router = APIRouter(prefix="/archive-courrier", tags=["archive_courrier"])


@router.post("/create", response_model=schemas.Msg)
async def create_archive_courrier(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ArchiveCourrierCreate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN", "BUREAU_ORDRE"]))
):
    courrier = crud.courriers.get_by_uuid(db, obj_in.courrier_uuid)
    if not courrier:
        raise HTTPException(status_code=404, detail=__(key="courier-not-found"))

    user = crud.user.get_by_uuid(db, obj_in.archive_par_uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__(key="archiver-not-found"))

    crud.archive_courrier.create(db=db, obj_in=obj_in)
    return schemas.Msg(message=__(key="archive-courrier-created"))


@router.get("/get", response_model=schemas.ArchiveCourrier)
async def get_archive_courrier_by_uuid(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    current_user: models.User = Depends(TokenRequired())
):
    archive = crud.archive_courrier.get(db=db, uuid=uuid)
    if not archive:
        raise HTTPException(status_code=404, detail=__(key="archive-courrier-not-found"))
    return archive


@router.get("/get-by-courrier", response_model=list[schemas.ArchiveCourrier])
async def get_by_courrier_uuid(
    *,
    db: Session = Depends(get_db),
    courrier_uuid: str,
    current_user: models.User = Depends(TokenRequired())
):
    return crud.archive_courrier.get_by_courrier_uuid(db=db, courrier_uuid=courrier_uuid)


@router.get("/list", response_model=schemas.ArchiveCourrierResponseList)
async def list_archives(
    *,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    current_user: models.User = Depends(TokenRequired())
):
    skip = (page - 1) * per_page
    data = crud.archive_courrier.get_multi(db=db, skip=skip, limit=per_page)
    total = db.query(models.ArchiveCourrier).count()
    pages = (total + per_page - 1) // per_page
    return schemas.ArchiveCourrierResponseList(
        total=total,
        pages=pages,
        per_page=per_page,
        current_page=page,
        data=data,
    )


@router.put("/update", response_model=schemas.Msg)
async def update_archive_courrier(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    obj_in: schemas.ArchiveCourrierUpdate,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN", "BUREAU_ORDRE"]))
):
    archive = crud.archive_courrier.get(db=db, uuid=uuid)
    if not archive:
        raise HTTPException(status_code=404, detail=__(key="archive-courrier-not-found"))
    
    crud.archive_courrier.update(db=db, db_obj=archive, obj_in=obj_in)
    return schemas.Msg(message=__(key="archive-courrier-updated"))


@router.delete("/delete", response_model=schemas.Msg)
async def delete_archive_courrier(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN", "ADMIN"]))
):
    archive = crud.archive_courrier.get(db=db, uuid=uuid)
    if not archive:
        raise HTTPException(status_code=404, detail=__(key="archive-courrier-not-found"))
    
    crud.archive_courrier.remove(db=db, uuid=uuid)
    return schemas.Msg(message=__(key="archive-courrier-deleted"))
