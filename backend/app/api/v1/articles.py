"""Articles/News API endpoints"""
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import PaperPublished
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/v1/articles", tags=["Articles"])


class ArticleResponse(BaseModel):
    """Response model for articles"""
    id: int
    title: str
    abstract: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    journal: Optional[str] = None
    journal_id: Optional[int] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get(
    "/",
    response_model=List[ArticleResponse],
    status_code=status.HTTP_200_OK,
    summary="List published articles",
    description="Retrieve a list of published articles with pagination support"
)
async def list_articles(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of articles to return")
):
    """
    Get all published articles with pagination support.
    
    - **skip**: Number of articles to skip (default: 0)
    - **limit**: Maximum number of articles to return (default: 10, max: 100)
    """
    articles = db.query(PaperPublished).order_by(
        PaperPublished.date.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        ArticleResponse(
            id=article.id,
            title=article.title or "Untitled",
            abstract=article.abstract,
            author=article.author,
            date=article.date.isoformat() if article.date else None,
            journal=article.journal,
            journal_id=article.journal_id,
            volume=article.volume,
            issue=article.issue
        )
        for article in articles
    ]


@router.get(
    "/latest",
    response_model=List[ArticleResponse],
    status_code=status.HTTP_200_OK,
    summary="Get latest articles",
    description="Retrieve the latest published articles"
)
async def get_latest_articles(
    db: Session = Depends(get_db),
    limit: int = Query(5, ge=1, le=50, description="Number of latest articles to return")
):
    """
    Get the latest published articles.
    
    - **limit**: Maximum number of articles to return (default: 5, max: 50)
    """
    articles = db.query(PaperPublished).order_by(
        PaperPublished.date.desc()
    ).limit(limit).all()
    
    return [
        ArticleResponse(
            id=article.id,
            title=article.title or "Untitled",
            abstract=article.abstract,
            author=article.author,
            date=article.date.isoformat() if article.date else None,
            journal=article.journal,
            journal_id=article.journal_id,
            volume=article.volume,
            issue=article.issue
        )
        for article in articles
    ]


@router.get(
    "/{article_id}",
    response_model=ArticleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get article details",
    description="Retrieve detailed information about a specific article"
)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """
    Get a specific article by ID.
    
    - **article_id**: The article ID
    """
    article = db.query(PaperPublished).filter(PaperPublished.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )
    
    return ArticleResponse(
        id=article.id,
        title=article.title or "Untitled",
        abstract=article.abstract,
        author=article.author,
        date=article.date.isoformat() if article.date else None,
        journal=article.journal,
        journal_id=article.journal_id,
        volume=article.volume,
        issue=article.issue
    )


@router.get(
    "/journal/{journal_id}",
    response_model=List[ArticleResponse],
    status_code=status.HTTP_200_OK,
    summary="Get articles by journal",
    description="Retrieve articles published in a specific journal"
)
async def get_articles_by_journal(
    journal_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of articles to return")
):
    """
    Get articles published in a specific journal.
    
    - **journal_id**: The journal ID
    - **skip**: Number of articles to skip (default: 0)
    - **limit**: Maximum number of articles to return (default: 10, max: 100)
    """
    articles = db.query(PaperPublished).filter(
        PaperPublished.journal_id == journal_id
    ).order_by(
        PaperPublished.date.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        ArticleResponse(
            id=article.id,
            title=article.title or "Untitled",
            abstract=article.abstract,
            author=article.author,
            date=article.date.isoformat() if article.date else None,
            journal=article.journal,
            journal_id=article.journal_id,
            volume=article.volume,
            issue=article.issue
        )
        for article in articles
    ]
