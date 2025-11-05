from datetime import datetime
from typing import List
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import User, UserRole
from src.models.daily_update import ProjectDailyUpdateCreate, ProjectDailyUpdateUpdate
from src.repositories.daily_update_repository import ProjectDailyUpdateRepository
from src.repositories.project_repository import ProjectRepository, ClientRepository
from src.utils.mappers import db_project_daily_update_to_pydantic


def create_project_daily_update(db: Session, user: User, project_id: str, update: ProjectDailyUpdateCreate):
    """Create a new daily update for a project."""
    update_repo = ProjectDailyUpdateRepository(db)
    project_repo = ProjectRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_id = str(uuid.uuid4())
    update_data = {
        "id": update_id,
        "project_id": project_id,
        "org_id": db_project.org_id,
        "user_id": user.id,
        "user_name": user.name,
        "update_text": update.update_text,
        "attachments": update.attachments,
        "created_at": datetime.now(datetime.UTC),
        "updated_at": datetime.now(datetime.UTC)
    }
    db_update = update_repo.create(update_data)
    
    return db_project_daily_update_to_pydantic(db_update)


def get_project_daily_updates(db: Session, user: User, project_id: str) -> List:
    """Get all daily updates for a project."""
    update_repo = ProjectDailyUpdateRepository(db)
    project_repo = ProjectRepository(db)
    client_repo = ClientRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        db_client = client_repo.get_by_email(user.email)
        if not db_client or db_project.client_id != db_client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif db_project.org_id != user.org_id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db_updates = update_repo.get_by_project_id(project_id)
    return [db_project_daily_update_to_pydantic(u) for u in db_updates]


def get_daily_update_by_id(db: Session, user: User, update_id: str):
    """Get a daily update by ID."""
    update_repo = ProjectDailyUpdateRepository(db)
    project_repo = ProjectRepository(db)
    
    db_update = update_repo.get_by_id(update_id)
    if not db_update:
        raise HTTPException(status_code=404, detail="Daily update not found")
    
    db_project = project_repo.get_by_id(db_update.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_project.org_id != user.org_id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return db_project_daily_update_to_pydantic(db_update)


def update_project_daily_update(db: Session, user: User, update_id: str, update_data: ProjectDailyUpdateUpdate):
    """Update a daily update."""
    update_repo = ProjectDailyUpdateRepository(db)
    project_repo = ProjectRepository(db)
    
    db_update = update_repo.get_by_id(update_id)
    if not db_update:
        raise HTTPException(status_code=404, detail="Daily update not found")
    
    db_project = project_repo.get_by_id(db_update.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_update.user_id != user.id and user.role not in [UserRole.ORG_OWNER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="You can only edit your own updates")
    
    if update_data.update_text is not None:
        db_update.update_text = update_data.update_text
    if update_data.attachments is not None:
        db_update.attachments = update_data.attachments
    
    db_update.updated_at = datetime.now(datetime.UTC)
    db_update = update_repo.update(db_update)
    
    return db_project_daily_update_to_pydantic(db_update)


def delete_project_daily_update(db: Session, user: User, update_id: str):
    """Delete a daily update."""
    update_repo = ProjectDailyUpdateRepository(db)
    project_repo = ProjectRepository(db)
    
    db_update = update_repo.get_by_id(update_id)
    if not db_update:
        raise HTTPException(status_code=404, detail="Daily update not found")
    
    db_project = project_repo.get_by_id(db_update.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_update.user_id != user.id and user.role not in [UserRole.ORG_OWNER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="You can only delete your own updates")
    
    update_repo.delete(db_update)
    return {"message": "Daily update deleted successfully"}
