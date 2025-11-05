import uuid
import re
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from src.database import models
from src.repositories.file_repository import FileCommentRepository


class FileCommentService:
    """Service for managing file comments, threading, and @mentions."""
    
    def __init__(self, db: Session):
        self.db = db
        self.comment_repo = FileCommentRepository(db)
    
    def create_comment(
        self,
        file_id: str,
        project_id: str,
        org_id: str,
        user_id: str,
        user_name: str,
        comment_text: str,
        parent_comment_id: Optional[str] = None
    ) -> models.FileComment:
        """
        Create a new comment on a file.
        
        Args:
            file_id: File ID
            project_id: Project ID
            org_id: Organization ID
            user_id: User ID who created comment
            user_name: User name who created comment
            comment_text: Comment text content
            parent_comment_id: Optional parent comment ID for threading
            
        Returns:
            Created FileComment object
        """
        mentions = self._extract_mentions(comment_text)
        
        comment_data = {
            "id": str(uuid.uuid4()),
            "file_id": file_id,
            "project_id": project_id,
            "org_id": org_id,
            "user_id": user_id,
            "user_name": user_name,
            "comment": comment_text,
            "parent_comment_id": parent_comment_id,
            "mentions": ",".join(mentions) if mentions else None,
            "is_resolved": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        comment = self.comment_repo.create(comment_data)
        
        if mentions:
            self._notify_mentioned_users(mentions, comment, user_name)
        
        return comment
    
    def update_comment(
        self,
        comment_id: str,
        comment_text: str,
        user_id: str
    ) -> Optional[models.FileComment]:
        """
        Update a comment.
        
        Args:
            comment_id: Comment ID
            comment_text: New comment text
            user_id: User ID requesting update
            
        Returns:
            Updated FileComment object or None if not found/unauthorized
        """
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment or comment.user_id != user_id:
            return None
        
        mentions = self._extract_mentions(comment_text)
        
        update_data = {
            "comment": comment_text,
            "mentions": ",".join(mentions) if mentions else None,
            "updated_at": datetime.now(timezone.utc)
        }
        
        updated_comment = self.comment_repo.update(comment_id, update_data)
        
        if mentions:
            self._notify_mentioned_users(mentions, updated_comment, comment.user_name)
        
        return updated_comment
    
    def delete_comment(
        self,
        comment_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a comment.
        
        Args:
            comment_id: Comment ID
            user_id: User ID requesting deletion
            
        Returns:
            True if successful
        """
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment or comment.user_id != user_id:
            return False
        
        return self.comment_repo.delete(comment_id)
    
    def get_comment(self, comment_id: str) -> Optional[models.FileComment]:
        """Get a comment by ID."""
        return self.comment_repo.get_by_id(comment_id)
    
    def list_comments(
        self,
        file_id: str,
        include_resolved: bool = True
    ) -> List[models.FileComment]:
        """
        List all comments for a file.
        
        Args:
            file_id: File ID
            include_resolved: Whether to include resolved comments
            
        Returns:
            List of FileComment objects
        """
        comments = self.comment_repo.get_by_file_id(file_id)
        
        if not include_resolved:
            comments = [c for c in comments if not c.is_resolved]
        
        return comments
    
    def get_threaded_comments(self, file_id: str) -> List[Dict]:
        """
        Get comments organized in threaded structure.
        
        Args:
            file_id: File ID
            
        Returns:
            List of comment dictionaries with nested replies
        """
        all_comments = self.comment_repo.get_by_file_id(file_id)
        
        comment_map = {}
        root_comments = []
        
        for comment in all_comments:
            comment_dict = self._comment_to_dict(comment)
            comment_dict["replies"] = []
            comment_map[comment.id] = comment_dict
            
            if not comment.parent_comment_id:
                root_comments.append(comment_dict)
        
        for comment in all_comments:
            if comment.parent_comment_id and comment.parent_comment_id in comment_map:
                comment_map[comment.parent_comment_id]["replies"].append(
                    comment_map[comment.id]
                )
        
        return root_comments
    
    def resolve_comment(
        self,
        comment_id: str,
        user_id: str,
        user_name: str,
        is_resolved: bool
    ) -> Optional[models.FileComment]:
        """
        Mark a comment as resolved or unresolved.
        
        Args:
            comment_id: Comment ID
            user_id: User ID performing action
            user_name: User name performing action
            is_resolved: Whether to mark as resolved
            
        Returns:
            Updated FileComment object or None if not found
        """
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            return None
        
        update_data = {
            "is_resolved": is_resolved,
            "resolved_by": user_id if is_resolved else None,
            "resolved_at": datetime.now(timezone.utc) if is_resolved else None,
            "updated_at": datetime.now(timezone.utc)
        }
        
        return self.comment_repo.update(comment_id, update_data)
    
    def get_unresolved_comments(self, project_id: str) -> List[models.FileComment]:
        """
        Get all unresolved comments for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of unresolved FileComment objects
        """
        all_comments = self.comment_repo.get_by_project_id(project_id)
        return [c for c in all_comments if not c.is_resolved]
    
    def _extract_mentions(self, text: str) -> List[str]:
        """
        Extract @mentions from comment text.
        
        Args:
            text: Comment text
            
        Returns:
            List of mentioned usernames (without @ symbol)
        """
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, text)
        return list(set(mentions))
    
    def _notify_mentioned_users(
        self,
        mentions: List[str],
        comment: models.FileComment,
        commenter_name: str
    ):
        """
        Send notifications to mentioned users.
        
        Args:
            mentions: List of mentioned usernames
            comment: FileComment object
            commenter_name: Name of user who created comment
        """
        for username in mentions:
            user = self.db.query(models.User).filter(
                models.User.name == username,
                models.User.org_id == comment.org_id
            ).first()
            
            if user:
                print(f"Notification: {commenter_name} mentioned {username} in a comment on file {comment.file_id}")
    
    def _comment_to_dict(self, comment: models.FileComment) -> Dict:
        """Convert FileComment model to dictionary."""
        return {
            "id": comment.id,
            "file_id": comment.file_id,
            "project_id": comment.project_id,
            "org_id": comment.org_id,
            "user_id": comment.user_id,
            "user_name": comment.user_name,
            "comment": comment.comment,
            "parent_comment_id": comment.parent_comment_id,
            "mentions": comment.mentions.split(",") if comment.mentions else [],
            "is_resolved": comment.is_resolved,
            "resolved_by": comment.resolved_by,
            "resolved_at": comment.resolved_at.isoformat() if comment.resolved_at else None,
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat()
        }
    
    def search_comments(
        self,
        project_id: str,
        search_term: str
    ) -> List[models.FileComment]:
        """
        Search comments by text content.
        
        Args:
            project_id: Project ID
            search_term: Search term
            
        Returns:
            List of matching FileComment objects
        """
        all_comments = self.comment_repo.get_by_project_id(project_id)
        return [
            c for c in all_comments 
            if search_term.lower() in c.comment.lower()
        ]
    
    def get_user_mentions(
        self,
        user_id: str,
        org_id: str
    ) -> List[models.FileComment]:
        """
        Get all comments where a user was mentioned.
        
        Args:
            user_id: User ID
            org_id: Organization ID
            
        Returns:
            List of FileComment objects where user was mentioned
        """
        user = self.db.query(models.User).filter(
            models.User.id == user_id
        ).first()
        
        if not user:
            return []
        
        all_comments = self.db.query(models.FileComment).filter(
            models.FileComment.org_id == org_id
        ).all()
        
        mentioned_comments = []
        for comment in all_comments:
            if comment.mentions and user.name in comment.mentions.split(","):
                mentioned_comments.append(comment)
        
        return mentioned_comments
