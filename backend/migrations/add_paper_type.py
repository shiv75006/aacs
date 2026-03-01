"""
Migration script to add paper_type column to the paper table.

Run with: python -m migrations.add_paper_type
"""

import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine
from sqlalchemy import text

def run_migration():
    """Add paper_type column to paper table"""
    
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("""
            SELECT COUNT(*) as cnt FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'paper' 
            AND COLUMN_NAME = 'paper_type'
        """))
        row = result.fetchone()
        
        if row and row[0] > 0:
            print("Column 'paper_type' already exists in 'paper' table. Skipping.")
            return
        
        # Add the paper_type column
        print("Adding 'paper_type' column to 'paper' table...")
        conn.execute(text("""
            ALTER TABLE paper 
            ADD COLUMN paper_type VARCHAR(50) DEFAULT 'Full Length Article'
        """))
        conn.commit()
        print("Successfully added 'paper_type' column.")
        
        # Update existing records to have default value
        print("Setting default value for existing records...")
        conn.execute(text("""
            UPDATE paper SET paper_type = 'Full Length Article' WHERE paper_type IS NULL
        """))
        conn.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
