import { useState } from 'react';
import PropTypes from 'prop-types';
import { acsApi } from '../../api/apiService';
import { useToast } from '../../hooks/useToast';
import styles from './AuthorContactModal.module.css';

const AuthorContactModal = ({ 
  isOpen, 
  onClose, 
  paperId, 
  paperCode,
  paperTitle
}) => {
  const { showSuccess, showError } = useToast();
  
  // State
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [inquiryType, setInquiryType] = useState('general');
  const [loading, setLoading] = useState(false);
  
  // Inquiry types
  const inquiryTypes = [
    { value: 'general', label: 'General Inquiry' },
    { value: 'status', label: 'Submission Status' },
    { value: 'revision', label: 'Revision Query' },
    { value: 'technical', label: 'Technical Issue' },
    { value: 'payment', label: 'Payment/Invoice' },
    { value: 'other', label: 'Other' }
  ];
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!subject.trim()) {
      showError('Please enter a subject');
      return;
    }
    
    if (!message.trim()) {
      showError('Please enter your message');
      return;
    }
    
    if (message.trim().length < 20) {
      showError('Please provide more details in your message (minimum 20 characters)');
      return;
    }
    
    setLoading(true);
    try {
      const response = await acsApi.author.contactEditorial(paperId, {
        subject: subject.trim(),
        message: message.trim(),
        inquiry_type: inquiryType
      });
      
      showSuccess(response.data?.message || 'Your message has been sent to the editorial office');
      handleClose();
    } catch (error) {
      console.error('Failed to send message:', error);
      showError(error.response?.data?.detail || 'Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Reset form on close
  const handleClose = () => {
    setSubject('');
    setMessage('');
    setInquiryType('general');
    onClose();
  };
  
  if (!isOpen) return null;
  
  return (
    <div className={styles.modalOverlay} onClick={handleClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <div className={styles.headerContent}>
            <span className="material-symbols-rounded">mail</span>
            <h2>Contact Editorial Office</h2>
          </div>
          <button className={styles.closeBtn} onClick={handleClose}>&times;</button>
        </div>
        
        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Paper Info */}
          <div className={styles.paperInfo}>
            <span className={styles.paperCode}>{paperCode}</span>
            <span className={styles.paperTitle}>{paperTitle}</span>
          </div>
          
          {/* Inquiry Type */}
          <div className={styles.formGroup}>
            <label htmlFor="inquiryType">Inquiry Type</label>
            <select
              id="inquiryType"
              value={inquiryType}
              onChange={(e) => setInquiryType(e.target.value)}
              className={styles.select}
            >
              {inquiryTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>
          
          {/* Subject */}
          <div className={styles.formGroup}>
            <label htmlFor="subject">Subject *</label>
            <input
              type="text"
              id="subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Brief description of your inquiry"
              className={styles.input}
              maxLength={200}
              required
            />
            <span className={styles.charCount}>{subject.length}/200</span>
          </div>
          
          {/* Message */}
          <div className={styles.formGroup}>
            <label htmlFor="message">Message *</label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Please provide details about your inquiry..."
              className={styles.textarea}
              rows={6}
              maxLength={2000}
              required
            />
            <span className={styles.charCount}>{message.length}/2000</span>
          </div>
          
          {/* Info Note */}
          <div className={styles.infoNote}>
            <span className="material-symbols-rounded">info</span>
            <p>
              Your message will be sent to the editorial team responsible for this journal. 
              You will receive a response via email and can also view it in your correspondence history.
            </p>
          </div>
          
          {/* Actions */}
          <div className={styles.actions}>
            <button 
              type="button" 
              className={styles.cancelBtn}
              onClick={handleClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className={styles.submitBtn}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className={styles.spinner}></span>
                  Sending...
                </>
              ) : (
                <>
                  <span className="material-symbols-rounded">send</span>
                  Send Message
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

AuthorContactModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  paperId: PropTypes.number.isRequired,
  paperCode: PropTypes.string,
  paperTitle: PropTypes.string
};

export default AuthorContactModal;
