"""Author API endpoints"""
from fastapi import APIRouter, Depends, status, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
from app.db.database import get_db
from app.db.models import User, Paper, PaperComment, OnlineReview
from app.core.security import get_current_user
from app.utils.file_handler import save_uploaded_file
from app.utils.auth_helpers import check_role
from app.utils.email_service import send_submission_confirmation

router = APIRouter(prefix="/api/v1/author", tags=["Author"])


@router.get("/dashboard/stats")
async def get_author_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get author dashboard statistics.
    
    Returns:
        Dictionary with author's submission stats
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    user_id = str(current_user.get("id"))
    
    total_submissions = db.query(func.count(Paper.id)).filter(
        Paper.added_by == user_id
    ).scalar() or 0
    
    accepted = db.query(func.count(Paper.id)).filter(
        Paper.added_by == user_id,
        Paper.status == "accepted"
    ).scalar() or 0
    
    rejected = db.query(func.count(Paper.id)).filter(
        Paper.added_by == user_id,
        Paper.status == "rejected"
    ).scalar() or 0
    
    under_review = db.query(func.count(Paper.id)).filter(
        Paper.added_by == user_id,
        Paper.status == "under review"
    ).scalar() or 0
    
    return {
        "total_submissions": total_submissions,
        "accepted_papers": accepted,
        "rejected_papers": rejected,
        "under_review": under_review
    }


@router.get("/submissions")
async def list_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List author's paper submissions.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        status_filter: Filter by paper status
        
    Returns:
        List of author's papers with pagination
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    user_id = str(current_user.get("id"))
    query = db.query(Paper).filter(Paper.added_by == user_id)
    
    if status_filter:
        query = query.filter(Paper.status == status_filter)
    
    total = query.count()
    papers = query.order_by(desc(Paper.added_on)).offset(skip).limit(limit).all()
    
    papers_list = []
    for paper in papers:
        papers_list.append({
            "id": paper.id,
            "title": paper.title,
            "abstract": paper.abstract,
            "status": paper.status,
            "submitted_date": paper.added_on.isoformat() if paper.added_on else None,
            "journal": paper.journal
        })
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "papers": papers_list
    }


@router.get("/submissions/{paper_id}")
async def get_submission_detail(
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a submission.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        Detailed paper information with reviews
    """
    user_id = str(current_user.get("id"))
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get reviews
    reviews = db.query(OnlineReview).filter(
        OnlineReview.paper_id == paper_id
    ).all()
    
    reviews_list = []
    for review in reviews:
        reviews_list.append({
            "id": review.id,
            "reviewer_name": review.reviewer_name,
            "comments": review.review_comment,
            "recommendation": review.recommendation,
            "date": review.date_submitted.isoformat() if review.date_submitted else None
        })
    
    return {
        "id": paper.id,
        "title": paper.title,
        "abstract": paper.abstract,
        "keywords": paper.keyword,
        "status": paper.status,
        "submitted_date": paper.added_on.isoformat() if paper.added_on else None,
        "journal": paper.journal,
        "reviews": reviews_list
    }


@router.post("/submit-paper")
async def submit_paper(
    title: str = Form(...),
    abstract: str = Form(...),
    keywords: str = Form(...),
    journal_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a new paper.
    
    Args:
        title: Paper title (form field)
        abstract: Paper abstract (form field)
        keywords: Paper keywords (form field)
        journal_id: Target journal ID (form field)
        file: Paper PDF file
        
    Returns:
        Created paper object
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    # Create paper record first to get the ID for file naming
    new_paper = Paper(
        title=title,
        abstract=abstract,
        keyword=keywords,
        journal=str(journal_id),
        author=current_user.get("email", ""),
        added_by=str(current_user.get("id", "")),
        status="submitted",
        mailstatus="0",
        added_on=datetime.utcnow()
    )
    
    db.add(new_paper)
    db.commit()
    db.refresh(new_paper)
    
    # Now save the file with the paper ID
    try:
        file_path = await save_uploaded_file(
            file=file,
            user_id=current_user.get("id"),
            paper_id=new_paper.id
        )
        
        # Update paper record with file path
        new_paper.file = file_path
        db.commit()
        db.refresh(new_paper)
        
        # Send confirmation email
        user = db.query(User).filter(User.id == current_user.get("id")).first()
        if user:
            author_name = f"{user.fname} {user.lname or ''}".strip() or "Author"
            send_submission_confirmation(
                author_email=current_user.get("email"),
                author_name=author_name,
                paper_title=title,
                journal_name=str(journal_id),
                paper_id=new_paper.id
            )
        
    except ValueError as e:
        # Rollback if file save fails
        db.delete(new_paper)
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Rollback if unexpected error (but don't rollback if just email fails)
        if "file" in str(e).lower():
            db.delete(new_paper)
            db.commit()
            raise HTTPException(status_code=500, detail="Failed to save paper file")
        # If it's just an email error, log it but don't fail the submission
        import logging
        logging.error(f"Failed to send confirmation email: {str(e)}")
    
    return {
        "id": new_paper.id,
        "title": new_paper.title,
        "status": new_paper.status,
        "file": new_paper.file,
        "submitted_date": new_paper.added_on.isoformat() if new_paper.added_on else None
    }


@router.get("/submissions/{paper_id}/comments")
async def get_paper_comments(
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all comments on an author's paper.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        List of comments/feedback
    """
    user_id = str(current_user.get("id"))
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    comments = db.query(PaperComment).filter(
        PaperComment.paper_id == paper_id
    ).order_by(desc(PaperComment.added_on)).all()
    
    comments_list = []
    for comment in comments:
        comments_list.append({
            "id": comment.id,
            "author": comment.comment_by,
            "text": comment.comment_text,
            "date": comment.added_on.isoformat() if comment.added_on else None
        })
    
    return comments_list
