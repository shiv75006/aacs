"""
Pydantic schemas for paper publishing and DOI management.

These schemas handle:
- Publishing accepted papers with DOI minting
- Access type management (subscription/open)
- DOI status tracking
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class AccessType(str, Enum):
    """Paper access type enum"""
    SUBSCRIPTION = "subscription"
    OPEN = "open"


class DOIStatus(str, Enum):
    """DOI registration status"""
    PENDING = "pending"
    REGISTERED = "registered"
    FAILED = "failed"


class AuthorInfo(BaseModel):
    """Author information for publishing"""
    name: str = Field(..., description="Author full name")
    email: Optional[EmailStr] = Field(None, description="Author email")
    affiliation: Optional[str] = Field(None, description="Author institution/affiliation")
    is_corresponding: bool = Field(False, description="Is corresponding author")


class PublishPaperRequest(BaseModel):
    """Request schema for publishing an accepted paper"""
    volume: str = Field(..., min_length=1, max_length=50, description="Volume number")
    issue: str = Field(..., min_length=1, max_length=50, description="Issue number")
    pages: str = Field(..., min_length=1, max_length=50, description="Page range (e.g., '1-14')")
    publication_date: Optional[date] = Field(None, description="Publication date (defaults to today)")
    language: str = Field("en", max_length=10, description="Language code")
    authors: Optional[List[AuthorInfo]] = Field(None, description="Author list with affiliations")
    references: Optional[str] = Field(None, description="References/citations text")
    paper_url: Optional[str] = Field(None, description="Full-text URL for Crossref")
    
    class Config:
        json_schema_extra = {
            "example": {
                "volume": "15",
                "issue": "2",
                "pages": "1-14",
                "publication_date": "2024-06-15",
                "language": "en",
                "authors": [
                    {
                        "name": "John Smith",
                        "email": "john.smith@university.edu",
                        "affiliation": "University of Technology",
                        "is_corresponding": True
                    }
                ],
                "references": "1. Smith, J. (2023). Previous work...",
                "paper_url": "https://aacsjournals.com/papers/IJICM-2024-001.pdf"
            }
        }


class DOIResponse(BaseModel):
    """Response schema for DOI operations"""
    doi: str = Field(..., description="The DOI identifier")
    doi_url: str = Field(..., description="Full DOI URL (https://doi.org/...)")
    status: DOIStatus = Field(..., description="Registration status")
    batch_id: Optional[str] = Field(None, description="Crossref batch ID for tracking")
    registered_at: Optional[datetime] = Field(None, description="Registration timestamp")
    message: str = Field(..., description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "doi": "10.58517/IJICM.2024.1502",
                "doi_url": "https://doi.org/10.58517/IJICM.2024.1502",
                "status": "registered",
                "batch_id": "abc123-def456",
                "registered_at": "2024-06-15T10:30:00Z",
                "message": "DOI registered successfully with Crossref"
            }
        }


class AccessTypeUpdate(BaseModel):
    """Request schema for updating paper access type"""
    access_type: AccessType = Field(..., description="New access type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_type": "open"
            }
        }


class PublishedPaperResponse(BaseModel):
    """Response schema for published paper"""
    id: int = Field(..., description="Published paper ID")
    title: str = Field(..., description="Paper title")
    abstract: str = Field(..., description="Paper abstract")
    author: str = Field(..., description="Author names")
    journal: str = Field(..., description="Journal name")
    journal_id: int = Field(..., description="Journal ID")
    volume: str = Field(..., description="Volume number")
    issue: str = Field(..., description="Issue number")
    pages: str = Field(..., description="Page range")
    date: datetime = Field(..., description="Publication date")
    keyword: str = Field(..., description="Keywords")
    language: str = Field(..., description="Language code")
    paper: Optional[str] = Field(None, description="PDF file path")
    access_type: AccessType = Field(..., description="Access type")
    doi: Optional[str] = Field(None, description="DOI identifier")
    doi_status: DOIStatus = Field(..., description="DOI registration status")
    doi_registered_at: Optional[datetime] = Field(None, description="DOI registration date")
    email: Optional[str] = Field(None, description="Corresponding author email")
    affiliation: Optional[str] = Field(None, description="Primary affiliation")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Machine Learning Applications in Healthcare",
                "abstract": "This paper explores...",
                "author": "John Smith, Jane Doe",
                "journal": "International Journal of Computer Science",
                "journal_id": 5,
                "volume": "15",
                "issue": "2",
                "pages": "1-14",
                "date": "2024-06-15T00:00:00Z",
                "keyword": "machine learning, healthcare, AI",
                "language": "en",
                "paper": "papers/IJICM-2024-001.pdf",
                "access_type": "subscription",
                "doi": "10.58517/IJICM.2024.1502",
                "doi_status": "registered",
                "doi_registered_at": "2024-06-15T10:30:00Z",
                "email": "john.smith@university.edu",
                "affiliation": "University of Technology"
            }
        }


class PublishPaperResponse(BaseModel):
    """Response schema for publish paper endpoint"""
    success: bool = Field(..., description="Whether publishing was successful")
    message: str = Field(..., description="Status message")
    published_paper: Optional[PublishedPaperResponse] = Field(None, description="Published paper data")
    doi_result: Optional[DOIResponse] = Field(None, description="DOI registration result")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Paper published successfully with DOI registration",
                "published_paper": {
                    "id": 1,
                    "title": "Machine Learning Applications",
                    "doi": "10.58517/IJICM.2024.1502"
                },
                "doi_result": {
                    "doi": "10.58517/IJICM.2024.1502",
                    "status": "registered",
                    "message": "DOI queued for registration"
                }
            }
        }


class DOIStatusCheckResponse(BaseModel):
    """Response schema for DOI status check"""
    doi: str = Field(..., description="DOI identifier")
    batch_id: str = Field(..., description="Crossref batch ID")
    status: DOIStatus = Field(..., description="Current status")
    crossref_response: Optional[str] = Field(None, description="Raw Crossref response")
    last_checked: datetime = Field(..., description="Last check timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "doi": "10.58517/IJICM.2024.1502",
                "batch_id": "abc123-def456",
                "status": "registered",
                "crossref_response": "Success",
                "last_checked": "2024-06-15T10:35:00Z"
            }
        }


class BulkAccessUpdateRequest(BaseModel):
    """Request schema for bulk access type update"""
    paper_ids: List[int] = Field(..., min_length=1, description="List of published paper IDs")
    access_type: AccessType = Field(..., description="New access type for all papers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "paper_ids": [1, 2, 3, 4, 5],
                "access_type": "open"
            }
        }


class BulkAccessUpdateResponse(BaseModel):
    """Response schema for bulk access update"""
    success: bool = Field(..., description="Whether update was successful")
    updated_count: int = Field(..., description="Number of papers updated")
    failed_ids: List[int] = Field(default=[], description="IDs that failed to update")
    message: str = Field(..., description="Status message")
