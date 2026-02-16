import { useState } from 'react';
import styles from './AdminSettings.module.css';

const AdminSettings = () => {
  const [settings, setSettings] = useState({
    siteName: 'AACS Journals',
    siteEmail: 'admin@aacsjournals.com',
    emailNotifications: true,
    autoAssignReviewers: false,
    reviewDeadlineDays: 14,
    maxFileSize: 10,
  });

  const [saved, setSaved] = useState(false);

  const handleChange = (field, value) => {
    setSettings(prev => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  const handleSave = (e) => {
    e.preventDefault();
    // In a real implementation, this would call an API
    console.log('Saving settings:', settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>System Settings</h1>
        <p>Configure global application settings</p>
      </div>

      <form onSubmit={handleSave} className={styles.form}>
        <div className={styles.section}>
          <h2>General Settings</h2>
          
          <div className={styles.formGroup}>
            <label htmlFor="siteName">Site Name</label>
            <input
              type="text"
              id="siteName"
              value={settings.siteName}
              onChange={(e) => handleChange('siteName', e.target.value)}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="siteEmail">Contact Email</label>
            <input
              type="email"
              id="siteEmail"
              value={settings.siteEmail}
              onChange={(e) => handleChange('siteEmail', e.target.value)}
            />
          </div>
        </div>

        <div className={styles.section}>
          <h2>Notification Settings</h2>
          
          <div className={styles.formGroupCheckbox}>
            <input
              type="checkbox"
              id="emailNotifications"
              checked={settings.emailNotifications}
              onChange={(e) => handleChange('emailNotifications', e.target.checked)}
            />
            <label htmlFor="emailNotifications">
              <span className={styles.checkboxLabel}>Email Notifications</span>
              <span className={styles.checkboxDesc}>Send email notifications for paper submissions and reviews</span>
            </label>
          </div>

          <div className={styles.formGroupCheckbox}>
            <input
              type="checkbox"
              id="autoAssignReviewers"
              checked={settings.autoAssignReviewers}
              onChange={(e) => handleChange('autoAssignReviewers', e.target.checked)}
            />
            <label htmlFor="autoAssignReviewers">
              <span className={styles.checkboxLabel}>Auto-assign Reviewers</span>
              <span className={styles.checkboxDesc}>Automatically assign reviewers to new submissions</span>
            </label>
          </div>
        </div>

        <div className={styles.section}>
          <h2>Review Settings</h2>
          
          <div className={styles.formGroup}>
            <label htmlFor="reviewDeadlineDays">Default Review Deadline (days)</label>
            <input
              type="number"
              id="reviewDeadlineDays"
              min="7"
              max="90"
              value={settings.reviewDeadlineDays}
              onChange={(e) => handleChange('reviewDeadlineDays', parseInt(e.target.value))}
            />
            <span className={styles.hint}>Number of days reviewers have to complete their review</span>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="maxFileSize">Maximum Upload Size (MB)</label>
            <input
              type="number"
              id="maxFileSize"
              min="1"
              max="50"
              value={settings.maxFileSize}
              onChange={(e) => handleChange('maxFileSize', parseInt(e.target.value))}
            />
            <span className={styles.hint}>Maximum file size allowed for paper uploads</span>
          </div>
        </div>

        <div className={styles.actions}>
          {saved && <span className={styles.savedMessage}>✓ Settings saved successfully</span>}
          <button type="submit" className={styles.saveBtn}>
            Save Settings
          </button>
        </div>
      </form>

      <div className={styles.infoBox}>
        <h3>Note</h3>
        <p>
          These settings are stored locally for demonstration purposes. 
          In a production environment, these would be persisted to the database 
          and require additional backend API endpoints.
        </p>
      </div>
    </div>
  );
};

export default AdminSettings;
