-- ============================================================================
-- AACS POST-IMPORT MIGRATION SCRIPT
-- ============================================================================
-- This script runs AFTER the original SQL dump has been imported.
-- It creates new unified tables and migrates data to the new schema.
-- ============================================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET FOREIGN_KEY_CHECKS = 0;
START TRANSACTION;

-- ============================================================================
-- STEP 0: ALTER EXISTING TABLES TO ADD MISSING COLUMNS
-- ============================================================================

-- Add missing columns to paper table (required by SQLAlchemy model)
-- Using separate ALTER statements to handle cases where columns may already exist

SET @dbname = 'aacsjour_aacs';
SET @tablename = 'paper';

-- Add version_number if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'version_number') > 0,
  'SELECT 1',
  'ALTER TABLE paper ADD COLUMN version_number int NOT NULL DEFAULT 1'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add revision_count if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'revision_count') > 0,
  'SELECT 1',
  'ALTER TABLE paper ADD COLUMN revision_count int NOT NULL DEFAULT 0'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add revision_deadline if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'revision_deadline') > 0,
  'SELECT 1',
  'ALTER TABLE paper ADD COLUMN revision_deadline datetime DEFAULT NULL'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add revision_notes if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'revision_notes') > 0,
  'SELECT 1',
  'ALTER TABLE paper ADD COLUMN revision_notes text DEFAULT NULL'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add revision_requested_date if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'revision_requested_date') > 0,
  'SELECT 1',
  'ALTER TABLE paper ADD COLUMN revision_requested_date datetime DEFAULT NULL'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add research_area if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'research_area') > 0,
  'SELECT 1',
  'ALTER TABLE paper ADD COLUMN research_area varchar(200) DEFAULT NULL'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add message_to_editor if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'message_to_editor') > 0,
  'SELECT 1',
  'ALTER TABLE paper ADD COLUMN message_to_editor text DEFAULT NULL'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add terms_accepted if not exists
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'terms_accepted') > 0,
  'SELECT 1',
  'ALTER TABLE paper ADD COLUMN terms_accepted tinyint(1) NOT NULL DEFAULT 0'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add paper_id column and copy from id if needed
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'paper_id') > 0,
  'SELECT 1',
  'ALTER TABLE paper ADD COLUMN paper_id int DEFAULT NULL'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Copy id to paper_id if paper_id is NULL
UPDATE paper SET paper_id = id WHERE paper_id IS NULL;

-- Add paper_title column and copy from title
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'paper_title') > 0,
  'SELECT 1',
  'ALTER TABLE paper ADD COLUMN paper_title varchar(500) DEFAULT NULL'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Copy title to paper_title if paper_title is NULL
UPDATE paper SET paper_title = title WHERE paper_title IS NULL;

-- Add paper_author_name column and copy from author
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = 'paper_author_name') > 0,
  'SELECT 1',
  'ALTER TABLE paper ADD COLUMN paper_author_name varchar(100) DEFAULT NULL'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Copy author to paper_author_name if paper_author_name is NULL
UPDATE paper SET paper_author_name = author WHERE paper_author_name IS NULL;

SELECT 'Paper table columns added' AS status;

-- ============================================================================
-- STEP 1: DROP OLD USER TABLE FROM DUMP AND CREATE NEW STRUCTURE
-- ============================================================================

-- The SQL dump creates an OLD user table with wrong structure
-- We need to drop it and create the correct one

DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `user_role`;
DROP TABLE IF EXISTS `paper_co_author`;
DROP TABLE IF EXISTS `paper_version`;
DROP TABLE IF EXISTS `reviewer_invitation`;
DROP TABLE IF EXISTS `review_submission`;
DROP TABLE IF EXISTS `paper_correspondence`;
DROP TABLE IF EXISTS `email_template`;
DROP TABLE IF EXISTS `role_request`;

-- Create unified user table with CORRECT structure matching SQLAlchemy model
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) DEFAULT 'User',
  `fname` varchar(100) DEFAULT NULL,
  `lname` varchar(100) DEFAULT NULL,
  `mname` varchar(100) DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `affiliation` varchar(255) DEFAULT NULL,
  `specialization` text DEFAULT NULL,
  `contact` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `added_on` datetime DEFAULT CURRENT_TIMESTAMP,
  `salutation` varchar(20) DEFAULT NULL,
  `designation` varchar(100) DEFAULT NULL,
  `department` varchar(200) DEFAULT NULL,
  `organisation` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create user_role table for multi-role support
CREATE TABLE IF NOT EXISTS `user_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `role` enum('admin','author','editor','reviewer') NOT NULL,
  `journal_id` int DEFAULT NULL,
  `assigned_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `journal_id` (`journal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create paper_co_author table
CREATE TABLE IF NOT EXISTS `paper_co_author` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paper_id` int NOT NULL,
  `author_name` varchar(200) NOT NULL,
  `author_email` varchar(200) DEFAULT NULL,
  `author_affiliation` varchar(500) DEFAULT NULL,
  `author_contact` varchar(50) DEFAULT NULL,
  `author_order` int DEFAULT 1,
  `added_on` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `paper_id` (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create paper_version table
CREATE TABLE IF NOT EXISTS `paper_version` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paper_id` int NOT NULL,
  `version_number` int NOT NULL DEFAULT 1,
  `file_path` varchar(500) DEFAULT NULL,
  `changes_description` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `paper_id` (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create reviewer_invitation table
CREATE TABLE IF NOT EXISTS `reviewer_invitation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paper_id` int NOT NULL,
  `reviewer_id` int NOT NULL,
  `invited_by` int DEFAULT NULL,
  `status` enum('pending','accepted','declined','expired') NOT NULL DEFAULT 'pending',
  `invited_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `responded_at` timestamp NULL DEFAULT NULL,
  `deadline` date DEFAULT NULL,
  `message` text,
  PRIMARY KEY (`id`),
  KEY `paper_id` (`paper_id`),
  KEY `reviewer_id` (`reviewer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create review_submission table
CREATE TABLE IF NOT EXISTS `review_submission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invitation_id` int NOT NULL,
  `paper_id` int NOT NULL,
  `reviewer_id` int NOT NULL,
  `recommendation` enum('accept','minor_revision','major_revision','reject') DEFAULT NULL,
  `comments_to_author` text,
  `comments_to_editor` text,
  `attachment` varchar(500) DEFAULT NULL,
  `submitted_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `invitation_id` (`invitation_id`),
  KEY `paper_id` (`paper_id`),
  KEY `reviewer_id` (`reviewer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create paper_correspondence table
CREATE TABLE IF NOT EXISTS `paper_correspondence` (
  `id` int NOT NULL AUTO_INCREMENT,
  `paper_id` int NOT NULL,
  `sender_id` int NOT NULL,
  `recipient_type` enum('author','editor','reviewer') NOT NULL,
  `subject` varchar(500) DEFAULT NULL,
  `message` text NOT NULL,
  `attachment` varchar(500) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_read` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `paper_id` (`paper_id`),
  KEY `sender_id` (`sender_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create email_template table
CREATE TABLE IF NOT EXISTS `email_template` (
  `id` int NOT NULL AUTO_INCREMENT,
  `slug` varchar(100) NOT NULL,
  `subject` varchar(500) NOT NULL,
  `body_template` text NOT NULL,
  `category` varchar(50) DEFAULT 'general',
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create role_request table
CREATE TABLE IF NOT EXISTS `role_request` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `requested_role` enum('editor','reviewer') NOT NULL,
  `journal_id` int DEFAULT NULL,
  `status` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  `requested_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `processed_at` timestamp NULL DEFAULT NULL,
  `processed_by` int DEFAULT NULL,
  `reason` text,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'New tables created/verified' AS status;

-- ============================================================================
-- STEP 2: CLEAR NEW TABLES (in case of re-run)
-- ============================================================================

DELETE FROM user_role;
DELETE FROM paper_co_author;
DELETE FROM paper_version;
DELETE FROM reviewer_invitation;
DELETE FROM review_submission;
DELETE FROM paper_correspondence;
DELETE FROM email_template;
DELETE FROM role_request;
DELETE FROM user;

ALTER TABLE user AUTO_INCREMENT = 1;
ALTER TABLE user_role AUTO_INCREMENT = 1;
ALTER TABLE paper_co_author AUTO_INCREMENT = 1;
ALTER TABLE paper_version AUTO_INCREMENT = 1;
ALTER TABLE reviewer_invitation AUTO_INCREMENT = 1;
ALTER TABLE review_submission AUTO_INCREMENT = 1;
ALTER TABLE paper_correspondence AUTO_INCREMENT = 1;
ALTER TABLE email_template AUTO_INCREMENT = 1;
ALTER TABLE role_request AUTO_INCREMENT = 1;

SELECT 'New tables cleared' AS status;

-- ============================================================================
-- STEP 3: MIGRATE DATA TO NEW SCHEMA
-- ============================================================================

-- 3.1 Migrate admin to unified user table
INSERT INTO user (email, password, role, fname, lname, mname, title, affiliation, specialization, contact, address, added_on)
SELECT 
    fld_email,
    fld_password,
    'Admin',
    fld_fname,
    COALESCE(fld_lname, ''),
    '',
    'Dr.',
    '',
    '',
    '',
    '',
    fld_addedon
FROM admin
WHERE fld_email IS NOT NULL AND fld_email != '';

SELECT CONCAT('Admins migrated: ', ROW_COUNT()) AS status;

-- 3.2 Migrate editors to unified user table (avoiding duplicates)
INSERT INTO user (email, password, role, fname, lname, mname, title, affiliation, specialization, contact, address, added_on)
SELECT 
    editor_email,
    password,
    CASE WHEN role = 'Admin' THEN 'Admin' ELSE 'Editor' END,
    CASE 
        WHEN editor_name LIKE 'Dr.%' THEN TRIM(SUBSTRING_INDEX(REPLACE(editor_name, 'Dr.', ''), ' ', 1))
        WHEN editor_name LIKE 'Dr %' THEN TRIM(SUBSTRING_INDEX(REPLACE(editor_name, 'Dr ', ''), ' ', 1))
        WHEN editor_name LIKE 'Prof.%' THEN TRIM(SUBSTRING_INDEX(REPLACE(editor_name, 'Prof.', ''), ' ', 1))
        WHEN editor_name LIKE 'Prof %' THEN TRIM(SUBSTRING_INDEX(REPLACE(editor_name, 'Prof ', ''), ' ', 1))
        ELSE TRIM(SUBSTRING_INDEX(editor_name, ' ', 1))
    END,
    CASE 
        WHEN editor_name LIKE 'Dr.%' THEN TRIM(SUBSTRING(editor_name, LOCATE(' ', REPLACE(editor_name, 'Dr.', '')) + 4))
        WHEN editor_name LIKE 'Dr %' THEN TRIM(SUBSTRING(editor_name, LOCATE(' ', REPLACE(editor_name, 'Dr ', '')) + 3))
        WHEN editor_name LIKE 'Prof.%' THEN TRIM(SUBSTRING(editor_name, LOCATE(' ', REPLACE(editor_name, 'Prof.', '')) + 6))
        WHEN editor_name LIKE 'Prof %' THEN TRIM(SUBSTRING(editor_name, LOCATE(' ', REPLACE(editor_name, 'Prof ', '')) + 5))
        WHEN LOCATE(' ', editor_name) > 0 THEN TRIM(SUBSTRING(editor_name, LOCATE(' ', editor_name) + 1))
        ELSE ''
    END,
    '',
    CASE 
        WHEN editor_name LIKE 'Dr.%' OR editor_name LIKE 'Dr %' THEN 'Dr.'
        WHEN editor_name LIKE 'Prof.%' OR editor_name LIKE 'Prof %' THEN 'Prof.'
        ELSE ''
    END,
    COALESCE(editor_affiliation, ''),
    '',
    COALESCE(editor_contact, ''),
    COALESCE(editor_address, ''),
    added_on
FROM editor
WHERE editor_email NOT IN (SELECT email FROM user)
AND editor_email IS NOT NULL AND editor_email != '';

SELECT CONCAT('Editors migrated: ', ROW_COUNT()) AS status;

-- 3.3 Create user_role entries for admins
INSERT INTO user_role (user_id, role, journal_id, assigned_on, is_active)
SELECT 
    u.id,
    'admin',
    NULL,
    u.added_on,
    1
FROM user u
JOIN admin a ON u.email = a.fld_email;

SELECT CONCAT('Admin roles created: ', ROW_COUNT()) AS status;

-- 3.4 Create user_role entries for editors
INSERT INTO user_role (user_id, role, journal_id, assigned_on, is_active)
SELECT 
    u.id,
    CASE WHEN e.role = 'Admin' THEN 'admin' ELSE 'editor' END,
    e.journal_id,
    e.added_on,
    1
FROM user u
JOIN editor e ON u.email = e.editor_email;

SELECT CONCAT('Editor roles created: ', ROW_COUNT()) AS status;

-- 3.5 Migrate author (co-authors) to paper_co_author table
INSERT INTO paper_co_author (paper_id, author_name, author_email, author_affiliation, author_contact, author_order, added_on)
SELECT 
    paper_id,
    author_name,
    author_email,
    author_address,
    author_contact,
    1,
    added_on
FROM author
ORDER BY paper_id, id;

SELECT CONCAT('Co-authors migrated: ', ROW_COUNT()) AS status;

-- 3.6 Insert email templates
INSERT INTO email_template (slug, subject, body_template, category, is_active, created_at, updated_at) VALUES
('paper_submission', 'Paper Submission Confirmation - {{journal_name}}', 
'Dear {{author_name}},

Thank you for submitting your paper titled "{{paper_title}}" to {{journal_name}}.

Your submission ID is: {{paper_code}}

We will review your submission and get back to you soon.

Best regards,
Editorial Team
{{journal_name}}', 'submission', 1, NOW(), NOW()),

('paper_accepted', 'Congratulations! Paper Accepted - {{journal_name}}', 
'Dear {{author_name}},

We are pleased to inform you that your paper titled "{{paper_title}}" has been accepted for publication in {{journal_name}}.

Paper ID: {{paper_code}}

Congratulations on this achievement!

Best regards,
Editorial Team
{{journal_name}}', 'decision', 1, NOW(), NOW()),

('paper_rejected', 'Paper Decision - {{journal_name}}', 
'Dear {{author_name}},

Thank you for your submission to {{journal_name}}.

After careful review, we regret to inform you that your paper titled "{{paper_title}}" cannot be accepted for publication at this time.

Paper ID: {{paper_code}}

We encourage you to consider our feedback and resubmit in the future.

Best regards,
Editorial Team
{{journal_name}}', 'decision', 1, NOW(), NOW()),

('paper_revision', 'Revision Required - {{journal_name}}', 
'Dear {{author_name}},

Your paper titled "{{paper_title}}" (ID: {{paper_code}}) requires revisions before it can be considered for publication in {{journal_name}}.

Please address the reviewer comments and resubmit your revised manuscript.

Revision Deadline: {{deadline}}

Best regards,
Editorial Team
{{journal_name}}', 'decision', 1, NOW(), NOW()),

('reviewer_invitation', 'Invitation to Review - {{journal_name}}', 
'Dear {{reviewer_name}},

You are cordially invited to review a paper titled "{{paper_title}}" for {{journal_name}}.

Please log in to your reviewer dashboard to accept or decline this invitation.

Review Deadline: {{deadline}}

Best regards,
Editorial Team
{{journal_name}}', 'reviewer', 1, NOW(), NOW()),

('reviewer_reminder', 'Review Reminder - {{journal_name}}', 
'Dear {{reviewer_name}},

This is a gentle reminder about the pending review for the paper titled "{{paper_title}}".

Review Deadline: {{deadline}}

Please complete your review at your earliest convenience.

Best regards,
Editorial Team
{{journal_name}}', 'reviewer', 1, NOW(), NOW()),

('password_reset', 'Password Reset Request - AACS Journals', 
'Dear {{user_name}},

We received a request to reset your password for your AACS Journals account.

Click the link below to reset your password:
{{reset_link}}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

Best regards,
AACS Journals Team', 'system', 1, NOW(), NOW()),

('welcome_email', 'Welcome to AACS Journals', 
'Dear {{user_name}},

Welcome to AACS Journals!

Your account has been created successfully. You can now log in and start submitting your research papers.

Login URL: {{login_url}}

Best regards,
AACS Journals Team', 'system', 1, NOW(), NOW());

SELECT CONCAT('Email templates created: ', ROW_COUNT()) AS status;

-- ============================================================================
-- STEP 4: VERIFICATION
-- ============================================================================

SELECT '=== MIGRATION VERIFICATION ===' AS info;

SELECT 'OLD TABLES:' AS section;
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
UNION ALL SELECT 'editorial_board', COUNT(*) FROM editorial_board
UNION ALL SELECT 'editor_profile', COUNT(*) FROM editor_profile
UNION ALL SELECT 'gallery', COUNT(*) FROM gallery
UNION ALL SELECT 'gallery_pics', COUNT(*) FROM gallery_pics
UNION ALL SELECT 'online_review', COUNT(*) FROM online_review
UNION ALL SELECT 'refree', COUNT(*) FROM refree
UNION ALL SELECT 'review_panel', COUNT(*) FROM review_panel;

SELECT 'NEW TABLES:' AS section;
SELECT 'user' as tbl, COUNT(*) as cnt FROM user
UNION ALL SELECT 'user_role', COUNT(*) FROM user_role
UNION ALL SELECT 'paper_co_author', COUNT(*) FROM paper_co_author
UNION ALL SELECT 'email_template', COUNT(*) FROM email_template;

SELECT 'USER DETAILS:' AS section;
SELECT id, fname, lname, email, role FROM user;

SELECT 'ROLE BREAKDOWN:' AS section;
SELECT role, COUNT(*) as count FROM user_role GROUP BY role;

COMMIT;
SET FOREIGN_KEY_CHECKS = 1;

SELECT '=== MIGRATION COMPLETE ===' AS final_status;
