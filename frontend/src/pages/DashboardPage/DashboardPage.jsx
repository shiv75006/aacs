import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import acsApi from '../../api/apiService';
import './DashboardPage.css';
import Footer from '../../components/footer/Footer';

// Utility function to strip HTML tags
const stripHtmlTags = (html) => {
  if (!html) return '';
  return html.replace(/<[^>]*>/g, '').trim();
};

export const DashboardPage = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [journals, setJournals] = useState([]);
  const [news, setNews] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  const featuredJournal = {
    title: 'International Transactions in Applied Sciences',
    description: 'The International Transactions in Applied Sciences (ITAS) is an international research journal, which publishes top-level work on applied sciences. The Journal ITAS is a direct successor of the Journal ITMSC with the aim of publishing papers in all areas of the applied science...',
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        try {
          const journalsData = await acsApi.journals.listJournals(0, 3);
          setJournals(Array.isArray(journalsData) ? journalsData : []);
        } catch (err) {
          console.error('Error fetching journals:', err);
          setJournals([]);
        }

        try {
          const articlesData = await acsApi.articles.latest(4);
          setNews(Array.isArray(articlesData) ? articlesData : []);
        } catch (err) {
          console.error('Error fetching articles:', err);
          setNews([]);
        }

        setAnnouncements([
          {
            id: 1,
            title: 'AACS Journal Rankings Updated',
            date: '2024-02-12',
            type: 'Update',
            typeColor: 'blue',
          },
          {
            id: 2,
            title: 'New Editorial Board Members',
            date: '2024-02-09',
            type: 'Staff',
            typeColor: 'gray',
          },
          {
            id: 3,
            title: 'Call for Special Issues',
            date: '2024-02-06',
            type: 'Call for Papers',
            typeColor: 'red',
          },
          {
            id: 4,
            title: 'Conference Announcements',
            date: '2024-02-04',
            type: 'Event',
            typeColor: 'green',
          },
        ]);

        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className={`${isDarkMode ? 'dark' : ''} dashboard-page-wrapper`}>
      <div className="dashboard-container">
        <main className="dashboard-main">
          {/* Featured Journal Section */}
          <section className="dashboard-section">
            <div className="featured-journal">
              {/* Content */}
              <div className="featured-content">
                <div className="featured-badge">
                  <span>Featured Journal</span>
                </div>
                <h2 className="featured-title">{featuredJournal.title}</h2>
                <p className="featured-description">
                  {featuredJournal.description}
                  <Link to="/journals" className="featured-description-link">
                    Read more
                  </Link>
                </p>
                <div className="featured-buttons">
                  <Link to="/journals" className="btn-primary">View Journal</Link>
                  <Link to="/journals" className="btn-secondary">Editorial Board</Link>
                </div>
              </div>

              {/* Illustration */}
              <div className="featured-illustration">
                <div className="featured-logo">
                  <div className="featured-logo-text">
                    it<span className="featured-logo-highlight">a</span>s
                  </div>
                  <div style={{ height: '0.5rem', width: '100%', backgroundColor: '#1f2937', marginTop: '0.5rem' }}></div>
                  <div style={{ height: '0.5rem', width: '66%', backgroundColor: '#f97316', marginTop: '0.25rem' }}></div>
                </div>
                <div className="featured-decoration featured-decoration-blur"></div>
                <div className="featured-decoration featured-decoration-secondary"></div>
              </div>
            </div>
          </section>

          {/* Journals Section */}
          <section className="dashboard-section">
            <div className="section-header">
              <div>
                <h2 className="section-title">Explore Our Journals</h2>
                <p className="section-subtitle">Specialized publications for advancement in various fields</p>
              </div>
              <Link to="/journals" className="section-link">
                <span>View All Journals</span>
                <span className="material-icons section-link-icon">arrow_forward</span>
              </Link>
            </div>

            <div className="journals-grid">
              {journals.length > 0 ? (
                journals.map((journal) => (
                  <div key={journal.id} className="journal-card">
                    <h3 className="journal-card-title">
                      {journal.name || journal.title || 'Untitled'}
                    </h3>
                    <div className="journal-card-info">
                      <div className="journal-card-row">
                        <span className="journal-card-label">Chief Editor</span>
                        <span className="journal-card-value">{journal.chief_editor || 'NA'}</span>
                      </div>
                      <div className="journal-card-row">
                        <span className="journal-card-label">ISSN Online</span>
                        <span className="journal-card-value">{journal.issn_online || 'Still Waiting'}</span>
                      </div>
                      <div className="journal-card-row">
                        <span className="journal-card-label">ISSN Print</span>
                        <span className="journal-card-value">{journal.issn_print || '-'}</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state" style={{ gridColumn: '1 / -1' }}>
                  <p>Loading journals...</p>
                </div>
              )}
            </div>
          </section>

          {/* Articles and Announcements Section */}
          <section className="dashboard-section" style={{ marginBottom: '5rem' }}>
            <div className="articles-announcements">
              {/* Articles */}
              <div className="article-section">
                <div className="article-header">
                  <div className="article-icon">
                    <span className="material-icons">description</span>
                  </div>
                  <h2 className="article-title">Latest Articles</h2>
                </div>
                <div className="article-container">
                  <div className="article-list">
                    {news.length > 0 ? (
                      news.map((article) => (
                        <div key={article.id} className="article-item">
                          <h4 className="article-item-title">
                            {stripHtmlTags(article.title) || 'Untitled Article'}
                          </h4>
                          <div className="article-meta">
                            <span className="article-date">
                              {article.date ? new Date(article.date).toLocaleDateString() : 'Unpublished'}
                            </span>
                            <span className="article-dot"></span>
                            <span className="article-author">{stripHtmlTags(article.author) || 'AACS'}</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="empty-state">
                        <p>No articles yet</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Announcements */}
              <div className="announcement-section">
                <div className="announcement-header">
                  <div className="announcement-icon">
                    <span className="material-icons">campaign</span>
                  </div>
                  <h2 className="announcement-title">Announcements</h2>
                </div>
                <div className="announcement-container">
                  <div className="announcement-list">
                    {announcements.length > 0 ? (
                      announcements.map((announcement) => {
                        const badgeClass = `announcement-badge badge-${announcement.typeColor}`;
                        return (
                          <div key={announcement.id} className="announcement-item">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                              <h4 className="announcement-item-title" style={{ flex: 1 }}>
                                {announcement.title}
                              </h4>
                              <span className={badgeClass}>
                                {announcement.type}
                              </span>
                            </div>
                            <span className="announcement-date" style={{ display: 'block', marginTop: '0.5rem' }}>
                              {announcement.date}
                            </span>
                          </div>
                        );
                      })
                    ) : (
                      <div className="empty-state">
                        <p>No announcements yet</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>
         <Footer />
      </div>
    </div>
  );
};
