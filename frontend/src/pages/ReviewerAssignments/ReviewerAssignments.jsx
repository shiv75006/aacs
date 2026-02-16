import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import acsApi from '../../api/apiService';
import StatusFilterBar from '../../components/StatusFilterBar/StatusFilterBar';
import Pagination from '../../components/Pagination/Pagination';
import { useListWithFilters } from '../../hooks/useListWithFilters';
import { useToast } from '../../hooks/useToast';
import styles from './ReviewerAssignments.module.css';

const ReviewerAssignments = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [statusStats, setStatusStats] = useState({});
  const [statsLoading, setStatsLoading] = useState(true);

  const fetchAssignmentsWithFilters = async (skip, limit, filters) => {
    return await acsApi.reviewer.listAssignments(skip, limit, filters.status || '', filters.sort || 'due_soon');
  };

  const {
    data: assignments,
    loading,
    error,
    pagination,
    filters,
    handleFilterChange,
    goToPage,
  } = useListWithFilters(fetchAssignmentsWithFilters, { status: '', sort: 'due_soon' }, 10);

  // Fetch assignment statistics
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setStatsLoading(true);
        const dashboardStats = await acsApi.reviewer.getDashboardStats();
        // Transform dashboard stats to status format
        setStatusStats({
          'pending': dashboardStats.pending_reviews || 0,
          'completed': dashboardStats.completed_reviews || 0,
          'all': dashboardStats.total_assignments || 0,
        });
      } catch (err) {
        console.warn('Failed to load assignment stats:', err);
        setStatusStats({});
      } finally {
        setStatsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleStatusFilter = (status) => {
    handleFilterChange('status', status);
  };

  const handleStartReview = (assignmentId) => {
    navigate(`/reviewer/assignments/${assignmentId}/review`);
  };

  const getDaysRemaining = (dueDate) => {
    const due = new Date(dueDate);
    const today = new Date();
    const diff = Math.ceil((due - today) / (1000 * 60 * 60 * 24));
    return diff;
  };

  const getUrgencyClass = (daysRemaining) => {
    if (daysRemaining < 3) return 'urgency-high';
    if (daysRemaining < 7) return 'urgency-medium';
    return 'urgency-low';
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>My Assignments</h1>
        <p>View and manage your paper review assignments</p>
      </div>

      {/* Status Filter Bar */}
      {!statsLoading && Object.keys(statusStats).length > 0 && (
        <StatusFilterBar
          statuses={statusStats}
          activeFilter={filters.status}
          onFilterChange={handleStatusFilter}
          loading={loading}
        />
      )}

      {/* Loading State */}
      {loading && (
        <div className={styles.loading}>
          <span className="material-symbols-rounded">hourglass_empty</span>
          <p>Loading assignments...</p>
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
      {!loading && !error && assignments.length === 0 && (
        <div className={styles.empty}>
          <span className="material-symbols-rounded">inbox</span>
          <p>No assignments found</p>
        </div>
      )}

      {/* Assignments List */}
      {!loading && assignments.length > 0 && (
        <>
          <div className={styles.assignmentsList}>
            {assignments.map((assignment) => {
              const daysRemaining = getDaysRemaining(assignment.due_date);
              return (
                <div key={assignment.id} className={styles.assignmentCard}>
                  <div className={styles.cardContent}>
                    <div className={styles.titleSection}>
                      <h3 className={styles.paperTitle}>{assignment.paper_title || 'Untitled Paper'}</h3>
                    </div>

                    <div className={styles.metaSection}>
                      <div className={styles.metaLeft}>
                        <span className={styles.metaItem}>
                          <span className="material-symbols-rounded">person</span>
                          {assignment.author || 'Unknown Author'}
                        </span>
                        <span className={styles.metaItem}>
                          <span className="material-symbols-rounded">newspaper</span>
                          {assignment.journal || 'No Journal'}
                        </span>
                        <span className={styles.metaItem}>
                          <span className="material-symbols-rounded">calendar_today</span>
                          Due: {new Date(assignment.due_date).toLocaleDateString()}
                        </span>
                      </div>

                      <div className={styles.metaRight}>
                        <span className={`${styles.statusBadge} ${styles[`status${assignment.status?.charAt(0).toUpperCase() + assignment.status?.slice(1)}`]}`}>
                          {assignment.status || 'Pending'}
                        </span>
                        <span className={`${styles.urgencyBadge} ${styles[getUrgencyClass(daysRemaining)]}`}>
                          {daysRemaining > 0 ? `${daysRemaining}d left` : 'Overdue'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {assignment.status === 'pending' && (
                    <button
                      className={styles.startBtn}
                      onClick={() => handleStartReview(assignment.id)}
                    >
                      <span>Start Review</span>
                      <span className="material-symbols-rounded">arrow_forward</span>
                    </button>
                  )}

                  {assignment.status === 'in_progress' && (
                    <button
                      className={styles.continueBtn}
                      onClick={() => handleStartReview(assignment.id)}
                    >
                      <span>Continue</span>
                      <span className="material-symbols-rounded">arrow_forward</span>
                    </button>
                  )}

                  {assignment.status === 'completed' && (
                    <button
                      className={styles.viewBtn}
                      onClick={() => navigate(`/reviewer/assignments/${assignment.id}`)}
                    >
                      <span>View</span>
                      <span className="material-symbols-rounded">open_in_new</span>
                    </button>
                  )}
                </div>
              );
            })}
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

export default ReviewerAssignments;
