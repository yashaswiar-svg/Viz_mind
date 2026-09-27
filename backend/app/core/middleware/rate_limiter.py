import time
from typing import Dict, List, Tuple
from fastapi import HTTPException, Request, status
from app.core.config import settings


class RateLimiter:
    """In-memory rate limiter for single-instance local deployment protection."""

    def __init__(self, requests_limit: int = 100, window_seconds: int = 60):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.client_requests: Dict[str, List[float]] = {}

    def is_rate_limited(self, client_ip: str) -> bool:
        if not settings.RATE_LIMIT_ENABLED:
            return False

        now = time.time()
        cutoff = now - self.window_seconds

        history = self.client_requests.get(client_ip, [])
        valid_history = [t for t in history if t > cutoff]

        if len(valid_history) >= self.requests_limit:
            self.client_requests[client_ip] = valid_history
            return True

        valid_history.append(now)
        self.client_requests[client_ip] = valid_history
        return False


rate_limiter = RateLimiter(
    requests_limit=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
)


async def check_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                }
            },
            headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW_SECONDS)},
        )
