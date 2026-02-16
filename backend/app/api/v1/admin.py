"""Admin API endpoints"""
from fastapi import APIRouter, Depends, status, HTTPException, Query, Body, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.database import get_db
from app.db.models import User, Journal, Paper, PaperPublished
from app.core.security import get_current_user
from app.core.rate_limit import limiter
from app.utils.auth_helpers import check_role

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/dashboard/stats")
@limiter.limit("200/minute")
async def get_dashboard_stats(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get admin dashboard statistics.
    
    Returns:
        Dictionary with dashboard stats (total users, journals, papers, published)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_journals = db.query(func.count(Journal.fld_id)).scalar() or 0
    total_submissions = db.query(func.count(Paper.id)).scalar() or 0
    pending_papers = db.query(func.count(Paper.id)).filter(
        Paper.status.in_(["submitted", "under review"])
    ).scalar() or 0
    published_papers = db.query(func.count(PaperPublished.id)).scalar() or 0
    
    return {
        "total_users": total_users,
        "total_journals": total_journals,
        "total_submissions": total_submissions,
        "pending_papers": pending_papers,
        "published_papers": published_papers
    }


@router.get("/users")
@limiter.limit("200/minute")
async def list_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    role: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all users with optional filtering and pagination.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        search: Search by email or name
        role: Filter by user role
        
    Returns:
        List of users with pagination info
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.fname.ilike(f"%{search}%")) |
            (User.lname.ilike(f"%{search}%"))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "users": [user.to_dict() for user in users]
    }


@router.post("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user role.
    
    Args:
        user_id: User ID to update
        role: New role (admin, author, editor, reviewer)
        
    Returns:
        Updated user object
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    allowed_roles = ["admin", "author", "editor", "reviewer"]
    if role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed: {allowed_roles}")
    
    user.role = role
    db.commit()
    db.refresh(user)
    
    return user.to_dict()


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user.
    
    Args:
        user_id: User ID to delete
        
    Returns:
        Confirmation message
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user_id} deleted successfully"}


@router.get("/papers")
@limiter.limit("200/minute")
async def list_all_papers(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all papers with optional status filter.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        status: Filter by paper status
        
    Returns:
        List of papers with pagination info
    """
    if not check_role(current_user.get("role"), ["admin", "editor"]):
        raise HTTPException(status_code=403, detail="Admin or Editor access required")
    
    query = db.query(Paper)
    
    if status:
        query = query.filter(Paper.status == status)
    
    total = query.count()
    papers = query.order_by(desc(Paper.added_on)).offset(skip).limit(limit).all()
    
    # Get journal names for papers
    paper_list = []
    for paper in papers:
        paper_dict = paper.to_dict()
        if paper.journal:
            journal = db.query(Journal).filter(Journal.fld_id == int(paper.journal) if paper.journal.isdigit() else 0).first()
            if journal:
                paper_dict['journal_name'] = journal.fld_journal_name
        paper_list.append(paper_dict)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "papers": paper_list
    }


@router.get("/journals")
@limiter.limit("200/minute")
async def list_all_journals(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all journals with optional search.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        search: Search by journal name or short form
        
    Returns:
        List of journals with pagination info
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(Journal)
    
    if search:
        query = query.filter(
            (Journal.fld_journal_name.ilike(f"%{search}%")) |
            (Journal.short_form.ilike(f"%{search}%"))
        )
    
    total = query.count()
    journals = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "journals": [journal.to_dict() for journal in journals]
    }


@router.get("/activity")
@limiter.limit("200/minute")
async def get_recent_activity(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent system activity (new users, papers, etc).
    
    Args:
        limit: Number of activities to return
        
    Returns:
        List of recent activities
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    activities = []
    
    # Get recent users
    recent_users = db.query(User).order_by(desc(User.added_on)).limit(limit // 2).all()
    for user in recent_users:
        if user.added_on:
            activities.append({
                "type": "user_registration",
                "description": f"New user registered: {user.email}",
                "timestamp": user.added_on.isoformat() if user.added_on else None
            })
    
    # Get recent papers
    recent_papers = db.query(Paper).order_by(desc(Paper.added_on)).limit(limit // 2).all()
    for paper in recent_papers:
        if paper.added_on:
            activities.append({
                "type": "paper_submission",
                "description": f"New paper submitted: {paper.title or 'Untitled'}",
                "timestamp": paper.added_on.isoformat() if paper.added_on else None
            })
    
    # Sort by timestamp (handle None) and return
    activities.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    return activities[:limit]


@router.get("/stats/papers-by-status")
@limiter.limit("200/minute")
async def get_papers_by_status(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get breakdown of papers by status.
    
    Returns:
        Dictionary with paper counts by status
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    statuses = ["submitted", "under review", "reviewed", "accepted", "rejected", "correction", "under publication", "published", "resubmitted"]
    stats = {}
    
    for status in statuses:
        count = db.query(func.count(Paper.id)).filter(
            Paper.status == status
        ).scalar() or 0
        stats[status] = count
    
    return stats
