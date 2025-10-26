from pydantic import BaseModel
from typing import Optional


class ProjectNotification(BaseModel):
    id: str
    project_id: str
    org_id: str
    user_id: Optional[str]
    notification_type: str
    title: str
    message: str
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True


class ProjectNotificationCreate(BaseModel):
    notification_type: str
    title: str
    message: str
    user_id: Optional[str] = None


class ProjectNotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
