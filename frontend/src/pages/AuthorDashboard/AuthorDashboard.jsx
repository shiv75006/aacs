import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useRole } from '../../hooks/useRole';
import { useAuth } from '../../hooks/useAuth';
import DashboardSidebar from '../../components/shared/DashboardSidebar';
import RequestAccessModal from '../../components/RequestAccessModal';
import acsApi from '../../api/apiService.js';
import styles from './AuthorDashboard.module.css';

export const AuthorDashboard = () => {
  const { user } = useRole();
  const { availableRoles } = useAuth();
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [stats, setStats] = useState({
    total_submissions: 0,
    accepted_papers: 0,
    rejected_papers: 0,
    under_review: 0,
  });
  const [recentSubmissions, setRecentSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch dashboard stats
        const statsData = await acsApi.author.getDashboardStats();
        console.log('Dashboard stats received:', statsData);
        setStats({
          total_submissions: statsData?.total_submissions || 0,
          accepted_papers: statsData?.accepted_papers || 0,
          rejected_papers: statsData?.rejected_papers || 0,
          under_review: statsData?.under_review || 0,
        });
        
        // Fetch recent submissions
        try {
          const submissionsData = await acsApi.author.listSubmissions(0, 5);
          console.log('Submissions data received:', submissionsData);
          const papers = submissionsData?.papers || submissionsData || [];
          setRecentSubmissions(Array.isArray(papers) ? papers.slice(0, 5) : []);
        } catch (paperErr) {
          console.warn('Failed to fetch submissions:', paperErr);
          setRecentSubmissions([]);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const getStatusColorClass = (status) => {
    const statusLower = status?.toLowerCase() || '';
    if (statusLower.includes('submit')) return 'Blue';
    if (statusLower.includes('review')) return 'Amber';
    if (statusLower.includes('accept') || statusLower.includes('publish')) return 'Emerald';
    if (statusLower.includes('reject')) return 'Rose';
    return 'Slate';
  };

  const getStatusIcon = (status) => {
    const statusLower = status?.toLowerCase() || '';
    if (statusLower.includes('submit')) return 'article';
    if (statusLower.includes('review')) return 'history_edu';
    if (statusLower.includes('accept') || statusLower.includes('publish')) return 'check_circle';
    if (statusLower.includes('reject')) return 'cancel';
    return 'description';
  };

  if (loading) {
    return (
      <div className={styles.dashboardLoading}>
        <span className={`material-symbols-rounded ${styles.loadingIcon}`}>clock_loader_20</span>
        <span>Loading</span>
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
    <div className={styles.authorDashboard}>
      {/* Stats Grid */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <div className={`${styles.statIcon} ${styles.statIconBlue}`}>
              <span className="material-symbols-rounded">description</span>
            </div>
            <span className={`${styles.statTrend} ${styles.statTrendUp}`}>↑ 8%</span>
          </div>
          <div className={styles.statBottom}>
            <p className={styles.statLabel}>Total Submissions</p>
            <h3 className={styles.statNumber}>{(stats.total_submissions || 0).toLocaleString()}</h3>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <div className={`${styles.statIcon} ${styles.statIconEmerald}`}>
              <span className="material-symbols-rounded">check_circle</span>
            </div>
            <span className={`${styles.statTrend} ${styles.statTrendUp}`}>↑ 3%</span>
          </div>
          <div className={styles.statBottom}>
            <p className={styles.statLabel}>Accepted Papers</p>
            <h3 className={styles.statNumber}>{(stats.accepted_papers || 0).toLocaleString()}</h3>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <div className={`${styles.statIcon} ${styles.statIconAmber}`}>
              <span className="material-symbols-rounded">history_edu</span>
            </div>
            <span className={`${styles.statTrend} ${styles.statTrendUp}`}>↑ 5%</span>
          </div>
          <div className={styles.statBottom}>
            <p className={styles.statLabel}>Under Review</p>
            <h3 className={styles.statNumber}>{(stats.under_review || 0).toLocaleString()}</h3>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <div className={`${styles.statIcon} ${styles.statIconRose}`}>
              <span className="material-symbols-rounded">cancel</span>
            </div>
            <span className={`${styles.statTrend} ${styles.statTrendDown}`}>↓ 1%</span>
          </div>
          <div className={styles.statBottom}>
            <p className={styles.statLabel}>Rejected Papers</p>
            <h3 className={styles.statNumber}>{(stats.rejected_papers || 0).toLocaleString()}</h3>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className={styles.dashboardGrid}>
        {/* Recent Submissions */}
        <div className={`${styles.dashboardCard} ${styles.submissionsCard}`}>
          <div className={styles.cardHeader}>
            <h3>My Recent Submissions</h3>
            <Link to="/author/submissions" className={styles.viewAllLink}>View All</Link>
          </div>
          <div className={styles.submissionsList}>
            {recentSubmissions.length > 0 ? (
              recentSubmissions.map((paper, index) => (
                <div key={paper.id || index} className={styles.submissionItem}>
                  <div className={styles.submissionContent}>
                    <div className={`${styles.submissionIcon} ${styles[`submissionIcon${getStatusColorClass(paper.status)}`]}`}>
                      <span className="material-symbols-rounded">{getStatusIcon(paper.status)}</span>
                    </div>
                    <div className={styles.submissionDetails}>
                      <h4>{paper.title || paper.name || 'Untitled Paper'}</h4>
                      <div className={styles.submissionMeta}>
                        <span className={`${styles.statusBadge} ${styles[`statusBadge${getStatusColorClass(paper.status)}`]}`}>
                          {paper.status || 'Unknown'}
                        </span>
                        <span className={styles.paperInfo}>
                          ID: {paper.id} • 
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', marginLeft: '4px' }}>
                            <span className="material-symbols-rounded" style={{ fontSize: '16px' }}>newspaper</span>
                            {paper.journal_name || (typeof paper.journal === 'object' ? paper.journal?.name : paper.journal) || 'No Journal'}
                          </span>
                        </span>
                      </div>
                    </div>
                  </div>
                  <button className={styles.moreBtn}>
                    <span className="material-symbols-rounded">more_vert</span>
                  </button>
                </div>
              ))
            ) : (
              <div className={styles.noData}>
                <span className="material-symbols-rounded">inbox</span>
                <p>No recent submissions</p>
              </div>
            )}
          </div>
        </div>
       
    
      </div>

      {/* Request Access Section - Always show so users can check status */}
      <div className={styles.requestAccessSection}>
        <button 
          className={styles.requestAccessBtn}
          onClick={() => setShowRequestModal(true)}
        >
          <span className="material-symbols-rounded">add_moderator</span>
          Request Additional Role Access
        </button>
      </div>

      {/* Request Access Modal */}
      <RequestAccessModal
        isOpen={showRequestModal}
        onClose={() => setShowRequestModal(false)}
      />
    </div>
  );
};

export default AuthorDashboard;
