"""Email service for sending notifications"""
import smtplib
import logging
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# SMTP Configuration
SMTP_SERVER = "mail.breakthroughpublishers.com"
SMTP_PORT = 587
SMTP_USERNAME = "info@breakthroughpublishers.com"
SMTP_PASSWORD = "Aacs@2020"
EMAIL_FROM = "info@breakthroughpublishers.com"
EMAIL_FROM_NAME = "Breakthrough Publishers Journal Management System"


class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    def _send_email(
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """
        Send email via SMTP.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (fallback)
            cc: List of CC addresses
            bcc: List of BCC addresses
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
            msg['To'] = ', '.join(to_emails)
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Attach text and HTML versions
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Prepare recipient list
            recipients = to_emails + (cc or []) + (bcc or [])
            
            logger.debug(f"Attempting to send email to {to_emails} via {SMTP_SERVER}:{SMTP_PORT}")
            
            # Send email with timeout
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                logger.debug("SMTP connection established")
                server.starttls()
                logger.debug("STARTTLS successful")
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                logger.debug("Login successful")
                server.sendmail(EMAIL_FROM, recipients, msg.as_string())
                logger.debug("Email sent")
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except smtplib.SMTPAuthenticationError as auth_err:
            logger.error(f"SMTP Authentication failed: {str(auth_err)}")
            logger.error(f"Username: {SMTP_USERNAME}")
            logger.error(traceback.format_exc())
            return False
        except smtplib.SMTPException as smtp_err:
            logger.error(f"SMTP error: {str(smtp_err)}")
            logger.error(traceback.format_exc())
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def send_submission_confirmation(
        author_email: str,
        author_name: str,
        paper_title: str,
        journal_name: str,
        paper_id: int,
    ) -> bool:
        """
        Send paper submission confirmation email to author.
        
        Args:
            author_email: Author's email address
            author_name: Author's full name
            paper_title: Title of submitted paper
            journal_name: Name of target journal
            paper_id: ID of submitted paper
            
        Returns:
            True if sent successfully
        """
        subject = f"Paper Submission Confirmation - {paper_title}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #769FCD;">Submission Confirmation</h2>
                    
                    <p>Dear {author_name},</p>
                    
                    <p>Thank you for submitting your paper to <strong>{journal_name}</strong>. We have successfully received your submission.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #769FCD; margin: 20px 0;">
                        <p><strong>Submission Details:</strong></p>
                        <p><strong>Paper Title:</strong> {paper_title}</p>
                        <p><strong>Journal:</strong> {journal_name}</p>
                        <p><strong>Submission ID:</strong> {paper_id}</p>
                        <p><strong>Submission Date:</strong> {datetime.utcnow().strftime('%B %d, %Y')}</p>
                    </div>
                    
                    <p>Our editorial team will review your paper and you will receive updates on its status shortly. The typical review timeline is 4-8 weeks.</p>
                    
                    <p>You can track your submission status by logging into your author portal.</p>
                    
                    <p>If you have any questions, please don't hesitate to contact us at info@breakthroughpublishers.com.</p>
                    
                    <p>Best regards,<br/>
                    The Breakthrough Publishers Editorial Team</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"""
        Submission Confirmation
        
        Dear {author_name},
        
        Thank you for submitting your paper to {journal_name}. We have successfully received your submission.
        
        Submission Details:
        Paper Title: {paper_title}
        Journal: {journal_name}
        Submission ID: {paper_id}
        Submission Date: {datetime.utcnow().strftime('%B %d, %Y')}
        
        Our editorial team will review your paper and you will receive updates on its status shortly.
        
        Best regards,
        The Breakthrough Publishers Editorial Team
        """
        
        return EmailService._send_email(
            to_emails=[author_email],
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def send_reviewer_invitation(
        reviewer_email: str,
        reviewer_name: str,
        paper_title: str,
        paper_abstract: str,
        journal_name: str,
        invitation_link: str,
        due_date: Optional[str] = None,
    ) -> bool:
        """
        Send reviewer invitation email.
        
        Args:
            reviewer_email: Reviewer's email address
            reviewer_name: Reviewer's full name
            paper_title: Title of paper to review
            paper_abstract: Abstract of paper
            journal_name: Name of journal
            invitation_link: Magic link for invitation acceptance
            due_date: Expected review completion date
            
        Returns:
            True if sent successfully
        """
        subject = f"Invitation to Review: {paper_title}"
        
        due_info = f"<p><strong>Expected Review Due Date:</strong> {due_date}</p>" if due_date else ""
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #769FCD;">Peer Review Invitation</h2>
                    
                    <p>Dear {reviewer_name},</p>
                    
                    <p>We are pleased to invite you to serve as a peer reviewer for a paper submitted to <strong>{journal_name}</strong>.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #769FCD; margin: 20px 0;">
                        <p><strong>Paper Details:</strong></p>
                        <p><strong>Title:</strong> {paper_title}</p>
                        <p><strong>Journal:</strong> {journal_name}</p>
                        <p><strong>Abstract:</strong></p>
                        <p style="font-style: italic; margin: 10px 0;">{paper_abstract[:300]}...</p>
                        {due_info}
                    </div>
                    
                    <p>Your expertise would be invaluable in evaluating this submission. To accept or decline this invitation, please click the button below:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{invitation_link}" 
                           style="background-color: #769FCD; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            View Invitation
                        </a>
                    </div>
                    
                    <p>If you are unable to review this paper, we would appreciate if you could let us know as soon as possible so we can identify an alternative reviewer.</p>
                    
                    <p>Thank you for your continued support of our journal.</p>
                    
                    <p>Best regards,<br/>
                    The Breakthrough Publishers Editorial Team</p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(
            to_emails=[reviewer_email],
            subject=subject,
            html_content=html_content
        )
    
    @staticmethod
    def send_decision_notification(
        author_email: str,
        author_name: str,
        paper_title: str,
        journal_name: str,
        decision: str,  # accepted, rejected, major_revisions, minor_revisions
        comments: Optional[str] = None,
        revision_url: Optional[str] = None,
    ) -> bool:
        """
        Send editorial decision notification to author.
        
        Args:
            author_email: Author's email address
            author_name: Author's full name
            paper_title: Title of paper
            journal_name: Name of journal
            decision: Editorial decision (accepted, rejected, major_revisions, minor_revisions)
            comments: Editor comments
            revision_url: URL to submit revisions (if applicable)
            
        Returns:
            True if sent successfully
        """
        decision_messages = {
            'accepted': ('Your paper has been ACCEPTED', '#27ae60'),
            'rejected': ('Unfortunately, your paper has been REJECTED', '#e74c3c'),
            'major_revisions': ('Your paper requires MAJOR REVISIONS', '#f39c12'),
            'minor_revisions': ('Your paper requires MINOR REVISIONS', '#f39c12'),
        }
        
        decision_title, decision_color = decision_messages.get(decision, ('Decision Pending', '#769FCD'))
        
        subject = f"Editorial Decision: {paper_title}"
        
        revision_section = ""
        if revision_url and decision in ['major_revisions', 'minor_revisions']:
            revision_section = f"""
            <div style="margin: 20px 0; text-align: center;">
                <a href="{revision_url}" 
                   style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Submit Revised Paper
                </a>
            </div>
            """
        
        comments_section = ""
        if comments:
            comments_section = f"""
            <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid {decision_color}; margin: 20px 0;">
                <p><strong>Editor Comments:</strong></p>
                <p>{comments}</p>
            </div>
            """
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: {decision_color};">{decision_title}</h2>
                    
                    <p>Dear {author_name},</p>
                    
                    <p>We are writing to inform you about the editorial decision regarding your submission to <strong>{journal_name}</strong>.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid {decision_color}; margin: 20px 0;">
                        <p><strong>Paper Title:</strong> {paper_title}</p>
                        <p><strong>Journal:</strong> {journal_name}</p>
                        <p><strong>Decision:</strong> <span style="color: {decision_color}; font-weight: bold;">{decision.upper().replace('_', ' ')}</span></p>
                    </div>
                    
                    {comments_section}
                    
                    {revision_section}
                    
                    <p>Thank you for considering {journal_name} for publication. We appreciate your contribution to our community.</p>
                    
                    <p>If you have any questions regarding this decision, please feel free to contact us.</p>
                    
                    <p>Best regards,<br/>
                    The Breakthrough Publishers Editorial Team</p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(
            to_emails=[author_email],
            subject=subject,
            html_content=html_content
        )
    
    @staticmethod
    def send_review_reminder(
        reviewer_email: str,
        reviewer_name: str,
        paper_title: str,
        due_date: str,
        review_dashboard_url: str,
    ) -> bool:
        """
        Send reminder email to reviewer about pending review.
        
        Args:
            reviewer_email: Reviewer's email address
            reviewer_name: Reviewer's full name
            paper_title: Title of paper under review
            due_date: Expected review due date
            review_dashboard_url: URL to reviewer dashboard
            
        Returns:
            True if sent successfully
        """
        subject = f"Reminder: Pending Review - {paper_title}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #f39c12;">Review Reminder</h2>
                    
                    <p>Dear {reviewer_name},</p>
                    
                    <p>This is a gentle reminder that your review is pending for the following paper:</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #f39c12; margin: 20px 0;">
                        <p><strong>Paper Title:</strong> {paper_title}</p>
                        <p><strong>Due Date:</strong> {due_date}</p>
                    </div>
                    
                    <p>Please submit your review as soon as possible to help us maintain our publication schedule.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{review_dashboard_url}" 
                           style="background-color: #769FCD; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            Submit Review
                        </a>
                    </div>
                    
                    <p>Thank you for your valuable contribution.</p>
                    
                    <p>Best regards,<br/>
                    The Breakthrough Publishers Editorial Team</p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(
            to_emails=[reviewer_email],
            subject=subject,
            html_content=html_content
        )


# Convenience functions for common email operations
def send_submission_confirmation(
    author_email: str,
    author_name: str,
    paper_title: str,
    journal_name: str,
    paper_id: int,
) -> bool:
    """Wrapper for sending submission confirmation email"""
    return EmailService.send_submission_confirmation(
        author_email, author_name, paper_title, journal_name, paper_id
    )


def send_reviewer_invitation(
    reviewer_email: str,
    reviewer_name: str,
    paper_title: str,
    paper_abstract: str,
    journal_name: str,
    invitation_link: str,
    due_date: Optional[str] = None,
) -> bool:
    """Wrapper for sending reviewer invitation email"""
    return EmailService.send_reviewer_invitation(
        reviewer_email, reviewer_name, paper_title, paper_abstract,
        journal_name, invitation_link, due_date
    )


def send_decision_notification(
    author_email: str,
    author_name: str,
    paper_title: str,
    journal_name: str,
    decision: str,
    comments: Optional[str] = None,
    revision_url: Optional[str] = None,
) -> bool:
    """Wrapper for sending decision notification email"""
    return EmailService.send_decision_notification(
        author_email, author_name, paper_title, journal_name,
        decision, comments, revision_url
    )
