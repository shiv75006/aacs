"""
Migration: Convert journal ID columns from VARCHAR to INT

This migration converts:
1. paper.journal from VARCHAR(12) to INT
2. editor.journal_id from VARCHAR(100) to INT

This ensures type consistency for filtering papers by editor's assigned journals.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine
from sqlalchemy import text


def run_migration():
    """Run the migration to convert journal columns to INT"""
    print("Running journal column type migration...")
    print("-" * 50)
    
    with engine.connect() as conn:
        # Step 1: Clean up invalid data in paper.journal
        print("\n1. Cleaning up invalid journal data in paper table...")
        # Set empty strings and non-numeric values to NULL temporarily
        conn.execute(text("""
            UPDATE paper 
            SET journal = NULL 
            WHERE journal = '' OR journal IS NULL OR journal NOT REGEXP '^[0-9]+$'
        """))
        conn.commit()
        print("   ✓ Cleaned invalid journal values in paper table")
        
        # Step 2: Clean up invalid data in editor.journal_id
        print("\n2. Cleaning up invalid journal data in editor table...")
        conn.execute(text("""
            UPDATE editor 
            SET journal_id = NULL 
            WHERE journal_id = '' OR journal_id IS NULL OR journal_id NOT REGEXP '^[0-9]+$'
        """))
        conn.commit()
        print("   ✓ Cleaned invalid journal_id values in editor table")
        
        # Step 3: Alter paper.journal to INT
        print("\n3. Converting paper.journal from VARCHAR to INT...")
        try:
            # First check if it's already INT
            result = conn.execute(text("SHOW COLUMNS FROM paper LIKE 'journal'"))
            col_info = result.fetchone()
            if col_info and 'int' in str(col_info[1]).lower():
                print("   ⓘ paper.journal is already INT, skipping...")
            else:
                conn.execute(text("""
                    ALTER TABLE paper 
                    MODIFY COLUMN journal INT NULL
                """))
                conn.commit()
                print("   ✓ Converted paper.journal to INT")
        except Exception as e:
            print(f"   ✗ Error converting paper.journal: {e}")
            raise
        
        # Step 4: Alter editor.journal_id to INT
        print("\n4. Converting editor.journal_id from VARCHAR to INT...")
        try:
            # First check if it's already INT
            result = conn.execute(text("SHOW COLUMNS FROM editor LIKE 'journal_id'"))
            col_info = result.fetchone()
            if col_info and 'int' in str(col_info[1]).lower():
                print("   ⓘ editor.journal_id is already INT, skipping...")
            else:
                conn.execute(text("""
                    ALTER TABLE editor 
                    MODIFY COLUMN journal_id INT NULL
                """))
                conn.commit()
                print("   ✓ Converted editor.journal_id to INT")
        except Exception as e:
            print(f"   ✗ Error converting editor.journal_id: {e}")
            raise
        
        # Step 5: Verify the changes
        print("\n5. Verifying changes...")
        result = conn.execute(text("SHOW COLUMNS FROM paper LIKE 'journal'"))
        paper_col = result.fetchone()
        print(f"   paper.journal type: {paper_col[1] if paper_col else 'NOT FOUND'}")
        
        result = conn.execute(text("SHOW COLUMNS FROM editor LIKE 'journal_id'"))
        editor_col = result.fetchone()
        print(f"   editor.journal_id type: {editor_col[1] if editor_col else 'NOT FOUND'}")
        
        print("\n" + "=" * 50)
        print("✓ Migration completed successfully!")
        print("=" * 50)


def rollback_migration():
    """Rollback the migration (convert back to VARCHAR)"""
    print("Rolling back journal column type migration...")
    print("-" * 50)
    
    with engine.connect() as conn:
        # Rollback paper.journal to VARCHAR
        print("\n1. Converting paper.journal back to VARCHAR...")
        conn.execute(text("""
            ALTER TABLE paper 
            MODIFY COLUMN journal VARCHAR(12) NOT NULL DEFAULT ''
        """))
        conn.commit()
        print("   ✓ Converted paper.journal to VARCHAR(12)")
        
        # Rollback editor.journal_id to VARCHAR
        print("\n2. Converting editor.journal_id back to VARCHAR...")
        conn.execute(text("""
            ALTER TABLE editor 
            MODIFY COLUMN journal_id VARCHAR(100) NULL
        """))
        conn.commit()
        print("   ✓ Converted editor.journal_id to VARCHAR(100)")
        
        print("\n✓ Rollback completed successfully!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert journal columns to INT")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    args = parser.parse_args()
    
    if args.rollback:
        rollback_migration()
    else:
        run_migration()
