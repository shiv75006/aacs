-- Migration: Add title_page and blinded_manuscript columns to papers table
-- Date: 2024
-- Description: Support two-file paper submission (title page with author info + blinded manuscript for review)

-- Add title_page column
ALTER TABLE papers ADD COLUMN title_page VARCHAR(200) DEFAULT '' AFTER file_path;

-- Add blinded_manuscript column  
ALTER TABLE papers ADD COLUMN blinded_manuscript VARCHAR(200) DEFAULT '' AFTER title_page;

-- Optional: Migrate existing file_path to blinded_manuscript (if you want existing papers to have their file as blinded manuscript)
-- UPDATE papers SET blinded_manuscript = file_path WHERE file_path IS NOT NULL AND file_path != '';
