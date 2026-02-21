"""
Migration script to add paper_correspondence table.
Run this script to create the correspondence tracking table.

Usage:
    python -m migrations.add_correspondence_table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine, Base
from app.db.models import PaperCorrespondence


def run_migration():
    """Create the paper_correspondence table if it doesn't exist."""
    print("Creating paper_correspondence table...")
    
    try:
        # Create only the PaperCorrespondence table
        PaperCorrespondence.__table__.create(engine, checkfirst=True)
        print("✓ paper_correspondence table created successfully!")
        return True
    except Exception as e:
        print(f"✗ Error creating table: {str(e)}")
        return False


def verify_table():
    """Verify that the table was created correctly."""
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if 'paper_correspondence' in tables:
        print("\n✓ Table verified: paper_correspondence exists")
        
        # List columns
        columns = inspector.get_columns('paper_correspondence')
        print("\nColumns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        return True
    else:
        print("\n✗ Table not found: paper_correspondence")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Paper Correspondence Table Migration")
    print("=" * 50)
    
    success = run_migration()
    
    if success:
        verify_table()
    
    print("\n" + "=" * 50)
    print("Migration completed!")
    print("=" * 50)
