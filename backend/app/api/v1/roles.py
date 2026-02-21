"""Role Management API endpoints"""
from fastapi import APIRouter, Depends, status, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
from app.db.database import get_db
from app.db.models import User, UserRole, RoleRequest, Journal
from app.core.security import get_current_user
from app.core.rate_limit import limiter
from app.utils.auth_helpers import check_role
from app.schemas.roles import (
    RoleRequestCreate, RoleRequestProcess, SwitchRoleRequest,
    UserRoleResponse, RoleRequestResponse, MyRolesResponse,
    RoleRequestListResponse, RoleSwitchResponse, RoleType, RoleStatus
)
from typing import List

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])

# Available roles that users can request
REQUESTABLE_ROLES = ["author", "reviewer", "editor"]
ALL_ROLES = ["author", "reviewer", "editor", "admin"]


# ============================================================================
# USER ENDPOINTS - Role Management for Current User
# ============================================================================

@router.get("/my-roles", response_model=MyRolesResponse)
@limiter.limit("100/minute")
async def get_my_roles(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's roles, pending requests, and available roles to request.
    
    Returns:
        - approved_roles: List of roles the user has
        - pending_requests: List of pending role requests
        - available_roles: Roles the user can still request
        - active_role: User's currently active role (from legacy field or first approved)
    """
    user_id = current_user.get("id")
    
    # Get approved roles
    approved_roles = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.status == "approved"
    ).all()
    
    # Get pending requests
    pending_requests = db.query(RoleRequest).filter(
        RoleRequest.user_id == user_id,
        RoleRequest.status == "pending"
    ).order_by(desc(RoleRequest.requested_at)).all()
    
    # Build approved roles response with journal info
    approved_list = []
    approved_role_names = set()
    for ur in approved_roles:
        role_data = {
            "id": ur.id,
            "role": ur.role,
            "status": ur.status,
            "requested_at": ur.requested_at,
            "approved_at": ur.approved_at,
            "journal_id": ur.journal_id,
            "journal_name": None
        }
        if ur.journal_id:
            journal = db.query(Journal).filter(Journal.fld_id == ur.journal_id).first()
            if journal:
                role_data["journal_name"] = journal.fld_journal_name
        approved_list.append(UserRoleResponse(**role_data))
        approved_role_names.add(ur.role.lower())
    
    # Build pending requests response
    pending_list = []
    pending_role_names = set()
    for pr in pending_requests:
        pending_list.append(RoleRequestResponse(
            id=pr.id,
            user_id=pr.user_id,
            requested_role=pr.requested_role,
            status=pr.status,
            reason=pr.reason,
            requested_at=pr.requested_at,
            processed_by=pr.processed_by,
            processed_at=pr.processed_at,
            admin_notes=pr.admin_notes
        ))
        pending_role_names.add(pr.requested_role.lower())
    
    # Calculate available roles (not approved and not pending)
    available_roles = [
        role for role in REQUESTABLE_ROLES
        if role.lower() not in approved_role_names and role.lower() not in pending_role_names
    ]
    
    # Determine active role - use legacy role field or first approved role
    active_role = current_user.get("role", "").lower()
    if not active_role or active_role == "user":
        active_role = approved_list[0].role if approved_list else "user"
    
    return MyRolesResponse(
        user_id=user_id,
        user_email=current_user.get("email"),
        active_role=active_role,
        approved_roles=approved_list,
        pending_requests=pending_list,
        available_roles=available_roles
    )


@router.post("/request", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def request_role(
    request: Request,
    role_request: RoleRequestCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request access to a new role.
    
    Users can request author, reviewer, or editor roles.
    Requests go to admin for approval.
    """
    user_id = current_user.get("id")
    requested_role = role_request.requested_role.value.lower()
    
    # Validate role is requestable
    if requested_role not in REQUESTABLE_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot request '{requested_role}' role. Requestable roles: {REQUESTABLE_ROLES}"
        )
    
    # Check if user already has this role
    existing_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        func.lower(UserRole.role) == requested_role,
        UserRole.status == "approved"
    ).first()
    
    if existing_role:
        raise HTTPException(
            status_code=400,
            detail=f"You already have the '{requested_role}' role"
        )
    
    # Check if there's already a pending request for this role
    pending_request = db.query(RoleRequest).filter(
        RoleRequest.user_id == user_id,
        func.lower(RoleRequest.requested_role) == requested_role,
        RoleRequest.status == "pending"
    ).first()
    
    if pending_request:
        raise HTTPException(
            status_code=400,
            detail=f"You already have a pending request for the '{requested_role}' role"
        )
    
    # Create new role request
    new_request = RoleRequest(
        user_id=user_id,
        requested_role=requested_role,
        reason=role_request.reason,
        status="pending",
        requested_at=datetime.utcnow()
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return {
        "message": f"Role request for '{requested_role}' submitted successfully",
        "request_id": new_request.id,
        "status": "pending"
    }


@router.post("/switch", response_model=RoleSwitchResponse)
@limiter.limit("60/minute")
async def switch_active_role(
    request: Request,
    switch_request: SwitchRoleRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Switch the user's active role/persona.
    
    User can only switch to roles they have approved access to.
    Updates the legacy role field for compatibility.
    """
    user_id = current_user.get("id")
    target_role = switch_request.role.value.lower()
    
    # Check if user has this role approved
    has_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        func.lower(UserRole.role) == target_role,
        UserRole.status == "approved"
    ).first()
    
    # Admin check - admin role from legacy field
    is_admin = current_user.get("role", "").lower() == "admin"
    
    if not has_role and not is_admin:
        raise HTTPException(
            status_code=403,
            detail=f"You don't have the '{target_role}' role. Request access first."
        )
    
    # Update the legacy role field for backward compatibility
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # Capitalize first letter for consistency
        user.role = target_role.capitalize()
        db.commit()
    
    return RoleSwitchResponse(
        success=True,
        active_role=target_role,
        message=f"Successfully switched to {target_role} role"
    )


# ============================================================================
# ADMIN ENDPOINTS - Role Request Management
# ============================================================================

@router.get("/requests", response_model=RoleRequestListResponse)
@limiter.limit("100/minute")
async def list_role_requests(
    request: Request,
    status_filter: str = Query(None, description="Filter by status: pending, approved, rejected"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all role requests (admin only).
    
    Returns role requests with user information for admin review.
    """
    if not check_role(current_user.get("role"), "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Build query
    query = db.query(RoleRequest)
    
    if status_filter:
        query = query.filter(RoleRequest.status == status_filter.lower())
    
    # Get counts
    total = query.count()
    pending_count = db.query(RoleRequest).filter(RoleRequest.status == "pending").count()
    
    # Get requests with pagination
    requests = query.order_by(desc(RoleRequest.requested_at)).offset(skip).limit(limit).all()
    
    # Build response with user info
    request_list = []
    for req in requests:
        user = db.query(User).filter(User.id == req.user_id).first()
        request_list.append(RoleRequestResponse(
            id=req.id,
            user_id=req.user_id,
            requested_role=req.requested_role,
            status=req.status,
            reason=req.reason,
            requested_at=req.requested_at,
            processed_by=req.processed_by,
            processed_at=req.processed_at,
            admin_notes=req.admin_notes,
            user_name=f"{user.fname or ''} {user.lname or ''}".strip() if user else None,
            user_email=user.email if user else None
        ))
    
    return RoleRequestListResponse(
        total=total,
        pending=pending_count,
        requests=request_list
    )


@router.patch("/requests/{request_id}")
@limiter.limit("60/minute")
async def process_role_request(
    request: Request,
    request_id: int,
    process_data: RoleRequestProcess,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve or reject a role request (admin only).
    
    When approved, creates a UserRole entry for the user.
    For editor role, optionally assigns a journal.
    """
    if not check_role(current_user.get("role"), "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get the request
    role_request = db.query(RoleRequest).filter(RoleRequest.id == request_id).first()
    if not role_request:
        raise HTTPException(status_code=404, detail="Role request not found")
    
    if role_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Request already processed with status: {role_request.status}"
        )
    
    admin_id = current_user.get("id")
    action = process_data.action.lower()
    
    if action == "approve":
        # Create UserRole entry
        new_role = UserRole(
            user_id=role_request.user_id,
            role=role_request.requested_role,
            status="approved",
            requested_at=role_request.requested_at,
            approved_by=admin_id,
            approved_at=datetime.utcnow(),
            journal_id=process_data.journal_id if role_request.requested_role == "editor" else None
        )
        db.add(new_role)
        
        # Update request status
        role_request.status = "approved"
        role_request.processed_by = admin_id
        role_request.processed_at = datetime.utcnow()
        role_request.admin_notes = process_data.admin_notes
        
        db.commit()
        
        return {
            "message": f"Role request approved. User now has '{role_request.requested_role}' access.",
            "request_id": request_id,
            "status": "approved"
        }
    
    elif action == "reject":
        role_request.status = "rejected"
        role_request.processed_by = admin_id
        role_request.processed_at = datetime.utcnow()
        role_request.admin_notes = process_data.admin_notes
        
        db.commit()
        
        return {
            "message": "Role request rejected.",
            "request_id": request_id,
            "status": "rejected"
        }


@router.get("/users/{user_id}/roles")
@limiter.limit("100/minute")
async def get_user_roles(
    request: Request,
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all roles for a specific user (admin only).
    """
    if not check_role(current_user.get("role"), "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user roles
    roles = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.status == "approved"
    ).all()
    
    roles_list = []
    for role in roles:
        role_data = role.to_dict()
        if role.journal_id:
            journal = db.query(Journal).filter(Journal.fld_id == role.journal_id).first()
            role_data["journal_name"] = journal.fld_journal_name if journal else None
        roles_list.append(role_data)
    
    return {
        "user_id": user_id,
        "user_name": f"{user.fname or ''} {user.lname or ''}".strip(),
        "user_email": user.email,
        "legacy_role": user.role,
        "roles": roles_list
    }


@router.post("/users/{user_id}/roles")
@limiter.limit("60/minute")
async def assign_role_to_user(
    request: Request,
    user_id: int,
    role: str = Query(..., description="Role to assign: author, reviewer, editor, admin"),
    journal_id: int = Query(None, description="Journal ID for editor role"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Directly assign a role to a user (admin only).
    Bypasses the request workflow for admin-initiated assignments.
    """
    if not check_role(current_user.get("role"), "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    role = role.lower()
    if role not in ALL_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {ALL_ROLES}"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user already has this role
    existing = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        func.lower(UserRole.role) == role,
        UserRole.status == "approved"
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"User already has the '{role}' role"
        )
    
    # Create role assignment
    new_role = UserRole(
        user_id=user_id,
        role=role,
        status="approved",
        requested_at=datetime.utcnow(),
        approved_by=current_user.get("id"),
        approved_at=datetime.utcnow(),
        journal_id=journal_id if role == "editor" else None
    )
    db.add(new_role)
    db.commit()
    
    return {
        "message": f"Role '{role}' assigned to user successfully",
        "user_id": user_id,
        "role": role
    }


@router.delete("/users/{user_id}/roles/{role}")
@limiter.limit("60/minute")
async def revoke_user_role(
    request: Request,
    user_id: int,
    role: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke a role from a user (admin only).
    """
    if not check_role(current_user.get("role"), "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    role = role.lower()
    
    # Find the role assignment
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        func.lower(UserRole.role) == role
    ).first()
    
    if not user_role:
        raise HTTPException(
            status_code=404,
            detail=f"User does not have the '{role}' role"
        )
    
    db.delete(user_role)
    db.commit()
    
    return {
        "message": f"Role '{role}' revoked from user",
        "user_id": user_id,
        "role": role
    }
