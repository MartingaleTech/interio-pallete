from sqlalchemy.orm import Session
from src.database.models import ProjectNotification
from typing import List, Optional


class ProjectNotificationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, notification_data: dict) -> ProjectNotification:
        """Create a new project notification."""
        notification = ProjectNotification(**notification_data)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def get_by_id(self, notification_id: str) -> Optional[ProjectNotification]:
        """Get a notification by ID."""
        return self.db.query(ProjectNotification).filter(
            ProjectNotification.id == notification_id
        ).first()
    
    def get_by_project_id(self, project_id: str) -> List[ProjectNotification]:
        """Get all notifications for a project."""
        return self.db.query(ProjectNotification).filter(
            ProjectNotification.project_id == project_id
        ).order_by(ProjectNotification.created_at.desc()).all()
    
    def get_by_user_id(self, user_id: str, project_id: str) -> List[ProjectNotification]:
        """Get all notifications for a user in a project."""
        return self.db.query(ProjectNotification).filter(
            ProjectNotification.project_id == project_id,
            ProjectNotification.user_id == user_id
        ).order_by(ProjectNotification.created_at.desc()).all()
    
    def get_unread_by_project(self, project_id: str) -> List[ProjectNotification]:
        """Get all unread notifications for a project."""
        return self.db.query(ProjectNotification).filter(
            ProjectNotification.project_id == project_id,
            ProjectNotification.is_read == False
        ).order_by(ProjectNotification.created_at.desc()).all()
    
    def update(self, notification: ProjectNotification) -> ProjectNotification:
        """Update a notification."""
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def delete(self, notification: ProjectNotification) -> None:
        """Delete a notification."""
        self.db.delete(notification)
        self.db.commit()
    
    def mark_as_read(self, notification_id: str) -> Optional[ProjectNotification]:
        """Mark a notification as read."""
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = True
            return self.update(notification)
        return None
    
    def mark_all_as_read(self, project_id: str) -> None:
        """Mark all notifications as read for a project."""
        self.db.query(ProjectNotification).filter(
            ProjectNotification.project_id == project_id
        ).update({"is_read": True})
        self.db.commit()
