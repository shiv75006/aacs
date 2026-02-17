import React from 'react';
import styles from './PaperViewer.module.css';

const PaperViewer = ({ paper, reviewId }) => {
  if (!paper) {
    return (
      <div className={styles.paperViewer}>
        <div className={styles.noContent}>
          <span className="material-symbols-rounded">description</span>
          <p>No paper information available</p>
        </div>
      </div>
    );
  }

  const handleViewPaper = () => {
    // Get token from localStorage for authentication
    const token = localStorage.getItem('authToken');
    if (reviewId && token) {
      // Open the paper in a new browser tab using the reviewer view endpoint
      const viewUrl = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/reviewer/assignments/${reviewId}/view-paper?token=${token}`;
      window.open(viewUrl, '_blank');
    } else if (!token) {
      alert('Please log in to view the paper');
    }
  };

  return (
    <div className={styles.paperViewer}>
      {/* Paper Header */}
      <div className={styles.paperHeader}>
        <h2 className={styles.title}>{paper.title || 'Untitled Paper'}</h2>
        <div className={styles.metadata}>
          <div className={styles.metaItem}>
            <span className="material-symbols-rounded">person</span>
            <div>
              <p className={styles.metaLabel}>Author</p>
              <p className={styles.metaValue}>{paper.author?.name || 'Unknown'}</p>
            </div>
          </div>
          <div className={styles.metaItem}>
            <span className="material-symbols-rounded">mail</span>
            <div>
              <p className={styles.metaLabel}>Email</p>
              <p className={styles.metaValue}>{paper.author?.email || 'N/A'}</p>
            </div>
          </div>
          <div className={styles.metaItem}>
            <span className="material-symbols-rounded">location_city</span>
            <div>
              <p className={styles.metaLabel}>Affiliation</p>
              <p className={styles.metaValue}>{paper.author?.affiliation || 'N/A'}</p>
            </div>
          </div>
        </div>

        {reviewId && (
          <button className={styles.downloadBtn} onClick={handleViewPaper} title="View paper in new tab">
            <span className="material-symbols-rounded">open_in_new</span>
            View Paper
          </button>
        )}
      </div>

      {/* Paper Content */}
      <div className={styles.paperContent}>
        {/* Abstract */}
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>Abstract</h3>
          <p className={styles.sectionContent}>
            {paper.abstract || 'No abstract provided'}
          </p>
        </section>

        {/* Keywords */}
        {paper.keywords && (
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Keywords</h3>
            <div className={styles.keywords}>
              {paper.keywords.split(',').map((keyword, idx) => (
                <span key={idx} className={styles.keyword}>
                  {keyword.trim()}
                </span>
              ))}
            </div>
          </section>
        )}

        {/* Journal */}
        {paper.journal && (
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Journal</h3>
            <p className={styles.sectionContent}>{typeof paper.journal === 'object' ? paper.journal?.name : paper.journal}</p>
          </section>
        )}

        {/* Submitted Date */}
        {paper.submitted_date && (
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Submitted</h3>
            <p className={styles.sectionContent}>
              {new Date(paper.submitted_date).toLocaleDateString()}
            </p>
          </section>
        )}
      </div>
    </div>
  );
};

export default PaperViewer;
