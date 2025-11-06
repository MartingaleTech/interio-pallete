import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from src.services import organization_service_new, project_service_new, client_service_new, invoice_service_new
from src.models import (
    OrganizationCreate, OrgMemberCreate, ProjectCreate, ClientCreate, 
    InvoiceCreate, TeamMemberAdd, CalendarEventCreate, ProjectDesignCreate
)
from src.database import models
import uuid


class TestOrganizationService:
    """Test organization service."""
    
    def test_create_organization(self, db_session):
        """Test creating an organization."""
        org_data = OrganizationCreate(
            name="Test Org",
            email="testorg@example.com",
            phone="1234567890",
            address="123 Test St",
            city="Test City",
            state="Test State",
            pincode="12345",
            owner_email="owner@example.com",
            owner_name="Owner Name",
            owner_phone="9876543210",
            owner_password="password123",
            subscription_plan="basic"
        )
        
        org = organization_service_new.create_organization(db_session, org_data)
        
        assert org.name == "Test Org"
        assert org.email == "testorg@example.com"
    
    def test_get_all_organizations(self, db_session, test_organization):
        """Test getting all organizations."""
        orgs = organization_service_new.get_all_organizations(db_session)
        
        assert len(orgs) > 0
        assert any(org.id == test_organization.id for org in orgs)
    
    def test_get_organization_by_id(self, db_session, test_organization):
        """Test getting organization by ID."""
        org = organization_service_new.get_organization_by_id(db_session, test_organization.id)
        
        assert org is not None
        assert org.id == test_organization.id
    
    def test_delete_organization(self, db_session, test_organization):
        """Test deleting an organization."""
        result = organization_service_new.delete_organization(db_session, test_organization.id)
        
        assert result["message"] == "Organization deleted successfully"
    
    def test_get_organization_members(self, db_session, test_user, test_organization):
        """Test getting organization members."""
        members = organization_service_new.get_organization_members(db_session, test_organization.id)
        
        assert len(members) > 0
        assert any(m.id == test_user.id for m in members)
    
    def test_add_organization_member(self, db_session, test_organization):
        """Test adding a member to an organization."""
        member_data = OrgMemberCreate(
            email="newmember@example.com",
            name="New Member",
            password="password123",
            phone="5555555555"
        )
        
        member = organization_service_new.add_organization_member(
            db_session, test_organization.id, member_data
        )
        
        assert member.email == "newmember@example.com"
        assert member.org_id == test_organization.id


class TestProjectService:
    """Test project service."""
    
    def test_create_project(self, db_session, test_user, test_organization, test_client):
        """Test creating a project."""
        project_data = ProjectCreate(
            name="New Project",
            description="Project description",
            client_id=test_client.id,
            budget=10000.0,
            start_date=datetime.now().strftime("%Y-%m-%d"),
            end_date=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        )
        
        project = project_service_new.create_project(db_session, test_user, project_data)
        
        assert project.name == "New Project"
        assert project.org_id == test_organization.id


class TestClientService:
    """Test client service."""
    
    def test_add_client(self, db_session, test_user, test_organization):
        """Test adding a client."""
        client_data = ClientCreate(
            name="New Client",
            email="newclient@example.com",
            phone="1234567890",
            address="456 Client St",
            password="password123"
        )
        
        client = client_service_new.add_client(db_session, test_user, client_data)
        
        assert client.name == "New Client"
        assert client.org_id == test_organization.id
    
    def test_get_clients_for_org(self, db_session, test_user, test_client):
        """Test getting clients for organization."""
        clients = client_service_new.get_clients_for_org(db_session, test_user)
        
        assert len(clients) > 0
        assert any(c.id == test_client.id for c in clients)


class TestInvoiceService:
    """Test invoice service."""
    
    def test_create_project_invoice(self, db_session, test_user, test_project):
        """Test creating a project invoice."""
        invoice_data = InvoiceCreate(
            project_id=test_project.id,
            amount=5000.0,
            tax=500.0,
            due_date="2025-12-31"
        )
        
        invoice = invoice_service_new.create_project_invoice(
            db_session, test_user, test_project.id, invoice_data
        )
        
        assert invoice.amount == 5000.0
        assert invoice.project_id == test_project.id
    
    def test_get_project_invoices(self, db_session, test_user, test_project):
        """Test getting project invoices."""
        invoice_data = InvoiceCreate(
            project_id=test_project.id,
            amount=5000.0,
            tax=500.0,
            due_date="2025-12-31"
        )
        
        invoice_service_new.create_project_invoice(
            db_session, test_user, test_project.id, invoice_data
        )
        
        invoices = invoice_service_new.get_project_invoices(db_session, test_user, test_project.id)
        
        assert len(invoices) > 0
