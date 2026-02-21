"""Articles/News API endpoints"""
from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import re
import html
import os
from app.db.database import get_db
from app.db.models import PaperPublished, Journal, News
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/v1/articles", tags=["Articles"])

# Base uploads directory for published papers
PUBLISHED_PAPERS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads", "published")


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text and clean up whitespace"""
    if not text:
        return text
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    # Replace multiple whitespace/newlines with single space
    clean = re.sub(r'\s+', ' ', clean)
    # Strip leading/trailing whitespace
    return clean.strip()


def decode_html_entities(text: str) -> str:
    """Decode HTML entities and clean up the text"""
    if not text:
        return text
    # First decode HTML entities (&quot; &ldquo; &rdquo; etc.)
    decoded = html.unescape(text)
    # Remove any remaining HTML tags
    decoded = re.sub(r'<[^>]+>', '', decoded)
    # Normalize whitespace
    decoded = re.sub(r'\s+', ' ', decoded)
    return decoded.strip()


def decode_references(text: str) -> str:
    """Decode HTML entities in references while preserving structure with newlines"""
    if not text:
        return text
    # First decode HTML entities (&quot; &ldquo; &rdquo; etc.)
    decoded = html.unescape(text)
    # Replace </div> with newline to preserve reference separation
    decoded = re.sub(r'</div>\s*', '\n', decoded, flags=re.IGNORECASE)
    # Remove remaining HTML tags
    decoded = re.sub(r'<[^>]+>', '', decoded)
    # Clean up each line
    lines = [line.strip() for line in decoded.split('\n')]
    # Filter empty lines and join with newlines
    return '\n'.join(line for line in lines if line)


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


class ArticleDetailResponse(BaseModel):
    """Detailed response model for single article"""
    id: int
    title: str
    abstract: Optional[str] = None
    p_reference: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    journal: Optional[str] = None
    journal_id: Optional[int] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    keyword: Optional[str] = None
    language: Optional[str] = None
    paper: Optional[str] = None
    access_type: Optional[str] = None
    email: Optional[str] = None
    affiliation: Optional[str] = None
    doi: Optional[str] = None
    
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
            title=strip_html_tags(article.title) or "Untitled",
            abstract=strip_html_tags(article.abstract),
            author=strip_html_tags(article.author),
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
            title=strip_html_tags(article.title) or "Untitled",
            abstract=strip_html_tags(article.abstract),
            author=strip_html_tags(article.author),
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
    response_model=ArticleDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get article details",
    description="Retrieve detailed information about a specific article"
)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """
    Get a specific article by ID with full details.
    
    - **article_id**: The article ID
    """
    article = db.query(PaperPublished).filter(PaperPublished.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )
    
    return ArticleDetailResponse(
        id=article.id,
        title=strip_html_tags(article.title) or "Untitled",
        abstract=strip_html_tags(article.abstract),
        p_reference=decode_references(article.p_reference),
        author=strip_html_tags(article.author),
        date=article.date.isoformat() if article.date else None,
        journal=article.journal,
        journal_id=article.journal_id,
        volume=article.volume,
        issue=article.issue,
        pages=strip_html_tags(article.pages),
        keyword=strip_html_tags(article.keyword),
        language=article.language,
        paper=article.paper,
        access_type=article.access_type,
        email=article.email,
        affiliation=strip_html_tags(article.affiliation),
        doi=strip_html_tags(article.doi)
    )


@router.get(
    "/{article_id}/pdf",
    status_code=status.HTTP_200_OK,
    summary="Get article PDF",
    description="Download or view the PDF file for a specific article"
)
async def get_article_pdf(article_id: int, db: Session = Depends(get_db)):
    """
    Get the PDF file for a specific article.
    
    - **article_id**: The article ID
    """
    article = db.query(PaperPublished).filter(PaperPublished.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )
    
    if not article.paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No PDF file available for this article"
        )
    
    # Check if article is open access
    if article.access_type != 'open':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This article requires a subscription to access"
        )
    
    # Try different possible locations for the PDF
    possible_paths = [
        # Published papers directory
        os.path.join(PUBLISHED_PAPERS_DIR, article.paper),
        # Journal-specific directory
        os.path.join(PUBLISHED_PAPERS_DIR, str(article.journal_id), article.paper),
        # Legacy uploads directory
        os.path.join(os.path.dirname(PUBLISHED_PAPERS_DIR), "papers", article.paper),
        # Absolute path if stored that way
        article.paper if os.path.isabs(article.paper) else None,
    ]
    
    file_path = None
    for path in possible_paths:
        if path and os.path.exists(path):
            file_path = path
            break
    
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF file not found on server. Please contact support."
        )
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=article.paper
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
            title=strip_html_tags(article.title) or "Untitled",
            abstract=strip_html_tags(article.abstract),
            author=strip_html_tags(article.author),
            date=article.date.isoformat() if article.date else None,
            journal=article.journal,
            journal_id=article.journal_id,
            volume=article.volume,
            issue=article.issue
        )
        for article in articles
    ]


# ============================================================================
# PUBLIC NEWS / ANNOUNCEMENTS ENDPOINTS
# ============================================================================

class NewsResponse(BaseModel):
    """Response model for news items"""
    id: int
    title: str
    description: Optional[str] = None
    added_on: Optional[str] = None
    journal_id: Optional[int] = None
    journal_name: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get(
    "/news",
    response_model=List[NewsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get public news and announcements",
    description="Retrieve news and announcements for the landing page (public endpoint)"
)
async def get_public_news(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of news items to skip"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of news items to return"),
    journal_id: Optional[int] = Query(None, description="Filter by specific journal ID")
):
    """
    Get public news and announcements for the landing page.
    This is a public endpoint that does not require authentication.
    
    - **skip**: Number of news items to skip (default: 0)
    - **limit**: Maximum number of news items to return (default: 10, max: 50)
    - **journal_id**: Optional filter by journal ID
    """
    query = db.query(News)
    
    if journal_id:
        query = query.filter(News.journal_id == journal_id)
    
    news_items = query.order_by(News.added_on.desc()).offset(skip).limit(limit).all()
    
    return [
        NewsResponse(
            id=item.id,
            title=item.title,
            description=item.description,
            added_on=item.added_on.isoformat() if item.added_on else None,
            journal_id=item.journal_id,
            journal_name=item.journal.fld_journal_name if item.journal else None
        )
        for item in news_items
    ]


@router.get(
    "/news/{news_id}",
    response_model=NewsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single news item",
    description="Retrieve details of a specific news item (public endpoint)"
)
async def get_news_detail(
    news_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific news item.
    This is a public endpoint that does not require authentication.
    
    - **news_id**: The ID of the news item to retrieve
    """
    news_item = db.query(News).filter(News.id == news_id).first()
    
    if not news_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"News item with ID {news_id} not found"
        )
    
    return NewsResponse(
        id=news_item.id,
        title=news_item.title,
        description=news_item.description,
        added_on=news_item.added_on.isoformat() if news_item.added_on else None,
        journal_id=news_item.journal_id,
        journal_name=news_item.journal.fld_journal_name if news_item.journal else None
    )
