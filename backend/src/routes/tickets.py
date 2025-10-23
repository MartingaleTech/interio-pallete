from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from src.models import (
    User, ProjectTicket, ProjectTicketCreate, ProjectTicketUpdate, ProjectTicketWithDetails,
    OrgTicket, OrgTicketCreate, OrgTicketUpdate, OrgTicketWithDetails,
    TicketComment, TicketCommentCreate, TicketAttachment, TicketAttachmentCreate
)
from src.services import project_ticket_service, org_ticket_service
from src.dependencies.auth_new import require_org_access, get_current_user, require_admin
from src.config.database import get_db

project_ticket_router = APIRouter(prefix="/api/projects", tags=["project-tickets"])


@project_ticket_router.post("/{project_id}/tickets", response_model=ProjectTicket)
async def create_project_ticket(
    project_id: str,
    ticket: ProjectTicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new ticket for a project."""
    return project_ticket_service.create_project_ticket(db, user, project_id, ticket)


@project_ticket_router.get("/{project_id}/tickets", response_model=List[ProjectTicket])
async def get_project_tickets(
    project_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all tickets for a project."""
    return project_ticket_service.get_project_tickets(db, user, project_id)


@project_ticket_router.get("/{project_id}/tickets/{ticket_id}", response_model=ProjectTicketWithDetails)
async def get_project_ticket(
    project_id: str,
    ticket_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get a specific project ticket with comments and attachments."""
    return project_ticket_service.get_project_ticket_by_id(db, user, ticket_id)


@project_ticket_router.patch("/{project_id}/tickets/{ticket_id}", response_model=ProjectTicket)
async def update_project_ticket(
    project_id: str,
    ticket_id: str,
    update: ProjectTicketUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Update a project ticket."""
    return project_ticket_service.update_project_ticket(db, user, ticket_id, update)


@project_ticket_router.delete("/{project_id}/tickets/{ticket_id}")
async def delete_project_ticket(
    project_id: str,
    ticket_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Delete a project ticket."""
    return project_ticket_service.delete_project_ticket(db, user, ticket_id)


@project_ticket_router.post("/{project_id}/tickets/{ticket_id}/comments", response_model=TicketComment)
async def add_project_ticket_comment(
    project_id: str,
    ticket_id: str,
    comment: TicketCommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Add a comment to a project ticket."""
    return project_ticket_service.add_ticket_comment(db, user, ticket_id, comment)


@project_ticket_router.post("/{project_id}/tickets/{ticket_id}/attachments", response_model=TicketAttachment)
async def add_project_ticket_attachment(
    project_id: str,
    ticket_id: str,
    attachment: TicketAttachmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Add an attachment to a project ticket."""
    return project_ticket_service.add_ticket_attachment(db, user, ticket_id, attachment)


org_ticket_router = APIRouter(prefix="/api/organizations/tickets", tags=["org-tickets"])


@org_ticket_router.post("", response_model=OrgTicket)
async def create_org_ticket(
    ticket: OrgTicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Create a new org ticket (org admin to super admin)."""
    return org_ticket_service.create_org_ticket(db, user, ticket)


@org_ticket_router.get("", response_model=List[OrgTicket])
async def get_org_tickets(
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Get all org tickets for the user's organization."""
    return org_ticket_service.get_org_tickets_for_org(db, user)


@org_ticket_router.get("/{ticket_id}", response_model=OrgTicketWithDetails)
async def get_org_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Get a specific org ticket with comments and attachments."""
    return org_ticket_service.get_org_ticket_by_id(db, user, ticket_id)


@org_ticket_router.patch("/{ticket_id}", response_model=OrgTicket)
async def update_org_ticket(
    ticket_id: str,
    update: OrgTicketUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Update an org ticket."""
    return org_ticket_service.update_org_ticket(db, user, ticket_id, update)


@org_ticket_router.delete("/{ticket_id}")
async def delete_org_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Delete an org ticket."""
    return org_ticket_service.delete_org_ticket(db, user, ticket_id)


@org_ticket_router.post("/{ticket_id}/comments", response_model=TicketComment)
async def add_org_ticket_comment(
    ticket_id: str,
    comment: TicketCommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Add a comment to an org ticket."""
    return org_ticket_service.add_org_ticket_comment(db, user, ticket_id, comment)


@org_ticket_router.post("/{ticket_id}/attachments", response_model=TicketAttachment)
async def add_org_ticket_attachment(
    ticket_id: str,
    attachment: TicketAttachmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Add an attachment to an org ticket."""
    return org_ticket_service.add_org_ticket_attachment(db, user, ticket_id, attachment)


admin_ticket_router = APIRouter(prefix="/api/admin/tickets", tags=["admin-tickets"])


@admin_ticket_router.get("", response_model=List[OrgTicket])
async def get_all_org_tickets(
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Get all org tickets (admin only)."""
    return org_ticket_service.get_all_org_tickets(db, user)


@admin_ticket_router.get("/assigned", response_model=List[OrgTicket])
async def get_my_assigned_tickets(
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Get all org tickets assigned to me (admin)."""
    return org_ticket_service.get_my_assigned_org_tickets(db, user)


@admin_ticket_router.get("/{ticket_id}", response_model=OrgTicketWithDetails)
async def get_org_ticket_admin(
    ticket_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Get a specific org ticket (admin view)."""
    return org_ticket_service.get_org_ticket_by_id(db, user, ticket_id)


@admin_ticket_router.patch("/{ticket_id}", response_model=OrgTicket)
async def update_org_ticket_admin(
    ticket_id: str,
    update: OrgTicketUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Update an org ticket (admin)."""
    return org_ticket_service.update_org_ticket(db, user, ticket_id, update)


@admin_ticket_router.post("/{ticket_id}/comments", response_model=TicketComment)
async def add_org_ticket_comment_admin(
    ticket_id: str,
    comment: TicketCommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Add a comment to an org ticket (admin)."""
    return org_ticket_service.add_org_ticket_comment(db, user, ticket_id, comment)


my_tickets_router = APIRouter(prefix="/api/my-tickets", tags=["my-tickets"])


@my_tickets_router.get("/assigned", response_model=List[ProjectTicket])
async def get_my_assigned_project_tickets(
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Get all project tickets assigned to me."""
    return project_ticket_service.get_my_assigned_tickets(db, user)
