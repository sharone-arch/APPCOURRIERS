from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime,Boolean
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum


class UserRole(str, Enum):
    """
    Enumeration for user roles.

    ADMIN: Standard administrator.
    SUPER_ADMIN: Administrator with advanced privileges.
    """
    ADMIN = "ADMIN"
    EDIMESTRE = "EDIMESTRE"
    SUPER_ADMIN = "SUPER_ADMIN"


class UserStatus(str, Enum):
    """
    Enumeration for user statuses.

    ACTIVED: Active user.
    UNACTIVED: Inactive user.
    DELETED: Deleted user.
    BLOCKED: Blocked user.
    """
    ACTIVED = "ACTIVED"
    UNACTIVED = "UNACTIVED"
    BLOCKED = "BLOCKED"


class User(Base):
    _tablename_ = "users"

    uuid = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)  # Unique email address
    country_code = Column(String(5), nullable=False, default="", index=True)  # Country code
    phone_number = Column(String(20), nullable=False, default="", index=True)  # Phone number
    full_phone_number = Column(String(25), nullable=False, default="", index=True)  # Full phone number with country code
    first_name = Column(String, nullable=False)  # First name
    last_name = Column(String, nullable=False)  # Last name
    password_hash = Column(String, nullable=False)  # Hashed password
    role = Column(String, nullable=False, default="ADMIN")  # User role
    otp = Column(String(5), nullable=True, default="")  # Temporary OTP code
    otp_expired_at = Column(DateTime, nullable=True, default=None)  # OTP expiration date
    otp_password = Column(String(5), nullable=True, default="")  # OTP password
    otp_password_expired_at = Column(DateTime, nullable=True, default=None)  # OTP password expiration date
    status = Column(String, nullable=False, default="ACTIVED")  # User status
    created_at = Column(DateTime, default=func.now())  # Account creation timestamp
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Last update timestamp
    is_deleted = Column(Boolean, default=False)  # Soft delete flag
    
    # Nouveaux champs ajoutés
    login = Column(String, nullable=True)  # Nombre de connexions de l'utilisateur
    is_new_user = Column(Boolean, default=True)  # Indicateur pour savoir si l'utilisateur est nouveau
    first_login_date = Column(DateTime, nullable=True, default=None)  # Date de la première connexion
    last_login_date = Column(DateTime, nullable=True, default=None)  # Date de la dernière connexion
    connexion_counter = Column(Integer, nullable=True, default=0)  # Compteur de connexions
    def _repr_(self):
        """
        String representation of the User object.

        Returns:
            str: Representation of the user with first name, last name, and email.
        """
        return f"User('{self.first_name} {self.last_name}', '{self.email}')"