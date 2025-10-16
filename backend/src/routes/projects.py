from fastapi import APIRouter, Depends
from typing import List
from src.models import (
    Project, ProjectCreate, User, TeamMember, TeamMemberAdd,
    CalendarEvent, CalendarEventCreate, ProjectDesign, ProjectDesignCreate,
    Invoice, InvoiceCreate
)
from src.services import (
    create_project, get_projects_for_org, get_project_by_id,
    add_team_member_to_project, get_team_members,
    create_calendar_event_for_project, get_calendar_events,
    create_project_design, get_project_designs,
    create_project_invoice, get_project_invoices
)
from src.dependencies import require_org_access, get_current_user

router = APIRouter(prefix="/api/organizations/projects", tags=["projects"])


@router.post("", response_model=Project)
async def create_new_project(project: ProjectCreate, user: User = Depends(require_org_access)):
    """Create a new project."""
    return create_project(user, project)


@router.get("", response_model=List[Project])
async def get_projects(user: User = Depends(require_org_access)):
    """Get all projects for the user's organization."""
    return get_projects_for_org(user)


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str, user: User = Depends(require_org_access)):
    """Get a project by ID."""
    return get_project_by_id(user, project_id)


project_router = APIRouter(prefix="/api/projects", tags=["projects"])


@project_router.post("/{project_id}/team", response_model=TeamMember)
async def add_team_member(project_id: str, member: TeamMemberAdd, user: User = Depends(require_org_access)):
    """Add a team member to a project."""
    return add_team_member_to_project(user, project_id, member)


@project_router.get("/{project_id}/team", response_model=List[TeamMember])
async def get_project_team_members(project_id: str, user: User = Depends(get_current_user)):
    """Get team members for a project."""
    return get_team_members(user, project_id)


@project_router.post("/{project_id}/calendar", response_model=CalendarEvent)
async def create_calendar_event(project_id: str, event: CalendarEventCreate, user: User = Depends(require_org_access)):
    """Create a calendar event for a project."""
    return create_calendar_event_for_project(user, project_id, event)


@project_router.get("/{project_id}/calendar", response_model=List[CalendarEvent])
async def get_project_calendar_events(project_id: str, user: User = Depends(get_current_user)):
    """Get calendar events for a project."""
    return get_calendar_events(user, project_id)


@project_router.post("/{project_id}/designs", response_model=ProjectDesign)
async def create_design(project_id: str, design: ProjectDesignCreate, user: User = Depends(require_org_access)):
    """Create a project design."""
    return create_project_design(user, project_id, design)


@project_router.get("/{project_id}/designs", response_model=List[ProjectDesign])
async def get_designs(project_id: str, user: User = Depends(get_current_user)):
    """Get project designs."""
    return get_project_designs(user, project_id)


@project_router.post("/{project_id}/invoices", response_model=Invoice)
async def create_invoice(project_id: str, invoice: InvoiceCreate, user: User = Depends(require_org_access)):
    """Create an invoice for a project."""
    return create_project_invoice(user, project_id, invoice)


@project_router.get("/{project_id}/invoices", response_model=List[Invoice])
async def get_invoices(project_id: str, user: User = Depends(get_current_user)):
    """Get invoices for a project."""
    return get_project_invoices(user, project_id)
