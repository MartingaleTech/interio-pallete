from pydantic import BaseModel, EmailStr


class Client(BaseModel):
    id: str
    org_id: str
    name: str
    email: EmailStr
    phone: str
    address: str
    created_at: str


class ClientCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    password: str
