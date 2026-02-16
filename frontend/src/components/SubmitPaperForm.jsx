import { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { ToastContext } from '../contexts/ToastContext';
import acsApi from '../api/apiService.js';
import styles from './SubmitPaperForm.module.css';

export const SubmitPaperForm = () => {
  const navigate = useNavigate();
  const { addToast } = useContext(ToastContext);
  
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [journals, setJournals] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    abstract: '',
    keywords: '',
    journal_id: '',
    coAuthors: [],
    file: null,
    filePreview: null,
  });

  useEffect(() => {
    const loadJournals = async () => {
      try {
        const response = await acsApi.getJournals(0, 100);
        const journalsArray = response.journals || response.data || response || [];
        setJournals(Array.isArray(journalsArray) ? journalsArray : []);
      } catch (err) {
        console.error('Failed to load journals:', err);
        setJournals([]);
      }
    };
    loadJournals();
  }, []);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(file.type)) {
      addToast('Only PDF and Word documents are allowed', 'error');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      addToast('File size must not exceed 50MB', 'error');
      return;
    }

    setFormData(prev => ({
      ...prev,
      file,
      filePreview: `${file.name} (${(file.size / 1024 / 1024).toFixed(2)}MB)`
    }));
  };

  const validateStep = (step) => {
    const validations = {
      1: () => {
        if (!formData.title || !formData.journal_id) {
          addToast('Please fill in title and select a journal', 'error');
          return false;
        }
        if (formData.title.length < 10) {
          addToast('Title must be at least 10 characters', 'error');
          return false;
        }
        return true;
      },
      2: () => {
        if (!formData.abstract || formData.abstract.length < 100) {
          addToast('Abstract must be at least 100 characters', 'error');
          return false;
        }
        if (formData.abstract.length > 2000) {
          addToast('Abstract must not exceed 2000 characters', 'error');
          return false;
        }
        if (!formData.keywords) {
          addToast('Please enter keywords', 'error');
          return false;
        }
        return true;
      },
      3: () => {
        if (!formData.file) {
          addToast('Please upload your paper file', 'error');
          return false;
        }
        return true;
      }
    };
    return validations[step]?.() ?? true;
  };

  const handleNextStep = () => {
    if (validateStep(currentStep) && currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await acsApi.author.submitPaper({
        title: formData.title,
        abstract: formData.abstract,
        keywords: formData.keywords,
        journal_id: formData.journal_id,
        file: formData.file
      });
      addToast(`Paper submitted successfully! Paper ID: ${response.id}`, 'success');
      navigate('/author');
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to submit paper', 'error');
    } finally {
      setLoading(false);
    }
  };

  const getStepStatus = (stepNum) => {
    if (currentStep > stepNum) return 'completed';
    if (currentStep === stepNum) return 'inProgress';
    return 'pending';
  };

  const steps = [
    { num: 1, label: 'Metadata', icon: 'description' },
    { num: 2, label: 'Content', icon: 'edit_note' },
    { num: 3, label: 'Upload', icon: 'cloud_upload' },
    { num: 4, label: 'Review', icon: 'done' }
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Submit Your Paper</h1>
        <p>Complete all steps to submit your paper for peer review</p>
      </div>

      {/* Stepper */}
      <div className={styles.stepper}>
        {steps.map((step) => {
          const status = getStepStatus(step.num);
          return (
            <div key={step.num} className={`${styles.step} ${styles[status]}`}>
              <div className={styles.stepContent}>
                <div
                  className={`${styles.stepDot} ${styles[status]}`}
                  onClick={() => currentStep > step.num && setCurrentStep(step.num)}
                >
                  <span className={`material-symbols-rounded ${styles.stepIcon}`}>
                    {step.icon}
                  </span>
                </div>
                <div className={styles.stepLabel}>
                  <strong>STEP {step.num}</strong>
                  <h4>{step.label}</h4>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Form Content */}
      <div className={styles.formCard}>
        {/* Step 1: Metadata */}
        {currentStep === 1 && (
          <div>
            <h2>Step 1: Paper Metadata</h2>
            <div className={styles.field}>
              <label htmlFor="journal">Select Journal *</label>
              <select
                id="journal"
                value={formData.journal_id}
                onChange={(e) => handleInputChange('journal_id', e.target.value)}
                className={styles.select}
              >
                <option value="">-- Select Journal --</option>
                {journals.map(j => (
                  <option key={j.id} value={j.id}>{j.name}</option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <label htmlFor="title">Paper Title *</label>
              <input
                id="title"
                type="text"
                placeholder="Enter paper title (minimum 10 characters)"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                maxLength={500}
                className={styles.input}
              />
              <small>{formData.title.length}/500 characters</small>
            </div>
          </div>
        )}

        {/* Step 2: Abstract & Keywords */}
        {currentStep === 2 && (
          <div>
            <h2>Step 2: Paper Content</h2>
            <div className={styles.field}>
              <label htmlFor="abstract">Abstract *</label>
              <textarea
                id="abstract"
                placeholder="Enter paper abstract (100-2000 characters)"
                value={formData.abstract}
                onChange={(e) => handleInputChange('abstract', e.target.value)}
                maxLength={2000}
                rows={6}
                className={styles.textarea}
              />
              <small>{formData.abstract.length}/2000 characters</small>
            </div>
            <div className={styles.field}>
              <label htmlFor="keywords">Keywords *</label>
              <input
                id="keywords"
                type="text"
                placeholder="Enter keywords separated by commas"
                value={formData.keywords}
                onChange={(e) => handleInputChange('keywords', e.target.value)}
                maxLength={1000}
                className={styles.input}
              />
              <small>Separate keywords with commas</small>
            </div>
          </div>
        )}

        {/* Step 3: File Upload */}
        {currentStep === 3 && (
          <div>
            <h2>Step 3: Upload Paper File</h2>
            <div className={styles.field}>
              <label>Paper File (PDF or Word) *</label>
              <div className={styles.uploadArea}>
                <input
                  id="file"
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx"
                  className={styles.hidden}
                />
                <div className={styles.uploadIcon}>📄</div>
                <p className={styles.uploadText}>Drag and drop your paper file here</p>
                <p className={styles.uploadOr}>or</p>
                <label htmlFor="file" className={styles.browseBtn}>Browse Files</label>
                <p className={styles.uploadHint}>
                  Supported formats: PDF, DOC, DOCX<br />Maximum size: 50MB
                </p>
              </div>
              {formData.filePreview && (
                <div className={styles.filePreview}>
                  <span className={styles.fileName}>{formData.filePreview}</span>
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, file: null, filePreview: null }))}
                    className={styles.removeFile}
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 4: Review */}
        {currentStep === 4 && (
          <div>
            <h2>Step 4: Review & Submit</h2>
            <div className={styles.reviewBox}>
              <div className={styles.reviewSection}>
                <h3>Journal</h3>
                <p>{journals.find(j => j.id === formData.journal_id)?.name || 'Not selected'}</p>
              </div>
              <div className={styles.reviewSection}>
                <h3>Title</h3>
                <p>{formData.title || 'Not provided'}</p>
              </div>
              <div className={styles.reviewSection}>
                <h3>Abstract</h3>
                <p className={styles.abstractPreview}>{formData.abstract || 'Not provided'}</p>
              </div>
              <div className={styles.reviewSection}>
                <h3>Keywords</h3>
                <p>{formData.keywords || 'Not provided'}</p>
              </div>
              <div className={styles.reviewSection}>
                <h3>Paper File</h3>
                <p>{formData.filePreview || 'Not uploaded'}</p>
              </div>
              <div className={styles.reviewNote}>
                <strong>Important:</strong> By submitting this paper, you confirm that:
                <ul>
                  <li>The paper is original and has not been published elsewhere</li>
                  <li>All authors have agreed to the submission</li>
                  <li>The paper complies with the journal's guidelines</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className={styles.actions}>
        <button
          onClick={handlePrevStep}
          disabled={currentStep === 1 || loading}
          className={`${styles.btn} ${styles.btnSecondary}`}
        >
          ← Previous
        </button>
        {currentStep < 4 ? (
          <button
            onClick={handleNextStep}
            disabled={loading}
            className={`${styles.btn} ${styles.btnPrimary}`}
          >
            Next →
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={loading}
            className={`${styles.btn} ${styles.btnSuccess}`}
          >
            {loading ? 'Submitting...' : 'Submit Paper'}
          </button>
        )}
      </div>

      {loading && <div className={styles.loadingOverlay}>Processing your submission...</div>}
    </div>
  );
};
