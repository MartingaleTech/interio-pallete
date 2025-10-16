from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.models import User, UserLogin, PhoneOTPRequest, PhoneOTPVerify
from src.services import login_user, logout_user, request_phone_otp, verify_phone_otp
from src.dependencies import get_current_user, security

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(credentials: UserLogin):
    """Login with email and password."""
    return login_user(credentials)


@router.get("/me", response_model=User)
async def get_me(user: User = Depends(get_current_user)):
    """Get the current user."""
    return user


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout the current user."""
    return logout_user(credentials.credentials)


@router.post("/phone/request-otp")
async def request_otp(request: PhoneOTPRequest):
    """Request an OTP for phone-based authentication."""
    return request_phone_otp(request)


@router.post("/phone/verify-otp")
async def verify_otp(request: PhoneOTPVerify):
    """Verify an OTP for phone-based authentication."""
    return verify_phone_otp(request)
