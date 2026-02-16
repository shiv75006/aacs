#!/usr/bin/env python
"""
Script to create a true admin user in the database with role='admin'
"""
import os
import sys
from datetime import datetime
from passlib.context import CryptContext

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.models import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_admin_user():
    """Create a new admin user with role='admin'"""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing = db.query(User).filter(User.role == "admin").first()
        if existing:
            print(f"Admin user already exists: {existing.email}")
            return
        
        # Create new admin user
        admin_user = User(
            email="admin@aacsjournals.com",
            password=hash_password("Admin@123"),
            role="admin",  # True admin role
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
        print(f"❌ Error creating admin user: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating true admin user with role='admin'...")
    create_admin_user()
