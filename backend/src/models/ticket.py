from pydantic import BaseModel
from typing import Optional, List
from .enums import TicketStatus, TicketPriority, TicketType


class ProjectTicket(BaseModel):
    id: str
    project_id: str
    org_id: str
    created_by: str
    assigned_to: Optional[str] = None
    title: str
    description: str
    ticket_type: TicketType
    status: TicketStatus
    priority: TicketPriority
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None
    creator_name: Optional[str] = None
    assignee_name: Optional[str] = None


class ProjectTicketCreate(BaseModel):
    title: str
    description: str
    ticket_type: TicketType
    priority: TicketPriority = TicketPriority.MEDIUM


class ProjectTicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    ticket_type: Optional[TicketType] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None


class OrgTicket(BaseModel):
    id: str
    org_id: str
    created_by: str
    assigned_to: Optional[str] = None
    title: str
    description: str
    ticket_type: TicketType
    status: TicketStatus
    priority: TicketPriority
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None
    creator_name: Optional[str] = None
    assignee_name: Optional[str] = None
    org_name: Optional[str] = None


class OrgTicketCreate(BaseModel):
    title: str
    description: str
    ticket_type: TicketType
    priority: TicketPriority = TicketPriority.MEDIUM


class OrgTicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    ticket_type: Optional[TicketType] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None


class TicketComment(BaseModel):
    id: str
    project_ticket_id: Optional[str] = None
    org_ticket_id: Optional[str] = None
    user_id: str
    comment: str
    is_internal: bool = False
    created_at: str
    updated_at: str
    user_name: Optional[str] = None


class TicketCommentCreate(BaseModel):
    comment: str
    is_internal: bool = False


class TicketAttachment(BaseModel):
    id: str
    project_ticket_id: Optional[str] = None
    org_ticket_id: Optional[str] = None
    uploaded_by: str
    file_name: str
    file_url: str
    file_type: str
    file_size: int
    created_at: str
    uploader_name: Optional[str] = None


class TicketAttachmentCreate(BaseModel):
    file_name: str
    file_url: str
    file_type: str
    file_size: int


class ProjectTicketWithDetails(ProjectTicket):
    comments: List[TicketComment] = []
    attachments: List[TicketAttachment] = []


class OrgTicketWithDetails(OrgTicket):
    comments: List[TicketComment] = []
    attachments: List[TicketAttachment] = []
