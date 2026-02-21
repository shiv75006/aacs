"""APScheduler configuration for background tasks"""
import logging
import asyncio
from datetime import datetime
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
