"""
Comprehensive tests for organization routes.
Tests all endpoints in src/routes/organizations.py
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


class TestOrganizationMembers:
    """Tests for organization member management"""
    
    def test_get_organization_members(self, client, owner_token, test_organization):
        """Test GET /api/v1/organizations/members"""
        response = client.get(
            "/api/v1/organizations/members",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    def test_get_organization_members_with_pagination(self, client, owner_token, test_organization):
        """Test GET /api/v1/organizations/members with pagination"""
        response = client.get(
            "/api/v1/organizations/members?page=1&page_size=10",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_members_unauthorized(self, client):
        """Test getting members without authentication"""
        response = client.get("/api/v1/organizations/members")
        assert response.status_code == 403
    
    def test_add_organization_member(self, client, owner_token, test_organization):
        """Test POST /api/v1/organizations/members"""
        response = client.post(
            "/api/v1/organizations/members",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "email": "newmember@example.com",
                "name": "New Member",
                "phone": "9876543210",
                "role": "org_member"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["email"] == "newmember@example.com"
    
    def test_add_member_missing_fields(self, client, owner_token):
        """Test adding member with missing required fields"""
        response = client.post(
            "/api/v1/organizations/members",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "email": "incomplete@example.com"
            }
        )
        assert response.status_code == 422
    
    def test_update_organization_member(self, client, owner_token, test_organization, test_db):
        """Test PUT /api/v1/organizations/members/{member_id}"""
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
        
        response = client.put(
            f"/api/v1/organizations/members/{member.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "email": "member@example.com",
                "name": "Updated Member Name",
                "phone": "1234567890",
                "role": "org_member"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Member Name"
    
    def test_remove_organization_member(self, client, owner_token, test_organization, test_db):
        """Test DELETE /api/v1/organizations/members/{member_id}"""
        member = models.User(
            id=str(uuid.uuid4()),
            email="removeme@example.com",
            name="Remove Me",
            role=models.UserRole.ORG_MEMBER,
            phone="1234567890",
            password_hash=hash_password("password123"),
            org_id=test_organization.id
        )
        db_session.add(member)
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/organizations/members/{member.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 204]


class TestSupportTickets:
    """Tests for organization support tickets"""
    
    def test_create_support_ticket(self, client, owner_token, test_organization):
        """Test POST /api/v1/organizations/support-tickets"""
        response = client.post(
            "/api/v1/organizations/support-tickets",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "subject": "Test Support Ticket",
                "description": "This is a test support ticket",
                "priority": "medium"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["subject"] == "Test Support Ticket"
    
    def test_create_ticket_without_org(self, client, test_db):
        """Test creating ticket for user without organization"""
        user = models.User(
            id=str(uuid.uuid4()),
            email="noorg@example.com",
            name="No Org User",
            role=models.UserRole.ORG_OWNER,
            phone="1234567890",
            password_hash=hash_password("password123")
        )
        db_session.add(user)
        db_session.commit()
        
        token = models.Token(
            token="noorg_token_123",
            user_id=user.id,
            expires_at=datetime.now() + timedelta(days=1)
        )
        db_session.add(token)
        db_session.commit()
        
        response = client.post(
            "/api/v1/organizations/support-tickets",
            headers={"Authorization": f"Bearer {token.token}"},
            json={
                "subject": "Test Ticket",
                "description": "Test"
            }
        )
        assert response.status_code == 400
    
    def test_get_organization_support_tickets(self, client, owner_token, test_organization):
        """Test GET /api/v1/organizations/support-tickets"""
        response = client.get(
            "/api/v1/organizations/support-tickets",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    def test_get_tickets_with_pagination(self, client, owner_token, test_organization):
        """Test GET /api/v1/organizations/support-tickets with pagination"""
        response = client.get(
            "/api/v1/organizations/support-tickets?page=1&page_size=5",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
