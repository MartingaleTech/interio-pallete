import pytest
from datetime import datetime, timedelta, timezone
from src.repositories import (
    UserRepository, TokenRepository, OTPRepository,
    OrganizationRepository, ProjectRepository, ClientRepository,
    InvoiceRepository
)
from src.database import models
from src.utils import hash_password
import uuid


class TestUserRepository:
    """Test user repository."""
    
    def test_create_user(self, db_session):
        """Test creating a user."""
        repo = UserRepository(db_session)
        user_data = {
            "id": str(uuid.uuid4()),
            "email": "newuser@example.com",
            "name": "New User",
            "role": models.UserRole.ORG_MEMBER,
            "org_id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc),
            "phone": "1234567890"
        }
        user = repo.create(user_data, hash_password("password123"))
        
        assert user.email == "newuser@example.com"
        assert user.name == "New User"
    
    def test_get_by_id(self, db_session, test_user):
        """Test getting user by ID."""
        repo = UserRepository(db_session)
        user = repo.get_by_id(test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
    
    def test_get_by_email(self, db_session, test_user):
        """Test getting user by email."""
        repo = UserRepository(db_session)
        user = repo.get_by_email(test_user.email)
        
        assert user is not None
        assert user.email == test_user.email
    
    def test_get_by_phone(self, db_session, test_user):
        """Test getting user by phone."""
        repo = UserRepository(db_session)
        user = repo.get_by_phone(test_user.phone)
        
        assert user is not None
        assert user.phone == test_user.phone
    
    def test_get_by_org_id(self, db_session, test_user, test_organization):
        """Test getting users by organization ID."""
        repo = UserRepository(db_session)
        users = repo.get_by_org_id(test_organization.id)
        
        assert len(users) > 0
        assert any(u.id == test_user.id for u in users)
    
    def test_update_user(self, db_session, test_user):
        """Test updating a user."""
        repo = UserRepository(db_session)
        updated = repo.update(test_user.id, name="Updated Name")
        
        assert updated.name == "Updated Name"
    
    def test_delete_user(self, db_session):
        """Test deleting a user."""
        repo = UserRepository(db_session)
        user_data = {
            "id": str(uuid.uuid4()),
            "email": "deleteme@example.com",
            "name": "Delete Me",
            "role": models.UserRole.ORG_MEMBER,
            "org_id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc),
            "phone": "9999999999"
        }
        user = repo.create(user_data, hash_password("password123"))
        
        repo.delete(user.id)
        deleted_user = repo.get_by_id(user.id)
        
        assert deleted_user is None


class TestTokenRepository:
    """Test token repository."""
    
    def test_create_token(self, db_session, test_user):
        """Test creating a token."""
        repo = TokenRepository(db_session)
        token_data = {
            "id": str(uuid.uuid4()),
            "user_id": test_user.id,
            "token": "test_token_123",
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            "created_at": datetime.now(timezone.utc)
        }
        token = repo.create(token_data)
        
        assert token.token == "test_token_123"
        assert token.user_id == test_user.id
    
    def test_get_user_id_valid_token(self, db_session, test_token):
        """Test getting user ID from valid token."""
        repo = TokenRepository(db_session)
        user_id = repo.get_user_id(test_token.token)
        
        assert user_id == test_token.user_id
    
    def test_get_user_id_expired_token(self, db_session, test_user):
        """Test getting user ID from expired token."""
        repo = TokenRepository(db_session)
        token_data = {
            "id": str(uuid.uuid4()),
            "user_id": test_user.id,
            "token": "expired_token",
            "expires_at": datetime.now(timezone.utc) - timedelta(hours=1),
            "created_at": datetime.now(timezone.utc) - timedelta(hours=2)
        }
        repo.create(token_data)
        
        user_id = repo.get_user_id("expired_token")
        
        assert user_id is None
    
    def test_delete_token(self, db_session, test_token):
        """Test deleting a token."""
        repo = TokenRepository(db_session)
        repo.delete(test_token.token)
        
        user_id = repo.get_user_id(test_token.token)
        assert user_id is None


class TestOTPRepository:
    """Test OTP repository."""
    
    def test_create_otp(self, db_session):
        """Test creating an OTP."""
        repo = OTPRepository(db_session)
        otp_data = {
            "id": str(uuid.uuid4()),
            "phone": "1234567890",
            "otp": "123456",
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
            "created_at": datetime.now(timezone.utc)
        }
        otp = repo.create(otp_data)
        
        assert otp.phone == "1234567890"
        assert otp.otp == "123456"
    
    def test_get_otp(self, db_session):
        """Test getting an OTP."""
        repo = OTPRepository(db_session)
        phone = "1234567890"
        otp_data = {
            "id": str(uuid.uuid4()),
            "phone": phone,
            "otp": "123456",
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
            "created_at": datetime.now(timezone.utc)
        }
        repo.create(otp_data)
        
        otp = repo.get(phone)
        
        assert otp is not None
        assert otp.phone == phone
    
    def test_delete_otp(self, db_session):
        """Test deleting an OTP."""
        repo = OTPRepository(db_session)
        phone = "1234567890"
        otp_data = {
            "id": str(uuid.uuid4()),
            "phone": phone,
            "otp": "123456",
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
            "created_at": datetime.now(timezone.utc)
        }
        repo.create(otp_data)
        
        repo.delete(phone)
        otp = repo.get(phone)
        
        assert otp is None


class TestOrganizationRepository:
    """Test organization repository."""
    
    def test_create_organization(self, db_session):
        """Test creating an organization."""
        repo = OrganizationRepository(db_session)
        org_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Org",
            "email": "testorg@example.com",
            "phone": "1234567890",
            "address": "123 Test St",
            "city": "Test City",
            "state": "Test State",
            "pincode": "12345",
            "owner_id": str(uuid.uuid4()),
            "subscription_status": models.SubscriptionStatus.ACTIVE,
            "subscription_plan": "basic",
            "subscription_start": datetime.now(timezone.utc),
            "subscription_end": datetime.now(timezone.utc) + timedelta(days=365),
            "created_at": datetime.now(timezone.utc)
        }
        org = repo.create(org_data)
        
        assert org.name == "Test Org"
        assert org.email == "testorg@example.com"
    
    def test_get_by_id(self, db_session, test_organization):
        """Test getting organization by ID."""
        repo = OrganizationRepository(db_session)
        org = repo.get_by_id(test_organization.id)
        
        assert org is not None
        assert org.id == test_organization.id
    
    def test_get_all(self, db_session, test_organization):
        """Test getting all organizations."""
        repo = OrganizationRepository(db_session)
        orgs = repo.get_all()
        
        assert len(orgs) > 0
        assert any(o.id == test_organization.id for o in orgs)
    
    def test_update_organization(self, db_session, test_organization):
        """Test updating an organization."""
        repo = OrganizationRepository(db_session)
        updated = repo.update(test_organization.id, name="Updated Org")
        
        assert updated.name == "Updated Org"
    
    def test_delete_organization(self, db_session):
        """Test deleting an organization."""
        repo = OrganizationRepository(db_session)
        org_data = {
            "id": str(uuid.uuid4()),
            "name": "Delete Me Org",
            "email": "deleteme@example.com",
            "phone": "9999999999",
            "address": "123 Delete St",
            "city": "Delete City",
            "state": "Delete State",
            "pincode": "99999",
            "owner_id": str(uuid.uuid4()),
            "subscription_status": models.SubscriptionStatus.ACTIVE,
            "subscription_plan": "basic",
            "subscription_start": datetime.now(timezone.utc),
            "subscription_end": datetime.now(timezone.utc) + timedelta(days=365),
            "created_at": datetime.now(timezone.utc)
        }
        org = repo.create(org_data)
        
        repo.delete(org.id)
        deleted_org = repo.get_by_id(org.id)
        
        assert deleted_org is None


class TestProjectRepository:
    """Test project repository."""
    
    def test_get_by_id(self, db_session, test_project):
        """Test getting project by ID."""
        repo = ProjectRepository(db_session)
        project = repo.get_by_id(test_project.id)
        
        assert project is not None
        assert project.id == test_project.id
    
    def test_get_by_org_id(self, db_session, test_project, test_organization):
        """Test getting projects by organization ID."""
        repo = ProjectRepository(db_session)
        projects = repo.get_by_org_id(test_organization.id)
        
        assert len(projects) > 0
        assert any(p.id == test_project.id for p in projects)
    
    def test_get_by_client_id(self, db_session, test_project, test_client):
        """Test getting projects by client ID."""
        repo = ProjectRepository(db_session)
        projects = repo.get_by_client_id(test_client.id)
        
        assert len(projects) > 0
        assert any(p.id == test_project.id for p in projects)
    
    def test_delete_project(self, db_session, test_project):
        """Test deleting a project."""
        repo = ProjectRepository(db_session)
        repo.delete(test_project.id)
        
        deleted_project = repo.get_by_id(test_project.id)
        assert deleted_project is None


class TestClientRepository:
    """Test client repository."""
    
    def test_get_by_id(self, db_session, test_client):
        """Test getting client by ID."""
        repo = ClientRepository(db_session)
        client = repo.get_by_id(test_client.id)
        
        assert client is not None
        assert client.id == test_client.id
    
    def test_get_by_email(self, db_session, test_client):
        """Test getting client by email."""
        repo = ClientRepository(db_session)
        client = repo.get_by_email(test_client.email)
        
        assert client is not None
        assert client.email == test_client.email
    
    def test_get_by_org_id(self, db_session, test_client, test_organization):
        """Test getting clients by organization ID."""
        repo = ClientRepository(db_session)
        clients = repo.get_by_org_id(test_organization.id)
        
        assert len(clients) > 0
        assert any(c.id == test_client.id for c in clients)


class TestInvoiceRepository:
    """Test invoice repository."""
    
    def test_get_by_project_id(self, db_session, test_project):
        """Test getting invoices by project ID."""
        repo = InvoiceRepository(db_session)
        invoices = repo.get_by_project_id(test_project.id)
        
        assert isinstance(invoices, list)
    
    def test_get_by_org_id(self, db_session, test_organization):
        """Test getting invoices by organization ID."""
        repo = InvoiceRepository(db_session)
        invoices = repo.get_by_org_id(test_organization.id)
        
        assert isinstance(invoices, list)
