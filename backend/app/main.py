from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import (
    auth_router, admin_router, organizations_router,
    projects_router, project_router, clients_router, client_router,
    project_ticket_router, org_ticket_router, admin_ticket_router, my_tickets_router
)
from src.routes.project_features import notification_router, daily_update_router
from src.routes.file_management import router as file_management_router
from src.core import initialize_admin_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Range", "Content-Disposition"],
)

initialize_admin_user()

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(organizations_router)
app.include_router(projects_router)
app.include_router(project_router)
app.include_router(clients_router)
app.include_router(client_router)
app.include_router(project_ticket_router)
app.include_router(org_ticket_router)
app.include_router(admin_ticket_router)
app.include_router(my_tickets_router)
app.include_router(notification_router)
app.include_router(daily_update_router)
app.include_router(file_management_router)


@app.get("/healthz")
async def healthz():
    """Health check endpoint."""
    return {"status": "ok"}
