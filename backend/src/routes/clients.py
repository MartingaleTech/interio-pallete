from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from src.models import Client, ClientCreate, User, Project
from src.services import client_service_new, project_service_new
from src.dependencies.auth_new import require_org_access, get_current_user
from src.config.database import get_db
from src.utils.pagination import paginate_query, create_paginated_response

router = APIRouter(prefix="/api/v1/organizations/clients", tags=["clients"])


@router.post("", response_model=Client)
async def create_new_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Create a new client."""
    return client_service_new.add_client(db, user, client)


@router.get("")
async def get_clients(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Get all clients for the user's organization with pagination."""
    from src.database.models import Client as ClientModel
    query = db.query(ClientModel).filter(ClientModel.org_id == user.org_id)
    items, total = paginate_query(query, page, page_size, sort_by, sort_order)
    return create_paginated_response(items, total, page, page_size)


client_router = APIRouter(prefix="/api/v1/clients", tags=["clients"])


@client_router.get("/projects")
async def get_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all projects for a client with pagination."""
    from src.database.models import Project as ProjectModel
    query = db.query(ProjectModel).filter(ProjectModel.client_id == user.id)
    items, total = paginate_query(query, page, page_size)
    return create_paginated_response(items, total, page, page_size)
