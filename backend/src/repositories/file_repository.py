from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import models


class FileCommentRepository:
    """Repository for FileComment database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, comment_data: dict) -> models.FileComment:
        """Create a new file comment."""
        db_comment = models.FileComment(**comment_data)
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def get_by_id(self, comment_id: str) -> Optional[models.FileComment]:
        """Get comment by ID."""
        return self.db.query(models.FileComment).filter(
            models.FileComment.id == comment_id
        ).first()
    
    def get_by_file_id(self, file_id: str) -> List[models.FileComment]:
        """Get all comments for a file."""
        return self.db.query(models.FileComment).filter(
            models.FileComment.file_id == file_id
        ).order_by(models.FileComment.created_at.asc()).all()
    
    def get_by_project_id(self, project_id: str) -> List[models.FileComment]:
        """Get all comments for a project."""
        return self.db.query(models.FileComment).filter(
            models.FileComment.project_id == project_id
        ).order_by(models.FileComment.created_at.desc()).all()
    
    def update(self, comment_id: str, update_data: dict) -> Optional[models.FileComment]:
        """Update a comment."""
        comment = self.get_by_id(comment_id)
        if comment:
            for key, value in update_data.items():
                if value is not None:
                    setattr(comment, key, value)
            self.db.commit()
            self.db.refresh(comment)
        return comment
    
    def delete(self, comment_id: str) -> bool:
        """Delete a comment."""
        comment = self.get_by_id(comment_id)
        if comment:
            self.db.delete(comment)
            self.db.commit()
            return True
        return False


class FilePermissionRepository:
    """Repository for FilePermission database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, permission_data: dict) -> models.FilePermission:
        """Create a new file permission."""
        db_permission = models.FilePermission(**permission_data)
        self.db.add(db_permission)
        self.db.commit()
        self.db.refresh(db_permission)
        return db_permission
    
    def get_by_id(self, permission_id: str) -> Optional[models.FilePermission]:
        """Get permission by ID."""
        return self.db.query(models.FilePermission).filter(
            models.FilePermission.id == permission_id
        ).first()
    
    def get_by_file_id(self, file_id: str) -> List[models.FilePermission]:
        """Get all permissions for a file."""
        return self.db.query(models.FilePermission).filter(
            models.FilePermission.file_id == file_id
        ).all()
    
    def get_by_file_and_user(self, file_id: str, user_id: str) -> Optional[models.FilePermission]:
        """Get permission for a specific file and user."""
        return self.db.query(models.FilePermission).filter(
            models.FilePermission.file_id == file_id,
            models.FilePermission.user_id == user_id
        ).first()
    
    def update(self, permission_id: str, update_data: dict) -> Optional[models.FilePermission]:
        """Update a permission."""
        permission = self.get_by_id(permission_id)
        if permission:
            for key, value in update_data.items():
                if value is not None:
                    setattr(permission, key, value)
            self.db.commit()
            self.db.refresh(permission)
        return permission
    
    def delete(self, permission_id: str) -> bool:
        """Delete a permission."""
        permission = self.get_by_id(permission_id)
        if permission:
            self.db.delete(permission)
            self.db.commit()
            return True
        return False


class FileAuditLogRepository:
    """Repository for FileAuditLog database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, log_data: dict) -> models.FileAuditLog:
        """Create a new audit log entry."""
        db_log = models.FileAuditLog(**log_data)
        self.db.add(db_log)
        self.db.commit()
        self.db.refresh(db_log)
        return db_log
    
    def get_by_id(self, log_id: str) -> Optional[models.FileAuditLog]:
        """Get audit log by ID."""
        return self.db.query(models.FileAuditLog).filter(
            models.FileAuditLog.id == log_id
        ).first()
    
    def get_by_file_id(self, file_id: str) -> List[models.FileAuditLog]:
        """Get all audit logs for a file."""
        return self.db.query(models.FileAuditLog).filter(
            models.FileAuditLog.file_id == file_id
        ).order_by(models.FileAuditLog.created_at.desc()).all()
    
    def get_by_user_id(self, user_id: str) -> List[models.FileAuditLog]:
        """Get all audit logs for a user."""
        return self.db.query(models.FileAuditLog).filter(
            models.FileAuditLog.user_id == user_id
        ).order_by(models.FileAuditLog.created_at.desc()).all()
