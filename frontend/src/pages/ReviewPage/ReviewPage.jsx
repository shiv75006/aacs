import React, { useEffect, useState, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ToastContext } from '../../contexts/ToastContext';
import acsApi from '../../api/apiService';
import ReviewForm from '../../components/ReviewForm/ReviewForm';
import PaperViewer from '../../components/PaperViewer/PaperViewer';
import styles from './ReviewPage.module.css';

const ReviewPage = () => {
  const { id: reviewId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useContext(ToastContext);

  const [reviewDetail, setReviewDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const fetchReviewDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await acsApi.reviewer.getReviewDetail(reviewId);
      setReviewDetail(data);
    } catch (err) {
      console.error('Error fetching review detail:', err);
      setError(err.response?.data?.detail || 'Failed to load review details');
      if (showToast) showToast('error', 'Failed to load review details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviewDetail();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reviewId]);

  const handleSaveDraft = async (reviewData) => {
    try {
      const result = await acsApi.reviewer.saveReviewDraft(reviewId, reviewData);
      if (showToast) showToast('success', 'Review draft saved successfully');
      return result;
    } catch (err) {
      console.error('Error saving draft:', err);
      if (showToast) showToast('error', err.response?.data?.detail || 'Failed to save draft');
      throw err;
    }
  };

  const handleSubmitReview = async (reviewData) => {
    try {
      setSubmitting(true);
      const result = await acsApi.reviewer.submitReview(reviewId, reviewData);
      if (showToast) showToast('success', 'Review submitted successfully');
      
      // Update local state with new status
      if (result.assignment) {
        setReviewDetail(prev => ({
          ...prev,
          assignment: {
            ...prev.assignment,
            status: result.assignment.status
          }
        }));
      }
      
      // Redirect to dashboard after successful submission
      setTimeout(() => {
        navigate('/reviewer-dashboard');
      }, 1500);
      
      return result;
    } catch (err) {
      console.error('Error submitting review:', err);
      if (showToast) showToast('error', err.response?.data?.detail || 'Failed to submit review');
      throw err;
    } finally {
      setSubmitting(false);
    }
  };

  const handleUploadReport = async (file) => {
    try {
      const result = await acsApi.reviewer.uploadReviewReport(reviewId, file);
      if (showToast) showToast('success', `Review report uploaded (v${result.file_version})`);
      return result;
    } catch (err) {
      console.error('Error uploading report:', err);
      if (showToast) showToast('error', err.response?.data?.detail || 'Failed to upload report');
      throw err;
    }
  };

  const handleDownloadReport = async () => {
    try {
      const result = await acsApi.reviewer.downloadReviewReport(reviewId);
      // Extract filename from the review submission data or generate one
      const filename = reviewDetail?.review_submission?.review_report_file?.split('/').pop() || `review_report_${reviewId}.pdf`;
      
      // Create blob and trigger download
      const url = window.URL.createObjectURL(new Blob([result.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      if (showToast) showToast('success', 'Report downloaded successfully');
    } catch (err) {
      console.error('Error downloading report:', err);
      if (showToast) showToast('error', err.response?.data?.detail || 'Failed to download report');
    }
  };

  const handleBackClick = () => {
    navigate('/reviewer/assignments');
  };

  if (loading) {
    return (
      <div className={styles.reviewPageContainer}>
        <div className={styles.loading}>
          <span className="material-symbols-rounded">hourglass_empty</span>
          <p>Loading review details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.reviewPageContainer}>
        <div className={styles.error}>
          <span className="material-symbols-rounded">error</span>
          <p>{error}</p>
          <button onClick={handleBackClick} className={styles.backBtn}>
            Back to Assignments
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.reviewPageContainer}>
      <div className={styles.header}>
        <button onClick={handleBackClick} className={styles.backBtn} title="Back to assignments">
          <span className="material-symbols-rounded">arrow_back</span>
        </button>
        <div className={styles.headerContent}>
          <h1>Paper Review</h1>
          <p>{reviewDetail?.paper?.title}</p>
        </div>
      </div>

      <div className={styles.reviewLayout}>
        {/* Left side: Paper Viewer */}
        <div className={styles.paperSection}>
          <PaperViewer paper={reviewDetail?.paper} reviewId={reviewId} />
        </div>

        {/* Right side: Review Form */}
        <div className={styles.formSection}>
          <ReviewForm
            reviewId={reviewId}
            paper={reviewDetail?.paper}
            assignment={reviewDetail?.assignment}
            initialSubmission={reviewDetail?.review_submission}
            onSaveDraft={handleSaveDraft}
            onSubmit={handleSubmitReview}
            onUploadReport={handleUploadReport}
            onDownloadReport={handleDownloadReport}
            isSubmitting={submitting}
          />
        </div>
      </div>
    </div>
  );
};

export default ReviewPage;
