from typing import List
import json
from src.database import models as db_models
from src import models as pydantic_models


def db_user_to_pydantic(db_user: db_models.User) -> pydantic_models.User:
    """Convert database User to Pydantic User."""
    return pydantic_models.User(
        id=db_user.id,
        email=db_user.email,
        name=db_user.name,
        role=db_user.role,
        org_id=db_user.org_id,
        created_at=db_user.created_at.isoformat() if db_user.created_at else None,
        phone=db_user.phone,
        first_name=db_user.first_name,
        last_name=db_user.last_name
    )


def db_organization_to_pydantic(db_org: db_models.Organization) -> pydantic_models.Organization:
    """Convert database Organization to Pydantic Organization."""
    return pydantic_models.Organization(
        id=db_org.id,
        name=db_org.name,
        email=db_org.email,
        phone=db_org.phone,
        address=db_org.address,
        city=db_org.city,
        state=db_org.state,
        pincode=db_org.pincode,
        owner_id=db_org.owner_id,
        subscription_status=db_org.subscription_status,
        subscription_plan=db_org.subscription_plan,
        subscription_start=db_org.subscription_start.isoformat() if db_org.subscription_start else None,
        subscription_end=db_org.subscription_end.isoformat() if db_org.subscription_end else None,
        created_at=db_org.created_at.isoformat() if db_org.created_at else None
    )


def db_project_to_pydantic(db_project: db_models.Project) -> pydantic_models.Project:
    """Convert database Project to Pydantic Project."""
    return pydantic_models.Project(
        id=db_project.id,
        org_id=db_project.org_id,
        name=db_project.name,
        description=db_project.description,
        status=db_project.status,
        client_id=db_project.client_id,
        client_name=db_project.client_name,
        budget=db_project.budget,
        start_date=db_project.start_date,
        end_date=db_project.end_date,
        created_at=db_project.created_at.isoformat() if db_project.created_at else None
    )


def db_client_to_pydantic(db_client: db_models.Client) -> pydantic_models.Client:
    """Convert database Client to Pydantic Client."""
    return pydantic_models.Client(
        id=db_client.id,
        org_id=db_client.org_id,
        name=db_client.name,
        email=db_client.email,
        phone=db_client.phone,
        address=db_client.address,
        created_at=db_client.created_at.isoformat() if db_client.created_at else None
    )


def db_team_member_to_pydantic(db_member: db_models.TeamMember) -> pydantic_models.TeamMember:
    """Convert database TeamMember to Pydantic TeamMember."""
    return pydantic_models.TeamMember(
        id=db_member.id,
        project_id=db_member.project_id,
        user_id=db_member.user_id,
        name=db_member.name,
        role=db_member.role
    )


def db_calendar_event_to_pydantic(db_event: db_models.CalendarEvent) -> pydantic_models.CalendarEvent:
    """Convert database CalendarEvent to Pydantic CalendarEvent."""
    attendees = json.loads(db_event.attendees) if isinstance(db_event.attendees, str) else db_event.attendees
    
    return pydantic_models.CalendarEvent(
        id=db_event.id,
        project_id=db_event.project_id,
        title=db_event.title,
        description=db_event.description,
        event_type=db_event.event_type,
        start_time=db_event.start_time,
        end_time=db_event.end_time,
        attendees=attendees,
        created_at=db_event.created_at.isoformat() if db_event.created_at else None
    )


def db_project_design_to_pydantic(db_design: db_models.ProjectDesign) -> pydantic_models.ProjectDesign:
    """Convert database ProjectDesign to Pydantic ProjectDesign."""
    return pydantic_models.ProjectDesign(
        id=db_design.id,
        project_id=db_design.project_id,
        title=db_design.title,
        description=db_design.description,
        file_url=db_design.file_url,
        file_type=db_design.file_type,
        uploaded_by=db_design.uploaded_by,
        uploaded_at=db_design.uploaded_at.isoformat() if db_design.uploaded_at else None
    )


def db_invoice_to_pydantic(db_invoice: db_models.Invoice) -> pydantic_models.Invoice:
    """Convert database Invoice to Pydantic Invoice."""
    return pydantic_models.Invoice(
        id=db_invoice.id,
        project_id=db_invoice.project_id,
        org_id=db_invoice.org_id,
        invoice_number=db_invoice.invoice_number,
        amount=db_invoice.amount,
        tax=db_invoice.tax,
        total=db_invoice.total,
        payment_status=db_invoice.payment_status,
        due_date=db_invoice.due_date,
        paid_date=db_invoice.paid_date,
        created_at=db_invoice.created_at.isoformat() if db_invoice.created_at else None
    )


def db_org_invoice_to_pydantic(db_invoice: db_models.OrgInvoice) -> pydantic_models.OrgInvoice:
    """Convert database OrgInvoice to Pydantic OrgInvoice."""
    return pydantic_models.OrgInvoice(
        id=db_invoice.id,
        org_id=db_invoice.org_id,
        invoice_number=db_invoice.invoice_number,
        subscription_plan=db_invoice.subscription_plan,
        amount=db_invoice.amount,
        payment_status=db_invoice.payment_status,
        billing_period_start=db_invoice.billing_period_start,
        billing_period_end=db_invoice.billing_period_end,
        due_date=db_invoice.due_date,
        paid_date=db_invoice.paid_date,
        created_at=db_invoice.created_at.isoformat() if db_invoice.created_at else None
    )


def db_project_ticket_to_pydantic(db_ticket: db_models.ProjectTicket) -> pydantic_models.ProjectTicket:
    """Convert database ProjectTicket to Pydantic ProjectTicket."""
    return pydantic_models.ProjectTicket(
        id=db_ticket.id,
        project_id=db_ticket.project_id,
        org_id=db_ticket.org_id,
        created_by=db_ticket.created_by,
        assigned_to=db_ticket.assigned_to,
        title=db_ticket.title,
        description=db_ticket.description,
        ticket_type=db_ticket.ticket_type,
        status=db_ticket.status,
        priority=db_ticket.priority,
        created_at=db_ticket.created_at.isoformat() if db_ticket.created_at else None,
        updated_at=db_ticket.updated_at.isoformat() if db_ticket.updated_at else None,
        resolved_at=db_ticket.resolved_at.isoformat() if db_ticket.resolved_at else None,
        creator_name=db_ticket.creator.name if db_ticket.creator else None,
        assignee_name=db_ticket.assignee.name if db_ticket.assignee else None
    )


def db_org_ticket_to_pydantic(db_ticket: db_models.OrgTicket) -> pydantic_models.OrgTicket:
    """Convert database OrgTicket to Pydantic OrgTicket."""
    return pydantic_models.OrgTicket(
        id=db_ticket.id,
        org_id=db_ticket.org_id,
        created_by=db_ticket.created_by,
        assigned_to=db_ticket.assigned_to,
        title=db_ticket.title,
        description=db_ticket.description,
        ticket_type=db_ticket.ticket_type,
        status=db_ticket.status,
        priority=db_ticket.priority,
        created_at=db_ticket.created_at.isoformat() if db_ticket.created_at else None,
        updated_at=db_ticket.updated_at.isoformat() if db_ticket.updated_at else None,
        resolved_at=db_ticket.resolved_at.isoformat() if db_ticket.resolved_at else None,
        creator_name=db_ticket.creator.name if db_ticket.creator else None,
        assignee_name=db_ticket.assignee.name if db_ticket.assignee else None,
        org_name=db_ticket.organization.name if db_ticket.organization else None
    )


def db_ticket_comment_to_pydantic(db_comment: db_models.TicketComment) -> pydantic_models.TicketComment:
    """Convert database TicketComment to Pydantic TicketComment."""
    return pydantic_models.TicketComment(
        id=db_comment.id,
        project_ticket_id=db_comment.project_ticket_id,
        org_ticket_id=db_comment.org_ticket_id,
        user_id=db_comment.user_id,
        comment=db_comment.comment,
        is_internal=db_comment.is_internal,
        created_at=db_comment.created_at.isoformat() if db_comment.created_at else None,
        updated_at=db_comment.updated_at.isoformat() if db_comment.updated_at else None,
        user_name=db_comment.user.name if db_comment.user else None
    )


def db_ticket_attachment_to_pydantic(db_attachment: db_models.TicketAttachment) -> pydantic_models.TicketAttachment:
    """Convert database TicketAttachment to Pydantic TicketAttachment."""
    return pydantic_models.TicketAttachment(
        id=db_attachment.id,
        project_ticket_id=db_attachment.project_ticket_id,
        org_ticket_id=db_attachment.org_ticket_id,
        uploaded_by=db_attachment.uploaded_by,
        file_name=db_attachment.file_name,
        file_url=db_attachment.file_url,
        file_type=db_attachment.file_type,
        file_size=db_attachment.file_size,
        created_at=db_attachment.created_at.isoformat() if db_attachment.created_at else None,
        uploader_name=db_attachment.uploader.name if db_attachment.uploader else None
    )


def db_project_notification_to_pydantic(db_notification: db_models.ProjectNotification):
    """Convert database ProjectNotification to Pydantic ProjectNotification."""
    from src.models.notification import ProjectNotification
    return ProjectNotification(
        id=db_notification.id,
        project_id=db_notification.project_id,
        org_id=db_notification.org_id,
        user_id=db_notification.user_id,
        notification_type=db_notification.notification_type,
        title=db_notification.title,
        message=db_notification.message,
        is_read=db_notification.is_read,
        created_at=db_notification.created_at.isoformat() if db_notification.created_at else None
    )


def db_project_daily_update_to_pydantic(db_update: db_models.ProjectDailyUpdate):
    """Convert database ProjectDailyUpdate to Pydantic ProjectDailyUpdate."""
    from src.models.daily_update import ProjectDailyUpdate
    return ProjectDailyUpdate(
        id=db_update.id,
        project_id=db_update.project_id,
        org_id=db_update.org_id,
        user_id=db_update.user_id,
        user_name=db_update.user_name,
        update_text=db_update.update_text,
        attachments=db_update.attachments,
        created_at=db_update.created_at.isoformat() if db_update.created_at else None,
        updated_at=db_update.updated_at.isoformat() if db_update.updated_at else None
    )
