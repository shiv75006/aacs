-- Fix database tables to match SQLAlchemy models exactly
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- FIX USER TABLE
-- ============================================

-- Check if backup exists and drop it
DROP TABLE IF EXISTS user_backup;

-- Backup user data
CREATE TABLE user_backup AS SELECT * FROM user;

-- Drop old user table
DROP TABLE IF EXISTS user;

-- Create user table matching SQLAlchemy model exactly
CREATE TABLE user (
  id int NOT NULL AUTO_INCREMENT,
  email varchar(255) NOT NULL,
  password varchar(255) NOT NULL,
  role varchar(50) DEFAULT 'User',
  fname varchar(100) DEFAULT NULL,
  lname varchar(100) DEFAULT NULL,
  mname varchar(100) DEFAULT NULL,
  title varchar(100) DEFAULT NULL,
  affiliation varchar(255) DEFAULT NULL,
  specialization text DEFAULT NULL,
  contact varchar(20) DEFAULT NULL,
  address text DEFAULT NULL,
  added_on datetime DEFAULT CURRENT_TIMESTAMP,
  salutation varchar(20) DEFAULT NULL,
  designation varchar(100) DEFAULT NULL,
  department varchar(200) DEFAULT NULL,
  organisation varchar(255) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Restore user data
INSERT INTO user (id, email, password, role, fname, lname, mname, title, affiliation, specialization, contact, address, added_on)
SELECT id, email, password, role, fname, lname, mname, title, affiliation, specialization, contact, address, added_on
FROM user_backup;

-- Cleanup
DROP TABLE IF EXISTS user_backup;

-- ============================================
-- FIX PAPER TABLE
-- ============================================

-- Backup paper data
DROP TABLE IF EXISTS paper_backup;
CREATE TABLE paper_backup AS SELECT * FROM paper;

-- Drop old paper table
DROP TABLE IF EXISTS paper;

-- Create paper table matching SQLAlchemy model exactly
CREATE TABLE paper (
  id int NOT NULL AUTO_INCREMENT,
  paper_code varchar(200) NOT NULL DEFAULT '',
  journal int DEFAULT NULL,
  title varchar(500) NOT NULL DEFAULT '',
  abstract varchar(1500) NOT NULL DEFAULT '',
  keyword varchar(1000) NOT NULL DEFAULT '',
  file varchar(200) NOT NULL DEFAULT '',
  added_on datetime DEFAULT CURRENT_TIMESTAMP,
  added_by varchar(100) NOT NULL DEFAULT '',
  status varchar(50) NOT NULL DEFAULT 'submitted',
  mailstatus varchar(10) NOT NULL DEFAULT '0',
  volume varchar(100) NOT NULL DEFAULT '',
  issue varchar(100) NOT NULL DEFAULT '',
  author varchar(100) NOT NULL DEFAULT '',
  coauth varchar(200) NOT NULL DEFAULT '',
  rev varchar(200) NOT NULL DEFAULT '',
  version_number int NOT NULL DEFAULT 1,
  revision_count int NOT NULL DEFAULT 0,
  revision_deadline datetime DEFAULT NULL,
  revision_notes text DEFAULT NULL,
  revision_requested_date datetime DEFAULT NULL,
  research_area varchar(200) DEFAULT NULL,
  message_to_editor text DEFAULT NULL,
  terms_accepted tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Restore paper data (convert journal from varchar to int)
INSERT INTO paper (id, paper_code, journal, title, abstract, keyword, file, added_on, added_by, status, mailstatus, volume, issue, author, coauth, rev, version_number, revision_count, revision_deadline, revision_notes, revision_requested_date, research_area, message_to_editor, terms_accepted)
SELECT 
  id, 
  paper_code, 
  CAST(journal AS SIGNED), 
  title, 
  abstract, 
  keyword, 
  file, 
  added_on, 
  added_by, 
  status, 
  mailstatus, 
  volume, 
  issue, 
  author, 
  coauth, 
  rev,
  COALESCE(version_number, 1),
  COALESCE(revision_count, 0),
  revision_deadline,
  revision_notes,
  revision_requested_date,
  research_area,
  message_to_editor,
  COALESCE(terms_accepted, 0)
FROM paper_backup;

-- Cleanup
DROP TABLE IF EXISTS paper_backup;

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Tables fixed successfully' AS status;
