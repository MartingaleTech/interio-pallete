from fastapi import APIRouter, Depends
from typing import List
from src.models import (
    Organization, OrganizationCreate, OrganizationUpdate,
    User, OrgMemberCreate, OrgInvoice, OrgInvoiceCreate
)
from src.services import (
    create_organization, get_all_organizations, get_organization_by_id,
    update_organization, delete_organization, get_organization_members,
    add_organization_member, remove_organization_member,
    create_org_invoice, get_org_invoices
)
from src.dependencies import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/organizations", response_model=Organization)
async def create_org(org: OrganizationCreate, admin: User = Depends(require_admin)):
    """Create a new organization (admin only)."""
    return create_organization(org)


@router.get("/organizations", response_model=List[Organization])
async def get_all_orgs(admin: User = Depends(require_admin)):
    """Get all organizations (admin only)."""
    return get_all_organizations()


@router.get("/organizations/{org_id}", response_model=Organization)
async def get_org(org_id: str, admin: User = Depends(require_admin)):
    """Get an organization by ID (admin only)."""
    return get_organization_by_id(org_id)


@router.patch("/organizations/{org_id}", response_model=Organization)
async def update_org(org_id: str, updates: OrganizationUpdate, admin: User = Depends(require_admin)):
    """Update an organization (admin only)."""
    return update_organization(org_id, updates)


@router.delete("/organizations/{org_id}")
async def delete_org(org_id: str, admin: User = Depends(require_admin)):
    """Delete an organization (admin only)."""
    return delete_organization(org_id)


@router.get("/organizations/{org_id}/members", response_model=List[User])
async def get_org_members(org_id: str, admin: User = Depends(require_admin)):
    """Get all members of an organization (admin only)."""
    return get_organization_members(org_id)


@router.post("/organizations/{org_id}/members", response_model=User)
async def add_org_member(org_id: str, member: OrgMemberCreate, admin: User = Depends(require_admin)):
    """Add a member to an organization (admin only)."""
    return add_organization_member(org_id, member)


@router.delete("/organizations/{org_id}/members/{user_id}")
async def remove_org_member(org_id: str, user_id: str, admin: User = Depends(require_admin)):
    """Remove a member from an organization (admin only)."""
    return remove_organization_member(org_id, user_id)


@router.post("/organizations/{org_id}/invoices", response_model=OrgInvoice)
async def create_invoice(org_id: str, invoice: OrgInvoiceCreate, admin: User = Depends(require_admin)):
    """Create an invoice for an organization (admin only)."""
    return create_org_invoice(org_id, invoice)


@router.get("/organizations/{org_id}/invoices", response_model=List[OrgInvoice])
async def get_invoices(org_id: str, admin: User = Depends(require_admin)):
    """Get all invoices for an organization (admin only)."""
    return get_org_invoices(org_id)
