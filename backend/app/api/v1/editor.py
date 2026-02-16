"""Editor API endpoints"""
from fastapi import APIRouter, Depends, status, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from app.db.database import get_db
from app.db.models import User, Paper, OnlineReview, Editor
from app.core.security import get_current_user
from app.core.rate_limit import limiter
from app.utils.auth_helpers import check_role, role_matches
from app.utils.email_service import send_reviewer_invitation

router = APIRouter(prefix="/api/v1/editor", tags=["Editor"])


@router.get("/dashboard/stats")
@limiter.limit("100/minute")
async def get_editor_stats(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get editor dashboard statistics.
    
    Returns:
        Dictionary with editor's paper management stats
    """
    if not check_role(current_user.get("role"), "editor"):
        raise HTTPException(status_code=403, detail="Editor access required")
    
    total_papers = db.query(func.count(Paper.id)).scalar() or 0
    
    pending_review = db.query(func.count(Paper.id)).filter(
        Paper.status == "pending"
    ).scalar() or 0
    
    under_review = db.query(func.count(Paper.id)).filter(
        Paper.status == "under_review"
    ).scalar() or 0
    
    ready_publish = db.query(func.count(Paper.id)).filter(
        Paper.status == "accepted"
    ).scalar() or 0
    
    return {
        "total_papers": total_papers,
        "pending_review": pending_review,
        "under_review": under_review,
        "ready_publish": ready_publish
    }


@router.get("/paper-queue")
@limiter.limit("100/minute")
async def get_paper_queue(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paper queue for editor to manage.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        status_filter: Filter by paper status (pending, under_review, accepted, rejected)
        
    Returns:
        List of papers for editorial management
    """
    if not check_role(current_user.get("role"), "editor"):
        raise HTTPException(status_code=403, detail="Editor access required")
    
    query = db.query(Paper)
    
    if status_filter:
        query = query.filter(Paper.status == status_filter)
    
    total = query.count()
    papers = query.order_by(desc(Paper.added_on)).offset(skip).limit(limit).all()
    
    papers_list = []
    for paper in papers:
        papers_list.append({
            "id": paper.id,
            "title": paper.title,
            "author": paper.author,
            "journal": paper.journal,
            "submitted_date": paper.added_on.isoformat() if paper.added_on else None,
            "status": paper.status
        })
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "papers": papers_list
    }


@router.post("/papers/{paper_id}/invite-reviewer")
@limiter.limit("100/minute")
async def invite_reviewer(
    request: Request,
    paper_id: int,
    reviewer_email: str = Query(..., description="Email of the reviewer to invite"),
    due_days: int = Query(14, ge=1, le=90, description="Days until review is due"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invite a reviewer to review a paper by email.
    
    Args:
        paper_id: Paper ID
        reviewer_email: Email of reviewer to invite
        due_days: Number of days until review is due (1-90, default 14)
        
    Returns:
        Confirmation with invitation details
    """
    if not check_role(current_user.get("role"), ["editor", "admin"]):
        raise HTTPException(
            status_code=403, 
            detail="Editor or Admin access required. Only editors and admins can send reviewer invitations."
        )
    
    # Validate paper exists
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "Paper not found",
                "message": f"No paper found with ID {paper_id}",
                "paper_id": paper_id,
                "fix": "Verify the paper ID is correct and exists in the system"
            }
        )
    
    # Validate reviewer exists by email
    reviewer = db.query(User).filter(User.email == reviewer_email).first()
    if not reviewer:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Reviewer not found",
                "message": f"No user found with email {reviewer_email}",
                "reviewer_email": reviewer_email,
                "fix": "Create a reviewer account with this email first or use an existing reviewer email"
            }
        )
    
    # Validate reviewer has reviewer role
    if "reviewer" not in (reviewer.role or "").lower():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid user role",
                "message": f"User {reviewer_email} has role '{reviewer.role}', not 'reviewer'",
                "reviewer_email": reviewer_email,
                "reviewer_role": reviewer.role,
                "fix": "Assign the 'reviewer' role to this user in the admin panel"
            }
        )
    
    # Check if already invited (optional - customize as needed)
    existing_review = db.query(OnlineReview).filter(
        OnlineReview.paper_id == paper_id,
        OnlineReview.reviewer_id == str(reviewer.id)
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Already invited",
                "message": f"Reviewer {reviewer_email} is already assigned to this paper",
                "reviewer_email": reviewer_email,
                "paper_id": paper_id,
                "review_id": existing_review.id,
                "fix": "Choose a different reviewer or remove the existing assignment"
            }
        )
    
    # Prepare invitation data
    reviewer_name = f"{reviewer.fname} {reviewer.lname or ''}".strip()
    paper_title = paper.title or "Untitled Paper"
    paper_abstract = paper.abstract or "No abstract provided"
    journal_name = paper.journal or "AACS Journal"
    
    # Calculate due date
    due_date = (datetime.utcnow() + timedelta(days=due_days)).strftime("%B %d, %Y")
    
    # Generate invitation link (placeholder - would need token generation in production)
    invitation_link = f"https://localhost:3000/invitations/pending-{paper_id}"
    
    # Send invitation email
    email_sent = send_reviewer_invitation(
        reviewer_email=reviewer_email,
        reviewer_name=reviewer_name,
        paper_title=paper_title,
        paper_abstract=paper_abstract,
        journal_name=journal_name,
        invitation_link=invitation_link,
        due_date=due_date
    )
    
    return {
        "message": "Reviewer invitation sent successfully" if email_sent else "Reviewer invitation prepared (email delivery pending)",
        "invitation_id": "pending",
        "paper_id": paper_id,
        "paper_title": paper_title,
        "reviewer_email": reviewer_email,
        "reviewer_name": reviewer_name,
        "due_days": due_days,
        "due_date": due_date,
        "status": "invitation_sent" if email_sent else "invitation_queued",
        "email_sent": email_sent
    }


@router.post("/papers/{paper_id}/assign-reviewer")
async def assign_reviewer(
    paper_id: int,
    reviewer_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign a reviewer to a paper.
    
    Args:
        paper_id: Paper ID
        reviewer_id: Reviewer user ID
        
    Returns:
        Confirmation with assignment details
    """
    if not check_role(current_user.get("role"), "editor"):
        raise HTTPException(status_code=403, detail="Editor access required")
    
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "Paper not found",
                "message": f"No paper found with ID {paper_id}",
                "paper_id": paper_id,
                "fix": "Verify the paper ID is correct"
            }
        )
    
    reviewer = db.query(User).filter(User.id == reviewer_id).first()
    if not reviewer or "reviewer" not in (reviewer.role or "").lower():
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "Reviewer not found",
                "message": f"No reviewer found with ID {reviewer_id}",
                "reviewer_id": reviewer_id,
                "fix": "Verify the reviewer ID exists and user has reviewer role"
            }
        )
    
    # Create review assignment
    new_review = OnlineReview(
        paper_id=paper_id,
        reviewer_id=str(reviewer_id)
    )
    
    db.add(new_review)
    paper.status = "under_review"
    db.commit()
    db.refresh(new_review)
    
    return {
        "message": "Reviewer assigned successfully",
        "review_id": new_review.id,
        "paper_id": paper_id,
        "reviewer_id": reviewer_id,
        "assigned_date": datetime.utcnow().isoformat()
    }


@router.post("/papers/{paper_id}/status")
async def update_paper_status(
    paper_id: int,
    status: str,
    comments: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update paper status (accept, reject, request revisions).
    
    Args:
        paper_id: Paper ID
        status: New status (accepted, rejected, under_review, pending)
        comments: Optional editorial comments
        
    Returns:
        Updated paper object
    """
    if not check_role(current_user.get("role"), "editor"):
        raise HTTPException(status_code=403, detail="Editor access required")
    
    allowed_statuses = ["accepted", "rejected", "under_review", "pending"]
    if status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed_statuses}")
    
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    paper.status = status
    
    db.commit()
    db.refresh(paper)
    
    return {
        "id": paper.id,
        "title": paper.title,
        "status": paper.status,
        "updated_date": datetime.utcnow().isoformat()
    }


@router.get("/papers/{paper_id}/reviews")
@limiter.limit("100/minute")
async def get_paper_reviews(
    request: Request,
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reviews for a paper.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        List of reviews with reviewer details
    """
    if not check_role(current_user.get("role"), "editor"):
        raise HTTPException(status_code=403, detail="Editor access required")
    
    reviews = db.query(OnlineReview).filter(
        OnlineReview.paper_id == paper_id
    ).all()
    
    reviews_list = []
    for review in reviews:
        reviews_list.append({
            "id": review.id,
            "paper_id": review.paper_id,
            "reviewer_id": review.reviewer_id,
            "assigned_on": review.assigned_on.isoformat() if review.assigned_on else None
        })
    
    return reviews_list


@router.get("/reviewers")
@limiter.limit("100/minute")
async def list_available_reviewers(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List available reviewers for assignment.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        search: Search by name or email
        
    Returns:
        List of available reviewers
    """
    if not check_role(current_user.get("role"), ["editor", "admin"]):
        raise HTTPException(status_code=403, detail="Editor or Admin access required")
    
    query = db.query(User).filter(User.role.ilike("%reviewer%"))
    
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.fname.ilike(f"%{search}%")) |
            (User.lname.ilike(f"%{search}%"))
        )
    
    total = query.count()
    reviewers = query.offset(skip).limit(limit).all()
    
    reviewers_list = []
    for reviewer in reviewers:
        reviewers_list.append({
            "id": reviewer.id,
            "name": f"{reviewer.fname} {reviewer.lname or ''}",
            "email": reviewer.email,
            "specialization": reviewer.specialization,
            "affiliation": reviewer.affiliation
        })
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "reviewers": reviewers_list
    }


@router.get("/pending-actions")
@limiter.limit("100/minute")
async def get_pending_actions(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get pending actions for editor dashboard.
    
    Returns:
        Summary of pending actions
    """
    if not check_role(current_user.get("role"), "editor"):
        raise HTTPException(status_code=403, detail="Editor access required")
    
    pending_assignments = db.query(func.count(Paper.id)).filter(
        Paper.status == "pending"
    ).scalar() or 0
    
    # Count assigned reviews (papers under review)
    overdue_reviews = db.query(func.count(OnlineReview.id)).scalar() or 0
    
    ready_for_publication = db.query(func.count(Paper.id)).filter(
        Paper.status == "accepted"
    ).scalar() or 0
    
    return {
        "pending_assignments": pending_assignments,
        "assigned_reviews": overdue_reviews,
        "ready_for_publication": ready_for_publication
    }


@router.get("/papers-pending-decision")
@limiter.limit("100/minute")
async def get_papers_pending_decision(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get papers that have completed reviews and are pending editor decision.
    
    Returns:
        List of papers with review status and summary statistics
    """
    if not check_role(current_user.get("role"), "editor"):
        raise HTTPException(status_code=403, detail="Editor access required")
    
    # Get papers that are under review or awaiting decision
    papers = db.query(Paper).filter(
        Paper.status.in_(["under_review", "revision_requested"])
    ).offset(skip).limit(limit).all()
    
    papers_with_reviews = []
    for paper in papers:
        papers_with_reviews.append({
            "id": paper.id,
            "title": paper.title,
            "author": paper.author,
            "status": paper.status,
            "submitted_date": paper.added_on.isoformat() if paper.added_on else None,
            "added_by": paper.added_by
        })
    
    total = db.query(func.count(Paper.id)).filter(
        Paper.status.in_(["under_review", "revision_requested"])
    ).scalar() or 0
    
    return {
        "papers": papers_with_reviews,
        "total": total,
        "skip": skip,
        "limit": limit
    }
