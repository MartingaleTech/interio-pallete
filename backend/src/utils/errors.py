from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from fastapi import HTTPException, status


class ErrorDetail(BaseModel):
    """Detailed error information"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response format"""
    error: str
    message: str
    request_id: Optional[str] = None
    details: Optional[List[ErrorDetail]] = None
    status_code: int


class APIError(HTTPException):
    """Base API error with standardized format"""
    
    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        details: Optional[List[ErrorDetail]] = None,
        request_id: Optional[str] = None
    ):
        self.error = error
        self.message = message
        self.details = details
        self.request_id = request_id
        super().__init__(status_code=status_code, detail=message)


class BadRequestError(APIError):
    """400 Bad Request"""
    def __init__(self, message: str, details: Optional[List[ErrorDetail]] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="BAD_REQUEST",
            message=message,
            details=details,
            request_id=request_id
        )


class UnauthorizedError(APIError):
    """401 Unauthorized"""
    def __init__(self, message: str = "Authentication required", request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="UNAUTHORIZED",
            message=message,
            request_id=request_id
        )


class ForbiddenError(APIError):
    """403 Forbidden"""
    def __init__(self, message: str = "Access forbidden", request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error="FORBIDDEN",
            message=message,
            request_id=request_id
        )


class NotFoundError(APIError):
    """404 Not Found"""
    def __init__(self, message: str, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error="NOT_FOUND",
            message=message,
            request_id=request_id
        )


class ConflictError(APIError):
    """409 Conflict"""
    def __init__(self, message: str, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error="CONFLICT",
            message=message,
            request_id=request_id
        )


class ValidationError(APIError):
    """422 Validation Error"""
    def __init__(self, message: str, details: Optional[List[ErrorDetail]] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error="VALIDATION_ERROR",
            message=message,
            details=details,
            request_id=request_id
        )


class RateLimitError(APIError):
    """429 Too Many Requests"""
    def __init__(self, message: str = "Rate limit exceeded", request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error="RATE_LIMIT_EXCEEDED",
            message=message,
            request_id=request_id
        )


class InternalServerError(APIError):
    """500 Internal Server Error"""
    def __init__(self, message: str = "Internal server error", request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="INTERNAL_SERVER_ERROR",
            message=message,
            request_id=request_id
        )
