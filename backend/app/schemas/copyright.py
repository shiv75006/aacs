"""Pydantic schemas for copyright form requests and responses"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CopyrightFormSubmit(BaseModel):
    """Schema for submitting a copyright form"""
    author_name: str = Field(..., min_length=1, max_length=255, description="Author's full name")
    author_affiliation: str = Field(..., min_length=1, max_length=500, description="Author's institutional affiliation")
    co_authors_consent: bool = Field(..., description="Confirmation that all co-authors have agreed")
    copyright_agreed: bool = Field(..., description="Agreement to copyright transfer")
    signature: str = Field(..., min_length=1, max_length=255, description="Digital signature (typed name)")
    original_work: bool = Field(..., description="Confirms work is original")
    no_conflict: bool = Field(..., description="Confirms no conflict of interest")
    rights_transfer: bool = Field(..., description="Agrees to transfer publication rights")
    
    class Config:
        json_schema_extra = {
            "example": {
                "author_name": "Dr. John Doe",
                "author_affiliation": "University of Example, Department of Computer Science",
                "co_authors_consent": True,
                "copyright_agreed": True,
                "signature": "John Doe",
                "original_work": True,
                "no_conflict": True,
                "rights_transfer": True
            }
        }


class CopyrightFormResponse(BaseModel):
    """Schema for copyright form response"""
    id: int
    paper_id: int
    author_id: int
    status: str
    deadline: Optional[str] = None
    time_remaining: Optional[str] = None  # Human readable time remaining
    reminder_count: int
    author_name: Optional[str] = None
    author_affiliation: Optional[str] = None
    co_authors_consent: Optional[bool] = None
    copyright_agreed: Optional[bool] = None
    signature: Optional[str] = None
    signed_date: Optional[str] = None
    original_work: Optional[bool] = None
    no_conflict: Optional[bool] = None
    rights_transfer: Optional[bool] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    # Paper details for context
    paper_title: Optional[str] = None
    paper_code: Optional[str] = None
    journal_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class PendingCopyrightFormsResponse(BaseModel):
    """Schema for list of pending copyright forms"""
    pending_count: int
    forms: list[CopyrightFormResponse]
