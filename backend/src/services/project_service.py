from datetime import datetime
from typing import List
import uuid
from fastapi import HTTPException
from src.models import (
    Project, ProjectCreate, User, UserRole, ProjectStatus,
    TeamMember, TeamMemberAdd, CalendarEvent, CalendarEventCreate,
    ProjectDesign, ProjectDesignCreate
)
from src.database import (
    get_projects_db, get_clients_db, get_users_db,
    get_team_members_db, get_calendar_events_db, get_project_designs_db
)


def create_project(user: User, project: ProjectCreate) -> Project:
    """Create a new project."""
    projects_db = get_projects_db()
    clients_db = get_clients_db()
    team_members_db = get_team_members_db()
    calendar_events_db = get_calendar_events_db()
    project_designs_db = get_project_designs_db()
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    if project.client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client = clients_db[project.client_id]
    if client.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Client does not belong to your organization")
    
    project_id = str(uuid.uuid4())
    new_project = Project(
        id=project_id,
        org_id=user.org_id,
        name=project.name,
        description=project.description,
        status=ProjectStatus.PLANNING,
        client_id=project.client_id,
        client_name=client.name,
        budget=project.budget,
        start_date=project.start_date,
        end_date=project.end_date,
        created_at=datetime.now().isoformat()
    )
    projects_db[project_id] = new_project
    team_members_db[project_id] = []
    calendar_events_db[project_id] = []
    project_designs_db[project_id] = []
    
    return new_project


def get_projects_for_org(user: User) -> List[Project]:
    """Get all projects for a user's organization."""
    projects_db = get_projects_db()
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    projects = [p for p in projects_db.values() if p.org_id == user.org_id]
    return projects


def get_project_by_id(user: User, project_id: str) -> Project:
    """Get a project by ID."""
    projects_db = get_projects_db()
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return project


def add_team_member_to_project(user: User, project_id: str, member: TeamMemberAdd) -> TeamMember:
    """Add a team member to a project."""
    projects_db = get_projects_db()
    users_db = get_users_db()
    team_members_db = get_team_members_db()
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if member.user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    member_user = users_db[member.user_id]
    
    team_member_id = str(uuid.uuid4())
    new_member = TeamMember(
        id=team_member_id,
        project_id=project_id,
        user_id=member.user_id,
        name=member_user.name,
        role=member.role
    )
    
    if project_id not in team_members_db:
        team_members_db[project_id] = []
    
    team_members_db[project_id].append(new_member)
    
    return new_member


def get_team_members(user: User, project_id: str) -> List[TeamMember]:
    """Get team members for a project."""
    projects_db = get_projects_db()
    clients_db = get_clients_db()
    team_members_db = get_team_members_db()
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    if user.role == UserRole.CLIENT:
        client = None
        for c in clients_db.values():
            if c.email == user.email and c.org_id == project.org_id:
                client = c
                break
        if not client or project.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return team_members_db.get(project_id, [])


def create_calendar_event_for_project(user: User, project_id: str, event: CalendarEventCreate) -> CalendarEvent:
    """Create a calendar event for a project."""
    projects_db = get_projects_db()
    calendar_events_db = get_calendar_events_db()
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    event_id = str(uuid.uuid4())
    new_event = CalendarEvent(
        id=event_id,
        project_id=project_id,
        title=event.title,
        description=event.description,
        event_type=event.event_type,
        start_time=event.start_time,
        end_time=event.end_time,
        attendees=event.attendees,
        created_at=datetime.now().isoformat()
    )
    
    if project_id not in calendar_events_db:
        calendar_events_db[project_id] = []
    
    calendar_events_db[project_id].append(new_event)
    
    return new_event


def get_calendar_events(user: User, project_id: str) -> List[CalendarEvent]:
    """Get calendar events for a project."""
    projects_db = get_projects_db()
    clients_db = get_clients_db()
    calendar_events_db = get_calendar_events_db()
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    if user.role == UserRole.CLIENT:
        client = None
        for c in clients_db.values():
            if c.email == user.email and c.org_id == project.org_id:
                client = c
                break
        if not client or project.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return calendar_events_db.get(project_id, [])


def create_project_design(user: User, project_id: str, design: ProjectDesignCreate) -> ProjectDesign:
    """Create a project design."""
    projects_db = get_projects_db()
    project_designs_db = get_project_designs_db()
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    design_id = str(uuid.uuid4())
    new_design = ProjectDesign(
        id=design_id,
        project_id=project_id,
        title=design.title,
        description=design.description,
        file_url=design.file_url,
        file_type=design.file_type,
        uploaded_by=user.name,
        uploaded_at=datetime.now().isoformat()
    )
    
    if project_id not in project_designs_db:
        project_designs_db[project_id] = []
    
    project_designs_db[project_id].append(new_design)
    
    return new_design


def get_project_designs(user: User, project_id: str) -> List[ProjectDesign]:
    """Get project designs."""
    projects_db = get_projects_db()
    clients_db = get_clients_db()
    project_designs_db = get_project_designs_db()
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    if user.role == UserRole.CLIENT:
        client = None
        for c in clients_db.values():
            if c.email == user.email and c.org_id == project.org_id:
                client = c
                break
        if not client or project.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return project_designs_db.get(project_id, [])


def get_client_projects(user: User) -> List[Project]:
    """Get all projects for a client."""
    clients_db = get_clients_db()
    projects_db = get_projects_db()
    
    if user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Client access required")
    
    client = None
    for c in clients_db.values():
        if c.email == user.email:
            client = c
            break
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    projects = [p for p in projects_db.values() if p.client_id == client.id]
    return projects
