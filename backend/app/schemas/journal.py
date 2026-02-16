"""Pydantic schemas for journal-related requests and responses"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class JournalDetailRequest(BaseModel):
    """Journal details request schema"""
    about_journal: Optional[str] = Field(None, description="About the journal")
    chief_say: Optional[str] = Field(None, description="Chief editor's statement")
    aim_objective: Optional[str] = Field(None, description="Aims and objectives")
    criteria: Optional[str] = Field(None, description="Publication criteria")
    scope: Optional[str] = Field(None, description="Journal scope")
    guidelines: Optional[str] = Field(None, description="Submission guidelines")
    readings: Optional[str] = Field(None, description="Recommended readings")


class JournalDetailResponse(BaseModel):
    """Journal details response schema"""
    id: int = Field(..., description="Detail ID")
    journal_id: str = Field(..., description="Journal ID")
    about_journal: Optional[str] = Field(None, description="About the journal")
    chief_say: Optional[str] = Field(None, description="Chief editor's statement")
    aim_objective: Optional[str] = Field(None, description="Aims and objectives")
    criteria: Optional[str] = Field(None, description="Publication criteria")
    scope: Optional[str] = Field(None, description="Journal scope")
    guidelines: Optional[str] = Field(None, description="Submission guidelines")
    readings: Optional[str] = Field(None, description="Recommended readings")
    added_on: Optional[str] = Field(None, description="Added date")
    
    class Config:
        from_attributes = True


class JournalRequest(BaseModel):
    """Journal request schema for create/update"""
    fld_journal_name: str = Field(..., min_length=1, max_length=200, description="Journal name")
    freq: Optional[str] = Field(None, max_length=250, description="Publication frequency")
    issn_ol: Optional[str] = Field(None, max_length=250, description="ISSN Online")
    issn_prt: Optional[str] = Field(None, max_length=250, description="ISSN Print")
    cheif_editor: Optional[str] = Field(None, max_length=250, description="Chief editor name")
    co_editor: Optional[str] = Field(None, max_length=250, description="Co-editor name")
    password: str = Field(..., min_length=1, max_length=100, description="Journal password")
    abs_ind: Optional[str] = Field(None, max_length=300, description="Abstract indexing services")
    short_form: str = Field(..., min_length=1, max_length=255, description="Journal short form/abbreviation")
    journal_image: Optional[str] = Field(None, max_length=255, description="Journal image path")
    journal_logo: Optional[str] = Field(None, max_length=200, description="Journal logo path")
    guidelines: Optional[str] = Field(None, max_length=500, description="Guidelines URL/path")
    copyright: Optional[str] = Field(None, max_length=200, description="Copyright info URL/path")
    membership: Optional[str] = Field(None, max_length=200, description="Membership URL/path")
    subscription: Optional[str] = Field(None, max_length=200, description="Subscription URL/path")
    publication: Optional[str] = Field(None, max_length=200, description="Publication policy URL/path")
    advertisement: Optional[str] = Field(None, max_length=200, description="Advertisement URL/path")
    description: Optional[str] = Field(None, description="Journal description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fld_journal_name": "International Journal of Computer Science",
                "freq": "Quarterly",
                "issn_ol": "2395-0056",
                "issn_prt": "2395-0064",
                "cheif_editor": "Dr. John Smith",
                "co_editor": "Dr. Jane Doe",
                "password": "secure_journal_password",
                "abs_ind": "Indexed in Scopus, Web of Science",
                "short_form": "IJCS",
                "journal_image": "/images/journal.jpg",
                "journal_logo": "/images/logo.png",
                "guidelines": "/guidelines.pdf",
                "copyright": "/copyright.pdf",
                "membership": "/membership.pdf",
                "subscription": "/subscription.pdf",
                "publication": "/publication-policy.pdf",
                "advertisement": "/advertisement.pdf",
                "description": "A leading journal in computer science research"
            }
        }


class JournalResponse(BaseModel):
    """Journal response schema"""
    id: int = Field(..., description="Journal ID")
    name: str = Field(..., description="Journal name")
    frequency: Optional[str] = Field(None, description="Publication frequency")
    issn_online: Optional[str] = Field(None, description="ISSN Online")
    issn_print: Optional[str] = Field(None, description="ISSN Print")
    chief_editor: Optional[str] = Field(None, description="Chief editor name")
    co_editor: Optional[str] = Field(None, description="Co-editor name")
    abstract_indexing: Optional[str] = Field(None, description="Abstract indexing services")
    short_form: str = Field(..., description="Journal short form/abbreviation")
    journal_image: str = Field(..., description="Journal image path")
    journal_logo: str = Field(..., description="Journal logo path")
    guidelines: str = Field(..., description="Guidelines URL/path")
    copyright: str = Field(..., description="Copyright info URL/path")
    membership: str = Field(..., description="Membership URL/path")
    subscription: str = Field(..., description="Subscription URL/path")
    publication: str = Field(..., description="Publication policy URL/path")
    advertisement: str = Field(..., description="Advertisement URL/path")
    description: str = Field(..., description="Journal description")
    added_on: Optional[str] = Field(None, description="Added date")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "International Journal of Computer Science",
                "frequency": "Quarterly",
                "issn_online": "2395-0056",
                "issn_print": "2395-0064",
                "chief_editor": "Dr. John Smith",
                "co_editor": "Dr. Jane Doe",
                "short_form": "IJCS",
                "journal_image": "/images/journal.jpg",
                "journal_logo": "/images/logo.png",
                "description": "A leading journal in computer science research",
                "added_on": "2026-02-15"
            }
        }


class JournalListResponse(BaseModel):
    """Journal list response schema (simplified)"""
    id: int = Field(..., description="Journal ID")
    name: str = Field(..., description="Journal name")
    short_form: str = Field(..., description="Journal short form")
    issn_online: Optional[str] = Field(None, description="ISSN Online")
    issn_print: Optional[str] = Field(None, description="ISSN Print")
    chief_editor: Optional[str] = Field(None, description="Chief editor")
    journal_logo: str = Field(..., description="Journal logo path")
    description: str = Field(..., description="Journal description")
    
    class Config:
        from_attributes = True
