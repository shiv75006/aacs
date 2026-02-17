/**
 * Paper Normalizer - Converts backend field names to standard frontend format
 * Handles field inconsistencies across different API endpoints
 */

export const paperNormalizer = {
  /**
   * Normalize paper object from backend response
   * Maps different field names to standard format
   */
  normalizePaper: (rawData) => {
    if (!rawData) return null;

    // Handle journal - can be string, object, or nested
    let journalId = rawData.journal_id;
    let journalName = rawData.journal_name || 'Unknown Journal';
    if (rawData.journal) {
      if (typeof rawData.journal === 'object') {
        journalId = journalId || rawData.journal.id;
        journalName = rawData.journal.name || journalName;
      } else {
        journalName = rawData.journal;
      }
    }

    // Handle author - can be string, object, or nested
    let authorId = rawData.author_id || rawData.added_by;
    let authorName = rawData.author_name || '';
    let authorEmail = rawData.author_email || '';
    let authorAffiliation = '';
    if (rawData.author) {
      if (typeof rawData.author === 'object') {
        authorId = authorId || rawData.author.id;
        authorName = rawData.author.name || authorName;
        authorEmail = rawData.author.email || authorEmail;
        authorAffiliation = rawData.author.affiliation || '';
      } else {
        authorName = rawData.author;
      }
    }

    // Handle co-authors - can be array of strings or array of objects
    let coAuthors = [];
    if (Array.isArray(rawData.co_authors)) {
      coAuthors = rawData.co_authors.map(ca => {
        if (typeof ca === 'object') {
          return `${ca.first_name || ''} ${ca.middle_name || ''} ${ca.last_name || ''}`.trim() || ca.email || 'Unknown';
        }
        return ca;
      });
    } else if (typeof rawData.co_authors === 'string') {
      coAuthors = rawData.co_authors.split(',').filter(a => a.trim());
    }

    return {
      id: rawData.id || rawData.paper_id,
      title: rawData.title || rawData.name || 'Untitled',
      abstract: rawData.abstract || '',
      keywords: Array.isArray(rawData.keywords)
        ? rawData.keywords
        : (rawData.keywords || '').split(',').filter(k => k.trim()),
      paperCode: rawData.code || rawData.paper_code || '',
      journal: {
        id: journalId,
        name: journalName
      },
      author: {
        id: authorId,
        name: authorName,
        email: authorEmail,
        affiliation: authorAffiliation
      },
      coAuthors: coAuthors,
      status: rawData.status || 'unknown',
      submittedDate: rawData.submitted_date || rawData.added_on || new Date().toISOString(),
      filePath: rawData.file_path || rawData.file || '',
      fileName: rawData.file_name || extractFileName(rawData.file_path || rawData.file || ''),
      fileSize: rawData.file_size,
      volume: rawData.volume,
      issue: rawData.issue,
      pageNumber: rawData.page_number || rawData.page,
      
      // Review-related fields (from OnlineReview model)
      reviews: rawData.reviews ? rawData.reviews.map(r => paperNormalizer.normalizeReview(r)) : [],
      
      // Assigned reviewers with full details
      assignedReviewers: rawData.assigned_reviewers || [],
      reviewStatus: rawData.review_status || 'not_assigned',
      totalReviewers: rawData.total_reviewers || 0,
      completedReviews: rawData.completed_reviews || 0,
      
      // Decision-related fields
      decision: rawData.decision ? paperNormalizer.normalizeDecision(rawData.decision) : null,
      
      // Additional metadata
      mailStatus: rawData.mail_status || rawData.mailstatus,
      createdAt: rawData.created_at,
      updatedAt: rawData.updated_at,
      
      // Version info
      versionNumber: rawData.version_number,
      revisionCount: rawData.revision_count,
      revisionDeadline: rawData.revision_deadline,
      revisionNotes: rawData.revision_notes,
      researchArea: rawData.research_area,
      messageToEditor: rawData.message_to_editor,
      
      // Original data for fallback
      _raw: rawData
    };
  },

  /**
   * Normalize review object from backend response
   */
  normalizeReview: (rawData) => {
    if (!rawData) return null;

    // Parse rating if it's stored as JSON string
    let ratings = {};
    if (typeof rawData.rating === 'string') {
      try {
        ratings = JSON.parse(rawData.rating);
      } catch (e) {
        ratings = {};
      }
    } else if (typeof rawData.rating === 'object') {
      ratings = rawData.rating;
    }

    return {
      id: rawData.id || rawData.review_id,
      paperId: rawData.paper_id,
      reviewerId: rawData.reviewer_id,
      reviewerName: rawData.reviewer_name || rawData.reviewer,
      reviewerEmail: rawData.reviewer_email,
      status: rawData.status || rawData.review_status || 'pending',
      technicalQuality: ratings.technical_quality || rawData.technical_quality || 0,
      clarity: ratings.clarity || rawData.clarity || 0,
      originality: ratings.originality || rawData.originality || 0,
      significance: ratings.significance || rawData.significance || 0,
      overallRating: ratings.overall_rating || rawData.overall_rating || rawData.rating || 0,
      recommendation: rawData.recommendation || '',
      authorComments: rawData.author_comments || rawData.comments || '',
      confidentialComments: rawData.confidential_comments || '',
      reviewComment: rawData.review_comment || '',
      reviewReportFile: rawData.review_report_file || null,
      submittedDate: rawData.submitted_date || rawData.date_submitted || rawData.date,
      assignedDate: rawData.assigned_date || rawData.date_assigned,
      dueDate: rawData.due_date,
      priority: rawData.priority,
      
      _raw: rawData
    };
  },

  /**
   * Normalize decision object from backend response
   */
  normalizeDecision: (rawData) => {
    if (!rawData) return null;

    return {
      id: rawData.id || rawData.decision_id,
      type: rawData.type || rawData.decision_type,
      reason: rawData.reason || '',
      requestedRevisions: rawData.requested_revisions || rawData.revision_comments || '',
      revisionType: rawData.revision_type, // 'minor' or 'major'
      decisionDate: rawData.decision_date || rawData.created_at,
      editorName: rawData.editor_name || rawData.editor,
      comments: rawData.comments || '',
      
      _raw: rawData
    };
  },

  /**
   * Normalize list of papers
   */
  normalizePapers: (rawArray) => {
    if (!Array.isArray(rawArray)) return [];
    return rawArray.map(p => paperNormalizer.normalizePaper(p));
  },

  /**
   * Get field mapping reference
   */
  getFieldMapping: () => ({
    id: ['id', 'paper_id'],
    title: ['title', 'name'],
    code: ['code', 'paper_code'],
    journal: ['journal', 'journal_name', 'journal_id'],
    author: ['author', 'author_name', 'author_id', 'added_by'],
    authorEmail: ['author_email', 'email'],
    abstract: ['abstract', 'abstract_text'],
    keywords: ['keywords', 'keyword'],
    filePath: ['file_path', 'file'],
    fileName: ['file_name'],
    status: ['status', 'paper_status'],
    submittedDate: ['submitted_date', 'added_on', 'created_at'],
    updatedDate: ['updated_date', 'updated_at', 'modified_on'],
    coAuthors: ['co_authors', 'coauthors', 'coauth'],
    volume: ['volume', 'vol'],
    issue: ['issue', 'issue_no'],
    pageNumber: ['page_number', 'page', 'page_no'],
    mailStatus: ['mail_status', 'mailstatus'],
    rating: ['rating', 'overall_rating'],
    recommendation: ['recommendation', 'reviewer_recommendation'],
    dueDate: ['due_date', 'due_on'],
    priority: ['priority', 'review_priority']
  })
};

/**
 * Helper function to extract filename from path
 */
function extractFileName(filePath) {
  if (!filePath) return 'document';
  return filePath.split('/').pop() || 'document';
}

export default paperNormalizer;
