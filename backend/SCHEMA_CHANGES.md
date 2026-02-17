"""
SCHEMA UPDATES DOCUMENTATION
============================

This document outlines the schema changes made to support the reviewer invitation
and assignment tracking system.

DATABASE SCHEMA CHANGES:
=======================

1. ONLINE_REVIEW TABLE UPDATES
   - New Field: submitted_on (DATETIME, nullable)
     Purpose: Tracks when a reviewer submitted their review
     
   - New Field: review_status (VARCHAR(50), default='pending')
     Purpose: Tracks the status of each review assignment
     Values: 'pending' | 'submitted' | 'completed'
     
   - New Index: idx_review_status (reviewer_id, review_status)
     Purpose: Optimize queries filtering by reviewer and status

   Migration Script: backend/add_review_fields.py
   Run: python add_review_fields.py (from backend directory)


2. REVIEWER_INVITATION TABLE (ALREADY CREATED)
   - id (INT, primary key)
   - paper_id (INT) - Reference to the paper being reviewed
   - reviewer_id (INT) - Reference to user.id if known
   - reviewer_email (VARCHAR 255) - Email address of invited reviewer
   - reviewer_name (VARCHAR 255) - Name of invited reviewer
   - journal_id (VARCHAR 100) - Journal identifier
   - invitation_token (VARCHAR 255, unique) - Magic link token
   - token_expiry (DATETIME) - When the invitation expires
   - status (VARCHAR 50) - pending | accepted | declined | expired
   - invited_on (DATETIME) - Timestamp of invitation
   - accepted_on (DATETIME, nullable) - When invitation was accepted
   - declined_on (DATETIME, nullable) - When invitation was declined
   - invitation_message (TEXT, nullable) - Custom message with invitation
   - decline_reason (TEXT, nullable) - Why reviewer declined

   Index: idx_invitation_token on invitation_token
   Index: idx_invitation_status on (reviewer_email, status)


DATABASE RELATIONSHIPS:
======================

Paper (1) -----> (*) OnlineReview
- A paper can have multiple reviewers assigned

OnlineReview (1) -----> (1) ReviewerInvitation
- Each review assignment can be tracked via invitations

User (1) -----> (*) OnlineReview
- A reviewer can have multiple assignments

User (1) -----> (*) ReviewerInvitation
- A reviewer can have multiple pending invitations


API COMPATIBILITY NOTES:
=======================

All existing APIs remain unchanged. The new schema fields are:
- Used internally by the backend for status tracking
- Returned in assignment responses for UI filtering
- Automatically populated when reviews are submitted

The following APIs now use the enhanced schema:
- GET /api/v1/reviewer/assignments - Returns review_status field
- GET /api/v1/reviewer/dashboard/stats - Accurately counts pending/completed
- GET /api/v1/reviewer/invitations - Uses ReviewerInvitation table


MIGRATION PATH:
==============

1. Run the migration script to add new columns:
   cd backend
   python add_review_fields.py

2. The system will default all existing online_review entries to 'pending' status

3. When reviewers submit reviews, the review_status and submitted_on will be updated

4. No changes needed to APIs - they automatically use the new fields


FUTURE ENHANCEMENTS:
====================

These fields enable the following future features:
- Review deadline tracking and notifications
- Review completion analytics
- Average review time calculations
- SLA monitoring for reviewers
- Reviewer performance metrics
"""
