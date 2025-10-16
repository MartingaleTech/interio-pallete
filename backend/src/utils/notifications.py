def send_otp_sms(phone: str, otp: str) -> bool:
    """Mock function to send OTP via SMS."""
    print(f"[MOCK SMS] Sending OTP {otp} to {phone}")
    return True
