"""Author API endpoints"""
from fastapi import APIRouter, Depends, status, HTTPException, Query, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
import json
from app.db.database import get_db
from app.db.models import User, Paper, PaperComment, OnlineReview, ReviewSubmission, ReviewerInvitation, PaperCoAuthor, Journal, PaperCorrespondence, Editor
from app.core.security import get_current_user, get_current_user_from_token_or_query
from app.utils.file_handler import save_uploaded_file
from app.utils.auth_helpers import check_role
from app.utils.email_service import send_submission_confirmation
from app.schemas.correspondence import CorrespondenceResponse, CorrespondenceListResponse
from app.services.correspondence_service import create_and_send_correspondence

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
        Paper.status == "under_review"
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
        # Get journal name from journal table
        journal = None
        if paper.journal:
            journal = db.query(Journal).filter(Journal.fld_id == paper.journal).first()
        
        papers_list.append({
            "id": paper.id,
            "title": paper.title,
            "abstract": paper.abstract,
            "status": paper.status,
            "submitted_date": paper.added_on.isoformat() if paper.added_on else None,
            "journal": journal.fld_journal_name if journal else "Unknown"
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
    
    # Get review submissions (actual submitted reviews with feedback)
    review_submissions = db.query(ReviewSubmission).filter(
        ReviewSubmission.paper_id == paper_id,
        ReviewSubmission.status == "submitted"
    ).all()
    
    reviews_list = []
    for review in review_submissions:
        # Get reviewer info from invitation if available
        reviewer_name = "Anonymous Reviewer"
        invitation = db.query(ReviewerInvitation).filter(
            ReviewerInvitation.paper_id == paper_id,
            ReviewerInvitation.reviewer_id == int(review.reviewer_id) if review.reviewer_id.isdigit() else None
        ).first()
        if invitation and invitation.reviewer_name:
            reviewer_name = invitation.reviewer_name
        
        reviews_list.append({
            "id": review.id,
            "reviewer_name": reviewer_name,
            "comments": review.author_comments,  # Only show comments for authors
            "recommendation": review.recommendation,
            "overall_rating": review.overall_rating,
            "date": review.submitted_at.isoformat() if review.submitted_at else None,
            "review_report_file": review.review_report_file,  # Include file path for download
            "technical_quality": review.technical_quality,
            "clarity": review.clarity,
            "originality": review.originality,
            "significance": review.significance
        })
    
    # Get journal name from journal table
    journal = None
    if paper.journal:
        journal = db.query(Journal).filter(Journal.fld_id == paper.journal).first()
    
    return {
        "id": paper.id,
        "title": paper.title,
        "abstract": paper.abstract,
        "keywords": paper.keyword,
        "status": paper.status,
        "submitted_date": paper.added_on.isoformat() if paper.added_on else None,
        "journal": journal.fld_journal_name if journal else "Unknown",
        "file": paper.file,
        "reviews": reviews_list
    }


@router.get("/submissions/{paper_id}/correspondence", response_model=CorrespondenceListResponse)
async def get_submission_correspondence(
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get email correspondence history for a submission.
    
    Returns all notification emails sent to the author for this paper,
    ordered by most recent first.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        List of correspondence entries with delivery status
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to this author
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get all correspondence for this paper
    correspondence_entries = db.query(PaperCorrespondence).filter(
        PaperCorrespondence.paper_id == paper_id
    ).order_by(desc(PaperCorrespondence.created_at)).all()
    
    correspondence_list = []
    for entry in correspondence_entries:
        correspondence_list.append(CorrespondenceResponse(
            id=entry.id,
            paper_id=entry.paper_id,
            recipient_email=entry.recipient_email,
            recipient_name=entry.recipient_name,
            subject=entry.subject,
            body=entry.body,
            email_type=entry.email_type,
            status_at_send=entry.status_at_send,
            delivery_status=entry.delivery_status,
            webhook_id=entry.webhook_id,
            webhook_received_at=entry.webhook_received_at,
            error_message=entry.error_message,
            retry_count=entry.retry_count,
            created_at=entry.created_at,
            sent_at=entry.sent_at
        ))
    
    return CorrespondenceListResponse(
        total=len(correspondence_list),
        paper_id=paper_id,
        paper_title=paper.title,
        correspondence=correspondence_list
    )


@router.put("/submissions/{paper_id}/correspondence/{correspondence_id}/read")
async def mark_correspondence_as_read(
    paper_id: int,
    correspondence_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a correspondence item as read.
    
    Args:
        paper_id: Paper ID
        correspondence_id: Correspondence ID
        
    Returns:
        Updated correspondence with read status
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to this author
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get correspondence
    correspondence = db.query(PaperCorrespondence).filter(
        PaperCorrespondence.id == correspondence_id,
        PaperCorrespondence.paper_id == paper_id
    ).first()
    
    if not correspondence:
        raise HTTPException(status_code=404, detail="Correspondence not found")
    
    # Mark as read if not already
    if not correspondence.is_read:
        correspondence.is_read = True
        correspondence.read_at = datetime.utcnow()
        db.commit()
        db.refresh(correspondence)
    
    return {
        "message": "Correspondence marked as read",
        "id": correspondence.id,
        "is_read": correspondence.is_read,
        "read_at": correspondence.read_at.isoformat() if correspondence.read_at else None
    }


@router.post("/submissions/{paper_id}/contact-editorial")
async def contact_editorial_office(
    paper_id: int,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    subject: str = Form(...),
    message: str = Form(...),
    inquiry_type: str = Form(default="general")
):
    """
    Allow author to send a message to the editorial office regarding their submission.
    
    Args:
        paper_id: Paper ID
        subject: Email subject
        message: Email message content
        inquiry_type: Type of inquiry (general, status, revision, technical)
        
    Returns:
        Confirmation of correspondence sent
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    user_id = str(current_user.get("id"))
    user_email = current_user.get("email", "")
    user_name = f"{current_user.get('fname', '')} {current_user.get('lname', '')}".strip() or "Author"
    
    # Verify paper belongs to this author
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found or access denied")
    
    # Get journal info to find editors
    journal = db.query(Journal).filter(Journal.fld_id == paper.journal).first()
    journal_name = journal.fld_journal_name if journal else "AACS Journal"
    
    # Find editors for this journal (chief editors first)
    editors = db.query(Editor).filter(
        Editor.journal_id == paper.journal
    ).order_by(
        desc(Editor.role == 'Admin'),  # Admin/Chief editors first
        Editor.id
    ).all()
    
    # Get recipient emails - if editors exist, use them; otherwise use default
    recipient_emails = []
    recipient_names = []
    
    if editors:
        for editor in editors[:3]:  # Max 3 recipients
            if editor.editor_email:
                recipient_emails.append(editor.editor_email)
                recipient_names.append(editor.editor_name or "Editor")
    
    if not recipient_emails:
        # Fallback to default editorial email
        recipient_emails = ["info@aacsjournals.com"]
        recipient_names = ["Editorial Office"]
    
    # Create correspondence record
    correspondence = PaperCorrespondence(
        paper_id=paper_id,
        sender_id=int(user_id),
        sender_role='author',
        recipient_email=recipient_emails[0],
        recipient_name=recipient_names[0],
        subject=subject,
        body=message,
        email_type=inquiry_type,
        status_at_send=paper.status,
        is_read=False,
        delivery_status='pending',
        created_at=datetime.utcnow()
    )
    db.add(correspondence)
    db.commit()
    db.refresh(correspondence)
    
    # Send email in background
    email_sent = False
    try:
        await create_and_send_correspondence(
            db=db,
            paper_id=paper_id,
            recipient_email=recipient_emails[0],
            recipient_name=recipient_names[0],
            subject=f"[Author Inquiry - {paper.paper_code}] {subject}",
            message=f"""
Dear Editorial Team,

You have received a message from an author regarding paper submission.

Paper Code: {paper.paper_code}
Paper Title: {paper.title}
Inquiry Type: {inquiry_type.replace('_', ' ').title()}

From: {user_name} ({user_email})

---
{message}
---

This message was sent through the AACS Journal Management System.
To respond, please use the correspondence feature in the admin panel.

Best regards,
AACS Journal System
""",
            sender_id=int(user_id),
            sender_role='author',
            template_id=None,
            send_email=True
        )
        email_sent = True
    except Exception as e:
        # Log error but don't fail - correspondence is already recorded
        print(f"Failed to send email: {e}")
    
    return {
        "success": True,
        "message": "Your message has been sent to the editorial office",
        "correspondence_id": correspondence.id,
        "email_sent": email_sent,
        "recipient": recipient_names[0]
    }


@router.get("/submissions/{paper_id}/unread-count")
async def get_unread_correspondence_count(
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get count of unread correspondence for a paper.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        Count of unread correspondence
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to this author
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Count unread correspondence
    unread_count = db.query(func.count(PaperCorrespondence.id)).filter(
        PaperCorrespondence.paper_id == paper_id,
        PaperCorrespondence.is_read == False
    ).scalar() or 0
    
    return {
        "paper_id": paper_id,
        "unread_count": unread_count
    }


@router.post("/submit-paper")
async def submit_paper(
    title: str = Form(...),
    abstract: str = Form(...),
    keywords: str = Form(...),
    journal_id: int = Form(...),
    file: UploadFile = File(...),
    research_area: str = Form(default=""),
    message_to_editor: str = Form(default=""),
    terms_accepted: bool = Form(default=False),
    author_details: str = Form(...),  # JSON string with primary author details
    co_authors: str = Form(default="[]"),  # JSON string array of co-authors
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a new paper with extended metadata and co-author support.
    
    Args:
        title: Paper title (form field)
        abstract: Paper abstract (form field)
        keywords: Paper keywords (form field)
        journal_id: Target journal ID (form field)
        file: Paper PDF file
        research_area: Research area/field (optional)
        message_to_editor: Message to editor (optional)
        terms_accepted: Terms and conditions acceptance
        author_details: JSON string with primary author details
        co_authors: JSON string array of co-author objects
        
    Returns:
        Created paper object
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Submit paper request received: title={title}, journal_id={journal_id}, file={file.filename}")
    
    if not check_role(current_user.get("role"), "author"):
        logger.error(f"Author access denied for user {current_user.get('id')}")
        raise HTTPException(status_code=403, detail="Author access required")
    
    # Validate terms acceptance
    if not terms_accepted:
        raise HTTPException(status_code=400, detail="You must accept the terms and conditions")
    
    try:
        # Parse author details and co-authors from JSON
        try:
            author_data = json.loads(author_details)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid author_details format - must be valid JSON")
        
        try:
            co_authors_data = json.loads(co_authors)
            if not isinstance(co_authors_data, list):
                co_authors_data = []
        except json.JSONDecodeError:
            co_authors_data = []
        
        # Build primary author string for legacy field
        author_name_parts = []
        if author_data.get("salutation"):
            author_name_parts.append(author_data.get("salutation"))
        if author_data.get("first_name"):
            author_name_parts.append(author_data.get("first_name"))
        if author_data.get("middle_name"):
            author_name_parts.append(author_data.get("middle_name"))
        if author_data.get("last_name"):
            author_name_parts.append(author_data.get("last_name"))
        author_name = " ".join(author_name_parts)
        
        # Update user profile with author details
        user = db.query(User).filter(User.id == current_user.get("id")).first()
        if user:
            user.fname = author_data.get("first_name", user.fname)
            user.mname = author_data.get("middle_name", user.mname)
            user.lname = author_data.get("last_name", user.lname)
            user.salutation = author_data.get("salutation", user.salutation)
            user.designation = author_data.get("designation", user.designation)
            user.department = author_data.get("department", user.department)
            user.organisation = author_data.get("organisation", user.organisation)
            db.commit()
        
        # Create paper record first to get the ID for file naming
        new_paper = Paper(
            title=title,
            abstract=abstract,
            keyword=keywords,
            journal=journal_id,  # journal is now INT, no str() conversion needed
            author=current_user.get("email", ""),
            added_by=str(current_user.get("id", "")),
            status="submitted",  # Must match database ENUM values
            mailstatus="0",
            added_on=datetime.utcnow(),
            research_area=research_area or None,
            message_to_editor=message_to_editor or None,
            terms_accepted=terms_accepted
        )
        
        db.add(new_paper)
        db.commit()
        db.refresh(new_paper)
        logger.info(f"Paper created with ID: {new_paper.id}")
        
        # Now save the file with the paper ID
        file_path = await save_uploaded_file(
            file=file,
            user_id=current_user.get("id"),
            paper_id=new_paper.id
        )
        
        # Update paper record with file path
        new_paper.file = file_path
        db.commit()
        db.refresh(new_paper)
        logger.info(f"File saved for paper {new_paper.id}: {file_path}")
        
        # Save co-authors
        for idx, co_author in enumerate(co_authors_data):
            co_author_record = PaperCoAuthor(
                paper_id=new_paper.id,
                salutation=co_author.get("salutation"),
                first_name=co_author.get("first_name", ""),
                middle_name=co_author.get("middle_name"),
                last_name=co_author.get("last_name", ""),
                email=co_author.get("email"),
                designation=co_author.get("designation"),
                department=co_author.get("department"),
                organisation=co_author.get("organisation"),
                author_order=co_author.get("author_order", idx + 2),  # Start from 2 as primary author is 1
                is_corresponding=co_author.get("is_corresponding", False),
                created_at=datetime.utcnow()
            )
            db.add(co_author_record)
        
        db.commit()
        logger.info(f"Saved {len(co_authors_data)} co-authors for paper {new_paper.id}")
        
        # Send submission confirmation email via background task
        email_queued = False
        if background_tasks:
            # Get author info
            author = db.query(User).filter(User.id == current_user.get("id")).first()
            
            # Get journal info
            journal = db.query(Journal).filter(Journal.fld_id == journal_id).first()
            
            if author and author.email:
                author_name = f"{author.fname or ''} {author.lname or ''}".strip() or "Author"
                journal_name = journal.fld_journal_name if journal else "AACS Journal"
                
                async def send_submission_email():
                    from app.db.database import SessionLocal
                    email_db = SessionLocal()
                    try:
                        await create_and_send_correspondence(
                            db=email_db,
                            paper_id=new_paper.id,
                            paper_code=new_paper.paper_code,
                            paper_title=new_paper.title,
                            journal_name=journal_name,
                            author_email=author.email,
                            author_name=author_name,
                            email_type="submission_confirmed",
                            status_at_send="submitted"
                        )
                    finally:
                        email_db.close()
                
                background_tasks.add_task(send_submission_email)
                email_queued = True
                logger.info(f"Submission confirmation email queued for paper {new_paper.id}")
        
        # Return success response
        response_data = {
            "id": new_paper.id,
            "title": new_paper.title,
            "status": new_paper.status,
            "file": new_paper.file,
            "submitted_date": new_paper.added_on.isoformat() if new_paper.added_on else None,
            "co_authors_count": len(co_authors_data),
            "email_notification_queued": email_queued
        }
        logger.info(f"Returning response: {response_data}")
        return response_data
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in submit_paper: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit paper: {str(e)}")


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

@router.get("/submissions/{paper_id}/reviews")
async def get_submission_reviews(
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reviewer feedback for an author's paper submission.
    Authors can see: author_comments, recommendation, ratings, but NOT confidential_comments.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        List of reviews with feedback visible to authors
    """
    from app.db.models import ReviewSubmission
    
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to author
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get all review submissions for this paper
    reviews = db.query(ReviewSubmission).filter(
        ReviewSubmission.paper_id == paper_id,
        ReviewSubmission.status == "submitted"
    ).order_by(desc(ReviewSubmission.submitted_at)).all()
    
    reviews_list = []
    for review in reviews:
        reviews_list.append({
            "id": review.id,
            "technical_quality": review.technical_quality,
            "clarity": review.clarity,
            "originality": review.originality,
            "significance": review.significance,
            "overall_rating": review.overall_rating,
            "author_comments": review.author_comments,
            "recommendation": review.recommendation,
            "submitted_on": review.submitted_at.isoformat() if review.submitted_at else None
        })
    
    return {
        "total_reviews": len(reviews_list),
        "reviews": reviews_list
    }


@router.get("/submissions/{paper_id}/decision")
async def get_editor_decision(
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get editor's final decision and revision requirements if applicable.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        Editor decision and revision details
    """
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to author
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    decision = None
    if paper.status in ["accepted", "rejected", "correction"]:
        decision = paper.status
    
    return {
        "decision": decision,
        "revision_required": paper.status == "correction",
        "revision_deadline": paper.revision_deadline.isoformat() if paper.revision_deadline else None,
        "revision_notes": paper.revision_notes,
        "revision_requested_date": paper.revision_requested_date.isoformat() if paper.revision_requested_date else None
    }


@router.get("/submissions/{paper_id}/revisions")
async def get_revision_history(
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get revision history and all versions of a paper.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        List of all paper versions with metadata
    """
    from app.db.models import PaperVersion
    
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to author
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get all versions
    versions = db.query(PaperVersion).filter(
        PaperVersion.paper_id == paper_id
    ).order_by(PaperVersion.version_number).all()
    
    versions_list = []
    for version in versions:
        versions_list.append({
            "version_number": version.version_number,
            "uploaded_on": version.uploaded_on.isoformat() if version.uploaded_on else None,
            "revision_reason": version.revision_reason,
            "change_summary": version.change_summary,
            "file_size": version.file_size
        })
    
    return {
        "paper_id": paper_id,
        "current_version": paper.version_number,
        "total_revisions": paper.revision_count,
        "versions": versions_list
    }


@router.post("/submissions/{paper_id}/resubmit")
async def resubmit_paper(
    paper_id: int,
    file: UploadFile = File(...),
    revision_reason: str = Form(...),
    change_summary: str = Form(None),
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resubmit a paper with revisions.
    
    Args:
        paper_id: Paper ID
        file: Revised paper file
        revision_reason: Why the paper is being resubmitted
        change_summary: Summary of changes made
        
    Returns:
        Updated paper and version info
    """
    from app.db.models import PaperVersion
    import os
    
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to author and requires revision
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    if paper.status != "correction":
        raise HTTPException(status_code=400, detail="This paper does not require revision")
    
    # Validate file
    allowed_types = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF and Word documents allowed")
    
    # Read and validate file size
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50MB max
        raise HTTPException(status_code=400, detail="File size must be less than 50MB")
    
    try:
        # Save new version
        upload_dir = f"uploads/papers/user_{user_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        new_version = paper.version_number + 1
        filename = f"{paper_id}_v{new_version}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        # Create version record
        version_record = PaperVersion(
            paper_id=paper_id,
            version_number=new_version,
            file=filepath,
            file_size=len(content),
            revision_reason=revision_reason,
            change_summary=change_summary,
            uploaded_by=user_id
        )
        
        # Update paper
        paper.version_number = new_version
        paper.revision_count += 1
        paper.file = filepath
        paper.status = "resubmitted"
        
        db.add(version_record)
        db.add(paper)
        db.commit()
        db.refresh(paper)
        
        # Send resubmission confirmation email to author and notify editor
        email_queued = False
        if background_tasks:
            author = db.query(User).filter(User.id == current_user.get("id")).first()
            journal = db.query(Journal).filter(Journal.fld_id == paper.journal).first()
            
            if author and author.email:
                author_name = f"{author.fname or ''} {author.lname or ''}".strip() or "Author"
                journal_name = journal.fld_journal_name if journal else "AACS Journal"
                
                # Notify author of successful resubmission
                async def send_resubmit_email():
                    from app.db.database import SessionLocal
                    email_db = SessionLocal()
                    try:
                        await create_and_send_correspondence(
                            db=email_db,
                            paper_id=paper.id,
                            paper_code=paper.paper_code,
                            paper_title=paper.title,
                            journal_name=journal_name,
                            author_email=author.email,
                            author_name=author_name,
                            email_type="resubmitted",
                            status_at_send="resubmitted",
                            version_number=paper.version_number
                        )
                    finally:
                        email_db.close()
                
                background_tasks.add_task(send_resubmit_email)
                email_queued = True
                
                # Also notify editor about the revision
                editor = None
                if paper.journal:
                    editor_record = db.query(Editor).filter(Editor.journal_id == paper.journal).first()
                    if editor_record:
                        editor = db.query(User).filter(User.email == editor_record.email).first()
                
                if editor and editor.email:
                    async def send_editor_notification():
                        from app.db.database import SessionLocal
                        email_db = SessionLocal()
                        try:
                            await create_and_send_correspondence(
                                db=email_db,
                                paper_id=paper.id,
                                paper_code=paper.paper_code,
                                paper_title=paper.title,
                                journal_name=journal_name,
                                author_email=editor.email,
                                author_name=f"{editor.fname or ''} {editor.lname or ''}".strip() or "Editor",
                                email_type="revision_received_editor",
                                status_at_send="resubmitted",
                                version_number=paper.version_number
                            )
                        finally:
                            email_db.close()
                    
                    background_tasks.add_task(send_editor_notification)
        
        return {
            "message": "Paper resubmitted successfully",
            "paper_id": paper.id,
            "version_number": paper.version_number,
            "status": paper.status,
            "email_notification_queued": email_queued
        }
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Error resubmitting paper: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resubmitting paper: {str(e)}")


@router.get("/submissions/{paper_id}/download")
async def download_paper_file(
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download the submitted paper file.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        Paper file as downloadable blob
    """
    from fastapi.responses import FileResponse
    from app.utils.file_handler import get_file_full_path
    import os
    
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to author
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    if not paper.file:
        raise HTTPException(status_code=404, detail="Paper file not found")
    
    # Get full file path from relative path stored in DB
    filepath = get_file_full_path(paper.file)
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Paper file not found on server")
    
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
        media_type=media_type
    )


@router.get("/submissions/{paper_id}/reviews/{review_id}/download-report")
async def download_review_report(
    paper_id: int,
    review_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download the review report file for a specific review.
    
    Args:
        paper_id: Paper ID
        review_id: Review ID
        
    Returns:
        Review report file as downloadable blob
    """
    from fastapi.responses import FileResponse
    from pathlib import Path
    
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to author
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get the review submission
    review = db.query(ReviewSubmission).filter(
        ReviewSubmission.id == review_id,
        ReviewSubmission.paper_id == paper_id,
        ReviewSubmission.status == "submitted"
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if not review.review_report_file:
        raise HTTPException(status_code=404, detail="No review report file available for this review")
    
    # Review reports are stored with paths like "uploads/reviews/reviewer_X/file.docx"
    # or relative paths - need to resolve to absolute path in backend directory
    filepath = Path(review.review_report_file)
    
    # If path is relative, make it absolute from the backend directory
    if not filepath.is_absolute():
        from app.utils.file_handler import UPLOAD_BASE_DIR
        # UPLOAD_BASE_DIR is backend/uploads/papers
        # UPLOAD_BASE_DIR.parent.parent is backend/
        # If path starts with "uploads/", join with backend directory
        if review.review_report_file.startswith("uploads/"):
            filepath = UPLOAD_BASE_DIR.parent.parent / review.review_report_file
        else:
            filepath = UPLOAD_BASE_DIR.parent / review.review_report_file
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Review report file not found on server")
    
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


@router.get("/submissions/{paper_id}/view")
async def view_paper_file(
    paper_id: int,
    current_user: dict = Depends(get_current_user_from_token_or_query),
    db: Session = Depends(get_db)
):
    """
    View the submitted paper file in browser.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        Paper file for inline viewing
    """
    from fastapi.responses import FileResponse
    from app.utils.file_handler import get_file_full_path
    
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to author
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
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


@router.get("/submissions/{paper_id}/reviews/{review_id}/view-report")
async def view_review_report(
    paper_id: int,
    review_id: int,
    current_user: dict = Depends(get_current_user_from_token_or_query),
    db: Session = Depends(get_db)
):
    """
    View the review report file in browser.
    
    Args:
        paper_id: Paper ID
        review_id: Review ID
        
    Returns:
        Review report file for inline viewing
    """
    from fastapi.responses import FileResponse
    from pathlib import Path
    
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to author
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get the review submission
    review = db.query(ReviewSubmission).filter(
        ReviewSubmission.id == review_id,
        ReviewSubmission.paper_id == paper_id,
        ReviewSubmission.status == "submitted"
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if not review.review_report_file:
        raise HTTPException(status_code=404, detail="No review report file available for this review")
    
    # Review reports are stored with paths like "uploads/reviews/reviewer_X/file.docx"
    filepath = Path(review.review_report_file)
    
    # If path is relative, make it absolute from the backend directory
    if not filepath.is_absolute():
        from app.utils.file_handler import UPLOAD_BASE_DIR
        if review.review_report_file.startswith("uploads/"):
            filepath = UPLOAD_BASE_DIR.parent.parent / review.review_report_file
        else:
            filepath = UPLOAD_BASE_DIR.parent / review.review_report_file
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Review report file not found on server")
    
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


@router.get("/profile")
async def get_author_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get author's profile information for form pre-fill.
    
    Returns:
        Author profile data including new author detail fields
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "fname": user.fname,
        "lname": user.lname,
        "mname": user.mname,
        "title": user.title,
        "affiliation": user.affiliation,
        "specialization": user.specialization,
        "contact": user.contact,
        "address": user.address,
        # New author profile fields for form pre-fill
        "salutation": user.salutation,
        "designation": user.designation,
        "department": user.department,
        "organisation": user.organisation
    }


@router.post("/profile")
async def update_author_profile(
    profile_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update author's profile information.
    
    Args:
        profile_data: Updated profile fields
        
    Returns:
        Updated profile
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Update allowed fields (including new author detail fields)
        allowed_fields = [
            "fname", "lname", "mname", "title", "affiliation", "specialization", 
            "contact", "address", "salutation", "designation", "department", "organisation"
        ]
        for field in allowed_fields:
            if field in profile_data:
                setattr(user, field, profile_data[field])
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "message": "Profile updated successfully",
            "id": user.id,
            "email": user.email,
            "fname": user.fname,
            "lname": user.lname,
            "mname": user.mname,
            "title": user.title,
            "affiliation": user.affiliation,
            "specialization": user.specialization,
            "contact": user.contact,
            "address": user.address,
            "salutation": user.salutation,
            "designation": user.designation,
            "department": user.department,
            "organisation": user.organisation
        }
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


@router.post("/submissions/{paper_id}/request-reviewers")
async def request_additional_reviewers(
    paper_id: int,
    reviewer_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request additional reviewers for paper (suggest reviewers for the journal editor).
    
    Args:
        paper_id: Paper ID
        reviewer_data: Dictionary with suggested_reviewers list and justification
        
    Returns:
        Request confirmation
    """
    user_id = str(current_user.get("id"))
    
    # Verify paper belongs to author and is under review
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.added_by == user_id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    if paper.status != "under_review":
        raise HTTPException(status_code=400, detail="Can only request reviewers while paper is under review")
    
    suggested_reviewers = reviewer_data.get("suggested_reviewers", [])
    justification = reviewer_data.get("justification", "")
    
    if not suggested_reviewers or len(suggested_reviewers) == 0:
        raise HTTPException(status_code=400, detail="At least one reviewer must be suggested")
    
    try:
        # Store suggestion as a comment for now (could create dedicated table later)
        reviewer_comment = PaperComment(
            paper_id=paper_id,
            comment_by=user_id,
            comment_text=f"REVIEWER_REQUEST: {justification}\nSuggested reviewers: {', '.join(suggested_reviewers)}",
            added_on=datetime.utcnow()
        )
        
        db.add(reviewer_comment)
        db.commit()
        
        return {
            "message": "Reviewer request submitted successfully",
            "suggested_count": len(suggested_reviewers),
            "status": "pending_editor_review"
        }
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Error requesting reviewers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")