from fastapi import APIRouter, Depends
from typing import List
from src.models import Client, ClientCreate, User, Project
from src.services import create_client, get_clients_for_org, get_client_projects
from src.dependencies import require_org_access, get_current_user

router = APIRouter(prefix="/api/organizations/clients", tags=["clients"])


@router.post("", response_model=Client)
async def create_new_client(client: ClientCreate, user: User = Depends(require_org_access)):
    """Create a new client."""
    return create_client(user, client)


@router.get("", response_model=List[Client])
async def get_clients(user: User = Depends(require_org_access)):
    """Get all clients for the user's organization."""
    return get_clients_for_org(user)


client_router = APIRouter(prefix="/api/clients", tags=["clients"])


@client_router.get("/projects", response_model=List[Project])
async def get_projects(user: User = Depends(get_current_user)):
    """Get all projects for a client."""
    return get_client_projects(user)
