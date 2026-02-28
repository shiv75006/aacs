"""
Migration to add co_authors_json column to paper_published table.

Run with: python -m migrations.add_co_authors_json
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import SessionLocal, engine


def migrate():
    """Add co_authors_json column to paper_published table"""
    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT COUNT(*) as cnt FROM information_schema.columns 
            WHERE table_name = 'paper_published' 
            AND column_name = 'co_authors_json'
        """))
        row = result.fetchone()
        
        if row[0] > 0:
            print("Column 'co_authors_json' already exists in paper_published table. Skipping.")
            return
        
        # Add the new column
        db.execute(text("""
            ALTER TABLE paper_published 
            ADD COLUMN co_authors_json TEXT NULL 
            COMMENT 'JSON array of author details with affiliations'
        """))
        
        # Update affiliation column size
        db.execute(text("""
            ALTER TABLE paper_published 
            MODIFY COLUMN affiliation VARCHAR(500) NULL
        """))
        
        db.commit()
        print("Successfully added 'co_authors_json' column to paper_published table")
        print("Successfully updated 'affiliation' column size to VARCHAR(500)")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
