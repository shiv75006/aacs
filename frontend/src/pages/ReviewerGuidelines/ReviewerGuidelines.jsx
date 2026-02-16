import React, { useState } from 'react';
import styles from './ReviewerGuidelines.module.css';

const ReviewerGuidelines = () => {
  const [activeTab, setActiveTab] = useState('process');

  const tabs = [
    { id: 'process', label: 'Review Process' },
    { id: 'timeline', label: 'Timeline' },
    { id: 'confidentiality', label: 'Confidentiality' },
    { id: 'communication', label: 'Communication' },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Reviewer Guidelines</h1>
        <p>Learn about our review process, expectations, and best practices</p>
      </div>

      {/* Tab Navigation */}
      <div className={styles.tabNav}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`${styles.tabBtn} ${activeTab === tab.id ? styles.active : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className={styles.tabContent}>
        {/* Review Process Tab */}
        {activeTab === 'process' && (
          <div className={styles.tabPane}>
            <h2>Review Process</h2>
            <div className={styles.processFlow}>
              <div className={styles.step}>
                <div className={`${styles.stepNumber} ${styles.step1}`}>1</div>
                <div className={styles.stepContent}>
                  <h3>Receive Assignment</h3>
                  <p>You will receive an email invitation with the paper details, abstract, and keywords. Review these to confirm your expertise aligns with the paper's scope.</p>
                </div>
              </div>

              <div className={styles.connector}></div>

              <div className={styles.step}>
                <div className={`${styles.stepNumber} ${styles.step2}`}>2</div>
                <div className={styles.stepContent}>
                  <h3>Download & Read Paper</h3>
                  <p>Log into your reviewer account, access the paper file, and thoroughly read the manuscript. Take notes on major and minor issues.</p>
                </div>
              </div>

              <div className={styles.connector}></div>

              <div className={styles.step}>
                <div className={`${styles.stepNumber} ${styles.step3}`}>3</div>
                <div className={styles.stepContent}>
                  <h3>Provide Ratings & Comments</h3>
                  <p>Rate the paper across multiple criteria (technical quality, clarity, originality, significance). Provide constructive comments for both authors and editors.</p>
                </div>
              </div>

              <div className={styles.connector}></div>

              <div className={styles.step}>
                <div className={`${styles.stepNumber} ${styles.step4}`}>4</div>
                <div className={styles.stepContent}>
                  <h3>Submit Recommendation</h3>
                  <p>Choose from: Accept, Minor Revisions, Major Revisions, or Reject. Your recommendation will help editors make final decisions.</p>
                </div>
              </div>

              <div className={styles.connector}></div>

              <div className={styles.step}>
                <div className={`${styles.stepNumber} ${styles.step5}`}>5</div>
                <div className={styles.stepContent}>
                  <h3>Submit Review</h3>
                  <p>Complete your review and submit through the portal. The editor will use your feedback for the final decision.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Timeline Tab */}
        {activeTab === 'timeline' && (
          <div className={styles.tabPane}>
            <h2>Timeline & Deadlines</h2>
            <p className={styles.introduction}>
              We understand your time is valuable. Here's what you can expect at each stage:
            </p>

            <div className={styles.timelineCards}>
              <div className={styles.timelineCard}>
                <div className={styles.timelineIcon}>
                  <span className="material-symbols-rounded">mail_notification</span>
                </div>
                <h3>Day 1: Invitation</h3>
                <p>Receive email with paper details and 14-day review deadline.</p>
              </div>

              <div className={styles.timelineCard}>
                <div className={styles.timelineIcon}>
                  <span className="material-symbols-rounded">download</span>
                </div>
                <h3>Day 2-3: Paper Access</h3>
                <p>Download and start reading the paper. Initial impressions and major issues emerge.</p>
              </div>

              <div className={styles.timelineCard}>
                <div className={styles.timelineIcon}>
                  <span className="material-symbols-rounded">schedule</span>
                </div>
                <h3>Day 4-12: Detailed Review</h3>
                <p>Conduct thorough review, make detailed notes, rate criteria, and prepare comments.</p>
              </div>

              <div className={styles.timelineCard}>
                <div className={styles.timelineIcon}>
                  <span className="material-symbols-rounded">send</span>
                </div>
                <h3>Day 13-14: Submit Review</h3>
                <p>Complete and submit your review. Reminder emails sent 48 hours before deadline.</p>
              </div>
            </div>

            <div className={styles.deadlineInfo}>
              <span className="material-symbols-rounded">info</span>
              <div>
                <h4>Standard Review Period</h4>
                <p>Most papers have a 14-day review period. Some high-priority papers may have shorter deadlines (7-10 days). Check your invitation for specific dates.</p>
              </div>
            </div>
          </div>
        )}

        {/* Confidentiality Tab */}
        {activeTab === 'confidentiality' && (
          <div className={styles.tabPane}>
            <h2>Confidentiality & Ethics</h2>
            <p className={styles.introduction}>
              As a reviewer, you play a crucial role in maintaining the integrity of the peer review process.
            </p>

            <div className={styles.guidelinesList}>
              <div className={styles.guidelineItem}>
                <div className={styles.guidelineIcon}>
                  <span className="material-symbols-rounded">lock</span>
                </div>
                <div className={styles.guidelineContent}>
                  <h3>Maintain Confidentiality</h3>
                  <p>Do not share the paper, your review, or author information with anyone outside the editorial process. Treat the manuscript as confidential until published.</p>
                </div>
              </div>

              <div className={styles.guidelineItem}>
                <div className={styles.guidelineIcon}>
                  <span className="material-symbols-rounded">verified</span>
                </div>
                <div className={styles.guidelineContent}>
                  <h3>Disclose Conflicts of Interest</h3>
                  <p>If you have a conflict of interest with the author(s) or institution, inform the editor immediately. We will reassign the paper to another reviewer.</p>
                </div>
              </div>

              <div className={styles.guidelineItem}>
                <div className={styles.guidelineIcon}>
                  <span className="material-symbols-rounded">rule</span>
                </div>
                <div className={styles.guidelineContent}>
                  <h3>Fair & Objective Assessment</h3>
                  <p>Base your review solely on the scientific merit of the work. Avoid personal bias and ensure your recommendations are well-supported by evidence from the paper.</p>
                </div>
              </div>

              <div className={styles.guidelineItem}>
                <div className={styles.guidelineIcon}>
                  <span className="material-symbols-rounded">comment</span>
                </div>
                <div className={styles.guidelineContent}>
                  <h3>Separate Comments</h3>
                  <p>Use author-visible comments for constructive feedback. Use confidential comments for suggestions to the editor only, such as concerns about ethics or methodology.</p>
                </div>
              </div>

              <div className={styles.guidelineItem}>
                <div className={styles.guidelineIcon}>
                  <span className="material-symbols-rounded">mood</span>
                </div>
                <div className={styles.guidelineContent}>
                  <h3>Professional Tone</h3>
                  <p>Maintain a professional, constructive tone in your review. Criticism should be specific and helpful, not personal or dismissive.</p>
                </div>
              </div>

              <div className={styles.guidelineItem}>
                <div className={styles.guidelineIcon}>
                  <span className="material-symbols-rounded">delete</span>
                </div>
                <div className={styles.guidelineContent}>
                  <h3>Dispose Securely</h3>
                  <p>After publication, securely delete any copies of the manuscript and your review notes. Do not retain copies for personal archives.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Communication Tab */}
        {activeTab === 'communication' && (
          <div className={styles.tabPane}>
            <h2>Communication & Support</h2>
            <p className={styles.introduction}>
              We're here to support you throughout the review process.
            </p>

            <div className={styles.communicationCards}>
              <div className={styles.commCard}>
                <h3>Need Help?</h3>
                <p>If you have questions about a paper or need technical assistance, please contact the managing editor:</p>
                <p className={styles.contact}>
                  <strong>Email:</strong> editor@aacsjournals.com<br />
                  <strong>Response time:</strong> Within 24 hours
                </p>
              </div>

              <div className={styles.commCard}>
                <h3>Cannot Complete Review?</h3>
                <p>If you need to decline the review or request an extension, notify us as soon as possible. We will find a replacement reviewer promptly.</p>
                <p className={styles.highlight}>
                  <span className="material-symbols-rounded">info</span>
                  Extensions are typically limited to 3-5 days. Inform the editor before the deadline.
                </p>
              </div>

              <div className={styles.commCard}>
                <h3>Provide Feedback</h3>
                <p>We value your feedback on the review process. If you have suggestions for improvement or concerns, please share them with the editor.</p>
                <p className={styles.highlight}>
                  <span className="material-symbols-rounded">favorite</span>
                  Your insights help us improve our journal's peer review system.
                </p>
              </div>

              <div className={styles.commCard}>
                <h3>Reviewer Community</h3>
                <p>Connect with other reviewers, share insights, and stay updated on journal news through our reviewer network.</p>
                <button className={styles.communityBtn}>
                  Join Our Community
                  <span className="material-symbols-rounded">open_in_new</span>
                </button>
              </div>
            </div>

            <div className={styles.bestPractices}>
              <h3>Review Best Practices</h3>
              <ul>
                <li>Read the paper carefully at least twice</li>
                <li>Provide specific, actionable feedback</li>
                <li>Balance criticism with positive observations</li>
                <li>Suggest improvements and alternatives</li>
                <li>Be consistent between your comments and recommendation</li>
                <li>Proofread your review before submission</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewerGuidelines;
