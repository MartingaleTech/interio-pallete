"""
Comprehensive tests for project routes.
Tests all endpoints in src/routes/projects.py
"""
import pytest
from datetime import datetime, timedelta
import uuid

from src.database import models
from src.utils.security import hash_password


@pytest.fixture
def test_org_owner(db_session):
    """Create a test organization owner."""
    user = models.User(
        id=str(uuid.uuid4()),
        email="owner@example.com",
        name="Org Owner",
        role=models.UserRole.ORG_OWNER,
        phone="1234567890",
        password_hash=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_organization(db_session, test_org_owner):
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
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    
    test_org_owner.org_id = org.id
    db_session.commit()
    db_session.refresh(test_org_owner)
    
    return org


@pytest.fixture
def test_client_user(db_session, test_organization):
    """Create a test client user."""
    client = models.Client(
        id=str(uuid.uuid4()),
        org_id=test_organization.id,
        name="Test Client",
        email="client@example.com",
        phone="1234567890",
        address="456 Client St"
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


@pytest.fixture
def test_project(db_session, test_organization, test_client_user):
    """Create a test project."""
    project = models.Project(
        id=str(uuid.uuid4()),
        org_id=test_organization.id,
        name="Test Project",
        description="Test project description",
        status=models.ProjectStatus.IN_PROGRESS,
        client_id=test_client_user.id,
        budget=10000.0,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30)
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def owner_token(db_session, test_org_owner):
    """Create a test token for org owner."""
    token = models.Token(
        token="owner_token_123",
        user_id=test_org_owner.id,
        expires_at=datetime.now() + timedelta(days=1)
    )
    db_session.add(token)
    db_session.commit()
    return token


class TestProjectCRUD:
    """Tests for project CRUD operations"""
    
    def test_create_project(self, client, owner_token, test_organization, test_client_user):
        """Test POST /api/v1/organizations/projects"""
        response = client.post(
            "/api/v1/organizations/projects",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "name": "New Project",
                "description": "New project description",
                "client_id": test_client_user.id,
                "budget": 15000.0,
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=60)).isoformat()
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["name"] == "New Project"
    
    def test_create_project_unauthorized(self, client):
        """Test creating project without authentication"""
        response = client.post(
            "/api/v1/organizations/projects",
            json={
                "name": "New Project",
                "description": "Test"
            }
        )
        assert response.status_code == 403
    
    def test_get_projects(self, client, owner_token, test_organization, test_project):
        """Test GET /api/v1/organizations/projects"""
        response = client.get(
            "/api/v1/organizations/projects",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    def test_get_projects_with_pagination(self, client, owner_token, test_organization):
        """Test GET /api/v1/organizations/projects with pagination"""
        response = client.get(
            "/api/v1/organizations/projects?page=1&page_size=10",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_projects_with_sorting(self, client, owner_token, test_organization):
        """Test GET /api/v1/organizations/projects with sorting"""
        response = client.get(
            "/api/v1/organizations/projects?sort_by=name&sort_order=desc",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_project_by_id(self, client, owner_token, test_project):
        """Test GET /api/v1/organizations/projects/{project_id}"""
        response = client.get(
            f"/api/v1/organizations/projects/{test_project.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project.id


class TestProjectTeam:
    """Tests for project team management"""
    
    def test_add_team_member(self, client, owner_token, test_project, test_db, test_organization):
        """Test POST /api/v1/projects/{project_id}/team"""
        member = models.User(
            id=str(uuid.uuid4()),
            email="member@example.com",
            name="Team Member",
            role=models.UserRole.ORG_MEMBER,
            phone="1234567890",
            password_hash=hash_password("password123"),
            org_id=test_organization.id
        )
        db_session.add(member)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/projects/{test_project.id}/team",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "user_id": member.id,
                "role": "designer"
            }
        )
        assert response.status_code in [200, 201]
    
    def test_get_project_team_members(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/team"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/team",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200


class TestProjectCalendar:
    """Tests for project calendar events"""
    
    def test_create_calendar_event(self, client, owner_token, test_project):
        """Test POST /api/v1/projects/{project_id}/calendar"""
        response = client.post(
            f"/api/v1/projects/{test_project.id}/calendar",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "title": "Project Meeting",
                "description": "Discuss project progress",
                "event_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "event_type": "meeting"
            }
        )
        assert response.status_code in [200, 201]
    
    def test_get_project_calendar_events(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/calendar"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/calendar",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200


class TestProjectDesigns:
    """Tests for project designs"""
    
    def test_create_design(self, client, owner_token, test_project):
        """Test POST /api/v1/projects/{project_id}/designs"""
        response = client.post(
            f"/api/v1/projects/{test_project.id}/designs",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "title": "Design Mockup",
                "description": "Initial design mockup",
                "file_url": "https://example.com/design.png"
            }
        )
        assert response.status_code in [200, 201]
    
    def test_get_designs(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/designs"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/designs",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200


class TestProjectInvoices:
    """Tests for project invoices"""
    
    def test_create_invoice(self, client, owner_token, test_project):
        """Test POST /api/v1/projects/{project_id}/invoices"""
        response = client.post(
            f"/api/v1/projects/{test_project.id}/invoices",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "amount": 5000.0,
                "tax": 900.0,
                "total": 5900.0,
                "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "description": "Project milestone payment"
            }
        )
        assert response.status_code in [200, 201]
    
    def test_get_invoices(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/invoices"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/invoices",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
