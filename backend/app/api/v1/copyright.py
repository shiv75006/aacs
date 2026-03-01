"""Copyright Form API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Optional

from app.db.database import get_db
from app.db.models import CopyrightForm, Paper, User, Journal
from app.core.security import get_current_user
from app.utils.auth_helpers import check_role
from app.schemas.copyright import CopyrightFormSubmit, CopyrightFormResponse, PendingCopyrightFormsResponse
from app.utils.email_service import EmailService

router = APIRouter(prefix="/api/v1/copyright", tags=["Copyright"])


def calculate_time_remaining(deadline: datetime) -> Optional[str]:
    """Calculate human-readable time remaining until deadline"""
    if not deadline:
        return None
    
    now = datetime.utcnow()
    remaining = deadline - now
    
    if remaining.total_seconds() <= 0:
        return "Expired"
    
    hours = int(remaining.total_seconds() // 3600)
    minutes = int((remaining.total_seconds() % 3600) // 60)
    
    if hours > 24:
        days = hours // 24
        hours = hours % 24
        return f"{days}d {hours}h remaining"
    elif hours > 0:
        return f"{hours}h {minutes}m remaining"
    else:
        return f"{minutes}m remaining"


def get_form_response(form: CopyrightForm, paper: Paper, journal: Optional[Journal]) -> dict:
    """Convert CopyrightForm to response dict with paper details"""
    return {
        "id": form.id,
        "paper_id": form.paper_id,
        "author_id": form.author_id,
        "status": form.status,
        "deadline": form.deadline.isoformat() if form.deadline else None,
        "time_remaining": calculate_time_remaining(form.deadline),
        "reminder_count": form.reminder_count,
        "author_name": form.author_name,
        "author_affiliation": form.author_affiliation,
        "co_authors_consent": form.co_authors_consent,
        "copyright_agreed": form.copyright_agreed,
        "signature": form.signature,
        "signed_date": form.signed_date.isoformat() if form.signed_date else None,
        "original_work": form.original_work,
        "no_conflict": form.no_conflict,
        "rights_transfer": form.rights_transfer,
        "created_at": form.created_at.isoformat() if form.created_at else None,
        "completed_at": form.completed_at.isoformat() if form.completed_at else None,
        "paper_title": paper.title if paper else None,
        "paper_code": paper.paper_code if paper else None,
        "journal_name": journal.fld_journal_name if journal else None,
    }


@router.get("/pending", response_model=PendingCopyrightFormsResponse)
async def get_pending_copyright_forms(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pending copyright forms for the current author.
    
    Returns:
        List of pending copyright forms with paper details
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    user_id = current_user.get("id")
    
    # Get all pending copyright forms for this author
    pending_forms = db.query(CopyrightForm).filter(
        CopyrightForm.author_id == user_id,
        CopyrightForm.status == "pending"
    ).all()
    
    forms_response = []
    for form in pending_forms:
        paper = db.query(Paper).filter(Paper.id == form.paper_id).first()
        journal = None
        if paper and paper.journal:
            journal = db.query(Journal).filter(Journal.fld_id == paper.journal).first()
        
        forms_response.append(get_form_response(form, paper, journal))
    
    return {
        "pending_count": len(forms_response),
        "forms": forms_response
    }


@router.get("/{paper_id}", response_model=CopyrightFormResponse)
async def get_copyright_form(
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get copyright form details for a specific paper.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        Copyright form details with paper info
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    user_id = current_user.get("id")
    
    # Find the copyright form
    form = db.query(CopyrightForm).filter(
        CopyrightForm.paper_id == paper_id,
        CopyrightForm.author_id == user_id
    ).first()
    
    if not form:
        raise HTTPException(status_code=404, detail="Copyright form not found")
    
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    journal = None
    if paper and paper.journal:
        journal = db.query(Journal).filter(Journal.fld_id == paper.journal).first()
    
    return get_form_response(form, paper, journal)


@router.post("/{paper_id}/submit", response_model=CopyrightFormResponse)
async def submit_copyright_form(
    paper_id: int,
    form_data: CopyrightFormSubmit,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit the copyright transfer form for a paper.
    
    Args:
        paper_id: Paper ID
        form_data: Copyright form submission data
        
    Returns:
        Updated copyright form with completed status
    """
    if not check_role(current_user.get("role"), "author"):
        raise HTTPException(status_code=403, detail="Author access required")
    
    user_id = current_user.get("id")
    
    # Find the copyright form
    form = db.query(CopyrightForm).filter(
        CopyrightForm.paper_id == paper_id,
        CopyrightForm.author_id == user_id
    ).first()
    
    if not form:
        raise HTTPException(status_code=404, detail="Copyright form not found")
    
    if form.status == "completed":
        raise HTTPException(status_code=400, detail="Copyright form already submitted")
    
    if form.status == "expired":
        raise HTTPException(status_code=400, detail="Copyright form deadline has expired")
    
    # Validate all required fields are True
    if not all([
        form_data.co_authors_consent,
        form_data.copyright_agreed,
        form_data.original_work,
        form_data.no_conflict,
        form_data.rights_transfer
    ]):
        raise HTTPException(
            status_code=400, 
            detail="All agreements must be accepted to submit the copyright form"
        )
    
    # Update the form
    form.author_name = form_data.author_name
    form.author_affiliation = form_data.author_affiliation
    form.co_authors_consent = form_data.co_authors_consent
    form.copyright_agreed = form_data.copyright_agreed
    form.signature = form_data.signature
    form.signed_date = datetime.utcnow()
    form.original_work = form_data.original_work
    form.no_conflict = form_data.no_conflict
    form.rights_transfer = form_data.rights_transfer
    form.status = "completed"
    form.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(form)
    
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    journal = None
    if paper and paper.journal:
        journal = db.query(Journal).filter(Journal.fld_id == paper.journal).first()
    
    return get_form_response(form, paper, journal)


# ============================================================================
# Helper functions for creating copyright forms (called from editor API)
# ============================================================================

def create_copyright_form_for_paper(db: Session, paper_id: int, author_id: int) -> CopyrightForm:
    """
    Create a new copyright form when a paper is accepted.
    Sets deadline to 48 hours from now.
    
    Args:
        db: Database session
        paper_id: Paper ID
        author_id: Author user ID
        
    Returns:
        Created CopyrightForm instance
    """
    # Check if form already exists
    existing = db.query(CopyrightForm).filter(
        CopyrightForm.paper_id == paper_id
    ).first()
    
    if existing:
        # Reset if expired
        if existing.status == "expired":
            existing.status = "pending"
            existing.deadline = datetime.utcnow() + timedelta(hours=48)
            existing.reminder_count = 0
            existing.last_reminder_at = None
            db.commit()
            return existing
        return existing
    
    # Create new form with 48-hour deadline
    form = CopyrightForm(
        paper_id=paper_id,
        author_id=author_id,
        status="pending",
        deadline=datetime.utcnow() + timedelta(hours=48),
        reminder_count=0,
        created_at=datetime.utcnow()
    )
    
    db.add(form)
    db.commit()
    db.refresh(form)
    
    return form


def send_copyright_form_email(
    author_email: str,
    author_name: str,
    paper_title: str,
    journal_name: str,
    paper_id: int,
    deadline: datetime,
    is_reminder: bool = False,
    reminder_number: int = 0
) -> bool:
    """
    Send copyright form notification email to author.
    
    Args:
        author_email: Author's email address
        author_name: Author's full name
        paper_title: Title of the paper
        journal_name: Name of the journal
        paper_id: Paper ID
        deadline: Form submission deadline
        is_reminder: Whether this is a reminder email
        reminder_number: Reminder count (1 or 2)
        
    Returns:
        True if sent successfully
    """
    deadline_str = deadline.strftime('%B %d, %Y at %I:%M %p UTC')
    time_remaining = calculate_time_remaining(deadline)
    
    if is_reminder:
        subject = f"REMINDER: Copyright Transfer Form Required - {paper_title}"
        urgency_text = f"<p style='color: #dc2626; font-weight: bold;'>⚠️ This is reminder #{reminder_number}. Time remaining: {time_remaining}</p>"
    else:
        subject = f"Action Required: Complete Copyright Transfer Form - {paper_title}"
        urgency_text = ""
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #166534;">Copyright Transfer Form Required</h2>
                
                {urgency_text}
                
                <p>Dear {author_name},</p>
                
                <p>Congratulations! Your paper has been <strong>accepted</strong> for publication in <strong>{journal_name}</strong>.</p>
                
                <div style="background-color: #f0fdf4; padding: 15px; border-left: 4px solid #166534; margin: 20px 0;">
                    <p><strong>Paper Details:</strong></p>
                    <p><strong>Title:</strong> {paper_title}</p>
                    <p><strong>Journal:</strong> {journal_name}</p>
                </div>
                
                <p>To proceed with publication, you must complete the <strong>Copyright Transfer Form</strong> within <strong>48 hours</strong> of acceptance.</p>
                
                <div style="background-color: #fef3c7; padding: 15px; border-left: 4px solid #f59e0b; margin: 20px 0;">
                    <p><strong>⏰ Deadline:</strong> {deadline_str}</p>
                    <p><strong>Time Remaining:</strong> {time_remaining}</p>
                </div>
                
                <p>Please log in to your author dashboard and complete the copyright transfer form for your accepted paper.</p>
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="https://breakthroughpublishers.com/author/submissions/{paper_id}" 
                       style="background-color: #166534; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                       Complete Copyright Form
                    </a>
                </p>
                
                <p><strong>What you need to confirm:</strong></p>
                <ul>
                    <li>The work is original and has not been published elsewhere</li>
                    <li>All co-authors have agreed to the submission and publication</li>
                    <li>Transfer of publication rights to Breakthrough Publishers India</li>
                    <li>No conflicts of interest</li>
                </ul>
                
                <p>If you have any questions, please contact us at info@breakthroughpublishers.com.</p>
                
                <p>Best regards,<br/>
                The Breakthrough Publishers India Editorial Team</p>
            </div>
        </body>
    </html>
    """
    
    return EmailService._send_email(
        to_emails=[author_email],
        subject=subject,
        html_content=html_content
    )
