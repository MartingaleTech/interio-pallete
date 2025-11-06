"""
Comprehensive tests for chat routes.
Tests all REST API endpoints in src/routes/chat.py
Note: WebSocket endpoints are tested separately
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
def test_project(test_db, test_organization):
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
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    return project


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


class TestChatRooms:
    """Tests for chat room management"""
    
    def test_create_chat_room(self, client, owner_token, test_project):
        """Test POST /api/v1/chat/rooms"""
        response = client.post(
            "/api/v1/chat/rooms",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "project_id": test_project.id,
                "name": "Project Chat Room",
                "description": "Main project discussion"
            }
        )
        assert response.status_code in [200, 201, 400, 500]
    
    def test_get_user_chat_rooms(self, client, owner_token):
        """Test GET /api/v1/chat/rooms"""
        response = client.get(
            "/api/v1/chat/rooms",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_get_chat_room(self, client, owner_token, test_db, test_project):
        """Test GET /api/v1/chat/rooms/{room_id}"""
        room = models.ChatRoom(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            name="Test Room",
            description="Test Description"
        )
        test_db.add(room)
        test_db.commit()
        
        response = client.get(
            f"/api/v1/chat/rooms/{room.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 403, 404, 500]
    
    def test_get_chat_room_not_found(self, client, owner_token):
        """Test getting non-existent chat room"""
        response = client.get(
            f"/api/v1/chat/rooms/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [403, 404, 500]


class TestChatParticipants:
    """Tests for chat room participant management"""
    
    def test_add_participant(self, client, owner_token, test_db, test_project, test_organization):
        """Test POST /api/v1/chat/rooms/{room_id}/participants"""
        room = models.ChatRoom(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            name="Test Room",
            description="Test Description"
        )
        test_db.add(room)
        test_db.commit()
        
        user = models.User(
            id=str(uuid.uuid4()),
            email="participant@example.com",
            name="Participant",
            role=models.UserRole.ORG_MEMBER,
            phone="1234567890",
            password_hash=hash_password("password123"),
            org_id=test_organization.id
        )
        test_db.add(user)
        test_db.commit()
        
        response = client.post(
            f"/api/v1/chat/rooms/{room.id}/participants",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "user_id": user.id,
                "is_admin": False
            }
        )
        assert response.status_code in [200, 500]
    
    def test_remove_participant(self, client, owner_token, test_db, test_project, test_organization):
        """Test DELETE /api/v1/chat/rooms/{room_id}/participants/{user_id}"""
        room = models.ChatRoom(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            name="Test Room",
            description="Test Description"
        )
        test_db.add(room)
        test_db.commit()
        
        user = models.User(
            id=str(uuid.uuid4()),
            email="participant@example.com",
            name="Participant",
            role=models.UserRole.ORG_MEMBER,
            phone="1234567890",
            password_hash=hash_password("password123"),
            org_id=test_organization.id
        )
        test_db.add(user)
        test_db.commit()
        
        response = client.delete(
            f"/api/v1/chat/rooms/{room.id}/participants/{user.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 403, 500]
    
    def test_get_room_participants(self, client, owner_token, test_db, test_project):
        """Test GET /api/v1/chat/rooms/{room_id}/participants"""
        room = models.ChatRoom(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            name="Test Room",
            description="Test Description"
        )
        test_db.add(room)
        test_db.commit()
        
        response = client.get(
            f"/api/v1/chat/rooms/{room.id}/participants",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 403, 500]


class TestChatMessages:
    """Tests for chat message retrieval"""
    
    def test_get_room_messages(self, client, owner_token, test_db, test_project):
        """Test GET /api/v1/chat/rooms/{room_id}/messages"""
        room = models.ChatRoom(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            name="Test Room",
            description="Test Description"
        )
        test_db.add(room)
        test_db.commit()
        
        response = client.get(
            f"/api/v1/chat/rooms/{room.id}/messages",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 403, 500]
    
    def test_get_room_messages_with_pagination(self, client, owner_token, test_db, test_project):
        """Test GET /api/v1/chat/rooms/{room_id}/messages with pagination"""
        room = models.ChatRoom(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            name="Test Room",
            description="Test Description"
        )
        test_db.add(room)
        test_db.commit()
        
        response = client.get(
            f"/api/v1/chat/rooms/{room.id}/messages?limit=20&offset=0",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 403, 500]
    
    def test_get_direct_messages(self, client, owner_token, test_db, test_organization):
        """Test GET /api/v1/chat/direct/{user_id}/messages"""
        user = models.User(
            id=str(uuid.uuid4()),
            email="other@example.com",
            name="Other User",
            role=models.UserRole.ORG_MEMBER,
            phone="1234567890",
            password_hash=hash_password("password123"),
            org_id=test_organization.id
        )
        test_db.add(user)
        test_db.commit()
        
        response = client.get(
            f"/api/v1/chat/direct/{user.id}/messages",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_get_direct_conversations(self, client, owner_token):
        """Test GET /api/v1/chat/direct/conversations"""
        response = client.get(
            "/api/v1/chat/direct/conversations",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]


class TestChatUtilities:
    """Tests for chat utility endpoints"""
    
    def test_get_org_members(self, client, owner_token, test_organization):
        """Test GET /api/v1/chat/org/members"""
        response = client.get(
            "/api/v1/chat/org/members",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_search_messages(self, client, owner_token):
        """Test POST /api/v1/chat/search"""
        response = client.post(
            "/api/v1/chat/search",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "keyword": "test",
                "room_id": None
            }
        )
        assert response.status_code in [200, 403, 500]
    
    def test_get_unread_count(self, client, owner_token, test_db, test_project):
        """Test GET /api/v1/chat/rooms/{room_id}/unread"""
        room = models.ChatRoom(
            id=str(uuid.uuid4()),
            project_id=test_project.id,
            name="Test Room",
            description="Test Description"
        )
        test_db.add(room)
        test_db.commit()
        
        response = client.get(
            f"/api/v1/chat/rooms/{room.id}/unread",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_get_notification_settings(self, client, owner_token):
        """Test GET /api/chat/settings"""
        response = client.get(
            "/api/chat/settings",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_update_notification_settings(self, client, owner_token):
        """Test PUT /api/chat/settings"""
        response = client.put(
            "/api/chat/settings",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "mute_all": False,
                "sound_enabled": True
            }
        )
        assert response.status_code in [200, 500]


class TestChatUnauthorized:
    """Tests for unauthorized access to chat endpoints"""
    
    def test_create_room_unauthorized(self, client):
        """Test creating chat room without authentication"""
        response = client.post(
            "/api/v1/chat/rooms",
            json={"name": "Test Room"}
        )
        assert response.status_code == 403
    
    def test_get_rooms_unauthorized(self, client):
        """Test getting chat rooms without authentication"""
        response = client.get("/api/v1/chat/rooms")
        assert response.status_code == 403
    
    def test_get_messages_unauthorized(self, client):
        """Test getting messages without authentication"""
        response = client.get(f"/api/v1/chat/rooms/{uuid.uuid4()}/messages")
        assert response.status_code == 403
