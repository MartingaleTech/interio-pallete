from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import secrets
import bcrypt

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

security = HTTPBearer()

class UserRole(str, Enum):
    ADMIN = "admin"
    ORG_OWNER = "org_owner"
    ORG_MEMBER = "org_member"
    CLIENT = "client"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class ProjectStatus(str, Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"

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
    role: UserRole
    added_at: str

class OrgMemberCreate(BaseModel):
    email: EmailStr
    name: str = ""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str
    phone: Optional[str] = None
    role: Optional[str] = None

class Project(BaseModel):
    id: str
    org_id: str
    name: str
    description: str
    status: ProjectStatus
    client_id: str
    client_name: str
    budget: float
    start_date: str
    end_date: Optional[str] = None
    created_at: str

class ProjectCreate(BaseModel):
    name: str
    description: str
    client_id: str
    budget: float
    start_date: str
    end_date: Optional[str] = None

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

class TeamMember(BaseModel):
    id: str
    project_id: str
    user_id: str
    name: str
    role: str

class TeamMemberAdd(BaseModel):
    user_id: str
    role: str

class CalendarEvent(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    event_type: str
    start_time: str
    end_time: str
    attendees: List[str]
    created_at: str

class CalendarEventCreate(BaseModel):
    title: str
    description: str
    event_type: str
    start_time: str
    end_time: str
    attendees: List[str]

class ProjectDesign(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    file_url: str
    file_type: str
    uploaded_by: str
    uploaded_at: str

class ProjectDesignCreate(BaseModel):
    title: str
    description: str
    file_url: str
    file_type: str

class Invoice(BaseModel):
    id: str
    project_id: str
    org_id: str
    invoice_number: str
    amount: float
    tax: float
    total: float
    payment_status: PaymentStatus
    due_date: str
    paid_date: Optional[str] = None
    created_at: str

class InvoiceCreate(BaseModel):
    project_id: str
    amount: float
    tax: float
    due_date: str

class OrgInvoice(BaseModel):
    id: str
    org_id: str
    invoice_number: str
    subscription_plan: str
    amount: float
    payment_status: PaymentStatus
    billing_period_start: str
    billing_period_end: str
    due_date: str
    paid_date: Optional[str] = None
    created_at: str

class OrgInvoiceCreate(BaseModel):
    org_id: str
    subscription_plan: str
    amount: float
    billing_period_start: str
    billing_period_end: str
    due_date: str

users_db: Dict[str, User] = {}
passwords_db: Dict[str, str] = {}
tokens_db: Dict[str, str] = {}
organizations_db: Dict[str, Organization] = {}
projects_db: Dict[str, Project] = {}
clients_db: Dict[str, Client] = {}
team_members_db: Dict[str, List[TeamMember]] = {}
calendar_events_db: Dict[str, List[CalendarEvent]] = {}
project_designs_db: Dict[str, List[ProjectDesign]] = {}
invoices_db: Dict[str, Invoice] = {}
org_invoices_db: Dict[str, OrgInvoice] = {}
otp_db: Dict[str, Dict[str, Any]] = {}

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token() -> str:
    return secrets.token_urlsafe(32)

def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)

def send_otp_sms(phone: str, otp: str):
    print(f"[MOCK SMS] Sending OTP {otp} to {phone}")
    return True

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    if token not in tokens_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = tokens_db[token]
    if user_id not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    return users_db[user_id]

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

async def require_org_access(user: User = Depends(get_current_user)) -> User:
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Organization access required")
    return user

admin_id = str(uuid.uuid4())
admin_user = User(
    id=admin_id,
    email="admin@designerconnect.com",
    name="Admin",
    role=UserRole.ADMIN,
    created_at=datetime.now().isoformat(),
    phone="9999999999"
)
users_db[admin_id] = admin_user
passwords_db[admin_id] = hash_password("admin123")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
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

@app.get("/api/auth/me")
async def get_me(user: User = Depends(get_current_user)):
    return user

@app.post("/api/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token in tokens_db:
        del tokens_db[token]
    return {"message": "Logged out successfully"}

@app.post("/api/auth/phone/request-otp")
async def request_phone_otp(request: PhoneOTPRequest):
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

@app.post("/api/auth/phone/verify-otp")
async def verify_phone_otp(request: PhoneOTPVerify):
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

@app.post("/api/admin/organizations", response_model=Organization)
async def create_organization(org: OrganizationCreate, admin: User = Depends(require_admin)):
    org_id = str(uuid.uuid4())
    owner_id = str(uuid.uuid4())
    
    owner_user = User(
        id=owner_id,
        email=org.owner_email,
        name=org.owner_name,
        role=UserRole.ORG_OWNER,
        org_id=org_id,
        created_at=datetime.now().isoformat(),
        phone=org.owner_phone
    )
    users_db[owner_id] = owner_user
    passwords_db[owner_id] = hash_password(org.owner_password)
    
    subscription_start = datetime.now()
    subscription_end = subscription_start + timedelta(days=365)
    
    new_org = Organization(
        id=org_id,
        name=org.name,
        email=org.email,
        phone=org.phone,
        address=org.address,
        city=org.city,
        state=org.state,
        pincode=org.pincode,
        owner_id=owner_id,
        subscription_status=SubscriptionStatus.ACTIVE,
        subscription_plan=org.subscription_plan,
        subscription_start=subscription_start.isoformat(),
        subscription_end=subscription_end.isoformat(),
        created_at=datetime.now().isoformat()
    )
    organizations_db[org_id] = new_org
    
    return new_org

@app.get("/api/admin/organizations", response_model=List[Organization])
async def get_all_organizations(admin: User = Depends(require_admin)):
    return list(organizations_db.values())

@app.get("/api/admin/organizations/{org_id}", response_model=Organization)
async def get_organization(org_id: str, admin: User = Depends(require_admin)):
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organizations_db[org_id]

@app.patch("/api/admin/organizations/{org_id}", response_model=Organization)
async def update_organization(org_id: str, updates: OrganizationUpdate, admin: User = Depends(require_admin)):
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    org = organizations_db[org_id]
    update_data = updates.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(org, field, value)
    
    organizations_db[org_id] = org
    return org

@app.delete("/api/admin/organizations/{org_id}")
async def delete_organization(org_id: str, admin: User = Depends(require_admin)):
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    del organizations_db[org_id]
    
    for user_id, user in list(users_db.items()):
        if user.org_id == org_id:
            del users_db[user_id]
            if user_id in passwords_db:
                del passwords_db[user_id]
    
    for project_id, project in list(projects_db.items()):
        if project.org_id == org_id:
            del projects_db[project_id]
    
    return {"message": "Organization deleted successfully"}

@app.get("/api/admin/organizations/{org_id}/members", response_model=List[User])
async def get_org_members(org_id: str, admin: User = Depends(require_admin)):
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    members = [u for u in users_db.values() if u.org_id == org_id]
    return members

@app.post("/api/admin/organizations/{org_id}/members", response_model=User)
async def add_org_member(org_id: str, member: OrgMemberCreate, admin: User = Depends(require_admin)):
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    member_id = str(uuid.uuid4())
    new_member = User(
        id=member_id,
        email=member.email,
        name=member.name,
        role=UserRole.ORG_MEMBER,
        org_id=org_id,
        created_at=datetime.now().isoformat(),
        phone=member.phone
    )
    users_db[member_id] = new_member
    passwords_db[member_id] = hash_password(member.password)
    
    return new_member

@app.delete("/api/admin/organizations/{org_id}/members/{user_id}")
async def remove_org_member(org_id: str, user_id: str, admin: User = Depends(require_admin)):
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    if user.org_id != org_id:
        raise HTTPException(status_code=400, detail="User is not a member of this organization")
    
    if user.role == UserRole.ORG_OWNER:
        raise HTTPException(status_code=400, detail="Cannot remove organization owner")
    
    del users_db[user_id]
    if user_id in passwords_db:
        del passwords_db[user_id]
    
    return {"message": "Member removed successfully"}

@app.get("/api/organizations/members", response_model=List[User])
async def get_organization_members(user: User = Depends(get_current_user)):
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    members = [u for u in users_db.values() if u.org_id == user.org_id]
    return members

@app.post("/api/organizations/members", response_model=User)
async def add_organization_member(member: OrgMemberCreate, user: User = Depends(get_current_user)):
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Not authorized to add members")
    
    for existing_user in users_db.values():
        if existing_user.email == member.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    member_id = str(uuid.uuid4())
    first_name = getattr(member, 'first_name', '')
    last_name = getattr(member, 'last_name', '')
    member_name = f"{first_name} {last_name}".strip() if first_name or last_name else member.name
    
    new_member = User(
        id=member_id,
        email=member.email,
        name=member_name,
        role=getattr(member, 'role', UserRole.ORG_MEMBER),
        org_id=user.org_id,
        created_at=datetime.now().isoformat(),
        phone=member.phone,
        first_name=first_name if first_name else None,
        last_name=last_name if last_name else None
    )
    users_db[member_id] = new_member
    passwords_db[member_id] = hash_password(member.password)
    
    return new_member

@app.put("/api/organizations/members/{member_id}", response_model=User)
async def update_organization_member(member_id: str, member: OrgMemberCreate, user: User = Depends(get_current_user)):
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Not authorized to update members")
    
    if member_id not in users_db:
        raise HTTPException(status_code=404, detail="Member not found")
    
    existing_member = users_db[member_id]
    if existing_member.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Member not in your organization")
    
    first_name = getattr(member, 'first_name', '')
    last_name = getattr(member, 'last_name', '')
    member_name = f"{first_name} {last_name}".strip() if first_name or last_name else member.name
    
    existing_member.email = member.email
    existing_member.name = member_name
    existing_member.phone = member.phone
    existing_member.role = getattr(member, 'role', existing_member.role)
    existing_member.first_name = first_name if first_name else None
    existing_member.last_name = last_name if last_name else None
    
    if member.password:
        passwords_db[member_id] = hash_password(member.password)
    
    return existing_member

@app.delete("/api/organizations/members/{member_id}")
async def remove_organization_member(member_id: str, user: User = Depends(get_current_user)):
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not part of an organization")
    
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Not authorized to remove members")
    
    if member_id not in users_db:
        raise HTTPException(status_code=404, detail="Member not found")
    
    member = users_db[member_id]
    if member.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Member not in your organization")
    
    if member.role == UserRole.ORG_OWNER:
        raise HTTPException(status_code=400, detail="Cannot remove organization owner")
    
    del users_db[member_id]
    if member_id in passwords_db:
        del passwords_db[member_id]
    
    return {"message": "Member removed successfully"}

@app.post("/api/admin/organizations/{org_id}/invoices", response_model=OrgInvoice)
async def create_org_invoice(org_id: str, invoice: OrgInvoiceCreate, admin: User = Depends(require_admin)):
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    invoice_id = str(uuid.uuid4())
    invoice_number = f"ORG-{len(org_invoices_db) + 1:05d}"
    
    new_invoice = OrgInvoice(
        id=invoice_id,
        org_id=org_id,
        invoice_number=invoice_number,
        subscription_plan=invoice.subscription_plan,
        amount=invoice.amount,
        payment_status=PaymentStatus.PENDING,
        billing_period_start=invoice.billing_period_start,
        billing_period_end=invoice.billing_period_end,
        due_date=invoice.due_date,
        created_at=datetime.now().isoformat()
    )
    org_invoices_db[invoice_id] = new_invoice
    
    return new_invoice

@app.get("/api/admin/organizations/{org_id}/invoices", response_model=List[OrgInvoice])
async def get_org_invoices(org_id: str, admin: User = Depends(require_admin)):
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    invoices = [inv for inv in org_invoices_db.values() if inv.org_id == org_id]
    return invoices

@app.post("/api/organizations/projects", response_model=Project)
async def create_project(project: ProjectCreate, user: User = Depends(require_org_access)):
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    if project.client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client = clients_db[project.client_id]
    if client.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Client does not belong to your organization")
    
    project_id = str(uuid.uuid4())
    new_project = Project(
        id=project_id,
        org_id=user.org_id,
        name=project.name,
        description=project.description,
        status=ProjectStatus.PLANNING,
        client_id=project.client_id,
        client_name=client.name,
        budget=project.budget,
        start_date=project.start_date,
        end_date=project.end_date,
        created_at=datetime.now().isoformat()
    )
    projects_db[project_id] = new_project
    team_members_db[project_id] = []
    calendar_events_db[project_id] = []
    project_designs_db[project_id] = []
    
    return new_project

@app.get("/api/organizations/projects", response_model=List[Project])
async def get_projects(user: User = Depends(require_org_access)):
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    projects = [p for p in projects_db.values() if p.org_id == user.org_id]
    return projects

@app.get("/api/organizations/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, user: User = Depends(require_org_access)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return project

@app.post("/api/organizations/clients", response_model=Client)
async def create_client(client: ClientCreate, user: User = Depends(require_org_access)):
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    client_id = str(uuid.uuid4())
    client_user_id = str(uuid.uuid4())
    
    client_user = User(
        id=client_user_id,
        email=client.email,
        name=client.name,
        role=UserRole.CLIENT,
        org_id=user.org_id,
        created_at=datetime.now().isoformat(),
        phone=client.phone
    )
    users_db[client_user_id] = client_user
    passwords_db[client_user_id] = hash_password(client.password)
    
    new_client = Client(
        id=client_id,
        org_id=user.org_id,
        name=client.name,
        email=client.email,
        phone=client.phone,
        address=client.address,
        created_at=datetime.now().isoformat()
    )
    clients_db[client_id] = new_client
    
    return new_client

@app.get("/api/organizations/clients", response_model=List[Client])
async def get_clients(user: User = Depends(require_org_access)):
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    clients = [c for c in clients_db.values() if c.org_id == user.org_id]
    return clients

@app.post("/api/projects/{project_id}/team", response_model=TeamMember)
async def add_team_member(project_id: str, member: TeamMemberAdd, user: User = Depends(require_org_access)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if member.user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    member_user = users_db[member.user_id]
    
    team_member_id = str(uuid.uuid4())
    new_member = TeamMember(
        id=team_member_id,
        project_id=project_id,
        user_id=member.user_id,
        name=member_user.name,
        role=member.role
    )
    
    if project_id not in team_members_db:
        team_members_db[project_id] = []
    
    team_members_db[project_id].append(new_member)
    
    return new_member

@app.get("/api/projects/{project_id}/team", response_model=List[TeamMember])
async def get_team_members(project_id: str, user: User = Depends(get_current_user)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    if user.role == UserRole.CLIENT:
        client = None
        for c in clients_db.values():
            if c.email == user.email and c.org_id == project.org_id:
                client = c
                break
        if not client or project.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return team_members_db.get(project_id, [])

@app.post("/api/projects/{project_id}/calendar", response_model=CalendarEvent)
async def create_calendar_event(project_id: str, event: CalendarEventCreate, user: User = Depends(require_org_access)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    event_id = str(uuid.uuid4())
    new_event = CalendarEvent(
        id=event_id,
        project_id=project_id,
        title=event.title,
        description=event.description,
        event_type=event.event_type,
        start_time=event.start_time,
        end_time=event.end_time,
        attendees=event.attendees,
        created_at=datetime.now().isoformat()
    )
    
    if project_id not in calendar_events_db:
        calendar_events_db[project_id] = []
    
    calendar_events_db[project_id].append(new_event)
    
    return new_event

@app.get("/api/projects/{project_id}/calendar", response_model=List[CalendarEvent])
async def get_calendar_events(project_id: str, user: User = Depends(get_current_user)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    if user.role == UserRole.CLIENT:
        client = None
        for c in clients_db.values():
            if c.email == user.email and c.org_id == project.org_id:
                client = c
                break
        if not client or project.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return calendar_events_db.get(project_id, [])

@app.post("/api/projects/{project_id}/designs", response_model=ProjectDesign)
async def create_project_design(project_id: str, design: ProjectDesignCreate, user: User = Depends(require_org_access)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    design_id = str(uuid.uuid4())
    new_design = ProjectDesign(
        id=design_id,
        project_id=project_id,
        title=design.title,
        description=design.description,
        file_url=design.file_url,
        file_type=design.file_type,
        uploaded_by=user.name,
        uploaded_at=datetime.now().isoformat()
    )
    
    if project_id not in project_designs_db:
        project_designs_db[project_id] = []
    
    project_designs_db[project_id].append(new_design)
    
    return new_design

@app.get("/api/projects/{project_id}/designs", response_model=List[ProjectDesign])
async def get_project_designs(project_id: str, user: User = Depends(get_current_user)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    if user.role == UserRole.CLIENT:
        client = None
        for c in clients_db.values():
            if c.email == user.email and c.org_id == project.org_id:
                client = c
                break
        if not client or project.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return project_designs_db.get(project_id, [])

@app.post("/api/projects/{project_id}/invoices", response_model=Invoice)
async def create_invoice(project_id: str, invoice: InvoiceCreate, user: User = Depends(require_org_access)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    invoice_id = str(uuid.uuid4())
    invoice_number = f"INV-{len(invoices_db) + 1:05d}"
    total = invoice.amount + invoice.tax
    
    new_invoice = Invoice(
        id=invoice_id,
        project_id=project_id,
        org_id=project.org_id,
        invoice_number=invoice_number,
        amount=invoice.amount,
        tax=invoice.tax,
        total=total,
        payment_status=PaymentStatus.PENDING,
        due_date=invoice.due_date,
        created_at=datetime.now().isoformat()
    )
    invoices_db[invoice_id] = new_invoice
    
    return new_invoice

@app.get("/api/projects/{project_id}/invoices", response_model=List[Invoice])
async def get_project_invoices(project_id: str, user: User = Depends(get_current_user)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    if user.role == UserRole.CLIENT:
        client = None
        for c in clients_db.values():
            if c.email == user.email and c.org_id == project.org_id:
                client = c
                break
        if not client or project.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    invoices = [inv for inv in invoices_db.values() if inv.project_id == project_id]
    return invoices

@app.get("/api/clients/projects", response_model=List[Project])
async def get_client_projects(user: User = Depends(get_current_user)):
    if user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Client access required")
    
    client = None
    for c in clients_db.values():
        if c.email == user.email:
            client = c
            break
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    projects = [p for p in projects_db.values() if p.client_id == client.id]
    return projects
