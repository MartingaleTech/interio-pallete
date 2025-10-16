from pydantic import BaseModel
from typing import Optional
from .enums import ProjectStatus


class Project(BaseModel):
    id: str
    org_id: str
    name: str
    description: str
    status: ProjectStatus
    client_id: str
    client_name: str
    budget: float
    start_date: str
    end_date: Optional[str] = None
    created_at: str


class ProjectCreate(BaseModel):
    name: str
    description: str
    client_id: str
    budget: float
    start_date: str
    end_date: Optional[str] = None


class TeamMember(BaseModel):
    id: str
    project_id: str
    user_id: str
    name: str
    role: str


class TeamMemberAdd(BaseModel):
    user_id: str
    role: str
