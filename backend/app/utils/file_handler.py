"""File handling utilities for paper uploads"""
import os
import shutil
from pathlib import Path
from fastapi import UploadFile
from datetime import datetime
import mimetypes

# Base directory for storing uploaded papers
UPLOAD_BASE_DIR = Path(__file__).parent.parent.parent.parent / "uploads" / "papers"
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def ensure_upload_directory():
    """Ensure upload directory exists"""
    UPLOAD_BASE_DIR.mkdir(parents=True, exist_ok=True)


async def save_uploaded_file(file: UploadFile, user_id: int, paper_id: int) -> str:
    """
    Save uploaded file to disk.
    
    Args:
        file: UploadFile object
        user_id: ID of uploading user
        paper_id: ID of paper
        
    Returns:
        Relative file path where file was saved
        
    Raises:
        ValueError: If file type not allowed or size exceeds limit
    """
    ensure_upload_directory()
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type '{file_ext}' not allowed. Allowed: {ALLOWED_EXTENSIONS}")
    
    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds maximum limit of {MAX_FILE_SIZE / 1024 / 1024}MB")
    
    # Reset file position
    await file.seek(0)
    
    # Create timestamped filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    original_name = Path(file.filename).stem  # Remove extension
    filename = f"user_{user_id}_paper_{paper_id}_{timestamp}{file_ext}"
    
    # Create user-specific subdirectory
    user_dir = UPLOAD_BASE_DIR / f"user_{user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Full file path
    file_path = user_dir / filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Return relative path for database storage
    relative_path = f"papers/user_{user_id}/{filename}"
    return relative_path


def delete_uploaded_file(file_path: str) -> bool:
    """
    Delete an uploaded file.
    
    Args:
        file_path: Relative file path
        
    Returns:
        True if deleted successfully, False otherwise
    """
    full_path = UPLOAD_BASE_DIR.parent / file_path
    
    try:
        if full_path.exists():
            full_path.unlink()
            return True
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
    
    return False


def get_file_full_path(file_path: str) -> Path:
    """
    Get full absolute path for a file.
    
    Args:
        file_path: Relative file path
        
    Returns:
        Full Path object
    """
    return UPLOAD_BASE_DIR.parent / file_path


def generate_proof_filename(paper_id: int) -> str:
    """
    Generate filename for PDF proof.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        Filename for proof PDF
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"proof_paper_{paper_id}_{timestamp}.pdf"


def anonymize_filename(file_path: str) -> str:
    """
    Create anonymized filename for blinded review.
    
    Args:
        file_path: Original file path
        
    Returns:
        Anonymized filename
    """
    file_ext = Path(file_path).suffix
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"blinded_manuscript_{timestamp}{file_ext}"
