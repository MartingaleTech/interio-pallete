from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.routes import (
    auth_router, admin_router, organizations_router,
    projects_router, project_router, clients_router, client_router,
    project_ticket_router, org_ticket_router, admin_ticket_router, my_tickets_router
)
from src.routes.project_features import notification_router, daily_update_router
from src.routes.file_management import router as file_management_router
from src.routes.chat import router as chat_router
from src.core import initialize_admin_user
from src.config.storage import storage_config
from src.middleware import (
    RequestIDMiddleware,
    RateLimitMiddleware,
    api_error_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from src.utils.errors import APIError
import os

app = FastAPI(
    title="Interio Palette API",
    description="Multi-tenant SaaS platform for interior designers and homeowners",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Range", "Content-Disposition", "X-Request-ID"],
)

app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

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
app.include_router(chat_router)

if storage_config.USE_LOCAL_STORAGE:
    os.makedirs(storage_config.LOCAL_STORAGE_PATH, exist_ok=True)
    app.mount("/files", StaticFiles(directory=storage_config.LOCAL_STORAGE_PATH), name="files")


@app.get("/healthz")
async def healthz():
    """Health check endpoint."""
    return {"status": "ok"}
