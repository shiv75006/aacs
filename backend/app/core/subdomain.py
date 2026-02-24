"""Subdomain detection middleware for journal-specific routing"""
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional

logger = logging.getLogger(__name__)


class SubdomainMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract journal context from subdomain.
    
    Extracts the subdomain from requests like 'ijest.aacsjournals.com'
    and stores the journal short_form in request.state for use by endpoints.
    """
    
    # Subdomains that should not be treated as journal identifiers
    EXCLUDED_SUBDOMAINS = {"www", "api", "admin", "static", "mail", "smtp", "ftp"}
    
    # Base domain for the application
    BASE_DOMAIN = "aacsjournals.com"
    
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "").lower()
        
        # Extract subdomain
        subdomain = self._extract_subdomain(host)
        
        # Store in request state for use by endpoints
        request.state.subdomain = subdomain
        request.state.journal_short_form = subdomain
        
        if subdomain:
            logger.debug(f"Detected journal subdomain: {subdomain}")
        
        response = await call_next(request)
        return response
    
    def _extract_subdomain(self, host: str) -> Optional[str]:
        """
        Extract subdomain from host header.
        
        Examples:
            - ijest.aacsjournals.com -> 'ijest'
            - www.aacsjournals.com -> None
            - aacsjournals.com -> None
            - localhost -> None
            - localhost:5173 -> None (check for dev query param handled in frontend)
        """
        # Remove port if present
        host = host.split(":")[0]
        
        # Check if this is the base domain
        if self.BASE_DOMAIN not in host:
            return None
        
        # Extract the part before the base domain
        prefix = host.replace(self.BASE_DOMAIN, "").rstrip(".")
        
        if not prefix:
            return None
        
        # Get the subdomain (last part of prefix)
        parts = prefix.split(".")
        subdomain = parts[-1] if parts else None
        
        # Exclude reserved subdomains
        if subdomain and subdomain.lower() in self.EXCLUDED_SUBDOMAINS:
            return None
        
        return subdomain.lower() if subdomain else None


def get_subdomain(request: Request) -> Optional[str]:
    """
    Helper function to get subdomain from request state.
    Use as a dependency in FastAPI endpoints.
    
    Usage:
        @router.get("/endpoint")
        async def endpoint(subdomain: str = Depends(get_subdomain)):
            if subdomain:
                # Handle journal-specific logic
                pass
    """
    return getattr(request.state, "subdomain", None)


def get_journal_short_form(request: Request) -> Optional[str]:
    """
    Alias for get_subdomain - returns the journal short_form from subdomain.
    """
    return getattr(request.state, "journal_short_form", None)
