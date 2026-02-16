#!/usr/bin/env python
"""
Script to update the user table role ENUM to include 'admin' and create admin user
"""
import os
import sys
from datetime import datetime
from passlib.context import CryptContext

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine
from app.db.models import User
from sqlalchemy import text

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def update_enum_and_create_admin():
    """Update role ENUM and create admin user"""
    db = SessionLocal()
    try:
        # First, update the ENUM to include 'admin'
        print("Updating role ENUM column...")
        db.execute(text(
            "ALTER TABLE user MODIFY role ENUM('Author','Editor','BoardMember','User','admin') "
            "CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL"
        ))
        db.commit()
        print("✅ Role ENUM updated successfully")
        
        # Check if admin user already exists
        existing = db.query(User).filter(User.role == "admin").first()
        if existing:
            print(f"Admin user already exists: {existing.email}")
            return
        
        # Create new admin user
        print("\nCreating admin user...")
        admin_user = User(
            email="admin@aacsjournals.com",
            password=hash_password("Admin@123"),
            role="admin",
            fname="System",
            lname="Administrator",
            mname="",
            title="Admin",
            affiliation="AACS",
            specialization="",
            contact="",
            address="",
            added_on=datetime.now()
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"   Email: {admin_user.email}")
        print(f"   Password: Admin@123")
        print(f"   Role: {admin_user.role}")
        print(f"   User ID: {admin_user.id}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("Updating database schema and creating admin user...\n")
    update_enum_and_create_admin()
