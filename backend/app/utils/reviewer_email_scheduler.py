"""Email notification scheduler for reviewer reminders and updates"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.models import OnlineReview, User, Paper, Journal, ReviewerInvitation
from app.utils.email_service import EmailService

logger = logging.getLogger(__name__)


class ReviewerEmailScheduler:
    """Handles scheduled email notifications for reviewers"""

    @staticmethod
    def send_deadline_reminder():
        """
        Send email reminders to reviewers 48 hours before deadline at 9AM.
        This should be called by a scheduler (APScheduler or Celery) daily at 9AM.
        """
        try:
            from app.db.database import SessionLocal
            db = SessionLocal()
            
            # Calculate target date (exactly 48 hours from now)
            now = datetime.utcnow()
            # Get reviews due in approximately 48 hours
            reminder_start = now + timedelta(hours=47.5)
            reminder_end = now + timedelta(hours=48.5)
            
            # Query for reviews due in this time window
            pending_reviews = db.query(OnlineReview).filter(
                and_(
                    OnlineReview.due_date >= reminder_start,
                    OnlineReview.due_date <= reminder_end,
                    OnlineReview.review_status.in_(["pending", "in_progress"])
                )
            ).all()
            
            logger.info(f"Found {len(pending_reviews)} reviews with deadline reminder due")
            
            for review in pending_reviews:
                try:
                    ReviewerEmailScheduler._send_individual_deadline_reminder(db, review)
                except Exception as e:
                    logger.error(f"Failed to send reminder for review {review.id}: {str(e)}")
            
            db.close()
            logger.info("Deadline reminder batch completed")
            
        except Exception as e:
            logger.error(f"Error in deadline reminder scheduler: {str(e)}")

    @staticmethod
    def _send_individual_deadline_reminder(db: Session, review: OnlineReview):
        """Send deadline reminder email to a specific reviewer"""
        try:
            # Fetch related data
            paper = db.query(Paper).filter(Paper.id == review.paper_id).first()
            reviewer = db.query(User).filter(User.email == review.reviewer_email).first()
            journal = db.query(Journal).filter(Journal.fld_id == paper.journal).first() if paper else None
            
            if not reviewer or not paper:
                logger.warning(f"Missing reviewer or paper for review {review.id}")
                return
            
            # Calculate time remaining
            now = datetime.utcnow()
            time_remaining = review.due_date - now
            hours_remaining = int(time_remaining.total_seconds() / 3600)
            
            # Build email content
            invitation_link = f"https://breakthroughpublishers.com/reviewer/assignments/{review.id}/review"
            
            subject = f"[REMINDER] Review Due in 48 Hours - {paper.title}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #d9534f;">⏰ Review Deadline Reminder</h2>
                        
                        <p>Dear {reviewer.fname},</p>
                        
                        <p>This is a friendly reminder that your paper review is due in <strong>48 hours</strong>.</p>
                        
                        <div style="background: #f9f9f9; padding: 16px; border-left: 4px solid #d9534f; margin: 20px 0;">
                            <h3 style="margin: 0 0 12px 0;">{paper.title}</h3>
                            <p style="margin: 0;"><strong>Journal:</strong> {journal.fld_journal_name if journal else 'N/A'}</p>
                            <p style="margin: 0;"><strong>Due Date:</strong> {review.due_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                            <p style="margin: 0;"><strong>Time Remaining:</strong> {hours_remaining} hours</p>
                        </div>
                        
                        <p>Please log into the reviewer portal to submit your review:</p>
                        
                        <a href="{invitation_link}" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                            Complete Your Review
                        </a>
                        
                        <p style="margin-top: 30px; color: #666; font-size: 12px;">
                            If you have any questions about the review or need to request an extension, please contact the editor at editor@breakthroughpublishers.com.
                        </p>
                        
                        <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                        <p style="color: #999; font-size: 11px; margin: 0;">
                            Breakthrough Publishers Journal Management System | {datetime.utcnow().strftime('%B %d, %Y')}
                        </p>
                    </div>
                </body>
            </html>
            """
            
            text_content = f"""
Dear {reviewer.fname},

This is a friendly reminder that your paper review is due in 48 hours.

PAPER: {paper.title}
JOURNAL: {journal.fld_journal_name if journal else 'N/A'}
DUE DATE: {review.due_date.strftime('%B %d, %Y at %I:%M %p')}
TIME REMAINING: {hours_remaining} hours

Please log into the reviewer portal to submit your review:
{invitation_link}

If you have any questions or need to request an extension, contact the editor at editor@breakthroughpublishers.com.

---
Breakthrough Publishers Journal Management System
            """
            
            # Send email
            success = EmailService._send_email(
                to_emails=[review.reviewer_email],
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                logger.info(f"Deadline reminder sent to {review.reviewer_email} for review {review.id}")
            else:
                logger.error(f"Failed to send deadline reminder to {review.reviewer_email}")
                
        except Exception as e:
            logger.error(f"Error sending deadline reminder: {str(e)}")

    @staticmethod
    def send_review_update_notification(reviewer_email: str, reviewer_name: str, 
                                        paper_title: str, journal_name: str, 
                                        update_type: str, message: str = ""):
        """
        Send email notification for review-related updates (new assignment, submission confirmation, etc.)
        
        Args:
            reviewer_email: Reviewer's email address
            reviewer_name: Reviewer's name
            paper_title: Title of the paper
            journal_name: Name of the journal
            update_type: Type of update ('new_assignment', 'submission_confirmed', 'admin_message')
            message: Optional custom message
        """
        try:
            subject_map = {
                'new_assignment': f"New Paper Review Assignment - {paper_title}",
                'submission_confirmed': f"Review Submission Confirmed - {paper_title}",
                'admin_message': f"Important Message from {journal_name} Editorial Team",
            }
            
            subject = subject_map.get(update_type, "Journal Notification")
            
            # Build email content based on update type
            if update_type == 'new_assignment':
                html_content = ReviewerEmailScheduler._build_new_assignment_email(
                    reviewer_name, paper_title, journal_name
                )
            elif update_type == 'submission_confirmed':
                html_content = ReviewerEmailScheduler._build_submission_confirmed_email(
                    reviewer_name, paper_title, journal_name
                )
            elif update_type == 'admin_message':
                html_content = ReviewerEmailScheduler._build_admin_message_email(
                    reviewer_name, journal_name, message
                )
            else:
                logger.warning(f"Unknown update type: {update_type}")
                return False
            
            success = EmailService._send_email(
                to_emails=[reviewer_email],
                subject=subject,
                html_content=html_content,
                text_content=f"Please view this email in HTML format for best results."
            )
            
            if success:
                logger.info(f"Update notification ({update_type}) sent to {reviewer_email}")
            else:
                logger.error(f"Failed to send update notification to {reviewer_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending update notification: {str(e)}")
            return False

    @staticmethod
    def _build_new_assignment_email(reviewer_name: str, paper_title: str, journal_name: str) -> str:
        """Build HTML email for new assignment notification"""
        assignment_link = "https://breakthroughpublishers.com/reviewer/assignments"
        
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #3b82f6;">📋 New Review Assignment</h2>
                    
                    <p>Dear {reviewer_name},</p>
                    
                    <p>You have been assigned to review a new paper for <strong>{journal_name}</strong>.</p>
                    
                    <div style="background: #f0f9ff; padding: 16px; border-left: 4px solid #3b82f6; margin: 20px 0;">
                        <h3 style="margin: 0 0 12px 0;">{paper_title}</h3>
                        <p style="margin: 0;">You have 14 days to complete this review.</p>
                    </div>
                    
                    <p>Please log into the reviewer portal to view the paper details and begin your review.</p>
                    
                    <a href="{assignment_link}" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                        View My Assignments
                    </a>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 12px;">
                        If you cannot complete this review, please decline within 48 hours so we can find another reviewer.
                    </p>
                    
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                    <p style="color: #999; font-size: 11px; margin: 0;">
                        Breakthrough Publishers Journal Management System | {datetime.utcnow().strftime('%B %d, %Y')}
                    </p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def _build_submission_confirmed_email(reviewer_name: str, paper_title: str, journal_name: str) -> str:
        """Build HTML email for submission confirmation"""
        history_link = "https://breakthroughpublishers.com/reviewer/history"
        
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #10b981;">✓ Review Submission Confirmed</h2>
                    
                    <p>Dear {reviewer_name},</p>
                    
                    <p>Thank you for submitting your review! Your feedback has been successfully received and recorded.</p>
                    
                    <div style="background: #dcfce7; padding: 16px; border-left: 4px solid #10b981; margin: 20px 0;">
                        <h3 style="margin: 0 0 12px 0;">{paper_title}</h3>
                        <p style="margin: 0;"><strong>Journal:</strong> {journal_name}</p>
                        <p style="margin: 0;"><strong>Submission Time:</strong> {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                    
                    <p>Your review will now be evaluated by the editorial team. You can view your submitted review in your history section.</p>
                    
                    <a href="{history_link}" style="display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                        View Review History
                    </a>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 12px;">
                        We appreciate your contribution to the peer review process. Your expertise and feedback help maintain the quality of our journals.
                    </p>
                    
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                    <p style="color: #999; font-size: 11px; margin: 0;">
                        Breakthrough Publishers Journal Management System | {datetime.utcnow().strftime('%B %d, %Y')}
                    </p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def _build_admin_message_email(reviewer_name: str, journal_name: str, message: str) -> str:
        """Build HTML email for admin messages"""
        
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #f59e0b;">📢 Message from {journal_name}</h2>
                    
                    <p>Dear {reviewer_name},</p>
                    
                    <div style="background: #fffbeb; padding: 16px; border-left: 4px solid #f59e0b; margin: 20px 0;">
                        {message}
                    </div>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 12px;">
                        If you have any questions, please contact the editorial team.
                    </p>
                    
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                    <p style="color: #999; font-size: 11px; margin: 0;">
                        Breakthrough Publishers Journal Management System | {datetime.utcnow().strftime('%B %d, %Y')}
                    </p>
                </div>
            </body>
        </html>
        """
