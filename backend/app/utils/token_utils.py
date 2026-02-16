"""Token generation and validation utilities"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple


def generate_invitation_token(length: int = 32) -> str:
    """
    Generate a secure random token for invitations.
    
    Args:
        length: Length of the token to generate
        
    Returns:
        Random token string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_magic_link(base_url: str, token: str, token_type: str = "review") -> str:
    """
    Generate a magic link for invitation acceptance/decline.
    
    Args:
        base_url: Base URL of the application (e.g., https://app.example.com)
        token: The invitation token
        token_type: Type of token (review, submission, etc.)
        
    Returns:
        Full magic link URL
    """
    return f"{base_url}/invitations/{token_type}/{token}"


def create_invitation_token_pair() -> Tuple[str, str, datetime]:
    """
    Create a token pair for accept/decline links.
    
    Returns:
        Tuple of (primary_token, expiry_datetime, created_datetime)
    """
    token = generate_invitation_token()
    expiry = datetime.utcnow() + timedelta(days=14)  # 14 days validity
    created = datetime.utcnow()
    return token, expiry, created


def is_token_expired(expiry_date: datetime) -> bool:
    """
    Check if a token has expired.
    
    Args:
        expiry_date: Expiry datetime of the token
        
    Returns:
        True if token is expired, False otherwise
    """
    return datetime.utcnow() > expiry_date
