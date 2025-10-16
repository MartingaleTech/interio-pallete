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
    
    def get_by_project_id(self, project_id: str) -> List[models.ProjectDesign]:
        """Get all designs for a project."""
        return self.db.query(models.ProjectDesign).filter(models.ProjectDesign.project_id == project_id).all()
