from datetime import datetime
from typing import List
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import (
    User, UserRole, TicketStatus,
    OrgTicketCreate, OrgTicketUpdate,
    TicketCommentCreate, TicketAttachmentCreate
)
from src.repositories import (
    OrgTicketRepository, OrganizationRepository,
    TicketCommentRepository, TicketAttachmentRepository
)
from src.utils.mappers import (
    db_org_ticket_to_pydantic, db_ticket_comment_to_pydantic,
    db_ticket_attachment_to_pydantic
)


def create_org_ticket(db: Session, user: User, ticket: OrgTicketCreate):
    """Create a new org ticket (org admin to super admin)."""
    ticket_repo = OrgTicketRepository(db)
    
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Only organization members can create org tickets")
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    ticket_id = str(uuid.uuid4())
    ticket_data = {
        "id": ticket_id,
        "org_id": user.org_id,
        "created_by": user.id,
        "title": ticket.title,
        "description": ticket.description,
        "ticket_type": ticket.ticket_type,
        "status": TicketStatus.OPEN,
        "priority": ticket.priority,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    db_ticket = ticket_repo.create(ticket_data)
    
    return db_org_ticket_to_pydantic(db_ticket)


def get_org_tickets_for_org(db: Session, user: User) -> List:
    """Get all org tickets for the user's organization."""
    ticket_repo = OrgTicketRepository(db)
    
    if user.role not in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    db_tickets = ticket_repo.get_by_org_id(user.org_id)
    return [db_org_ticket_to_pydantic(t) for t in db_tickets]


def get_all_org_tickets(db: Session, user: User) -> List:
    """Get all org tickets (admin only)."""
    ticket_repo = OrgTicketRepository(db)
    
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db_tickets = ticket_repo.get_all()
    return [db_org_ticket_to_pydantic(t) for t in db_tickets]


def get_org_ticket_by_id(db: Session, user: User, ticket_id: str):
    """Get an org ticket by ID."""
    ticket_repo = OrgTicketRepository(db)
    comment_repo = TicketCommentRepository(db)
    attachment_repo = TicketAttachmentRepository(db)
    
    db_ticket = ticket_repo.get_by_id(ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if user.role == UserRole.ADMIN:
        pass
    elif user.role in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        if user.org_id != db_ticket.org_id:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    ticket_pydantic = db_org_ticket_to_pydantic(db_ticket)
    
    db_comments = comment_repo.get_by_org_ticket_id(ticket_id)
    comments = [db_ticket_comment_to_pydantic(c) for c in db_comments]
    
    db_attachments = attachment_repo.get_by_org_ticket_id(ticket_id)
    attachments = [db_ticket_attachment_to_pydantic(a) for a in db_attachments]
    
    from src.models import OrgTicketWithDetails
    return OrgTicketWithDetails(
        **ticket_pydantic.model_dump(),
        comments=comments,
        attachments=attachments
    )


def update_org_ticket(db: Session, user: User, ticket_id: str, update: OrgTicketUpdate):
    """Update an org ticket."""
    ticket_repo = OrgTicketRepository(db)
    
    db_ticket = ticket_repo.get_by_id(ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if user.role == UserRole.ADMIN:
        pass
    elif user.role in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        if user.org_id != db_ticket.org_id:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    if update.status == TicketStatus.RESOLVED and not db_ticket.resolved_at:
        update_data["resolved_at"] = datetime.utcnow()
    
    db_ticket = ticket_repo.update(ticket_id, update_data)
    return db_org_ticket_to_pydantic(db_ticket)


def delete_org_ticket(db: Session, user: User, ticket_id: str):
    """Delete an org ticket."""
    ticket_repo = OrgTicketRepository(db)
    
    db_ticket = ticket_repo.get_by_id(ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if user.role == UserRole.ADMIN:
        pass
    elif user.role in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        if user.org_id != db_ticket.org_id:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    ticket_repo.delete(ticket_id)
    return {"message": "Ticket deleted successfully"}


def add_org_ticket_comment(db: Session, user: User, ticket_id: str, comment: TicketCommentCreate):
    """Add a comment to an org ticket."""
    ticket_repo = OrgTicketRepository(db)
    comment_repo = TicketCommentRepository(db)
    
    db_ticket = ticket_repo.get_by_id(ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if user.role == UserRole.ADMIN:
        pass
    elif user.role in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        if user.org_id != db_ticket.org_id:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    comment_id = str(uuid.uuid4())
    comment_data = {
        "id": comment_id,
        "org_ticket_id": ticket_id,
        "user_id": user.id,
        "comment": comment.comment,
        "is_internal": comment.is_internal,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    db_comment = comment_repo.create(comment_data)
    
    ticket_repo.update(ticket_id, {"updated_at": datetime.utcnow()})
    
    return db_ticket_comment_to_pydantic(db_comment)


def add_org_ticket_attachment(db: Session, user: User, ticket_id: str, attachment: TicketAttachmentCreate):
    """Add an attachment to an org ticket."""
    ticket_repo = OrgTicketRepository(db)
    attachment_repo = TicketAttachmentRepository(db)
    
    db_ticket = ticket_repo.get_by_id(ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if user.role == UserRole.ADMIN:
        pass
    elif user.role in [UserRole.ORG_OWNER, UserRole.ORG_MEMBER]:
        if user.org_id != db_ticket.org_id:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    attachment_id = str(uuid.uuid4())
    attachment_data = {
        "id": attachment_id,
        "org_ticket_id": ticket_id,
        "uploaded_by": user.id,
        "file_name": attachment.file_name,
        "file_url": attachment.file_url,
        "file_type": attachment.file_type,
        "file_size": attachment.file_size,
        "created_at": datetime.utcnow()
    }
    db_attachment = attachment_repo.create(attachment_data)
    
    ticket_repo.update(ticket_id, {"updated_at": datetime.utcnow()})
    
    return db_ticket_attachment_to_pydantic(db_attachment)


def get_my_assigned_org_tickets(db: Session, user: User) -> List:
    """Get all org tickets assigned to the current user (admin)."""
    ticket_repo = OrgTicketRepository(db)
    
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db_tickets = ticket_repo.get_by_assignee(user.id)
    return [db_org_ticket_to_pydantic(t) for t in db_tickets]
