import React from 'react';
import styles from './ReviewerGuidelines.module.css';

const ReviewerGuidelines = () => {
  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <h1>Reviewer Guidelines</h1>
        <p>Everything you need to know about the review process</p>
      </header>

      {/* Quick Stats */}
      <div className={styles.statsBar}>
        <div className={styles.stat}>
          <span className={styles.statValue}>14</span>
          <span className={styles.statLabel}>days to review</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statValue}>4</span>
          <span className={styles.statLabel}>rating criteria</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statValue}>24h</span>
          <span className={styles.statLabel}>support response</span>
        </div>
      </div>

      {/* Review Process */}
      <section className={styles.section}>
        <h2>Review Process</h2>
        <div className={styles.steps}>
          <div className={styles.step}>
            <span className={styles.stepNum}>1</span>
            <div>
              <h3>Receive & Accept</h3>
              <p>Review the paper abstract and confirm your expertise matches the topic</p>
            </div>
          </div>
          <div className={styles.step}>
            <span className={styles.stepNum}>2</span>
            <div>
              <h3>Read & Evaluate</h3>
              <p>Download the manuscript and assess quality, methodology, and originality</p>
            </div>
          </div>
          <div className={styles.step}>
            <span className={styles.stepNum}>3</span>
            <div>
              <h3>Rate & Comment</h3>
              <p>Provide ratings and constructive feedback for authors and editors</p>
            </div>
          </div>
          <div className={styles.step}>
            <span className={styles.stepNum}>4</span>
            <div>
              <h3>Submit Decision</h3>
              <p>Recommend: Accept, Minor Revisions, Major Revisions, or Reject</p>
            </div>
          </div>
        </div>
      </section>

      {/* Ethics & Confidentiality */}
      <section className={styles.section}>
        <h2>Ethics & Confidentiality</h2>
        <ul className={styles.list}>
          <li>
            <span className="material-symbols-rounded">lock</span>
            Keep all manuscript content strictly confidential
          </li>
          <li>
            <span className="material-symbols-rounded">verified</span>
            Disclose any conflicts of interest immediately
          </li>
          <li>
            <span className="material-symbols-rounded">balance</span>
            Provide objective, unbiased assessments
          </li>
          <li>
            <span className="material-symbols-rounded">edit_note</span>
            Be constructive and professional in feedback
          </li>
          <li>
            <span className="material-symbols-rounded">delete</span>
            Securely dispose of manuscripts after publication
          </li>
        </ul>
      </section>

      {/* Best Practices */}
      <section className={styles.section}>
        <h2>Best Practices</h2>
        <div className={styles.practicesGrid}>
          <div className={styles.practice}>
            <span className="material-symbols-rounded">schedule</span>
            <h4>Be Timely</h4>
            <p>Submit reviews within the 14-day deadline. Request extensions early if needed.</p>
          </div>
          <div className={styles.practice}>
            <span className="material-symbols-rounded">psychology</span>
            <h4>Be Thorough</h4>
            <p>Read the paper at least twice. Note both major issues and minor suggestions.</p>
          </div>
          <div className={styles.practice}>
            <span className="material-symbols-rounded">lightbulb</span>
            <h4>Be Constructive</h4>
            <p>Offer specific feedback that helps authors improve their work.</p>
          </div>
          <div className={styles.practice}>
            <span className="material-symbols-rounded">handshake</span>
            <h4>Be Fair</h4>
            <p>Evaluate based on scientific merit, not personal preferences.</p>
          </div>
        </div>
      </section>

      {/* Contact */}
      <section className={styles.contact}>
        <span className="material-symbols-rounded">mail</span>
        <div>
          <h3>Need Help?</h3>
          <p>Contact the editorial office at <a href="mailto:editor@breakthroughpublishers.com">editor@breakthroughpublishers.com</a></p>
        </div>
      </section>
    </div>
  );
};

export default ReviewerGuidelines;
