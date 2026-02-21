-- ============================================================================
-- AACS DATABASE MIGRATION SCRIPT
-- ============================================================================
-- Description: Migrates data from old PHP/MySQL schema to new FastAPI/SQLAlchemy schema
-- Date: February 2026
-- 
-- USAGE:
--   1. Backup your database first: mysqldump -u root -p aacsjour_aacs > backup.sql
--   2. Run this script: mysql -u root -p aacsjour_aacs < migrate_old_data.sql
-- ============================================================================

START TRANSACTION;
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';

-- ============================================================================
-- SECTION 1: CREATE NEW TABLES (if not exist)
-- ============================================================================

-- 1.1 User table (unified authentication)
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `role` ENUM('admin', 'editor', 'reviewer', 'author') DEFAULT 'author',
    `fname` VARCHAR(100),
    `lname` VARCHAR(100),
    `mname` VARCHAR(100),
    `title` VARCHAR(50),
    `affiliation` VARCHAR(255),
    `contact` VARCHAR(50),
    `address` TEXT,
    `department` VARCHAR(255),
    `organisation` VARCHAR(255),
    `is_active` TINYINT(1) DEFAULT 1,
    `added_on` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_on` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 1.2 User role table (multi-role support)
CREATE TABLE IF NOT EXISTS `user_role` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `role` VARCHAR(50) NOT NULL,
    `journal_id` INT,
    `editor_type` VARCHAR(50),
    `status` ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    `requested_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `approved_at` DATETIME,
    `approved_by` INT,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `user_role_journal` (`user_id`, `role`, `journal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 1.3 Paper version table (revision tracking)
CREATE TABLE IF NOT EXISTS `paper_version` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `paper_id` INT NOT NULL,
    `version_number` INT NOT NULL DEFAULT 1,
    `file` VARCHAR(255),
    `uploaded_on` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `change_summary` TEXT,
    `uploaded_by` INT,
    UNIQUE KEY `paper_version_unique` (`paper_id`, `version_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 1.4 Paper co-author table
CREATE TABLE IF NOT EXISTS `paper_co_author` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `paper_id` INT NOT NULL,
    `first_name` VARCHAR(100),
    `last_name` VARCHAR(100),
    `email` VARCHAR(255),
    `affiliation` VARCHAR(255),
    `author_order` INT DEFAULT 1,
    `is_corresponding` TINYINT(1) DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 1.5 Volume table
CREATE TABLE IF NOT EXISTS `volume` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `journal` INT NOT NULL,
    `volume_no` VARCHAR(10) NOT NULL,
    `year` VARCHAR(10),
    `added_on` DATE,
    UNIQUE KEY `journal_volume` (`journal`, `volume_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 1.6 Reviewer invitation table
CREATE TABLE IF NOT EXISTS `reviewer_invitation` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `paper_id` INT NOT NULL,
    `reviewer_id` INT,
    `reviewer_email` VARCHAR(255) NOT NULL,
    `invited_by` INT,
    `invited_on` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `status` ENUM('pending', 'accepted', 'declined', 'expired') DEFAULT 'pending',
    `response_on` DATETIME,
    `token` VARCHAR(255),
    `expires_on` DATETIME,
    `message` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 1.7 Review submission table
CREATE TABLE IF NOT EXISTS `review_submission` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `online_review_id` INT NOT NULL,
    `originality_score` INT,
    `methodology_score` INT,
    `clarity_score` INT,
    `significance_score` INT,
    `overall_score` INT,
    `recommendation` ENUM('accept', 'minor_revision', 'major_revision', 'reject') DEFAULT 'minor_revision',
    `comments_to_author` TEXT,
    `comments_to_editor` TEXT,
    `attachment` VARCHAR(255),
    `submitted_on` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 1.8 Email template table
CREATE TABLE IF NOT EXISTS `email_template` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `subject` VARCHAR(255) NOT NULL,
    `body` TEXT NOT NULL,
    `variables` TEXT,
    `category` VARCHAR(50),
    `is_active` TINYINT(1) DEFAULT 1,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 1.9 Paper correspondence table
CREATE TABLE IF NOT EXISTS `paper_correspondence` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `paper_id` INT NOT NULL,
    `sender_id` INT,
    `sender_role` VARCHAR(50),
    `recipient_email` VARCHAR(255) NOT NULL,
    `subject` VARCHAR(255) NOT NULL,
    `message` TEXT NOT NULL,
    `template_id` INT,
    `is_read` TINYINT(1) DEFAULT 0,
    `read_at` DATETIME,
    `sent_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- SECTION 2: ADD NEW COLUMNS TO EXISTING TABLES
-- ============================================================================

-- 2.1 Add new columns to paper table
ALTER TABLE `paper`
    ADD COLUMN IF NOT EXISTS `version_number` INT DEFAULT 1,
    ADD COLUMN IF NOT EXISTS `revision_count` INT DEFAULT 0,
    ADD COLUMN IF NOT EXISTS `decision_date` DATETIME,
    ADD COLUMN IF NOT EXISTS `submitted_by_user_id` INT;

-- 2.2 Add new columns to paper_published table
ALTER TABLE `paper_published`
    ADD COLUMN IF NOT EXISTS `access_type` VARCHAR(20) DEFAULT 'open',
    ADD COLUMN IF NOT EXISTS `doi_status` VARCHAR(20) DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS `published_on` DATETIME,
    ADD COLUMN IF NOT EXISTS `paper_id` INT;

-- 2.3 Add new columns to online_review table
ALTER TABLE `online_review`
    ADD COLUMN IF NOT EXISTS `review_status` VARCHAR(20) DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS `submitted_on` DATETIME,
    ADD COLUMN IF NOT EXISTS `deadline` DATE,
    ADD COLUMN IF NOT EXISTS `review_submission_id` INT,
    ADD COLUMN IF NOT EXISTS `invitation_id` INT;

-- 2.4 Add new columns to editor table
ALTER TABLE `editor`
    ADD COLUMN IF NOT EXISTS `editor_type` VARCHAR(50) DEFAULT 'section_editor',
    ADD COLUMN IF NOT EXISTS `user_id` INT;

-- ============================================================================
-- SECTION 3: MIGRATE USER DATA
-- ============================================================================

-- 3.1 Migrate admin users to user table
INSERT INTO `user` (email, password, role, fname, lname, is_active, added_on)
SELECT 
    fld_email,
    fld_password,
    'admin',
    fld_fname,
    fld_lname,
    COALESCE(fld_active, 1),
    fld_addedon
FROM `admin`
WHERE fld_email IS NOT NULL 
  AND fld_email != ''
  AND fld_email NOT IN (SELECT email FROM `user`)
ON DUPLICATE KEY UPDATE 
    role = 'admin',
    fname = VALUES(fname),
    lname = VALUES(lname);

-- 3.2 Migrate editor users to user table
INSERT INTO `user` (email, password, role, fname, lname, affiliation, contact, address, department, organisation, added_on)
SELECT 
    editor_email,
    password,
    CASE WHEN role = 'Admin' THEN 'admin' ELSE 'editor' END,
    SUBSTRING_INDEX(TRIM(editor_name), ' ', 1),
    TRIM(SUBSTRING(TRIM(editor_name), LENGTH(SUBSTRING_INDEX(editor_name, ' ', 1)) + 2)),
    editor_affiliation,
    editor_contact,
    editor_address,
    editor_department,
    editor_college,
    added_on
FROM `editor`
WHERE editor_email IS NOT NULL 
  AND editor_email != ''
  AND editor_email NOT IN (SELECT email FROM `user`)
ON DUPLICATE KEY UPDATE
    fname = VALUES(fname),
    lname = VALUES(lname);

-- 3.3 Create user_role entries for admin users
INSERT INTO `user_role` (user_id, role, status, requested_at)
SELECT 
    u.id,
    'admin',
    'approved',
    u.added_on
FROM `user` u
WHERE u.role = 'admin'
  AND NOT EXISTS (
      SELECT 1 FROM `user_role` ur 
      WHERE ur.user_id = u.id AND ur.role = 'admin'
  );

-- 3.4 Create user_role entries for editors with journal assignments
INSERT INTO `user_role` (user_id, role, journal_id, editor_type, status, requested_at)
SELECT 
    u.id,
    'editor',
    e.journal_id,
    CASE WHEN e.role = 'Admin' THEN 'chief_editor' ELSE 'section_editor' END,
    'approved',
    e.added_on
FROM `user` u
JOIN `editor` e ON u.email = e.editor_email
WHERE e.journal_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM `user_role` ur 
      WHERE ur.user_id = u.id AND ur.role = 'editor' AND ur.journal_id = e.journal_id
  );

-- 3.5 Update editor table with user_id references
UPDATE `editor` e
JOIN `user` u ON e.editor_email = u.email
SET e.user_id = u.id,
    e.editor_type = CASE WHEN e.role = 'Admin' THEN 'chief_editor' ELSE 'section_editor' END
WHERE e.user_id IS NULL;

-- ============================================================================
-- SECTION 4: MIGRATE PAPER DATA
-- ============================================================================

-- 4.1 Set default values for new paper columns
UPDATE `paper` 
SET version_number = 1, 
    revision_count = 0 
WHERE version_number IS NULL OR version_number = 0;

-- 4.2 Create initial paper_version records for existing papers
INSERT INTO `paper_version` (paper_id, version_number, file, uploaded_on, change_summary)
SELECT 
    id,
    1,
    file,
    added_on,
    'Initial submission (migrated from legacy system)'
FROM `paper`
WHERE file IS NOT NULL 
  AND file != ''
  AND id NOT IN (SELECT paper_id FROM `paper_version`);

-- 4.3 Extract co-authors from paper.coauth field (if JSON format)
-- Note: This handles the common case where coauth is stored as JSON array of IDs
-- For more complex parsing, use application-level migration

INSERT INTO `paper_co_author` (paper_id, first_name, last_name, author_order, created_at)
SELECT 
    p.id,
    'Co-Author',
    CONCAT('(Migrated from paper #', p.id, ')'),
    2,
    p.added_on
FROM `paper` p
WHERE p.coauth IS NOT NULL 
  AND p.coauth != '' 
  AND p.coauth != '[]'
  AND p.id NOT IN (SELECT DISTINCT paper_id FROM `paper_co_author`);

-- ============================================================================
-- SECTION 5: MIGRATE PUBLISHED PAPERS
-- ============================================================================

-- 5.1 Update paper_published with new field defaults
UPDATE `paper_published` 
SET access_type = 'open',
    doi_status = CASE 
        WHEN doi IS NOT NULL AND doi != '' AND doi NOT LIKE '%waiting%' THEN 'registered'
        ELSE 'pending'
    END,
    published_on = `date`
WHERE access_type IS NULL OR access_type = '';

-- ============================================================================
-- SECTION 6: MIGRATE REVIEW SYSTEM
-- ============================================================================

-- 6.1 Update online_review with new status field
UPDATE `online_review` 
SET review_status = 'pending'
WHERE review_status IS NULL OR review_status = '';

-- 6.2 Set deadline for existing reviews (30 days from assignment)
UPDATE `online_review`
SET deadline = DATE_ADD(assigned_on, INTERVAL 30 DAY)
WHERE deadline IS NULL AND assigned_on IS NOT NULL;

-- ============================================================================
-- SECTION 7: CREATE VOLUME RECORDS FROM ISSUE DATA
-- ============================================================================

INSERT INTO `volume` (journal, volume_no, year, added_on)
SELECT DISTINCT 
    journal,
    CAST(volume AS CHAR),
    CASE 
        WHEN add_on IS NOT NULL THEN YEAR(add_on)
        ELSE NULL
    END,
    MIN(add_on)
FROM `issue`
WHERE volume IS NOT NULL 
  AND volume > 0
  AND journal IS NOT NULL
GROUP BY journal, volume
ON DUPLICATE KEY UPDATE
    year = VALUES(year);

-- ============================================================================
-- SECTION 8: SEED DEFAULT EMAIL TEMPLATES
-- ============================================================================

INSERT INTO `email_template` (name, subject, body, variables, category, is_active) VALUES
('submission_received', 'Paper Submission Received - {{paper_code}}', 
'Dear {{author_name}},\n\nThank you for submitting your paper titled \"{{paper_title}}\" to {{journal_name}}.\n\nYour submission has been received and assigned the code: {{paper_code}}\n\nWe will review your submission and get back to you shortly.\n\nBest regards,\nEditorial Team',
'author_name,paper_title,paper_code,journal_name', 'submission', 1),

('under_review', 'Paper Under Review - {{paper_code}}',
'Dear {{author_name}},\n\nYour paper \"{{paper_title}}\" ({{paper_code}}) is now under review.\n\nWe will notify you once the review process is complete.\n\nBest regards,\nEditorial Team',
'author_name,paper_title,paper_code', 'status', 1),

('revision_requested', 'Revision Requested - {{paper_code}}',
'Dear {{author_name}},\n\nAfter reviewing your paper \"{{paper_title}}\" ({{paper_code}}), the reviewers have requested revisions.\n\nPlease review the comments and submit your revised manuscript.\n\n{{comments}}\n\nBest regards,\nEditorial Team',
'author_name,paper_title,paper_code,comments', 'decision', 1),

('paper_accepted', 'Congratulations! Paper Accepted - {{paper_code}}',
'Dear {{author_name}},\n\nWe are pleased to inform you that your paper \"{{paper_title}}\" ({{paper_code}}) has been accepted for publication in {{journal_name}}.\n\nCongratulations on this achievement!\n\nBest regards,\nEditorial Team',
'author_name,paper_title,paper_code,journal_name', 'decision', 1),

('paper_rejected', 'Decision on Your Submission - {{paper_code}}',
'Dear {{author_name}},\n\nThank you for submitting your paper \"{{paper_title}}\" ({{paper_code}}) to {{journal_name}}.\n\nAfter careful review, we regret to inform you that we are unable to accept your paper for publication at this time.\n\n{{comments}}\n\nWe appreciate your interest in our journal.\n\nBest regards,\nEditorial Team',
'author_name,paper_title,paper_code,journal_name,comments', 'decision', 1),

('reviewer_invitation', 'Invitation to Review - {{paper_code}}',
'Dear {{reviewer_name}},\n\nYou are invited to review the paper \"{{paper_title}}\" ({{paper_code}}) for {{journal_name}}.\n\nAbstract:\n{{abstract}}\n\nPlease respond to this invitation by {{deadline}}.\n\nAccept: {{accept_link}}\nDecline: {{decline_link}}\n\nBest regards,\nEditorial Team',
'reviewer_name,paper_title,paper_code,journal_name,abstract,deadline,accept_link,decline_link', 'review', 1),

('review_reminder', 'Review Reminder - {{paper_code}}',
'Dear {{reviewer_name}},\n\nThis is a reminder that your review for paper \"{{paper_title}}\" ({{paper_code}}) is due on {{deadline}}.\n\nPlease submit your review at your earliest convenience.\n\nBest regards,\nEditorial Team',
'reviewer_name,paper_title,paper_code,deadline', 'review', 1),

('general_notification', 'Notification from {{journal_name}}',
'Dear {{recipient_name}},\n\n{{message}}\n\nBest regards,\nEditorial Team\n{{journal_name}}',
'recipient_name,message,journal_name', 'general', 1)

ON DUPLICATE KEY UPDATE
    subject = VALUES(subject),
    body = VALUES(body);

-- ============================================================================
-- SECTION 9: DATA CLEANUP AND VALIDATION
-- ============================================================================

-- 9.1 Fix any NULL values in critical fields
UPDATE `paper` SET status = 'submitted' WHERE status IS NULL OR status = '';
UPDATE `paper` SET mailstatus = '0' WHERE mailstatus IS NULL;

-- 9.2 Fix online_review with invalid paper_id references
UPDATE `online_review` 
SET paper_id = 0 
WHERE paper_id = '' OR paper_id IS NULL;

-- ============================================================================
-- SECTION 10: RE-ENABLE CONSTRAINTS AND VERIFY
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 1;

-- Verification queries
SELECT '========================================' AS '';
SELECT 'MIGRATION COMPLETED - SUMMARY REPORT' AS '';
SELECT '========================================' AS '';

SELECT 'Users migrated:' AS metric, COUNT(*) AS count FROM `user`;
SELECT 'User roles created:' AS metric, COUNT(*) AS count FROM `user_role`;
SELECT 'Papers in system:' AS metric, COUNT(*) AS count FROM `paper`;
SELECT 'Paper versions created:' AS metric, COUNT(*) AS count FROM `paper_version`;
SELECT 'Paper co-authors:' AS metric, COUNT(*) AS count FROM `paper_co_author`;
SELECT 'Published papers:' AS metric, COUNT(*) AS count FROM `paper_published`;
SELECT 'Online reviews:' AS metric, COUNT(*) AS count FROM `online_review`;
SELECT 'Editors:' AS metric, COUNT(*) AS count FROM `editor`;
SELECT 'Volumes created:' AS metric, COUNT(*) AS count FROM `volume`;
SELECT 'Issues:' AS metric, COUNT(*) AS count FROM `issue`;
SELECT 'Journals:' AS metric, COUNT(*) AS count FROM `journal`;
SELECT 'Email templates:' AS metric, COUNT(*) AS count FROM `email_template`;

SELECT '========================================' AS '';
SELECT 'Migration completed successfully!' AS '';
SELECT '========================================' AS '';

COMMIT;

-- ============================================================================
-- END OF MIGRATION SCRIPT
-- ============================================================================
