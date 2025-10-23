from datetime import datetime
from typing import List
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException
from src.models import (
    User, SupportTicket, SupportTicketCreate, SupportTicketUpdate,
    AdminNotification, AdminNotificationCreate, AdminStats
)
from src.database.models import (
    RecentlyViewedOrg as DBRecentlyViewedOrg,
    SupportTicket as DBSupportTicket,
    AdminNotification as DBAdminNotification,
    Organization as DBOrganization,
    Project as DBProject,
    OrgInvoice as DBOrgInvoice
)


def record_org_view(db: Session, admin_id: str, org_id: str):
    """Record that an admin viewed an organization."""
    existing = db.query(DBRecentlyViewedOrg).filter(
        DBRecentlyViewedOrg.admin_id == admin_id,
        DBRecentlyViewedOrg.org_id == org_id
    ).first()
    
    if existing:
        existing.viewed_at = datetime.utcnow()
        db.commit()
    else:
        view_record = DBRecentlyViewedOrg(
            id=str(uuid.uuid4()),
            admin_id=admin_id,
            org_id=org_id,
            viewed_at=datetime.utcnow()
        )
        db.add(view_record)
        db.commit()


def get_recently_viewed_orgs(db: Session, admin_id: str, limit: int = 5):
    """Get recently viewed organizations for an admin."""
    views = db.query(DBRecentlyViewedOrg).filter(
        DBRecentlyViewedOrg.admin_id == admin_id
    ).order_by(desc(DBRecentlyViewedOrg.viewed_at)).limit(limit).all()
    
    orgs = []
    for view in views:
        org = db.query(DBOrganization).filter(DBOrganization.id == view.org_id).first()
        if org:
            from src.utils.mappers import db_organization_to_pydantic
            orgs.append(db_organization_to_pydantic(org))
    
    return orgs


def get_newly_added_orgs(db: Session, limit: int = 5):
    """Get newly added organizations."""
    orgs = db.query(DBOrganization).order_by(
        desc(DBOrganization.created_at)
    ).limit(limit).all()
    
    from src.utils.mappers import db_organization_to_pydantic
    return [db_organization_to_pydantic(org) for org in orgs]


def get_admin_stats(db: Session) -> AdminStats:
    """Get statistics for admin dashboard."""
    total_orgs = db.query(func.count(DBOrganization.id)).scalar()
    active_orgs = db.query(func.count(DBOrganization.id)).filter(
        DBOrganization.subscription_status == 'ACTIVE'
    ).scalar()
    inactive_orgs = total_orgs - active_orgs
    
    total_projects = db.query(func.count(DBProject.id)).scalar()
    
    total_revenue = db.query(func.sum(DBOrgInvoice.amount)).filter(
        DBOrgInvoice.payment_status == 'PAID'
    ).scalar() or 0.0
    
    pending_tickets = db.query(func.count(DBSupportTicket.id)).filter(
        DBSupportTicket.status == 'open'
    ).scalar()
    
    return AdminStats(
        total_orgs=total_orgs or 0,
        active_orgs=active_orgs or 0,
        inactive_orgs=inactive_orgs or 0,
        total_projects=total_projects or 0,
        total_revenue=total_revenue,
        pending_tickets=pending_tickets or 0
    )


def create_support_ticket(db: Session, org_id: str, user_id: str, ticket: SupportTicketCreate) -> SupportTicket:
    """Create a support ticket."""
    ticket_id = str(uuid.uuid4())
    
    db_ticket = DBSupportTicket(
        id=ticket_id,
        org_id=org_id,
        created_by=user_id,
        subject=ticket.subject,
        description=ticket.description,
        status='open',
        priority=ticket.priority,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    create_notification_for_new_ticket(db, org_id, ticket_id, ticket.subject)
    
    return SupportTicket.model_validate(db_ticket)


def get_support_tickets_for_org(db: Session, org_id: str) -> List[SupportTicket]:
    """Get all support tickets for an organization."""
    tickets = db.query(DBSupportTicket).filter(
        DBSupportTicket.org_id == org_id
    ).order_by(desc(DBSupportTicket.created_at)).all()
    
    return [SupportTicket.model_validate(t) for t in tickets]


def get_all_support_tickets(db: Session) -> List[SupportTicket]:
    """Get all support tickets (admin only)."""
    tickets = db.query(DBSupportTicket).order_by(
        desc(DBSupportTicket.created_at)
    ).all()
    
    return [SupportTicket.model_validate(t) for t in tickets]


def update_support_ticket(db: Session, ticket_id: str, updates: SupportTicketUpdate) -> SupportTicket:
    """Update a support ticket."""
    db_ticket = db.query(DBSupportTicket).filter(DBSupportTicket.id == ticket_id).first()
    
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    
    if updates.status:
        db_ticket.status = updates.status
    if updates.priority:
        db_ticket.priority = updates.priority
    
    db_ticket.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_ticket)
    
    return SupportTicket.model_validate(db_ticket)


def create_notification_for_new_ticket(db: Session, org_id: str, ticket_id: str, subject: str):
    """Create a notification for admins when a new ticket is created."""
    from src.models.enums import UserRole
    
    admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
    
    for admin in admins:
        notification = DBAdminNotification(
            id=str(uuid.uuid4()),
            admin_id=admin.id,
            org_id=org_id,
            notification_type='new_ticket',
            title='New Support Ticket',
            message=f'New support ticket created: {subject}',
            is_read=0,
            created_at=datetime.utcnow()
        )
        db.add(notification)
    
    db.commit()


def get_admin_notifications(db: Session, admin_id: str, unread_only: bool = False) -> List[AdminNotification]:
    """Get notifications for an admin."""
    query = db.query(DBAdminNotification).filter(
        DBAdminNotification.admin_id == admin_id
    )
    
    if unread_only:
        query = query.filter(DBAdminNotification.is_read == 0)
    
    notifications = query.order_by(desc(DBAdminNotification.created_at)).all()
    
    return [AdminNotification.model_validate(n) for n in notifications]


def mark_notification_as_read(db: Session, notification_id: str):
    """Mark a notification as read."""
    notification = db.query(DBAdminNotification).filter(
        DBAdminNotification.id == notification_id
    ).first()
    
    if notification:
        notification.is_read = 1
        db.commit()


def mark_all_notifications_as_read(db: Session, admin_id: str):
    """Mark all notifications as read for an admin."""
    db.query(DBAdminNotification).filter(
        DBAdminNotification.admin_id == admin_id
    ).update({DBAdminNotification.is_read: 1})
    
    db.commit()
