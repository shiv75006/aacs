import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import acsApi from '../../api/apiService';
import Pagination from '../../components/pagination/Pagination';
import AssignmentCard from '../../components/AssignmentCard/AssignmentCard';
import { useListWithFilters } from '../../hooks/useListWithFilters';
import styles from './ReviewerAssignments.module.css';

const ReviewerAssignments = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const fetchAssignmentsWithFilters = useCallback(async (skip, limit, filters) => {
    return await acsApi.reviewer.listAssignments(skip, limit, '', filters.sort || 'due_soon');
  }, []);

  const {
    data: allAssignments,
    loading,
    error,
    pagination,
    filters,
    goToPage,
  } = useListWithFilters(fetchAssignmentsWithFilters, { sort: 'due_soon' }, 10, refreshTrigger);

  // Refresh data when page regains focus
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        setRefreshTrigger(prev => prev + 1);
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm.toLowerCase());
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Filter assignments based on search term
  const assignments = allAssignments.filter(assignment => {
    if (!debouncedSearchTerm) return true;
    const title = (assignment.paper_title || '').toLowerCase();
    const code = (assignment.paper_code || '').toLowerCase();
    return title.includes(debouncedSearchTerm) || code.includes(debouncedSearchTerm);
  });

  // Debug logging
  useEffect(() => {
    if (assignments.length > 0) {
      console.log('✓ Assignments loaded:', assignments.length);
    }
    if (error) {
      console.error('✗ Error loading assignments:', error);
    }
  }, [assignments, error]);

  const handleStartReview = (assignmentId) => {
    navigate(`/reviewer/assignments/${assignmentId}/review`);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>My Submissions</h1>
        <p>View and manage your paper review assignments</p>
      </div>

      {/* Search Bar */}
      <div className={styles.searchBar}>
        <span className="material-symbols-rounded">search</span>
        <input
          type="text"
          placeholder="Search by paper title or code..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className={styles.searchInput}
        />
        {searchTerm && (
          <button
            className={styles.clearSearchBtn}
            onClick={() => setSearchTerm('')}
            title="Clear search"
          >
            <span className="material-symbols-rounded">close</span>
          </button>
        )}
      </div>

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
          <p>No assignments yet</p>
        </div>
      )}

      {/* Assignments List */}
      {!loading && assignments.length > 0 && (
        <>
          <div className={styles.assignmentsHeader}>
            <h2>Active Assignments</h2>
          </div>
          <div className={styles.assignmentsList}>
            {assignments.map((assignment) => (
              <AssignmentCard
                key={assignment.id}
                assignment={assignment}
                onStartReview={handleStartReview}
              />
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

export default ReviewerAssignments;
