from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from src.models import (
    Organization, OrganizationCreate, OrganizationUpdate,
    User, OrgMemberCreate, OrgInvoice, OrgInvoiceCreate,
    SupportTicket, SupportTicketUpdate, AdminNotification, AdminStats
)
from src.services import organization_service_new, invoice_service_new, admin_service_new
from src.dependencies.auth_new import require_admin, get_current_user
from src.config.database import get_db
from src.utils.pagination import paginate_query, create_paginated_response

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/organizations", response_model=Organization)
async def create_org(
    org: OrganizationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create a new organization (admin only)."""
    return organization_service_new.create_organization(db, org)


@router.get("/organizations")
async def get_all_orgs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all organizations (admin only) with pagination."""
    from src.database.models import Organization as OrgModel
    query = db.query(OrgModel)
    items, total = paginate_query(query, page, page_size, sort_by, sort_order)
    return create_paginated_response(items, total, page, page_size)


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


@router.get("/organizations/{org_id}/members")
async def get_org_members(
    org_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all members of an organization (admin only) with pagination."""
    from src.database.models import User as UserModel
    query = db.query(UserModel).filter(UserModel.org_id == org_id)
    items, total = paginate_query(query, page, page_size)
    return create_paginated_response(items, total, page, page_size)


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


@router.get("/organizations/{org_id}/invoices")
async def get_invoices(
    org_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all invoices for an organization (admin only) with pagination."""
    from src.database.models import OrgInvoice as OrgInvoiceModel
    query = db.query(OrgInvoiceModel).filter(OrgInvoiceModel.org_id == org_id)
    items, total = paginate_query(query, page, page_size)
    return create_paginated_response(items, total, page, page_size)


@router.get("/stats", response_model=AdminStats)
async def get_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get admin dashboard statistics."""
    return admin_service_new.get_admin_stats(db)


@router.get("/organizations/newly-added", response_model=List[Organization])
async def get_newly_added_orgs(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get newly added organizations."""
    return admin_service_new.get_newly_added_orgs(db, limit)


@router.get("/organizations/recently-viewed", response_model=List[Organization])
async def get_recently_viewed_orgs(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get recently viewed organizations."""
    return admin_service_new.get_recently_viewed_orgs(db, admin.id, limit)


@router.post("/organizations/{org_id}/view")
async def record_org_view(
    org_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Record that an admin viewed an organization."""
    admin_service_new.record_org_view(db, admin.id, org_id)
    return {"message": "View recorded"}


@router.get("/support-tickets")
async def get_all_tickets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all support tickets (admin only) with pagination."""
    from src.database.models import SupportTicket as SupportTicketModel
    query = db.query(SupportTicketModel)
    items, total = paginate_query(query, page, page_size)
    return create_paginated_response(items, total, page, page_size)


@router.get("/organizations/{org_id}/support-tickets")
async def get_org_tickets(
    org_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get support tickets for an organization with pagination."""
    from src.database.models import SupportTicket as SupportTicketModel
    query = db.query(SupportTicketModel).filter(SupportTicketModel.org_id == org_id)
    items, total = paginate_query(query, page, page_size)
    return create_paginated_response(items, total, page, page_size)


@router.patch("/support-tickets/{ticket_id}", response_model=SupportTicket)
async def update_ticket(
    ticket_id: str,
    updates: SupportTicketUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a support ticket."""
    return admin_service_new.update_support_ticket(db, ticket_id, updates)


@router.get("/notifications")
async def get_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get admin notifications with pagination."""
    from src.database.models import AdminNotification as AdminNotificationModel
    query = db.query(AdminNotificationModel).filter(AdminNotificationModel.admin_id == admin.id)
    if unread_only:
        query = query.filter(AdminNotificationModel.is_read == False)
    items, total = paginate_query(query, page, page_size)
    return create_paginated_response(items, total, page, page_size)


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Mark a notification as read."""
    admin_service_new.mark_notification_as_read(db, notification_id)
    return {"message": "Notification marked as read"}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Mark all notifications as read."""
    admin_service_new.mark_all_notifications_as_read(db, admin.id)
    return {"message": "All notifications marked as read"}
