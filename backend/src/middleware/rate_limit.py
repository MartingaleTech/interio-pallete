import time
from typing import Dict, Tuple
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.utils.errors import RateLimitError
from src.middleware.request_id import get_request_id


class RateLimiter:
    """
    Simple in-memory rate limiter using token bucket algorithm.
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60
        self.buckets: Dict[str, Tuple[int, float]] = {}
    
    def is_allowed(self, key: str) -> bool:
        """
        Check if a request is allowed based on rate limit.
        
        Args:
            key: Unique identifier for the client (e.g., user_id or IP)
        
        Returns:
            True if request is allowed, False otherwise
        """
        current_time = time.time()
        
        if key not in self.buckets:
            self.buckets[key] = (1, current_time)
            return True
        
        count, start_time = self.buckets[key]
        
        if current_time - start_time >= self.window_size:
            self.buckets[key] = (1, current_time)
            return True
        
        if count < self.requests_per_minute:
            self.buckets[key] = (count + 1, start_time)
            return True
        
        return False
    
    def cleanup_old_entries(self):
        """Remove old entries from the buckets to prevent memory leaks"""
        current_time = time.time()
        keys_to_remove = [
            key for key, (_, start_time) in self.buckets.items()
            if current_time - start_time >= self.window_size * 2
        ]
        for key in keys_to_remove:
            del self.buckets[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting on API requests.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.cleanup_counter = 0
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            user_id = getattr(request.state, "user_id", None)
            client_ip = request.client.host if request.client else "unknown"
            
            rate_limit_key = user_id if user_id else client_ip
            
            if not self.rate_limiter.is_allowed(rate_limit_key):
                request_id = get_request_id(request)
                raise RateLimitError(
                    message="Too many requests. Please try again later.",
                    request_id=request_id
                )
            
            self.cleanup_counter += 1
            if self.cleanup_counter >= 1000:
                self.rate_limiter.cleanup_old_entries()
                self.cleanup_counter = 0
        
        response = await call_next(request)
        return response
