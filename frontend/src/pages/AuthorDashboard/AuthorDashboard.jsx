import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import acsApi from '../../api/apiService.js';
import styles from './AuthorDashboard.module.css';

export const AuthorDashboard = () => {
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

      {/* Section Heading */}
      <div className={styles.sectionHeader}>
        <h2 className={styles.sectionTitle}>My Recent Submissions</h2>
        <Link to="/author/submissions" className={styles.viewAllLink}>View All</Link>
      </div>

      {/* Main Content Grid */}
      <div className={styles.dashboardGrid}>
        {/* Recent Submissions */}
        <div className={`${styles.dashboardCard} ${styles.submissionsCard}`}>
          <div className={styles.tableWrapper}>
            {recentSubmissions.length > 0 ? (
              <table className={styles.submissionsTable}>
                <thead>
                  <tr>
                    <th>Paper Title</th>
                    <th>Journal</th>
                    <th>Status</th>
                    <th>Paper ID</th>
                  </tr>
                </thead>
                <tbody>
                  {recentSubmissions.map((paper, index) => (
                    <tr key={paper.id || index}>
                      <td className={styles.titleCell}>
                        <span className={styles.paperTitle}>{paper.title || paper.name || 'Untitled Paper'}</span>
                      </td>
                      <td className={styles.journalCell}>
                        {paper.journal_name || (typeof paper.journal === 'object' ? paper.journal?.name : paper.journal) || 'No Journal'}
                      </td>
                      <td>
                        <span className={`${styles.statusBadge} ${styles[`statusBadge${getStatusColorClass(paper.status)}`]}`}>
                          {paper.status || 'Unknown'}
                        </span>
                      </td>
                      <td className={styles.idCell}>#{paper.id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className={styles.noData}>
                <span className="material-symbols-rounded">inbox</span>
                <p>No recent submissions</p>
              </div>
            )}
          </div>
        </div>
       
    
      </div>
    </div>
  );
};

export default AuthorDashboard;
