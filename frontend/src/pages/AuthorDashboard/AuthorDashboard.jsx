import React, { useEffect, useState } from 'react';
import { useRole } from '../../hooks/useRole';
import acsApi from '../../api/apiService.js';
import './AuthorDashboard.css';

export const AuthorDashboard = () => {
  const { user } = useRole();
  const [stats, setStats] = useState({
    totalSubmissions: 0,
    acceptedPapers: 0,
    rejectedPapers: 0,
    underReview: 0,
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
        setStats(statsData);
        
        // Fetch recent submissions
        const submissionsData = await acsApi.author.listSubmissions(0, 3);
        setRecentSubmissions(submissionsData.papers || []);
        
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const getStatusBadge = (status) => {
    const statusMap = {
      under_review: { class: 'badge-review', label: 'Under Review' },
      accepted: { class: 'badge-accepted', label: 'Accepted' },
      rejected: { class: 'badge-rejected', label: 'Rejected' },
      draft: { class: 'badge-draft', label: 'Draft' },
    };
    return statusMap[status] || statusMap.draft;
  };

  if (loading) {
    return <div className="dashboard-loading">Loading your dashboard...</div>;
  }

  if (error) {
    return <div className="dashboard-error">Error: {error}</div>;
  }

  return (
    <div className="author-dashboard">
      <div className="dashboard-header">
        <h1>My Dashboard</h1>
        <p>Welcome, {user?.email}. Manage your paper submissions here.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon submissions-icon">📄</div>
          <div className="stat-content">
            <h3>Total Submissions</h3>
            <p className="stat-number">{stats.totalSubmissions}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon accepted-icon">✓</div>
          <div className="stat-content">
            <h3>Accepted</h3>
            <p className="stat-number">{stats.acceptedPapers}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon rejected-icon">✕</div>
          <div className="stat-content">
            <h3>Rejected</h3>
            <p className="stat-number">{stats.rejectedPapers}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon review-icon">⏳</div>
          <div className="stat-content">
            <h3>Under Review</h3>
            <p className="stat-number">{stats.underReview}</p>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <section className="submissions-section">
          <div className="section-header">
            <h2>Recent Submissions</h2>
            <button className="btn-primary">+ Submit New Paper</button>
          </div>

          <div className="submissions-table">
            <table>
              <thead>
                <tr>
                  <th>Paper Title</th>
                  <th>Journal</th>
                  <th>Submitted Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentSubmissions.map((submission) => {
                  const badge = getStatusBadge(submission.status);
                  return (
                    <tr key={submission.id}>
                      <td className="title">{submission.title}</td>
                      <td>{submission.journal}</td>
                      <td>{submission.submitted_date ? new Date(submission.submitted_date).toLocaleDateString() : 'N/A'}</td>
                      <td>
                        <span className={`badge ${badge.class}`}>{badge.label}</span>
                      </td>
                      <td className="actions">
                        <button className="btn-small view-btn">View</button>
                        <button className="btn-small edit-btn">Edit</button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        <section className="info-section">
          <h2>Quick Tips</h2>
          <div className="tips-list">
            <div className="tip-item">
              <span className="tip-icon">📋</span>
              <p><strong>Before Submitting:</strong> Ensure your paper meets the journal's formatting guidelines.</p>
            </div>
            <div className="tip-item">
              <span className="tip-icon">✉️</span>
              <p><strong>Notifications:</strong> You'll receive email updates about your paper status.</p>
            </div>
            <div className="tip-item">
              <span className="tip-icon">🔍</span>
              <p><strong>Review Process:</strong> Papers typically take 2-4 weeks for initial review.</p>
            </div>
            <div className="tip-item">
              <span className="tip-icon">💬</span>
              <p><strong>Questions?</strong> Contact the journal editors for support.</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default AuthorDashboard;
