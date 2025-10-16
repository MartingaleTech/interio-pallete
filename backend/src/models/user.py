from pydantic import BaseModel, EmailStr
from typing import Optional
from .enums import UserRole


class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: UserRole
    org_id: Optional[str] = None
    created_at: str
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PhoneOTPRequest(BaseModel):
    phone: str


class PhoneOTPVerify(BaseModel):
    phone: str
    otp: str
