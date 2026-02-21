"""Security and authorization utilities"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional


def check_role(user_role: str, required_role) -> bool:
    """
    Check if user has required role (case-insensitive).
    Uses legacy role field for backward compatibility.
    
    Args:
        user_role: User's actual role from database (legacy field)
        required_role: Required role(s) - can be string or list of strings
        
    Returns:
        True if user role matches required role(s) (case-insensitive)
    """
    if not user_role:
        return False
    
    # Handle list of roles
    if isinstance(required_role, list):
        return any(user_role.lower() == role.lower() for role in required_role)
    
    # Handle single role string
    return user_role.lower() == required_role.lower()


def check_user_has_role(user_id: int, required_role, db: Session) -> bool:
    """
    Check if user has required role in the multi-role system.
    Checks both UserRole table AND legacy role field for backward compatibility.
    
    Args:
        user_id: User's ID
        required_role: Required role(s) - can be string or list of strings
        db: Database session
        
    Returns:
        True if user has any of the required roles
    """
    from app.db.models import User, UserRole
    
    # Normalize required_role to list
    if isinstance(required_role, str):
        required_roles = [required_role.lower()]
    else:
        required_roles = [r.lower() for r in required_role]
    
    # Check legacy role field first
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.role and user.role.lower() in required_roles:
        return True
    
    # Check UserRole table
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        func.lower(UserRole.role).in_(required_roles),
        UserRole.status == "approved"
    ).first()
    
    return user_role is not None


def get_user_roles(user_id: int, db: Session) -> List[str]:
    """
    Get all approved roles for a user.
    Combines legacy role field with UserRole table entries.
    
    Args:
        user_id: User's ID
        db: Database session
        
    Returns:
        List of role names (lowercase) the user has access to
    """
    from app.db.models import User, UserRole
    
    roles = set()
    
    # Get legacy role
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.role and user.role.lower() not in ["user", ""]:
        roles.add(user.role.lower())
    
    # Get roles from UserRole table
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.status == "approved"
    ).all()
    
    for ur in user_roles:
        roles.add(ur.role.lower())
    
    return list(roles)


def role_matches(user_role: str, *required_roles: str) -> bool:
    """
    Check if user role matches any of the provided roles (case-insensitive).
    
    Args:
        user_role: User's actual role from database
        required_roles: One or more roles to check
        
    Returns:
        True if user role matches any of the required roles
    """
    if not user_role:
        return False
    user_role_lower = user_role.lower()
    return user_role_lower in [role.lower() for role in required_roles]


def get_editor_journal_ids(user_email: str, db: Session) -> List[int]:
    """
    Get journal IDs that an editor has access to.
    
    Uses user_role table to find which journal(s) the user
    is assigned to based on their email.
    
    Args:
        user_email: The email address of the logged-in editor
        db: Database session
        
    Returns:
        List of journal IDs the editor has access to.
        Returns empty list if user is not found or has no journal assigned.
    """
    from app.db.models import User, UserRole
    
    # Find user by email
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return []
    
    # Query user_role entries with role='editor' and approved status
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == user.id,
        UserRole.role == "editor",
        UserRole.status == "approved",
        UserRole.journal_id.isnot(None)
    ).all()
    
    journal_ids = [ur.journal_id for ur in user_roles if ur.journal_id is not None]
    return list(set(journal_ids))  # Remove duplicates


def editor_has_journal_access(user_email: str, journal_id: int, db: Session) -> bool:
    """
    Check if an editor has access to a specific journal.
    
    Args:
        user_email: The email address of the logged-in editor
        journal_id: The journal ID to check access for
        db: Database session
        
    Returns:
        True if editor has access to the journal, False otherwise
    """
    allowed_journals = get_editor_journal_ids(user_email, db)
    return journal_id in allowed_journals


def get_editor_journal_info(user_email: str, db: Session) -> List[dict]:
    """
    Get detailed journal information for journals an editor has access to.
    Uses user_role + user tables.
    
    Args:
        user_email: The email address of the logged-in editor
        db: Database session
        
    Returns:
        List of dictionaries with journal_id, journal name, and editor_type
    """
    from app.db.models import User, UserRole, Journal
    
    # Find user by email
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return []
    
    # Query user_role entries with role='editor' and approved status
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == user.id,
        UserRole.role == "editor",
        UserRole.status == "approved",
        UserRole.journal_id.isnot(None)
    ).all()
    
    journals_info = []
    seen_ids = set()
    
    for user_role in user_roles:
        jid = user_role.journal_id
        if jid in seen_ids:
            continue
        seen_ids.add(jid)
        
        journal = db.query(Journal).filter(Journal.fld_id == jid).first()
        if journal:
            journals_info.append({
                "journal_id": jid,
                "journal_name": journal.fld_journal_name,
                "short_form": journal.short_form,
                "editor_type": user_role.editor_type or "section_editor",
                "user_role_id": user_role.id,
                "description": journal.description,
                "issn_online": journal.issn_ol,
                "issn_print": journal.issn_prt,
                "chief_editor": journal.cheif_editor,
                "journal_logo": journal.journal_logo
            })
    
    return journals_info
