import smtplib
import logging
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from app.main.core.config import Config

def send_account_creation_email(email_to: str, first_name: str, last_name: str, password: str) -> None:
    try:
        # Charger et rendre le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "account_creation.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            first_name=first_name, last_name=last_name, password=password, project_name=Config.PROJECT_NAME
        )

        # Création et envoi de l'email
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = Config.EMAILS_FROM_CLOUDINARY, email_to, "COURIERLINK | Compte créé"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.MAILTRAP_HOST, Config.MAILTRAP_PORT) as server:
            server.starttls()
            server.login(Config.MAILTRAP_USERNAME, Config.MAILTRAP_PASSWORD)
            server.send_message(msg)

        logging.info(f"Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"Erreur envoi email : {e}")



def send_start_reset_password(email_to: str,name:str ,code:str) -> None:
    try:
        # Charger et rendre le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "start_reset_password.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
           name=name, code=code, project_name=Config.PROJECT_NAME
        )

        # Création et envoi de l'email
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = Config.EMAILS_FROM_CLOUDINARY, email_to, "COURIERLINK | Réinitialisation du mot de passe"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.MAILTRAP_HOST, Config.MAILTRAP_PORT) as server:
            server.starttls()
            server.login(Config.MAILTRAP_USERNAME, Config.MAILTRAP_PASSWORD)
            server.send_message(msg)

        logging.info(f"Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"Erreur envoi email : {e}")



def notify_admin_new_couriers(email_to: str,name: str,subject: str,content: str,sender: str) -> None:
    try:
        # Chargement du template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "notify_admin_new_couriers.html"
        template_content = template_path.read_text(encoding="utf-8")
        template = Template(template_content)

        # Rendu du contenu HTML avec les variables
        html_content = template.render(name=name,project_name=Config.PROJECT_NAME,subject=subject,content=content,sender=sender)
        # Création de l’email
        msg = MIMEMultipart()
        msg["From"] = Config.EMAILS_FROM_CLOUDINARY
        msg["To"] = email_to
        msg["Subject"] = "COURIERLINK | Nouveau courrier reçu"

        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.MAILTRAP_HOST, Config.MAILTRAP_PORT) as server:
            server.starttls()
            server.login(Config.MAILTRAP_USERNAME, Config.MAILTRAP_PASSWORD)
            server.send_message(msg)

        logging.info(f"[INTERNE] Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"[INTERNE] Erreur envoi mail : {e}")


def notify_receiver_new_mail(
    email_to: str,
    name: str,
    subject: str,
    content: str,
    sender: str
) -> None:
    try:
        # Chargement du template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "notify_receiver_new_mail.html"
        template_content = template_path.read_text(encoding="utf-8")
        template = Template(template_content)

        # Rendu du contenu HTML avec les variables
        html_content = template.render(
            name=name,
            project_name=Config.PROJECT_NAME,
            subject=subject,
            content=content,
            sender=sender
        )

        # Construction de l’email
        msg = MIMEMultipart()
        msg["From"] = Config.EMAILS_FROM_CLOUDINARY
        msg["To"] = email_to
        msg["Subject"] = "COURIERLINK | Vous avez reçu un nouveau courrier"

        msg.attach(MIMEText(html_content, "html"))

        # Envoi de l’email via Mailtrap
        with smtplib.SMTP(Config.MAILTRAP_HOST, Config.MAILTRAP_PORT) as server:
            server.starttls()
            server.login(Config.MAILTRAP_USERNAME, Config.MAILTRAP_PASSWORD)
            server.send_message(msg)

        logging.info(f"[RECEIVER] Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"[RECEIVER] Erreur envoi mail : {e}")


def send_reset_password_option2_email(email_to: str, name: str,  otp: str):
    try:
        # Charger et rendre le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "reset_password_option2.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            name=name, otp=otp, project_name=Config.PROJECT_NAME
        )

        # Création et envoi de l'email
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = Config.EMAILS_FROM_CLOUDINARY, email_to, "COURIERLINK | Réinitialisation du mot de passe"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.MAILTRAP_HOST, Config.MAILTRAP_PORT) as server:
            server.starttls()
            server.login(Config.MAILTRAP_USERNAME, Config.MAILTRAP_PASSWORD)
            server.send_message(msg)

        logging.info(f"Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"Erreur envoi email : {e}")


# def send_new_couriers(email_to: str, name: str,  otp: str):
#     try:
#         # Charger et rendre le template HTML
#         template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "new_courrier.html"
#         html_content = Template(template_path.read_text(encoding="utf-8")).render(
#             name=name, otp=otp, project_name=Config.PROJECT_NAME
#         )

#         # Création et envoi de l'email
#         msg = MIMEMultipart()
#         msg["From"], msg["To"], msg["Subject"] = Config.EMAILS_FROM_CLOUDINARY, email_to, "UNIVERSITY GRADES MANAGEMENT SYSTEM | Réinitialisation du mot de passe"
#         msg.attach(MIMEText(html_content, "html"))

#         with smtplib.SMTP(Config.MAILTRAP_HOST, Config.MAILTRAP_PORT) as server:
#             server.starttls()
#             server.login(Config.MAILTRAP_USERNAME, Config.MAILTRAP_PASSWORD)
#             server.send_message(msg)

#         logging.info(f"Email envoyé à {email_to}")

#     except Exception as e:
#         logging.error(f"Erreur envoi email : {e}")