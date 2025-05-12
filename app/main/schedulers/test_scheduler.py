from app.main.utils import logger


def test_scheduler():
    logger.info("Test scheduler")

def check_urgent_unprocessed_mails():
    db: Session = SessionLocal()
    now = datetime.utcnow()
    threshold_time = now - timedelta(minutes=30)

    mails = db.query(models.Mail).filter(
        models.Mail.status == MailStatus.RECU,
        models.Mail.received_at <= threshold_time,
        models.Mail.nature.has(models.NatureCourriers.label == "URGENT")
    ).all()

    for mail in mails:
        crud.create_notification(
            db=db,
            user_id=mail.receiver_uuid,
            title="📨 Courrier URGENT non traité",
            content=f"Le courrier URGENT '{mail.subject}' est toujours au statut RECU après 30 minutes."
        )

    db.close()
