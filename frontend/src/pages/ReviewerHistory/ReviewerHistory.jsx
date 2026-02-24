import React, { useEffect, useState } from 'react';
import acsApi from '../../api/apiService';
import Pagination from '../../components/pagination/Pagination';
import { useListWithFilters } from '../../hooks/useListWithFilters';
import styles from './ReviewerHistory.module.css';

const ReviewerHistory = () => {
  const fetchHistoryWithFilters = async (skip, limit) => {
    return await acsApi.reviewer.getReviewHistory(skip, limit);
  };

  const {
    data: reviews,
    loading,
    error,
    pagination,
    goToPage,
  } = useListWithFilters(fetchHistoryWithFilters, {}, 10);

  const getRecommendationColor = (recommendation) => {
    const colorMap = {
      'accept': 'recommendation-accept',
      'minor_revisions': 'recommendation-minor',
      'major_revisions': 'recommendation-major',
      'reject': 'recommendation-reject',
    };
    return colorMap[recommendation] || 'recommendation-neutral';
  };

  const getRecommendationLabel = (recommendation) => {
    const labelMap = {
      'accept': 'Accept',
      'minor_revisions': 'Minor Revisions',
      'major_revisions': 'Major Revisions',
      'reject': 'Reject',
    };
    return labelMap[recommendation] || recommendation;
  };

  const calculateAverageRating = (review) => {
    if (!review.ratings) return 'N/A';
    const ratings = Object.values(review.ratings).filter(r => typeof r === 'number');
    if (ratings.length === 0) return 'N/A';
    const average = (ratings.reduce((a, b) => a + b, 0) / ratings.length).toFixed(1);
    return average;
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Review History</h1>
        <p>View your completed reviews and submissions</p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className={styles.loading}>
          <span className="material-symbols-rounded">hourglass_empty</span>
          <p>Loading review history...</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className={styles.error}>
          <span className="material-symbols-rounded">error_outline</span>
          <p>{error}</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && reviews.length === 0 && (
        <div className={styles.empty}>
          <span className="material-symbols-rounded">inbox</span>
          <p>No reviews completed yet</p>
        </div>
      )}

      {/* Reviews List */}
      {!loading && reviews.length > 0 && (
        <>
          <div className={styles.reviewsList}>
            {reviews.map((review) => (
              <div key={review.id} className={styles.reviewCard}>
                <div className={styles.cardHeader}>
                  <h3 className={styles.paperTitle}>{review.paper_title || 'Untitled Paper'}</h3>
                  <span className={`${styles.recommendationBadge} ${styles[getRecommendationColor(review.recommendation)]}`}>
                    {getRecommendationLabel(review.recommendation)}
                  </span>
                </div>

                <div className={styles.cardMeta}>
                  <div className={styles.metaLeft}>
                    <span className={styles.metaItem}>
                      <span className="material-symbols-rounded">newspaper</span>
                      {review.journal || 'No Journal'}
                    </span>
                    <span className={styles.metaItem}>
                      <span className="material-symbols-rounded">calendar_today</span>
                      {new Date(review.submitted_date).toLocaleDateString()}
                    </span>
                  </div>

                  <div className={styles.metaRight}>
                    <span className={styles.averageRating}>
                      <span className="material-symbols-rounded">star</span>
                      {calculateAverageRating(review)} / 5
                    </span>
                  </div>
                </div>

                {review.ratings && (
                  <div className={styles.ratingsGrid}>
                    {Object.entries(review.ratings).map(([criterion, rating]) => (
                      typeof rating === 'number' && (
                        <div key={criterion} className={styles.ratingItem}>
                          <span className={styles.ratingLabel}>
                            {criterion.replace(/_/g, ' ').charAt(0).toUpperCase() + criterion.replace(/_/g, ' ').slice(1)}
                          </span>
                          <div className={styles.ratingStars}>
                            {[...Array(5)].map((_, i) => (
                              <span
                                key={i}
                                className={`material-symbols-rounded ${i < rating ? styles.starFilled : styles.starEmpty}`}
                              >
                                star
                              </span>
                            ))}
                          </div>
                        </div>
                      )
                    ))}
                  </div>
                )}

                {review.author_comments && (
                  <div className={styles.comments}>
                    <h4>Author Comments</h4>
                    <p>{review.author_comments}</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination */}
          {pagination.totalPages > 1 && (
            <div className={styles.paginationContainer}>
              <Pagination
                currentPage={pagination.currentPage}
                totalPages={pagination.totalPages}
                onPageChange={goToPage}
                isLoading={loading}
                itemsPerPage={pagination.limit}
                totalItems={pagination.total}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ReviewerHistory;
