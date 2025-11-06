"""
Comprehensive tests for client routes.
Tests all endpoints in src/routes/clients.py
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid

from app.main import app
from src.config.database import Base, get_db
from src.database import models
from src.utils.security import hash_password


@pytest.fixture(scope="function")
def test_db():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(test_db):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_org_owner(test_db):
    """Create a test organization owner."""
    user = models.User(
        id=str(uuid.uuid4()),
        email="owner@example.com",
        name="Org Owner",
        role=models.UserRole.ORG_OWNER,
        phone="1234567890",
        password_hash=hash_password("password123")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_organization(test_db, test_org_owner):
    """Create a test organization."""
    org = models.Organization(
        id=str(uuid.uuid4()),
        name="Test Organization",
        email="org@example.com",
        phone="1234567890",
        address="123 Test St",
        city="Test City",
        state="Test State",
        pincode="12345",
        owner_id=test_org_owner.id,
        subscription_status=models.SubscriptionStatus.ACTIVE,
        subscription_plan="basic",
        subscription_start=datetime.now(),
        subscription_end=datetime.now() + timedelta(days=30)
    )
    test_db.add(org)
    test_db.commit()
    test_db.refresh(org)
    
    test_org_owner.org_id = org.id
    test_db.commit()
    test_db.refresh(test_org_owner)
    
    return org


@pytest.fixture
def test_client_user(test_db, test_organization):
    """Create a test client user."""
    client = models.Client(
        id=str(uuid.uuid4()),
        org_id=test_organization.id,
        name="Test Client",
        email="client@example.com",
        phone="1234567890",
        address="456 Client St"
    )
    test_db.add(client)
    test_db.commit()
    test_db.refresh(client)
    return client


@pytest.fixture
def owner_token(test_db, test_org_owner):
    """Create a test token for org owner."""
    token = models.Token(
        token="owner_token_123",
        user_id=test_org_owner.id,
        expires_at=datetime.now() + timedelta(days=1)
    )
    test_db.add(token)
    test_db.commit()
    return token


@pytest.fixture
def client_user_with_auth(test_db, test_organization):
    """Create a client user with authentication."""
    user = models.User(
        id=str(uuid.uuid4()),
        email="clientuser@example.com",
        name="Client User",
        role=models.UserRole.CLIENT,
        phone="1234567890",
        password_hash=hash_password("password123")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def client_token(test_db, client_user_with_auth):
    """Create a test token for client user."""
    token = models.Token(
        token="client_token_123",
        user_id=client_user_with_auth.id,
        expires_at=datetime.now() + timedelta(days=1)
    )
    test_db.add(token)
    test_db.commit()
    return token


class TestClientManagement:
    """Tests for client management endpoints"""
    
    def test_create_client(self, client, owner_token, test_organization):
        """Test POST /api/v1/organizations/clients"""
        response = client.post(
            "/api/v1/organizations/clients",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "name": "New Client",
                "email": "newclient@example.com",
                "phone": "9876543210",
                "address": "789 New St"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["name"] == "New Client"
        assert data["email"] == "newclient@example.com"
    
    def test_create_client_unauthorized(self, client):
        """Test creating client without authentication"""
        response = client.post(
            "/api/v1/organizations/clients",
            json={
                "name": "New Client",
                "email": "newclient@example.com"
            }
        )
        assert response.status_code == 403
    
    def test_create_client_missing_fields(self, client, owner_token):
        """Test creating client with missing required fields"""
        response = client.post(
            "/api/v1/organizations/clients",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "name": "Incomplete Client"
            }
        )
        assert response.status_code == 422
    
    def test_get_clients(self, client, owner_token, test_organization, test_client_user):
        """Test GET /api/v1/organizations/clients"""
        response = client.get(
            "/api/v1/organizations/clients",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    def test_get_clients_with_pagination(self, client, owner_token, test_organization):
        """Test GET /api/v1/organizations/clients with pagination"""
        response = client.get(
            "/api/v1/organizations/clients?page=1&page_size=10",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_clients_with_sorting(self, client, owner_token, test_organization):
        """Test GET /api/v1/organizations/clients with sorting"""
        response = client.get(
            "/api/v1/organizations/clients?sort_by=name&sort_order=asc",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_clients_unauthorized(self, client):
        """Test getting clients without authentication"""
        response = client.get("/api/v1/organizations/clients")
        assert response.status_code == 403


class TestClientProjects:
    """Tests for client project access"""
    
    def test_get_client_projects(self, client, client_token, test_db, client_user_with_auth, test_organization):
        """Test GET /api/v1/clients/projects"""
        test_client = models.Client(
            id=str(uuid.uuid4()),
            org_id=test_organization.id,
            name="Test Client",
            email="client@example.com",
            phone="1234567890",
            address="456 Client St"
        )
        test_db.add(test_client)
        test_db.commit()
        
        project = models.Project(
            id=str(uuid.uuid4()),
            org_id=test_organization.id,
            name="Client Project",
            description="Project for client",
            status=models.ProjectStatus.IN_PROGRESS,
            client_id=client_user_with_auth.id,
            budget=10000.0,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        test_db.add(project)
        test_db.commit()
        
        response = client.get(
            "/api/v1/clients/projects",
            headers={"Authorization": f"Bearer {client_token.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    def test_get_client_projects_with_pagination(self, client, client_token):
        """Test GET /api/v1/clients/projects with pagination"""
        response = client.get(
            "/api/v1/clients/projects?page=1&page_size=5",
            headers={"Authorization": f"Bearer {client_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_client_projects_unauthorized(self, client):
        """Test getting client projects without authentication"""
        response = client.get("/api/v1/clients/projects")
        assert response.status_code == 403
