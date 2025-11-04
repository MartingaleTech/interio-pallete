import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add a unique request ID to each request.
    The request ID is added to the response headers and can be used for debugging.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        
        request.state.request_id = request_id
        
        response = await call_next(request)
        
        response.headers["X-Request-ID"] = request_id
        
        return response


def get_request_id(request: Request) -> str:
    """Get the request ID from the request state"""
    return getattr(request.state, "request_id", None)
