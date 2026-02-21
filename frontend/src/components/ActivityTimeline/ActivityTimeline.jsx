import React from 'react';
import styles from './ActivityTimeline.module.css';

/**
 * ActivityTimeline - Displays paper activity history with visual timeline
 * 
 * @param {Object} props
 * @param {Array} props.events - Array of event objects with type, title, date, time
 */
const ActivityTimeline = ({ events = [] }) => {
  // Map event types to icons and colors
  const getEventStyle = (type) => {
    const eventStyles = {
      submitted: { icon: 'publish', color: 'blue' },
      under_review: { icon: 'visibility', color: 'blue' },
      reviewer_assigned: { icon: 'person_search', color: 'slate' },
      review_completed: { icon: 'rate_review', color: 'green' },
      revision_requested: { icon: 'edit_note', color: 'amber' },
      resubmitted: { icon: 'upload_file', color: 'blue' },
      accepted: { icon: 'check_circle', color: 'green' },
      rejected: { icon: 'cancel', color: 'red' },
      published: { icon: 'public', color: 'green' },
      default: { icon: 'schedule', color: 'slate' }
    };
    return eventStyles[type] || eventStyles.default;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  const formatTime = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true
    });
  };

  if (!events || events.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h2 className={styles.title}>Activity Timeline</h2>
        </div>
        <div className={styles.empty}>
          <span className="material-symbols-outlined">history</span>
          <p>No activity yet</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Activity Timeline</h2>
      </div>
      <div className={styles.timeline}>
        {events.map((event, index) => {
          const eventStyle = getEventStyle(event.type);
          const isLast = index === events.length - 1;
          
          return (
            <div key={index} className={styles.event}>
              {!isLast && <div className={styles.connector} />}
              <div className={`${styles.iconWrapper} ${styles[eventStyle.color]}`}>
                <span className="material-symbols-outlined">{eventStyle.icon}</span>
              </div>
              <div className={styles.content}>
                <p className={styles.eventTitle}>{event.title}</p>
                <p className={styles.eventTime}>
                  {formatDate(event.date)} • {formatTime(event.date)}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ActivityTimeline;
