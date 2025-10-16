from pydantic import BaseModel, EmailStr
from typing import Optional
from .enums import SubscriptionStatus


class Organization(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    pincode: str
    owner_id: str
    subscription_status: SubscriptionStatus
    subscription_plan: str
    subscription_start: str
    subscription_end: str
    created_at: str


class OrganizationCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    pincode: str
    owner_email: EmailStr
    owner_name: str
    owner_phone: str
    owner_password: str
    subscription_plan: str = "basic"


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    subscription_status: Optional[SubscriptionStatus] = None
    subscription_plan: Optional[str] = None


class OrgMember(BaseModel):
    id: str
    org_id: str
    user_id: str
    name: str
    email: EmailStr
    role: str
    added_at: str


class OrgMemberCreate(BaseModel):
    email: EmailStr
    name: str = ""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str
    phone: Optional[str] = None
    role: Optional[str] = None
