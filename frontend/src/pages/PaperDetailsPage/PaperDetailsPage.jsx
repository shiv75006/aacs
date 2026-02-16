import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useRole } from '../../hooks/useRole';
import { useToast } from '../../hooks/useToast';
import { useModal } from '../../hooks/useModal';
import acsApi from '../../api/apiService';
import paperNormalizer from '../../services/paperNormalizer';
import FileViewer from '../../components/FileViewer/FileViewer';
import StatusChips from '../../components/StatusChips/StatusChips';
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
      const response = await acsApi.editor.listReviewers(0, 100);
      setAvailableReviewers(response.reviewers || []);
      setFilteredReviewers(response.reviewers || []);
    } catch (err) {
      console.error('Failed to fetch reviewers:', err);
      showError('Failed to load available reviewers', 3000);
    } finally {
      setLoadingReviewers(false);
    }
  };

  const fetchPaperDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch based on user role
      let response;
      if (isEditor()) {
        response = await acsApi.admin.listAllPapers(0, 100);
        const found = response.papers?.find(p => p.id === parseInt(id));
        if (!found) {
          setError('Paper not found or you do not have access to it');
          return;
        }
        response = found;
      } else if (isAuthor()) {
        response = await acsApi.author.getSubmissionDetail(id);
      } else if (isReviewer()) {
        response = await acsApi.reviewer.getAssignmentDetail(id);
      } else if (isAdmin()) {
        response = await acsApi.admin.listAllPapers(0, 100);
        const found = response.papers?.find(p => p.id === parseInt(id));
        if (!found) {
          setError('Paper not found or you do not have access to it');
          return;
        }
        response = found;
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
      await acsApi.editor.inviteReviewer(paper.id, reviewerEmail, dueDays);
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

  const handleDownloadPaper = () => {
    if (paper?.filePath) {
      const fileUrl = paper.filePath.startsWith('http')
        ? paper.filePath
        : `/public/${paper.filePath}`;
      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = paper.fileName || 'paper';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      success('Download started', 2000);
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

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate(-1)}>
          <span className="material-symbols-rounded">arrow_back</span>
          Back
        </button>
      </div>

      {/* Main Content */}
      <div className={styles.mainContent}>
        {/* Paper Overview */}
        <div className={styles.card}>
          <div className={styles.titleSection}>
            <h1 className={styles.title}>{paper.title}</h1>
            <StatusChips status={paper.status} />
          </div>

          <div className={styles.metaGrid}>
            <div className={styles.metaItem}>
              <label>Paper ID</label>
              <span>{paper.id}</span>
            </div>
            <div className={styles.metaItem}>
              <label>Journal</label>
              <span>{paper.journal.name}</span>
            </div>
            <div className={styles.metaItem}>
              <label>Submitted Date</label>
              <span>{new Date(paper.submittedDate).toLocaleDateString()}</span>
            </div>
            {paper.paperCode && (
              <div className={styles.metaItem}>
                <label>Paper Code</label>
                <span>{paper.paperCode}</span>
              </div>
            )}
          </div>
        </div>

        {/* Author Information */}
        <div className={styles.card}>
          <h2 className={styles.sectionTitle}>Author Information</h2>
          <div className={styles.authorInfo}>
            <div>
              <p className={styles.authorName}>{paper.author.name || 'Unknown Author'}</p>
              {paper.author.email && <p className={styles.authorEmail}>{paper.author.email}</p>}
            </div>
            {paper.coAuthors && paper.coAuthors.length > 0 && (
              <div className={styles.coAuthors}>
                <h4>Co-Authors</h4>
                <ul>
                  {paper.coAuthors.map((author, idx) => (
                    <li key={idx}>{author}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Abstract */}
        <div className={styles.card}>
          <h2 className={styles.sectionTitle}>Abstract</h2>
          <p className={styles.abstractText}>{paper.abstract || 'No abstract provided'}</p>
        </div>

        {/* Keywords */}
        {paper.keywords && paper.keywords.length > 0 && (
          <div className={styles.card}>
            <h2 className={styles.sectionTitle}>Keywords</h2>
            <div className={styles.keywordsList}>
              {paper.keywords.map((kw, idx) => (
                <span key={idx} className={styles.keyword}>
                  {kw}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* File */}
        <div className={styles.card}>
          <h2 className={styles.sectionTitle}>Paper Document</h2>
          <FileViewer
            filePath={paper.filePath}
            fileName={paper.fileName}
            fileSize={paper.fileSize}
            submittedDate={paper.submittedDate}
          />
        </div>

        {/* Reviews Section - Visible to Editor, Admin, Author */}
        {(isEditor() || isAdmin() || isAuthor()) && paper.reviews && paper.reviews.length > 0 && (
          <div className={styles.card}>
            <h2 className={styles.sectionTitle}>Reviews ({paper.reviews.length})</h2>
            <div className={styles.reviewsList}>
              {paper.reviews.map((review) => (
                <div
                  key={review.id}
                  className={styles.reviewItem}
                  onClick={() => setExpandedReviewId(expandedReviewId === review.id ? null : review.id)}
                >
                  <div className={styles.reviewHeader}>
                    <div className={styles.reviewerInfo}>
                      <p className={styles.reviewerName}>{review.reviewerName}</p>
                      {isEditor() || isAdmin() ? (
                        <p className={styles.reviewerEmail}>{review.reviewerEmail}</p>
                      ) : null}
                    </div>
                    <div className={styles.reviewMeta}>
                      {review.status && (
                        <span className={`${styles.reviewStatus} ${styles[`status${review.status.replace(/_/g, '')}`.toLowerCase()]}`}>
                          {review.status.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      )}
                      {review.overallRating && (
                        <span className={styles.rating}>
                          ⭐ {review.overallRating.toFixed(1)}
                        </span>
                      )}
                      <span className={styles.expandIcon}>
                        {expandedReviewId === review.id ? '−' : '+'}
                      </span>
                    </div>
                  </div>

                  {expandedReviewId === review.id && (
                    <div className={styles.reviewBody}>
                      {(review.technicalQuality || review.clarity || review.originality || review.significance) && (
                        <div className={styles.ratingsGrid}>
                          {review.technicalQuality && (
                            <div className={styles.ratingItem}>
                              <label>Technical Quality</label>
                              <span>{review.technicalQuality}/5</span>
                            </div>
                          )}
                          {review.clarity && (
                            <div className={styles.ratingItem}>
                              <label>Clarity</label>
                              <span>{review.clarity}/5</span>
                            </div>
                          )}
                          {review.originality && (
                            <div className={styles.ratingItem}>
                              <label>Originality</label>
                              <span>{review.originality}/5</span>
                            </div>
                          )}
                          {review.significance && (
                            <div className={styles.ratingItem}>
                              <label>Significance</label>
                              <span>{review.significance}/5</span>
                            </div>
                          )}
                        </div>
                      )}

                      {review.recommendation && (
                        <div className={styles.recommendation}>
                          <label>Recommendation</label>
                          <p>{review.recommendation}</p>
                        </div>
                      )}

                      {review.authorComments && (
                        <div className={styles.comments}>
                          <label>Comments for Authors</label>
                          <p>{review.authorComments}</p>
                        </div>
                      )}

                      {(isEditor() || isAdmin()) && review.confidentialComments && (
                        <div className={styles.confidential}>
                          <label>Confidential Comments (Editor Only)</label>
                          <p>{review.confidentialComments}</p>
                        </div>
                      )}

                      {review.submittedDate && (
                        <p className={styles.submittedDate}>
                          Submitted: {new Date(review.submittedDate).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className={styles.actions}>
          {isEditor() && (
            <>
              <button
                className={`${styles.btn} ${styles.btnPrimary}`}
                onClick={() => setShowAssignReviewer(!showAssignReviewer)}
              >
                <span className="material-symbols-rounded">person_add</span>
                Assign Reviewer
              </button>
              <button className={`${styles.btn} ${styles.btnSecondary}`} onClick={handleDownloadPaper}>
                <span className="material-symbols-rounded">download</span>
                Download Paper
              </button>
            </>
          )}

          {isAdmin() && (
            <>
              <button
                className={`${styles.btn} ${styles.btnPrimary}`}
                onClick={() => setShowAssignReviewer(!showAssignReviewer)}
              >
                <span className="material-symbols-rounded">person_add</span>
                Assign Reviewer
              </button>
              <button className={`${styles.btn} ${styles.btnSecondary}`} onClick={handleDownloadPaper}>
                <span className="material-symbols-rounded">download</span>
                Download Paper
              </button>
            </>
          )}

          {isAuthor() && (
            <button className={`${styles.btn} ${styles.btnSecondary}`} onClick={handleDownloadPaper}>
              <span className="material-symbols-rounded">download</span>
              Download My Paper
            </button>
          )}
        </div>

        {/* Assign Reviewer Form */}
        {showAssignReviewer && (isEditor() || isAdmin()) && (
          <div className={styles.card}>
            <h2 className={styles.sectionTitle}>Assign Reviewer</h2>
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
                    className={styles.reviewerInput}
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
                  <p className={styles.selectedReviewer}>
                    Selected: <strong>{reviewerEmail}</strong>
                  </p>
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
                />
              </div>

              <div className={styles.formActions}>
                <button
                  className={`${styles.btn} ${styles.btnPrimary}`}
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
                <button
                  className={`${styles.btn} ${styles.btnSecondary}`}
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
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PaperDetailsPage;
