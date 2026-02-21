import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useRole } from '../../hooks/useRole';
import acsApi from '../../api/apiService.js';
import styles from './AdminDashboard.module.css';

export const AdminDashboard = () => {
  const { user } = useRole();
  const [stats, setStats] = useState({
    total_users: 0,
    total_journals: 0,
    total_submissions: 0,
    pending_papers: 0,
    published_papers: 0,
  });
  const [recentPapers, setRecentPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch dashboard stats
        const statsData = await acsApi.admin.getDashboardStats();
        setStats({
          total_users: statsData?.total_users || 0,
          total_journals: statsData?.total_journals || 0,
          total_submissions: statsData?.total_submissions || 0,
          pending_papers: statsData?.pending_papers || 0,
          published_papers: statsData?.published_papers || 0,
        });
        
        // Fetch recent papers
        try {
          const papersData = await acsApi.admin.listAllPapers(0, 5);
          const papers = papersData?.papers || papersData || [];
          setRecentPapers(Array.isArray(papers) ? papers.slice(0, 5) : []);
        } catch (paperErr) {
          console.warn('Failed to fetch papers:', paperErr);
          setRecentPapers([]);
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
    <div className={styles.adminDashboard}>
      {/* Stats Grid */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <div className={`${styles.statIcon} ${styles.statIconBlue}`}>
              <span className="material-symbols-rounded">description</span>
            </div>
            <span className={`${styles.statTrend} ${styles.statTrendUp}`}>↑ 12%</span>
          </div>
          <div className={styles.statBottom}>
            <p className={styles.statLabel}>Total Submissions</p>
            <h3 className={styles.statNumber}>{(stats.total_submissions || 0).toLocaleString()}</h3>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <div className={`${styles.statIcon} ${styles.statIconEmerald}`}>
              <span className="material-symbols-rounded">book</span>
            </div>
            <span className={`${styles.statTrend} ${styles.statTrendUp}`}>↑ 4%</span>
          </div>
          <div className={styles.statBottom}>
            <p className={styles.statLabel}>Active Journals</p>
            <h3 className={styles.statNumber}>{(stats.total_journals || 0).toLocaleString()}</h3>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <div className={`${styles.statIcon} ${styles.statIconAmber}`}>
              <span className="material-symbols-rounded">rate_review</span>
            </div>
            <span className={`${styles.statTrend} ${styles.statTrendDown}`}>↓ 2%</span>
          </div>
          <div className={styles.statBottom}>
            <p className={styles.statLabel}>Pending Reviews</p>
            <h3 className={styles.statNumber}>{(stats.pending_papers || 0).toLocaleString()}</h3>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <div className={`${styles.statIcon} ${styles.statIconPurple}`}>
              <span className="material-symbols-rounded">group</span>
            </div>
            <span className={`${styles.statTrend} ${styles.statTrendStable}`}>Stable</span>
          </div>
          <div className={styles.statBottom}>
            <p className={styles.statLabel}>Total Registered Users</p>
            <h3 className={styles.statNumber}>{(stats.total_users || 0).toLocaleString()}</h3>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className={styles.dashboardGrid}>
        {/* Recent Submissions */}
        <div className={`${styles.dashboardCard} ${styles.submissionsCard}`}>
          <div className={styles.cardHeader}>
            <h3>Recent Submissions</h3>
            <Link to="/admin/submissions" className={styles.viewAllLink}>View All</Link>
          </div>
          <div className={styles.submissionsList}>
            {recentPapers.length > 0 ? (
              recentPapers.map((paper, index) => (
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

        {/* Sidebar */}
        <div className={styles.dashboardSidebar}>
          {/* Submission Trends */}
          <div className={`${styles.dashboardCard} ${styles.trendsCard}`}>
            <h3>Submission Trends</h3>
            <div className={styles.chartPlaceholder}>
              <div className={styles.bar} style={{ height: '50%' }}></div>
              <div className={styles.bar} style={{ height: '75%' }}></div>
              <div className={`${styles.bar} ${styles.barActive}`} style={{ height: '100%' }}></div>
              <div className={styles.bar} style={{ height: '66%' }}></div>
              <div className={styles.bar} style={{ height: '80%' }}></div>
              <div className={styles.bar} style={{ height: '33%' }}></div>
            </div>
            <div className={styles.chartLabels}>
              <span>Mon</span>
              <span>Tue</span>
              <span>Wed</span>
              <span>Thu</span>
              <span>Fri</span>
              <span>Sat</span>
            </div>
          </div>

          {/* Quick Links */}
          <div className={`${styles.dashboardCard} ${styles.quickLinksCard}`}>
            <h3>Quick Links</h3>
            <div className={styles.quickLinksGrid}>
              <Link to="/admin/journals" className={styles.quickLink}>
                <span className={`material-symbols-rounded ${styles.quickLinkBlue}`}>add_circle</span>
                <span>New Journal</span>
              </Link>
              <Link to="/admin/users" className={styles.quickLink}>
                <span className={`material-symbols-rounded ${styles.quickLinkEmerald}`}>person_add</span>
                <span>Invite User</span>
              </Link>
              <Link to="/admin/settings" className={styles.quickLink}>
                <span className={`material-symbols-rounded ${styles.quickLinkAmber}`}>mail</span>
                <span>Broadcast</span>
              </Link>
              <Link to="/admin/submissions" className={styles.quickLink}>
                <span className={`material-symbols-rounded ${styles.quickLinkPurple}`}>assessment</span>
                <span>View Logs</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
