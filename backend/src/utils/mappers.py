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
