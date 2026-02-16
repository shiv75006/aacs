"""APScheduler configuration for background tasks"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


def start_scheduler():
    """Initialize and start the background scheduler for reviewer reminders"""
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


def shutdown_scheduler(scheduler):
    """Gracefully shutdown the scheduler"""
    if scheduler:
        try:
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")
