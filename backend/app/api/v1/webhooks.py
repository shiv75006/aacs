"""Webhook endpoints for email delivery tracking"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import hmac
import hashlib

from app.db.database import get_db
from app.db.models import PaperCorrespondence
from app.schemas.correspondence import WebhookPayload, WebhookResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])

# Secret key for HMAC verification (should be configured in environment)
WEBHOOK_SECRET = "your-webhook-secret-key-change-in-production"


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify webhook signature using HMAC-SHA256.
    
    Args:
        payload: Raw request body
        signature: Signature from X-Webhook-Signature header
        
    Returns:
        True if signature is valid
    """
    if not signature:
        return False
    
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@router.post("/email-delivery", response_model=WebhookResponse)
async def handle_email_delivery_webhook(
    request: Request,
    payload: WebhookPayload,
    db: Session = Depends(get_db)
):
    """
    Handle email delivery status webhooks.
    
    This endpoint receives delivery status updates from the email service.
    Supported events: delivered, bounced, failed, opened
    
    Args:
        payload: Webhook payload with delivery status
        
    Returns:
        Webhook processing result
    """
    # Optional: Verify webhook signature for security
    # signature = request.headers.get("X-Webhook-Signature")
    # raw_body = await request.body()
    # if not verify_webhook_signature(raw_body, signature):
    #     raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    logger.info(f"Received email webhook: {payload.event_type} for {payload.webhook_id}")
    
    # Find correspondence by webhook_id
    correspondence = db.query(PaperCorrespondence).filter(
        PaperCorrespondence.webhook_id == payload.webhook_id
    ).first()
    
    if not correspondence:
        logger.warning(f"Correspondence not found for webhook_id: {payload.webhook_id}")
        return WebhookResponse(
            success=False,
            message=f"Correspondence not found for webhook_id: {payload.webhook_id}"
        )
    
    # Map event types to delivery status
    event_to_status = {
        "delivered": "delivered",
        "bounced": "bounced",
        "failed": "failed",
        "opened": "delivered",  # Opened implies delivered
        "sent": "sent"
    }
    
    new_status = event_to_status.get(payload.event_type.lower())
    
    if not new_status:
        logger.warning(f"Unknown event type: {payload.event_type}")
        return WebhookResponse(
            success=False,
            message=f"Unknown event type: {payload.event_type}"
        )
    
    # Update correspondence record
    correspondence.delivery_status = new_status
    correspondence.webhook_received_at = payload.timestamp or datetime.utcnow()
    
    # Store error info for failed/bounced events
    if payload.event_type.lower() in ["bounced", "failed"]:
        error_parts = []
        if payload.error_code:
            error_parts.append(f"Code: {payload.error_code}")
        if payload.error_message:
            error_parts.append(payload.error_message)
        correspondence.error_message = " - ".join(error_parts) if error_parts else f"Email {payload.event_type}"
    
    db.commit()
    
    logger.info(f"Updated correspondence {correspondence.id} status to {new_status}")
    
    return WebhookResponse(
        success=True,
        message=f"Delivery status updated to {new_status}",
        correspondence_id=correspondence.id
    )


@router.get("/email-delivery/status/{webhook_id}")
async def get_delivery_status(
    webhook_id: str,
    db: Session = Depends(get_db)
):
    """
    Get delivery status for a specific webhook_id.
    
    Args:
        webhook_id: Unique webhook identifier
        
    Returns:
        Current delivery status
    """
    correspondence = db.query(PaperCorrespondence).filter(
        PaperCorrespondence.webhook_id == webhook_id
    ).first()
    
    if not correspondence:
        raise HTTPException(status_code=404, detail="Correspondence not found")
    
    return {
        "webhook_id": webhook_id,
        "correspondence_id": correspondence.id,
        "paper_id": correspondence.paper_id,
        "delivery_status": correspondence.delivery_status,
        "sent_at": correspondence.sent_at.isoformat() if correspondence.sent_at else None,
        "webhook_received_at": correspondence.webhook_received_at.isoformat() if correspondence.webhook_received_at else None,
        "error_message": correspondence.error_message
    }
