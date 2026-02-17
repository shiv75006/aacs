import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import acsApi from '../api/apiService.js';
import './EditorDecisionPanel.css';

const DECISIONS = [
  { value: 'accepted', label: 'Accept', color: 'success', icon: '✓' },
  { value: 'correction', label: 'Request Revisions', color: 'warning', icon: '⟳' },
  { value: 'rejected', label: 'Reject', color: 'danger', icon: '✗' }
];

const REVISION_TYPES = [
  { value: 'minor', label: 'Minor Revisions' },
  { value: 'major', label: 'Major Revisions' }
];

export default function EditorDecisionPanel() {
  const { paperId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const [paperDetails, setPaperDetails] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [statistics, setStatistics] = useState(null);

  const [selectedDecision, setSelectedDecision] = useState(null);
  const [revisionType, setRevisionType] = useState('minor');
  const [editorComments, setEditorComments] = useState('');
  const [validationErrors, setValidationErrors] = useState({});

  const [expandedReview, setExpandedReview] = useState(null);

  useEffect(() => {
    loadPaperReviews();
  }, [paperId]);

  const loadPaperReviews = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await acsApi.editor.getPaperReviews(paperId);
      setPaperDetails({
        paper_id: response.paper_id,
        paper_name: response.paper_name,
        author: response.author,
        abstract: response.abstract,
        keywords: response.keywords,
        status: response.status,
        submitted_date: response.submitted_date
      });
      setReviews(response.reviews);
      setStatistics(response.statistics);
    } catch (err) {
      setError(
        err.response?.status === 404
          ? 'Paper or reviews not found'
          : err.message || 'Failed to load paper reviews'
      );
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!selectedDecision) {
      errors.decision = 'Please select a decision';
    }

    if (!editorComments.trim()) {
      errors.editorComments = 'Editor comments are required';
    } else if (editorComments.length < 50) {
      errors.editorComments = 'Comments must be at least 50 characters';
    } else if (editorComments.length > 2000) {
      errors.editorComments = 'Comments must not exceed 2000 characters';
    }

    if (selectedDecision === 'correction' && !revisionType) {
      errors.revisionType = 'Please specify revision type';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmitDecision = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const decisionPayload = {
        decision: selectedDecision,
        editor_comments: editorComments.trim()
      };

      if (selectedDecision === 'correction') {
        decisionPayload.revision_type = revisionType;
      }

      const response = await acsApi.editor.makePaperDecision(paperId, decisionPayload);

      setSuccess(true);
      setSuccessMessage(`Decision recorded: ${response.decision.toUpperCase()}`);
      
      setTimeout(() => {
        navigate('/editor-dashboard');
      }, 2000);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Failed to record decision'
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="editor-decision-panel">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading paper reviews...</p>
        </div>
      </div>
    );
  }

  if (error && !success) {
    return (
      <div className="editor-decision-panel">
        <div className="error-state">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadPaperReviews} className="retry-btn">
            Retry
          </button>
          <button onClick={() => navigate('/editor-dashboard')} className="back-btn">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="editor-decision-panel">
        <div className="success-state">
          <div className="success-icon">✓</div>
          <h2>Decision Recorded</h2>
          <p>{successMessage}</p>
          <p className="redirect-msg">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="editor-decision-panel">
      <div className="panel-header">
        <h1>Editorial Decision Panel</h1>
        <button onClick={() => navigate('/editor-dashboard')} className="close-btn">
          ← Back
        </button>
      </div>

      {/* Paper Details */}
      <div className="paper-section">
        <div className="paper-header">
          <h2>{paperDetails?.paper_name}</h2>
          <p className="author">by {paperDetails?.author}</p>
          <p className="meta">
            Submitted: {paperDetails?.submitted_date ? new Date(paperDetails.submitted_date).toLocaleDateString() : 'Unknown'}
            {' | '}
            Status: <span className={`status-badge ${paperDetails?.status}`}>{paperDetails?.status}</span>
          </p>
        </div>
        <div className="paper-body">
          <p className="abstract">
            <strong>Abstract:</strong> {paperDetails?.abstract}
          </p>
          {paperDetails?.keywords && (
            <p className="keywords">
              <strong>Keywords:</strong> {paperDetails.keywords}
            </p>
          )}
        </div>
      </div>

      {/* Review Statistics */}
      {statistics && (
        <div className="statistics-section">
          <h3>Review Summary</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{statistics.total_reviews}</div>
              <div className="stat-label">Total Reviews</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{statistics.average_rating.toFixed(1)}</div>
              <div className="stat-label">Avg Rating</div>
            </div>
            <div className="stat-card">
              <div className="stat-value accent-success">{statistics.accept_count}</div>
              <div className="stat-label">Accept</div>
            </div>
            <div className="stat-card">
              <div className="stat-value accent-warning">{statistics.minor_revisions_count}</div>
              <div className="stat-label">Minor Revisions</div>
            </div>
            <div className="stat-card">
              <div className="stat-value accent-orange">{statistics.major_revisions_count}</div>
              <div className="stat-label">Major Revisions</div>
            </div>
            <div className="stat-card">
              <div className="stat-value accent-danger">{statistics.reject_count}</div>
              <div className="stat-label">Reject</div>
            </div>
          </div>
        </div>
      )}

      {/* Reviews List */}
      {reviews.length > 0 && (
        <div className="reviews-section">
          <h3>Reviewer Feedback</h3>
          <div className="reviews-container">
            {reviews.map((review, index) => (
              <div key={review.review_id} className="review-card">
                <div
                  className="review-header"
                  onClick={() => setExpandedReview(expandedReview === index ? null : index)}
                >
                  <div className="review-meta">
                    <span className="reviewer-name">{review.reviewer_name || review.reviewer_email}</span>
                    <span className="rating-badge">Rating: {review.rating}/5</span>
                    <span className={`recommendation ${review.recommendation}`}>
                      {review.recommendation?.replace(/_/g, ' ').toUpperCase()}
                    </span>
                  </div>
                  <button className="expand-btn">
                    {expandedReview === index ? '−' : '+'}
                  </button>
                </div>

                {expandedReview === index && (
                  <div className="review-body">
                    <div className="comments">
                      <strong>Reviewer Comments:</strong>
                      <p>{review.author_comments || 'No comments provided'}</p>
                    </div>
                    <div className="submitted-info">
                      Submitted: {new Date(review.submitted_date).toLocaleDateString()}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Decision Section */}
      <div className="decision-section">
        <h3>Make Editorial Decision</h3>

        {error && <div className="error-message">{error}</div>}

        {/* Decision Selection */}
        <div className="decision-buttons">
          {DECISIONS.map(decision => (
            <button
              key={decision.value}
              className={`decision-btn ${decision.color} ${selectedDecision === decision.value ? 'selected' : ''}`}
              onClick={() => {
                setSelectedDecision(decision.value);
                setValidationErrors(prev => ({ ...prev, decision: null }));
              }}
              disabled={submitting}
            >
              <span className="icon">{decision.icon}</span>
              <span className="label">{decision.label}</span>
            </button>
          ))}
        </div>

        {validationErrors.decision && (
          <div className="validation-error">{validationErrors.decision}</div>
        )}

        {/* Revision Type (if revision requested) */}
        {selectedDecision === 'revision_requested' && (
          <div className="revision-type-section">
            <label>Revision Type:</label>
            <div className="revision-options">
              {REVISION_TYPES.map(type => (
                <label key={type.value} className="radio-label">
                  <input
                    type="radio"
                    name="revision_type"
                    value={type.value}
                    checked={revisionType === type.value}
                    onChange={(e) => setRevisionType(e.target.value)}
                    disabled={submitting}
                  />
                  <span>{type.label}</span>
                </label>
              ))}
            </div>
            {validationErrors.revisionType && (
              <div className="validation-error">{validationErrors.revisionType}</div>
            )}
          </div>
        )}

        {/* Editor Comments */}
        <div className="comments-section">
          <label htmlFor="editor-comments">
            Editor Comments
            <span className="required">*</span>
            <span className="hint">(Minimum 50 characters)</span>
          </label>
          {validationErrors.editorComments && (
            <span className="validation-error">{validationErrors.editorComments}</span>
          )}
          <textarea
            id="editor-comments"
            value={editorComments}
            onChange={(e) => {
              setEditorComments(e.target.value);
              setValidationErrors(prev => ({ ...prev, editorComments: null }));
            }}
            placeholder="Provide detailed reasons for this decision. Include specific feedback based on the reviewer comments."
            rows="6"
            disabled={submitting}
          />
          <div className="char-count">
            {editorComments.length} / 2000 characters
          </div>
        </div>

        {/* Action Buttons */}
        <div className="action-buttons">
          <button
            className="btn-submit"
            onClick={handleSubmitDecision}
            disabled={submitting || !selectedDecision}
          >
            {submitting ? 'Recording Decision...' : 'Record Decision'}
          </button>
          <button
            className="btn-cancel"
            onClick={() => navigate('/editor-dashboard')}
            disabled={submitting}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
