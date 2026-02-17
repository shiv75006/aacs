"""
Database Migration Script: Add Co-Authors Table and New Paper/User Fields
=========================================================================

This script adds:
1. New columns to the 'user' table:
   - salutation (VARCHAR 20)
   - designation (VARCHAR 100)
   - department (VARCHAR 200)
   - organisation (VARCHAR 255)

2. New columns to the 'paper' table:
   - research_area (VARCHAR 200)
   - message_to_editor (TEXT)
   - terms_accepted (BOOLEAN)

3. New 'paper_co_author' table for structured co-author storage

Run this script after backing up your database:
    cd backend
    source venv/bin/activate
    python add_coauthor_support.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import engine, Base
from app.db.models import PaperCoAuthor  # Import new model


def run_migration():
    """Execute the migration to add co-author support."""
    
    print("=" * 60)
    print("DATABASE MIGRATION: Co-Author Support")
    print("=" * 60)
    
    with engine.connect() as conn:
        # ============================================
        # 1. Add new columns to 'user' table
        # ============================================
        print("\n[1/3] Updating 'user' table...")
        
        user_columns = [
            ("salutation", "VARCHAR(20) NULL"),
            ("designation", "VARCHAR(100) NULL"),
            ("department", "VARCHAR(200) NULL"),
            ("organisation", "VARCHAR(255) NULL"),
        ]
        
        for col_name, col_def in user_columns:
            try:
                # Check if column exists
                result = conn.execute(text(f"""
                    SELECT COUNT(*) as cnt FROM information_schema.columns 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'user' 
                    AND column_name = '{col_name}'
                """))
                exists = result.fetchone()[0] > 0
                
                if not exists:
                    conn.execute(text(f"ALTER TABLE user ADD COLUMN {col_name} {col_def}"))
                    conn.commit()
                    print(f"   ✓ Added column: user.{col_name}")
                else:
                    print(f"   - Column already exists: user.{col_name}")
            except Exception as e:
                print(f"   ✗ Error adding user.{col_name}: {str(e)}")
        
        # ============================================
        # 2. Add new columns to 'paper' table
        # ============================================
        print("\n[2/3] Updating 'paper' table...")
        
        paper_columns = [
            ("research_area", "VARCHAR(200) NULL"),
            ("message_to_editor", "TEXT NULL"),
            ("terms_accepted", "BOOLEAN NOT NULL DEFAULT FALSE"),
        ]
        
        for col_name, col_def in paper_columns:
            try:
                # Check if column exists
                result = conn.execute(text(f"""
                    SELECT COUNT(*) as cnt FROM information_schema.columns 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'paper' 
                    AND column_name = '{col_name}'
                """))
                exists = result.fetchone()[0] > 0
                
                if not exists:
                    conn.execute(text(f"ALTER TABLE paper ADD COLUMN {col_name} {col_def}"))
                    conn.commit()
                    print(f"   ✓ Added column: paper.{col_name}")
                else:
                    print(f"   - Column already exists: paper.{col_name}")
            except Exception as e:
                print(f"   ✗ Error adding paper.{col_name}: {str(e)}")
        
        # ============================================
        # 3. Create 'paper_co_author' table
        # ============================================
        print("\n[3/3] Creating 'paper_co_author' table...")
        
        try:
            # Check if table exists
            result = conn.execute(text("""
                SELECT COUNT(*) as cnt FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'paper_co_author'
            """))
            exists = result.fetchone()[0] > 0
            
            if not exists:
                conn.execute(text("""
                    CREATE TABLE paper_co_author (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        paper_id INT NOT NULL,
                        salutation VARCHAR(20) NULL,
                        first_name VARCHAR(100) NOT NULL,
                        middle_name VARCHAR(100) NULL,
                        last_name VARCHAR(100) NOT NULL,
                        email VARCHAR(255) NULL,
                        designation VARCHAR(100) NULL,
                        department VARCHAR(200) NULL,
                        organisation VARCHAR(255) NULL,
                        author_order INT NOT NULL DEFAULT 1,
                        is_corresponding BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        
                        INDEX idx_paper_id (paper_id),
                        INDEX idx_email (email),
                        CONSTRAINT fk_paper_co_author_paper 
                            FOREIGN KEY (paper_id) REFERENCES paper(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                conn.commit()
                print("   ✓ Created table: paper_co_author")
            else:
                print("   - Table already exists: paper_co_author")
        except Exception as e:
            print(f"   ✗ Error creating paper_co_author table: {str(e)}")
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)
    print("\nSummary:")
    print("  • User table: 4 new columns for author profile")
    print("  • Paper table: 3 new columns for metadata")
    print("  • Paper Co-Author table: New table for structured co-authors")
    print("\nYou can now restart the backend server.")


if __name__ == "__main__":
    confirm = input("This will modify the database. Continue? (yes/no): ")
    if confirm.lower() == "yes":
        run_migration()
    else:
        print("Migration cancelled.")
