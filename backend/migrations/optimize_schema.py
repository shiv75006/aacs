"""
Database Schema Optimization Migration
======================================

This migration script:
1. Migrates existing editor data from `editor` table to `user` + `user_role` system
2. Creates user accounts for editors not already in user table
3. Creates user_role entries linking editors to journals

Run with: python -m migrations.optimize_schema
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from sqlalchemy import text
from app.db.database import SessionLocal, engine
from app.db.models import User, UserRole, Editor
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e


def migrate_editors_to_user_role():
    """
    Migrate editor table data to user + user_role system.
    
    For each editor record:
    1. Check if a user exists with that email
    2. If not, create a new user account
    3. Create a user_role entry with role='editor', journal_id, and editor_type
    """
    db = get_db()
    
    try:
        print("=" * 60)
        print("STARTING EDITOR DATA MIGRATION")
        print("=" * 60)
        
        # Get all editors
        editors = db.query(Editor).all()
        print(f"\nFound {len(editors)} editor records to migrate")
        
        migrated_count = 0
        created_users_count = 0
        skipped_count = 0
        errors = []
        
        for editor in editors:
            try:
                print(f"\n--- Processing: {editor.editor_name} ({editor.editor_email}) ---")
                
                if not editor.editor_email:
                    print(f"  SKIP: No email address")
                    skipped_count += 1
                    continue
                
                # Check if user already exists with this email
                existing_user = db.query(User).filter(
                    User.email == editor.editor_email
                ).first()
                
                if existing_user:
                    print(f"  Found existing user: ID={existing_user.id}")
                    user_id = existing_user.id
                    
                    # Update user profile with editor data if missing
                    if not existing_user.fname and editor.editor_name:
                        name_parts = editor.editor_name.split(' ', 1)
                        existing_user.fname = name_parts[0]
                        if len(name_parts) > 1:
                            existing_user.lname = name_parts[1]
                    
                    if not existing_user.affiliation and editor.editor_affiliation:
                        existing_user.affiliation = editor.editor_affiliation
                    
                    if not existing_user.department and editor.editor_department:
                        existing_user.department = editor.editor_department
                    
                    if not existing_user.contact and editor.editor_contact:
                        existing_user.contact = editor.editor_contact
                    
                    db.commit()
                    print(f"  Updated user profile with editor data")
                else:
                    # Create new user account
                    name_parts = editor.editor_name.split(' ', 1) if editor.editor_name else ['', '']
                    
                    # Use existing password if available, otherwise generate temporary
                    hashed_password = editor.password if editor.password else pwd_context.hash("TempPassword123!")
                    
                    # Use empty strings for NOT NULL columns that may be None
                    new_user = User(
                        email=editor.editor_email,
                        password=hashed_password,
                        role="Editor",  # Legacy role field
                        fname=name_parts[0] if name_parts else "",
                        lname=name_parts[1] if len(name_parts) > 1 else "",
                        mname="",  # Required NOT NULL field
                        title="",  # Required NOT NULL field
                        affiliation=editor.editor_affiliation or "",
                        specialization="",  # Required NOT NULL field
                        contact=editor.editor_contact or "",
                        address="",  # Required NOT NULL field
                        department=editor.editor_department or "",
                        added_on=editor.added_on or datetime.utcnow()
                    )
                    
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)
                    
                    user_id = new_user.id
                    created_users_count += 1
                    print(f"  Created new user: ID={user_id}")
                
                # Check if user_role entry already exists
                existing_role = db.query(UserRole).filter(
                    UserRole.user_id == user_id,
                    UserRole.role == "editor",
                    UserRole.journal_id == editor.journal_id
                ).first()
                
                if existing_role:
                    print(f"  SKIP: user_role entry already exists (ID={existing_role.id})")
                    # Update editor_type if needed
                    if editor.editor_type and existing_role.editor_type != editor.editor_type:
                        existing_role.editor_type = editor.editor_type
                        db.commit()
                        print(f"  Updated editor_type to: {editor.editor_type}")
                    skipped_count += 1
                    continue
                
                # Create user_role entry
                new_role = UserRole(
                    user_id=user_id,
                    role="editor",
                    status="approved",
                    requested_at=editor.added_on or datetime.utcnow(),
                    approved_at=editor.added_on or datetime.utcnow(),
                    journal_id=editor.journal_id,
                    editor_type=editor.editor_type or "section_editor"
                )
                
                db.add(new_role)
                db.commit()
                
                migrated_count += 1
                print(f"  Created user_role: journal_id={editor.journal_id}, type={editor.editor_type}")
                
            except Exception as e:
                db.rollback()
                error_msg = f"Error migrating {editor.editor_email}: {str(e)}"
                print(f"  ERROR: {error_msg}")
                errors.append(error_msg)
        
        print("\n" + "=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Total editors processed: {len(editors)}")
        print(f"User accounts created:   {created_users_count}")
        print(f"User_role entries created: {migrated_count}")
        print(f"Skipped (existing/no email): {skipped_count}")
        print(f"Errors: {len(errors)}")
        
        if errors:
            print("\nErrors encountered:")
            for err in errors:
                print(f"  - {err}")
        
        return {
            "total": len(editors),
            "created_users": created_users_count,
            "migrated": migrated_count,
            "skipped": skipped_count,
            "errors": errors
        }
        
    finally:
        db.close()


def verify_migration():
    """Verify the migration was successful"""
    db = get_db()
    
    try:
        print("\n" + "=" * 60)
        print("VERIFYING MIGRATION")
        print("=" * 60)
        
        # Count editors
        editor_count = db.query(Editor).count()
        print(f"\nEditor table records: {editor_count}")
        
        # Count user_role entries with role='editor'
        editor_roles = db.query(UserRole).filter(UserRole.role == "editor").count()
        print(f"User_role editor entries: {editor_roles}")
        
        # Check for editors without corresponding user_role
        editors = db.query(Editor).filter(Editor.editor_email.isnot(None)).all()
        orphaned = 0
        
        for editor in editors:
            user = db.query(User).filter(User.email == editor.editor_email).first()
            if not user:
                print(f"  Orphaned editor (no user): {editor.editor_email}")
                orphaned += 1
                continue
            
            role = db.query(UserRole).filter(
                UserRole.user_id == user.id,
                UserRole.role == "editor",
                UserRole.journal_id == editor.journal_id
            ).first()
            
            if not role:
                print(f"  Missing user_role for: {editor.editor_email} -> journal {editor.journal_id}")
                orphaned += 1
        
        if orphaned == 0:
            print("\n✓ All editors have corresponding user + user_role entries")
        else:
            print(f"\n⚠ {orphaned} editors need attention")
        
        return orphaned == 0
        
    finally:
        db.close()


def show_editor_mapping():
    """Show mapping between editor table and user_role table"""
    db = get_db()
    
    try:
        print("\n" + "=" * 60)
        print("EDITOR -> USER_ROLE MAPPING")
        print("=" * 60)
        
        editors = db.query(Editor).all()
        
        for editor in editors:
            print(f"\nEditor: {editor.editor_name} ({editor.editor_email})")
            print(f"  - Journal ID: {editor.journal_id}")
            print(f"  - Editor Type: {editor.editor_type}")
            
            if editor.editor_email:
                user = db.query(User).filter(User.email == editor.editor_email).first()
                if user:
                    print(f"  -> User ID: {user.id}")
                    
                    roles = db.query(UserRole).filter(
                        UserRole.user_id == user.id,
                        UserRole.role == "editor"
                    ).all()
                    
                    for role in roles:
                        print(f"     -> UserRole ID: {role.id}, Journal: {role.journal_id}, Type: {role.editor_type}")
                else:
                    print(f"  -> No matching user found")
            else:
                print(f"  -> No email address")
        
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database schema optimization")
    parser.add_argument("--migrate", action="store_true", help="Run editor migration")
    parser.add_argument("--verify", action="store_true", help="Verify migration status")
    parser.add_argument("--show-mapping", action="store_true", help="Show editor to user_role mapping")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    
    args = parser.parse_args()
    
    if args.show_mapping:
        show_editor_mapping()
    elif args.verify:
        verify_migration()
    elif args.migrate:
        if args.dry_run:
            print("DRY RUN MODE - No changes will be made")
            show_editor_mapping()
        else:
            result = migrate_editors_to_user_role()
            verify_migration()
    else:
        parser.print_help()
        print("\n\nUsage examples:")
        print("  python -m migrations.optimize_schema --migrate        # Run migration")
        print("  python -m migrations.optimize_schema --verify         # Verify status")
        print("  python -m migrations.optimize_schema --show-mapping   # Show current mapping")
