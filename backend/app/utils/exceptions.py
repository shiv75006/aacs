"""Custom exception classes"""
from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    """Raised when login credentials are invalid"""
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFoundException(HTTPException):
    """Raised when user is not found"""
    def __init__(self, detail: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class TokenExpiredException(HTTPException):
    """Raised when token is expired"""
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PasswordMismatchException(HTTPException):
    """Raised when passwords don't match"""
    def __init__(self, detail: str = "Passwords do not match"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
