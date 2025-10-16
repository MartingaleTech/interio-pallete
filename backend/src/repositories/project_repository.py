from sqlalchemy.orm import Session
from typing import Optional, List
from src.database import models


class ProjectRepository:
    """Repository for Project database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, project_data: dict) -> models.Project:
        """Create a new project."""
        db_project = models.Project(**project_data)
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project
    
    def get_by_id(self, project_id: str) -> Optional[models.Project]:
        """Get project by ID."""
        return self.db.query(models.Project).filter(models.Project.id == project_id).first()
    
    def get_by_org_id(self, org_id: str) -> List[models.Project]:
        """Get all projects for an organization."""
        return self.db.query(models.Project).filter(models.Project.org_id == org_id).all()
    
    def get_by_client_id(self, client_id: str) -> List[models.Project]:
        """Get all projects for a client."""
        return self.db.query(models.Project).filter(models.Project.client_id == client_id).all()
    
    def delete(self, project_id: str) -> bool:
        """Delete project."""
        project = self.get_by_id(project_id)
        if project:
            self.db.delete(project)
            self.db.commit()
            return True
        return False


class ClientRepository:
    """Repository for Client database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, client_data: dict) -> models.Client:
        """Create a new client."""
        db_client = models.Client(**client_data)
        self.db.add(db_client)
        self.db.commit()
        self.db.refresh(db_client)
        return db_client
    
    def get_by_id(self, client_id: str) -> Optional[models.Client]:
        """Get client by ID."""
        return self.db.query(models.Client).filter(models.Client.id == client_id).first()
    
    def get_by_org_id(self, org_id: str) -> List[models.Client]:
        """Get all clients for an organization."""
        return self.db.query(models.Client).filter(models.Client.org_id == org_id).all()
    
    def get_by_email(self, email: str) -> Optional[models.Client]:
        """Get client by email."""
        return self.db.query(models.Client).filter(models.Client.email == email).first()
