from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src.config.database import get_db
from src.dependencies.auth_new import get_current_user, require_org_access
from src.database.models import User
from src.services.file_management_service import FileManagementService
from src.services.file_comment_service import FileCommentService
from src.models.file_management import (
    FileUploadResponse,
    FileMetadata,
    FileCommentCreate,
    FileCommentUpdate,
    FileCommentResponse,
    FileCommentResolveRequest,
    FilePermissionCreate,
    FilePermissionResponse,
    FileAuditLogResponse,
    FileVersionResponse,
    FileListResponse,
    FileDownloadResponse
)

router = APIRouter()


@router.post("/api/projects/{project_id}/files/upload", response_model=FileUploadResponse)
async def upload_file(
    project_id: str,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    is_public: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_access)
):
    """
    Upload a new file to a project.
    
    Supports:
    - Images (JPEG, PNG, etc.)
    - PDFs
    - 3D models (.obj, .fbx, .skp, .stl, .gltf, .glb)
    - Drag-and-drop and multi-file upload
    """
    service = FileManagementService(db)
    
    design = await service.upload_file(
        file=file,
        project_id=project_id,
        title=title,
        description=description,
        user_id=current_user.id,
        user_name=current_user.name,
        org_id=current_user.org_id,
        is_public=is_public
    )
    
    return FileUploadResponse(
        id=design.id,
        project_id=design.project_id,
        title=design.title,
        description=design.description,
        file_name=design.file_name,
        file_url=design.file_url,
        file_type=design.file_type,
        file_size=design.file_size,
        uploaded_by=design.uploaded_by,
        uploaded_at=design.uploaded_at.isoformat(),
        version=design.version,
        is_latest_version=design.is_latest_version,
        thumbnail_url=design.thumbnail_url,
        is_public=design.is_public,
        download_count=design.download_count
    )


@router.post("/api/files/{file_id}/versions/upload", response_model=FileUploadResponse)
async def upload_new_version(
    file_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_access)
):
    """Upload a new version of an existing file."""
    service = FileManagementService(db)
    
    design = await service.upload_new_version(
        file=file,
        parent_file_id=file_id,
        user_id=current_user.id,
        user_name=current_user.name,
        org_id=current_user.org_id
    )
    
    return FileUploadResponse(
        id=design.id,
        project_id=design.project_id,
        title=design.title,
        description=design.description,
        file_name=design.file_name,
        file_url=design.file_url,
        file_type=design.file_type,
        file_size=design.file_size,
        uploaded_by=design.uploaded_by,
        uploaded_at=design.uploaded_at.isoformat(),
        version=design.version,
        is_latest_version=design.is_latest_version,
        thumbnail_url=design.thumbnail_url,
        is_public=design.is_public,
        download_count=design.download_count
    )


@router.get("/api/files/{file_id}/download", response_model=FileDownloadResponse)
async def download_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get download URL for a file.
    
    Includes audit logging for compliance.
    """
    service = FileManagementService(db)
    
    file_url, file_name, file_type = await service.download_file(
        file_id=file_id,
        user_id=current_user.id,
        user_name=current_user.name
    )
    
    return FileDownloadResponse(
        file_url=file_url,
        file_name=file_name,
        file_type=file_type
    )


@router.delete("/api/files/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_access)
):
    """Soft delete a file."""
    service = FileManagementService(db)
    
    success = await service.delete_file(
        file_id=file_id,
        user_id=current_user.id,
        user_name=current_user.name
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"message": "File deleted successfully"}


@router.get("/api/files/{file_id}", response_model=FileMetadata)
async def get_file_metadata(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get file metadata by ID."""
    service = FileManagementService(db)
    
    design = service.get_file_metadata(file_id)
    if not design:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileMetadata(
        id=design.id,
        project_id=design.project_id,
        title=design.title,
        description=design.description,
        file_name=design.file_name,
        file_url=design.file_url,
        file_type=design.file_type,
        file_size=design.file_size,
        uploaded_by=design.uploaded_by,
        uploaded_by_id=design.uploaded_by_id,
        uploaded_at=design.uploaded_at.isoformat(),
        version=design.version,
        parent_id=design.parent_id,
        is_latest_version=design.is_latest_version,
        thumbnail_url=design.thumbnail_url,
        is_public=design.is_public,
        download_count=design.download_count,
        is_deleted=design.is_deleted
    )


@router.get("/api/projects/{project_id}/files", response_model=FileListResponse)
async def list_project_files(
    project_id: str,
    latest_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all files for a project.
    
    Query params:
    - latest_only: If true, only return latest versions (default: true)
    """
    service = FileManagementService(db)
    
    designs = service.list_files(project_id, latest_only)
    
    files = [
        FileMetadata(
            id=d.id,
            project_id=d.project_id,
            title=d.title,
            description=d.description,
            file_name=d.file_name,
            file_url=d.file_url,
            file_type=d.file_type,
            file_size=d.file_size,
            uploaded_by=d.uploaded_by,
            uploaded_by_id=d.uploaded_by_id,
            uploaded_at=d.uploaded_at.isoformat(),
            version=d.version,
            parent_id=d.parent_id,
            is_latest_version=d.is_latest_version,
            thumbnail_url=d.thumbnail_url,
            is_public=d.is_public,
            download_count=d.download_count,
            is_deleted=d.is_deleted
        )
        for d in designs
    ]
    
    return FileListResponse(files=files, total=len(files))


@router.get("/api/files/{file_id}/versions", response_model=List[FileVersionResponse])
async def get_file_versions(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all versions of a file."""
    service = FileManagementService(db)
    
    versions = service.get_file_versions(file_id)
    
    return [
        FileVersionResponse(
            id=v.id,
            version=v.version,
            file_name=v.file_name,
            file_size=v.file_size,
            uploaded_by=v.uploaded_by,
            uploaded_at=v.uploaded_at.isoformat(),
            is_latest_version=v.is_latest_version
        )
        for v in versions
    ]


@router.post("/api/files/versions/{version_id}/restore", response_model=FileUploadResponse)
async def restore_file_version(
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_access)
):
    """Restore a previous version as the latest version."""
    service = FileManagementService(db)
    
    design = await service.restore_version(
        version_id=version_id,
        user_id=current_user.id,
        user_name=current_user.name,
        org_id=current_user.org_id
    )
    
    return FileUploadResponse(
        id=design.id,
        project_id=design.project_id,
        title=design.title,
        description=design.description,
        file_name=design.file_name,
        file_url=design.file_url,
        file_type=design.file_type,
        file_size=design.file_size,
        uploaded_by=design.uploaded_by,
        uploaded_at=design.uploaded_at.isoformat(),
        version=design.version,
        is_latest_version=design.is_latest_version,
        thumbnail_url=design.thumbnail_url,
        is_public=design.is_public,
        download_count=design.download_count
    )


@router.get("/api/files/{file_id}/audit-logs", response_model=List[FileAuditLogResponse])
async def get_file_audit_logs(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_access)
):
    """Get audit logs for a file."""
    service = FileManagementService(db)
    
    logs = service.get_file_audit_logs(file_id)
    
    return [
        FileAuditLogResponse(
            id=log.id,
            file_id=log.file_id,
            user_id=log.user_id,
            user_name=log.user_name,
            action=log.action,
            action_metadata=log.action_metadata,
            created_at=log.created_at.isoformat()
        )
        for log in logs
    ]


@router.post("/api/files/{file_id}/permissions", response_model=FilePermissionResponse)
async def set_file_permissions(
    file_id: str,
    permission: FilePermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_org_access)
):
    """Set permissions for a file."""
    service = FileManagementService(db)
    
    perm = service.set_file_permissions(
        file_id=file_id,
        user_id=permission.user_id,
        role=permission.role,
        can_view=permission.can_view,
        can_download=permission.can_download,
        can_comment=permission.can_comment,
        can_delete=permission.can_delete
    )
    
    return FilePermissionResponse(
        id=perm.id,
        file_id=perm.file_id,
        user_id=perm.user_id,
        role=perm.role,
        can_view=perm.can_view,
        can_download=perm.can_download,
        can_comment=perm.can_comment,
        can_delete=perm.can_delete,
        created_at=perm.created_at.isoformat()
    )


@router.post("/api/files/{file_id}/comments", response_model=FileCommentResponse)
async def create_file_comment(
    file_id: str,
    comment_data: FileCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a comment on a file.
    
    Supports:
    - Rich text formatting
    - @mentions for team collaboration
    - Threaded replies
    """
    from src.database import models as db_models
    
    design = db.query(db_models.ProjectDesign).filter(
        db_models.ProjectDesign.id == file_id
    ).first()
    
    if not design:
        raise HTTPException(status_code=404, detail="File not found")
    
    service = FileCommentService(db)
    
    comment = service.create_comment(
        file_id=file_id,
        project_id=design.project_id,
        org_id=current_user.org_id,
        user_id=current_user.id,
        user_name=current_user.name,
        comment_text=comment_data.comment,
        parent_comment_id=comment_data.parent_comment_id
    )
    
    return FileCommentResponse(
        id=comment.id,
        file_id=comment.file_id,
        project_id=comment.project_id,
        org_id=comment.org_id,
        user_id=comment.user_id,
        user_name=comment.user_name,
        comment=comment.comment,
        parent_comment_id=comment.parent_comment_id,
        mentions=comment.mentions.split(",") if comment.mentions else [],
        is_resolved=comment.is_resolved,
        resolved_by=comment.resolved_by,
        resolved_at=comment.resolved_at.isoformat() if comment.resolved_at else None,
        created_at=comment.created_at.isoformat(),
        updated_at=comment.updated_at.isoformat(),
        replies=[]
    )


@router.get("/api/files/{file_id}/comments", response_model=List[FileCommentResponse])
async def list_file_comments(
    file_id: str,
    include_resolved: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all comments for a file.
    
    Query params:
    - include_resolved: Include resolved comments (default: true)
    """
    service = FileCommentService(db)
    
    comments = service.list_comments(file_id, include_resolved)
    
    return [
        FileCommentResponse(
            id=c.id,
            file_id=c.file_id,
            project_id=c.project_id,
            org_id=c.org_id,
            user_id=c.user_id,
            user_name=c.user_name,
            comment=c.comment,
            parent_comment_id=c.parent_comment_id,
            mentions=c.mentions.split(",") if c.mentions else [],
            is_resolved=c.is_resolved,
            resolved_by=c.resolved_by,
            resolved_at=c.resolved_at.isoformat() if c.resolved_at else None,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
            replies=[]
        )
        for c in comments
    ]


@router.get("/api/files/{file_id}/comments/threaded")
async def get_threaded_comments(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comments organized in threaded structure."""
    service = FileCommentService(db)
    
    return service.get_threaded_comments(file_id)


@router.put("/api/comments/{comment_id}", response_model=FileCommentResponse)
async def update_comment(
    comment_id: str,
    comment_data: FileCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a comment."""
    service = FileCommentService(db)
    
    comment = service.update_comment(
        comment_id=comment_id,
        comment_text=comment_data.comment,
        user_id=current_user.id
    )
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or unauthorized")
    
    return FileCommentResponse(
        id=comment.id,
        file_id=comment.file_id,
        project_id=comment.project_id,
        org_id=comment.org_id,
        user_id=comment.user_id,
        user_name=comment.user_name,
        comment=comment.comment,
        parent_comment_id=comment.parent_comment_id,
        mentions=comment.mentions.split(",") if comment.mentions else [],
        is_resolved=comment.is_resolved,
        resolved_by=comment.resolved_by,
        resolved_at=comment.resolved_at.isoformat() if comment.resolved_at else None,
        created_at=comment.created_at.isoformat(),
        updated_at=comment.updated_at.isoformat(),
        replies=[]
    )


@router.delete("/api/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment."""
    service = FileCommentService(db)
    
    success = service.delete_comment(comment_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found or unauthorized")
    
    return {"message": "Comment deleted successfully"}


@router.patch("/api/comments/{comment_id}/resolve", response_model=FileCommentResponse)
async def resolve_comment(
    comment_id: str,
    resolve_data: FileCommentResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a comment as resolved or unresolved.
    
    Includes visual indicators and audit trail.
    """
    service = FileCommentService(db)
    
    comment = service.resolve_comment(
        comment_id=comment_id,
        user_id=current_user.id,
        user_name=current_user.name,
        is_resolved=resolve_data.is_resolved
    )
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return FileCommentResponse(
        id=comment.id,
        file_id=comment.file_id,
        project_id=comment.project_id,
        org_id=comment.org_id,
        user_id=comment.user_id,
        user_name=comment.user_name,
        comment=comment.comment,
        parent_comment_id=comment.parent_comment_id,
        mentions=comment.mentions.split(",") if comment.mentions else [],
        is_resolved=comment.is_resolved,
        resolved_by=comment.resolved_by,
        resolved_at=comment.resolved_at.isoformat() if comment.resolved_at else None,
        created_at=comment.created_at.isoformat(),
        updated_at=comment.updated_at.isoformat(),
        replies=[]
    )


@router.get("/api/projects/{project_id}/comments/unresolved", response_model=List[FileCommentResponse])
async def get_unresolved_comments(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unresolved comments for a project."""
    service = FileCommentService(db)
    
    comments = service.get_unresolved_comments(project_id)
    
    return [
        FileCommentResponse(
            id=c.id,
            file_id=c.file_id,
            project_id=c.project_id,
            org_id=c.org_id,
            user_id=c.user_id,
            user_name=c.user_name,
            comment=c.comment,
            parent_comment_id=c.parent_comment_id,
            mentions=c.mentions.split(",") if c.mentions else [],
            is_resolved=c.is_resolved,
            resolved_by=c.resolved_by,
            resolved_at=c.resolved_at.isoformat() if c.resolved_at else None,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
            replies=[]
        )
        for c in comments
    ]


@router.get("/api/users/mentions", response_model=List[FileCommentResponse])
async def get_user_mentions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all comments where the current user was mentioned."""
    service = FileCommentService(db)
    
    comments = service.get_user_mentions(current_user.id, current_user.org_id)
    
    return [
        FileCommentResponse(
            id=c.id,
            file_id=c.file_id,
            project_id=c.project_id,
            org_id=c.org_id,
            user_id=c.user_id,
            user_name=c.user_name,
            comment=c.comment,
            parent_comment_id=c.parent_comment_id,
            mentions=c.mentions.split(",") if c.mentions else [],
            is_resolved=c.is_resolved,
            resolved_by=c.resolved_by,
            resolved_at=c.resolved_at.isoformat() if c.resolved_at else None,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
            replies=[]
        )
        for c in comments
    ]
