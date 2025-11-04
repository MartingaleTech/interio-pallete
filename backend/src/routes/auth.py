from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.models import User, UserLogin, PhoneOTPRequest, PhoneOTPVerify
from src.services import auth_service_new
from src.dependencies.auth_new import get_current_user, security
from src.config.database import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""
    return auth_service_new.login_user(db, credentials)


@router.get("/me", response_model=User)
async def get_me(user: User = Depends(get_current_user)):
    """Get the current user."""
    return user


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout the current user."""
    return auth_service_new.logout_user(db, credentials.credentials)


@router.post("/phone/request-otp")
async def request_otp(request: PhoneOTPRequest, db: Session = Depends(get_db)):
    """Request an OTP for phone-based authentication."""
    return auth_service_new.request_phone_otp(db, request)


@router.post("/phone/verify-otp")
async def verify_otp(request: PhoneOTPVerify, db: Session = Depends(get_db)):
    """Verify an OTP for phone-based authentication."""
    return auth_service_new.verify_phone_otp(db, request)
