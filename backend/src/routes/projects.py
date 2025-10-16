from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from src.models import (
    Project, ProjectCreate, User, TeamMember, TeamMemberAdd,
    CalendarEvent, CalendarEventCreate, ProjectDesign, ProjectDesignCreate,
    Invoice, InvoiceCreate
)
from src.services import project_service_new, invoice_service_new
from src.dependencies.auth_new import require_org_access, get_current_user
from src.config.database import get_db

router = APIRouter(prefix="/api/organizations/projects", tags=["projects"])


@router.post("", response_model=Project)
async def create_new_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Create a new project."""
    return project_service_new.create_project(db, user, project)


@router.get("", response_model=List[Project])
async def get_projects(
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Get all projects for the user's organization."""
    return project_service_new.get_projects_for_org(db, user)


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Get a project by ID."""
    return project_service_new.get_project_by_id(db, user, project_id)


project_router = APIRouter(prefix="/api/projects", tags=["projects"])


@project_router.post("/{project_id}/team", response_model=TeamMember)
async def add_team_member(
    project_id: str,
    member: TeamMemberAdd,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Add a team member to a project."""
    return project_service_new.add_team_member_to_project(db, user, project_id, member)


@project_router.get("/{project_id}/team", response_model=List[TeamMember])
async def get_project_team_members(
    project_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get team members for a project."""
    return project_service_new.get_team_members(db, user, project_id)


@project_router.post("/{project_id}/calendar", response_model=CalendarEvent)
async def create_calendar_event(
    project_id: str,
    event: CalendarEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Create a calendar event for a project."""
    return project_service_new.create_calendar_event_for_project(db, user, project_id, event)


@project_router.get("/{project_id}/calendar", response_model=List[CalendarEvent])
async def get_project_calendar_events(
    project_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get calendar events for a project."""
    return project_service_new.get_calendar_events(db, user, project_id)


@project_router.post("/{project_id}/designs", response_model=ProjectDesign)
async def create_design(
    project_id: str,
    design: ProjectDesignCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Create a project design."""
    return project_service_new.create_project_design(db, user, project_id, design)


@project_router.get("/{project_id}/designs", response_model=List[ProjectDesign])
async def get_designs(
    project_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get project designs."""
    return project_service_new.get_project_designs(db, user, project_id)


@project_router.post("/{project_id}/invoices", response_model=Invoice)
async def create_invoice(
    project_id: str,
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Create an invoice for a project."""
    return invoice_service_new.create_project_invoice(db, user, project_id, invoice)


@project_router.get("/{project_id}/invoices", response_model=List[Invoice])
async def get_invoices(
    project_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get invoices for a project."""
    return invoice_service_new.get_project_invoices(db, user, project_id)
