"""Rate limiting configuration for Breakthrough Publishers API"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from app.core.auth import verify_token


# Initialize limiter with in-memory storage
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri="memory://"
)


def get_rate_limit_key(request: Request) -> str:
    """
    Custom key function for rate limiting that considers authenticated users separately.
    
    Args:
        request: FastAPI request object
        
    Returns:
        String key for rate limiting (IP:user_id or just IP for unauthenticated)
    """
    remote_address = get_remote_address(request)
    
    # Try to extract user from JWT token in Authorization header
    try:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            payload = verify_token(token)
            user_id = payload.get("sub") if payload else None
            if user_id:
                return f"{remote_address}:{user_id}"
    except Exception:
        pass
    
    return remote_address


# Rate limit definitions for different endpoint categories
RATE_LIMITS = {
    # Authentication endpoints - strict limits
    "auth_login": "5/minute",
    "auth_signup": "5/minute",
    "auth_refresh": "10/minute",
    
    # Public endpoints - moderate limits
    "public_list_journals": "50/minute",
    "public_get_journal": "50/minute",
    "public_get_news": "50/minute",
    
    # Paper submission - moderate limits
    "paper_submit": "20/minute",
    "paper_list": "50/minute",
    
    # Author operations
    "author_papers": "30/minute",
    "author_paper_detail": "30/minute",
    
    # Reviewer operations
    "reviewer_papers": "30/minute",
    "reviewer_submit_review": "10/minute",
    
    # Editor operations - admin friendly
    "editor_dashboard": "100/minute",
    "editor_paper_queue": "100/minute",
    "editor_reviewers": "100/minute",
    "editor_assign_reviewer": "20/minute",
    "editor_update_status": "20/minute",
    "editor_pending_decision": "100/minute",
    
    # Admin operations - generous limits
    "admin_dashboard": "200/minute",
    "admin_list_all": "200/minute",
    "admin_user_management": "100/minute",
    "admin_journal_management": "100/minute",
}


# Bypass rate limiting for admin/editor in development
BYPASS_RATE_LIMIT_ROLES = []  # Set to ["admin", "editor"] to bypass during dev


rate_limit_error_message = (
    "Rate limit exceeded. Please wait before making another request. "
    "Limit: {limit}. Remaining: {remaining}. Reset: {reset}"
)
