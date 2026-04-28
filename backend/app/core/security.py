"""
Security middleware and authentication utilities.
Handles Firebase token verification, role-based access control,
rate limiting, and request validation.
"""
from fastapi import HTTPException, Security, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import structlog
import time
from collections import defaultdict

from .supabase import verify_supabase_token, get_supabase_client
from .config import get_settings

logger = structlog.get_logger(__name__)
security_scheme = HTTPBearer(auto_error=False)

# ── In-memory rate limiter (use Redis in production) ────────────
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


class RateLimiter:
    """Token bucket rate limiter per client IP."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_rate_limited(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        # Clean old entries
        _rate_limit_store[client_ip] = [
            t for t in _rate_limit_store[client_ip] if t > window_start
        ]
        if len(_rate_limit_store[client_ip]) >= self.max_requests:
            return True
        _rate_limit_store[client_ip].append(now)
        return False


rate_limiter = RateLimiter()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
) -> dict:
    """
    Extract and verify the current user from Firebase ID token.
    Returns user claims dict with uid, email, role, etc.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide a valid Firebase ID token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        decoded = await verify_supabase_token(credentials.credentials)
        return decoded
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(allowed_roles: list[str]):
    """
    Role-based access control decorator.
    Usage: Depends(require_role(["admin", "ngo_manager"]))
    """
    async def role_checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in allowed_roles:
            logger.warning(
                "unauthorized_role_access",
                uid=user.get("uid"),
                role=user.get("role"),
                required=allowed_roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )
        return user

    return role_checker


async def rate_limit_middleware(request: Request):
    """Check rate limits for incoming requests."""
    client_ip = request.client.host if request.client else "unknown"
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )
