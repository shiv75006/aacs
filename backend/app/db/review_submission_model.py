"""Review Submission Model - To be added to models.py"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ReviewSubmission(Base):
    """Review Submission model for storing reviewer feedback with version control"""
    __tablename__ = "review_submission"
    __table_args__ = (
        {"mysql_engine": "InnoDB"},
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to paper and reviewer
    paper_id = Column(Integer, nullable=False, index=True)
    reviewer_id = Column(String(100), nullable=False, index=True)
    
    # Link to online_review assignment
    assignment_id = Column(Integer, nullable=True, index=True)
    
    # Review ratings (1-5 scale)
    technical_quality = Column(Integer, nullable=True)  # 1-5
    clarity = Column(Integer, nullable=True)  # 1-5
    originality = Column(Integer, nullable=True)  # 1-5
    significance = Column(Integer, nullable=True)  # 1-5
    overall_rating = Column(Integer, nullable=True)  # 1-5
    
    # Review comments
    author_comments = Column(Text, nullable=True)  # Public comments for authors
    confidential_comments = Column(Text, nullable=True)  # Private comments for editors
    
    # Recommendation
    recommendation = Column(String(50), nullable=True)  # accept, minor_revisions, major_revisions, reject
    
    # File upload tracking for review reports (multiple versions)
    review_report_file = Column(String(500), nullable=True)  # Path to uploaded review report
    file_version = Column(Integer, default=1)  # Version number for multiple uploads
    
    # Status and timestamps
    status = Column(String(50), default="draft")  # draft, submitted
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "paper_id": self.paper_id,
            "reviewer_id": self.reviewer_id,
            "assignment_id": self.assignment_id,
            "technical_quality": self.technical_quality,
            "clarity": self.clarity,
            "originality": self.originality,
            "significance": self.significance,
            "overall_rating": self.overall_rating,
            "author_comments": self.author_comments,
            "confidential_comments": self.confidential_comments,
            "recommendation": self.recommendation,
            "review_report_file": self.review_report_file,
            "file_version": self.file_version,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }
