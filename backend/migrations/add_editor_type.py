"""
Migration script to add editor_type column to editor and user_role tables.
Run this script to add support for chief_editor and section_editor roles.
"""
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine
from sqlalchemy import text


def run_migration():
    """Add editor_type column to editor and user_role tables."""
    
    with engine.connect() as connection:
        # Add editor_type to editor table
        try:
            connection.execute(text("""
                ALTER TABLE editor 
                ADD COLUMN editor_type VARCHAR(50) DEFAULT 'section_editor'
            """))
            connection.commit()
            print("✓ Added editor_type column to editor table")
        except Exception as e:
            if "Duplicate column" in str(e) or "already exists" in str(e).lower():
                print("✓ editor_type column already exists in editor table")
            else:
                print(f"✗ Error adding editor_type to editor table: {e}")
        
        # Add editor_type to user_role table
        try:
            connection.execute(text("""
                ALTER TABLE user_role 
                ADD COLUMN editor_type VARCHAR(50) DEFAULT NULL
            """))
            connection.commit()
            print("✓ Added editor_type column to user_role table")
        except Exception as e:
            if "Duplicate column" in str(e) or "already exists" in str(e).lower():
                print("✓ editor_type column already exists in user_role table")
            else:
                print(f"✗ Error adding editor_type to user_role table: {e}")
        
        # Update existing editors without editor_type to be section_editor
        try:
            connection.execute(text("""
                UPDATE editor 
                SET editor_type = 'section_editor' 
                WHERE editor_type IS NULL
            """))
            connection.commit()
            print("✓ Updated existing editors with default editor_type")
        except Exception as e:
            print(f"✗ Error updating existing editors: {e}")
        
        print("\n✓ Migration completed successfully!")


if __name__ == "__main__":
    print("Running editor_type migration...")
    print("-" * 40)
    run_migration()
