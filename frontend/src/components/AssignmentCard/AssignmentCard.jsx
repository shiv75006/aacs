import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './AssignmentCard.module.css';

const AssignmentCard = ({ assignment, onStartReview }) => {
  const navigate = useNavigate();

  const getDaysRemaining = (dueDate) => {
    const due = new Date(dueDate);
    const today = new Date();
    const diff = Math.ceil((due - today) / (1000 * 60 * 60 * 24));
    return diff;
  };

  const getUrgencyClass = (daysRemaining) => {
    if (daysRemaining < 3) return 'urgency-high';
    if (daysRemaining < 7) return 'urgency-medium';
    return 'urgency-low';
  };

  const daysRemaining = getDaysRemaining(assignment.due_date);

  const getStatusClass = (status) => {
    if (!status) return 'Pending';
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <div className={styles.assignmentCard}>
      <div className={styles.cardContent}>
        <div className={styles.titleSection}>
          <h3 className={styles.paperTitle}>{assignment.paper_title || 'Untitled Paper'}</h3>
        </div>

        <div className={styles.metaSection}>
          <div className={styles.metaLeft}>
            <span className={styles.metaItem}>
              <span className="material-symbols-rounded">calendar_today</span>
              Due: {new Date(assignment.due_date).toLocaleDateString()}
            </span>
          </div>

          <div className={styles.metaRight}>
            <span className={`${styles.statusBadge} ${styles[`status${getStatusClass(assignment.status)}`]}`}>
              {assignment.status || 'Pending'}
            </span>
            <span className={`${styles.urgencyBadge} ${styles[getUrgencyClass(daysRemaining)]}`}>
              {daysRemaining > 0 ? `${daysRemaining}d left` : 'Overdue'}
            </span>
          </div>
        </div>
      </div>

      {assignment.status === 'pending' && (
        <button
          className={styles.startBtn}
          onClick={() => navigate(`/reviewer/assignments/${assignment.id}/review`)}
          title="Start Review"
        >
          <span>Start Review</span>
          <span className="material-symbols-rounded">arrow_forward</span>
        </button>
      )}

      {assignment.status === 'in_progress' && (
        <button
          className={styles.continueBtn}
          onClick={() => navigate(`/reviewer/assignments/${assignment.id}/review`)}
          title="Continue Review"
        >
          <span>Continue</span>
          <span className="material-symbols-rounded">arrow_forward</span>
        </button>
      )}

      {assignment.status === 'completed' && (
        <button
          className={styles.viewBtn}
          onClick={() => navigate(`/reviewer/assignments/${assignment.id}`)}
          title="View Submission"
        >
          <span>View</span>
          <span className="material-symbols-rounded">open_in_new</span>
        </button>
      )}
    </div>
  );
};

export default AssignmentCard;
