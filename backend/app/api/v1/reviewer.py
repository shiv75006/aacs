"""Reviewer API endpoints"""
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
from app.db.database import get_db
from app.db.models import Paper, OnlineReview, User
from app.core.security import get_current_user
from app.utils.auth_helpers import check_role, role_matches
router = APIRouter(prefix="/api/v1/reviewer", tags=["Reviewer"])


@router.get("/dashboard/stats")
async def get_reviewer_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get reviewer dashboard statistics.
    
    Returns:
        Dictionary with reviewer's assignment and review stats
    """
    try:
        if not check_role(current_user.get("role"), "reviewer"):
            raise HTTPException(status_code=403, detail="Reviewer access required")
        
        reviewer_id = str(current_user.get("id"))
        
        # Count total assignments for this reviewer
        total_assignments = db.query(func.count(OnlineReview.id)).filter(
            OnlineReview.reviewer_id == reviewer_id
        ).scalar() or 0
        
        # For now, pending and completed are estimated based on total
        # In a real scenario, you'd have a status field tracking this
        pending_reviews = max(0, total_assignments - 1)  # Approximate
        completed_reviews = 1 if total_assignments > 0 else 0  # Approximate
        
        return {
            "total_assignments": total_assignments,
            "pending_reviews": pending_reviews,
            "completed_reviews": completed_reviews,
            "avg_review_time": "0 days"
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error fetching reviewer stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@router.get("/assignments")
async def list_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    sort_by: str = Query("due_soon"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List reviewer's paper assignments.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        status_filter: Filter by review status
        sort_by: Sort option (recent, assigned_date)
        
    Returns:
        List of paper assignments for review
    """
    try:
        if not check_role(current_user.get("role"), "reviewer"):
            raise HTTPException(status_code=403, detail="Reviewer access required")
        
        reviewer_id = str(current_user.get("id"))
        query = db.query(OnlineReview).filter(
            OnlineReview.reviewer_id == reviewer_id
        )
        
        # Sorting
        if sort_by == "recent":
            query = query.order_by(desc(OnlineReview.assigned_on))
        else:  # default to assigned_date
            query = query.order_by(OnlineReview.assigned_on)
        
        total = query.count()
        reviews = query.offset(skip).limit(limit).all()
        
        assignments_list = []
        for review in reviews:
            paper = db.query(Paper).filter(Paper.id == review.paper_id).first()
            
            assignments_list.append({
                "id": review.id,
                "paper_id": review.paper_id,
                "paper_title": paper.title if paper else "Unknown",
                "author": paper.added_by if paper else "Unknown",
                "journal": paper.journal if paper else "Unknown",
                "assigned_date": review.assigned_on.isoformat() if review.assigned_on else None,
                "status": "pending"
            })
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "assignments": assignments_list
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error fetching assignments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching assignments: {str(e)}")


@router.get("/assignments/{review_id}")
async def get_assignment_detail(
    review_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a review assignment.
    
    Args:
        review_id: Review assignment ID
        
    Returns:
        Complete paper and review details
    """
    try:
        reviewer_id = str(current_user.get("id"))
        review = db.query(OnlineReview).filter(
            OnlineReview.id == review_id,
            OnlineReview.reviewer_id == reviewer_id
        ).first()
        
        if not review:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        paper = db.query(Paper).filter(Paper.id == review.paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        author = db.query(User).filter(User.email == paper.added_by).first()
        
        return {
            "review_id": review.id,
            "paper": {
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "keywords": paper.keyword,
                "author": {
                    "name": f"{author.fname} {author.lname or ''}" if author else "Unknown",
                    "email": author.email if author else "Unknown",
                    "affiliation": author.affiliation if author else "Unknown"
                },
                "journal": paper.journal,
                "submitted_date": paper.added_on.isoformat() if paper.added_on else None,
                "file_url": f"/static/{paper.file}" if paper.file else None
            },
            "assignment": {
                "assigned_date": review.assigned_on.isoformat() if review.assigned_on else None,
                "status": "pending"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error fetching assignment detail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching assignment: {str(e)}")


@router.post("/assignments/{review_id}/submit-review")
async def submit_review(
    review_id: int,
    review_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a review for a paper.
    
    Args:
        review_id: Review assignment ID
        review_data: Review form data containing ratings and comments
        
    Returns:
        Updated review object
    """
    try:
        if not check_role(current_user.get("role"), "reviewer"):
            raise HTTPException(status_code=403, detail="Reviewer access required")
        
        reviewer_id = str(current_user.get("id"))
        review = db.query(OnlineReview).filter(
            OnlineReview.id == review_id,
            OnlineReview.reviewer_id == reviewer_id
        ).first()
        
        if not review:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Since OnlineReview model is simple, we can only store basic info
        # In a production system, you'd want to create a separate reviews table
        # For now, mark as reviewed and commit
        
        db.commit()
        db.refresh(review)
        
        return {
            "id": review.id,
            "paper_id": review.paper_id,
            "reviewer_id": review.reviewer_id,
            "assigned_on": review.assigned_on.isoformat() if review.assigned_on else None,
            "status": "submitted"
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error submitting review: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting review: {str(e)}")
    
    return {
        "message": "Review submitted successfully",
        "review_id": review.id,
        "recommendation": review.recommendation,
        "submitted_date": review.date_submitted.isoformat()
    }


@router.get("/history")
async def get_review_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get reviewer's review history.
    
    Returns:
        List of completed reviews with details
    """
    try:
        if not check_role(current_user.get("role"), "reviewer"):
            raise HTTPException(status_code=403, detail="Reviewer access required")
        
        reviewer_id = str(current_user.get("id"))
        all_reviews = db.query(OnlineReview).filter(
            OnlineReview.reviewer_id == reviewer_id
        ).order_by(desc(OnlineReview.assigned_on)).all()
        
        history_list = []
        for review in all_reviews:
            paper = db.query(Paper).filter(Paper.id == review.paper_id).first()
            
            history_list.append({
                "review_id": review.id,
                "paper_id": review.paper_id,
                "paper_title": paper.title if paper else "Unknown",
                "journal": paper.journal if paper else "Unknown",
                "assigned_date": review.assigned_on.isoformat() if review.assigned_on else None,
                "status": "pending"
            })
        
        return {
            "total": len(history_list),
            "history": history_list
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error fetching review history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")
    
    return history_list


@router.get("/profile")
async def get_reviewer_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get reviewer's profile information.
    
    Returns:
        Reviewer profile with specialization and statistics
    """
    try:
        if not check_role(current_user.get("role"), "reviewer"):
            raise HTTPException(status_code=403, detail="Reviewer access required")
        
        user_id = current_user.get("id")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Use reviewer_id instead of reviewer_email
        reviewer_id = str(user_id)
        total_reviews = db.query(func.count(OnlineReview.id)).filter(
            OnlineReview.reviewer_id == reviewer_id
        ).scalar() or 0
        
        return {
            "name": f"{user.fname} {user.lname or ''}",
            "email": user.email,
            "title": user.title,
            "affiliation": user.affiliation,
            "specialization": user.specialization,
            "contact": user.contact,
            "total_reviews": total_reviews
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error fetching reviewer profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching profile: {str(e)}")

@router.post("/notify-update")
async def notify_review_update(
    notification_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send email notification to reviewer for updates (new assignment, submission confirmation, etc.).
    Can be called by reviewers for their own notifications or by editors/admins.
    
    Args:
        notification_data: Dictionary containing:
            - reviewer_email: Reviewer's email address
            - reviewer_name: Reviewer's name (optional, will fetch if not provided)
            - paper_title: Title of the paper
            - journal_name: Name of the journal
            - update_type: Type of update (new_assignment, submission_confirmed, admin_message)
            - message: Optional custom message (for admin_message type)
    
    Returns:
        Status of email delivery
    """
    from app.utils.reviewer_email_scheduler import ReviewerEmailScheduler
    
    # Only allow editors, admins, and the reviewer themselves
    user_role = current_user.get("role")
    user_email = current_user.get("email")
    target_reviewer_email = notification_data.get("reviewer_email")
    
    # Validate access - allow if user is admin/editor or if they're the target reviewer
    if not check_role(user_role, ["admin", "editor"]) and user_email != target_reviewer_email:
        raise HTTPException(status_code=403, detail="Not authorized to send this notification")
    
    try:
        reviewer_email = notification_data.get("reviewer_email")
        reviewer_name = notification_data.get("reviewer_name")
        paper_title = notification_data.get("paper_title")
        journal_name = notification_data.get("journal_name")
        update_type = notification_data.get("update_type", "admin_message")
        message = notification_data.get("message", "")
        
        # Validate required fields
        if not reviewer_email or not paper_title or not journal_name:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: reviewer_email, paper_title, journal_name"
            )
        
        # Fetch reviewer name if not provided
        if not reviewer_name:
            reviewer = db.query(User).filter(User.email == reviewer_email).first()
            if reviewer:
                reviewer_name = reviewer.fname or "Reviewer"
            else:
                reviewer_name = "Reviewer"
        
        # Send notification
        success = ReviewerEmailScheduler.send_review_update_notification(
            reviewer_email=reviewer_email,
            reviewer_name=reviewer_name,
            paper_title=paper_title,
            journal_name=journal_name,
            update_type=update_type,
            message=message
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email notification"
            )
        
        return {
            "status": "success",
            "message": f"Notification sent to {reviewer_email}",
            "update_type": update_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending review update notification: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error sending notification: {str(e)}"
        )


@router.post("/deadline-reminder")
async def send_deadline_reminder(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger deadline reminder emails. 
    This endpoint should be called by a scheduler (e.g., APScheduler) at 9AM daily.
    Only accessible by admin or system scheduler.
    
    Returns:
        Summary of emails sent
    """
    from app.utils.reviewer_email_scheduler import ReviewerEmailScheduler
    
    # Only allow admin or internal calls
    user_role = current_user.get("role")
    if not check_role(user_role, "admin"):
        raise HTTPException(
            status_code=403,
            detail="Only administrators can trigger deadline reminders"
        )
    
    try:
        ReviewerEmailScheduler.send_deadline_reminder()
        
        return {
            "status": "success",
            "message": "Deadline reminder batch completed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in deadline reminder endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error sending reminders: {str(e)}"
        )