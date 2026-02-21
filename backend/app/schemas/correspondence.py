"""Pydantic schemas for paper correspondence"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EmailType(str, Enum):
    """Types of emails sent during paper lifecycle"""
    SUBMISSION_CONFIRMED = "submission_confirmed"
    UNDER_REVIEW = "under_review"
    REVISION_REQUESTED = "revision_requested"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PUBLISHED = "published"
    RESUBMITTED = "resubmitted"


class DeliveryStatus(str, Enum):
    """Email delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


class CorrespondenceCreate(BaseModel):
    """Schema for creating a new correspondence entry"""
    paper_id: int = Field(..., description="Paper ID")
    recipient_email: EmailStr = Field(..., description="Recipient email address")
    recipient_name: Optional[str] = Field(None, description="Recipient name")
    subject: str = Field(..., max_length=500, description="Email subject")
    body: str = Field(..., description="Email body (HTML)")
    email_type: EmailType = Field(..., description="Type of email")
    status_at_send: Optional[str] = Field(None, description="Paper status when email was sent")


class CorrespondenceResponse(BaseModel):
    """Schema for correspondence response"""
    id: int
    paper_id: int
    recipient_email: str
    recipient_name: Optional[str]
    subject: str
    body: str
    email_type: str
    status_at_send: Optional[str]
    delivery_status: str
    webhook_id: Optional[str]
    webhook_received_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    sent_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "paper_id": 123,
                "recipient_email": "author@example.com",
                "recipient_name": "John Doe",
                "subject": "Paper Submission Confirmation",
                "body": "<html>...</html>",
                "email_type": "submission_confirmed",
                "status_at_send": "submitted",
                "delivery_status": "delivered",
                "webhook_id": "abc123-xyz789",
                "webhook_received_at": "2026-02-18T10:30:00",
                "error_message": None,
                "retry_count": 0,
                "created_at": "2026-02-18T10:00:00",
                "sent_at": "2026-02-18T10:00:05"
            }
        }


class CorrespondenceListResponse(BaseModel):
    """Schema for list of correspondence entries"""
    total: int = Field(..., description="Total number of correspondence entries")
    paper_id: int = Field(..., description="Paper ID")
    paper_title: str = Field(..., description="Paper title")
    correspondence: List[CorrespondenceResponse] = Field(..., description="List of correspondence entries")


class WebhookPayload(BaseModel):
    """Schema for email delivery webhook payload"""
    webhook_id: str = Field(..., description="Unique webhook ID sent with the email")
    event_type: str = Field(..., description="Event type: delivered, bounced, failed, opened")
    timestamp: datetime = Field(..., description="Event timestamp")
    recipient_email: Optional[str] = Field(None, description="Recipient email")
    error_code: Optional[str] = Field(None, description="Error code if failed/bounced")
    error_message: Optional[str] = Field(None, description="Error message if failed/bounced")
    
    class Config:
        json_schema_extra = {
            "example": {
                "webhook_id": "abc123-xyz789",
                "event_type": "delivered",
                "timestamp": "2026-02-18T10:30:00",
                "recipient_email": "author@example.com",
                "error_code": None,
                "error_message": None
            }
        }


class WebhookResponse(BaseModel):
    """Schema for webhook response"""
    success: bool
    message: str
    correspondence_id: Optional[int] = None
