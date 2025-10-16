from sqlalchemy.orm import Session
from typing import Optional, List
from src.database import models
from src.models import UserRole
import json


class UserRepository:
    """Repository for User database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_data: dict, password_hash: str) -> models.User:
        """Create a new user."""
        db_user = models.User(
            **user_data,
            password_hash=password_hash
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_by_id(self, user_id: str) -> Optional[models.User]:
        """Get user by ID."""
        return self.db.query(models.User).filter(models.User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[models.User]:
        """Get user by email."""
        return self.db.query(models.User).filter(models.User.email == email).first()
    
    def get_by_phone(self, phone: str) -> Optional[models.User]:
        """Get user by phone."""
        return self.db.query(models.User).filter(models.User.phone == phone).first()
    
    def get_by_org_id(self, org_id: str) -> List[models.User]:
        """Get all users in an organization."""
        return self.db.query(models.User).filter(models.User.org_id == org_id).all()
    
    def update(self, user_id: str, **kwargs) -> Optional[models.User]:
        """Update user."""
        user = self.get_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def delete(self, user_id: str) -> bool:
        """Delete user."""
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    
    def get_password_hash(self, user_id: str) -> Optional[str]:
        """Get password hash for a user."""
        user = self.get_by_id(user_id)
        return user.password_hash if user else None


class TokenRepository:
    """Repository for Token database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, token: str, user_id: str) -> models.Token:
        """Create a new token."""
        db_token = models.Token(token=token, user_id=user_id)
        self.db.add(db_token)
        self.db.commit()
        return db_token
    
    def get_user_id(self, token: str) -> Optional[str]:
        """Get user ID for a token."""
        db_token = self.db.query(models.Token).filter(models.Token.token == token).first()
        return db_token.user_id if db_token else None
    
    def delete(self, token: str) -> bool:
        """Delete a token."""
        db_token = self.db.query(models.Token).filter(models.Token.token == token).first()
        if db_token:
            self.db.delete(db_token)
            self.db.commit()
            return True
        return False


class OTPRepository:
    """Repository for OTP database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, phone: str, otp: str, user_id: str, expires_at: str) -> models.OTP:
        """Create or update OTP."""
        db_otp = self.db.query(models.OTP).filter(models.OTP.phone == phone).first()
        if db_otp:
            db_otp.otp = otp
            db_otp.user_id = user_id
            db_otp.expires_at = expires_at
        else:
            db_otp = models.OTP(phone=phone, otp=otp, user_id=user_id, expires_at=expires_at)
            self.db.add(db_otp)
        self.db.commit()
        self.db.refresh(db_otp)
        return db_otp
    
    def get(self, phone: str) -> Optional[models.OTP]:
        """Get OTP by phone."""
        return self.db.query(models.OTP).filter(models.OTP.phone == phone).first()
    
    def delete(self, phone: str) -> bool:
        """Delete OTP."""
        db_otp = self.get(phone)
        if db_otp:
            self.db.delete(db_otp)
            self.db.commit()
            return True
        return False
