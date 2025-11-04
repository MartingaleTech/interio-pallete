import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError as PydanticValidationError
from src.utils.errors import APIError, ErrorResponse, ErrorDetail
from src.middleware.request_id import get_request_id

logger = logging.getLogger(__name__)


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom API errors"""
    request_id = get_request_id(request)
    
    error_response = ErrorResponse(
        error=exc.error,
        message=exc.message,
        request_id=request_id,
        details=exc.details,
        status_code=exc.status_code
    )
    
    logger.error(
        f"API Error: {exc.error} - {exc.message} (Request ID: {request_id})",
        extra={"request_id": request_id, "status_code": exc.status_code}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions"""
    request_id = get_request_id(request)
    
    error_response = ErrorResponse(
        error="HTTP_ERROR",
        message=str(exc.detail),
        request_id=request_id,
        status_code=exc.status_code
    )
    
    logger.error(
        f"HTTP Error: {exc.status_code} - {exc.detail} (Request ID: {request_id})",
        extra={"request_id": request_id, "status_code": exc.status_code}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    request_id = get_request_id(request)
    
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        details.append(ErrorDetail(
            field=field,
            message=error["msg"],
            code=error["type"]
        ))
    
    error_response = ErrorResponse(
        error="VALIDATION_ERROR",
        message="Request validation failed",
        request_id=request_id,
        details=details,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
    
    logger.warning(
        f"Validation Error: {len(details)} validation errors (Request ID: {request_id})",
        extra={"request_id": request_id, "errors": details}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    request_id = get_request_id(request)
    
    error_response = ErrorResponse(
        error="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        request_id=request_id,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    logger.exception(
        f"Unexpected Error: {str(exc)} (Request ID: {request_id})",
        extra={"request_id": request_id},
        exc_info=exc
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )
