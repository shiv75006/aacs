import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useRole } from '../../hooks/useRole';
import { useToast } from '../../hooks/useToast';
import { useModal } from '../../hooks/useModal';
import acsApi from '../../api/apiService';
import paperNormalizer from '../../services/paperNormalizer';
import FileViewer from '../../components/FileViewer/FileViewer';
import StatusChips from '../../components/StatusChips/StatusChips';
import ContactEditorialModal from '../../components/ContactEditorialModal';
import AuthorContactModal from '../../components/AuthorContactModal';
import styles from './PaperDetailsPage.module.css';

const PaperDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAdmin, isEditor, isAuthor, isReviewer } = useRole();
  const { success, error: showError, info } = useToast();
  const { confirm } = useModal();

  const [paper, setPaper] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedReviewId, setExpandedReviewId] = useState(null);
  const [showAssignReviewer, setShowAssignReviewer] = useState(false);
  const [reviewerEmail, setReviewerEmail] = useState('');
  const [dueDays, setDueDays] = useState(14);
  const [assigningReviewer, setAssigningReviewer] = useState(false);
  const [availableReviewers, setAvailableReviewers] = useState([]);
  const [searchReviewers, setSearchReviewers] = useState('');
  const [filteredReviewers, setFilteredReviewers] = useState([]);
  const [loadingReviewers, setLoadingReviewers] = useState(false);
  const [showReviewerDropdown, setShowReviewerDropdown] = useState(false);
  // Author resubmission state
  const [showResubmitForm, setShowResubmitForm] = useState(false);
  const [resubmitFile, setResubmitFile] = useState(null);
  const [revisionReason, setRevisionReason] = useState('');
  const [changeSummary, setChangeSummary] = useState('');
  const [resubmitting, setResubmitting] = useState(false);
  // Correspondence history
  const [correspondence, setCorrespondence] = useState([]);
  const [loadingCorrespondence, setLoadingCorrespondence] = useState(false);
  const [showCorrespondence, setShowCorrespondence] = useState(false);
  // Contact Editorial Modal (for admin/editor)
  const [showContactModal, setShowContactModal] = useState(false);
  // Author Contact Modal (for author to contact editorial)
  const [showAuthorContactModal, setShowAuthorContactModal] = useState(false);
  // Revision history
  const [revisionHistory, setRevisionHistory] = useState([]);
  const [loadingRevisions, setLoadingRevisions] = useState(false);
  const [showRevisions, setShowRevisions] = useState(false);

  useEffect(() => {
    fetchPaperDetails();
  }, [id]);

  useEffect(() => {
    // Filter reviewers when search term changes
    if (searchReviewers.trim()) {
      const filtered = availableReviewers.filter(reviewer =>
        reviewer.name.toLowerCase().includes(searchReviewers.toLowerCase()) ||
        reviewer.email.toLowerCase().includes(searchReviewers.toLowerCase())
      );
      setFilteredReviewers(filtered);
    } else {
      setFilteredReviewers(availableReviewers);
    }
  }, [searchReviewers, availableReviewers]);

  const fetchAvailableReviewers = async () => {
    try {
      setLoadingReviewers(true);
      // Use appropriate API based on role
      const response = isAdmin() 
        ? await acsApi.admin.listReviewers(0, 100)
        : await acsApi.editor.listReviewers(0, 100);
      setAvailableReviewers(response.reviewers || []);
      setFilteredReviewers(response.reviewers || []);
    } catch (err) {
      console.error('Failed to fetch reviewers:', err);
      showError('Failed to load available reviewers', 3000);
    } finally {
      setLoadingReviewers(false);
    }
  };

  // Fetch correspondence history for author
  const fetchCorrespondence = async () => {
    if (!paper?.id) return;
    try {
      setLoadingCorrespondence(true);
      let response;
      if (isAuthor()) {
        response = await acsApi.author.getCorrespondence(paper.id);
      } else if (isAdmin() || isEditor()) {
        response = await acsApi.admin.getPaperCorrespondence(paper.id);
      }
      setCorrespondence(response?.correspondence || []);
    } catch (err) {
      console.error('Failed to fetch correspondence:', err);
      // Don't show error toast, just log it
    } finally {
      setLoadingCorrespondence(false);
    }
  };

  // Handle contact modal close
  const handleContactModalClose = (sent) => {
    setShowContactModal(false);
    if (sent) {
      success('Correspondence sent successfully');
      // Refresh correspondence list if it's visible
      if (showCorrespondence) {
        fetchCorrespondence();
      }
    }
  };

  // Fetch revision history for author
  const fetchRevisionHistory = async () => {
    if (!paper?.id || !isAuthor()) return;
    try {
      setLoadingRevisions(true);
      const response = await acsApi.author.getRevisionHistory(paper.id);
      setRevisionHistory(response.revisions || []);
    } catch (err) {
      console.error('Failed to fetch revision history:', err);
    } finally {
      setLoadingRevisions(false);
    }
  };

  // Handle paper resubmission
  const handleResubmit = async () => {
    if (!resubmitFile) {
      showError('Please select a revised paper file', 3000);
      return;
    }
    if (!revisionReason.trim()) {
      showError('Please provide a reason/summary for your revisions', 3000);
      return;
    }

    try {
      setResubmitting(true);
      await acsApi.author.resubmitPaper(paper.id, resubmitFile, revisionReason, changeSummary);
      success('Paper resubmitted successfully!', 4000);
      setShowResubmitForm(false);
      setResubmitFile(null);
      setRevisionReason('');
      setChangeSummary('');
      // Refresh paper details
      await fetchPaperDetails();
    } catch (err) {
      console.error('Error resubmitting paper:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to resubmit paper';
      showError(errorMsg, 5000);
    } finally {
      setResubmitting(false);
    }
  };

  const fetchPaperDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch based on user role
      let response;
      if (isEditor()) {
        response = await acsApi.editor.getPaperDetail(id);
      } else if (isAuthor()) {
        response = await acsApi.author.getSubmissionDetail(id);
      } else if (isReviewer()) {
        response = await acsApi.reviewer.getAssignmentDetail(id);
      } else if (isAdmin()) {
        response = await acsApi.admin.getPaperDetail(id);
      }

      // Normalize the paper data
      const normalized = paperNormalizer.normalizePaper(response);
      setPaper(normalized);
    } catch (err) {
      console.error('Error fetching paper details:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load paper details';
      setError(errorMsg);
      showError(errorMsg, 5000);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignReviewer = async () => {
    if (!reviewerEmail.trim()) {
      showError('Please select or enter a reviewer email', 3000);
      return;
    }

    try {
      setAssigningReviewer(true);
      // Use appropriate API based on role
      if (isAdmin()) {
        await acsApi.admin.inviteReviewer(paper.id, reviewerEmail, dueDays);
      } else {
        await acsApi.editor.inviteReviewer(paper.id, reviewerEmail, dueDays);
      }
      success(`Reviewer invitation sent to ${reviewerEmail}`, 4000);
      setReviewerEmail('');
      setSearchReviewers('');
      setDueDays(14);
      setShowAssignReviewer(false);
      setShowReviewerDropdown(false);
      // Refresh paper details
      await fetchPaperDetails();
    } catch (err) {
      console.error('Error assigning reviewer:', err);
      
      // Extract detailed error message
      let errorMsg = 'Failed to assign reviewer';
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'object') {
          errorMsg = detail.message || detail.error || errorMsg;
          if (detail.fix) {
            errorMsg += ` - ${detail.fix}`;
          }
        } else {
          errorMsg = detail;
        }
      }
      showError(errorMsg, 5000);
    } finally {
      setAssigningReviewer(false);
    }
  };

  const handleSelectReviewer = (reviewer) => {
    setReviewerEmail(reviewer.email);
    setSearchReviewers(reviewer.name);
    setShowReviewerDropdown(false);
  };

  const handleViewPaper = () => {
    if (paper?.id) {
      // Get token for authentication (stored as 'authToken' in localStorage)
      const token = localStorage.getItem('authToken');
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // Use different endpoint based on role
      let viewUrl;
      if (isAdmin()) {
        viewUrl = `${baseUrl}/api/v1/admin/papers/${paper.id}/view`;
      } else if (isEditor()) {
        viewUrl = `${baseUrl}/api/v1/editor/papers/${paper.id}/view`;
      } else {
        viewUrl = `${baseUrl}/api/v1/author/submissions/${paper.id}/view`;
      }
      
      // Open with token in URL for authentication
      window.open(`${viewUrl}?token=${token}`, '_blank');
      info('Opening file in new tab...', 2000);
    }
  };

  const handleViewReviewReport = (reviewId, e) => {
    e.stopPropagation(); // Prevent expanding/collapsing the review card
    if (paper?.id) {
      const token = localStorage.getItem('authToken');
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const viewUrl = `${baseUrl}/api/v1/author/submissions/${paper.id}/reviews/${reviewId}/view-report`;
      window.open(`${viewUrl}?token=${token}`, '_blank');
      info('Opening review report in new tab...', 2000);
    }
  };

  const handleDownloadReviewReport = async (reviewId, e) => {
    e.stopPropagation(); // Prevent expanding/collapsing the review card
    try {
      info('Downloading review report...', 2000);
      const response = await acsApi.author.downloadReviewReport(paper.id, reviewId);
      
      // Create blob from response data
      const contentType = response.headers['content-type'] || 'application/octet-stream';
      const blob = new Blob([response.data], { type: contentType });
      const url = window.URL.createObjectURL(blob);
      
      // Get filename from content-disposition header or determine from content-type
      const contentDisposition = response.headers['content-disposition'];
      let filename = `review_report_${reviewId}`;
      
      // Try to get filename from content-disposition header
      if (contentDisposition) {
        // Try filename*=UTF-8'' format first
        const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;\s]+)/i);
        if (utf8Match) {
          filename = decodeURIComponent(utf8Match[1]);
        } else {
          // Try filename="..." or filename=... format
          const filenameMatch = contentDisposition.match(/filename="?([^"\n;]+)"?/i);
          if (filenameMatch) {
            filename = filenameMatch[1].trim();
          }
        }
      } else {
        // Fallback: determine extension from content-type
        const extMap = {
          'application/pdf': '.pdf',
          'application/msword': '.doc',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
        };
        const ext = extMap[contentType] || '';
        filename = `review_report_${reviewId}${ext}`;
      }
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      success('Review report downloaded', 2000);
    } catch (err) {
      console.error('Error downloading review report:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to download review report';
      showError(errorMsg, 3000);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <span className="material-symbols-rounded">hourglass_empty</span>
          <p>Loading paper details...</p>
        </div>
      </div>
    );
  }

  if (error || !paper) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <span className="material-symbols-rounded">error</span>
          <p>{error || 'Paper not found'}</p>
          <button className={styles.backBtn} onClick={() => navigate(-1)}>
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Format date helper
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatDateTime = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', { 
      month: 'short', day: 'numeric', year: 'numeric',
      hour: 'numeric', minute: '2-digit', hour12: true 
    });
  };

  // Get initials for avatar
  const getInitials = (name) => {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <div className={styles.container}>
      {/* Sticky Header */}
      <header className={styles.pageHeader}>
        <div className={styles.headerContent}>
          {/* Back Link */}
          <button className={styles.backLink} onClick={() => navigate(-1)}>
            <span className="material-symbols-rounded">arrow_back</span>
            <span>Back to Dashboard</span>
          </button>

          {/* Title Section */}
          <div className={styles.headerMain}>
            <div className={styles.headerLeft}>
              <StatusChips status={paper.status} />
              <h1 className={styles.pageTitle}>{paper.title}</h1>
            </div>
            
            {/* Action Buttons */}
            <div className={styles.headerActions}>
              <button className={styles.btnOutline} onClick={handleViewPaper}>
                <span className="material-symbols-rounded">visibility</span>
                View PDF
              </button>
              
              {isAuthor() && (paper.status === 'correction' || paper.status === 'revision_requested') && (
                <button className={styles.btnDark} onClick={() => setShowResubmitForm(!showResubmitForm)}>
                  <span className="material-symbols-rounded">edit</span>
                  Revise
                </button>
              )}
              
              {(isEditor() || isAdmin()) && (
                <button className={styles.btnDark} onClick={() => {
                  setShowAssignReviewer(true);
                  if (!availableReviewers.length) {
                    fetchAvailableReviewers();
                  }
                }}>
                  <span className="material-symbols-rounded">person_add</span>
                  Assign Reviewer
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Two Column Layout */}
      <div className={styles.pageContent}>
        {/* Left Column - Main Content */}
        <div className={styles.mainColumn}>
          {/* Meta Info Card */}
          <section className={styles.metaCard}>
            <div className={styles.metaGrid}>
              <div className={styles.metaItem}>
                <p className={styles.metaLabel}>Paper ID</p>
                <p className={styles.metaValue}>{paper.paperCode || `#${paper.id}`}</p>
              </div>
              <div className={styles.metaItem}>
                <p className={styles.metaLabel}>Journal</p>
                <p className={styles.metaValue}>{paper.journal?.name || 'IJSE 2026'}</p>
              </div>
              <div className={styles.metaItem}>
                <p className={styles.metaLabel}>Submitted</p>
                <p className={styles.metaValue}>{formatDate(paper.submittedDate)}</p>
              </div>
              <div className={styles.metaItem}>
                <p className={styles.metaLabel}>Primary Author</p>
                <p className={styles.metaValue}>{paper.author?.name || 'Unknown'}</p>
              </div>
            </div>
          </section>

          {/* Abstract Section */}
          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <span className="material-symbols-rounded">subject</span>
              <h2 className={styles.sectionTitle}>Abstract</h2>
            </div>
            <div className={styles.sectionCard}>
              <p className={styles.abstractText}>{paper.abstract || 'No abstract provided'}</p>
            </div>
          </section>

          {/* Keywords */}
          {paper.keywords && paper.keywords.length > 0 && (
            <section className={styles.section}>
              <div className={styles.sectionHeader}>
                <span className="material-symbols-rounded">label</span>
                <h2 className={styles.sectionTitle}>Keywords</h2>
              </div>
              <div className={styles.sectionCard}>
                <div className={styles.keywordsList}>
                  {paper.keywords.map((kw, idx) => (
                    <span key={idx} className={styles.keyword}>{kw}</span>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* Reviews Section */}
          {(isEditor() || isAdmin() || isAuthor()) && paper.reviews && paper.reviews.length > 0 && (
            <section className={styles.section}>
              <div className={styles.sectionHeader}>
                <span className="material-symbols-rounded">reviews</span>
                <h2 className={styles.sectionTitle}>Reviewer Feedback ({paper.reviews.length})</h2>
                {paper.status === 'revision_requested' && (
                  <span className={styles.actionBadge}>Action Required</span>
                )}
              </div>
              
              <div className={styles.reviewsCard}>
                {paper.reviews.map((review, idx) => (
                  <div key={review.id} className={styles.reviewBlock}>
                    <div className={styles.reviewContent}>
                      {/* Reviewer Header */}
                      <div className={styles.reviewerHeader}>
                        <div className={styles.reviewerInfo}>
                          <div className={styles.reviewerAvatar}>
                            {getInitials(review.reviewerName || `Reviewer ${idx + 1}`)}
                          </div>
                          <span className={styles.reviewerName}>
                            {isEditor() || isAdmin() ? review.reviewerName : `Reviewer #${idx + 1}`}
                          </span>
                        </div>
                        {review.overallRating && (
                          <div className={styles.overallRating}>
                            <span className="material-symbols-rounded">star</span>
                            <span>{review.overallRating.toFixed(1)} / 5.0</span>
                          </div>
                        )}
                      </div>

                      {/* Rating Bars */}
                      {(review.technicalQuality || review.clarity || review.originality || review.significance) && (
                        <div className={styles.ratingsGrid}>
                          {review.technicalQuality && (
                            <div className={styles.ratingItem}>
                              <p className={styles.ratingLabel}>Technical</p>
                              <div className={styles.ratingBar}>
                                <div className={styles.ratingTrack}>
                                  <div 
                                    className={styles.ratingFill} 
                                    style={{ width: `${(review.technicalQuality / 5) * 100}%` }}
                                  />
                                </div>
                                <span className={styles.ratingValue}>{review.technicalQuality}/5</span>
                              </div>
                            </div>
                          )}
                          {review.clarity && (
                            <div className={styles.ratingItem}>
                              <p className={styles.ratingLabel}>Clarity</p>
                              <div className={styles.ratingBar}>
                                <div className={styles.ratingTrack}>
                                  <div 
                                    className={styles.ratingFill} 
                                    style={{ width: `${(review.clarity / 5) * 100}%` }}
                                  />
                                </div>
                                <span className={styles.ratingValue}>{review.clarity}/5</span>
                              </div>
                            </div>
                          )}
                          {review.originality && (
                            <div className={styles.ratingItem}>
                              <p className={styles.ratingLabel}>Originality</p>
                              <div className={styles.ratingBar}>
                                <div className={styles.ratingTrack}>
                                  <div 
                                    className={styles.ratingFill} 
                                    style={{ width: `${(review.originality / 5) * 100}%` }}
                                  />
                                </div>
                                <span className={styles.ratingValue}>{review.originality}/5</span>
                              </div>
                            </div>
                          )}
                          {review.significance && (
                            <div className={styles.ratingItem}>
                              <p className={styles.ratingLabel}>Significance</p>
                              <div className={styles.ratingBar}>
                                <div className={styles.ratingTrack}>
                                  <div 
                                    className={styles.ratingFill} 
                                    style={{ width: `${(review.significance / 5) * 100}%` }}
                                  />
                                </div>
                                <span className={styles.ratingValue}>{review.significance}/5</span>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Recommendation */}
                      {review.recommendation && (
                        <div className={styles.reviewField}>
                          <h4 className={styles.fieldLabel}>Critical Requirement</h4>
                          <p className={styles.fieldValue}>{review.recommendation}</p>
                        </div>
                      )}

                      {/* Comments */}
                      {review.authorComments && (
                        <div className={styles.reviewField}>
                          <h4 className={styles.fieldLabel}>Comments</h4>
                          <p className={styles.fieldComment}>"{review.authorComments}"</p>
                        </div>
                      )}

                      {/* Confidential Comments - Editor Only */}
                      {(isEditor() || isAdmin()) && review.confidentialComments && (
                        <div className={styles.reviewFieldConfidential}>
                          <h4 className={styles.fieldLabel}>Confidential Comments (Editor Only)</h4>
                          <p className={styles.fieldComment}>{review.confidentialComments}</p>
                        </div>
                      )}
                    </div>

                    {/* Download Report Button */}
                    {review.reviewReportFile && (
                      <div className={styles.reviewFooter}>
                        <button 
                          className={styles.downloadBtn}
                          onClick={(e) => handleDownloadReviewReport(review.id, e)}
                        >
                          <span className="material-symbols-rounded">download</span>
                          Download Full Report
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Resubmit Form - kept inline as it's author-specific */}
          {showResubmitForm && isAuthor() && (
            <section className={styles.section}>
              <div className={styles.sectionHeader}>
                <span className="material-symbols-rounded">upload_file</span>
                <h2 className={styles.sectionTitle}>Resubmit Revised Paper</h2>
              </div>
              <div className={styles.sectionCard}>
                <p className={styles.resubmitNote}>
                  Please upload your revised manuscript addressing the reviewer's comments and provide a summary of the changes made.
                </p>
                <div className={styles.form}>
                  <div className={styles.formGroup}>
                    <label htmlFor="revisedFile">Revised Paper File *</label>
                    <input
                      type="file"
                      id="revisedFile"
                      accept=".pdf,.doc,.docx"
                      onChange={(e) => setResubmitFile(e.target.files[0])}
                      disabled={resubmitting}
                      className={styles.fileInput}
                    />
                    {resubmitFile && (
                      <p className={styles.selectedFile}>
                        <span className="material-symbols-rounded">description</span>
                        {resubmitFile.name} ({(resubmitFile.size / 1024 / 1024).toFixed(2)} MB)
                      </p>
                    )}
                  </div>

                  <div className={styles.formGroup}>
                    <label htmlFor="revisionReason">Revision Summary *</label>
                    <textarea
                      id="revisionReason"
                      value={revisionReason}
                      onChange={(e) => setRevisionReason(e.target.value)}
                      placeholder="Briefly describe the changes made in response to the reviewer comments..."
                      rows={4}
                      disabled={resubmitting}
                      className={styles.textarea}
                    />
                  </div>

                  <div className={styles.formGroup}>
                    <label htmlFor="changeSummary">Detailed Change Log (Optional)</label>
                    <textarea
                      id="changeSummary"
                      value={changeSummary}
                      onChange={(e) => setChangeSummary(e.target.value)}
                      placeholder="List specific changes made..."
                      rows={6}
                      disabled={resubmitting}
                      className={styles.textarea}
                    />
                  </div>

                  <div className={styles.formActions}>
                    <button
                      className={styles.btnPrimary}
                      onClick={handleResubmit}
                      disabled={resubmitting || !resubmitFile || !revisionReason.trim()}
                    >
                      {resubmitting ? 'Resubmitting...' : 'Submit Revision'}
                    </button>
                    <button
                      className={styles.btnSecondary}
                      onClick={() => {
                        setShowResubmitForm(false);
                        setResubmitFile(null);
                        setRevisionReason('');
                        setChangeSummary('');
                      }}
                      disabled={resubmitting}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </section>
          )}
        </div>

        {/* Right Column - Sidebar */}
        <aside className={styles.sideColumn}>
          {/* Activity Timeline */}
          <div className={styles.timelineCard}>
            <div className={styles.timelineHeader}>
              <h2 className={styles.timelineTitle}>Activity Timeline</h2>
            </div>
            <div className={styles.timelineContent}>
              <div className={styles.timelineList}>
                {/* Submission Event */}
                <div className={styles.timelineItem}>
                  <div className={styles.timelineConnector} />
                  <div className={`${styles.timelineIcon} ${styles.iconBlue}`}>
                    <span className="material-symbols-rounded">publish</span>
                  </div>
                  <div className={styles.timelineInfo}>
                    <p className={styles.timelineEvent}>Paper Submitted</p>
                    <p className={styles.timelineDate}>{formatDateTime(paper.submittedDate)}</p>
                  </div>
                </div>

                {/* Review Assignment Events */}
                {paper.reviews && paper.reviews.length > 0 && (
                  <div className={styles.timelineItem}>
                    <div className={styles.timelineConnector} />
                    <div className={`${styles.timelineIcon} ${styles.iconSlate}`}>
                      <span className="material-symbols-rounded">person_search</span>
                    </div>
                    <div className={styles.timelineInfo}>
                      <p className={styles.timelineEvent}>Reviewer Assigned</p>
                      <p className={styles.timelineDate}>
                        {paper.reviews.length} reviewer{paper.reviews.length > 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                )}

                {/* Status-based Event */}
                {paper.status === 'revision_requested' && (
                  <div className={styles.timelineItem}>
                    <div className={`${styles.timelineIcon} ${styles.iconAmber}`}>
                      <span className="material-symbols-rounded">edit_note</span>
                    </div>
                    <div className={styles.timelineInfo}>
                      <p className={styles.timelineEvent}>Revision Requested</p>
                      <p className={styles.timelineDate}>Action Required</p>
                    </div>
                  </div>
                )}

                {paper.status === 'accepted' && (
                  <div className={styles.timelineItem}>
                    <div className={`${styles.timelineIcon} ${styles.iconGreen}`}>
                      <span className="material-symbols-rounded">check_circle</span>
                    </div>
                    <div className={styles.timelineInfo}>
                      <p className={styles.timelineEvent}>Paper Accepted</p>
                      <p className={styles.timelineDate}>Congratulations!</p>
                    </div>
                  </div>
                )}

                {paper.status === 'rejected' && (
                  <div className={styles.timelineItem}>
                    <div className={`${styles.timelineIcon} ${styles.iconRed}`}>
                      <span className="material-symbols-rounded">cancel</span>
                    </div>
                    <div className={styles.timelineInfo}>
                      <p className={styles.timelineEvent}>Paper Rejected</p>
                      <p className={styles.timelineDate}>See feedback for details</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Alerts Card */}
          <div className={styles.alertCard}>
            <div className={styles.alertContent}>
              <span className="material-symbols-rounded">notifications</span>
              <p>No new alerts for this paper.</p>
            </div>
          </div>

          {/* Help Card / Contact Author Card */}
          <div className={styles.helpCard}>
            <h3 className={styles.helpTitle}>
              {(isAdmin() || isEditor()) ? 'Contact Author' : 'Need assistance?'}
            </h3>
            <p className={styles.helpText}>
              {(isAdmin() || isEditor()) 
                ? 'Send email correspondence to the author regarding this submission.'
                : 'Our editorial board is here to assist you with any questions regarding the submission process or peer-review status.'}
            </p>
            <button 
              className={styles.helpBtn}
              onClick={() => {
                if (isAdmin() || isEditor()) {
                  setShowContactModal(true);
                } else {
                  // For authors, show the contact modal
                  setShowAuthorContactModal(true);
                }
              }}
            >
              {(isAdmin() || isEditor()) ? 'Send Email to Author' : 'Contact Editorial Office'}
            </button>
          </div>

          {/* Admin/Editor Actions */}
          {(isAdmin() || isEditor()) && (
            <div className={styles.authorActionsCard}>
              <button 
                className={styles.actionCardBtn}
                onClick={() => {
                  setShowCorrespondence(!showCorrespondence);
                  if (!showCorrespondence && correspondence.length === 0) {
                    fetchCorrespondence();
                  }
                }}
              >
                <span className="material-symbols-rounded">mail</span>
                Correspondence History
              </button>
            </div>
          )}

          {/* Author Actions */}
          {isAuthor() && (
            <div className={styles.authorActionsCard}>
              <button 
                className={styles.actionCardBtn}
                onClick={() => {
                  setShowCorrespondence(!showCorrespondence);
                  if (!showCorrespondence && correspondence.length === 0) {
                    fetchCorrespondence();
                  }
                }}
              >
                <span className="material-symbols-rounded">mail</span>
                View Notifications
              </button>
              <button 
                className={styles.actionCardBtn}
                onClick={() => {
                  setShowRevisions(!showRevisions);
                  if (!showRevisions && revisionHistory.length === 0) {
                    fetchRevisionHistory();
                  }
                }}
              >
                <span className="material-symbols-rounded">history</span>
                Version History
              </button>
            </div>
          )}
        </aside>
      </div>

      {/* Correspondence Modal/Section */}
      {showCorrespondence && (isAuthor() || isAdmin() || isEditor()) && (
        <div className={styles.modalOverlay} onClick={() => setShowCorrespondence(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>{isAuthor() ? 'Email Notifications' : 'Correspondence History'}</h2>
              <button onClick={() => setShowCorrespondence(false)}>
                <span className="material-symbols-rounded">close</span>
              </button>
            </div>
            <div className={styles.modalBody}>
              {loadingCorrespondence ? (
                <div className={styles.loadingSection}>
                  <span className="material-symbols-rounded">hourglass_empty</span>
                  Loading...
                </div>
              ) : correspondence.length === 0 ? (
                <div className={styles.emptySection}>
                  <span className="material-symbols-rounded">inbox</span>
                  <p>No {isAuthor() ? 'email notifications' : 'correspondence'} yet.</p>
                </div>
              ) : (
                <div className={styles.correspondenceList}>
                  {correspondence.map((email, idx) => (
                    <div key={email.id || idx} className={styles.correspondenceItem}>
                      <div className={styles.correspondenceHeader}>
                        <span className={styles.emailType}>
                          {email.email_type?.replace(/_/g, ' ').toUpperCase() || 
                           (email.sender_role ? `Sent by ${email.sender_role}` : 'Email')}
                        </span>
                        <span className={styles.emailDate}>
                          {new Date(email.created_at || email.sent_at).toLocaleString()}
                        </span>
                      </div>
                      <div className={styles.correspondenceBody}>
                        <p className={styles.emailSubject}>{email.subject}</p>
                        <span className={`${styles.emailStatus} ${styles[`status${email.delivery_status || 'sent'}`]}`}>
                          {email.delivery_status === 'sent' || !email.delivery_status ? '✓ Delivered' : 
                           email.delivery_status === 'failed' ? '✗ Failed' : '⋯ Pending'}
                        </span>
                        {(isAdmin() || isEditor()) && (
                          <span className={styles.readStatus}>
                            {email.is_read ? '👁 Read' : '○ Unread'}
                          </span>
                        )}
                      </div>
                      {/* Show message preview for admin/editor */}
                      {(isAdmin() || isEditor()) && email.message && (
                        <div className={styles.messagePreview}>
                          {email.message.substring(0, 150)}...
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Revision History Modal */}
      {showRevisions && isAuthor() && (
        <div className={styles.modalOverlay} onClick={() => setShowRevisions(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Version History</h2>
              <button onClick={() => setShowRevisions(false)}>
                <span className="material-symbols-rounded">close</span>
              </button>
            </div>
            <div className={styles.modalBody}>
              {loadingRevisions ? (
                <div className={styles.loadingSection}>
                  <span className="material-symbols-rounded">hourglass_empty</span>
                  Loading...
                </div>
              ) : revisionHistory.length === 0 ? (
                <div className={styles.emptySection}>
                  <span className="material-symbols-rounded">inventory_2</span>
                  <p>No previous versions. This is the original submission.</p>
                </div>
              ) : (
                <div className={styles.revisionList}>
                  {revisionHistory.map((revision, idx) => (
                    <div key={idx} className={styles.revisionItem}>
                      <div className={styles.revisionVersion}>
                        <span className={styles.versionBadge}>V{revision.version_number || idx + 1}</span>
                        <span className={styles.revisionDate}>
                          {new Date(revision.submitted_at || revision.created_at).toLocaleString()}
                        </span>
                      </div>
                      <div className={styles.revisionDetails}>
                        {revision.revision_reason && (
                          <p className={styles.revisionReason}>
                            <strong>Reason:</strong> {revision.revision_reason}
                          </p>
                        )}
                        {revision.change_summary && (
                          <p className={styles.changeSummary}>
                            <strong>Changes:</strong> {revision.change_summary}
                          </p>
                        )}
                        {revision.file_name && (
                          <p className={styles.revisionFile}>
                            <span className="material-symbols-rounded">description</span>
                            {revision.file_name}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Assign Reviewer Modal */}
      {showAssignReviewer && (isEditor() || isAdmin()) && (
        <div className={styles.modalOverlay} onClick={() => {
          setShowAssignReviewer(false);
          setReviewerEmail('');
          setSearchReviewers('');
          setShowReviewerDropdown(false);
        }}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Assign Reviewer</h2>
              <button onClick={() => {
                setShowAssignReviewer(false);
                setReviewerEmail('');
                setSearchReviewers('');
                setShowReviewerDropdown(false);
              }}>
                <span className="material-symbols-rounded">close</span>
              </button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.assignReviewerInfo}>
                <div className={styles.paperInfoRow}>
                  <span className={styles.paperInfoLabel}>Paper:</span>
                  <span className={styles.paperInfoValue}>{paper.title}</span>
                </div>
                <div className={styles.paperInfoRow}>
                  <span className={styles.paperInfoLabel}>Status:</span>
                  <StatusChips status={paper.status} />
                </div>
              </div>

              {/* Show currently assigned reviewers */}
              {paper.reviews && paper.reviews.length > 0 && (
                <div className={styles.currentReviewers}>
                  <h4 className={styles.currentReviewersTitle}>Currently Assigned Reviewers</h4>
                  <div className={styles.currentReviewersList}>
                    {paper.reviews.map((review, idx) => (
                      <div key={review.id || idx} className={styles.currentReviewerItem}>
                        <div className={styles.reviewerAvatarSmall}>
                          {getInitials(review.reviewerName || `R${idx + 1}`)}
                        </div>
                        <div className={styles.currentReviewerInfo}>
                          <p className={styles.currentReviewerName}>{review.reviewerName || `Reviewer #${idx + 1}`}</p>
                          <p className={styles.currentReviewerStatus}>
                            {review.status === 'completed' ? '✓ Review Completed' : 
                             review.status === 'pending' ? '⋯ Review Pending' : 
                             '○ Invited'}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className={styles.form}>
                <div className={styles.formGroup}>
                  <label htmlFor="reviewerEmail">Select or Enter Reviewer Email</label>
                  <div className={styles.reviewerInputContainer}>
                    <input
                      type="text"
                      id="reviewerEmail"
                      value={searchReviewers}
                      onChange={(e) => {
                        setSearchReviewers(e.target.value);
                        setShowReviewerDropdown(true);
                      }}
                      onFocus={() => {
                        if (!availableReviewers.length) {
                          fetchAvailableReviewers();
                        }
                        setShowReviewerDropdown(true);
                      }}
                      placeholder="Search reviewers by name or email..."
                      disabled={assigningReviewer}
                      className={styles.formInput}
                    />
                    {showReviewerDropdown && (
                      <div className={styles.reviewerDropdown}>
                        {loadingReviewers ? (
                          <div className={styles.dropdownItem}>
                            <span className="material-symbols-rounded">hourglass_empty</span>
                            Loading reviewers...
                          </div>
                        ) : filteredReviewers.length > 0 ? (
                          filteredReviewers.map((reviewer) => (
                            <div
                              key={reviewer.id}
                              className={styles.dropdownItem}
                              onClick={() => handleSelectReviewer(reviewer)}
                            >
                              <div className={styles.reviewerAvatarSmall}>
                                {getInitials(reviewer.name)}
                              </div>
                              <div className={styles.dropdownItemContent}>
                                <p className={styles.dropdownItemName}>{reviewer.name}</p>
                                <p className={styles.dropdownItemEmail}>{reviewer.email}</p>
                                {reviewer.specialization && (
                                  <p className={styles.dropdownItemSpec}>{reviewer.specialization}</p>
                                )}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className={styles.dropdownItem}>
                            <span className="material-symbols-rounded">search_off</span>
                            No reviewers found
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  {reviewerEmail && (
                    <div className={styles.selectedReviewerCard}>
                      <div className={styles.selectedReviewerAvatar}>
                        {getInitials(searchReviewers || reviewerEmail)}
                      </div>
                      <div className={styles.selectedReviewerInfo}>
                        <p className={styles.selectedReviewerName}>{searchReviewers || 'Unknown'}</p>
                        <p className={styles.selectedReviewerEmail}>{reviewerEmail}</p>
                      </div>
                      <button 
                        className={styles.clearSelection}
                        onClick={() => {
                          setReviewerEmail('');
                          setSearchReviewers('');
                        }}
                      >
                        <span className="material-symbols-rounded">close</span>
                      </button>
                    </div>
                  )}
                </div>

                <div className={styles.formGroup}>
                  <label htmlFor="dueDays">Review Due In (Days)</label>
                  <input
                    type="number"
                    id="dueDays"
                    value={dueDays}
                    onChange={(e) => setDueDays(parseInt(e.target.value) || 14)}
                    min="1"
                    max="90"
                    disabled={assigningReviewer}
                    className={styles.formInput}
                  />
                  <p className={styles.formHint}>
                    Due date: {new Date(Date.now() + dueDays * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' })}
                  </p>
                </div>

                <div className={styles.formActions}>
                  <button
                    className={styles.btnSecondary}
                    onClick={() => {
                      setShowAssignReviewer(false);
                      setReviewerEmail('');
                      setSearchReviewers('');
                      setShowReviewerDropdown(false);
                    }}
                    disabled={assigningReviewer}
                  >
                    Cancel
                  </button>
                  <button
                    className={styles.btnPrimary}
                    onClick={handleAssignReviewer}
                    disabled={assigningReviewer || !reviewerEmail}
                  >
                    {assigningReviewer ? (
                      <>
                        <span className="material-symbols-rounded">hourglass_empty</span>
                        Sending...
                      </>
                    ) : (
                      <>
                        <span className="material-symbols-rounded">send</span>
                        Send Invitation
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Contact Editorial Modal (Admin/Editor) */}
      {paper && (isAdmin() || isEditor()) && (
        <ContactEditorialModal
          isOpen={showContactModal}
          onClose={handleContactModalClose}
          paperId={paper.id}
          paperTitle={paper.title}
          authorName={paper.author?.name || paper.authorName || 'Author'}
          authorEmail={paper.author?.email || paper.authorEmail || ''}
          currentStatus={paper.status}
          senderRole={isAdmin() ? 'admin' : 'editor'}
        />
      )}

      {/* Author Contact Editorial Modal */}
      {paper && isAuthor() && (
        <AuthorContactModal
          isOpen={showAuthorContactModal}
          onClose={() => setShowAuthorContactModal(false)}
          paperId={paper.id}
          paperCode={paper.paperCode || paper.paper_code || `#${paper.id}`}
          paperTitle={paper.title}
        />
      )}
    </div>
  );
};

export default PaperDetailsPage;
