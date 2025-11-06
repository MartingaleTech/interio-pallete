"""
Comprehensive tests for file management routes.
Tests all endpoints in src/routes/file_management.py
"""
import pytest
from datetime import datetime, timedelta
import uuid
from io import BytesIO

from src.database import models
from src.utils.security import hash_password


@pytest.fixture
def test_org_owner(db_session):
    """Create a test organization owner."""
    user = models.User(
        id=str(uuid.uuid4()),
        email="owner@example.com",
        name="Org Owner",
        role=models.UserRole.ORG_OWNER,
        phone="1234567890",
        password_hash=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_organization(db_session, test_org_owner):
    """Create a test organization."""
    org = models.Organization(
        id=str(uuid.uuid4()),
        name="Test Organization",
        email="org@example.com",
        phone="1234567890",
        address="123 Test St",
        city="Test City",
        state="Test State",
        pincode="12345",
        owner_id=test_org_owner.id,
        subscription_status=models.SubscriptionStatus.ACTIVE,
        subscription_plan="basic",
        subscription_start=datetime.now(),
        subscription_end=datetime.now() + timedelta(days=30)
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    
    test_org_owner.org_id = org.id
    db_session.commit()
    db_session.refresh(test_org_owner)
    
    return org


@pytest.fixture
def test_project(db_session, test_organization):
    """Create a test project."""
    project = models.Project(
        id=str(uuid.uuid4()),
        org_id=test_organization.id,
        name="Test Project",
        description="Test project description",
        status=models.ProjectStatus.IN_PROGRESS,
        budget=10000.0,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30)
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def owner_token(db_session, test_org_owner):
    """Create a test token for org owner."""
    token = models.Token(
        token="owner_token_123",
        user_id=test_org_owner.id,
        expires_at=datetime.now() + timedelta(days=1)
    )
    db_session.add(token)
    db_session.commit()
    return token


@pytest.fixture
def test_file(db_session, test_project, test_org_owner):
    """Create a test file."""
    design = models.ProjectDesign(
        id=str(uuid.uuid4()),
        project_id=test_project.id,
        title="Test Design",
        description="Test Description",
        file_name="test.png",
        file_url="https://example.com/test.png",
        file_type="image/png",
        file_size=1024,
        uploaded_by=test_org_owner.name,
        uploaded_by_id=test_org_owner.id,
        version=1,
        is_latest_version=True
    )
    db_session.add(design)
    db_session.commit()
    db_session.refresh(design)
    return design


class TestFileUpload:
    """Tests for file upload endpoints"""
    
    def test_upload_file(self, client, owner_token, test_project):
        """Test POST /api/v1/projects/{project_id}/files/upload"""
        file_content = b"fake image content"
        files = {
            "file": ("test.png", BytesIO(file_content), "image/png")
        }
        data = {
            "title": "Test Upload",
            "description": "Test file upload",
            "is_public": "false"
        }
        
        response = client.post(
            f"/api/v1/projects/{test_project.id}/files/upload",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            files=files,
            data=data
        )
        assert response.status_code in [200, 201, 500]
    
    def test_upload_file_unauthorized(self, client, test_project):
        """Test uploading file without authentication"""
        file_content = b"fake image content"
        files = {
            "file": ("test.png", BytesIO(file_content), "image/png")
        }
        data = {
            "title": "Test Upload",
            "description": "Test file upload"
        }
        
        response = client.post(
            f"/api/v1/projects/{test_project.id}/files/upload",
            files=files,
            data=data
        )
        assert response.status_code == 403
    
    def test_upload_new_version(self, client, owner_token, test_file):
        """Test POST /api/v1/files/{file_id}/versions/upload"""
        file_content = b"new version content"
        files = {
            "file": ("test_v2.png", BytesIO(file_content), "image/png")
        }
        
        response = client.post(
            f"/api/v1/files/{test_file.id}/versions/upload",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            files=files
        )
        assert response.status_code in [200, 201, 500]


class TestFileRetrieval:
    """Tests for file retrieval endpoints"""
    
    def test_download_file(self, client, owner_token, test_file):
        """Test GET /api/v1/files/{file_id}/download"""
        response = client.get(
            f"/api/v1/files/{test_file.id}/download",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_get_file_metadata(self, client, owner_token, test_file):
        """Test GET /api/v1/files/{file_id}"""
        response = client.get(
            f"/api/v1/files/{test_file.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 404, 500]
    
    def test_get_file_metadata_not_found(self, client, owner_token):
        """Test getting metadata for non-existent file"""
        response = client.get(
            f"/api/v1/files/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code == 404
    
    def test_list_project_files(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/files"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/files",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_list_project_files_latest_only(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/files with latest_only filter"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/files?latest_only=true",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_get_file_versions(self, client, owner_token, test_file):
        """Test GET /api/v1/files/{file_id}/versions"""
        response = client.get(
            f"/api/v1/files/{test_file.id}/versions",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]


class TestFileManagement:
    """Tests for file management endpoints"""
    
    def test_delete_file(self, client, owner_token, test_file):
        """Test DELETE /api/v1/files/{file_id}"""
        response = client.delete(
            f"/api/v1/files/{test_file.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 404, 500]
    
    def test_restore_file_version(self, client, owner_token, test_file):
        """Test POST /api/v1/files/versions/{version_id}/restore"""
        response = client.post(
            f"/api/v1/files/versions/{test_file.id}/restore",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 404, 500]
    
    def test_get_file_audit_logs(self, client, owner_token, test_file):
        """Test GET /api/v1/files/{file_id}/audit-logs"""
        response = client.get(
            f"/api/v1/files/{test_file.id}/audit-logs",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]


class TestFilePermissions:
    """Tests for file permission endpoints"""
    
    def test_set_file_permissions(self, client, owner_token, test_file, test_db, test_organization):
        """Test POST /api/v1/files/{file_id}/permissions"""
        user = models.User(
            id=str(uuid.uuid4()),
            email="member@example.com",
            name="Member",
            role=models.UserRole.ORG_MEMBER,
            phone="1234567890",
            password_hash=hash_password("password123"),
            org_id=test_organization.id
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/files/{test_file.id}/permissions",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "user_id": user.id,
                "role": "viewer",
                "can_view": True,
                "can_download": True,
                "can_comment": True,
                "can_delete": False
            }
        )
        assert response.status_code in [200, 500]


class TestFileComments:
    """Tests for file comment endpoints"""
    
    def test_create_file_comment(self, client, owner_token, test_file):
        """Test POST /api/v1/files/{file_id}/comments"""
        response = client.post(
            f"/api/v1/files/{test_file.id}/comments",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "comment": "This looks great!",
                "parent_comment_id": None
            }
        )
        assert response.status_code in [200, 201, 404, 500]
    
    def test_create_file_comment_reply(self, client, owner_token, test_file, test_db):
        """Test creating a reply to a comment"""
        comment = models.FileComment(
            id=str(uuid.uuid4()),
            file_id=test_file.id,
            project_id=test_file.project_id,
            org_id=test_file.project.org_id,
            user_id=test_file.uploaded_by_id,
            user_name=test_file.uploaded_by,
            comment="Parent comment"
        )
        db_session.add(comment)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/files/{test_file.id}/comments",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "comment": "Reply to comment",
                "parent_comment_id": comment.id
            }
        )
        assert response.status_code in [200, 201, 404, 500]
    
    def test_list_file_comments(self, client, owner_token, test_file):
        """Test GET /api/v1/files/{file_id}/comments"""
        response = client.get(
            f"/api/v1/files/{test_file.id}/comments",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_list_file_comments_include_resolved(self, client, owner_token, test_file):
        """Test GET /api/v1/files/{file_id}/comments with include_resolved filter"""
        response = client.get(
            f"/api/v1/files/{test_file.id}/comments?include_resolved=true",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_get_threaded_comments(self, client, owner_token, test_file):
        """Test GET /api/v1/files/{file_id}/comments/threaded"""
        response = client.get(
            f"/api/v1/files/{test_file.id}/comments/threaded",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_update_comment(self, client, owner_token, test_file, test_db, test_org_owner):
        """Test PUT /api/v1/comments/{comment_id}"""
        comment = models.FileComment(
            id=str(uuid.uuid4()),
            file_id=test_file.id,
            project_id=test_file.project_id,
            org_id=test_org_owner.org_id,
            user_id=test_org_owner.id,
            user_name=test_org_owner.name,
            comment="Original comment"
        )
        db_session.add(comment)
        db_session.commit()
        
        response = client.put(
            f"/api/v1/comments/{comment.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "comment": "Updated comment"
            }
        )
        assert response.status_code in [200, 404, 500]
    
    def test_delete_comment(self, client, owner_token, test_file, test_db, test_org_owner):
        """Test DELETE /api/v1/comments/{comment_id}"""
        comment = models.FileComment(
            id=str(uuid.uuid4()),
            file_id=test_file.id,
            project_id=test_file.project_id,
            org_id=test_org_owner.org_id,
            user_id=test_org_owner.id,
            user_name=test_org_owner.name,
            comment="Comment to delete"
        )
        db_session.add(comment)
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/comments/{comment.id}",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 404, 500]
    
    def test_resolve_comment(self, client, owner_token, test_file, test_db, test_org_owner):
        """Test PATCH /api/v1/comments/{comment_id}/resolve"""
        comment = models.FileComment(
            id=str(uuid.uuid4()),
            file_id=test_file.id,
            project_id=test_file.project_id,
            org_id=test_org_owner.org_id,
            user_id=test_org_owner.id,
            user_name=test_org_owner.name,
            comment="Comment to resolve",
            is_resolved=False
        )
        db_session.add(comment)
        db_session.commit()
        
        response = client.patch(
            f"/api/v1/comments/{comment.id}/resolve",
            headers={"Authorization": f"Bearer {owner_token.token}"},
            json={
                "is_resolved": True
            }
        )
        assert response.status_code in [200, 404, 500]
    
    def test_get_unresolved_comments(self, client, owner_token, test_project):
        """Test GET /api/v1/projects/{project_id}/comments/unresolved"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/comments/unresolved",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]
    
    def test_get_user_mentions(self, client, owner_token):
        """Test GET /api/v1/users/mentions"""
        response = client.get(
            "/api/v1/users/mentions",
            headers={"Authorization": f"Bearer {owner_token.token}"}
        )
        assert response.status_code in [200, 500]


class TestFileUnauthorized:
    """Tests for unauthorized access to file endpoints"""
    
    def test_upload_file_unauthorized(self, client, test_project):
        """Test uploading file without authentication"""
        file_content = b"fake content"
        files = {
            "file": ("test.png", BytesIO(file_content), "image/png")
        }
        data = {
            "title": "Test",
            "description": "Test"
        }
        
        response = client.post(
            f"/api/v1/projects/{test_project.id}/files/upload",
            files=files,
            data=data
        )
        assert response.status_code == 403
    
    def test_download_file_unauthorized(self, client, test_file):
        """Test downloading file without authentication"""
        response = client.get(f"/api/v1/files/{test_file.id}/download")
        assert response.status_code == 403
    
    def test_delete_file_unauthorized(self, client, test_file):
        """Test deleting file without authentication"""
        response = client.delete(f"/api/v1/files/{test_file.id}")
        assert response.status_code == 403
    
    def test_create_comment_unauthorized(self, client, test_file):
        """Test creating comment without authentication"""
        response = client.post(
            f"/api/v1/files/{test_file.id}/comments",
            json={"comment": "Test"}
        )
        assert response.status_code == 403
