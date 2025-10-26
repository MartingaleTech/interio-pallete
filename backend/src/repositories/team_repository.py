from sqlalchemy.orm import Session
from typing import List
from src.database import models
import json


class TeamMemberRepository:
    """Repository for TeamMember database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, team_member_data: dict) -> models.TeamMember:
        """Add a team member to a project."""
        db_member = models.TeamMember(**team_member_data)
        self.db.add(db_member)
        self.db.commit()
        self.db.refresh(db_member)
        return db_member
    
    def get_by_project_id(self, project_id: str) -> List[models.TeamMember]:
        """Get all team members for a project."""
        return self.db.query(models.TeamMember).filter(models.TeamMember.project_id == project_id).all()


class CalendarEventRepository:
    """Repository for CalendarEvent database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, event_data: dict) -> models.CalendarEvent:
        """Create a calendar event."""
        if 'attendees' in event_data and isinstance(event_data['attendees'], list):
            event_data['attendees'] = json.dumps(event_data['attendees'])
        
        db_event = models.CalendarEvent(**event_data)
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event
    
    def get_by_project_id(self, project_id: str) -> List[models.CalendarEvent]:
        """Get all calendar events for a project."""
        return self.db.query(models.CalendarEvent).filter(models.CalendarEvent.project_id == project_id).all()


class ProjectDesignRepository:
    """Repository for ProjectDesign database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, design_data: dict) -> models.ProjectDesign:
        """Create a project design."""
        db_design = models.ProjectDesign(**design_data)
        self.db.add(db_design)
        self.db.commit()
        self.db.refresh(db_design)
        return db_design
    
    def get_by_id(self, design_id: str) -> models.ProjectDesign:
        """Get a design by ID."""
        return self.db.query(models.ProjectDesign).filter(
            models.ProjectDesign.id == design_id,
            models.ProjectDesign.is_deleted == False
        ).first()
    
    def get_by_project_id(self, project_id: str, include_deleted: bool = False) -> List[models.ProjectDesign]:
        """Get all designs for a project."""
        query = self.db.query(models.ProjectDesign).filter(
            models.ProjectDesign.project_id == project_id
        )
        if not include_deleted:
            query = query.filter(models.ProjectDesign.is_deleted == False)
        return query.order_by(models.ProjectDesign.uploaded_at.desc()).all()
    
    def get_latest_versions(self, project_id: str) -> List[models.ProjectDesign]:
        """Get only the latest versions of designs for a project."""
        return self.db.query(models.ProjectDesign).filter(
            models.ProjectDesign.project_id == project_id,
            models.ProjectDesign.is_latest_version == True,
            models.ProjectDesign.is_deleted == False
        ).order_by(models.ProjectDesign.uploaded_at.desc()).all()
    
    def get_versions(self, file_id: str) -> List[models.ProjectDesign]:
        """Get all versions of a file."""
        design = self.get_by_id(file_id)
        if not design:
            return []
        
        root_id = design.parent_id if design.parent_id else design.id
        
        return self.db.query(models.ProjectDesign).filter(
            (models.ProjectDesign.id == root_id) | (models.ProjectDesign.parent_id == root_id)
        ).order_by(models.ProjectDesign.version.desc()).all()
    
    def update(self, design_id: str, update_data: dict) -> models.ProjectDesign:
        """Update a design."""
        design = self.get_by_id(design_id)
        if design:
            for key, value in update_data.items():
                if value is not None:
                    setattr(design, key, value)
            self.db.commit()
            self.db.refresh(design)
        return design
    
    def soft_delete(self, design_id: str) -> bool:
        """Soft delete a design."""
        design = self.get_by_id(design_id)
        if design:
            design.is_deleted = True
            self.db.commit()
            return True
        return False
    
    def increment_download_count(self, design_id: str) -> bool:
        """Increment download count for a design."""
        design = self.get_by_id(design_id)
        if design:
            design.download_count += 1
            self.db.commit()
            return True
        return False
