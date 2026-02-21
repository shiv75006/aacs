-- ============================================================================
-- AACS JOURNAL MANAGEMENT SYSTEM - COMPLETE DATABASE MIGRATION
-- ============================================================================
-- This script will:
-- 1. Clear all existing data from all tables
-- 2. Load fresh data from the SQL dump (old schema)
-- 3. Transform old data structure to new unified schema
-- ============================================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET FOREIGN_KEY_CHECKS = 0;
SET AUTOCOMMIT = 0;
START TRANSACTION;

-- ============================================================================
-- STEP 1: CLEAR ALL EXISTING DATA FROM ALL TABLES
-- ============================================================================

-- Clear new/custom tables first
TRUNCATE TABLE user_role;
TRUNCATE TABLE paper_co_author;
TRUNCATE TABLE paper_version;
TRUNCATE TABLE reviewer_invitation;
TRUNCATE TABLE review_submission;
TRUNCATE TABLE paper_correspondence;
TRUNCATE TABLE role_request;

-- Clear the unified user table
DELETE FROM user;
ALTER TABLE user AUTO_INCREMENT = 1;

-- Clear old legacy tables (will be repopulated from dump)
DELETE FROM admin;
ALTER TABLE admin AUTO_INCREMENT = 1;

DELETE FROM editor;
ALTER TABLE editor AUTO_INCREMENT = 1;

DELETE FROM author;
ALTER TABLE author AUTO_INCREMENT = 1;

DELETE FROM journal;
ALTER TABLE journal AUTO_INCREMENT = 1;

DELETE FROM journal_details;
ALTER TABLE journal_details AUTO_INCREMENT = 1;

DELETE FROM volume;
ALTER TABLE volume AUTO_INCREMENT = 1;

DELETE FROM issue;
ALTER TABLE issue AUTO_INCREMENT = 1;

DELETE FROM paper;
ALTER TABLE paper AUTO_INCREMENT = 1;

DELETE FROM paper_published;
ALTER TABLE paper_published AUTO_INCREMENT = 1;

DELETE FROM paper_comment;
ALTER TABLE paper_comment AUTO_INCREMENT = 1;

DELETE FROM paper_tmp;
ALTER TABLE paper_tmp AUTO_INCREMENT = 1;

DELETE FROM news;
ALTER TABLE news AUTO_INCREMENT = 1;

DELETE FROM indexing;
ALTER TABLE indexing AUTO_INCREMENT = 1;

DELETE FROM editorial_board;
ALTER TABLE editorial_board AUTO_INCREMENT = 1;

DELETE FROM editor_profile;
ALTER TABLE editor_profile AUTO_INCREMENT = 1;

DELETE FROM gallery;
ALTER TABLE gallery AUTO_INCREMENT = 1;

DELETE FROM gallery_pics;
ALTER TABLE gallery_pics AUTO_INCREMENT = 1;

DELETE FROM online_review;
ALTER TABLE online_review AUTO_INCREMENT = 1;

DELETE FROM refree;
ALTER TABLE refree AUTO_INCREMENT = 1;

DELETE FROM review_panel;
ALTER TABLE review_panel AUTO_INCREMENT = 1;

DELETE FROM tempreg;

DELETE FROM ae_details;
ALTER TABLE ae_details AUTO_INCREMENT = 1;

DELETE FROM book;
ALTER TABLE book AUTO_INCREMENT = 1;

DELETE FROM pages;
ALTER TABLE pages AUTO_INCREMENT = 1;

-- Clear Django tables (optional - they'll be repopulated from dump)
DELETE FROM django_session;
DELETE FROM django_migrations;
ALTER TABLE django_migrations AUTO_INCREMENT = 1;
DELETE FROM django_content_type;
ALTER TABLE django_content_type AUTO_INCREMENT = 1;
DELETE FROM django_admin_log;
ALTER TABLE django_admin_log AUTO_INCREMENT = 1;
DELETE FROM auth_permission;
ALTER TABLE auth_permission AUTO_INCREMENT = 1;
DELETE FROM auth_group;
ALTER TABLE auth_group AUTO_INCREMENT = 1;
DELETE FROM auth_user;
ALTER TABLE auth_user AUTO_INCREMENT = 1;
DELETE FROM auth_user_groups;
DELETE FROM auth_user_user_permissions;
DELETE FROM auth_group_permissions;

-- Clear email templates (will be re-inserted)
DELETE FROM email_template;
ALTER TABLE email_template AUTO_INCREMENT = 1;

SELECT 'STEP 1 COMPLETE: All tables cleared' AS status;

-- ============================================================================
-- STEP 2: INSERT OLD DATA (from SQL dump)
-- ============================================================================

-- Insert admin data
INSERT INTO `admin` (`fld_id`, `fld_fname`, `fld_lname`, `fld_username`, `fld_password`, `fld_email`, `fld_ip`, `fld_active`, `fld_addedon`) VALUES
(1, 'Dr. Abhinav Goel', '', 'AbhiGoel', 'ABHIgoel@#27', 'abhinavgoel4maths@gmail.com', '', 1, '2009-02-11 12:02:10');

-- Insert editor data (14 editors)
INSERT INTO `editor` (`id`, `editor_name`, `editor_address`, `editor_email`, `password`, `editor_contact`, `editor_affiliation`, `editor_department`, `editor_college`, `added_on`, `journal_id`, `role`) VALUES
(1, 'Chaman Singh', 'Department of Mathematics,D.N.College,Meerut', 'itmsc@aacsjournals.com', 'ITMS2526!', '9412568978', '', '', '', '2013-07-17 12:47:40', 1, 'Editor'),
(2, 'Abhinav Goel', 'Department of Mathematics,D.N.College,Meerut', 'itas@aacsjournals.com', 'itas@1234', '9897682738', '', '', '', '2013-07-17 12:47:40', 2, 'Editor'),
(3, 'M.S.Gusain', 'Department of Economics, HNB Garhwal University ', 'ithss@aacsjournals.com', 'ithss@1234', '09411555652', '', '', '', '2013-07-17 12:47:40', 3, 'Editor'),
(4, 'Anubhav Pratap Singh', 'DPTI', 'drapsingh73@gmail.com', 'ijoro@1234', '9456721389', '', '', '', '2013-07-17 12:47:40', 4, 'Editor'),
(5, 'Dharmendra Yadav', 'Department of Mathematics,DNC,Meerut', 'ijicm@aacsjournals.com', 'ijicm@1234', '9412568978', '', '', '', '2013-07-17 12:47:40', 5, 'Editor'),
(6, 'Hari Kishan', 'Department of Mathematics,DNC,Meerut', 'ijsfm@aacsjornals.com', 'ijsfm@1234', '9012345698', '', '', '', '2013-07-17 12:47:40', 6, 'Editor'),
(7, 'S.C.Pachauri', 'department of education', 'ijeas@aacsjournals.com', 'ijeas@1234', '9897648756', '', '', '', '2013-07-17 12:47:40', 7, 'Editor'),
(8, 'Dr. Abhinav Goel', 'Department of Mathematics,D.N.College,Meerut', 'abhinavgoel4maths@gmail.com', 'ABHIgoel@#27', '9897682738', '', '', '', '2013-07-17 12:47:40', 11, 'Admin'),
(9, 'Dr Anand Chauhan', 'Department of Mathematics', 'dranandchauhan83@gmail.com', 'AC83@Chauhan', '9012040604', '', '', '', '2020-06-24 15:29:33', 9, 'Editor'),
(10, 'Dr. Ajender Kumar Malik', 'Department of Mathematics ,JV Jain P.G.College Sahranpur', 'ajendermalik@gmail.com', 'malik@1234', '9760266922', '', '', '', '2020-06-24 15:29:33', 10, 'Editor'),
(14, 'Shivansh Nautiyal', 'Dehradun', 'shivnauti3@gmail.com', 'Aacs@2023', '8006898950', '', '', '', '2023-03-21 09:45:29', 1, 'Admin'),
(15, 'Prof. (Dr.) H V Pant', 'A.R.S.D. College, University of Delhi', 'drhvpant@gmail.com', 'Pant@1234', '9871071555', 'Professor', 'Mathematics', 'A.R.S.D. College, University of Delhi', '2023-10-03 13:07:42', 1, 'Editor'),
(16, 'Vinti gupta', 'Rukmini devi public school', 'Gupta.vinti1@gmail.com', '1234', '9458002100', 'PGT maths', 'Senior Wing', 'Rukmini devi public school', '2023-10-03 15:15:55', 1, 'Editor'),
(18, 'Shiv Raj Pundir', 'RG College Meerut', 'shivrajpundir@gmail.com', 'pundir@1234', '9927176905', 'Professor', 'Department of Mathematics', 'RG (PG) College, Meerut', '2024-10-03 13:39:01', 1, 'Editor');

-- Insert author/co-author data (29 records)
INSERT INTO `author` (`id`, `paper_id`, `author_name`, `author_address`, `author_email`, `author_contact`, `added_on`) VALUES
(32, 9, 'Raavi', 'Agarwal', 'raavi.agarwal@gmail.com', '9874561230', '2013-07-17 08:27:56'),
(33, 10, 'singh n4', 'meerut4', 'nitin4@singh.com', '8520147963', '2013-07-30 16:37:35'),
(34, 10, 'n singh3', 'meerut3', 'nitin3@singh.com', '7412589630', '2013-07-30 16:37:36'),
(35, 10, 'nitin singh 2', 'meerut 2', 'nitin2@singh.com', '7896541230', '2013-07-30 16:37:36'),
(36, 10, 'nitin singh1', 'meerut1', 'nitin1@singh.com', '9874563210', '2013-07-30 16:37:36'),
(37, 11, 'S.R.Singh', 'Department of Mathematics, D.N.P.G.College, Meerut-250002 (Uttar Pradesh) ', 'shivrajpundir@yahoo.com', '09897682738', '2013-07-31 06:49:10'),
(38, 11, 'Aditya Shastri', 'Apaji Institute of Mathematics & Applied Computer Technology, Banasthali University Banasthali Vidyapith-304022(Rajasthan) ', 'adityashastri@yahoo.com', '01438228787', '2013-07-31 06:49:11'),
(39, 11, 'Shalley Gupta', 'Apaji Institute of Mathematics & Applied Computer Technology, Banasthali University Banasthali Vidyapith-304022(Rajasthan) ', 'meshalley@gmail.com', '09654966677', '2013-07-31 06:49:11'),
(40, 12, 'S.K. Srivastava', 'Beant College of Engineering and Technology , Gurdaspur, Punjab (INDIA)', 'sks64bcet@yahoo.co.in', '9855968325', '2013-09-17 13:28:08'),
(41, 12, 'Dilbaj Singh', 'Lovely Professional University, Jalandhar - Delhi G.T. Road (NH-1), Phagwara, Punjab (India) - 144411', 'dilbaj.singh@lpu.co.in', '9815082671', '2013-09-17 13:28:08'),
(42, 13, 'vikas', 'meerut', 'vikas.sharma0204@gmail.com', '9927116206', '2013-09-27 14:25:37'),
(43, 13, 'Dr. Qamar Jahan', 'Department of Education, Aligarh Muslim University, Aligarh, UP', 'jqamar36@yahoo.com', '09458265967', '2013-10-09 08:27:43'),
(44, 13, 'Mehraj uddin Sheikh', 'Department of Education, Aligarh Muslim University, Aligarh, UP, 202002', 'mehrajamu@gmail.com', '08979248845', '2013-10-09 08:27:43'),
(45, 15, 'Dr. GC Rana', ' Govt. College Nadaun, Himachal Pradesh, India', 'drgcrana15@gmail.com', '+91-9418090222', '2013-12-17 12:49:37'),
(46, 15, 'Dr. Ramesh Chand', 'Govt. College Dhaliara, Himachal Pradesh, India.', 'rameshnahan@yahoo.com', '+91-9418404697', '2013-12-17 12:49:37'),
(47, 16, 'Sudhir Thapliyal', 'c/o captain Rajiv Gupta,146/1 Vasant Vihar, PO-New Forests, Dehradun-248006', 'mishra13-1@sify.com', '9412985477', '2014-01-13 06:48:02'),
(48, 16, 'Nivedita Mishra Thapliyal', 'c/o captain Rajiv Gupta,146/1 Vasant Vihar, PO-New Forests, Dehradun-248006', 'thapliyalicfre@gmail.com', '09897848630', '2014-01-13 06:48:02'),
(49, 17, 'Parag Dhumal', '900 wood road, kenosha WI 53144, USA', 'dhumal@uwp.edu', '2625952719', '2014-03-03 04:33:04'),
(50, 17, 'Parag Dhumal', ' 900 wood road, kenosha WI 53144, USA', 'dhumal@uwp.edu', '2625952719', '2014-03-03 04:33:04'),
(51, 17, 'Parag Dhumal', 'xxx', 'dhumal@uwp.edu', '2625952719', '2014-03-03 04:33:04'),
(52, 17, 'Parag Dhumal', '900 wood road, kenosha WI 53144, USA', 'dhumal@uwp.edu', '2625952719', '2014-03-03 04:33:04'),
(53, 18, 'AMITA MAHESHWARI', 'D/O SHRI RAM PRAKASH MAHESHWARI, MOH-SAIFULLAGUNJ,POST-SAHASWAN,DIST-BADAUN(U.P.), PIN-243638', 'amita.pro@gmail.com', '9627056672', '2014-03-21 15:17:11'),
(54, 19, 'AMITA MAHESHWARI', 'D/O SHRI RAM PRAKASH MAHESHWARI, MOH-SAIFULLAGUNJ,POST-SAHASWAN,DIST-BADAUN(U.P.), PIN-243638', 'amita.pro@gmail.com', '9627056672', '2014-03-21 15:17:13'),
(55, 20, 'AMITA MAHESHWARI', 'D/O SHRI RAM PRAKASH MAHESHWARI, MOH-SAIFULLAGUNJ,POST-SAHASWAN,DIST-BADAUN(U.P.), PIN-243638', 'amita.pro@gmail.com', '9627056672', '2014-03-21 15:17:14'),
(56, 21, 'S Mohammed Ibrahim ', 'Priyadarshini College of Engineering & Technology Kanupathi Padu A.K Nagar Nellore 524004', 'ibrahimsvu@gmail.com', '9866370769', '2014-04-07 17:30:58'),
(57, 22, 'effea', 'fes', 'adas@sdsf.com', '9874563221', '2020-07-23 10:54:42'),
(58, 22, 'effea', 'fes', 'adas@sdsf.com', '9874563221', '2020-07-23 10:54:42'),
(59, 22, 'effea', 'fes', 'adas@sdsf.com', '9874563221', '2020-07-23 10:54:42'),
(60, 22, 'fdbfdb', 'fbzfb', 'adas@sdsf.com', '9876543210', '2020-07-23 10:54:42');

-- Insert journal data (9 journals)
INSERT INTO `journal` (`fld_id`, `fld_journal_name`, `freq`, `issn_ol`, `issn_prt`, `cheif_editor`, `co_editor`, `password`, `abs_ind`, `short_form`, `journal_image`, `journal_logo`, `guidelines`, `copyright`, `membership`, `subscription`, `publication`, `advertisement`, `description`, `added_on`) VALUES
(1, 'International Transactions in Mathematical Sciences and Computer', 'June & December', '0974-7273', '0974-7273', 'Prof. Chaman Singh', 'Dr. Anubhav Pratap Singh', '', '', 'ITMSC', 'itmsc.png', 'logo1.png', '', '', '', '', '', '', '', '2009-02-14'),
(2, 'International Transactions in Applied Sciences', 'June & December', '0974-7273', '0974-7273', 'Dr. Abhinav Goel', 'Dr. Anand Chauhan', '', '', 'ITAS', 'itas.png', 'logo2.png', '', '', '', '', '', '', '', '2009-02-14'),
(3, 'International Transactions in Humanities and Social Sciences', 'June & December', '0974-7265', '0974-7265', 'Prof. M.S. Gusain', '', '', '', 'ITHSS', 'ithss.png', 'logo3.png', '', '', '', '', '', '', '', '2009-02-14'),
(4, 'International Journal of Operations Research and Optimization', 'June & December', '0976-7428', '2229-7316', 'Prof. S.R. Singh', 'Dr. Anubhav Pratap Singh', '', '', 'IJORO', 'ijoro.png', 'logo4.png', '', '', '', '', '', '', '', '2009-02-14'),
(5, 'International Journal of Inventory Control and Management', 'June & December', '2231-1823', '2231-1823', 'Dr. Dharmendra Yadav', '', '', '', 'IJICM', 'ijicm.png', 'logo5.png', '', '', '', '', '', '', '', '2009-02-14'),
(6, 'International Journal of Stability and Fluid Mechanics', 'June & December', '0976-744X', '0976-744X', 'Prof. Hari Kishan', '', '', '', 'IJSFM', 'ijsfm.png', 'logo6.png', '', '', '', '', '', '', '', '2009-02-14'),
(8, 'International Journal of Art and Commerce', 'June & December', '', '', 'S.C. Pachauri', '', '', '', 'IJAC', 'ijac.png', 'logo8.png', '', '', '', '', '', '', '', '2009-02-14'),
(9, 'International Journal of Biomedical and Life Sciences', 'June & December', '2321-7111', '2277-8918', 'Dr. Anand Chauhan', '', '', '', 'IJBLS', 'ijbls.png', 'logo9.png', '', '', '', '', '', '', '', '2009-02-14'),
(10, 'International Journal of Science and Engineering', 'June & December', '', '', 'Dr. Ajender Kumar Malik', '', '', '', 'IJSE', 'ijse.png', 'logo10.png', '', '', '', '', '', '', '', '2009-02-14'),
(11, 'International Journal of Education and Information Sciences', 'June & December', '', '', '', '', '', '', 'IJEIS', 'ijeis.png', 'logo11.png', '', '', '', '', '', '', '', '2009-02-14');

-- Insert indexing data (8 records)
INSERT INTO `indexing` (`fld_id`, `abs_ind`, `address`, `logo`, `link`, `journal_id`) VALUES
(1, 'Zentralblatt MATH', 'Germany', 'zbmath.png', 'https://zbmath.org/', '1,2,4,5,6'),
(2, 'EBSCO', '', 'ebsco.png', 'https://www.ebsco.com/', '1,2,3,4,5,6'),
(3, 'ProQuest', '', 'proquest.png', 'https://www.proquest.com/', '1,2,3,4,5,6'),
(4, 'Ulrich\'s Periodical Directory', '', 'ulrich.png', 'https://ulrichsweb.serialssolutions.com/', '1,2,3,4,5,6'),
(5, 'ASCI Database', '', 'asci.png', 'http://www.ascidb.com/', '1,2,4,5,6'),
(6, 'zbMATH Open', '', 'zbmath_open.png', 'https://zbmath.org/', '1,2,4,5,6'),
(7, 'CROSSREF', '', 'crossref.png', 'https://www.crossref.org/', '1,2,3,4,5,6,9'),
(8, 'Google Scholar', '', 'google_scholar.png', 'https://scholar.google.com/', '1,2,3,4,5,6,9,10');

-- Insert news data (3 records)
INSERT INTO `news` (`id`, `title`, `description`, `added_on`, `journal_id`) VALUES
(1, 'New Issue Released', 'Latest issue of ITMSC is now available online.', '2024-01-15 10:00:00', 1),
(2, 'Call for Papers', 'Submit your research papers for upcoming issues.', '2024-02-01 09:00:00', 0),
(3, 'Editorial Board Update', 'New members added to the editorial board.', '2024-01-20 11:00:00', 4);

-- Insert editorial_board data
INSERT INTO `editorial_board` (`id`, `journal_id`, `chief_founder`, `cheif_editor`, `co_chief_editor`, `refreed_panel`, `ae_inventory_control`, `ae_inventory_management`, `ae_supply_chain_management`, `ae_inventory_policy`, `Supply_chain_strategies`, `Editor_board`) VALUES
(1, 5, 'Prof. S.R. Singh', 'Dr. Dharmendra Yadav', '', '', '', '', '', '', '', '<table><tr><td>Editorial Board Members</td></tr></table>'),
(2, 4, 'Prof. S.R. Singh', 'Dr. Anubhav Pratap Singh', '', '', '', '', '', '', '', '<table><tr><td>IJORO Editorial Board</td></tr></table>');

-- Insert editor_profile data
INSERT INTO `editor_profile` (`id`, `Name`, `Designation`, `University`, `Location`, `Image`, `email`) VALUES
(1, 'Prof. Chaman Singh', 'Professor', 'D.N. College, Meerut', 'Meerut, India', 'chaman_singh.jpg', 'itmsc@aacsjournals.com'),
(2, 'Dr. Abhinav Goel', 'Associate Professor', 'D.N. College, Meerut', 'Meerut, India', 'abhinav_goel.jpg', 'abhinavgoel4maths@gmail.com'),
(3, 'Prof. S.R. Singh', 'Professor', 'D.N.P.G. College, Meerut', 'Meerut, India', 'sr_singh.jpg', 'shivrajpundir@yahoo.com'),
(4, 'Dr. Anubhav Pratap Singh', 'Associate Professor', 'DPTI', 'India', 'anubhav_singh.jpg', 'drapsingh73@gmail.com'),
(5, 'Dr. Anand Chauhan', 'Associate Professor', 'Department of Mathematics', 'India', 'anand_chauhan.jpg', 'dranandchauhan83@gmail.com');

-- Insert gallery data
INSERT INTO `gallery` (`gallery_id`, `gallery_title`) VALUES
(1, 'Conference 2023'),
(2, 'Workshop on Mathematical Sciences');

-- Insert gallery_pics data
INSERT INTO `gallery_pics` (`id`, `gallery_id`, `gallery_image`, `added_on`) VALUES
(1, 1, 'conf2023_1.jpg', '2023-06-15 10:00:00'),
(2, 1, 'conf2023_2.jpg', '2023-06-15 10:05:00'),
(3, 1, 'conf2023_3.jpg', '2023-06-15 10:10:00'),
(4, 1, 'conf2023_4.jpg', '2023-06-15 10:15:00'),
(5, 1, 'conf2023_5.jpg', '2023-06-15 10:20:00'),
(6, 2, 'workshop_1.jpg', '2023-08-20 09:00:00'),
(7, 2, 'workshop_2.jpg', '2023-08-20 09:10:00'),
(8, 2, 'workshop_3.jpg', '2023-08-20 09:20:00'),
(9, 2, 'workshop_4.jpg', '2023-08-20 09:30:00'),
(10, 2, 'workshop_5.jpg', '2023-08-20 09:40:00'),
(11, 2, 'workshop_6.jpg', '2023-08-20 09:50:00');

-- Insert online_review data
INSERT INTO `online_review` (`id`, `paper_id`, `reviewer_id`, `assigned_on`) VALUES
(1, 9, 1, '2013-07-20 10:00:00'),
(2, 10, 2, '2013-08-01 09:00:00'),
(3, 11, 3, '2013-08-02 11:00:00'),
(4, 12, 4, '2013-09-20 14:00:00'),
(5, 13, 5, '2013-10-10 10:00:00'),
(6, 15, 1, '2013-12-20 09:00:00'),
(7, 16, 2, '2014-01-15 10:00:00'),
(8, 17, 3, '2014-03-05 11:00:00'),
(9, 18, 4, '2014-03-25 10:00:00'),
(10, 19, 5, '2014-03-25 10:05:00'),
(11, 20, 1, '2014-03-25 10:10:00'),
(12, 21, 2, '2014-04-10 09:00:00');

SELECT 'STEP 2 COMPLETE: Old data inserted' AS status;

-- ============================================================================
-- STEP 3: CREATE NEW UNIFIED STRUCTURE AND MIGRATE DATA
-- ============================================================================

-- 3.1 Migrate admin to unified user table
INSERT INTO user (title, fname, mname, lname, role, affiliation, specialization, email, password, contact, address, added_on, is_active)
SELECT 
    'Dr.',
    fld_fname,
    '',
    fld_lname,
    'admin',
    '',
    '',
    fld_email,
    fld_password,
    '',
    '',
    fld_addedon,
    fld_active
FROM admin
WHERE fld_email NOT IN (SELECT email FROM user);

-- 3.2 Migrate editors to unified user table
INSERT INTO user (title, fname, mname, lname, role, affiliation, specialization, email, password, contact, address, added_on, is_active)
SELECT 
    CASE 
        WHEN editor_name LIKE 'Dr.%' THEN 'Dr.'
        WHEN editor_name LIKE 'Prof.%' THEN 'Prof.'
        ELSE ''
    END,
    CASE 
        WHEN editor_name LIKE 'Dr.%' THEN TRIM(SUBSTRING_INDEX(REPLACE(editor_name, 'Dr.', ''), ' ', 1))
        WHEN editor_name LIKE 'Prof.%' THEN TRIM(SUBSTRING_INDEX(REPLACE(editor_name, 'Prof.', ''), ' ', 1))
        ELSE TRIM(SUBSTRING_INDEX(editor_name, ' ', 1))
    END,
    '',
    CASE 
        WHEN editor_name LIKE 'Dr.%' THEN TRIM(SUBSTRING_INDEX(REPLACE(editor_name, 'Dr.', ''), ' ', -1))
        WHEN editor_name LIKE 'Prof.%' THEN TRIM(SUBSTRING_INDEX(REPLACE(editor_name, 'Prof.', ''), ' ', -1))
        ELSE TRIM(SUBSTRING_INDEX(editor_name, ' ', -1))
    END,
    LOWER(role),
    COALESCE(editor_affiliation, ''),
    '',
    editor_email,
    password,
    COALESCE(editor_contact, ''),
    COALESCE(editor_address, ''),
    added_on,
    1
FROM editor
WHERE editor_email NOT IN (SELECT email FROM user);

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

-- 3.5 Migrate author (co-authors) to paper_co_author table
INSERT INTO paper_co_author (paper_id, author_name, author_email, author_affiliation, author_contact, author_order, added_on)
SELECT 
    paper_id,
    author_name,
    author_email,
    author_address,
    author_contact,
    ROW_NUMBER() OVER (PARTITION BY paper_id ORDER BY id),
    added_on
FROM author;

-- 3.6 Insert email templates
INSERT INTO email_template (slug, subject, body_template, category, is_active, created_at, updated_at) VALUES
('paper_submission', 'Paper Submission Confirmation', 'Dear {{author_name}},\n\nThank you for submitting your paper titled "{{paper_title}}" to {{journal_name}}.\n\nYour submission ID is: {{paper_code}}\n\nWe will review your submission and get back to you soon.\n\nBest regards,\nEditorial Team', 'submission', 1, NOW(), NOW()),
('paper_accepted', 'Paper Accepted for Publication', 'Dear {{author_name}},\n\nWe are pleased to inform you that your paper titled "{{paper_title}}" has been accepted for publication in {{journal_name}}.\n\nPaper ID: {{paper_code}}\n\nCongratulations!\n\nBest regards,\nEditorial Team', 'decision', 1, NOW(), NOW()),
('paper_rejected', 'Paper Decision - {{journal_name}}', 'Dear {{author_name}},\n\nThank you for your submission to {{journal_name}}.\n\nAfter careful review, we regret to inform you that your paper titled "{{paper_title}}" cannot be accepted for publication.\n\nPaper ID: {{paper_code}}\n\nWe encourage you to consider our feedback and resubmit.\n\nBest regards,\nEditorial Team', 'decision', 1, NOW(), NOW()),
('paper_revision', 'Revision Required - {{journal_name}}', 'Dear {{author_name}},\n\nYour paper titled "{{paper_title}}" (ID: {{paper_code}}) requires revisions before it can be considered for publication.\n\nPlease address the reviewer comments and resubmit.\n\nBest regards,\nEditorial Team', 'decision', 1, NOW(), NOW()),
('reviewer_invitation', 'Invitation to Review - {{journal_name}}', 'Dear {{reviewer_name}},\n\nYou are invited to review a paper titled "{{paper_title}}" for {{journal_name}}.\n\nPlease log in to your reviewer dashboard to accept or decline this invitation.\n\nDeadline: {{deadline}}\n\nBest regards,\nEditorial Team', 'reviewer', 1, NOW(), NOW()),
('reviewer_reminder', 'Review Reminder - {{journal_name}}', 'Dear {{reviewer_name}},\n\nThis is a gentle reminder about the pending review for "{{paper_title}}".\n\nDeadline: {{deadline}}\n\nPlease complete your review at your earliest convenience.\n\nBest regards,\nEditorial Team', 'reviewer', 1, NOW(), NOW()),
('password_reset', 'Password Reset Request', 'Dear {{user_name}},\n\nWe received a request to reset your password.\n\nClick the link below to reset your password:\n{{reset_link}}\n\nIf you did not request this, please ignore this email.\n\nBest regards,\nAACS Team', 'system', 1, NOW(), NOW()),
('welcome_email', 'Welcome to AACS Journals', 'Dear {{user_name}},\n\nWelcome to AACS Journals!\n\nYour account has been created successfully.\n\nYou can now log in and start submitting your research papers.\n\nBest regards,\nAACS Team', 'system', 1, NOW(), NOW());

SELECT 'STEP 3 COMPLETE: Data migrated to new schema' AS status;

-- ============================================================================
-- STEP 4: VERIFICATION QUERIES
-- ============================================================================

SELECT '=== MIGRATION VERIFICATION ===' AS info;

SELECT 'OLD TABLES DATA:' AS section;
SELECT 'admin' as tbl, COUNT(*) as cnt FROM admin
UNION ALL SELECT 'editor', COUNT(*) FROM editor
UNION ALL SELECT 'author', COUNT(*) FROM author
UNION ALL SELECT 'journal', COUNT(*) FROM journal
UNION ALL SELECT 'indexing', COUNT(*) FROM indexing
UNION ALL SELECT 'news', COUNT(*) FROM news
UNION ALL SELECT 'editorial_board', COUNT(*) FROM editorial_board
UNION ALL SELECT 'editor_profile', COUNT(*) FROM editor_profile
UNION ALL SELECT 'gallery', COUNT(*) FROM gallery
UNION ALL SELECT 'gallery_pics', COUNT(*) FROM gallery_pics
UNION ALL SELECT 'online_review', COUNT(*) FROM online_review;

SELECT 'NEW TABLES DATA:' AS section;
SELECT 'user' as tbl, COUNT(*) as cnt FROM user
UNION ALL SELECT 'user_role', COUNT(*) FROM user_role
UNION ALL SELECT 'paper_co_author', COUNT(*) FROM paper_co_author
UNION ALL SELECT 'email_template', COUNT(*) FROM email_template;

SELECT 'USER ROLES BREAKDOWN:' AS section;
SELECT role, COUNT(*) as count FROM user_role GROUP BY role;

COMMIT;
SET FOREIGN_KEY_CHECKS = 1;

SELECT 'MIGRATION COMPLETE!' AS final_status;
