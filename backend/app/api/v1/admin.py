"""Admin API endpoints"""
from fastapi import APIRouter, Depends, status, HTTPException, Query, Body, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.database import get_db
from app.db.models import User, Journal, Paper, PaperPublished, OnlineReview, ReviewSubmission
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
        Paper.status.in_(["submitted", "under_review"])
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
    
    # Get journal names and review status for papers
    paper_list = []
    for paper in papers:
        paper_dict = paper.to_dict()
        if paper.journal:
            journal = db.query(Journal).filter(Journal.fld_id == int(paper.journal) if paper.journal.isdigit() else 0).first()
            if journal:
                paper_dict['journal_name'] = journal.fld_journal_name
        
        # Get author info - added_by stores user ID
        if paper.added_by and paper.added_by.isdigit():
            author = db.query(User).filter(User.id == int(paper.added_by)).first()
            if author:
                paper_dict['author_name'] = f"{author.fname} {author.lname or ''}".strip()
        
        # Get review status for the paper
        # Note: OnlineReview.paper_id is stored as VARCHAR in the database
        total_assignments = db.query(func.count(OnlineReview.id)).filter(
            OnlineReview.paper_id == str(paper.id)
        ).scalar() or 0
        
        completed_reviews = db.query(func.count(ReviewSubmission.id)).filter(
            ReviewSubmission.paper_id == paper.id,
            ReviewSubmission.status == "submitted"
        ).scalar() or 0
        
        # Determine review status
        if total_assignments == 0:
            review_status = "not_assigned"
        elif completed_reviews == 0:
            review_status = "pending"
        elif completed_reviews < total_assignments:
            review_status = "partial"
        else:
            review_status = "reviewed"
        
        paper_dict['review_status'] = review_status
        paper_dict['total_reviewers'] = total_assignments
        paper_dict['completed_reviews'] = completed_reviews
        
        paper_list.append(paper_dict)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "papers": paper_list
    }


@router.get("/papers/{paper_id}")
@limiter.limit("200/minute")
async def get_paper_detail(
    request: Request,
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a single paper.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        Complete paper details with reviews and assigned reviewers
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get journal info
    journal = None
    if paper.journal:
        journal = db.query(Journal).filter(Journal.fld_id == paper.journal).first()
    
    # Get author info
    author = None
    if paper.added_by and paper.added_by.isdigit():
        author = db.query(User).filter(User.id == int(paper.added_by)).first()
    
    # Get co-authors
    from app.db.models import PaperCoAuthor
    co_authors = db.query(PaperCoAuthor).filter(PaperCoAuthor.paper_id == paper_id).all()
    co_authors_list = []
    for ca in co_authors:
        co_authors_list.append({
            "id": ca.id,
            "salutation": ca.salutation,
            "first_name": ca.first_name,
            "middle_name": ca.middle_name,
            "last_name": ca.last_name,
            "email": ca.email
        })
    
    # Get review assignments
    assignments = db.query(OnlineReview).filter(
        OnlineReview.paper_id == str(paper.id)
    ).all()
    
    assigned_reviewers = []
    for assignment in assignments:
        reviewer = None
        if assignment.reviewer_id:
            reviewer = db.query(User).filter(User.id == assignment.reviewer_id).first()
        
        # Get review submission if exists
        review_submission = db.query(ReviewSubmission).filter(
            ReviewSubmission.assignment_id == assignment.id
        ).first()
        
        reviewer_info = {
            "assignment_id": assignment.id,
            "reviewer_id": assignment.reviewer_id,
            "reviewer_name": f"{reviewer.fname} {reviewer.lname or ''}".strip() if reviewer else "Unknown",
            "reviewer_email": reviewer.email if reviewer else None,
            "specialization": reviewer.specialization if reviewer else None,
            "affiliation": reviewer.affiliation if reviewer else None,
            "assigned_on": assignment.assigned_on.isoformat() if assignment.assigned_on else None,
            "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
            "review_status": assignment.review_status,
            "has_submitted": False,
            "submitted_at": None,
            "review": None
        }
        
        if review_submission:
            reviewer_info["has_submitted"] = review_submission.status == "submitted"
            reviewer_info["submitted_at"] = review_submission.submitted_at.isoformat() if review_submission.submitted_at else None
            if review_submission.status == "submitted":
                reviewer_info["review"] = {
                    "id": review_submission.id,
                    "technical_quality": review_submission.technical_quality,
                    "clarity": review_submission.clarity,
                    "originality": review_submission.originality,
                    "significance": review_submission.significance,
                    "overall_rating": review_submission.overall_rating,
                    "author_comments": review_submission.author_comments,
                    "confidential_comments": review_submission.confidential_comments,
                    "recommendation": review_submission.recommendation,
                    "review_report_file": review_submission.review_report_file
                }
        
        assigned_reviewers.append(reviewer_info)
    
    # Calculate review stats
    total_assignments = len(assigned_reviewers)
    completed_reviews = sum(1 for r in assigned_reviewers if r["has_submitted"])
    
    # Determine review status
    if total_assignments == 0:
        review_status = "not_assigned"
    elif completed_reviews == 0:
        review_status = "pending"
    elif completed_reviews < total_assignments:
        review_status = "partial"
    else:
        review_status = "reviewed"
    
    return {
        "id": paper.id,
        "paper_code": paper.paper_code,
        "title": paper.title,
        "abstract": paper.abstract,
        "keywords": paper.keyword.split(",") if paper.keyword else [],
        "file": paper.file,
        "status": paper.status,
        "submitted_date": paper.added_on.isoformat() if paper.added_on else None,
        "author": {
            "id": author.id if author else None,
            "name": f"{author.fname} {author.lname or ''}".strip() if author else (paper.author or "Unknown"),
            "email": author.email if author else None,
            "affiliation": author.affiliation if author else None
        },
        "co_authors": co_authors_list,
        "journal": {
            "id": journal.fld_id if journal else None,
            "name": journal.fld_journal_name if journal else "Unknown"
        },
        "review_status": review_status,
        "total_reviewers": total_assignments,
        "completed_reviews": completed_reviews,
        "assigned_reviewers": assigned_reviewers,
        "version_number": paper.version_number,
        "revision_count": paper.revision_count,
        "revision_deadline": paper.revision_deadline.isoformat() if paper.revision_deadline else None,
        "revision_notes": paper.revision_notes,
        "research_area": paper.research_area,
        "message_to_editor": paper.message_to_editor
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
    
    # Include all paper statuses including "reviewed"
    statuses = ["submitted", "under_review", "reviewed", "accepted", "rejected", "correction", "under_publication", "published", "resubmitted"]
    stats = {}
    
    for status in statuses:
        count = db.query(func.count(Paper.id)).filter(
            Paper.status == status
        ).scalar() or 0
        # Only include statuses that have at least one paper
        if count > 0:
            stats[status] = count
    
    return stats


@router.get("/papers/{paper_id}/view")
@limiter.limit("200/minute")
async def admin_view_paper_file(
    request: Request,
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    View any paper file (admin only).
    
    Args:
        paper_id: Paper ID
        
    Returns:
        Paper file for inline viewing
    """
    from fastapi.responses import FileResponse
    from app.utils.file_handler import get_file_full_path
    
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    if not paper.file:
        raise HTTPException(status_code=404, detail="Paper file not found")
    
    # Get full file path from relative path stored in DB
    filepath = get_file_full_path(paper.file)
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Paper file not found on server")
    
    filename = filepath.name
    
    # Determine correct media type based on file extension
    ext = filepath.suffix.lower()
    media_types = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    media_type = media_types.get(ext, 'application/octet-stream')
    
    return FileResponse(
        path=str(filepath),
        filename=filename,
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename=\"{filename}\""}
    )
