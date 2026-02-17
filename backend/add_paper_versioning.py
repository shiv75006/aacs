#!/usr/bin/env python3
"""
Migration script to add paper versioning and author portal fields.
Adds version tracking columns to paper table and creates paper_version table.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mysql.connector
from app.config import settings
from datetime import datetime

def add_paper_versioning():
    """Add versioning columns to paper table and create paper_version table"""
    
    config = {
        'host': settings.DB_HOST,
        'user': settings.DB_USER,
        'password': settings.DB_PASSWORD if settings.DB_PASSWORD else None,
        'database': settings.DB_NAME
    }
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("📋 Adding paper versioning fields...")
        
        # Add columns to paper table if they don't exist
        columns_to_add = [
            ('version_number', 'INT DEFAULT 1'),
            ('revision_count', 'INT DEFAULT 0'),
            ('revision_deadline', 'DATETIME NULL'),
            ('revision_notes', 'LONGTEXT NULL'),
            ('revision_requested_date', 'DATETIME NULL'),
        ]
        
        for col_name, col_type in columns_to_add:
            cursor.execute(f"""
                SELECT COUNT(*) FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'paper' AND COLUMN_NAME = %s
            """, (settings.DB_NAME, col_name))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"ALTER TABLE paper ADD COLUMN {col_name} {col_type}")
                print(f"✓ Added column: {col_name}")
            else:
                print(f"✓ Column already exists: {col_name}")
        
        # Create paper_version table
        print("\n📋 Creating paper_version table...")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'paper_version'
        """, (settings.DB_NAME,))
        
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                CREATE TABLE paper_version (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    paper_id INT NOT NULL,
                    version_number INT NOT NULL,
                    file VARCHAR(200) NOT NULL,
                    file_size INT NULL,
                    uploaded_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    revision_reason TEXT NULL,
                    change_summary TEXT NULL,
                    uploaded_by VARCHAR(100) NOT NULL,
                    KEY idx_paper_id (paper_id),
                    KEY idx_version (paper_id, version_number)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("✓ Created paper_version table")
        else:
            print("✓ paper_version table already exists")
        
        # Add columns to online_review if they don't exist
        print("\n📋 Updating online_review table...")
        
        review_columns = [
            ('date_submitted', 'DATETIME NULL'),
            ('review_submission_id', 'INT NULL'),
            ('invitation_id', 'INT NULL'),
            ('due_date', 'DATETIME NULL'),
        ]
        
        for col_name, col_type in review_columns:
            cursor.execute(f"""
                SELECT COUNT(*) FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'online_review' AND COLUMN_NAME = %s
            """, (settings.DB_NAME, col_name))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"ALTER TABLE online_review ADD COLUMN {col_name} {col_type}")
                print(f"✓ Added column: {col_name}")
            else:
                print(f"✓ Column already exists: {col_name}")
        
        connection.commit()
        print("\n✅ Database migration completed successfully!")
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        connection.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    add_paper_versioning()
