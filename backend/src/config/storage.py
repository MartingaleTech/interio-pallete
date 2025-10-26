import os
from typing import Optional


class StorageConfig:
    """Configuration for cloud storage (S3 or compatible services)."""
    
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "interio-palette-files")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    S3_ACCESS_KEY: Optional[str] = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = os.getenv("S3_SECRET_KEY")
    S3_ENDPOINT_URL: Optional[str] = os.getenv("S3_ENDPOINT_URL")
    
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(100 * 1024 * 1024)))
    
    ALLOWED_FILE_TYPES = {
        "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
        "application/pdf",
        "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "model/obj", "model/fbx", "application/octet-stream",
        "application/zip", "application/x-rar-compressed",
        "text/plain", "text/csv",
        "application/dwg", "application/dxf"
    }
    
    ALLOWED_EXTENSIONS = {
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg",
        ".pdf",
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".obj", ".fbx", ".skp", ".stl", ".gltf", ".glb",
        ".dwg", ".dxf",
        ".zip", ".rar",
        ".txt", ".csv"
    }
    
    USE_LOCAL_STORAGE: bool = os.getenv("USE_LOCAL_STORAGE", "true").lower() == "true"
    LOCAL_STORAGE_PATH: str = os.getenv("LOCAL_STORAGE_PATH", "/tmp/interio-palette-files")


storage_config = StorageConfig()
