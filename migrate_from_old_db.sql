-- =====================================================
-- AACS DATABASE MIGRATION SCRIPT
-- Migrates data from old schema to new schema
-- =====================================================
-- Version: 1.0
-- Date: Generated for AACS Journal Management System
-- =====================================================

-- IMPORTANT: BACKUP YOUR DATABASE BEFORE RUNNING THIS SCRIPT!
-- Command: mysqldump -u root -p aacsjour_aacs > backup_before_migration.sql

-- =====================================================
-- STEP 0: DISABLE FOREIGN KEY CHECKS
-- =====================================================
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_SAFE_UPDATES = 0;

-- =====================================================
-- STEP 1: CREATE NEW TABLES IF THEY DON'T EXIST
-- =====================================================

-- User table (if not exists)
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `role` VARCHAR(50) DEFAULT 'User',
    `fname` VARCHAR(100),
    `lname` VARCHAR(100),
    `mname` VARCHAR(100),
    `title` VARCHAR(100),
    `affiliation` VARCHAR(255),
    `specialization` TEXT,
    `contact` VARCHAR(20),
    `address` TEXT,
    `added_on` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `salutation` VARCHAR(20),
    `designation` VARCHAR(100),
    `department` VARCHAR(200),
    `organisation` VARCHAR(255),
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User Role table for multi-role support
CREATE TABLE IF NOT EXISTS `user_role` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `role` VARCHAR(50) NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'approved',
    `requested_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `approved_by` INT,
    `approved_at` DATETIME,
    `rejected_reason` TEXT,
    `journal_id` INT,
    `editor_type` VARCHAR(50),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_role` (`role`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Paper Co-Author table
CREATE TABLE IF NOT EXISTS `paper_co_author` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `paper_id` INT NOT NULL,
    `salutation` VARCHAR(20),
    `first_name` VARCHAR(100) NOT NULL,
    `middle_name` VARCHAR(100),
    `last_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(255),
    `designation` VARCHAR(100),
    `department` VARCHAR(200),
    `organisation` VARCHAR(255),
    `author_order` INT NOT NULL DEFAULT 1,
    `is_corresponding` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_paper_id` (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Paper Version table (for version history)
CREATE TABLE IF NOT EXISTS `paper_version` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `paper_id` INT NOT NULL,
    `version_number` INT NOT NULL,
    `file` VARCHAR(200) NOT NULL,
    `file_size` INT,
    `uploaded_on` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `revision_reason` TEXT,
    `change_summary` TEXT,
    `uploaded_by` VARCHAR(100) NOT NULL,
    INDEX `idx_paper_id` (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reviewer Invitation table
CREATE TABLE IF NOT EXISTS `reviewer_invitation` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `paper_id` INT NOT NULL,
    `reviewer_id` INT,
    `reviewer_email` VARCHAR(255) NOT NULL,
    `reviewer_name` VARCHAR(255),
    `journal_id` VARCHAR(100),
    `invitation_token` VARCHAR(255) NOT NULL UNIQUE,
    `token_expiry` DATETIME NOT NULL,
    `status` VARCHAR(50) DEFAULT 'pending',
    `invited_on` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `accepted_on` DATETIME,
    `declined_on` DATETIME,
    `invitation_message` TEXT,
    `decline_reason` TEXT,
    INDEX `idx_paper_id` (`paper_id`),
    INDEX `idx_invitation_token` (`invitation_token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Review Submission table
CREATE TABLE IF NOT EXISTS `review_submission` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `paper_id` INT NOT NULL,
    `reviewer_id` VARCHAR(100) NOT NULL,
    `assignment_id` INT,
    `technical_quality` INT,
    `clarity` INT,
    `originality` INT,
    `significance` INT,
    `overall_rating` INT,
    `author_comments` TEXT,
    `confidential_comments` TEXT,
    `recommendation` VARCHAR(50),
    `review_report_file` VARCHAR(500),
    `file_version` INT DEFAULT 1,
    `status` VARCHAR(50) DEFAULT 'draft',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `submitted_at` DATETIME,
    INDEX `idx_paper_id` (`paper_id`),
    INDEX `idx_reviewer_id` (`reviewer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Paper Correspondence table
CREATE TABLE IF NOT EXISTS `paper_correspondence` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `paper_id` INT NOT NULL,
    `sender_id` INT,
    `sender_email` VARCHAR(255),
    `sender_type` VARCHAR(50) DEFAULT 'author',
    `recipient_type` VARCHAR(50) DEFAULT 'editor',
    `subject` VARCHAR(500),
    `message` TEXT NOT NULL,
    `attachment` VARCHAR(255),
    `is_read` TINYINT(1) DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_paper_id` (`paper_id`),
    INDEX `idx_sender_id` (`sender_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- STEP 2: MIGRATE ADMIN USERS TO USER TABLE
-- =====================================================

-- First, migrate admin users to user table
INSERT INTO `user` (`email`, `password`, `role`, `fname`, `lname`, `added_on`)
SELECT 
    a.fld_email,
    a.fld_password,
    'admin',
    a.fld_fname,
    a.fld_lname,
    a.fld_addedon
FROM `admin` a
WHERE a.fld_email IS NOT NULL 
  AND a.fld_email != ''
  AND a.fld_email NOT IN (SELECT email FROM `user` WHERE email IS NOT NULL)
ON DUPLICATE KEY UPDATE
    fname = VALUES(fname),
    lname = VALUES(lname);

-- Create user_role entries for admin users
INSERT INTO `user_role` (`user_id`, `role`, `status`, `requested_at`, `approved_at`)
SELECT 
    u.id,
    'admin',
    'approved',
    NOW(),
    NOW()
FROM `user` u
INNER JOIN `admin` a ON u.email = a.fld_email
WHERE NOT EXISTS (
    SELECT 1 FROM `user_role` ur 
    WHERE ur.user_id = u.id AND ur.role = 'admin'
);

-- =====================================================
-- STEP 3: MIGRATE EDITOR USERS TO USER TABLE
-- =====================================================

-- Migrate editors to user table (only if email doesn't exist)
INSERT INTO `user` (`email`, `password`, `role`, `fname`, `lname`, `affiliation`, `department`, `organisation`, `contact`, `address`, `added_on`)
SELECT 
    e.editor_email,
    e.password,
    'editor',
    SUBSTRING_INDEX(e.editor_name, ' ', 1) as fname,
    CASE 
        WHEN LOCATE(' ', e.editor_name) > 0 
        THEN SUBSTRING_INDEX(e.editor_name, ' ', -1)
        ELSE ''
    END as lname,
    e.editor_affiliation,
    e.editor_department,
    e.editor_college,
    e.editor_contact,
    e.editor_address,
    e.added_on
FROM `editor` e
WHERE e.editor_email IS NOT NULL 
  AND e.editor_email != ''
  AND e.editor_email NOT IN (SELECT email FROM `user` WHERE email IS NOT NULL)
ON DUPLICATE KEY UPDATE
    affiliation = VALUES(affiliation),
    department = VALUES(department),
    organisation = VALUES(organisation);

-- Create user_role entries for editor users (with journal assignment)
INSERT INTO `user_role` (`user_id`, `role`, `status`, `requested_at`, `approved_at`, `journal_id`, `editor_type`)
SELECT 
    u.id,
    'editor',
    'approved',
    NOW(),
    NOW(),
    e.journal_id,
    COALESCE(e.role, 'section_editor')
FROM `user` u
INNER JOIN `editor` e ON u.email = e.editor_email
WHERE NOT EXISTS (
    SELECT 1 FROM `user_role` ur 
    WHERE ur.user_id = u.id AND ur.role = 'editor' AND ur.journal_id = e.journal_id
);

-- =====================================================
-- STEP 4: MIGRATE CO-AUTHORS TO PAPER_CO_AUTHOR TABLE
-- =====================================================

-- Migrate author records to paper_co_author
INSERT INTO `paper_co_author` (`paper_id`, `first_name`, `last_name`, `email`, `organisation`, `author_order`, `created_at`)
SELECT 
    a.paper_id,
    SUBSTRING_INDEX(a.author_name, ' ', 1) as first_name,
    CASE 
        WHEN LOCATE(' ', a.author_name) > 0 
        THEN SUBSTRING_INDEX(a.author_name, ' ', -1)
        ELSE ''
    END as last_name,
    a.author_email,
    a.author_address,
    (@row_num := @row_num + 1) as author_order,
    a.added_on
FROM `author` a, (SELECT @row_num := 0) r
WHERE a.paper_id IS NOT NULL 
  AND a.paper_id != ''
ON DUPLICATE KEY UPDATE
    email = VALUES(email);

-- =====================================================
-- STEP 5: INSERT DEFAULT EMAIL TEMPLATES
-- =====================================================

INSERT INTO `email_template` (`name`, `slug`, `subject`, `body_template`, `placeholders`, `category`, `is_active`)
VALUES 
    ('Submission Confirmation', 'submission_confirmation', 'Paper Submission Confirmation - {{paper_code}}', 
     'Dear {{author_name}},\n\nThank you for submitting your paper titled "{{paper_title}}" to {{journal_name}}.\n\nYour submission has been received and assigned the code: {{paper_code}}\n\nWe will notify you once the review process begins.\n\nBest regards,\nAACS Editorial Team', 
     'author_name,paper_title,journal_name,paper_code', 'submission', 1),
    
    ('Reviewer Invitation', 'reviewer_invitation', 'Invitation to Review Paper - {{journal_name}}',
     'Dear {{reviewer_name}},\n\nWe would like to invite you to review a paper submitted to {{journal_name}}.\n\nPaper Title: {{paper_title}}\nAbstract: {{paper_abstract}}\n\nPlease click the link below to accept or decline this invitation:\n{{invitation_link}}\n\nThis invitation expires on {{expiry_date}}.\n\nThank you for your contribution.\n\nBest regards,\nAACS Editorial Team',
     'reviewer_name,journal_name,paper_title,paper_abstract,invitation_link,expiry_date', 'reviewer', 1),
    
    ('Review Reminder', 'review_reminder', 'Reminder: Review Due - {{paper_code}}',
     'Dear {{reviewer_name}},\n\nThis is a reminder that your review for paper "{{paper_title}}" ({{paper_code}}) is due on {{due_date}}.\n\nPlease submit your review at your earliest convenience.\n\nBest regards,\nAACS Editorial Team',
     'reviewer_name,paper_title,paper_code,due_date', 'reviewer', 1),
    
    ('Decision Accept', 'decision_accept', 'Paper Accepted - {{paper_code}}',
     'Dear {{author_name}},\n\nWe are pleased to inform you that your paper titled "{{paper_title}}" has been accepted for publication in {{journal_name}}.\n\nPaper Code: {{paper_code}}\n\nCongratulations on your acceptance!\n\nBest regards,\nAACS Editorial Team',
     'author_name,paper_title,journal_name,paper_code', 'decision', 1),
    
    ('Decision Revision', 'decision_revision', 'Revision Required - {{paper_code}}',
     'Dear {{author_name}},\n\nYour paper titled "{{paper_title}}" ({{paper_code}}) requires revision before it can be considered for publication.\n\nPlease review the comments below and submit your revised manuscript by {{deadline}}.\n\nReviewer Comments:\n{{reviewer_comments}}\n\nBest regards,\nAACS Editorial Team',
     'author_name,paper_title,paper_code,deadline,reviewer_comments', 'decision', 1),
    
    ('Decision Reject', 'decision_reject', 'Paper Decision - {{paper_code}}',
     'Dear {{author_name}},\n\nAfter careful review, we regret to inform you that your paper titled "{{paper_title}}" ({{paper_code}}) has not been accepted for publication in {{journal_name}}.\n\nReviewer feedback:\n{{reviewer_comments}}\n\nWe encourage you to consider the feedback for future submissions.\n\nBest regards,\nAACS Editorial Team',
     'author_name,paper_title,paper_code,journal_name,reviewer_comments', 'decision', 1),
    
    ('Password Reset', 'password_reset', 'Password Reset Request - AACS Journals',
     'Dear {{user_name}},\n\nWe received a request to reset your password for your AACS Journals account.\n\nClick the link below to reset your password:\n{{reset_link}}\n\nThis link expires in 24 hours.\n\nIf you did not request this reset, please ignore this email.\n\nBest regards,\nAACS Team',
     'user_name,reset_link', 'system', 1),
    
    ('Contact Editorial', 'contact_editorial', 'Contact from Author: {{subject}}',
     'A message has been received from an author regarding paper {{paper_code}}.\n\nFrom: {{author_name}} ({{author_email}})\nSubject: {{subject}}\n\nMessage:\n{{message}}\n\n---\nThis message was sent via the AACS Journal Management System.',
     'paper_code,author_name,author_email,subject,message', 'correspondence', 1)
ON DUPLICATE KEY UPDATE
    subject = VALUES(subject),
    body_template = VALUES(body_template);

-- =====================================================
-- STEP 6: CREATE DEFAULT ADMIN USER (IF NEEDED)
-- =====================================================

-- Insert default admin if no admin exists
INSERT INTO `user` (`email`, `password`, `role`, `fname`, `lname`, `added_on`)
SELECT 
    'shivsaini75006@gmail.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qR6zMFQ/aVtC0.',
    'admin',
    'Shiv',
    'Saini',
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM `user` WHERE email = 'shivsaini75006@gmail.com'
);

-- Create admin role for default admin
INSERT INTO `user_role` (`user_id`, `role`, `status`, `requested_at`, `approved_at`)
SELECT 
    id,
    'admin',
    'approved',
    NOW(),
    NOW()
FROM `user` 
WHERE email = 'shivsaini75006@gmail.com'
AND NOT EXISTS (
    SELECT 1 FROM `user_role` ur 
    INNER JOIN `user` u ON ur.user_id = u.id 
    WHERE u.email = 'shivsaini75006@gmail.com' AND ur.role = 'admin'
);

-- =====================================================
-- STEP 7: RE-ENABLE FOREIGN KEY CHECKS
-- =====================================================
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;

-- =====================================================
-- STEP 8: VERIFICATION QUERIES
-- =====================================================

-- Check user migration
SELECT 'Users migrated:' as metric, COUNT(*) as count FROM `user`;

-- Check user roles created
SELECT 'User roles created:' as metric, COUNT(*) as count FROM `user_role`;

-- Check roles breakdown
SELECT 'Roles breakdown:' as metric, role, COUNT(*) as count FROM `user_role` GROUP BY role;

-- Check co-authors migrated
SELECT 'Co-authors migrated:' as metric, COUNT(*) as count FROM `paper_co_author`;

-- Check email templates
SELECT 'Email templates:' as metric, COUNT(*) as count FROM `email_template`;

-- Check for duplicate emails (should be 0)
SELECT 'Duplicate emails:' as metric, COUNT(*) as count 
FROM (SELECT email FROM `user` GROUP BY email HAVING COUNT(*) > 1) as dups;

-- Check editor-journal assignments
SELECT 'Editor assignments:' as metric, COUNT(*) as count 
FROM `user_role` WHERE role = 'editor' AND journal_id IS NOT NULL;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
SELECT '========================================' as '';
SELECT 'MIGRATION COMPLETED SUCCESSFULLY!' as status;
SELECT '========================================' as '';
