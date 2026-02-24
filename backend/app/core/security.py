"""Security module for dependency injection and access control"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Optional
from app.core.auth import verify_token
from app.db.database import get_db
from app.db.models import User
from sqlalchemy.orm import Session

security = HTTPBearer()


async def get_current_user(
    credentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from request
        db: Database session
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.lower() if user.role else None,  # Normalize to lowercase for consistent checks
        "fname": user.fname,
        "lname": user.lname
    }


from fastapi import Request, Query

async def get_current_user_from_token_or_query(
    request: Request,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get current authenticated user from JWT token (header or query param).
    This is used for file viewing endpoints where browser opens in new tab.
    
    Args:
        request: FastAPI request object
        token: Optional token from query parameter
        db: Database session
        
    Returns:
        User information dictionary
    """
    auth_token = None
    
    # First try to get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        auth_token = auth_header.split(" ")[1]
    
    # Fall back to query parameter
    if not auth_token and token:
        auth_token = token
    
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_token(auth_token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.lower() if user.role else None,  # Normalize to lowercase
        "fname": user.fname,
        "lname": user.lname
    }


async def get_current_user_optional(
    credentials: Optional[HTTPBearer] = Depends(security)
) -> Optional[dict]:
    """
    Get current user if authenticated, otherwise return None.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        User info if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        return None
    
    return payload.get("sub")
