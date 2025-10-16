from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import UserLogin, PhoneOTPRequest, PhoneOTPVerify
from src.repositories import UserRepository, TokenRepository, OTPRepository
from src.utils import verify_password, create_token, generate_otp, send_otp_sms
from src.utils.mappers import db_user_to_pydantic


def login_user(db: Session, credentials: UserLogin) -> Dict[str, Any]:
    """Authenticate a user and return a token."""
    user_repo = UserRepository(db)
    token_repo = TokenRepository(db)
    
    db_user = user_repo.get_by_email(credentials.email)
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    password_hash = db_user.password_hash
    if not verify_password(credentials.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token()
    token_repo.create(token, db_user.id)
    
    user = db_user_to_pydantic(db_user)
    
    return {
        "token": token,
        "user": user
    }


def logout_user(db: Session, token: str) -> Dict[str, str]:
    """Logout a user by removing their token."""
    token_repo = TokenRepository(db)
    token_repo.delete(token)
    return {"message": "Logged out successfully"}


def request_phone_otp(db: Session, request: PhoneOTPRequest) -> Dict[str, Any]:
    """Send OTP to user's phone number."""
    user_repo = UserRepository(db)
    otp_repo = OTPRepository(db)
    
    db_user = user_repo.get_by_phone(request.phone)
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User with this phone number not found")
    
    otp = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=10)
    
    otp_repo.create(request.phone, otp, db_user.id, expires_at)
    
    send_otp_sms(request.phone, otp)
    
    return {
        "message": "OTP sent successfully",
        "phone": request.phone,
        "otp": otp
    }


def verify_phone_otp(db: Session, request: PhoneOTPVerify) -> Dict[str, Any]:
    """Verify OTP and return a token."""
    user_repo = UserRepository(db)
    otp_repo = OTPRepository(db)
    token_repo = TokenRepository(db)
    
    db_otp = otp_repo.get(request.phone)
    
    if not db_otp:
        raise HTTPException(status_code=400, detail="No OTP found for this phone number")
    
    if datetime.now() > db_otp.expires_at:
        otp_repo.delete(request.phone)
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    if db_otp.otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    db_user = user_repo.get_by_id(db_otp.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    token = create_token()
    token_repo.create(token, db_user.id)
    
    otp_repo.delete(request.phone)
    
    user = db_user_to_pydantic(db_user)
    
    return {
        "token": token,
        "user": user
    }
