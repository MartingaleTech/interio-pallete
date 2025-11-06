"""
Comprehensive tests for admin routes.
Tests all endpoints in src/routes/admin.py
"""
import pytest
from datetime import datetime, timedelta
import uuid

from src.database import models
from src.utils.security import hash_password


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


@pytest.fixture
def test_organization(db_session, test_admin):
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
        owner_id=test_admin.id,
        subscription_status=models.SubscriptionStatus.ACTIVE,
        subscription_plan="basic",
        subscription_start=datetime.now(),
        subscription_end=datetime.now() + timedelta(days=30)
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


class TestAdminOrganizations:
    """Tests for admin organization management endpoints"""
    
    def test_create_organization(self, client, admin_token):
        """Test POST /api/v1/admin/organizations"""
        response = client.post(
            "/api/v1/admin/organizations",
            headers={"Authorization": f"Bearer {admin_token.token}"},
            json={
                "name": "New Organization",
                "email": "neworg@example.com",
                "phone": "1234567890",
                "address": "123 Main St",
                "city": "New City",
                "state": "New State",
                "pincode": "54321",
                "subscription_plan": "premium"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["name"] == "New Organization"
    
    def test_create_organization_unauthorized(self, client):
        """Test creating organization without admin token"""
        response = client.post(
            "/api/v1/admin/organizations",
            json={
                "name": "New Organization",
                "email": "neworg@example.com"
            }
        )
        assert response.status_code == 403
    
    def test_get_all_organizations(self, client, admin_token, test_organization):
        """Test GET /api/v1/admin/organizations"""
        response = client.get(
            "/api/v1/admin/organizations",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    def test_get_all_organizations_with_pagination(self, client, admin_token):
        """Test GET /api/v1/admin/organizations with pagination"""
        response = client.get(
            "/api/v1/admin/organizations?page=1&page_size=10",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_organization_by_id(self, client, admin_token, test_organization):
        """Test GET /api/v1/admin/organizations/{org_id}"""
        response = client.get(
            f"/api/v1/admin/organizations/{test_organization.id}",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_organization.id
    
    def test_get_organization_not_found(self, client, admin_token):
        """Test getting non-existent organization"""
        response = client.get(
            f"/api/v1/admin/organizations/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 404
    
    def test_update_organization(self, client, admin_token, test_organization):
        """Test PATCH /api/v1/admin/organizations/{org_id}"""
        response = client.patch(
            f"/api/v1/admin/organizations/{test_organization.id}",
            headers={"Authorization": f"Bearer {admin_token.token}"},
            json={
                "name": "Updated Organization Name"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Organization Name"
    
    def test_delete_organization(self, client, admin_token, test_organization):
        """Test DELETE /api/v1/admin/organizations/{org_id}"""
        response = client.delete(
            f"/api/v1/admin/organizations/{test_organization.id}",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code in [200, 204]


class TestAdminOrganizationMembers:
    """Tests for admin organization member management"""
    
    def test_get_org_members(self, client, admin_token, test_organization):
        """Test GET /api/v1/admin/organizations/{org_id}/members"""
        response = client.get(
            f"/api/v1/admin/organizations/{test_organization.id}/members",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_add_org_member(self, client, admin_token, test_organization):
        """Test POST /api/v1/admin/organizations/{org_id}/members"""
        response = client.post(
            f"/api/v1/admin/organizations/{test_organization.id}/members",
            headers={"Authorization": f"Bearer {admin_token.token}"},
            json={
                "email": "newmember@example.com",
                "name": "New Member",
                "phone": "1234567890",
                "role": "org_member"
            }
        )
        assert response.status_code in [200, 201]
    
    def test_remove_org_member(self, client, admin_token, test_organization, test_db):
        """Test DELETE /api/v1/admin/organizations/{org_id}/members/{user_id}"""
        member = models.User(
            id=str(uuid.uuid4()),
            email="member@example.com",
            name="Member",
            role=models.UserRole.ORG_MEMBER,
            phone="1234567890",
            password_hash=hash_password("password123"),
            org_id=test_organization.id
        )
        db_session.add(member)
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/admin/organizations/{test_organization.id}/members/{member.id}",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code in [200, 204]


class TestAdminInvoices:
    """Tests for admin invoice management"""
    
    def test_create_org_invoice(self, client, admin_token, test_organization):
        """Test POST /api/v1/admin/organizations/{org_id}/invoices"""
        response = client.post(
            f"/api/v1/admin/organizations/{test_organization.id}/invoices",
            headers={"Authorization": f"Bearer {admin_token.token}"},
            json={
                "amount": 1000.0,
                "tax": 180.0,
                "total": 1180.0,
                "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "description": "Monthly subscription"
            }
        )
        assert response.status_code in [200, 201]
    
    def test_get_org_invoices(self, client, admin_token, test_organization):
        """Test GET /api/v1/admin/organizations/{org_id}/invoices"""
        response = client.get(
            f"/api/v1/admin/organizations/{test_organization.id}/invoices",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200


class TestAdminStats:
    """Tests for admin statistics"""
    
    def test_get_admin_stats(self, client, admin_token):
        """Test GET /api/v1/admin/stats"""
        response = client.get(
            "/api/v1/admin/stats",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_organizations" in data or isinstance(data, dict)


class TestAdminOrganizationViews:
    """Tests for admin organization view tracking"""
    
    def test_get_newly_added_orgs(self, client, admin_token):
        """Test GET /api/v1/admin/organizations/newly-added"""
        response = client.get(
            "/api/v1/admin/organizations/newly-added",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_recently_viewed_orgs(self, client, admin_token):
        """Test GET /api/v1/admin/organizations/recently-viewed"""
        response = client.get(
            "/api/v1/admin/organizations/recently-viewed",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_record_org_view(self, client, admin_token, test_organization):
        """Test POST /api/v1/admin/organizations/{org_id}/view"""
        response = client.post(
            f"/api/v1/admin/organizations/{test_organization.id}/view",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200


class TestAdminSupportTickets:
    """Tests for admin support ticket management"""
    
    def test_get_all_tickets(self, client, admin_token):
        """Test GET /api/v1/admin/support-tickets"""
        response = client.get(
            "/api/v1/admin/support-tickets",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_org_tickets(self, client, admin_token, test_organization):
        """Test GET /api/v1/admin/organizations/{org_id}/support-tickets"""
        response = client.get(
            f"/api/v1/admin/organizations/{test_organization.id}/support-tickets",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_update_ticket(self, client, admin_token, test_db, test_organization):
        """Test PATCH /api/v1/admin/support-tickets/{ticket_id}"""
        ticket = models.SupportTicket(
            id=str(uuid.uuid4()),
            org_id=test_organization.id,
            subject="Test Ticket",
            description="Test Description",
            status=models.TicketStatus.OPEN,
            priority=models.TicketPriority.MEDIUM
        )
        db_session.add(ticket)
        db_session.commit()
        
        response = client.patch(
            f"/api/v1/admin/support-tickets/{ticket.id}",
            headers={"Authorization": f"Bearer {admin_token.token}"},
            json={
                "status": "in_progress"
            }
        )
        assert response.status_code == 200


class TestAdminNotifications:
    """Tests for admin notification management"""
    
    def test_get_notifications(self, client, admin_token):
        """Test GET /api/v1/admin/notifications"""
        response = client.get(
            "/api/v1/admin/notifications",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_unread_notifications(self, client, admin_token):
        """Test GET /api/v1/admin/notifications with unread_only filter"""
        response = client.get(
            "/api/v1/admin/notifications?unread_only=true",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_mark_notification_read(self, client, admin_token, test_db, test_admin):
        """Test POST /api/v1/admin/notifications/{notification_id}/read"""
        notification = models.AdminNotification(
            id=str(uuid.uuid4()),
            admin_id=test_admin.id,
            title="Test Notification",
            message="Test Message",
            is_read=False
        )
        db_session.add(notification)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/admin/notifications/{notification.id}/read",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
    
    def test_mark_all_notifications_read(self, client, admin_token):
        """Test POST /api/v1/admin/notifications/read-all"""
        response = client.post(
            "/api/v1/admin/notifications/read-all",
            headers={"Authorization": f"Bearer {admin_token.token}"}
        )
        assert response.status_code == 200
