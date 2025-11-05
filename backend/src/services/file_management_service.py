import uuid
import json
from typing import List, Optional, Tuple
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from src.database import models
from src.repositories.team_repository import ProjectDesignRepository
from src.repositories.file_repository import FileAuditLogRepository, FilePermissionRepository
from src.repositories.notification_repository import ProjectNotificationRepository
from src.services.file_storage_service import FileStorageService
from src.utils.file_validation import validate_upload_file, sanitize_filename, get_file_extension, is_image_file


class FileManagementService:
    """Service for managing file uploads, downloads, and operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.design_repo = ProjectDesignRepository(db)
        self.audit_repo = FileAuditLogRepository(db)
        self.permission_repo = FilePermissionRepository(db)
        self.notification_repo = ProjectNotificationRepository(db)
        self.storage_service = FileStorageService()
    
    async def upload_file(
        self,
        file: UploadFile,
        project_id: str,
        title: str,
        description: str,
        user_id: str,
        user_name: str,
        org_id: str,
        is_public: bool = False
    ) -> models.ProjectDesign:
        """
        Upload a new file to a project.
        
        Args:
            file: The uploaded file
            project_id: Project ID
            title: File title
            description: File description
            user_id: User ID who uploaded
            user_name: User name who uploaded
            org_id: Organization ID
            is_public: Whether file is publicly accessible
            
        Returns:
            Created ProjectDesign object
        """
        is_valid, error_message = validate_upload_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        file_id = str(uuid.uuid4())
        sanitized_filename = sanitize_filename(file.filename)
        
        file_content = await file.read()
        content_type = file.content_type or "application/octet-stream"
        file_size = len(file_content)
        
        file_url = self.storage_service.upload_file(
            file_content=file_content,
            org_id=org_id,
            project_id=project_id,
            file_id=file_id,
            filename=sanitized_filename,
            content_type=content_type,
            version=1
        )
        
        thumbnail_url = None
        if is_image_file(content_type):
            try:
                thumbnail_url = self.storage_service.generate_thumbnail(
                    file_content=file_content,
                    file_type=content_type,
                    org_id=org_id,
                    project_id=project_id,
                    file_id=file_id
                )
            except Exception as e:
                print(f"Failed to generate thumbnail: {e}")
        
        design_data = {
            "id": file_id,
            "project_id": project_id,
            "title": title,
            "description": description,
            "file_name": sanitized_filename,
            "file_url": file_url,
            "file_type": file.content_type or "application/octet-stream",
            "file_size": file_size,
            "uploaded_by_id": user_id,
            "uploaded_by": user_name,
            "uploaded_at": datetime.now(datetime.UTC),
            "version": 1,
            "is_latest_version": True,
            "thumbnail_url": thumbnail_url,
            "is_public": is_public,
            "download_count": 0,
            "is_deleted": False
        }
        
        design = self.design_repo.create(design_data)
        
        self._create_audit_log(
            file_id=file_id,
            user_id=user_id,
            user_name=user_name,
            action="upload",
            metadata={"file_name": sanitized_filename, "file_size": file_size}
        )
        
        notification_id = str(uuid.uuid4())
        notification_data = {
            "id": notification_id,
            "project_id": project_id,
            "org_id": org_id,
            "user_id": None,
            "notification_type": "file_uploaded",
            "title": "New File Uploaded",
            "message": f"{user_name} uploaded {title} ({sanitized_filename})",
            "is_read": False,
            "created_at": datetime.now(datetime.UTC)
        }
        self.notification_repo.create(notification_data)
        
        return design
    
    async def upload_new_version(
        self,
        file: UploadFile,
        parent_file_id: str,
        user_id: str,
        user_name: str,
        org_id: str
    ) -> models.ProjectDesign:
        """
        Upload a new version of an existing file.
        
        Args:
            file: The uploaded file
            parent_file_id: ID of the parent file
            user_id: User ID who uploaded
            user_name: User name who uploaded
            org_id: Organization ID
            
        Returns:
            Created ProjectDesign object for new version
        """
        parent_design = self.design_repo.get_by_id(parent_file_id)
        if not parent_design:
            raise HTTPException(status_code=404, detail="Parent file not found")
        
        is_valid, error_message = validate_upload_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        versions = self.design_repo.get_versions(parent_file_id)
        next_version = max([v.version for v in versions]) + 1
        
        self.design_repo.update(parent_design.id, {"is_latest_version": False})
        
        file_id = str(uuid.uuid4())
        sanitized_filename = sanitize_filename(file.filename)
        
        file_content = await file.read()
        content_type = file.content_type or "application/octet-stream"
        file_size = len(file_content)
        
        file_url = self.storage_service.upload_file(
            file_content=file_content,
            org_id=org_id,
            project_id=parent_design.project_id,
            file_id=file_id,
            filename=sanitized_filename,
            content_type=content_type,
            version=next_version
        )
        
        thumbnail_url = None
        if is_image_file(content_type):
            try:
                thumbnail_url = self.storage_service.generate_thumbnail(
                    file_content=file_content,
                    file_type=content_type,
                    org_id=org_id,
                    project_id=parent_design.project_id,
                    file_id=file_id
                )
            except Exception as e:
                print(f"Failed to generate thumbnail: {e}")
        
        root_id = parent_design.parent_id if parent_design.parent_id else parent_design.id
        
        design_data = {
            "id": file_id,
            "project_id": parent_design.project_id,
            "title": parent_design.title,
            "description": parent_design.description,
            "file_name": sanitized_filename,
            "file_url": file_url,
            "file_type": file.content_type or "application/octet-stream",
            "file_size": file_size,
            "uploaded_by_id": user_id,
            "uploaded_by": user_name,
            "uploaded_at": datetime.now(datetime.UTC),
            "version": next_version,
            "parent_id": root_id,
            "is_latest_version": True,
            "thumbnail_url": thumbnail_url,
            "is_public": parent_design.is_public,
            "download_count": 0,
            "is_deleted": False
        }
        
        design = self.design_repo.create(design_data)
        
        self._create_audit_log(
            file_id=file_id,
            user_id=user_id,
            user_name=user_name,
            action="upload_version",
            metadata={"version": next_version, "parent_id": root_id}
        )
        
        return design
    
    async def download_file(
        self,
        file_id: str,
        user_id: str,
        user_name: str
    ) -> Tuple[str, str, str]:
        """
        Get download URL for a file and log the download.
        
        Args:
            file_id: File ID
            user_id: User ID requesting download
            user_name: User name requesting download
            
        Returns:
            Tuple of (file_url, file_name, file_type)
        """
        design = self.design_repo.get_by_id(file_id)
        if not design:
            raise HTTPException(status_code=404, detail="File not found")
        
        download_url = self.storage_service.generate_presigned_url(design.file_url)
        
        self.design_repo.increment_download_count(file_id)
        
        self._create_audit_log(
            file_id=file_id,
            user_id=user_id,
            user_name=user_name,
            action="download",
            metadata={"file_name": design.file_name}
        )
        
        return download_url, design.file_name, design.file_type
    
    async def delete_file(
        self,
        file_id: str,
        user_id: str,
        user_name: str
    ) -> bool:
        """
        Soft delete a file.
        
        Args:
            file_id: File ID
            user_id: User ID requesting deletion
            user_name: User name requesting deletion
            
        Returns:
            True if successful
        """
        design = self.design_repo.get_by_id(file_id)
        if not design:
            raise HTTPException(status_code=404, detail="File not found")
        
        success = self.design_repo.soft_delete(file_id)
        
        if success:
            self._create_audit_log(
                file_id=file_id,
                user_id=user_id,
                user_name=user_name,
                action="delete",
                metadata={"file_name": design.file_name}
            )
        
        return success
    
    def get_file_metadata(self, file_id: str) -> Optional[models.ProjectDesign]:
        """Get file metadata by ID."""
        return self.design_repo.get_by_id(file_id)
    
    def list_files(self, project_id: str, latest_only: bool = True) -> List[models.ProjectDesign]:
        """
        List all files for a project.
        
        Args:
            project_id: Project ID
            latest_only: If True, only return latest versions
            
        Returns:
            List of ProjectDesign objects
        """
        if latest_only:
            return self.design_repo.get_latest_versions(project_id)
        return self.design_repo.get_by_project_id(project_id)
    
    def get_file_versions(self, file_id: str) -> List[models.ProjectDesign]:
        """Get all versions of a file."""
        return self.design_repo.get_versions(file_id)
    
    async def restore_version(
        self,
        version_id: str,
        user_id: str,
        user_name: str,
        org_id: str
    ) -> models.ProjectDesign:
        """
        Restore a previous version as the latest version.
        
        Args:
            version_id: ID of the version to restore
            user_id: User ID requesting restore
            user_name: User name requesting restore
            org_id: Organization ID
            
        Returns:
            New ProjectDesign object representing restored version
        """
        version_design = self.design_repo.get_by_id(version_id)
        if not version_design:
            raise HTTPException(status_code=404, detail="Version not found")
        
        versions = self.design_repo.get_versions(version_id)
        current_latest = next((v for v in versions if v.is_latest_version), None)
        
        if current_latest:
            self.design_repo.update(current_latest.id, {"is_latest_version": False})
        
        next_version = max([v.version for v in versions]) + 1
        
        file_id = str(uuid.uuid4())
        root_id = version_design.parent_id if version_design.parent_id else version_design.id
        
        design_data = {
            "id": file_id,
            "project_id": version_design.project_id,
            "title": version_design.title,
            "description": version_design.description,
            "file_name": version_design.file_name,
            "file_url": version_design.file_url,
            "file_type": version_design.file_type,
            "file_size": version_design.file_size,
            "uploaded_by_id": user_id,
            "uploaded_by": user_name,
            "uploaded_at": datetime.now(datetime.UTC),
            "version": next_version,
            "parent_id": root_id,
            "is_latest_version": True,
            "thumbnail_url": version_design.thumbnail_url,
            "is_public": version_design.is_public,
            "download_count": 0,
            "is_deleted": False
        }
        
        design = self.design_repo.create(design_data)
        
        self._create_audit_log(
            file_id=file_id,
            user_id=user_id,
            user_name=user_name,
            action="restore_version",
            metadata={"restored_from_version": version_design.version, "new_version": next_version}
        )
        
        return design
    
    def get_file_audit_logs(self, file_id: str) -> List[models.FileAuditLog]:
        """Get audit logs for a file."""
        return self.audit_repo.get_by_file_id(file_id)
    
    def check_user_permission(
        self,
        file_id: str,
        user_id: str,
        permission_type: str
    ) -> bool:
        """
        Check if user has specific permission for a file.
        
        Args:
            file_id: File ID
            user_id: User ID
            permission_type: Type of permission (view, download, comment, delete)
            
        Returns:
            True if user has permission
        """
        permission = self.permission_repo.get_by_file_and_user(file_id, user_id)
        
        if not permission:
            return True
        
        permission_map = {
            "view": permission.can_view,
            "download": permission.can_download,
            "comment": permission.can_comment,
            "delete": permission.can_delete
        }
        
        return permission_map.get(permission_type, False)
    
    def set_file_permissions(
        self,
        file_id: str,
        user_id: Optional[str],
        role: Optional[str],
        can_view: bool,
        can_download: bool,
        can_comment: bool,
        can_delete: bool
    ) -> models.FilePermission:
        """Set permissions for a file."""
        permission_data = {
            "id": str(uuid.uuid4()),
            "file_id": file_id,
            "user_id": user_id,
            "role": role,
            "can_view": can_view,
            "can_download": can_download,
            "can_comment": can_comment,
            "can_delete": can_delete,
            "created_at": datetime.now(datetime.UTC)
        }
        
        return self.permission_repo.create(permission_data)
    
    def _create_audit_log(
        self,
        file_id: str,
        user_id: str,
        user_name: str,
        action: str,
        metadata: dict = None
    ) -> models.FileAuditLog:
        """Create an audit log entry."""
        log_data = {
            "id": str(uuid.uuid4()),
            "file_id": file_id,
            "user_id": user_id,
            "user_name": user_name,
            "action": action,
            "action_metadata": json.dumps(metadata) if metadata else None,
            "created_at": datetime.now(datetime.UTC)
        }
        
        return self.audit_repo.create(log_data)
