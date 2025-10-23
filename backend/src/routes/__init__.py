from .auth import router as auth_router
from .admin import router as admin_router
from .organizations import router as organizations_router
from .projects import router as projects_router, project_router
from .clients import router as clients_router, client_router
from .tickets import (
    project_ticket_router, org_ticket_router, 
    admin_ticket_router, my_tickets_router
)

__all__ = [
    "auth_router",
    "admin_router",
    "organizations_router",
    "projects_router",
    "project_router",
    "clients_router",
    "client_router",
    "project_ticket_router",
    "org_ticket_router",
    "admin_ticket_router",
    "my_tickets_router",
]
