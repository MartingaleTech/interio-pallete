# File Management & Collaboration System - Technical Design

## Overview
This document outlines the technical design for implementing comprehensive file management and collaboration features for the Interio Palette platform.

## Current State Analysis

### Existing Implementation
1. **Database Models:**
   - `ProjectDesign`: Basic model with `file_url`, `file_type`, `title`, `description`, `uploaded_by`, `uploaded_at`
   - `TicketAttachment`: Model with `file_name`, `file_url`, `file_type`, `file_size`, `uploaded_by`
   - `TicketComment`: Basic comment model for tickets

2. **API Endpoints:**
   - `POST /api/projects/{project_id}/designs` - Create design (manual URL)
   - `GET /api/projects/{project_id}/designs` - List designs

3. **Frontend:**
   - `ProjectAttachments.tsx` - Basic UI with manual URL entry
   - No file upload widget
   - No preview functionality
   - No comments or collaboration features

### Gaps to Address
1. No actual file upload functionality (users manually enter URLs)
2. No cloud storage integration
3. No file validation or size limits
4. No metadata tracking (file size, version, etc.)
5. No comments on attachments
6. No @mentions or notifications
7. No version tracking
8. No role-based permissions on files
9. No file preview (images, PDFs, 3D models)
10. No audit logging

## Architecture Design

### 1. Cloud Storage Integration

**Technology Choice:** AWS S3 (or compatible service)

**Configuration:**
```python
# backend/src/config/storage.py
- S3_BUCKET_NAME
- S3_REGION
- S3_ACCESS_KEY
- S3_SECRET_KEY
- S3_ENDPOINT_URL (for S3-compatible services)
```

**Folder Structure:**
```
s3://bucket-name/
  ├── organizations/
  │   └── {org_id}/
  │       └── projects/
  │           └── {project_id}/
  │               ├── designs/
  │               │   └── {file_id}/
  │               │       ├── v1_{filename}
  │               │       ├── v2_{filename}
  │               │       └── ...
  │               └── attachments/
  │                   └── {file_id}/
  │                       └── {filename}
```

### 2. Enhanced Database Models

#### ProjectDesign (Enhanced)
```python
class ProjectDesign(Base):
    id: str (UUID)
    project_id: str (FK)
    title: str
    description: str
    file_name: str (original filename)
    file_url: str (S3 URL)
    file_type: str (MIME type)
    file_size: int (bytes)
    uploaded_by_id: str (FK to User)
    uploaded_by: str (name - denormalized)
    uploaded_at: datetime
    version: int (default 1)
    parent_id: str (FK to ProjectDesign, nullable - for versions)
    is_latest_version: bool (default True)
    # Metadata
    thumbnail_url: str (nullable - for images/PDFs)
    # Permissions
    is_public: bool (default False - visible to client)
    # Audit
    download_count: int (default 0)
```

#### FileComment (New Model)
```python
class FileComment(Base):
    id: str (UUID)
    file_id: str (FK to ProjectDesign)
    project_id: str (FK to Project)
    org_id: str (FK to Organization)
    user_id: str (FK to User)
    user_name: str (denormalized)
    comment: text
    parent_comment_id: str (FK to FileComment, nullable - for threading)
    mentions: text (JSON array of user IDs)
    is_resolved: bool (default False)
    resolved_by: str (FK to User, nullable)
    resolved_at: datetime (nullable)
    created_at: datetime
    updated_at: datetime
```

#### FilePermission (New Model)
```python
class FilePermission(Base):
    id: str (UUID)
    file_id: str (FK to ProjectDesign)
    user_id: str (FK to User, nullable)
    role: str (nullable - for role-based permissions)
    can_view: bool (default True)
    can_download: bool (default True)
    can_comment: bool (default True)
    can_delete: bool (default False)
    created_at: datetime
```

#### FileAuditLog (New Model)
```python
class FileAuditLog(Base):
    id: str (UUID)
    file_id: str (FK to ProjectDesign)
    user_id: str (FK to User)
    user_name: str (denormalized)
    action: str (UPLOAD, DOWNLOAD, DELETE, VIEW, COMMENT, VERSION_CREATE)
    metadata: text (JSON - additional context)
    created_at: datetime
```

### 3. API Endpoints

#### File Upload & Management
```
POST   /api/projects/{project_id}/files/upload
       - Multipart form data upload
       - Supports multiple files
       - Returns file metadata

GET    /api/projects/{project_id}/files
       - List all files for project
       - Query params: file_type, uploaded_by, is_latest_version

GET    /api/projects/{project_id}/files/{file_id}
       - Get file metadata

GET    /api/projects/{project_id}/files/{file_id}/download
       - Download file (with audit logging)

DELETE /api/projects/{project_id}/files/{file_id}
       - Soft delete file (mark as deleted)

GET    /api/projects/{project_id}/files/{file_id}/preview
       - Get preview URL (for images/PDFs)
```

#### File Versions
```
GET    /api/projects/{project_id}/files/{file_id}/versions
       - List all versions of a file

POST   /api/projects/{project_id}/files/{file_id}/versions
       - Upload new version of existing file

GET    /api/projects/{project_id}/files/{file_id}/versions/{version_id}
       - Get specific version metadata

POST   /api/projects/{project_id}/files/{file_id}/versions/{version_id}/restore
       - Restore a previous version as latest
```

#### File Comments
```
POST   /api/projects/{project_id}/files/{file_id}/comments
       - Add comment to file

GET    /api/projects/{project_id}/files/{file_id}/comments
       - Get all comments (with threading)

PUT    /api/projects/{project_id}/files/{file_id}/comments/{comment_id}
       - Update comment

DELETE /api/projects/{project_id}/files/{file_id}/comments/{comment_id}
       - Delete comment

POST   /api/projects/{project_id}/files/{file_id}/comments/{comment_id}/resolve
       - Mark comment as resolved/unresolved
```

#### File Permissions
```
GET    /api/projects/{project_id}/files/{file_id}/permissions
       - Get file permissions

POST   /api/projects/{project_id}/files/{file_id}/permissions
       - Set file permissions

PUT    /api/projects/{project_id}/files/{file_id}/permissions/{permission_id}
       - Update permissions
```

### 4. Service Layer Architecture

#### FileStorageService
```python
class FileStorageService:
    - upload_file(file, org_id, project_id, file_id) -> str (S3 URL)
    - download_file(file_url) -> bytes
    - delete_file(file_url) -> bool
    - generate_presigned_url(file_url, expiry=3600) -> str
    - generate_thumbnail(file_url, file_type) -> str (thumbnail URL)
```

#### FileManagementService
```python
class FileManagementService:
    - create_file(db, user, project_id, file_data, uploaded_file) -> ProjectDesign
    - get_files(db, user, project_id, filters) -> List[ProjectDesign]
    - get_file_by_id(db, user, file_id) -> ProjectDesign
    - delete_file(db, user, file_id) -> bool
    - download_file(db, user, file_id) -> (bytes, filename)
    - create_version(db, user, file_id, uploaded_file) -> ProjectDesign
    - get_versions(db, user, file_id) -> List[ProjectDesign]
    - restore_version(db, user, file_id, version_id) -> ProjectDesign
```

#### FileCommentService
```python
class FileCommentService:
    - create_comment(db, user, file_id, comment_data) -> FileComment
    - get_comments(db, user, file_id) -> List[FileComment] (threaded)
    - update_comment(db, user, comment_id, update_data) -> FileComment
    - delete_comment(db, user, comment_id) -> bool
    - resolve_comment(db, user, comment_id, is_resolved) -> FileComment
    - process_mentions(comment_text) -> List[str] (extract @mentions)
    - notify_mentioned_users(db, comment, mentioned_users) -> None
```

#### FilePermissionService
```python
class FilePermissionService:
    - check_permission(db, user, file_id, action) -> bool
    - get_permissions(db, user, file_id) -> List[FilePermission]
    - set_permissions(db, user, file_id, permissions) -> List[FilePermission]
    - update_permission(db, user, permission_id, update_data) -> FilePermission
```

### 5. File Validation

**Supported File Types:**
- Images: JPEG, PNG, GIF, WebP, SVG
- Documents: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX
- 3D Models: OBJ, FBX, SKP, STL, GLTF, GLB
- CAD: DWG, DXF
- Archives: ZIP, RAR
- Other: TXT, CSV

**Validation Rules:**
- Max file size: 100MB (configurable)
- File type whitelist (MIME type validation)
- Filename sanitization
- Virus scanning (optional - future enhancement)

### 6. Frontend Components

#### FileUploadWidget
```typescript
<FileUploadWidget
  projectId={string}
  onUploadComplete={(files) => void}
  maxFiles={number}
  maxFileSize={number}
  acceptedFileTypes={string[]}
  dragAndDrop={boolean}
/>
```

#### FilePreview
```typescript
<FilePreview
  file={FileMetadata}
  onClose={() => void}
  onComment={(comment) => void}
  onDownload={() => void}
/>
```

#### FileComments
```typescript
<FileComments
  fileId={string}
  comments={Comment[]}
  onAddComment={(comment) => void}
  onResolve={(commentId) => void}
  onMention={(userId) => void}
/>
```

#### FileVersionHistory
```typescript
<FileVersionHistory
  fileId={string}
  versions={FileVersion[]}
  onRestore={(versionId) => void}
  onCompare={(v1, v2) => void}
/>
```

## Implementation Phases

### Phase 1: Core File Upload (Priority: High)
1. Add boto3 dependency for S3
2. Create storage configuration
3. Implement FileStorageService
4. Enhance ProjectDesign model with new fields
5. Create file upload API endpoint
6. Build frontend file upload widget
7. Database migration

### Phase 2: File Management (Priority: High)
1. Implement file download with audit logging
2. Add file preview functionality
3. Implement file deletion
4. Build frontend file list with preview
5. Add file metadata display

### Phase 3: Comments & Collaboration (Priority: Medium)
1. Create FileComment model
2. Implement FileCommentService
3. Create comment API endpoints
4. Build frontend comment UI
5. Implement threading
6. Database migration

### Phase 4: @Mentions & Notifications (Priority: Medium)
1. Implement mention parsing
2. Create notification system for mentions
3. Build frontend @mention autocomplete
4. Integrate with existing notification system

### Phase 5: Version Tracking (Priority: Medium)
1. Enhance ProjectDesign for versioning
2. Implement version creation API
3. Build version history UI
4. Implement version restore
5. Add version comparison (future)

### Phase 6: Permissions & Security (Priority: Low)
1. Create FilePermission model
2. Implement FilePermissionService
3. Add permission checks to all file operations
4. Build permission management UI

### Phase 7: Advanced Features (Priority: Low)
1. 3D model viewer integration
2. PDF annotation
3. Image hotspot comments
4. Bulk file operations
5. File search and filtering

## Security Considerations

1. **Authentication:** All file operations require valid JWT token
2. **Authorization:** Multi-tenant isolation by org_id
3. **File Access:** Presigned URLs with expiry for downloads
4. **Input Validation:** File type, size, and content validation
5. **Rate Limiting:** Limit upload frequency per user
6. **Audit Logging:** Track all file operations
7. **Encryption:** Files encrypted at rest in S3
8. **CORS:** Proper CORS configuration for file uploads

## Performance Considerations

1. **Async Upload:** Use background tasks for large files
2. **Thumbnail Generation:** Generate thumbnails asynchronously
3. **Caching:** Cache file metadata and presigned URLs
4. **CDN:** Use CloudFront or similar for file delivery
5. **Pagination:** Paginate file lists and comments
6. **Lazy Loading:** Load file previews on demand

## Testing Strategy

1. **Unit Tests:**
   - File validation logic
   - Storage service operations
   - Permission checks
   - Comment threading logic

2. **Integration Tests:**
   - File upload flow
   - Download with audit logging
   - Version creation and restore
   - Comment creation with mentions

3. **E2E Tests:**
   - Complete file upload workflow
   - Comment and resolve workflow
   - Version tracking workflow

## Dependencies to Add

```toml
# backend/pyproject.toml
boto3 = "^1.34.0"  # AWS S3 SDK
python-multipart = "^0.0.6"  # File upload support
pillow = "^10.0.0"  # Image processing for thumbnails
python-magic = "^0.4.27"  # MIME type detection
```

## Migration Plan

1. Create new database models (FileComment, FilePermission, FileAuditLog)
2. Add new fields to ProjectDesign model
3. Migrate existing file_url data (if any)
4. Deploy backend changes
5. Deploy frontend changes
6. Test end-to-end
7. Monitor and optimize

## Success Metrics

1. File upload success rate > 99%
2. Average upload time < 5 seconds for files < 10MB
3. Comment response time < 500ms
4. Zero data loss incidents
5. User adoption rate > 80% within 1 month
