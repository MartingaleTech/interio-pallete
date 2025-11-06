import pytest
from src.utils.security import hash_password, verify_password, create_token, generate_otp
from src.utils.notifications import send_otp_sms


class TestSecurity:
    """Test security utilities."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_token(self):
        """Test token creation."""
        token1 = create_token()
        token2 = create_token()
        
        assert len(token1) > 0
        assert len(token2) > 0
        assert token1 != token2
    
    def test_generate_otp(self):
        """Test OTP generation."""
        otp1 = generate_otp()
        otp2 = generate_otp()
        
        assert len(otp1) == 6
        assert len(otp2) == 6
        assert otp1.isdigit()
        assert otp2.isdigit()
        assert int(otp1) >= 100000
        assert int(otp1) <= 999999


class TestNotifications:
    """Test notification utilities."""
    
    def test_send_otp_sms(self):
        """Test sending OTP SMS (mock)."""
        result = send_otp_sms("1234567890", "123456")
        
        assert result is True
