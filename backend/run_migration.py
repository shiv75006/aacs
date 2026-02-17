"""Database migration to update paper status ENUM"""
from sqlalchemy import create_engine, text
from app.config import settings

def run_migration():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Step 1: Alter ENUM to include underscore versions
            print('Step 1: Altering status ENUM...')
            conn.execute(text("""
                ALTER TABLE paper 
                MODIFY COLUMN status ENUM(
                    'submitted',
                    'under review',
                    'under_review',
                    'reviewed',
                    'accepted',
                    'rejected',
                    'correction',
                    'under publication',
                    'under_publication',
                    'published',
                    'resubmitted'
                ) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL
            """))
            print('  ENUM updated successfully')
            
            # Step 2: Migrate 'under review' to 'under_review'
            print('Step 2: Migrating under review -> under_review...')
            result = conn.execute(text("UPDATE paper SET status = 'under_review' WHERE status = 'under review'"))
            print(f'  Updated {result.rowcount} rows')
            
            # Step 3: Migrate 'under publication' to 'under_publication'
            print('Step 3: Migrating under publication -> under_publication...')
            result = conn.execute(text("UPDATE paper SET status = 'under_publication' WHERE status = 'under publication'"))
            print(f'  Updated {result.rowcount} rows')
            
            trans.commit()
            print('\n✅ Migration completed successfully!')
            
            # Verify
            print('\nCurrent status distribution:')
            result = conn.execute(text('SELECT status, COUNT(*) FROM paper GROUP BY status'))
            for row in result:
                print(f'  {row[0]}: {row[1]}')
                
        except Exception as e:
            trans.rollback()
            print(f'❌ Error: {e}')
            raise

if __name__ == "__main__":
    run_migration()
