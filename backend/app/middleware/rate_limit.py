"""Monthly request rate limiter to stay within free tier."""
import os
import json
from datetime import datetime
from pathlib import Path
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class MonthlyRequestLimiter(BaseHTTPMiddleware):
    """Middleware to enforce monthly request limits."""
    
    # Google Cloud Run free tier limit
    FREE_TIER_LIMIT = 2_000_000
    COUNTER_FILE = "/tmp/request_counter.json"
    
    def __init__(self, app, max_requests: int = FREE_TIER_LIMIT):
        super().__init__(app)
        self.max_requests = max_requests
        self._ensure_counter_file()
    
    def _ensure_counter_file(self):
        """Ensure counter file exists."""
        if not os.path.exists(self.COUNTER_FILE):
            self._reset_counter()
    
    def _get_current_month(self) -> str:
        """Get current month as YYYY-MM string."""
        return datetime.utcnow().strftime("%Y-%m")
    
    def _read_counter(self) -> dict:
        """Read request counter from file."""
        try:
            with open(self.COUNTER_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._reset_counter()
    
    def _reset_counter(self) -> dict:
        """Reset counter for new month."""
        data = {
            "month": self._get_current_month(),
            "count": 0
        }
        self._write_counter(data)
        return data
    
    def _write_counter(self, data: dict):
        """Write counter to file."""
        os.makedirs(os.path.dirname(self.COUNTER_FILE), exist_ok=True)
        with open(self.COUNTER_FILE, 'w') as f:
            json.dump(data, f)
    
    def _increment_counter(self) -> int:
        """Increment and return current request count."""
        data = self._read_counter()
        current_month = self._get_current_month()
        
        # Reset if new month
        if data.get("month") != current_month:
            data = self._reset_counter()
        
        data["count"] += 1
        self._write_counter(data)
        return data["count"]
    
    async def dispatch(self, request: Request, call_next):
        """Process request and enforce rate limit."""
        # Skip rate limiting for health checks
        if request.url.path in ["/", "/health", "/api/v1/health"]:
            return await call_next(request)
        
        # Check and increment counter
        current_count = self._increment_counter()
        
        # Calculate remaining requests
        remaining = self.max_requests - current_count
        
        # Add rate limit headers
        response = None
        if current_count > self.max_requests:
            # Exceeded free tier limit
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Monthly request limit exceeded",
                    "message": f"Free tier limit of {self.max_requests:,} requests per month has been reached. Please try again next month.",
                    "limit": self.max_requests,
                    "current": current_count,
                    "reset_date": f"{self._get_current_month()}-01"
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit info to response headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Used"] = str(current_count)
        
        # Warning when approaching limit
        if remaining < 100000:  # Less than 100k requests remaining
            response.headers["X-RateLimit-Warning"] = f"Approaching monthly limit. {remaining:,} requests remaining."
        
        return response
