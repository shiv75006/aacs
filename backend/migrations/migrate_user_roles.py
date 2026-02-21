"""
Migration script to:
1. Create user_role and role_request tables
2. Migrate existing user.role values to user_role table

Run: python -m migrations.migrate_user_roles [--force]
"""
import sys
import argparse
from datetime import datetime
from sqlalchemy import text
sys.path.insert(0, '/Users/shivyanshusaini/Desktop/AACS/backend')

from app.db.database import SessionLocal, engine


def create_tables(db):
    """Create user_role and role_request tables if they don't exist"""
    
    # Create user_role table
    create_user_role = """
    CREATE TABLE IF NOT EXISTS user_role (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        role VARCHAR(50) NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'approved',
        requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        approved_by INT NULL,
        approved_at DATETIME NULL,
        rejected_reason TEXT NULL,
        journal_id INT NULL,
        INDEX idx_user_id (user_id),
        INDEX idx_role (role),
        INDEX idx_status (status),
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY (approved_by) REFERENCES user(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    
    # Create role_request table
    create_role_request = """
    CREATE TABLE IF NOT EXISTS role_request (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        requested_role VARCHAR(50) NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        reason TEXT NULL,
        requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        processed_by INT NULL,
        processed_at DATETIME NULL,
        admin_notes TEXT NULL,
        INDEX idx_user_id (user_id),
        INDEX idx_status (status),
        INDEX idx_requested_role (requested_role),
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY (processed_by) REFERENCES user(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    
    print("Creating user_role table...")
    db.execute(text(create_user_role))
    
    print("Creating role_request table...")
    db.execute(text(create_role_request))
    
    db.commit()
    print("Tables created successfully!")


def migrate_existing_roles(db, force=False):
    """Migrate existing user.role values to user_role table"""
    
    # Check if migration already done
    existing_count = db.execute(text("SELECT COUNT(*) FROM user_role")).scalar()
    if existing_count > 0 and not force:
        print(f"user_role table already has {existing_count} entries.")
        print("Use --force to run migration anyway.")
        return
    
    # Get all users with valid roles
    users_query = """
    SELECT id, role, email, added_on 
    FROM user 
    WHERE role IS NOT NULL 
    AND LOWER(role) IN ('author', 'reviewer', 'editor', 'admin')
    """
    
    users = db.execute(text(users_query)).fetchall()
    print(f"Found {len(users)} users with valid roles to migrate")
    
    migrated = 0
    skipped = 0
    
    for user in users:
        user_id = user[0]
        role = user[1].lower()
        email = user[2]
        added_on = user[3] or datetime.utcnow()
        
        # Check if already exists
        check_query = """
        SELECT id FROM user_role 
        WHERE user_id = :user_id AND LOWER(role) = :role
        """
        existing = db.execute(text(check_query), {"user_id": user_id, "role": role}).first()
        
        if existing:
            skipped += 1
            continue
        
        # Insert role
        insert_query = """
        INSERT INTO user_role (user_id, role, status, requested_at, approved_at)
        VALUES (:user_id, :role, 'approved', :requested_at, :approved_at)
        """
        db.execute(text(insert_query), {
            "user_id": user_id,
            "role": role,
            "requested_at": added_on,
            "approved_at": added_on
        })
        migrated += 1
        print(f"  Migrated: {email} -> {role}")
    
    db.commit()
    print(f"\nMigration complete!")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped (already exists): {skipped}")


def show_statistics(db):
    """Show current role statistics"""
    print("\n" + "="*50)
    print("CURRENT ROLE STATISTICS")
    print("="*50)
    
    # Legacy role field stats
    legacy_stats = db.execute(text("""
        SELECT LOWER(role) as role, COUNT(*) as count
        FROM user
        WHERE role IS NOT NULL AND role != ''
        GROUP BY LOWER(role)
        ORDER BY count DESC
    """)).fetchall()
    
    print("\nLegacy role field:")
    for row in legacy_stats:
        print(f"  {row[0]}: {row[1]}")
    
    # UserRole table stats
    try:
        role_stats = db.execute(text("""
            SELECT role, status, COUNT(*) as count
            FROM user_role
            GROUP BY role, status
            ORDER BY role, status
        """)).fetchall()
        
        print("\nuser_role table:")
        for row in role_stats:
            print(f"  {row[0]} ({row[1]}): {row[2]}")
    except Exception as e:
        print(f"\nuser_role table: Not created yet")
    
    # Pending requests
    try:
        pending = db.execute(text("""
            SELECT COUNT(*) FROM role_request WHERE status = 'pending'
        """)).scalar()
        print(f"\nPending role requests: {pending}")
    except:
        pass


def main():
    parser = argparse.ArgumentParser(description="Migrate user roles to multi-role system")
    parser.add_argument("--force", action="store_true", help="Force migration even if data exists")
    parser.add_argument("--stats-only", action="store_true", help="Only show statistics")
    args = parser.parse_args()
    
    db = SessionLocal()
    
    try:
        if args.stats_only:
            show_statistics(db)
            return
        
        print("="*50)
        print("USER ROLE MIGRATION")
        print("="*50)
        
        # Create tables
        create_tables(db)
        
        # Migrate existing roles
        migrate_existing_roles(db, force=args.force)
        
        # Show statistics
        show_statistics(db)
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
