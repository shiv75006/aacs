"""Review submission endpoints - Add to app/api/v1/reviewer.py"""

import os
from fastapi import File, UploadFile
from datetime import datetime, timedelta


# Add these imports to the top of reviewer.py
# from app.db.models import ReviewSubmission
# from app.utils.file_handler import save_review_file


@router.get("/assignments/{review_id}/detail")
async def get_review_detail(
    review_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get review assignment detail with paper information and current review draft"""
    
    try:
        if not check_role(current_user.get("role"), "reviewer"):
            raise HTTPException(status_code=403, detail="Reviewer access required")
        
        reviewer_id = str(current_user.get("id"))
        
        # Get assignment
        assignment = db.query(OnlineReview).filter(OnlineReview.id == review_id).first()
        if not assignment or assignment.reviewer_id != reviewer_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this review")
        
        # Get paper details
        paper = db.query(Paper).filter(Paper.id == assignment.paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Get existing review submission if any
        from app.db.models import ReviewSubmission
        review_submission = db.query(ReviewSubmission).filter(
            ReviewSubmission.assignment_id == review_id,
            ReviewSubmission.reviewer_id == reviewer_id
        ).order_by(ReviewSubmission.created_at.desc()).first()
        
        # Get user info
        user = db.query(User).filter(User.id == paper.user_id).first()
        
        # Calculate due date (14 days from assignment)
        due_date = assignment.assigned_on + timedelta(days=14) if assignment.assigned_on else None
        
        return {
            "review_id": review_id,
            "paper": {
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "keywords": paper.keywords,
                "author": {
                    "name": user.fname + " " + user.lname if user else paper.author,
                    "email": user.email if user else paper.author_email,
                    "affiliation": paper.affiliation
                },
                "journal": paper.journal,
                "submitted_date": paper.submitted_on.isoformat() if paper.submitted_on else None,
                "file": paper.file
            },
            "assignment": {
                "assigned_date": assignment.assigned_on.isoformat() if assignment.assigned_on else None,
                "due_date": due_date.isoformat() if due_date else None,
                "status": assignment.review_status
            },
            "review_submission": review_submission.to_dict() if review_submission else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching review detail: {str(e)}")


@router.post("/assignments/{review_id}/save-draft")
async def save_review_draft(
    review_id: int,
    review_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save review draft and auto-update assignment to in_progress"""
    
    try:
        if not check_role(current_user.get("role"), "reviewer"):
            raise HTTPException(status_code=403, detail="Reviewer access required")
        
        reviewer_id = str(current_user.get("id"))
        
        # Get assignment
        assignment = db.query(OnlineReview).filter(OnlineReview.id == review_id).first()
        if not assignment or assignment.reviewer_id != reviewer_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this review")
        
        # Get or create review submission
        from app.db.models import ReviewSubmission
        review_submission = db.query(ReviewSubmission).filter(
            ReviewSubmission.assignment_id == review_id,
            ReviewSubmission.reviewer_id == reviewer_id
        ).first()
        
        if not review_submission:
            review_submission = ReviewSubmission(
                paper_id=assignment.paper_id,
                reviewer_id=reviewer_id,
                assignment_id=review_id,
                status="draft"
            )
            db.add(review_submission)
        
        # Update review data
        if "technical_quality" in review_data and review_data["technical_quality"] is not None:
            review_submission.technical_quality = review_data["technical_quality"]
        if "clarity" in review_data and review_data["clarity"] is not None:
            review_submission.clarity = review_data["clarity"]
        if "originality" in review_data and review_data["originality"] is not None:
            review_submission.originality = review_data["originality"]
        if "significance" in review_data and review_data["significance"] is not None:
            review_submission.significance = review_data["significance"]
        if "overall_rating" in review_data and review_data["overall_rating"] is not None:
            review_submission.overall_rating = review_data["overall_rating"]
        if "author_comments" in review_data:
            review_submission.author_comments = review_data["author_comments"]
        if "confidential_comments" in review_data:
            review_submission.confidential_comments = review_data["confidential_comments"]
        
        # Auto-update assignment to in_progress on first interaction
        if assignment.review_status == "pending":
            assignment.review_status = "in_progress"
        
        db.commit()
        db.refresh(review_submission)
        
        return {
            "success": True,
            "message": "Review draft saved",
            "review_submission": review_submission.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving review draft: {str(e)}")


@router.post("/assignments/{review_id}/submit")
async def submit_review(
    review_id: int,
    review_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit final review with validation"""
    
    try:
        if not check_role(current_user.get("role"), "reviewer"):
            raise HTTPException(status_code=403, detail="Reviewer access required")
        
        reviewer_id = str(current_user.get("id"))
        
        # Validate required fields
        required_ratings = [
            review_data.get("technical_quality"),
            review_data.get("clarity"),
            review_data.get("originality"),
            review_data.get("significance"),
            review_data.get("overall_rating")
        ]
        
        if any(r is None for r in required_ratings):
            raise HTTPException(status_code=400, detail="All ratings are required")
        
        # Validate at least one comment (50+ chars)
        author_comments = review_data.get("author_comments", "").strip()
        confidential_comments = review_data.get("confidential_comments", "").strip()
        
        total_comments = author_comments + confidential_comments
        if len(total_comments) < 50:
            raise HTTPException(status_code=400, detail="At least one comment with 50+ characters is required")
        
        # Validate recommendation
        if not review_data.get("recommendation"):
            raise HTTPException(status_code=400, detail="Recommendation is required")
        
        recommendation = review_data["recommendation"]
        valid_recommendations = ["accept", "minor_revisions", "major_revisions", "reject"]
        if recommendation not in valid_recommendations:
            raise HTTPException(status_code=400, detail=f"Invalid recommendation. Must be one of: {', '.join(valid_recommendations)}")
        
        # Get assignment
        assignment = db.query(OnlineReview).filter(OnlineReview.id == review_id).first()
        if not assignment or assignment.reviewer_id != reviewer_id:
            raise HTTPException(status_code=403, detail="Not authorized to submit this review")
        
        # Get or create review submission
        from app.db.models import ReviewSubmission
        review_submission = db.query(ReviewSubmission).filter(
            ReviewSubmission.assignment_id == review_id,
            ReviewSubmission.reviewer_id == reviewer_id
        ).first()
        
        if not review_submission:
            review_submission = ReviewSubmission(
                paper_id=assignment.paper_id,
                reviewer_id=reviewer_id,
                assignment_id=review_id,
                status="draft"
            )
            db.add(review_submission)
        
        # Update all review fields
        review_submission.technical_quality = review_data["technical_quality"]
        review_submission.clarity = review_data["clarity"]
        review_submission.originality = review_data["originality"]
        review_submission.significance = review_data["significance"]
        review_submission.overall_rating = review_data["overall_rating"]
        review_submission.author_comments = author_comments
        review_submission.confidential_comments = confidential_comments
        review_submission.recommendation = recommendation
        review_submission.status = "submitted"
        review_submission.submitted_at = datetime.utcnow()
        
        # Update assignment status
        assignment.review_status = "completed"
        assignment.submitted_on = datetime.utcnow()
        
        db.commit()
        db.refresh(review_submission)
        
        return {
            "success": True,
            "message": "Review submitted successfully",
            "review_submission": review_submission.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting review: {str(e)}")


@router.post("/assignments/{review_id}/upload-report")
async def upload_review_report(
    review_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload review report file with version control"""
    
    try:
        if not check_role(current_user.get("role"), "reviewer"):
            raise HTTPException(status_code=403, detail="Reviewer access required")
        
        reviewer_id = str(current_user.get("id"))
        
        # Validate file type
        allowed_extensions = {'.pdf', '.doc', '.docx'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {', '.join(allowed_extensions)}")
        
        # Check file size (max 10MB for review reports)
        max_size = 10 * 1024 * 1024
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > max_size:
            raise HTTPException(status_code=400, detail="File too large. Maximum size: 10MB")
        
        # Get assignment
        assignment = db.query(OnlineReview).filter(OnlineReview.id == review_id).first()
        if not assignment or assignment.reviewer_id != reviewer_id:
            raise HTTPException(status_code=403, detail="Not authorized to upload for this review")
        
        # Get review submission
        from app.db.models import ReviewSubmission
        review_submission = db.query(ReviewSubmission).filter(
            ReviewSubmission.assignment_id == review_id,
            ReviewSubmission.reviewer_id == reviewer_id
        ).first()
        
        if not review_submission:
            raise HTTPException(status_code=404, detail="Review submission not found. Please save review first.")
        
        # Create upload directory
        upload_dir = f"uploads/reviews/reviewer_{reviewer_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate filename with version control
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"paper_{assignment.paper_id}_v{review_submission.file_version}_{timestamp}{file_ext}"
        filepath = os.path.join(upload_dir, filename)
        
        # Save file
        with open(filepath, "wb") as buffer:
            buffer.write(file_content)
        
        # Update review submission
        old_file = review_submission.review_report_file
        review_submission.review_report_file = filepath
        review_submission.file_version += 1
        
        db.commit()
        db.refresh(review_submission)
        
        return {
            "success": True,
            "message": "Review report uploaded successfully",
            "file_path": filepath,
            "file_version": review_submission.file_version - 1,
            "old_file": old_file
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
