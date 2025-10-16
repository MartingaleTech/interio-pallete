import pytest
from fastapi import HTTPException
from src.models import OrganizationCreate
from src.services.organization_service import create_organization, get_all_organizations
from src.database import get_organizations_db, get_users_db, get_passwords_db


def test_create_organization():
    """Test creating a new organization."""
    org_data = OrganizationCreate(
        name="Test Organization",
        email="org@example.com",
        phone="1234567890",
        address="123 Main St",
        city="Test City",
        state="Test State",
        pincode="12345",
        owner_email="owner@example.com",
        owner_name="Owner Name",
        owner_phone="0987654321",
        owner_password="password123",
        subscription_plan="basic"
    )
    
    result = create_organization(org_data)
    
    assert result.name == "Test Organization"
    assert result.email == "org@example.com"
    assert result.subscription_plan == "basic"
    
    get_organizations_db().clear()
    get_users_db().clear()
    get_passwords_db().clear()


def test_get_all_organizations():
    """Test getting all organizations."""
    organizations = get_all_organizations()
    assert isinstance(organizations, list)
