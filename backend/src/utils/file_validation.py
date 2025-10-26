import os
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException
from src.config.storage import storage_config


def validate_file_size(file_size: int) -> bool:
    """
    Validate file size against maximum allowed size.
    
    Args:
        file_size: File size in bytes
        
    Returns:
        True if valid, False otherwise
    """
    return file_size <= storage_config.MAX_FILE_SIZE


def validate_file_type(filename: str, content_type: str) -> bool:
    """
    Validate file type based on extension and MIME type.
    
    Args:
        filename: Original filename
        content_type: MIME type
        
    Returns:
        True if valid, False otherwise
    """
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext not in storage_config.ALLOWED_EXTENSIONS:
        return False
    
    if content_type and content_type not in storage_config.ALLOWED_FILE_TYPES:
        if not content_type.startswith('application/octet-stream'):
            return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other security issues.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    filename = os.path.basename(filename)
    filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
    filename = filename.strip()
    
    if not filename:
        filename = "unnamed_file"
    
    return filename[:255]


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Filename
        
    Returns:
        File extension (including dot)
    """
    return os.path.splitext(filename)[1].lower()


def validate_upload_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file for size and type.
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file.filename:
        return False, "Filename is required"
    
    if not validate_file_type(file.filename, file.content_type or ""):
        return False, f"File type not allowed. Allowed extensions: {', '.join(storage_config.ALLOWED_EXTENSIONS)}"
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if not validate_file_size(file_size):
        max_size_mb = storage_config.MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File size exceeds maximum allowed size of {max_size_mb}MB"
    
    return True, None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def is_image_file(content_type: str) -> bool:
    """
    Check if file is an image based on content type.
    
    Args:
        content_type: MIME type
        
    Returns:
        True if image, False otherwise
    """
    return content_type.startswith('image/')


def is_pdf_file(content_type: str) -> bool:
    """
    Check if file is a PDF based on content type.
    
    Args:
        content_type: MIME type
        
    Returns:
        True if PDF, False otherwise
    """
    return content_type == 'application/pdf'


def is_3d_model_file(filename: str) -> bool:
    """
    Check if file is a 3D model based on extension.
    
    Args:
        filename: Filename
        
    Returns:
        True if 3D model, False otherwise
    """
    ext = get_file_extension(filename)
    return ext in ['.obj', '.fbx', '.skp', '.stl', '.gltf', '.glb']
