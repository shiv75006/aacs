"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.database import get_db
from app.db.models import User
from app.schemas.user import (
    UserLogin, SignupRequest, TokenResponse, UserResponse, 
    PasswordChangeRequest, RefreshTokenRequest
)
from app.core.auth import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, verify_token
)
from app.core.security import get_current_user
from app.core.rate_limit import limiter
from app.utils.exceptions import (
    InvalidCredentialsException, UserNotFoundException,
    PasswordMismatchException
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """
    User login endpoint.
    
    Authenticates user with email and password, returns JWT tokens.
    
    Args:
        credentials: User login credentials (email, password)
        db: Database session
        
    Returns:
        TokenResponse with access_token, refresh_token, and expiration
        
    Raises:
        InvalidCredentialsException: If email or password is incorrect
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise InvalidCredentialsException()
    
    # Verify password
    if not verify_password(credentials.password, user.password):
        raise InvalidCredentialsException()
    
    # Create tokens
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=86400,  # 24 hours in seconds
        id=user.id,
        email=user.email,
        role=user.role,
        fname=user.fname,
        lname=user.lname
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def signup(request: Request, data: SignupRequest, db: Session = Depends(get_db)):
    """
    User signup endpoint.
    
    Creates a new user account with email and password, returns JWT tokens.
    
    Args:
        data: User signup data including email, password, name, and optional fields
        db: Database session
        
    Returns:
        TokenResponse with access_token, refresh_token, and expiration
        
    Raises:
        HTTPException: If email already exists or passwords don't match
    """
    # Validate passwords match
    if data.password != data.confirm_password:
        raise PasswordMismatchException()
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {data.email} is already registered"
        )
    
    # Create new user with hashed password
    new_user = User(
        email=data.email,
        password=hash_password(data.password),
        fname=data.fname,
        lname=data.lname,
        mname=data.mname or "",  # Default to empty string if not provided (DB doesn't allow NULL)
        title=data.title or "",  # Default to empty string if not provided (DB doesn't allow NULL)
        affiliation=data.affiliation,
        specialization=data.specialization,
        contact=data.contact,
        address=data.address,
        role="author"  # Default role for new users
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create tokens for newly registered user
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(new_user.id), "email": new_user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=86400,  # 24 hours in seconds
        id=new_user.id,
        email=new_user.email,
        role=new_user.role,
        fname=new_user.fname,
        lname=new_user.lname
    )


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def refresh_token(http_request: Request, request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token endpoint.
    
    Uses refresh token to generate a new access token.
    
    Args:
        request: RefreshTokenRequest with refresh_token
        db: Database session
        
    Returns:
        TokenResponse with new access_token
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    payload = verify_token(request.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user:
        raise UserNotFoundException()
    
    # Create new access token
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # Return same refresh token
        token_type="bearer",
        expires_in=86400
    )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user from JWT token
        db: Database session
        
    Returns:
        UserResponse with user information
        
    Raises:
        UserNotFoundException: If user not found
    """
    user = db.query(User).filter(User.id == current_user["id"]).first()
    
    if not user:
        raise UserNotFoundException()
    
    return UserResponse(**user.to_dict())


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password endpoint.
    
    Allows authenticated user to change their password.
    
    Args:
        request: PasswordChangeRequest with current and new passwords
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        InvalidCredentialsException: If current password is incorrect
        PasswordMismatchException: If new passwords don't match
    """
    # Validate new passwords match
    if request.new_password != request.confirm_password:
        raise PasswordMismatchException()
    
    # Get user from database
    user = db.query(User).filter(User.id == current_user["id"]).first()
    
    if not user:
        raise UserNotFoundException()
    
    # Verify current password
    if not verify_password(request.current_password, user.password):
        raise InvalidCredentialsException("Current password is incorrect")
    
    # Update password with hash
    user.password = hash_password(request.new_password)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Password changed successfully",
        "status": "success"
    }
