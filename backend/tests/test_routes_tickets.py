"""
Comprehensive tests for ticket routes.
Tests all endpoints in src/routes/tickets.py
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
def test_admin(db_session):
    """Create a test admin user."""
    admin = models.User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        name="Admin User",
        role=models.UserRole.ADMIN,
        phone="9999999999",
        password_hash=hash_password("admin123")
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


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
def test_project(db_session, test_organization):
    """Create a test project."""
    project = models.Project(
        id=str(uuid.uuid4()),
        org_id=test_organization.id,
        name="Test Project",
        description="Test project description",
        status=models.ProjectStatus.IN_PROGRESS,
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


@pytest.fixture
def admin_token(db_session, test_admin):
    """Create a test admin token."""
    token = models.Token(
        token="admin_token_123",
        user_id=test_admin.id,
        expires_at=datetime.now() + timedelta(days=1)
    )
    db_session.add(token)
    db_session.commit()
    return token


class TestProjectTickets:
    """Tests for project ticket endpoints"""
    
    def test_create_project_ticket(self, client, owner_token, test_project):
        """Test POST /api/v1/projects/{project_id}/tickets"""
        response = client.post(
            f"/api/v1/projects/{test_project.id}/tickets",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "title": "Bug Fix",
                "description": "Fix critical bug",
                "priority": "high",
                "status": "open"
            }
        )
        assert response.status_code in [200, 201]
    
    def test_get_project_tickets(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/tickets"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/tickets",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_project_tickets_with_pagination(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/tickets with pagination"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/tickets?page=1&page_size=10",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_project_ticket(self, client, owner_token, test_project, test_db):
        """Test GET /api/v1/projects/{project_id}/tickets/{ticket_id}"""
        ticket = models.ProjectTicket(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            title="Test Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/projects/{test_project.id}/tickets/{ticket.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_update_project_ticket(self, client, owner_token, test_project, test_db):
        """Test PATCH /api/v1/projects/{project_id}/tickets/{ticket_id}"""
        ticket = models.ProjectTicket(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            title="Test Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.patch(
            f"/api/v1/projects/{test_project.id}/tickets/{ticket.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "status": "in_progress"
            }
        )
        assert response.status_code == 200
    
    def test_delete_project_ticket(self, client, owner_token, test_project, test_db):
        """Test DELETE /api/v1/projects/{project_id}/tickets/{ticket_id}"""
        ticket = models.ProjectTicket(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            title="Test Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/projects/{test_project.id}/tickets/{ticket.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 204]
    
    def test_add_project_ticket_comment(self, client, owner_token, test_project, test_db):
        """Test POST /api/v1/projects/{project_id}/tickets/{ticket_id}/comments"""
        ticket = models.ProjectTicket(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            title="Test Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/projects/{test_project.id}/tickets/{ticket.id}/comments",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "comment": "This is a test comment"
            }
        )
        assert response.status_code in [200, 201]
    
    def test_add_project_ticket_attachment(self, client, owner_token, test_project, test_db):
        """Test POST /api/v1/projects/{project_id}/tickets/{ticket_id}/attachments"""
        ticket = models.ProjectTicket(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            title="Test Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/projects/{test_project.id}/tickets/{ticket.id}/attachments",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "file_url": "https://example.com/file.pdf",
                "file_name": "document.pdf"
            }
        )
        assert response.status_code in [200, 201]


class TestOrgTickets:
    """Tests for organization ticket endpoints"""
    
    def test_create_org_ticket(self, client, owner_token, test_organization):
        """Test POST /api/v1/organizations/tickets"""
        response = client.post(
            "/api/v1/organizations/tickets",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "title": "Support Request",
                "description": "Need help with feature",
                "priority": "medium"
            }
        )
        assert response.status_code in [200, 201]
    
    def test_get_org_tickets(self, client, owner_token, test_organization):
        """Test GET /api/v1/organizations/tickets"""
        response = client.get(
            "/api/v1/organizations/tickets",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_org_tickets_with_pagination(self, client, owner_token, test_organization):
        """Test GET /api/v1/organizations/tickets with pagination"""
        response = client.get(
            "/api/v1/organizations/tickets?page=1&page_size=10",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_org_ticket(self, client, owner_token, test_organization, test_db):
        """Test GET /api/v1/organizations/tickets/{ticket_id}"""
        ticket = models.OrgTicket(
            id=str(uuid.uuid4()),
            org_id=test_organization.id,
            title="Test Org Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/organizations/tickets/{ticket.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_update_org_ticket(self, client, owner_token, test_organization, test_db):
        """Test PATCH /api/v1/organizations/tickets/{ticket_id}"""
        ticket = models.OrgTicket(
            id=str(uuid.uuid4()),
            org_id=test_organization.id,
            title="Test Org Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.patch(
            f"/api/v1/organizations/tickets/{ticket.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "status": "in_progress"
            }
        )
        assert response.status_code == 200
    
    def test_delete_org_ticket(self, client, owner_token, test_organization, test_db):
        """Test DELETE /api/v1/organizations/tickets/{ticket_id}"""
        ticket = models.OrgTicket(
            id=str(uuid.uuid4()),
            org_id=test_organization.id,
            title="Test Org Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/organizations/tickets/{ticket.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 204]
    
    def test_add_org_ticket_comment(self, client, owner_token, test_organization, test_db):
        """Test POST /api/v1/organizations/tickets/{ticket_id}/comments"""
        ticket = models.OrgTicket(
            id=str(uuid.uuid4()),
            org_id=test_organization.id,
            title="Test Org Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/organizations/tickets/{ticket.id}/comments",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "comment": "This is a test comment"
            }
        )
        assert response.status_code in [200, 201]
    
    def test_add_org_ticket_attachment(self, client, owner_token, test_organization, test_db):
        """Test POST /api/v1/organizations/tickets/{ticket_id}/attachments"""
        ticket = models.OrgTicket(
            id=str(uuid.uuid4()),
            org_id=test_organization.id,
            title="Test Org Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/organizations/tickets/{ticket.id}/attachments",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "file_url": "https://example.com/file.pdf",
                "file_name": "document.pdf"
            }
        )
        assert response.status_code in [200, 201]


class TestAdminTickets:
    """Tests for admin ticket management endpoints"""
    
    def test_get_all_org_tickets(self, client, admin_token):
        """Test GET /api/v1/admin/tickets"""
        response = client.get(
            "/api/v1/admin/tickets",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_all_org_tickets_with_pagination(self, client, admin_token):
        """Test GET /api/v1/admin/tickets with pagination"""
        response = client.get(
            "/api/v1/admin/tickets?page=1&page_size=10",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_my_assigned_tickets(self, client, admin_token):
        """Test GET /api/v1/admin/tickets/assigned"""
        response = client.get(
            "/api/v1/admin/tickets/assigned",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_org_ticket_admin(self, client, admin_token, test_organization, test_db):
        """Test GET /api/v1/admin/tickets/{ticket_id}"""
        ticket = models.OrgTicket(
            id=str(uuid.uuid4()),
            org_id=test_organization.id,
            title="Test Org Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/admin/tickets/{ticket.id}",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_update_org_ticket_admin(self, client, admin_token, test_organization, test_db):
        """Test PATCH /api/v1/admin/tickets/{ticket_id}"""
        ticket = models.OrgTicket(
            id=str(uuid.uuid4()),
            org_id=test_organization.id,
            title="Test Org Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.patch(
            f"/api/v1/admin/tickets/{ticket.id}",
            headers={"Authorization": f"Bearer {admin_token.token}"},
            json={
                "status": "resolved"
            }
        )
        assert response.status_code == 200
    
    def test_add_org_ticket_comment_admin(self, client, admin_token, test_organization, test_db):
        """Test POST /api/v1/admin/tickets/{ticket_id}/comments"""
        ticket = models.OrgTicket(
            id=str(uuid.uuid4()),
            org_id=test_organization.id,
            title="Test Org Ticket",
            description="Test Description",
            priority=models.TicketPriority.MEDIUM,
            status=models.TicketStatus.OPEN
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/admin/tickets/{ticket.id}/comments",
            headers={"Authorization": f"Bearer {admin_token.token}"},
            json={
                "comment": "Admin response"
            }
        )
        assert response.status_code in [200, 201]


class TestMyTickets:
    """Tests for user's assigned tickets"""
    
    def test_get_my_assigned_project_tickets(self, client, owner_token, test_organization):
        """Test GET /api/v1/my-tickets/assigned"""
        response = client.get(
            "/api/v1/my-tickets/assigned",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_my_assigned_project_tickets_with_pagination(self, client, owner_token):
        """Test GET /api/v1/my-tickets/assigned with pagination"""
        response = client.get(
            "/api/v1/my-tickets/assigned?page=1&page_size=10",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200


class TestTicketsUnauthorized:
    """Tests for unauthorized access to ticket endpoints"""
    
    def test_create_project_ticket_unauthorized(self, client, test_project):
        """Test creating project ticket without authentication"""
        response = client.post(
            f"/api/v1/projects/{test_project.id}/tickets",
            json={"title": "Test"}
        )
        assert response.status_code == 403
    
    def test_create_org_ticket_unauthorized(self, client):
        """Test creating org ticket without authentication"""
        response = client.post(
            "/api/v1/organizations/tickets",
            json={"title": "Test"}
        )
        assert response.status_code == 403
    
    def test_get_admin_tickets_unauthorized(self, client, owner_token):
        """Test accessing admin tickets without admin role"""
        response = client.get(
            "/api/v1/admin/tickets",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 403
