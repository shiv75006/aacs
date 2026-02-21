#!/bin/bash
# ============================================================================
# AACS Complete Database Migration Script
# ============================================================================
# This script will:
# 1. Drop the existing database
# 2. Create a fresh database  
# 3. Import the original SQL dump
# 4. Run the migration queries to create new schema
# ============================================================================

DB_NAME="aacsjour_aacs"
DB_USER="root"
DB_PASS="shiv75006"
SQL_DUMP="/Users/shivyanshusaini/Desktop/AACS/aacsjour_aacs.sql"
MIGRATION_SCRIPT="/Users/shivyanshusaini/Desktop/AACS/post_import_migration.sql"

echo "=============================================="
echo "AACS Database Migration"
echo "=============================================="

# Step 1: Drop and recreate database
echo ""
echo "Step 1: Dropping and recreating database..."
mysql -u $DB_USER -p$DB_PASS -e "DROP DATABASE IF EXISTS $DB_NAME;"
mysql -u $DB_USER -p$DB_PASS -e "CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo "Database recreated successfully."

# Step 2: Import original SQL dump
echo ""
echo "Step 2: Importing SQL dump (this may take a while)..."
mysql -u $DB_USER -p$DB_PASS $DB_NAME < "$SQL_DUMP"
echo "SQL dump imported successfully."

# Step 3: Run post-import migration
echo ""
echo "Step 3: Running post-import migration..."
mysql -u $DB_USER -p$DB_PASS $DB_NAME < "$MIGRATION_SCRIPT"
echo "Migration completed successfully."

# Step 4: Verification
echo ""
echo "Step 4: Verifying migration..."
echo ""
echo "=== Data Counts ==="
mysql -u $DB_USER -p$DB_PASS $DB_NAME -e "
SELECT 'admin' as tbl, COUNT(*) as cnt FROM admin
UNION ALL SELECT 'editor', COUNT(*) FROM editor
UNION ALL SELECT 'author', COUNT(*) FROM author
UNION ALL SELECT 'journal', COUNT(*) FROM journal
UNION ALL SELECT 'paper', COUNT(*) FROM paper
UNION ALL SELECT 'paper_published', COUNT(*) FROM paper_published
UNION ALL SELECT 'volume', COUNT(*) FROM volume
UNION ALL SELECT 'issue', COUNT(*) FROM issue
UNION ALL SELECT 'indexing', COUNT(*) FROM indexing
UNION ALL SELECT 'news', COUNT(*) FROM news
UNION ALL SELECT 'user (new)', COUNT(*) FROM user
UNION ALL SELECT 'user_role (new)', COUNT(*) FROM user_role
UNION ALL SELECT 'paper_co_author (new)', COUNT(*) FROM paper_co_author;
"

echo ""
echo "=============================================="
echo "Migration Complete!"
echo "=============================================="
