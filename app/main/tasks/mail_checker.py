
from datetime import timedelta, datetime
import math
from typing import Any, List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.mail import notify_receiver_new_mail
from app.main.core.security import create_access_token, get_password_hash
from app.main.core.config import Config
from app.main.core.dependencies import TokenRequired

def check_urgent_unprocessed_mails():
    db: Session = Depends(get_db),
    now = datetime.utcnow()
    threshold_time = now - timedelta(minutes=30)

    mails = db.query(models.Mail).filter(
        models.Mail.status == models.MailStatus.RECU,
        models.Mail.received_at <= threshold_time,
        models.Mail.nature.has(models.NatureCourriers.name == "Urgent")
    ).all()

    for mail in mails:
        crud.create_notification(
            db=db,
            user_uuid=mail.receiver_uuid,
            title="📨 Courrier URGENT non traité",
            content=f"Le courrier URGENT '{mail.subject}' est toujours au statut RECU après 30 minutes."
        )

    db.close()
