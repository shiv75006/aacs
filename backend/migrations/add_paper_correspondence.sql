-- Migration: Add paper_correspondence table for email tracking
-- Date: 2026-02-18
-- Description: Creates table to store all email correspondence related to paper lifecycle

CREATE TABLE IF NOT EXISTS paper_correspondence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT NOT NULL,
    
    -- Recipient info (author only)
    recipient_email VARCHAR(255) NOT NULL,
    recipient_name VARCHAR(255),
    
    -- Email content
    subject VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    
    -- Email metadata
    email_type VARCHAR(50) NOT NULL COMMENT 'submission_confirmed, under_review, revision_requested, accepted, rejected, published, resubmitted',
    status_at_send VARCHAR(50) COMMENT 'Paper status when email was sent',
    
    -- Delivery tracking
    delivery_status VARCHAR(50) NOT NULL DEFAULT 'pending' COMMENT 'pending, sent, delivered, failed, bounced',
    webhook_id VARCHAR(100) UNIQUE COMMENT 'For delivery webhook tracking',
    webhook_received_at DATETIME,
    error_message TEXT,
    retry_count INT NOT NULL DEFAULT 0,
    
    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME,
    
    -- Foreign key constraint
    CONSTRAINT fk_correspondence_paper FOREIGN KEY (paper_id) 
        REFERENCES paper(id) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_correspondence_paper_id (paper_id),
    INDEX idx_correspondence_webhook_id (webhook_id),
    INDEX idx_correspondence_delivery_status (delivery_status),
    INDEX idx_correspondence_email_type (email_type),
    INDEX idx_correspondence_created_at (created_at)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add comment to table
ALTER TABLE paper_correspondence COMMENT = 'Stores all email correspondence for paper lifecycle tracking';
