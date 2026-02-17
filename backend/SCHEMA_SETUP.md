# Schema Updates - Setup Guide

## Overview
The schema has been updated to support proper review tracking with new fields in the `online_review` table.

## Changes Made

### 1. Backend Models Updated
- **OnlineReview Model** (`backend/app/db/models.py`)
  - Added `submitted_on`: DateTime field to track when review was submitted
  - Added `review_status`: String field with values (pending, submitted, completed)

### 2. Database Migration Script
- Created `backend/add_review_fields.py` to add columns to the database

## Installation Steps

### Step 1: Run the Migration Script

```bash
cd backend
python add_review_fields.py
```

This will:
- Add `submitted_on` column to `online_review` table
- Add `review_status` column with default value 'pending'
- Create an index for optimized queries

### Step 2: Verify the Changes

Check if the columns were added successfully:

```sql
DESCRIBE online_review;
```

You should see:
- `submitted_on` DATETIME NULL
- `review_status` VARCHAR(50) NOT NULL DEFAULT 'pending'

## API Changes

**No API changes** - The existing APIs automatically use the new fields:

- **GET /api/v1/reviewer/assignments** - Now returns accurate `status` field
- **GET /api/v1/reviewer/dashboard/stats** - Accurate pending/completed counts
- All endpoints work exactly as before

## Status Values

The `review_status` field can have these values:

| Status | Meaning |
|--------|---------|
| `pending` | Review invitation accepted, waiting for submission |
| `submitted` | Review has been submitted by reviewer |
| `completed` | Review process is complete |

## Database Queries

### Get pending reviews for a reviewer
```sql
SELECT * FROM online_review 
WHERE reviewer_id = '123' 
AND review_status = 'pending';
```

### Get completed reviews for a reviewer
```sql
SELECT * FROM online_review 
WHERE reviewer_id = '123' 
AND review_status = 'completed';
```

## Next Steps

1. Ensure the migration runs successfully
2. Test the dashboard stats endpoint
3. Monitor the API responses for the new `status` field

## Troubleshooting

If the migration script fails:

1. Verify database connection details in `add_review_fields.py`
2. Check if columns already exist:
   ```sql
   SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
   WHERE TABLE_NAME='online_review';
   ```
3. If columns exist, no action needed - they're already in the schema

## Rollback (if needed)

If you need to remove these columns:

```sql
ALTER TABLE `online_review` DROP COLUMN `submitted_on`;
ALTER TABLE `online_review` DROP COLUMN `review_status`;
DROP INDEX idx_review_status ON `online_review`;
```
