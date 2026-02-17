"""
COMPLETE SCHEMA REFERENCE
=========================

This document provides a complete reference of the database schema
relevant to the reviewer assignment and invitation system.
"""

# ==============================================================================
# TABLE: online_review
# ==============================================================================
# Purpose: Tracks assignments of papers to reviewers for peer review
# Engine: InnoDB
# 
# Columns:
# --------
# id (INT, PK)
#   - Primary key, auto-incrementing
#   - Unique identifier for each assignment
#
# paper_id (INT, nullable)
#   - Foreign key reference to paper.id
#   - The paper being reviewed
#
# reviewer_id (VARCHAR 100, nullable)
#   - Foreign key reference to user.id (as string)
#   - The reviewer assigned to this paper
#
# assigned_on (DATE, nullable)
#   - Date when the reviewer was assigned
#   - Used to calculate due dates (typically 14 days)
#
# submitted_on (DATETIME, nullable) [NEW]
#   - DateTime when the reviewer submitted their review
#   - NULL if review not yet submitted
#   - Set to CURRENT_TIMESTAMP when review is submitted
#
# review_status (VARCHAR 50, NOT NULL, default='pending') [NEW]
#   - Current status of the review process
#   - Values: 'pending' | 'submitted' | 'completed'
#   - Defaults to 'pending' when assignment created
#   - Updated to 'submitted' when review is submitted
#   - Updated to 'completed' when editor has processed review
#
# Indexes:
# --------
# PRIMARY KEY (id)
# idx_review_status (reviewer_id, review_status) [NEW]
#   - Optimizes filtering by reviewer and status
#   - Supports dashboard queries for pending/completed counts

# ==============================================================================
# TABLE: reviewer_invitation
# ==============================================================================
# Purpose: Tracks invitation lifecycle for external/new reviewers
# Engine: InnoDB
# 
# Columns:
# --------
# id (INT, PK)
#   - Primary key, auto-incrementing
#
# paper_id (INT, NOT NULL)
#   - Reference to paper.id
#   - The paper reviewer is being invited to review
#
# reviewer_id (INT, nullable)
#   - Reference to user.id (if reviewer is registered)
#   - NULL if reviewer hasn't created account yet
#   - Populated when invitation is accepted
#
# reviewer_email (VARCHAR 255, NOT NULL)
#   - Email address of the invited reviewer
#   - Used for sending invitation emails
#
# reviewer_name (VARCHAR 255, nullable)
#   - Name of the reviewer
#   - Displayed in invitation emails
#
# journal_id (VARCHAR 100, nullable)
#   - Reference to journal.fld_id
#   - Journal to which paper was submitted
#
# invitation_token (VARCHAR 255, NOT NULL, UNIQUE)
#   - Secure random token for magic link
#   - Used to accept invitation without login
#   - Expires after token_expiry date
#
# token_expiry (DATETIME, NOT NULL)
#   - When the invitation token expires
#   - Typically 14-30 days from invited_on
#
# status (VARCHAR 50, default='pending')
#   - Status of the invitation
#   - Values: 'pending' | 'accepted' | 'declined' | 'expired'
#   - 'pending': Invitation sent, awaiting response
#   - 'accepted': Reviewer accepted, now in online_review table
#   - 'declined': Reviewer declined the invitation
#   - 'expired': Token expired without response
#
# invited_on (DATETIME, default=CURRENT_TIMESTAMP)
#   - DateTime when invitation was sent
#
# accepted_on (DATETIME, nullable)
#   - DateTime when reviewer accepted invitation
#   - NULL if not yet accepted
#   - Set when status changes to 'accepted'
#
# declined_on (DATETIME, nullable)
#   - DateTime when reviewer declined invitation
#   - NULL if not declined
#   - Set when status changes to 'declined'
#
# invitation_message (TEXT, nullable)
#   - Custom message included with invitation
#   - From the editor/journal
#
# decline_reason (TEXT, nullable)
#   - Reason provided by reviewer for declining
#   - Only populated if status = 'declined'
#
# Indexes:
# --------
# PRIMARY KEY (id)
# UNIQUE (invitation_token) - Ensures token uniqueness
# idx_invitation_token (invitation_token) - Fast token lookups
# idx_invitation_status (reviewer_email, status) - Query by email & status

# ==============================================================================
# TABLE: paper
# ==============================================================================
# Existing table - schema not changed
#
# Columns relevant to review system:
# -----------------------------------
# id (INT, PK)
#   - Paper identifier
#
# title (VARCHAR 500)
#   - Paper title, displayed in invitations and dashboard
#
# abstract (VARCHAR 1500)
#   - Paper abstract
#
# journal (VARCHAR 12)
#   - Journal code
#
# added_by (VARCHAR 100)
#   - User ID of paper author
#
# status (VARCHAR 50, default='submitted')
#   - Paper submission status
#   - Values: 'submitted' | 'under_review' | 'accepted' | 'rejected' etc.
#
# added_on (DATETIME)
#   - When paper was submitted

# ==============================================================================
# TABLE: user
# ==============================================================================
# Existing table - schema not changed
#
# Columns relevant to review system:
# -----------------------------------
# id (INT, PK)
#   - User identifier
#   - Referenced by reviewer_id in online_review
#
# email (VARCHAR 255, UNIQUE)
#   - User email address
#   - Used to match with invitations
#
# role (VARCHAR 50)
#   - User role: 'Author' | 'Reviewer' | 'Editor' | 'Admin'
#
# fname, lname, mname (VARCHAR 100)
#   - Reviewer name fields
#
# specialization (TEXT)
#   - Reviewer expertise areas
#
# contact (VARCHAR 20)
#   - Contact phone number
#
# affiliation (VARCHAR 255)
#   - Reviewer's institutional affiliation

# ==============================================================================
# TABLE: paper_comment
# ==============================================================================
# Existing table - used to store actual review content
#
# Columns:
# --------
# id (INT, PK)
#
# paper_id (VARCHAR 50)
#   - Reference to paper being reviewed
#
# reviewed_by (VARCHAR 50)
#   - User ID of reviewer
#   - Links to user.id
#
# reviewed_on (DATE)
#   - Date review was submitted
#   - Used with online_review.submitted_on for tracking
#
# comment (TEXT)
#   - Reviewer's comments on the paper
#
# editor_comment (TEXT)
#   - Editor's response to review
#
# correction (VARCHAR 100)
#   - Correction status: 'correct' | 'notcorrect' etc.
#
# attachment (VARCHAR 200)
#   - File attachment with review
#
# showattachment (VARCHAR 200)
#   - Whether attachment is visible to author

# ==============================================================================
# KEY RELATIONSHIPS
# ==============================================================================
#
# Invitation Flow:
# 1. Editor sends invitation -> reviewer_invitation entry created
# 2. Reviewer opens magic link with token
# 3. Reviewer accepts -> Status changed to 'accepted', reviewer_id populated
# 4. OnlineReview record created automatically (from editor.py)
# 5. Reviewer submits review -> online_review.review_status = 'submitted'
# 6. Editor reviews -> paper_comment entry created
#
# Query Examples:
# ---------------
#
# Get all pending reviews for a reviewer:
# SELECT * FROM online_review 
# WHERE reviewer_id = '123' AND review_status = 'pending'
#
# Get invitation expiry status:
# SELECT * FROM reviewer_invitation 
# WHERE reviewer_email = 'test@example.com' 
# AND status = 'pending' AND token_expiry < NOW()
# (These should have status updated to 'expired')
#
# Get reviewer's submitted reviews:
# SELECT * FROM online_review o
# JOIN paper_comment pc ON o.paper_id = pc.paper_id 
# WHERE o.reviewer_id = '123' AND o.review_status = 'submitted'
#
# Get papers awaiting reviewer assignment:
# SELECT p.* FROM paper p
# WHERE p.status = 'under_review' 
# AND p.id NOT IN (SELECT paper_id FROM online_review)

# ==============================================================================
# FUTURE ENHANCEMENTS
# ==============================================================================
#
# Potential schema additions:
#
# 1. online_review: 
#    - due_date (DATETIME) - Explicit due date instead of calculating
#    - priority (INT 1-5) - Review priority level
#    - comments_to_reviewer (TEXT) - Private notes for reviewer
#    - rating (INT 1-5) - Editor's rating of review quality
#
# 2. reviewer_invitation:
#    - reminder_sent_count (INT) - Number of reminders sent
#    - last_reminder_sent (DATETIME) - Last reminder timestamp
#    - acceptance_deadline (DATETIME) - Must accept by this date
#
# 3. New table: review_milestone
#    - track key milestones: sent, viewed, accepted, started, submitted, etc.
#
# 4. New table: reviewer_preference
#    - reviewer specializations/preferences per journal
#    - availability status
#    - notification preferences
"""
