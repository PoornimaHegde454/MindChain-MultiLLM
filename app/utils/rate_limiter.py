"""
Rate limiting utilities for MultiLLM Router
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
)

def get_rate_limit_exceeded_handler():
    """Get rate limit exceeded handler"""
    return _rate_limit_exceeded_handler

def get_rate_limit_middleware():
    """Get rate limit middleware for FastAPI"""
    return limiter

