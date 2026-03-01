"""APScheduler configuration for background tasks"""
import logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


def start_scheduler():
    """Initialize and start the background scheduler for reviewer reminders and email retries"""
    try:
        scheduler = BackgroundScheduler()
        
        # Add job to send deadline reminders daily at 9 AM UTC
        # Adjust timezone as needed for your deployment
        scheduler.add_job(
            send_reviewer_reminders,
            trigger=CronTrigger(hour=9, minute=0),
            id='reviewer_deadline_reminders',
            name='Send reviewer deadline reminders at 9 AM UTC',
            replace_existing=True
        )
        
        # Add job to retry failed correspondence emails every 30 minutes
        scheduler.add_job(
            retry_failed_correspondence,
            trigger=IntervalTrigger(minutes=30),
            id='retry_failed_emails',
            name='Retry failed correspondence emails',
            replace_existing=True
        )
        
        # Add job to check and send copyright form reminders every hour
        scheduler.add_job(
            send_copyright_form_reminders,
            trigger=IntervalTrigger(hours=1),
            id='copyright_form_reminders',
            name='Send copyright form reminders',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Background scheduler started successfully")
        logger.info("Scheduled jobs:")
        for job in scheduler.get_jobs():
            logger.info(f"  - {job.name} (ID: {job.id})")
        
        return scheduler
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        return None


def send_reviewer_reminders():
    """Background job to send reviewer deadline reminders"""
    try:
        from app.utils.reviewer_email_scheduler import ReviewerEmailScheduler
        
        logger.info(f"[{datetime.utcnow()}] Starting reviewer deadline reminder batch...")
        ReviewerEmailScheduler.send_deadline_reminder()
        logger.info("Deadline reminder batch completed successfully")
        
    except Exception as e:
        logger.error(f"Error in deadline reminder batch: {str(e)}")


def retry_failed_correspondence():
    """
    Background job to retry failed correspondence emails.
    Only retries emails that have failed less than 3 times.
    """
    try:
        from app.db.database import SessionLocal
        from app.db.models import PaperCorrespondence
        from app.services.correspondence_service import send_pending_correspondence
        
        logger.info(f"[{datetime.utcnow()}] Starting failed email retry batch...")
        
        db = SessionLocal()
        try:
            # Get failed emails with retry_count < 3
            failed_emails = db.query(PaperCorrespondence).filter(
                PaperCorrespondence.delivery_status == "failed",
                PaperCorrespondence.retry_count < 3
            ).all()
            
            if not failed_emails:
                logger.info("No failed emails to retry")
                return
            
            logger.info(f"Found {len(failed_emails)} failed emails to retry")
            
            # Run async retry in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            retry_count = 0
            success_count = 0
            
            for correspondence in failed_emails:
                try:
                    # Create new session for each retry to avoid stale data
                    retry_db = SessionLocal()
                    try:
                        success = loop.run_until_complete(
                            send_pending_correspondence(retry_db, correspondence.id)
                        )
                        retry_count += 1
                        if success:
                            success_count += 1
                    finally:
                        retry_db.close()
                except Exception as e:
                    logger.error(f"Error retrying email {correspondence.id}: {str(e)}")
            
            loop.close()
            
            logger.info(f"Retry batch completed: {success_count}/{retry_count} successful")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in email retry batch: {str(e)}")


def shutdown_scheduler(scheduler):
    """Gracefully shutdown the scheduler"""
    if scheduler:
        try:
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")


def send_copyright_form_reminders():
    """
    Background job to send copyright form reminders.
    Sends reminders at 16 hours (reminder 1) and 32 hours (reminder 2) after creation.
    Also marks expired forms.
    """
    try:
        from app.db.database import SessionLocal
        from app.db.models import CopyrightForm, Paper, User, Journal
        from app.api.v1.copyright import send_copyright_form_email
        
        logger.info(f"[{datetime.utcnow()}] Starting copyright form reminder batch...")
        
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            
            # Get all pending copyright forms
            pending_forms = db.query(CopyrightForm).filter(
                CopyrightForm.status == "pending"
            ).all()
            
            if not pending_forms:
                logger.info("No pending copyright forms")
                return
            
            logger.info(f"Found {len(pending_forms)} pending copyright forms")
            
            reminder_sent = 0
            expired_count = 0
            
            for form in pending_forms:
                # Calculate hours since creation
                hours_elapsed = (now - form.created_at).total_seconds() / 3600
                
                # Check if deadline has passed
                if now >= form.deadline:
                    form.status = "expired"
                    db.commit()
                    expired_count += 1
                    logger.info(f"Copyright form {form.id} for paper {form.paper_id} marked as expired")
                    continue
                
                # Determine if we need to send a reminder
                should_send_reminder = False
                reminder_number = 0
                
                # Reminder 1: After 16 hours (one-third of 48 hours)
                if hours_elapsed >= 16 and form.reminder_count == 0:
                    should_send_reminder = True
                    reminder_number = 1
                # Reminder 2: After 32 hours (two-thirds of 48 hours)
                elif hours_elapsed >= 32 and form.reminder_count == 1:
                    should_send_reminder = True
                    reminder_number = 2
                
                if should_send_reminder:
                    # Get paper, author, and journal info
                    paper = db.query(Paper).filter(Paper.id == form.paper_id).first()
                    author = db.query(User).filter(User.id == form.author_id).first()
                    journal = None
                    if paper and paper.journal:
                        journal = db.query(Journal).filter(Journal.fld_id == paper.journal).first()
                    
                    if paper and author and author.email:
                        author_name = f"{author.fname or ''} {author.lname or ''}".strip() or "Author"
                        journal_name = journal.fld_journal_name if journal else "Breakthrough Publishers India Journal"
                        
                        # Send reminder email
                        success = send_copyright_form_email(
                            author_email=author.email,
                            author_name=author_name,
                            paper_title=paper.title,
                            journal_name=journal_name,
                            paper_id=paper.id,
                            deadline=form.deadline,
                            is_reminder=True,
                            reminder_number=reminder_number
                        )
                        
                        if success:
                            form.reminder_count = reminder_number
                            form.last_reminder_at = now
                            db.commit()
                            reminder_sent += 1
                            logger.info(f"Sent reminder {reminder_number} for copyright form {form.id}")
            
            logger.info(f"Copyright reminder batch completed: {reminder_sent} reminders sent, {expired_count} expired")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in copyright form reminder batch: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
