import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import acsApi from '../../api/apiService';
import Footer from '../../components/footer/Footer';
import styles from './DashboardPage.module.css';

export const DashboardPage = () => {
  const [journals, setJournals] = useState([]);

  // Default journals if API returns empty
  const defaultJournals = [
    {
      id: 1,
      name: 'Breakthrough: A Multidisciplinary Journal',
      description: 'Committed to advancing knowledge across a broad range of academic disciplines, promoting synergy between fields.',
    },
    {
      id: 2,
      name: 'Breakthrough: Journal of Energy Research',
      description: 'Focused on advancing innovative research in energy science, renewable technologies, and sustainable systems.',
    },
    {
      id: 3,
      name: 'Breakthrough: XYZ Journal',
      description: 'Dedicated to publishing peer-reviewed scholarly research across emerging and specialized interdisciplinary frontiers.',
    },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const journalsData = await acsApi.journals.listJournals(0, 3);
        setJournals(Array.isArray(journalsData) ? journalsData : []);
      } catch (err) {
        console.error('Error fetching journals:', err);
        setJournals([]);
      }
    };

    fetchData();
  }, []);

  const displayJournals = journals.length > 0 ? journals : defaultJournals;

  return (
    <div className={styles.dashboardPageWrapper}>
      <div className={styles.dashboardContainer}>
        {/* Hero Section */}
        <header className={styles.heroSection}>
          <div className={styles.heroGradient}></div>
          <div className={styles.heroCard}>
            <h2 className={styles.heroTitle}>Breakthrough Publishers India</h2>
            <p className={styles.heroDescription}>
              Committed to redefining scholarly communication by fostering high-quality, ethical, and interdisciplinary research that addresses real-world challenges. Through rigorous peer review and accessible models, we transform ideas into meaningful contributions.
            </p>
          </div>
        </header>

        {/* Journals Section */}
        <section className={styles.journalsSection}>
          <div className={styles.journalsContainer}>
            <div className={styles.journalsHeader}>
              <h2 className={styles.journalsTitle}>Our Journals</h2>
              <div className={styles.journalsUnderline}></div>
            </div>

            <div className={styles.journalsGrid}>
              {displayJournals.map((journal, index) => (
                <div key={journal.id || index} className={styles.journalCard}>
                  <h3 className={styles.journalCardTitle}>
                    {journal.name || journal.title || `Breakthrough: Journal ${index + 1}`}
                  </h3>
                  <p className={styles.journalCardDescription}>
                    {journal.description || journal.about || 'Dedicated to publishing high-quality peer-reviewed research in specialized fields.'}
                  </p>
                  <Link
                    to={`/journal/${journal.id}`}
                    className={styles.journalCardBtn}
                  >
                    View Journal
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className={styles.ctaSection}>
          <div className={styles.ctaContainer}>
            <div className={styles.ctaBlur1}></div>
            <div className={styles.ctaBlur2}></div>
            <div className={styles.ctaContent}>
              <h2 className={styles.ctaTitle}>Ready to Submit Your Manuscript?</h2>
              <p className={styles.ctaDescription}>
                Join our global research community and publish with us. We offer a streamlined submission process and expert editorial guidance.
              </p>
              <div className={styles.ctaButtons}>
                <Link to="/submit" className={styles.ctaBtnPrimary}>
                  <span className="material-icons">upload_file</span>
                  Submit Manuscript
                </Link>
                <Link to="/author-guidelines" className={styles.ctaBtnSecondary}>
                  Author Guidelines
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
};

export default DashboardPage;
