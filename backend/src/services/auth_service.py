from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException
from src.models import User, UserLogin, PhoneOTPRequest, PhoneOTPVerify
from src.database import get_users_db, get_passwords_db, get_tokens_db, get_otp_db
from src.utils import hash_password, verify_password, create_token, generate_otp, send_otp_sms


def login_user(credentials: UserLogin) -> Dict[str, Any]:
    """Authenticate a user and return a token."""
    users_db = get_users_db()
    passwords_db = get_passwords_db()
    tokens_db = get_tokens_db()
    
    user = None
    for u in users_db.values():
        if u.email == credentials.email:
            user = u
            break
    
    if not user or not verify_password(credentials.password, passwords_db[user.id]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token()
    tokens_db[token] = user.id
    
    return {
        "token": token,
        "user": user
    }


def logout_user(token: str) -> Dict[str, str]:
    """Logout a user by removing their token."""
    tokens_db = get_tokens_db()
    if token in tokens_db:
        del tokens_db[token]
    return {"message": "Logged out successfully"}


def request_phone_otp(request: PhoneOTPRequest) -> Dict[str, Any]:
    """Send OTP to user's phone number."""
    users_db = get_users_db()
    otp_db = get_otp_db()
    
    user = None
    for u in users_db.values():
        if u.phone == request.phone:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=404, detail="User with this phone number not found")
    
    otp = generate_otp()
    otp_db[request.phone] = {
        "otp": otp,
        "user_id": user.id,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()
    }
    
    send_otp_sms(request.phone, otp)
    
    return {
        "message": "OTP sent successfully",
        "phone": request.phone,
        "otp": otp
    }


def verify_phone_otp(request: PhoneOTPVerify) -> Dict[str, Any]:
    """Verify OTP and return a token."""
    users_db = get_users_db()
    otp_db = get_otp_db()
    tokens_db = get_tokens_db()
    
    if request.phone not in otp_db:
        raise HTTPException(status_code=400, detail="No OTP found for this phone number")
    
    otp_data = otp_db[request.phone]
    
    expires_at = datetime.fromisoformat(otp_data["expires_at"])
    if datetime.now() > expires_at:
        del otp_db[request.phone]
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    if otp_data["otp"] != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    user_id = otp_data["user_id"]
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    
    token = create_token()
    tokens_db[token] = user_id
    
    del otp_db[request.phone]
    
    return {
        "token": token,
        "user": user
    }
