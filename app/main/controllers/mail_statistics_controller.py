from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __

router = APIRouter(prefix="/mail_statistics", tags=["mail_statistics"])


@router.post("/create", response_model=schemas.Msg)
def create_statistique(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.StatistiquesAutomatiquesCreate,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN", "SUPER_ADMIN"]))
):
    """Créer une statistique automatique pour un courrier"""
    crud.statistiques_automatiques.create(
        db=db,
        obj_in=obj_in,
        added_by_uuid=current_user.uuid
    )
    return {"message": __(key="statistique-created-successfully")}


@router.get("/get-by-uuid/{uuid}", response_model=schemas.StatistiquesAutomatiques)
def get_statistique_by_uuid(
    *,
    db: Session = Depends(get_db),
    uuid: str,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN", "SUPER_ADMIN"]))
):
    """Récupérer une statistique automatique par son UUID"""
    statistique = crud.statistiques_automatiques.get_by_uuid(db=db, uuid=uuid)
    if not statistique:
        raise HTTPException(status_code=404, detail=__(key="statistique-not-found"))
    return statistique


@router.get("/get-many", response_model=schemas.StatistiquesAutomatiquesResponseList)
def get_statistiques(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: Optional[str] = Query(None, enum=["ASC", "DESC"]),
    keyword: Optional[str] = None,
    current_user: models.User = Depends(TokenRequired(roles=["ADMIN", "SUPER_ADMIN"]))
):
    """Récupérer une liste paginée des statistiques automatiques"""
    return crud.statistiques_automatiques.get_many(
        db=db,
        page=page,
        per_page=per_page,
        order=order,
        keyword=keyword
    )
