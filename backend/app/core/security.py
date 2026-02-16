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
        "role": user.role,
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
