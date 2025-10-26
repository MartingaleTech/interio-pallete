from pydantic import BaseModel
from typing import Optional


class ProjectDailyUpdate(BaseModel):
    id: str
    project_id: str
    org_id: str
    user_id: str
    user_name: str
    update_text: str
    attachments: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ProjectDailyUpdateCreate(BaseModel):
    update_text: str
    attachments: Optional[str] = None


class ProjectDailyUpdateUpdate(BaseModel):
    update_text: Optional[str] = None
    attachments: Optional[str] = None
