import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import acsApi from '../../api/apiService.js';
import styles from './ReviewerDashboard.module.css';

export const ReviewerDashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    total_assignments: 0,
    pending_reviews: 0,
    completed_reviews: 0,
    avg_review_time: 0,
  });
  const [recentAssignments, setRecentAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      // Only fetch if user is authenticated
      if (!isAuthenticated || !user) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        
        // Fetch dashboard stats
        const statsData = await acsApi.reviewer.getDashboardStats();
        console.log('Reviewer stats received:', statsData);
        setStats({
          total_assignments: statsData?.total_assignments || 0,
          pending_reviews: statsData?.pending_reviews || 0,
          completed_reviews: statsData?.completed_reviews || 0,
          avg_review_time: statsData?.avg_review_time || 0,
        });
        
        // Fetch recent assignments
        try {
          const assignmentsData = await acsApi.reviewer.listAssignments(0, 5);
          console.log('Assignments data received:', assignmentsData);
          const assignments = assignmentsData?.assignments || assignmentsData || [];
          setRecentAssignments(Array.isArray(assignments) ? assignments.slice(0, 5) : []);
        } catch (assignErr) {
          console.warn('Failed to fetch assignments:', assignErr);
          setRecentAssignments([]);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [isAuthenticated, user]);

  const getStatusColorClass = (status) => {
    const statusLower = status?.toLowerCase() || '';
    if (statusLower.includes('pending')) return 'Blue';
    if (statusLower.includes('progress') || statusLower.includes('in_progress')) return 'Amber';
    if (statusLower.includes('submit') || statusLower.includes('completed')) return 'Emerald';
    if (statusLower.includes('reject')) return 'Rose';
    return 'Slate';
  };

  const getStatusIcon = (status) => {
    const statusLower = status?.toLowerCase() || '';
    if (statusLower.includes('pending')) return 'schedule';
    if (statusLower.includes('progress') || statusLower.includes('in_progress')) return 'history_edu';
    if (statusLower.includes('submit') || statusLower.includes('completed')) return 'check_circle';
    if (statusLower.includes('reject')) return 'cancel';
    return 'description';
  };

  if (loading) {
    return (
      <div className={styles.dashboardLoading}>
        <span className={`material-symbols-rounded ${styles.loadingIcon}`}>hourglass_empty</span>
        <span>Loading dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.dashboardError}>
        <span className="material-symbols-rounded">error</span>
        <span>Error: {error}</span>
      </div>
    );
  }

  return (
    <div className={styles.reviewerDashboard}>
      {/* Stats Grid */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <div className={`${styles.statIcon} ${styles.statIconBlue}`}>
              <span className="material-symbols-rounded">description</span>
            </div>
            <span className={`${styles.statTrend} ${stats.total_assignments > 0 ? styles.statTrendUp : styles.statTrendStable}`}>
              {stats.total_assignments > 0 ? '↑' : '→'} {stats.total_assignments}
            </span>
          </div>
          <div className={styles.statBottom}>
            <p className={styles.statLabel}>Total Assignments</p>
            <h3 className={styles.statNumber}>{(stats.total_assignments || 0).toLocaleString()}</h3>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <div className={`${styles.statIcon} ${styles.statIconAmber}`}>
              <span className="material-symbols-rounded">rate_review</span>
            </div>
            <span className={`${styles.statTrend} ${stats.pending_reviews > 0 ? styles.statTrendDown : styles.statTrendStable}`}>
              {stats.pending_reviews > 0 ? '↓' : '→'} {stats.pending_reviews}
            </span>
          </div>
          <div className={styles.statBottom}>
            <p className={styles.statLabel}>Pending Reviews</p>
            <h3 className={styles.statNumber}>{(stats.pending_reviews || 0).toLocaleString()}</h3>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <div className={`${styles.statIcon} ${styles.statIconEmerald}`}>
              <span className="material-symbols-rounded">check_circle</span>
            </div>
            <span className={`${styles.statTrend} ${styles.statTrendUp}`}>↑ {stats.completed_reviews}</span>
          </div>
          <div className={styles.statBottom}>
            <p className={styles.statLabel}>Completed Reviews</p>
            <h3 className={styles.statNumber}>{(stats.completed_reviews || 0).toLocaleString()}</h3>
          </div>
        </div>


      </div>

      {/* Recent Assignments */}
      <div className={styles.dashboardCard}>
        <div className={styles.cardHeader}>
          <h3>Recent Assignments</h3>
          <Link to="/reviewer/assignments" className={styles.viewAllLink}>
            View All
          </Link>
        </div>

        <div className={styles.assignmentsList}>
          {recentAssignments.length === 0 ? (
            <div className={styles.emptyState}>
              <span className="material-symbols-rounded">inbox</span>
              <p>No assignments yet</p>
            </div>
          ) : (
            recentAssignments.map((assignment) => (
              <div key={assignment.id} className={styles.assignmentItem}>
                <div className={styles.assignmentContent}>
                  <div className={styles.assignmentInfo}>
                    <h4 className={styles.assignmentTitle}>{assignment.paper_title}</h4>
                    <p className={styles.assignmentDate}>
                      <span className="material-symbols-rounded">calendar_today</span>
                      Due: {new Date(assignment.due_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className={styles.assignmentActions}>
                  <span className={`${styles.statusBadge} ${styles[`status${getStatusColorClass(assignment.status)}`]}`}>
                    {assignment.status}
                  </span>
                  <button
                    className={styles.startReviewBtn}
                    onClick={() => {
                      navigate(`/reviewer/assignments/${assignment.id}/review`);
                    }}
                    title="Start Review"
                  >
                    <span className="material-symbols-rounded">chevron_right</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default ReviewerDashboard;
