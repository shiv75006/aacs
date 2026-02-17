#!/usr/bin/env python3
"""
Migration script to add review status tracking fields to online_review table
Run this script to add the necessary columns to the database
"""
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def add_review_fields():
    """Add submitted_on and review_status fields to online_review table"""
    
    config = {
        'host': settings.DB_HOST,
        'user': settings.DB_USER,
        'password': settings.DB_PASSWORD if settings.DB_PASSWORD else None,
        'database': settings.DB_NAME
    }
    
    connection = None
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Check if columns already exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='online_review' AND COLUMN_NAME='review_status'
        """)
        
        if cursor.fetchone():
            print("Columns already exist. Skipping migration.")
            return
        
        # Add submitted_on column
        alter_sql_1 = """
        ALTER TABLE `online_review` 
        ADD COLUMN `submitted_on` DATETIME NULL AFTER `assigned_on`
        """
        cursor.execute(alter_sql_1)
        print("✓ Added submitted_on column")
        
        # Add review_status column with default value
        alter_sql_2 = """
        ALTER TABLE `online_review` 
        ADD COLUMN `review_status` VARCHAR(50) DEFAULT 'pending' NOT NULL AFTER `submitted_on`
        """
        cursor.execute(alter_sql_2)
        print("✓ Added review_status column")
        
        # Create index on review_status for better query performance
        alter_sql_3 = """
        CREATE INDEX idx_review_status ON `online_review`(`reviewer_id`, `review_status`)
        """
        try:
            cursor.execute(alter_sql_3)
            print("✓ Created index on reviewer_id and review_status")
        except Error:
            print("✓ Index already exists or could not be created (this is OK)")
        
        connection.commit()
        print("\n✅ Migration completed successfully!")
        
    except Error as e:
        print(f"❌ Error: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("Running migration to add review tracking fields...\n")
    add_review_fields()
