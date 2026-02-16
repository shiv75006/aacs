"""Pydantic schemas for user-related requests and responses"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    """User login request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }


class SignupRequest(BaseModel):
    """User signup request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    confirm_password: str = Field(..., min_length=8, description="Confirm password")
    fname: str = Field(..., min_length=1, max_length=100, description="First name")
    lname: str = Field(..., min_length=1, max_length=100, description="Last name")
    mname: Optional[str] = Field(None, max_length=100, description="Middle name")
    title: Optional[str] = Field(None, max_length=100, description="Title/Designation")
    affiliation: Optional[str] = Field(None, max_length=255, description="Affiliation/Organization")
    specialization: Optional[str] = Field(None, description="Specialization/Research area")
    contact: Optional[str] = Field(None, max_length=20, description="Contact number")
    address: Optional[str] = Field(None, description="Address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "author@example.com",
                "password": "securepass123",
                "confirm_password": "securepass123",
                "fname": "John",
                "lname": "Doe",
                "mname": "M",
                "title": "Dr.",
                "affiliation": "University of Example",
                "specialization": "Computer Science"
            }
        }


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    id: Optional[int] = Field(None, description="User ID")
    email: Optional[str] = Field(None, description="User email")
    role: Optional[str] = Field(None, description="User role")
    fname: Optional[str] = Field(None, description="First name")
    lname: Optional[str] = Field(None, description="Last name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "id": 1,
                "email": "user@example.com",
                "role": "author",
                "fname": "John",
                "lname": "Doe"
            }
        }


class UserResponse(BaseModel):
    """User response schema"""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    role: Optional[str] = Field(None, description="User role")
    fname: Optional[str] = Field(None, description="First name")
    lname: Optional[str] = Field(None, description="Last name")
    mname: Optional[str] = Field(None, description="Middle name")
    title: Optional[str] = Field(None, description="Title/Designation")
    affiliation: Optional[str] = Field(None, description="Affiliation")
    specialization: Optional[str] = Field(None, description="Specialization")
    contact: Optional[str] = Field(None, description="Contact number")
    address: Optional[str] = Field(None, description="Address")
    added_on: Optional[datetime] = Field(None, description="Registration date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "role": "author",
                "fname": "John",
                "lname": "Doe"
            }
        }


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 chars)")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class UserUpdate(BaseModel):
    """User update request schema"""
    fname: Optional[str] = Field(None, max_length=100, description="First name")
    lname: Optional[str] = Field(None, max_length=100, description="Last name")
    mname: Optional[str] = Field(None, max_length=100, description="Middle name")
    title: Optional[str] = Field(None, max_length=100, description="Title/Designation")
    affiliation: Optional[str] = Field(None, max_length=255, description="Affiliation/Organization")
    specialization: Optional[str] = Field(None, description="Specialization/Research area")
    contact: Optional[str] = Field(None, max_length=20, description="Contact number")
    address: Optional[str] = Field(None, description="Address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fname": "John",
                "lname": "Doe",
                "title": "Dr.",
                "affiliation": "University of Example"
            }
        }
