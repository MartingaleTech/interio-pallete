from sqlalchemy.orm import Session
from typing import Optional, List
from src.database import models


class OrganizationRepository:
    """Repository for Organization database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, org_data: dict) -> models.Organization:
        """Create a new organization."""
        db_org = models.Organization(**org_data)
        self.db.add(db_org)
        self.db.commit()
        self.db.refresh(db_org)
        return db_org
    
    def get_by_id(self, org_id: str) -> Optional[models.Organization]:
        """Get organization by ID."""
        return self.db.query(models.Organization).filter(models.Organization.id == org_id).first()
    
    def get_all(self) -> List[models.Organization]:
        """Get all organizations."""
        return self.db.query(models.Organization).all()
    
    def update(self, org_id: str, **kwargs) -> Optional[models.Organization]:
        """Update organization."""
        org = self.get_by_id(org_id)
        if org:
            for key, value in kwargs.items():
                setattr(org, key, value)
            self.db.commit()
            self.db.refresh(org)
        return org
    
    def delete(self, org_id: str) -> bool:
        """Delete organization."""
        org = self.get_by_id(org_id)
        if org:
            self.db.delete(org)
            self.db.commit()
            return True
        return False
