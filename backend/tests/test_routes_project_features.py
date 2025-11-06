"""
Comprehensive tests for project features routes.
Tests all endpoints in src/routes/project_features.py
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


class TestProjectNotifications:
    """Tests for project notification endpoints"""
    
    def test_create_project_notification(self, client, owner_token, test_project):
        """Test POST /api/v1/projects/{project_id}/notifications"""
        response = client.post(
            f"/api/v1/projects/{test_project.id}/notifications",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "title": "Project Update",
                "message": "Important project update",
                "priority": "high"
            }
        )
        assert response.status_code in [200, 201]
    
    def test_get_project_notifications(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/notifications"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/notifications",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_project_notifications_with_pagination(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/notifications with pagination"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/notifications?page=1&page_size=10",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_unread_project_notifications(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/notifications/unread"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/notifications/unread",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_mark_notification_as_read(self, client, owner_token, test_project, test_db):
        """Test PATCH /api/v1/projects/{project_id}/notifications/{notification_id}/read"""
        notification = models.ProjectNotification(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            title="Test Notification",
            message="Test Message",
            is_read=False
        )
        db_session.add(notification)
        db_session.commit()
        
        response = client.patch(
            f"/api/v1/projects/{test_project.id}/notifications/{notification.id}/read",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_mark_all_notifications_as_read(self, client, owner_token, test_project):
        """Test POST /api/v1/projects/{project_id}/notifications/mark-all-read"""
        response = client.post(
            f"/api/v1/projects/{test_project.id}/notifications/mark-all-read",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_delete_project_notification(self, client, owner_token, test_project, test_db):
        """Test DELETE /api/v1/projects/{project_id}/notifications/{notification_id}"""
        notification = models.ProjectNotification(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            title="Test Notification",
            message="Test Message",
            is_read=False
        )
        db_session.add(notification)
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/projects/{test_project.id}/notifications/{notification.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 204]


class TestProjectDailyUpdates:
    """Tests for project daily update endpoints"""
    
    def test_create_project_daily_update(self, client, owner_token, test_project):
        """Test POST /api/v1/projects/{project_id}/daily-updates"""
        response = client.post(
            f"/api/v1/projects/{test_project.id}/daily-updates",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "title": "Daily Progress",
                "description": "Today's progress update",
                "progress_percentage": 25.5
            }
        )
        assert response.status_code in [200, 201]
    
    def test_get_project_daily_updates(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/daily-updates"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/daily-updates",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_project_daily_updates_with_pagination(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/daily-updates with pagination"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/daily-updates?page=1&page_size=10",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_get_daily_update(self, client, owner_token, test_project, test_db):
        """Test GET /api/v1/projects/{project_id}/daily-updates/{update_id}"""
        update = models.ProjectDailyUpdate(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            title="Test Update",
            description="Test Description",
            progress_percentage=50.0
        )
        db_session.add(update)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/projects/{test_project.id}/daily-updates/{update.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 200
    
    def test_update_project_daily_update(self, client, owner_token, test_project, test_db):
        """Test PATCH /api/v1/projects/{project_id}/daily-updates/{update_id}"""
        update = models.ProjectDailyUpdate(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            title="Test Update",
            description="Test Description",
            progress_percentage=50.0
        )
        db_session.add(update)
        db_session.commit()
        
        response = client.patch(
            f"/api/v1/projects/{test_project.id}/daily-updates/{update.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "title": "Updated Title",
                "progress_percentage": 75.0
            }
        )
        assert response.status_code == 200
    
    def test_delete_project_daily_update(self, client, owner_token, test_project, test_db):
        """Test DELETE /api/v1/projects/{project_id}/daily-updates/{update_id}"""
        update = models.ProjectDailyUpdate(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            title="Test Update",
            description="Test Description",
            progress_percentage=50.0
        )
        db_session.add(update)
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/projects/{test_project.id}/daily-updates/{update.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 204]
    
    def test_create_daily_update_unauthorized(self, client, test_project):
        """Test creating daily update without authentication"""
        response = client.post(
            f"/api/v1/projects/{test_project.id}/daily-updates",
            json={
                "title": "Daily Progress",
                "description": "Test"
            }
        )
        assert response.status_code == 403
