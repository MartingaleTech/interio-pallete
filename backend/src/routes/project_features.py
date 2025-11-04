from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from src.models import User
from src.models.notification import ProjectNotification, ProjectNotificationCreate, ProjectNotificationUpdate
from src.models.daily_update import ProjectDailyUpdate, ProjectDailyUpdateCreate, ProjectDailyUpdateUpdate
from src.services import notification_service, daily_update_service
from src.dependencies.auth_new import require_org_access, get_current_user
from src.config.database import get_db
from src.utils.pagination import paginate_query, create_paginated_response

notification_router = APIRouter(prefix="/api/v1/projects", tags=["project-notifications"])


@notification_router.post("/{project_id}/notifications", response_model=ProjectNotification)
async def create_project_notification(
    project_id: str,
    notification: ProjectNotificationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Create a new notification for a project."""
    return notification_service.create_project_notification(db, user, project_id, notification)


@notification_router.get("/{project_id}/notifications")
async def get_project_notifications(
    project_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all notifications for a project with pagination."""
    from src.database.models import ProjectNotification as ProjectNotificationModel
    query = db.query(ProjectNotificationModel).filter(ProjectNotificationModel.project_id == project_id)
    items, total = paginate_query(query, page, page_size)
    return create_paginated_response(items, total, page, page_size)


@notification_router.get("/{project_id}/notifications/unread")
async def get_unread_project_notifications(
    project_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all unread notifications for a project with pagination."""
    from src.database.models import ProjectNotification as ProjectNotificationModel
    query = db.query(ProjectNotificationModel).filter(
        ProjectNotificationModel.project_id == project_id,
        ProjectNotificationModel.is_read == False
    )
    items, total = paginate_query(query, page, page_size)
    return create_paginated_response(items, total, page, page_size)


@notification_router.patch("/{project_id}/notifications/{notification_id}/read", response_model=ProjectNotification)
async def mark_notification_as_read(
    project_id: str,
    notification_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Mark a notification as read."""
    return notification_service.mark_notification_as_read(db, user, notification_id)


@notification_router.post("/{project_id}/notifications/mark-all-read")
async def mark_all_notifications_as_read(
    project_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Mark all notifications as read for a project."""
    return notification_service.mark_all_notifications_as_read(db, user, project_id)


@notification_router.delete("/{project_id}/notifications/{notification_id}")
async def delete_project_notification(
    project_id: str,
    notification_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Delete a project notification."""
    return notification_service.delete_project_notification(db, user, notification_id)


daily_update_router = APIRouter(prefix="/api/v1/projects", tags=["project-daily-updates"])


@daily_update_router.post("/{project_id}/daily-updates", response_model=ProjectDailyUpdate)
async def create_project_daily_update(
    project_id: str,
    update: ProjectDailyUpdateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Create a new daily update for a project."""
    return daily_update_service.create_project_daily_update(db, user, project_id, update)


@daily_update_router.get("/{project_id}/daily-updates")
async def get_project_daily_updates(
    project_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all daily updates for a project with pagination."""
    from src.database.models import ProjectDailyUpdate as ProjectDailyUpdateModel
    query = db.query(ProjectDailyUpdateModel).filter(ProjectDailyUpdateModel.project_id == project_id)
    items, total = paginate_query(query, page, page_size)
    return create_paginated_response(items, total, page, page_size)


@daily_update_router.get("/{project_id}/daily-updates/{update_id}", response_model=ProjectDailyUpdate)
async def get_daily_update(
    project_id: str,
    update_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get a specific daily update."""
    return daily_update_service.get_daily_update_by_id(db, user, update_id)


@daily_update_router.patch("/{project_id}/daily-updates/{update_id}", response_model=ProjectDailyUpdate)
async def update_project_daily_update(
    project_id: str,
    update_id: str,
    update: ProjectDailyUpdateUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Update a daily update."""
    return daily_update_service.update_project_daily_update(db, user, update_id, update)


@daily_update_router.delete("/{project_id}/daily-updates/{update_id}")
async def delete_project_daily_update(
    project_id: str,
    update_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_org_access)
):
    """Delete a daily update."""
    return daily_update_service.delete_project_daily_update(db, user, update_id)
