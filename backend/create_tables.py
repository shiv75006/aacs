#!/usr/bin/env python3
"""Script to create database tables"""
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import Base, engine
from app.db.models import ReviewerInvitation

if __name__ == "__main__":
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("ReviewerInvitation table created successfully!")
