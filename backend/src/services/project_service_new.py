from datetime import datetime, timezone
from typing import List
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import (
    ProjectCreate, User, UserRole, ProjectStatus,
    TeamMemberAdd, CalendarEventCreate, ProjectDesignCreate
)
from src.repositories import (
    ProjectRepository, ClientRepository, UserRepository,
    TeamMemberRepository, CalendarEventRepository, ProjectDesignRepository
)
from src.repositories.notification_repository import ProjectNotificationRepository
from src.utils.mappers import (
    db_project_to_pydantic, db_team_member_to_pydantic,
    db_calendar_event_to_pydantic, db_project_design_to_pydantic
)


def create_project(db: Session, user: User, project: ProjectCreate):
    """Create a new project."""
    project_repo = ProjectRepository(db)
    client_repo = ClientRepository(db)
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    db_client = client_repo.get_by_id(project.client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if db_client.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Client does not belong to your organization")
    
    project_id = str(uuid.uuid4())
    project_data = {
        "id": project_id,
        "org_id": user.org_id,
        "name": project.name,
        "description": project.description,
        "status": ProjectStatus.PLANNING,
        "client_id": project.client_id,
        "budget": project.budget,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "created_at": datetime.now(timezone.utc)
    }
    db_project = project_repo.create(project_data)
    
    return db_project_to_pydantic(db_project)


def get_projects_for_org(db: Session, user: User) -> List:
    """Get all projects for a user's organization."""
    project_repo = ProjectRepository(db)
    
    if not user.org_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization")
    
    db_projects = project_repo.get_by_org_id(user.org_id)
    return [db_project_to_pydantic(p) for p in db_projects]


def get_project_by_id(db: Session, user: User, project_id: str):
    """Get a project by ID."""
    project_repo = ProjectRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return db_project_to_pydantic(db_project)


def add_team_member_to_project(db: Session, user: User, project_id: str, member: TeamMemberAdd):
    """Add a team member to a project."""
    project_repo = ProjectRepository(db)
    user_repo = UserRepository(db)
    team_repo = TeamMemberRepository(db)
    notification_repo = ProjectNotificationRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db_user = user_repo.get_by_id(member.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    team_member_id = str(uuid.uuid4())
    team_data = {
        "id": team_member_id,
        "project_id": project_id,
        "user_id": member.user_id,
        "name": db_user.name,
        "role": member.role
    }
    db_member = team_repo.create(team_data)
    
    notification_id = str(uuid.uuid4())
    notification_data = {
        "id": notification_id,
        "project_id": project_id,
        "org_id": db_project.org_id,
        "user_id": member.user_id,
        "notification_type": "team_member_added",
        "title": "New Team Member Added",
        "message": f"{db_user.name} has been added to the project as {member.role}",
        "is_read": False,
        "created_at": datetime.now(timezone.utc)
    }
    notification_repo.create(notification_data)
    
    return db_team_member_to_pydantic(db_member)


def get_team_members(db: Session, user: User, project_id: str) -> List:
    """Get team members for a project."""
    project_repo = ProjectRepository(db)
    client_repo = ClientRepository(db)
    team_repo = TeamMemberRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        db_client = client_repo.get_by_email(user.email)
        if not db_client or db_project.client_id != db_client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != db_project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db_members = team_repo.get_by_project_id(project_id)
    return [db_team_member_to_pydantic(m) for m in db_members]


def create_calendar_event_for_project(db: Session, user: User, project_id: str, event: CalendarEventCreate):
    """Create a calendar event for a project."""
    project_repo = ProjectRepository(db)
    calendar_repo = CalendarEventRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    event_id = str(uuid.uuid4())
    event_data = {
        "id": event_id,
        "project_id": project_id,
        "title": event.title,
        "description": event.description,
        "event_type": event.event_type,
        "start_time": event.start_time,
        "end_time": event.end_time,
        "attendees": event.attendees,
        "created_at": datetime.now(timezone.utc)
    }
    db_event = calendar_repo.create(event_data)
    
    return db_calendar_event_to_pydantic(db_event)


def get_calendar_events(db: Session, user: User, project_id: str) -> List:
    """Get calendar events for a project."""
    project_repo = ProjectRepository(db)
    client_repo = ClientRepository(db)
    calendar_repo = CalendarEventRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        db_client = client_repo.get_by_email(user.email)
        if not db_client or db_project.client_id != db_client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != db_project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db_events = calendar_repo.get_by_project_id(project_id)
    return [db_calendar_event_to_pydantic(e) for e in db_events]


def create_project_design(db: Session, user: User, project_id: str, design: ProjectDesignCreate):
    """Create a project design."""
    project_repo = ProjectRepository(db)
    design_repo = ProjectDesignRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    design_id = str(uuid.uuid4())
    design_data = {
        "id": design_id,
        "project_id": project_id,
        "title": design.title,
        "description": design.description,
        "file_url": design.file_url,
        "file_type": design.file_type,
        "uploaded_by_id": user.id,
        "uploaded_at": datetime.now(timezone.utc)
    }
    db_design = design_repo.create(design_data)
    
    return db_project_design_to_pydantic(db_design)


def get_project_designs(db: Session, user: User, project_id: str) -> List:
    """Get project designs."""
    project_repo = ProjectRepository(db)
    client_repo = ClientRepository(db)
    design_repo = ProjectDesignRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        db_client = client_repo.get_by_email(user.email)
        if not db_client or db_project.client_id != db_client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != db_project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db_designs = design_repo.get_by_project_id(project_id)
    return [db_project_design_to_pydantic(d) for d in db_designs]


def get_client_projects(db: Session, user: User) -> List:
    """Get all projects for a client."""
    client_repo = ClientRepository(db)
    project_repo = ProjectRepository(db)
    
    if user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Client access required")
    
    db_client = client_repo.get_by_email(user.email)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_projects = project_repo.get_by_client_id(db_client.id)
    return [db_project_to_pydantic(p) for p in db_projects]
