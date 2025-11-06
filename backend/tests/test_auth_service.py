import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from src.services import auth_service_new
from src.models import UserLogin, PhoneOTPRequest, PhoneOTPVerify
from src.database import models
import uuid


def test_login_user_success(db_session, test_user):
    """Test successful user login."""
    credentials = UserLogin(email="test@example.com", password="password123")
    result = auth_service_new.login_user(db_session, credentials)
    
    assert "token" in result
    assert "user" in result
    assert result["user"].email == "test@example.com"


def test_login_user_invalid_email(db_session):
    """Test login with invalid email."""
    credentials = UserLogin(email="nonexistent@example.com", password="password123")
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service_new.login_user(db_session, credentials)
    
    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in str(exc_info.value.detail)


def test_login_user_invalid_password(db_session, test_user):
    """Test login with invalid password."""
    credentials = UserLogin(email="test@example.com", password="wrongpassword")
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service_new.login_user(db_session, credentials)
    
    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in str(exc_info.value.detail)


def test_logout_user(db_session, test_user, test_token):
    """Test user logout."""
    result = auth_service_new.logout_user(db_session, "test_token_123")
    
    assert result["message"] == "Logged out successfully"
    
    token = db_session.query(models.Token).filter(
        models.Token.token == "test_token_123"
    ).first()
    assert token is None


def test_request_phone_otp_success(db_session, test_user):
    """Test successful OTP request."""
    request = PhoneOTPRequest(phone="1234567890")
    result = auth_service_new.request_phone_otp(db_session, request)
    
    assert result["message"] == "OTP sent successfully"
    assert result["phone"] == "1234567890"
    assert "otp" in result
    
    otp = db_session.query(models.OTP).filter(
        models.OTP.phone == "1234567890"
    ).first()
    assert otp is not None
    assert otp.user_id == test_user.id


def test_request_phone_otp_user_not_found(db_session):
    """Test OTP request for non-existent user."""
    request = PhoneOTPRequest(phone="9999999999")
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service_new.request_phone_otp(db_session, request)
    
    assert exc_info.value.status_code == 404
    assert "User with this phone number not found" in str(exc_info.value.detail)


def test_verify_phone_otp_success(db_session, test_user):
    """Test successful OTP verification."""
    otp = models.OTP(
        phone="1234567890",
        otp="123456",
        user_id=test_user.id,
        expires_at=datetime.now() + timedelta(minutes=10)
    )
    db_session.add(otp)
    db_session.commit()
    
    request = PhoneOTPVerify(phone="1234567890", otp="123456")
    result = auth_service_new.verify_phone_otp(db_session, request)
    
    assert "token" in result
    assert "user" in result
    assert result["user"].email == "test@example.com"
    
    otp_after = db_session.query(models.OTP).filter(
        models.OTP.phone == "1234567890"
    ).first()
    assert otp_after is None


def test_verify_phone_otp_not_found(db_session):
    """Test OTP verification when OTP doesn't exist."""
    request = PhoneOTPVerify(phone="1234567890", otp="123456")
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service_new.verify_phone_otp(db_session, request)
    
    assert exc_info.value.status_code == 400
    assert "No OTP found" in str(exc_info.value.detail)


def test_verify_phone_otp_expired(db_session, test_user):
    """Test OTP verification with expired OTP."""
    otp = models.OTP(
        phone="1234567890",
        otp="123456",
        user_id=test_user.id,
        expires_at=datetime.now() - timedelta(minutes=1)
    )
    db_session.add(otp)
    db_session.commit()
    
    request = PhoneOTPVerify(phone="1234567890", otp="123456")
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service_new.verify_phone_otp(db_session, request)
    
    assert exc_info.value.status_code == 400
    assert "OTP has expired" in str(exc_info.value.detail)


def test_verify_phone_otp_invalid(db_session, test_user):
    """Test OTP verification with invalid OTP."""
    otp = models.OTP(
        phone="1234567890",
        otp="123456",
        user_id=test_user.id,
        expires_at=datetime.now() + timedelta(minutes=10)
    )
    db_session.add(otp)
    db_session.commit()
    
    request = PhoneOTPVerify(phone="1234567890", otp="654321")
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service_new.verify_phone_otp(db_session, request)
    
    assert exc_info.value.status_code == 400
    assert "Invalid OTP" in str(exc_info.value.detail)
