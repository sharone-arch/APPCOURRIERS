from datetime import timedelta, datetime
import math
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.security import create_access_token, get_password_hash
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired


router = APIRouter(prefix="/statistics", tags=["statistics"])
@router.get("/count-users", summary="Nombre total d'utilisateurs", description="Renvoie le nombre total d'utilisateurs valides selon leur rôle.")
async def count_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    total_users = db.query(models.User).filter(
        models.User.role.in_(["ADMIN", "EDIMESTRE", "SUPER_ADMIN", "BUREAU_ORDRE", "SECRETAIRE"]),
        models.User.is_deleted == False
    ).count()

    return {"total_users": total_users}



@router.get("/count-mails")
async def count_mails(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    total_mails = db.query(models.Mail).filter(models.Mail.is_deleted == False).count()
    return {"total_mails": total_mails}


@router.get("/count-senders")
async def count_senders(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    total_senders = db.query(models.Sender).filter(models.Sender.is_deleted == False).count()
    return {"total_senders": total_senders}


@router.get("/count-receivers")
async def count_receivers(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["SUPER_ADMIN"]))
):
    total_receivers = db.query(models.Externe).filter(models.Externe.is_deleted == False).count()
    return {"total_receivers": total_receivers}

@router.get("/mail-statistics", summary="Statistiques des courriers par statut")
async def get_mail_statistics(db: Session = Depends(get_db)):
    # Requête groupée par statut
    stats = db.query(
        models.Mail.status,
        func.count(models.Mail.uuid)
    ).filter(
        models.Mail.is_deleted == False,
        models.Mail.status != None
    ).group_by(models.Mail.status).all()

    data = {status: count for status, count in stats}

    for status in models.MailStatus:
        data.setdefault(status.value, 0)

    result = [
        {"status": status, "count": data[status]} for status in models.MailStatus
    ]

    return result