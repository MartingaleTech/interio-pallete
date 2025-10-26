from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FileUploadResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    file_name: str
    file_url: str
    file_type: str
    file_size: int
    uploaded_by: str
    uploaded_at: str
    version: int
    is_latest_version: bool
    thumbnail_url: Optional[str] = None
    is_public: bool
    download_count: int


class FileMetadata(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    file_name: str
    file_url: str
    file_type: str
    file_size: int
    uploaded_by: str
    uploaded_by_id: str
    uploaded_at: str
    version: int
    parent_id: Optional[str] = None
    is_latest_version: bool
    thumbnail_url: Optional[str] = None
    is_public: bool
    download_count: int
    is_deleted: bool


class FileCommentCreate(BaseModel):
    comment: str
    parent_comment_id: Optional[str] = None


class FileCommentUpdate(BaseModel):
    comment: str


class FileCommentResponse(BaseModel):
    id: str
    file_id: str
    project_id: str
    org_id: str
    user_id: str
    user_name: str
    comment: str
    parent_comment_id: Optional[str] = None
    mentions: Optional[List[str]] = None
    is_resolved: bool
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None
    created_at: str
    updated_at: str
    replies: Optional[List['FileCommentResponse']] = []


class FileCommentResolveRequest(BaseModel):
    is_resolved: bool


class FilePermissionCreate(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None
    can_view: bool = True
    can_download: bool = True
    can_comment: bool = True
    can_delete: bool = False


class FilePermissionResponse(BaseModel):
    id: str
    file_id: str
    user_id: Optional[str] = None
    role: Optional[str] = None
    can_view: bool
    can_download: bool
    can_comment: bool
    can_delete: bool
    created_at: str


class FileAuditLogResponse(BaseModel):
    id: str
    file_id: str
    user_id: str
    user_name: str
    action: str
    action_metadata: Optional[str] = None
    created_at: str


class FileVersionResponse(BaseModel):
    id: str
    version: int
    file_name: str
    file_size: int
    uploaded_by: str
    uploaded_at: str
    is_latest_version: bool


class FileListResponse(BaseModel):
    files: List[FileMetadata]
    total: int


class FileDownloadResponse(BaseModel):
    file_url: str
    file_name: str
    file_type: str


FileCommentResponse.model_rebuild()
