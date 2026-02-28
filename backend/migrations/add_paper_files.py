"""
Migration: Add title_page and blinded_manuscript columns to papers table
Run this script to add the new columns for two-file paper submission.
"""

import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import engine

def migrate():
    """Add title_page and blinded_manuscript columns to papers table."""
    
    with engine.connect() as conn:
        try:
            # Check if columns already exist
            result = conn.execute(text("SHOW COLUMNS FROM papers LIKE 'title_page'"))
            if result.fetchone():
                print("Column 'title_page' already exists, skipping...")
            else:
                conn.execute(text("ALTER TABLE papers ADD COLUMN title_page VARCHAR(200) DEFAULT '' AFTER file_path"))
                print("Added 'title_page' column to papers table")
            
            result = conn.execute(text("SHOW COLUMNS FROM papers LIKE 'blinded_manuscript'"))
            if result.fetchone():
                print("Column 'blinded_manuscript' already exists, skipping...")
            else:
                conn.execute(text("ALTER TABLE papers ADD COLUMN blinded_manuscript VARCHAR(200) DEFAULT '' AFTER title_page"))
                print("Added 'blinded_manuscript' column to papers table")
            
            conn.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
