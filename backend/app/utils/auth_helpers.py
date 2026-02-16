"""Security and authorization utilities"""


def check_role(user_role: str, required_role) -> bool:
    """
    Check if user has required role (case-insensitive).
    
    Args:
        user_role: User's actual role from database
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
