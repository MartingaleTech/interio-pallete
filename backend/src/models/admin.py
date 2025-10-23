from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RecentlyViewedOrg(BaseModel):
    id: str
    admin_id: str
    org_id: str
    viewed_at: datetime
    
    class Config:
        from_attributes = True


class SupportTicket(BaseModel):
    id: str
    org_id: str
    created_by: str
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SupportTicketCreate(BaseModel):
    subject: str
    description: str
    priority: str = "medium"


class SupportTicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None


class AdminNotification(BaseModel):
    id: str
    admin_id: str
    org_id: Optional[str]
    notification_type: str
    title: str
    message: str
    is_read: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminNotificationCreate(BaseModel):
    admin_id: str
    org_id: Optional[str] = None
    notification_type: str
    title: str
    message: str


class AdminStats(BaseModel):
    total_orgs: int
    active_orgs: int
    inactive_orgs: int
    total_projects: int
    total_revenue: float
    pending_tickets: int
