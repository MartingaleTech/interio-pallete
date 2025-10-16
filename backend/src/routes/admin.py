from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from src.models import (
    Organization, OrganizationCreate, OrganizationUpdate,
    User, OrgMemberCreate, OrgInvoice, OrgInvoiceCreate
)
from src.services import organization_service_new, invoice_service_new
from src.dependencies.auth_new import require_admin
from src.config.database import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/organizations", response_model=Organization)
async def create_org(
    org: OrganizationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create a new organization (admin only)."""
    return organization_service_new.create_organization(db, org)


@router.get("/organizations", response_model=List[Organization])
async def get_all_orgs(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all organizations (admin only)."""
    return organization_service_new.get_all_organizations(db)


@router.get("/organizations/{org_id}", response_model=Organization)
async def get_org(
    org_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get an organization by ID (admin only)."""
    return organization_service_new.get_organization_by_id(db, org_id)


@router.patch("/organizations/{org_id}", response_model=Organization)
async def update_org(
    org_id: str,
    updates: OrganizationUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update an organization (admin only)."""
    return organization_service_new.update_organization(db, org_id, updates)


@router.delete("/organizations/{org_id}")
async def delete_org(
    org_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete an organization (admin only)."""
    return organization_service_new.delete_organization(db, org_id)


@router.get("/organizations/{org_id}/members", response_model=List[User])
async def get_org_members(
    org_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all members of an organization (admin only)."""
    return organization_service_new.get_organization_members(db, org_id)


@router.post("/organizations/{org_id}/members", response_model=User)
async def add_org_member(
    org_id: str,
    member: OrgMemberCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Add a member to an organization (admin only)."""
    return organization_service_new.add_organization_member(db, org_id, member)


@router.delete("/organizations/{org_id}/members/{user_id}")
async def remove_org_member(
    org_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Remove a member from an organization (admin only)."""
    return organization_service_new.remove_organization_member(db, org_id, user_id)


@router.post("/organizations/{org_id}/invoices", response_model=OrgInvoice)
async def create_invoice(
    org_id: str,
    invoice: OrgInvoiceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create an invoice for an organization (admin only)."""
    return invoice_service_new.create_org_invoice(db, org_id, invoice)


@router.get("/organizations/{org_id}/invoices", response_model=List[OrgInvoice])
async def get_invoices(
    org_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all invoices for an organization (admin only)."""
    return invoice_service_new.get_org_invoices(db, org_id)
