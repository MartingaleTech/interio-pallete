import pytest
from datetime import datetime, timezone
from src.utils.mappers import (
    db_user_to_pydantic, db_organization_to_pydantic,
    db_project_to_pydantic, db_team_member_to_pydantic,
    db_calendar_event_to_pydantic, db_project_design_to_pydantic
)
from src.database import models
import uuid


class TestMappers:
    """Test mapper functions."""
    
    def test_db_user_to_pydantic(self, test_user):
        """Test mapping database user to Pydantic model."""
        user = db_user_to_pydantic(test_user)
        
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.name == test_user.name
    
    def test_db_organization_to_pydantic(self, test_organization):
        """Test mapping database organization to Pydantic model."""
        org = db_organization_to_pydantic(test_organization)
        
        assert org.id == test_organization.id
        assert org.name == test_organization.name
        assert org.email == test_organization.email
    
    def test_db_project_to_pydantic(self, test_project):
        """Test mapping database project to Pydantic model."""
        project = db_project_to_pydantic(test_project)
        
        assert project.id == test_project.id
        assert project.name == test_project.name
        assert project.org_id == test_project.org_id
