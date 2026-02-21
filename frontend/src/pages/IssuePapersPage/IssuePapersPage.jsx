import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { acsApi, apiService } from '../../api/apiService';
import Breadcrumbs from '../../components/breadcrumbs/Breadcrumbs';
import './IssuePapersPage.css';

const IssuePapersPage = () => {
  const { id: journalId, volumeNo, issueNo } = useParams();
  const navigate = useNavigate();
  
  const [journal, setJournal] = useState(null);
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch journal details
      const journalData = await acsApi.journals.getDetail(journalId);
      setJournal(journalData);

      // Fetch papers for this issue - using correct API path
      const papersResponse = await apiService.get(
        `/api/v1/journals/${journalId}/issues/${volumeNo}/${issueNo}/papers`
      );
      setPapers(papersResponse.papers || []);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load issue papers');
    } finally {
      setLoading(false);
    }
  }, [journalId, volumeNo, issueNo]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <div className="issue-papers-page">
        <div className="issue-papers-loading">
          <div className="spinner"></div>
          <p>Loading papers...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="issue-papers-page">
        <div className="issue-papers-error">
          <p>{error}</p>
          <button className="btn-back" onClick={() => navigate(`/journal/${journalId}`)}>
            Back to Journal
          </button>
        </div>
      </div>
    );
  }

  const breadcrumbItems = [
    { label: 'Home', path: '/' },
    { label: 'Journals', path: '/journals' },
    { label: journal?.name || 'Journal', path: `/journal/${journalId}` },
    { label: `Vol. ${volumeNo}, Issue ${issueNo}`, path: `/journal/${journalId}/volume/${volumeNo}/issue/${issueNo}` },
  ];

  return (
    <div className="issue-papers-page">
      <Breadcrumbs items={breadcrumbItems} />

      {/* Header */}
      <div className="issue-papers-header">
        <div className="issue-papers-header-content">
          <h1>{journal?.name}</h1>
          <div className="issue-info">
            <span className="volume-badge">Volume {volumeNo}</span>
            <span className="issue-badge">Issue {issueNo}</span>
          </div>
        </div>
      </div>

      {/* Papers List */}
      <div className="issue-papers-container">
        <div className="issue-papers-main">
          <div className="papers-header">
            <h2>Published Papers</h2>
            <span className="papers-count">{papers.length} {papers.length === 1 ? 'Paper' : 'Papers'}</span>
          </div>

          {papers.length === 0 ? (
            <div className="no-papers">
              <span className="material-symbols-rounded">article</span>
              <p>No papers published in this issue yet.</p>
            </div>
          ) : (
            <div className="papers-list">
              {papers.map((paper, index) => (
                <Link 
                  key={paper.id} 
                  to={`/article/${paper.id}`}
                  className="paper-card"
                >
                  <div className="paper-number">{index + 1}</div>
                  <div className="paper-content">
                    <h3 className="paper-title">{paper.title}</h3>
                    <div className="paper-authors">
                      <span className="material-symbols-rounded">person</span>
                      {paper.author || paper.authors}
                    </div>
                    {paper.abstract && (
                      <p className="paper-abstract">
                        {paper.abstract.length > 250 
                          ? paper.abstract.substring(0, 250) + '...' 
                          : paper.abstract}
                      </p>
                    )}
                    <div className="paper-meta">
                      {paper.pages && (
                        <span className="paper-pages">
                          <span className="material-symbols-rounded">menu_book</span>
                          Pages: {paper.pages}
                        </span>
                      )}
                      {paper.doi && (
                        <span className="paper-doi">
                          <span className="material-symbols-rounded">link</span>
                          DOI: {paper.doi}
                        </span>
                      )}
                      {paper.published_date && (
                        <span className="paper-date">
                          <span className="material-symbols-rounded">calendar_today</span>
                          {new Date(paper.published_date).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="paper-arrow">
                    <span className="material-symbols-rounded">chevron_right</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IssuePapersPage;
