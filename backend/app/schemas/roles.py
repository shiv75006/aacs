"""Pydantic schemas for role management"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RoleType(str, Enum):
    """Available roles in the system"""
    AUTHOR = "author"
    REVIEWER = "reviewer"
    EDITOR = "editor"
    ADMIN = "admin"


class RoleStatus(str, Enum):
    """Status of a role assignment"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class RoleRequestCreate(BaseModel):
    """Schema for creating a new role request"""
    requested_role: RoleType = Field(..., description="The role being requested")
    reason: Optional[str] = Field(None, max_length=1000, description="Reason for requesting this role")


class RoleRequestProcess(BaseModel):
    """Schema for processing (approve/reject) a role request"""
    action: str = Field(..., pattern="^(approve|reject)$", description="Action to take: 'approve' or 'reject'")
    admin_notes: Optional[str] = Field(None, max_length=500, description="Notes from admin")
    journal_id: Optional[int] = Field(None, description="Journal ID to assign (for editor role)")


class SwitchRoleRequest(BaseModel):
    """Schema for switching active role"""
    role: RoleType = Field(..., description="The role to switch to")


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class UserRoleResponse(BaseModel):
    """Schema for a user's role"""
    id: int
    role: str
    status: str
    requested_at: Optional[datetime]
    approved_at: Optional[datetime]
    journal_id: Optional[int] = None
    journal_name: Optional[str] = None  # Populated when returning

    class Config:
        from_attributes = True


class RoleRequestResponse(BaseModel):
    """Schema for a role request"""
    id: int
    user_id: int
    requested_role: str
    status: str
    reason: Optional[str]
    requested_at: datetime
    processed_by: Optional[int]
    processed_at: Optional[datetime]
    admin_notes: Optional[str]
    # User info (populated in response)
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True


class MyRolesResponse(BaseModel):
    """Schema for user's current roles and pending requests"""
    user_id: int
    user_email: str
    active_role: str
    approved_roles: List[UserRoleResponse]
    pending_requests: List[RoleRequestResponse]
    available_roles: List[str]  # Roles the user can still request


class RoleRequestListResponse(BaseModel):
    """Schema for admin role request list"""
    total: int
    pending: int
    requests: List[RoleRequestResponse]


class RoleSwitchResponse(BaseModel):
    """Response after switching roles"""
    success: bool
    active_role: str
    message: str
