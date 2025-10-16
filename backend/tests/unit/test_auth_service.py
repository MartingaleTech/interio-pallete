import pytest
from fastapi import HTTPException
from src.models import UserLogin, PhoneOTPRequest, PhoneOTPVerify
from src.services.auth_service import login_user, logout_user, request_phone_otp, verify_phone_otp
from src.database import get_users_db, get_passwords_db, get_tokens_db, get_otp_db
from src.utils import hash_password


def test_login_user_success():
    """Test successful user login."""
    users_db = get_users_db()
    passwords_db = get_passwords_db()
    
    test_user_id = "test_user_1"
    users_db[test_user_id] = type('User', (), {
        'id': test_user_id,
        'email': 'test@example.com',
        'name': 'Test User',
        'role': 'org_member',
        'org_id': 'org_1',
        'created_at': '2024-01-01T00:00:00',
        'phone': '1234567890'
    })()
    passwords_db[test_user_id] = hash_password("password123")
    
    credentials = UserLogin(email="test@example.com", password="password123")
    result = login_user(credentials)
    
    assert "token" in result
    assert "user" in result
    
    users_db.clear()
    passwords_db.clear()
    get_tokens_db().clear()


def test_login_user_invalid_credentials():
    """Test login with invalid credentials."""
    credentials = UserLogin(email="nonexistent@example.com", password="wrongpassword")
    
    with pytest.raises(HTTPException) as exc_info:
        login_user(credentials)
    
    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in str(exc_info.value.detail)


def test_logout_user():
    """Test user logout."""
    tokens_db = get_tokens_db()
    tokens_db["test_token"] = "test_user_id"
    
    result = logout_user("test_token")
    
    assert result["message"] == "Logged out successfully"
    assert "test_token" not in tokens_db
