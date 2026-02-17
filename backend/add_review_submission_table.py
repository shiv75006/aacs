#!/usr/bin/env python3
"""
Migration script to create review_submission table for storing reviewer feedback with version control.
Supports multiple review submissions per paper with file upload tracking.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mysql.connector
from app.config import settings
from datetime import datetime

def create_review_submission_table():
    """Create review_submission table with proper schema and indexes"""
    
    config = {
        'host': settings.DB_HOST,
        'user': settings.DB_USER,
        'password': settings.DB_PASSWORD if settings.DB_PASSWORD else None,
        'database': settings.DB_NAME
    }
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("📋 Checking for review_submission table...")
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'review_submission'
        """, (settings.DB_NAME,))
        
        if cursor.fetchone()[0] > 0:
            print("✓ review_submission table already exists")
            cursor.close()
            connection.close()
            return True
        
        # Create review_submission table
        print("🔨 Creating review_submission table...")
        
        create_table_sql = """
        CREATE TABLE review_submission (
            id INT PRIMARY KEY AUTO_INCREMENT,
            
            -- Links to paper and reviewer
            paper_id INT NOT NULL,
            reviewer_id VARCHAR(100) NOT NULL,
            
            -- Link to online_review assignment
            assignment_id INT,
            
            -- Review ratings (1-5 scale)
            technical_quality INT,
            clarity INT,
            originality INT,
            significance INT,
            overall_rating INT,
            
            -- Review comments
            author_comments LONGTEXT,
            confidential_comments LONGTEXT,
            
            -- Recommendation
            recommendation VARCHAR(50),
            
            -- File upload tracking for review reports (multiple versions)
            review_report_file VARCHAR(500),
            file_version INT DEFAULT 1,
            
            -- Status and timestamps
            status VARCHAR(50) DEFAULT 'draft' NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
            submitted_at DATETIME,
            
            -- Indexes for efficient queries
            INDEX idx_paper_id (paper_id),
            INDEX idx_reviewer_id (reviewer_id),
            INDEX idx_assignment_id (assignment_id),
            INDEX idx_paper_reviewer (paper_id, reviewer_id),
            INDEX idx_status (status),
            INDEX idx_created_at (created_at DESC),
            INDEX idx_updated_at (updated_at DESC),
            INDEX idx_submitted_at (submitted_at DESC),
            
            -- Foreign key constraints
            CONSTRAINT fk_review_paper FOREIGN KEY (paper_id) REFERENCES paper(id) ON DELETE CASCADE,
            CONSTRAINT fk_review_assignment FOREIGN KEY (assignment_id) REFERENCES online_review(id) ON DELETE CASCADE
            
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_table_sql)
        connection.commit()
        print("✓ Created review_submission table")
        
        print("\n✅ Migration completed successfully!")
        print("\n📊 Table Schema:")
        
        cursor.execute("DESCRIBE review_submission")
        print("Column Name              | Type            | Null | Key | Default")
        print("-" * 70)
        for col in cursor.fetchall():
            col_name = col[0]
            col_type = str(col[1])
            is_null = col[2]
            key = col[3] if col[3] else "-"
            default = col[5] if col[5] else "-"
            print(f"{col_name:23} | {col_type:15} | {is_null:4} | {key:3} | {default}")
        
        cursor.close()
        connection.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"\n❌ Database Error: {err}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_review_submission_table()
    sys.exit(0 if success else 1)
