from datetime import datetime
from typing import List
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import (
    User, UserRole, TicketStatus,
    ProjectTicketCreate, ProjectTicketUpdate,
    TicketCommentCreate, TicketAttachmentCreate
)
from src.repositories import (
    ProjectTicketRepository, ProjectRepository, ClientRepository,
    TicketCommentRepository, TicketAttachmentRepository
)
from src.utils.mappers import (
    db_project_ticket_to_pydantic, db_ticket_comment_to_pydantic,
    db_ticket_attachment_to_pydantic
)


def create_project_ticket(db: Session, user: User, project_id: str, ticket: ProjectTicketCreate):
    """Create a new project ticket."""
    ticket_repo = ProjectTicketRepository(db)
    project_repo = ProjectRepository(db)
    client_repo = ClientRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        db_client = client_repo.get_by_email(user.email)
        if not db_client or db_project.client_id != db_client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != db_project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    ticket_id = str(uuid.uuid4())
    ticket_data = {
        "id": ticket_id,
        "project_id": project_id,
        "org_id": db_project.org_id,
        "created_by": user.id,
        "title": ticket.title,
        "description": ticket.description,
        "ticket_type": ticket.ticket_type,
        "status": TicketStatus.OPEN,
        "priority": ticket.priority,
        "created_at": datetime.now(datetime.UTC),
        "updated_at": datetime.now(datetime.UTC)
    }
    db_ticket = ticket_repo.create(ticket_data)
    
    return db_project_ticket_to_pydantic(db_ticket)


def get_project_tickets(db: Session, user: User, project_id: str) -> List:
    """Get all tickets for a project."""
    ticket_repo = ProjectTicketRepository(db)
    project_repo = ProjectRepository(db)
    client_repo = ClientRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        db_client = client_repo.get_by_email(user.email)
        if not db_client or db_project.client_id != db_client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != db_project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db_tickets = ticket_repo.get_by_project_id(project_id)
    return [db_project_ticket_to_pydantic(t) for t in db_tickets]


def get_project_ticket_by_id(db: Session, user: User, ticket_id: str):
    """Get a project ticket by ID."""
    ticket_repo = ProjectTicketRepository(db)
    project_repo = ProjectRepository(db)
    client_repo = ClientRepository(db)
    comment_repo = TicketCommentRepository(db)
    attachment_repo = TicketAttachmentRepository(db)
    
    db_ticket = ticket_repo.get_by_id(ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db_project = project_repo.get_by_id(db_ticket.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        db_client = client_repo.get_by_email(user.email)
        if not db_client or db_project.client_id != db_client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != db_project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    ticket_pydantic = db_project_ticket_to_pydantic(db_ticket)
    
    db_comments = comment_repo.get_by_project_ticket_id(ticket_id)
    comments = [db_ticket_comment_to_pydantic(c) for c in db_comments]
    
    db_attachments = attachment_repo.get_by_project_ticket_id(ticket_id)
    attachments = [db_ticket_attachment_to_pydantic(a) for a in db_attachments]
    
    from src.models import ProjectTicketWithDetails
    return ProjectTicketWithDetails(
        **ticket_pydantic.model_dump(),
        comments=comments,
        attachments=attachments
    )


def update_project_ticket(db: Session, user: User, ticket_id: str, update: ProjectTicketUpdate):
    """Update a project ticket."""
    ticket_repo = ProjectTicketRepository(db)
    project_repo = ProjectRepository(db)
    
    db_ticket = ticket_repo.get_by_id(ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db_project = project_repo.get_by_id(db_ticket.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Clients cannot update tickets")
    
    if user.org_id != db_project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(datetime.UTC)
    
    if update.status == TicketStatus.RESOLVED and not db_ticket.resolved_at:
        update_data["resolved_at"] = datetime.now(datetime.UTC)
    
    db_ticket = ticket_repo.update(ticket_id, update_data)
    return db_project_ticket_to_pydantic(db_ticket)


def delete_project_ticket(db: Session, user: User, ticket_id: str):
    """Delete a project ticket."""
    ticket_repo = ProjectTicketRepository(db)
    project_repo = ProjectRepository(db)
    
    db_ticket = ticket_repo.get_by_id(ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db_project = project_repo.get_by_id(db_ticket.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Clients cannot delete tickets")
    
    if user.org_id != db_project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    ticket_repo.delete(ticket_id)
    return {"message": "Ticket deleted successfully"}


def add_ticket_comment(db: Session, user: User, ticket_id: str, comment: TicketCommentCreate):
    """Add a comment to a project ticket."""
    ticket_repo = ProjectTicketRepository(db)
    project_repo = ProjectRepository(db)
    client_repo = ClientRepository(db)
    comment_repo = TicketCommentRepository(db)
    
    db_ticket = ticket_repo.get_by_id(ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db_project = project_repo.get_by_id(db_ticket.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        db_client = client_repo.get_by_email(user.email)
        if not db_client or db_project.client_id != db_client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != db_project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    comment_id = str(uuid.uuid4())
    comment_data = {
        "id": comment_id,
        "project_ticket_id": ticket_id,
        "user_id": user.id,
        "comment": comment.comment,
        "is_internal": comment.is_internal,
        "created_at": datetime.now(datetime.UTC),
        "updated_at": datetime.now(datetime.UTC)
    }
    db_comment = comment_repo.create(comment_data)
    
    ticket_repo.update(ticket_id, {"updated_at": datetime.now(datetime.UTC)})
    
    return db_ticket_comment_to_pydantic(db_comment)


def add_ticket_attachment(db: Session, user: User, ticket_id: str, attachment: TicketAttachmentCreate):
    """Add an attachment to a project ticket."""
    ticket_repo = ProjectTicketRepository(db)
    project_repo = ProjectRepository(db)
    client_repo = ClientRepository(db)
    attachment_repo = TicketAttachmentRepository(db)
    
    db_ticket = ticket_repo.get_by_id(ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db_project = project_repo.get_by_id(db_ticket.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        db_client = client_repo.get_by_email(user.email)
        if not db_client or db_project.client_id != db_client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != db_project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    attachment_id = str(uuid.uuid4())
    attachment_data = {
        "id": attachment_id,
        "project_ticket_id": ticket_id,
        "uploaded_by": user.id,
        "file_name": attachment.file_name,
        "file_url": attachment.file_url,
        "file_type": attachment.file_type,
        "file_size": attachment.file_size,
        "created_at": datetime.now(datetime.UTC)
    }
    db_attachment = attachment_repo.create(attachment_data)
    
    ticket_repo.update(ticket_id, {"updated_at": datetime.now(datetime.UTC)})
    
    return db_ticket_attachment_to_pydantic(db_attachment)


def get_my_assigned_tickets(db: Session, user: User) -> List:
    """Get all project tickets assigned to the current user."""
    ticket_repo = ProjectTicketRepository(db)
    
    if user.role == UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Clients cannot be assigned tickets")
    
    db_tickets = ticket_repo.get_by_assignee(user.id)
    return [db_project_ticket_to_pydantic(t) for t in db_tickets]
