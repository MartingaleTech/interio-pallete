from sqlalchemy.orm import Session
from typing import Optional, List
from src.database import models


class ProjectTicketRepository:
    """Repository for ProjectTicket database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, ticket_data: dict) -> models.ProjectTicket:
        """Create a new project ticket."""
        db_ticket = models.ProjectTicket(**ticket_data)
        self.db.add(db_ticket)
        self.db.commit()
        self.db.refresh(db_ticket)
        return db_ticket
    
    def get_by_id(self, ticket_id: str) -> Optional[models.ProjectTicket]:
        """Get project ticket by ID."""
        return self.db.query(models.ProjectTicket).filter(models.ProjectTicket.id == ticket_id).first()
    
    def get_by_project_id(self, project_id: str) -> List[models.ProjectTicket]:
        """Get all tickets for a project."""
        return self.db.query(models.ProjectTicket).filter(
            models.ProjectTicket.project_id == project_id
        ).order_by(models.ProjectTicket.created_at.desc()).all()
    
    def get_by_org_id(self, org_id: str) -> List[models.ProjectTicket]:
        """Get all project tickets for an organization."""
        return self.db.query(models.ProjectTicket).filter(
            models.ProjectTicket.org_id == org_id
        ).order_by(models.ProjectTicket.created_at.desc()).all()
    
    def get_by_assignee(self, user_id: str) -> List[models.ProjectTicket]:
        """Get all tickets assigned to a user."""
        return self.db.query(models.ProjectTicket).filter(
            models.ProjectTicket.assigned_to == user_id
        ).order_by(models.ProjectTicket.created_at.desc()).all()
    
    def get_by_creator(self, user_id: str) -> List[models.ProjectTicket]:
        """Get all tickets created by a user."""
        return self.db.query(models.ProjectTicket).filter(
            models.ProjectTicket.created_by == user_id
        ).order_by(models.ProjectTicket.created_at.desc()).all()
    
    def update(self, ticket_id: str, update_data: dict) -> Optional[models.ProjectTicket]:
        """Update a project ticket."""
        ticket = self.get_by_id(ticket_id)
        if ticket:
            for key, value in update_data.items():
                if value is not None:
                    setattr(ticket, key, value)
            self.db.commit()
            self.db.refresh(ticket)
        return ticket
    
    def delete(self, ticket_id: str) -> bool:
        """Delete a project ticket."""
        ticket = self.get_by_id(ticket_id)
        if ticket:
            self.db.delete(ticket)
            self.db.commit()
            return True
        return False


class OrgTicketRepository:
    """Repository for OrgTicket database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, ticket_data: dict) -> models.OrgTicket:
        """Create a new org ticket."""
        db_ticket = models.OrgTicket(**ticket_data)
        self.db.add(db_ticket)
        self.db.commit()
        self.db.refresh(db_ticket)
        return db_ticket
    
    def get_by_id(self, ticket_id: str) -> Optional[models.OrgTicket]:
        """Get org ticket by ID."""
        return self.db.query(models.OrgTicket).filter(models.OrgTicket.id == ticket_id).first()
    
    def get_by_org_id(self, org_id: str) -> List[models.OrgTicket]:
        """Get all tickets for an organization."""
        return self.db.query(models.OrgTicket).filter(
            models.OrgTicket.org_id == org_id
        ).order_by(models.OrgTicket.created_at.desc()).all()
    
    def get_all(self) -> List[models.OrgTicket]:
        """Get all org tickets (for admin)."""
        return self.db.query(models.OrgTicket).order_by(
            models.OrgTicket.created_at.desc()
        ).all()
    
    def get_by_assignee(self, user_id: str) -> List[models.OrgTicket]:
        """Get all tickets assigned to a user (admin)."""
        return self.db.query(models.OrgTicket).filter(
            models.OrgTicket.assigned_to == user_id
        ).order_by(models.OrgTicket.created_at.desc()).all()
    
    def get_by_creator(self, user_id: str) -> List[models.OrgTicket]:
        """Get all tickets created by a user."""
        return self.db.query(models.OrgTicket).filter(
            models.OrgTicket.created_by == user_id
        ).order_by(models.OrgTicket.created_at.desc()).all()
    
    def update(self, ticket_id: str, update_data: dict) -> Optional[models.OrgTicket]:
        """Update an org ticket."""
        ticket = self.get_by_id(ticket_id)
        if ticket:
            for key, value in update_data.items():
                if value is not None:
                    setattr(ticket, key, value)
            self.db.commit()
            self.db.refresh(ticket)
        return ticket
    
    def delete(self, ticket_id: str) -> bool:
        """Delete an org ticket."""
        ticket = self.get_by_id(ticket_id)
        if ticket:
            self.db.delete(ticket)
            self.db.commit()
            return True
        return False


class TicketCommentRepository:
    """Repository for TicketComment database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, comment_data: dict) -> models.TicketComment:
        """Create a new ticket comment."""
        db_comment = models.TicketComment(**comment_data)
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def get_by_id(self, comment_id: str) -> Optional[models.TicketComment]:
        """Get comment by ID."""
        return self.db.query(models.TicketComment).filter(models.TicketComment.id == comment_id).first()
    
    def get_by_project_ticket_id(self, ticket_id: str) -> List[models.TicketComment]:
        """Get all comments for a project ticket."""
        return self.db.query(models.TicketComment).filter(
            models.TicketComment.project_ticket_id == ticket_id
        ).order_by(models.TicketComment.created_at.asc()).all()
    
    def get_by_org_ticket_id(self, ticket_id: str) -> List[models.TicketComment]:
        """Get all comments for an org ticket."""
        return self.db.query(models.TicketComment).filter(
            models.TicketComment.org_ticket_id == ticket_id
        ).order_by(models.TicketComment.created_at.asc()).all()
    
    def update(self, comment_id: str, update_data: dict) -> Optional[models.TicketComment]:
        """Update a comment."""
        comment = self.get_by_id(comment_id)
        if comment:
            for key, value in update_data.items():
                if value is not None:
                    setattr(comment, key, value)
            self.db.commit()
            self.db.refresh(comment)
        return comment
    
    def delete(self, comment_id: str) -> bool:
        """Delete a comment."""
        comment = self.get_by_id(comment_id)
        if comment:
            self.db.delete(comment)
            self.db.commit()
            return True
        return False


class TicketAttachmentRepository:
    """Repository for TicketAttachment database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, attachment_data: dict) -> models.TicketAttachment:
        """Create a new ticket attachment."""
        db_attachment = models.TicketAttachment(**attachment_data)
        self.db.add(db_attachment)
        self.db.commit()
        self.db.refresh(db_attachment)
        return db_attachment
    
    def get_by_id(self, attachment_id: str) -> Optional[models.TicketAttachment]:
        """Get attachment by ID."""
        return self.db.query(models.TicketAttachment).filter(
            models.TicketAttachment.id == attachment_id
        ).first()
    
    def get_by_project_ticket_id(self, ticket_id: str) -> List[models.TicketAttachment]:
        """Get all attachments for a project ticket."""
        return self.db.query(models.TicketAttachment).filter(
            models.TicketAttachment.project_ticket_id == ticket_id
        ).order_by(models.TicketAttachment.created_at.asc()).all()
    
    def get_by_org_ticket_id(self, ticket_id: str) -> List[models.TicketAttachment]:
        """Get all attachments for an org ticket."""
        return self.db.query(models.TicketAttachment).filter(
            models.TicketAttachment.org_ticket_id == ticket_id
        ).order_by(models.TicketAttachment.created_at.asc()).all()
    
    def delete(self, attachment_id: str) -> bool:
        """Delete an attachment."""
        attachment = self.get_by_id(attachment_id)
        if attachment:
            self.db.delete(attachment)
            self.db.commit()
            return True
        return False
