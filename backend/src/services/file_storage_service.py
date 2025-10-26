import os
import uuid
import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
from pathlib import Path
from src.config.storage import storage_config
from PIL import Image
import io


class FileStorageService:
    """Service for handling file storage operations (S3 or local)."""
    
    def __init__(self):
        self.use_local = storage_config.USE_LOCAL_STORAGE
        
        if not self.use_local:
            self.s3_client = boto3.client(
                's3',
                region_name=storage_config.S3_REGION,
                aws_access_key_id=storage_config.S3_ACCESS_KEY,
                aws_secret_access_key=storage_config.S3_SECRET_KEY,
                endpoint_url=storage_config.S3_ENDPOINT_URL
            )
            self.bucket_name = storage_config.S3_BUCKET_NAME
        else:
            self.local_storage_path = Path(storage_config.LOCAL_STORAGE_PATH)
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, org_id: str, project_id: str, file_id: str, filename: str, version: int = 1) -> str:
        """Generate file path in storage."""
        safe_filename = self._sanitize_filename(filename)
        versioned_filename = f"v{version}_{safe_filename}"
        return f"organizations/{org_id}/projects/{project_id}/files/{file_id}/{versioned_filename}"
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks."""
        filename = os.path.basename(filename)
        filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
        return filename[:255]
    
    def upload_file(
        self, 
        file_content: bytes, 
        org_id: str, 
        project_id: str, 
        file_id: str, 
        filename: str,
        content_type: str,
        version: int = 1
    ) -> str:
        """
        Upload file to storage and return the file URL.
        
        Args:
            file_content: File content as bytes
            org_id: Organization ID
            project_id: Project ID
            file_id: Unique file ID
            filename: Original filename
            content_type: MIME type
            version: File version number
            
        Returns:
            File URL or path
        """
        file_path = self._get_file_path(org_id, project_id, file_id, filename, version)
        
        if self.use_local:
            return self._upload_local(file_content, file_path)
        else:
            return self._upload_s3(file_content, file_path, content_type)
    
    def _upload_local(self, file_content: bytes, file_path: str) -> str:
        """Upload file to local storage."""
        full_path = self.local_storage_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(file_content)
        
        return str(full_path)
    
    def _upload_s3(self, file_content: bytes, file_path: str, content_type: str) -> str:
        """Upload file to S3."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_content,
                ContentType=content_type
            )
            return f"s3://{self.bucket_name}/{file_path}"
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def download_file(self, file_url: str) -> bytes:
        """
        Download file from storage.
        
        Args:
            file_url: File URL or path
            
        Returns:
            File content as bytes
        """
        if self.use_local:
            return self._download_local(file_url)
        else:
            return self._download_s3(file_url)
    
    def _download_local(self, file_path: str) -> bytes:
        """Download file from local storage."""
        with open(file_path, 'rb') as f:
            return f.read()
    
    def _download_s3(self, file_url: str) -> bytes:
        """Download file from S3."""
        if file_url.startswith('s3://'):
            file_url = file_url[5:]
            bucket_name, key = file_url.split('/', 1)
        else:
            bucket_name = self.bucket_name
            key = file_url
        
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Failed to download file from S3: {str(e)}")
    
    def delete_file(self, file_url: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            file_url: File URL or path
            
        Returns:
            True if successful
        """
        if self.use_local:
            return self._delete_local(file_url)
        else:
            return self._delete_s3(file_url)
    
    def _delete_local(self, file_path: str) -> bool:
        """Delete file from local storage."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete local file: {str(e)}")
    
    def _delete_s3(self, file_url: str) -> bool:
        """Delete file from S3."""
        if file_url.startswith('s3://'):
            file_url = file_url[5:]
            bucket_name, key = file_url.split('/', 1)
        else:
            bucket_name = self.bucket_name
            key = file_url
        
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=key)
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete file from S3: {str(e)}")
    
    def generate_presigned_url(self, file_url: str, expiry: int = 3600) -> str:
        """
        Generate presigned URL for file download.
        
        Args:
            file_url: File URL or path
            expiry: URL expiry time in seconds
            
        Returns:
            Presigned URL
        """
        if self.use_local:
            return file_url
        
        if file_url.startswith('s3://'):
            file_url = file_url[5:]
            bucket_name, key = file_url.split('/', 1)
        else:
            bucket_name = self.bucket_name
            key = file_url
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=expiry
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def generate_thumbnail(
        self, 
        file_content: bytes, 
        file_type: str,
        org_id: str,
        project_id: str,
        file_id: str,
        max_size: tuple = (300, 300)
    ) -> Optional[str]:
        """
        Generate thumbnail for image files.
        
        Args:
            file_content: Original file content
            file_type: MIME type
            org_id: Organization ID
            project_id: Project ID
            file_id: File ID
            max_size: Maximum thumbnail dimensions
            
        Returns:
            Thumbnail URL or None if not applicable
        """
        if not file_type.startswith('image/'):
            return None
        
        try:
            image = Image.open(io.BytesIO(file_content))
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            thumbnail_buffer = io.BytesIO()
            image_format = image.format or 'PNG'
            image.save(thumbnail_buffer, format=image_format)
            thumbnail_content = thumbnail_buffer.getvalue()
            
            thumbnail_filename = f"thumbnail_{file_id}.{image_format.lower()}"
            thumbnail_path = f"organizations/{org_id}/projects/{project_id}/thumbnails/{thumbnail_filename}"
            
            if self.use_local:
                return self._upload_local(thumbnail_content, thumbnail_path)
            else:
                return self._upload_s3(thumbnail_content, thumbnail_path, file_type)
        except Exception as e:
            print(f"Failed to generate thumbnail: {str(e)}")
            return None


file_storage_service = FileStorageService()
