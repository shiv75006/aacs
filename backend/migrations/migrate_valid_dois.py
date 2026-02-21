"""
Migration script to update existing paper_published records.

This script:
1. Adds new columns (doi_status, doi_registered_at, crossref_batch_id, access_type, paper_submission_id)
   if they don't exist
2. Sets access_type='subscription' for all papers with valid DOIs (DOI LIKE '10.%')
3. Sets doi_status='registered' for papers with valid DOIs
4. Leaves papers with NULL or invalid DOIs unchanged for manual review

Run this script once after deploying the updated models.

Usage:
    cd /path/to/backend
    python -m migrations.migrate_valid_dois
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings


def get_database_url():
    """Get database URL from settings"""
    return f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


def run_migration():
    """Run the DOI migration"""
    print("=" * 60)
    print("AACS Paper Published Migration Script")
    print("=" * 60)
    
    # Create database connection
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Step 1: Check and add missing columns
        print("\n[Step 1] Checking for missing columns...")
        
        columns_to_add = [
            ("doi_status", "VARCHAR(50) DEFAULT 'pending'"),
            ("doi_registered_at", "DATETIME DEFAULT NULL"),
            ("crossref_batch_id", "VARCHAR(100) DEFAULT NULL"),
            ("access_type", "VARCHAR(20) DEFAULT 'subscription'"),
            ("paper_submission_id", "INT DEFAULT NULL"),
            ("p_reference", "TEXT DEFAULT NULL"),
            ("email", "VARCHAR(100) DEFAULT NULL"),
            ("affiliation", "VARCHAR(100) DEFAULT NULL"),
        ]
        
        for col_name, col_def in columns_to_add:
            try:
                # Check if column exists
                check_sql = text(f"""
                    SELECT COUNT(*) as cnt FROM information_schema.columns 
                    WHERE table_schema = :db_name 
                    AND table_name = 'paper_published' 
                    AND column_name = :col_name
                """)
                result = session.execute(check_sql, {"db_name": settings.DB_NAME, "col_name": col_name})
                exists = result.scalar() > 0
                
                if not exists:
                    print(f"  Adding column: {col_name}")
                    alter_sql = text(f"ALTER TABLE paper_published ADD COLUMN {col_name} {col_def}")
                    session.execute(alter_sql)
                    session.commit()
                    print(f"  ✓ Column {col_name} added successfully")
                else:
                    print(f"  ✓ Column {col_name} already exists")
                    
            except Exception as e:
                print(f"  ⚠ Warning adding column {col_name}: {str(e)}")
                session.rollback()
        
        # Step 2: Count papers before migration
        print("\n[Step 2] Analyzing existing data...")
        
        count_sql = text("SELECT COUNT(*) FROM paper_published")
        total_count = session.execute(count_sql).scalar()
        print(f"  Total published papers: {total_count}")
        
        valid_doi_sql = text("SELECT COUNT(*) FROM paper_published WHERE doi IS NOT NULL AND doi LIKE '10.%'")
        valid_doi_count = session.execute(valid_doi_sql).scalar()
        print(f"  Papers with valid DOIs (10.%): {valid_doi_count}")
        
        null_doi_sql = text("SELECT COUNT(*) FROM paper_published WHERE doi IS NULL")
        null_doi_count = session.execute(null_doi_sql).scalar()
        print(f"  Papers with NULL DOIs: {null_doi_count}")
        
        invalid_doi_sql = text("SELECT COUNT(*) FROM paper_published WHERE doi IS NOT NULL AND doi NOT LIKE '10.%'")
        invalid_doi_count = session.execute(invalid_doi_sql).scalar()
        print(f"  Papers with invalid DOIs: {invalid_doi_count}")
        
        # Step 3: Update papers with valid DOIs
        print("\n[Step 3] Updating papers with valid DOIs...")
        
        update_sql = text("""
            UPDATE paper_published 
            SET access_type = 'subscription',
                doi_status = 'registered'
            WHERE doi IS NOT NULL 
            AND doi LIKE '10.%'
        """)
        result = session.execute(update_sql)
        session.commit()
        print(f"  ✓ Updated {result.rowcount} papers with valid DOIs")
        print(f"    - access_type set to 'subscription'")
        print(f"    - doi_status set to 'registered'")
        
        # Step 4: Set default access_type for papers without DOIs
        print("\n[Step 4] Setting default access_type for papers without DOIs...")
        
        update_no_doi_sql = text("""
            UPDATE paper_published 
            SET access_type = 'subscription',
                doi_status = 'pending'
            WHERE doi IS NULL OR doi = ''
        """)
        result = session.execute(update_no_doi_sql)
        session.commit()
        print(f"  ✓ Updated {result.rowcount} papers without DOIs")
        print(f"    - access_type set to 'subscription'")
        print(f"    - doi_status set to 'pending' (for future DOI assignment)")
        
        # Step 5: Handle legacy 'download' column if exists
        print("\n[Step 5] Checking legacy 'download' column...")
        
        check_download_sql = text("""
            SELECT COUNT(*) as cnt FROM information_schema.columns 
            WHERE table_schema = :db_name 
            AND table_name = 'paper_published' 
            AND column_name = 'download'
        """)
        has_download = session.execute(check_download_sql, {"db_name": settings.DB_NAME}).scalar() > 0
        
        if has_download:
            print("  Found legacy 'download' column, migrating values...")
            # Set access_type='open' for papers where download='YES'
            migrate_download_sql = text("""
                UPDATE paper_published 
                SET access_type = 'open'
                WHERE download = 'YES'
            """)
            result = session.execute(migrate_download_sql)
            session.commit()
            print(f"  ✓ Migrated {result.rowcount} papers with download='YES' to access_type='open'")
        else:
            print("  ✓ No legacy 'download' column found")
        
        # Step 6: Summary
        print("\n[Step 6] Migration Summary")
        print("-" * 40)
        
        summary_sql = text("""
            SELECT 
                access_type,
                doi_status,
                COUNT(*) as count
            FROM paper_published
            GROUP BY access_type, doi_status
            ORDER BY access_type, doi_status
        """)
        results = session.execute(summary_sql)
        
        print(f"{'Access Type':<15} {'DOI Status':<15} {'Count':<10}")
        print("-" * 40)
        for row in results:
            print(f"{row.access_type or 'NULL':<15} {row.doi_status or 'NULL':<15} {row.count:<10}")
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        session.rollback()
        return False
        
    finally:
        session.close()


def show_preview():
    """Preview what the migration will do without making changes"""
    print("=" * 60)
    print("AACS Paper Published Migration - PREVIEW MODE")
    print("=" * 60)
    
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Show sample DOIs
        print("\nSample DOIs in database:")
        sample_sql = text("""
            SELECT id, title, doi, 
                   CASE WHEN doi LIKE '10.%' THEN 'VALID' ELSE 'INVALID/NULL' END as doi_validity
            FROM paper_published 
            LIMIT 10
        """)
        results = session.execute(sample_sql)
        
        for row in results:
            doi_display = row.doi[:50] if row.doi else 'NULL'
            print(f"  ID {row.id}: {doi_display} ({row.doi_validity})")
        
        print("\nWhat the migration will do:")
        print("  1. Add new columns if missing (doi_status, access_type, etc.)")
        print("  2. Set access_type='subscription' for papers with valid DOIs")
        print("  3. Set doi_status='registered' for papers with valid DOIs")
        print("  4. Set access_type='subscription' for papers without DOIs")
        print("  5. Migrate legacy 'download' field values if present")
        
    finally:
        session.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate paper_published table for DOI and access control")
    parser.add_argument("--preview", action="store_true", help="Preview changes without applying them")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    if args.preview:
        show_preview()
    else:
        if not args.force:
            print("This will modify the paper_published table.")
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() != "yes":
                print("Migration cancelled.")
                sys.exit(0)
        
        success = run_migration()
        sys.exit(0 if success else 1)
