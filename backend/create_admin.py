#!/usr/bin/env python
"""Script to create an admin user in the database"""

import sys
from datetime import datetime
from app.db.database import get_db, engine
from app.db.models import Base, User
from app.core.auth import hash_password
from sqlalchemy.orm import Session

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def create_admin_user():
    """Create a new admin user"""
    db = next(get_db())
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "admin@aacsjournals.com").first()
    if existing_user:
        print(f"❌ User already exists with email: {existing_user.email}")
        return
    
    # Create new admin user
    admin_user = User(
        email="admin@aacsjournals.com",
        password=hash_password("Admin@123"),  # Hash the password
        role="Editor",  # Using Editor role (database allows: Author, Editor, BoardMember, User)
        fname="System",
        lname="Admin",
        mname="",  # Middle name (required by database)
        title="Administrator",
        affiliation="AACS",
        specialization="Administration",  # Required by database
        contact="+91-9999999999",
        address="AACS Headquarters",
        added_on=datetime.utcnow()
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print("✅ Admin user created successfully!")
    print(f"   Email: admin@aacsjournals.com")
    print(f"   Password: Admin@123")
    print(f"   Role: Editor")
    print(f"   User ID: {admin_user.id}")

if __name__ == "__main__":
    try:
        create_admin_user()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
