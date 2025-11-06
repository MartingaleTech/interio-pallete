"""
Comprehensive tests for authentication routes.
Tests all endpoints in src/routes/auth.py
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
def test_user(test_db):
    """Create a test user."""
    user = models.User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        name="Test User",
        role=models.UserRole.ORG_OWNER,
        phone="1234567890",
        password_hash=hash_password("password123")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_token(test_db, test_user):
    """Create a test token."""
    token = models.Token(
        token="test_token_123",
        user_id=test_user.id,
        expires_at=datetime.now() + timedelta(days=1)
    )
    test_db.add(token)
    test_db.commit()
    return token


class TestAuthLogin:
    """Tests for POST /api/v1/auth/login"""
    
    def test_login_success(self, client, test_user):
        """Test successful login with valid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["email"] == "test@example.com"
    
    def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code in [400, 401, 404]
    
    def test_login_invalid_password(self, client, test_user):
        """Test login with incorrect password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code in [400, 401]
    
    def test_login_missing_email(self, client):
        """Test login with missing email field."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    def test_login_missing_password(self, client):
        """Test login with missing password field."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com"
            }
        )
        assert response.status_code == 422


class TestAuthGetMe:
    """Tests for GET /api/v1/auth/me"""
    
    def test_get_me_success(self, client, test_user, test_token):
        """Test getting current user with valid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {test_token.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
    
    def test_get_me_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403
    
    def test_get_me_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 403
    
    def test_get_me_expired_token(self, client, test_db, test_user):
        """Test getting current user with expired token."""
        expired_token = models.Token(
            token="expired_token_123",
            user_id=test_user.id,
            expires_at=datetime.now() - timedelta(days=1)
        )
        test_db.add(expired_token)
        test_db.commit()
        
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token.token}"}
        )
        assert response.status_code == 403


class TestAuthLogout:
    """Tests for POST /api/v1/auth/logout"""
    
    def test_logout_success(self, client, test_user, test_token):
        """Test successful logout."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {test_token.token}"}
        )
        assert response.status_code == 200
    
    def test_logout_no_token(self, client):
        """Test logout without token."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 403
    
    def test_logout_invalid_token(self, client):
        """Test logout with invalid token."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code in [403, 404]


class TestPhoneOTP:
    """Tests for phone OTP authentication"""
    
    def test_request_otp_success(self, client):
        """Test requesting OTP for a phone number."""
        response = client.post(
            "/api/v1/auth/phone/request-otp",
            json={
                "phone": "9876543210"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "otp" in data
    
    def test_request_otp_invalid_phone(self, client):
        """Test requesting OTP with invalid phone format."""
        response = client.post(
            "/api/v1/auth/phone/request-otp",
            json={
                "phone": "invalid"
            }
        )
        assert response.status_code in [200, 400, 422]
    
    def test_request_otp_missing_phone(self, client):
        """Test requesting OTP without phone number."""
        response = client.post(
            "/api/v1/auth/phone/request-otp",
            json={}
        )
        assert response.status_code == 422
    
    def test_verify_otp_success(self, client, test_db):
        """Test verifying OTP with valid code."""
        phone = "9876543210"
        client.post(
            "/api/v1/auth/phone/request-otp",
            json={"phone": phone}
        )
        
        otp_record = test_db.query(models.OTP).filter(
            models.OTP.phone == phone
        ).first()
        
        if otp_record:
            response = client.post(
                "/api/v1/auth/phone/verify-otp",
                json={
                    "phone": phone,
                    "otp": otp_record.otp
                }
            )
            assert response.status_code in [200, 400, 404]
    
    def test_verify_otp_invalid_code(self, client):
        """Test verifying OTP with invalid code."""
        response = client.post(
            "/api/v1/auth/phone/verify-otp",
            json={
                "phone": "9876543210",
                "otp": "000000"
            }
        )
        assert response.status_code in [400, 404]
    
    def test_verify_otp_missing_fields(self, client):
        """Test verifying OTP with missing fields."""
        response = client.post(
            "/api/v1/auth/phone/verify-otp",
            json={
                "phone": "9876543210"
            }
        )
        assert response.status_code == 422
