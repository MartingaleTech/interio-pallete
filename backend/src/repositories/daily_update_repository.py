from sqlalchemy.orm import Session
from src.database.models import ProjectDailyUpdate
from typing import List, Optional


class ProjectDailyUpdateRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, update_data: dict) -> ProjectDailyUpdate:
        """Create a new daily update."""
        update = ProjectDailyUpdate(**update_data)
        self.db.add(update)
        self.db.commit()
        self.db.refresh(update)
        return update
    
    def get_by_id(self, update_id: str) -> Optional[ProjectDailyUpdate]:
        """Get a daily update by ID."""
        return self.db.query(ProjectDailyUpdate).filter(
            ProjectDailyUpdate.id == update_id
        ).first()
    
    def get_by_project_id(self, project_id: str) -> List[ProjectDailyUpdate]:
        """Get all daily updates for a project."""
        return self.db.query(ProjectDailyUpdate).filter(
            ProjectDailyUpdate.project_id == project_id
        ).order_by(ProjectDailyUpdate.created_at.desc()).all()
    
    def get_by_user_id(self, user_id: str, project_id: str) -> List[ProjectDailyUpdate]:
        """Get all daily updates by a user in a project."""
        return self.db.query(ProjectDailyUpdate).filter(
            ProjectDailyUpdate.project_id == project_id,
            ProjectDailyUpdate.user_id == user_id
        ).order_by(ProjectDailyUpdate.created_at.desc()).all()
    
    def update(self, update: ProjectDailyUpdate) -> ProjectDailyUpdate:
        """Update a daily update."""
        self.db.commit()
        self.db.refresh(update)
        return update
    
    def delete(self, update: ProjectDailyUpdate) -> None:
        """Delete a daily update."""
        self.db.delete(update)
        self.db.commit()
