from datetime import datetime
from typing import List
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import User, UserRole
from src.models.notification import ProjectNotificationCreate, ProjectNotificationUpdate
from src.repositories.notification_repository import ProjectNotificationRepository
from src.repositories.project_repository import ProjectRepository, ClientRepository
from src.utils.mappers import db_project_notification_to_pydantic


def create_project_notification(db: Session, user: User, project_id: str, notification: ProjectNotificationCreate):
    """Create a new project notification."""
    notification_repo = ProjectNotificationRepository(db)
    project_repo = ProjectRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_project.org_id != user.org_id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    notification_id = str(uuid.uuid4())
    notification_data = {
        "id": notification_id,
        "project_id": project_id,
        "org_id": db_project.org_id,
        "user_id": notification.user_id,
        "notification_type": notification.notification_type,
        "title": notification.title,
        "message": notification.message,
        "is_read": False,
        "created_at": datetime.utcnow()
    }
    db_notification = notification_repo.create(notification_data)
    
    return db_project_notification_to_pydantic(db_notification)


def get_project_notifications(db: Session, user: User, project_id: str) -> List:
    """Get all notifications for a project."""
    notification_repo = ProjectNotificationRepository(db)
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
    
    db_notifications = notification_repo.get_by_project_id(project_id)
    return [db_project_notification_to_pydantic(n) for n in db_notifications]


def get_unread_project_notifications(db: Session, user: User, project_id: str) -> List:
    """Get all unread notifications for a project."""
    notification_repo = ProjectNotificationRepository(db)
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
    
    db_notifications = notification_repo.get_unread_by_project(project_id)
    return [db_project_notification_to_pydantic(n) for n in db_notifications]


def mark_notification_as_read(db: Session, user: User, notification_id: str):
    """Mark a notification as read."""
    notification_repo = ProjectNotificationRepository(db)
    project_repo = ProjectRepository(db)
    
    db_notification = notification_repo.get_by_id(notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db_project = project_repo.get_by_id(db_notification.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_project.org_id != user.org_id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db_notification = notification_repo.mark_as_read(notification_id)
    return db_project_notification_to_pydantic(db_notification)


def mark_all_notifications_as_read(db: Session, user: User, project_id: str):
    """Mark all notifications as read for a project."""
    notification_repo = ProjectNotificationRepository(db)
    project_repo = ProjectRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_project.org_id != user.org_id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    notification_repo.mark_all_as_read(project_id)
    return {"message": "All notifications marked as read"}


def delete_project_notification(db: Session, user: User, notification_id: str):
    """Delete a project notification."""
    notification_repo = ProjectNotificationRepository(db)
    project_repo = ProjectRepository(db)
    
    db_notification = notification_repo.get_by_id(notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db_project = project_repo.get_by_id(db_notification.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_project.org_id != user.org_id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    notification_repo.delete(db_notification)
    return {"message": "Notification deleted successfully"}
