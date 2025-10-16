from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from src.models import Client, ClientCreate, User, Project
from src.services import client_service_new, project_service_new
from src.dependencies.auth_new import require_org_access, get_current_user
from src.config.database import get_db

router = APIRouter(prefix="/api/organizations/clients", tags=["clients"])


@router.post("", response_model=Client)
async def create_new_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Create a new client."""
    return client_service_new.add_client(db, user, client)


@router.get("", response_model=List[Client])
async def get_clients(
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Get all clients for the user's organization."""
    return client_service_new.get_clients_for_org(db, user)


client_router = APIRouter(prefix="/api/clients", tags=["clients"])


@client_router.get("/projects", response_model=List[Project])
async def get_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all projects for a client."""
    return project_service_new.get_client_projects(db, user)
