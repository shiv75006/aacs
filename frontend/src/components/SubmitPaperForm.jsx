import { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { ToastContext } from '../contexts/ToastContext';
import acsApi from '../api/apiService.js';
import styles from './SubmitPaperForm.module.css';

const SALUTATION_OPTIONS = [
  { value: '', label: 'Select...' },
  { value: 'Prof. Dr.', label: 'Prof. Dr.' },
  { value: 'Prof.', label: 'Prof.' },
  { value: 'Dr.', label: 'Dr.' },
  { value: 'Mr.', label: 'Mr.' },
  { value: 'Ms.', label: 'Ms.' },
];

const EMPTY_CO_AUTHOR = {
  salutation: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  designation: '',
  department: '',
  organisation: '',
  email: '',
  is_corresponding: false,
};

export const SubmitPaperForm = () => {
  const navigate = useNavigate();
  const { addToast } = useContext(ToastContext);
  
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [journals, setJournals] = useState([]);
  const [keywordInput, setKeywordInput] = useState('');
  const [keywordChips, setKeywordChips] = useState([]);
  
  const [formData, setFormData] = useState({
    // Step 1: Paper Metadata
    title: '',
    abstract: '',
    keywords: '',
    research_area: '',
    message_to_editor: '',
    journal_id: '',
    // Step 2: Author Details
    authorDetails: {
      salutation: '',
      first_name: '',
      middle_name: '',
      last_name: '',
      designation: '',
      department: '',
      organisation: '',
    },
    coAuthors: [],
    // Step 3: File Upload
    file: null,
    filePreview: null,
    // Step 4: Terms
    termsAccepted: false,
  });

  // Load journals and author profile on mount
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Load journals
        const journalsResponse = await acsApi.getJournals(0, 100);
        const journalsArray = journalsResponse.journals || journalsResponse.data || journalsResponse || [];
        setJournals(Array.isArray(journalsArray) ? journalsArray : []);
        
        // Load author profile for pre-fill
        try {
          const profile = await acsApi.author.getAuthorProfile();
          if (profile) {
            setFormData(prev => ({
              ...prev,
              authorDetails: {
                salutation: profile.salutation || '',
                first_name: profile.fname || '',
                middle_name: profile.mname || '',
                last_name: profile.lname || '',
                designation: profile.designation || '',
                department: profile.department || '',
                organisation: profile.organisation || profile.affiliation || '',
              }
            }));
          }
        } catch (profileErr) {
          console.log('Could not load author profile for pre-fill:', profileErr);
        }
      } catch (err) {
        console.error('Failed to load initial data:', err);
        setJournals([]);
      }
    };
    loadInitialData();
  }, []);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAuthorChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      authorDetails: { ...prev.authorDetails, [field]: value }
    }));
  };

  // Keyword chip handling
  const handleKeywordInputChange = (e) => {
    const value = e.target.value;
    setKeywordInput(value);
    
    // Check if comma was entered
    if (value.includes(',')) {
      const parts = value.split(',');
      const newKeyword = parts[0].trim();
      
      if (newKeyword && !keywordChips.includes(newKeyword)) {
        const newChips = [...keywordChips, newKeyword];
        setKeywordChips(newChips);
        setFormData(prev => ({ ...prev, keywords: newChips.join(', ') }));
      }
      setKeywordInput(parts[1] || '');
    }
  };

  const handleKeywordKeyDown = (e) => {
    if (e.key === 'Enter' && keywordInput.trim()) {
      e.preventDefault();
      const newKeyword = keywordInput.trim();
      if (!keywordChips.includes(newKeyword)) {
        const newChips = [...keywordChips, newKeyword];
        setKeywordChips(newChips);
        setFormData(prev => ({ ...prev, keywords: newChips.join(', ') }));
      }
      setKeywordInput('');
    } else if (e.key === 'Backspace' && !keywordInput && keywordChips.length > 0) {
      // Remove last chip on backspace if input is empty
      const newChips = keywordChips.slice(0, -1);
      setKeywordChips(newChips);
      setFormData(prev => ({ ...prev, keywords: newChips.join(', ') }));
    }
  };

  const removeKeywordChip = (indexToRemove) => {
    const newChips = keywordChips.filter((_, idx) => idx !== indexToRemove);
    setKeywordChips(newChips);
    setFormData(prev => ({ ...prev, keywords: newChips.join(', ') }));
  };

  // Co-author handling
  const addCoAuthor = () => {
    setFormData(prev => ({
      ...prev,
      coAuthors: [...prev.coAuthors, { ...EMPTY_CO_AUTHOR, author_order: prev.coAuthors.length + 2 }]
    }));
  };

  const removeCoAuthor = (index) => {
    setFormData(prev => ({
      ...prev,
      coAuthors: prev.coAuthors.filter((_, idx) => idx !== index).map((co, idx) => ({
        ...co,
        author_order: idx + 2
      }))
    }));
  };

  const updateCoAuthor = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      coAuthors: prev.coAuthors.map((co, idx) => 
        idx === index ? { ...co, [field]: value } : co
      )
    }));
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
        if (!formData.journal_id) {
          addToast('Please select a journal', 'error');
          return false;
        }
        if (!formData.title || formData.title.length < 10) {
          addToast('Title must be at least 10 characters', 'error');
          return false;
        }
        if (!formData.abstract || formData.abstract.length < 100) {
          addToast('Abstract must be at least 100 characters', 'error');
          return false;
        }
        if (formData.abstract.length > 2000) {
          addToast('Abstract must not exceed 2000 characters', 'error');
          return false;
        }
        if (keywordChips.length === 0) {
          addToast('Please enter at least one keyword', 'error');
          return false;
        }
        return true;
      },
      2: () => {
        const { authorDetails } = formData;
        if (!authorDetails.first_name?.trim()) {
          addToast('First name is required', 'error');
          return false;
        }
        if (!authorDetails.last_name?.trim()) {
          addToast('Last name is required', 'error');
          return false;
        }
        // Validate co-authors if any
        for (let i = 0; i < formData.coAuthors.length; i++) {
          const co = formData.coAuthors[i];
          if (!co.first_name?.trim() || !co.last_name?.trim()) {
            addToast(`Co-author ${i + 1}: First and last name are required`, 'error');
            return false;
          }
        }
        return true;
      },
      3: () => {
        if (!formData.file) {
          addToast('Please upload your paper file', 'error');
          return false;
        }
        return true;
      },
      4: () => {
        if (!formData.termsAccepted) {
          addToast('Please accept the terms and conditions', 'error');
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
    if (!validateStep(4)) return;

    setLoading(true);
    try {
      const response = await acsApi.author.submitPaper({
        title: formData.title,
        abstract: formData.abstract,
        keywords: formData.keywords,
        journal_id: parseInt(formData.journal_id),
        file: formData.file,
        research_area: formData.research_area,
        message_to_editor: formData.message_to_editor,
        terms_accepted: formData.termsAccepted,
        author_details: formData.authorDetails,
        co_authors: formData.coAuthors.map((co, idx) => ({
          ...co,
          author_order: idx + 2
        }))
      });

      addToast(`Paper submitted successfully! Paper ID: ${response.id}`, 'success');
      setTimeout(() => navigate('/author'), 1500);
    } catch (err) {
      console.error('Submit error:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to submit paper';
      addToast(errorMsg, 'error');
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
    { num: 1, label: 'Paper Metadata', icon: 'description' },
    { num: 2, label: 'Author Details', icon: 'person' },
    { num: 3, label: 'Upload', icon: 'cloud_upload' },
    { num: 4, label: 'Review & Submit', icon: 'done' }
  ];

  const formatAuthorName = (author) => {
    const parts = [];
    if (author.salutation) parts.push(author.salutation);
    if (author.first_name) parts.push(author.first_name);
    if (author.middle_name) parts.push(author.middle_name);
    if (author.last_name) parts.push(author.last_name);
    return parts.join(' ') || 'Not provided';
  };

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
        {/* Step 1: Paper Metadata */}
        {currentStep === 1 && (
          <div>
            <h2>Step 1: Paper Metadata</h2>
            
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
                placeholder="Type keyword and press comma or Enter"
                value={keywordInput}
                onChange={handleKeywordInputChange}
                onKeyDown={handleKeywordKeyDown}
                className={styles.input}
              />
              <small>Separate keywords with commas or press Enter</small>
              {keywordChips.length > 0 && (
                <div className={styles.keywordChipsBelow}>
                  {keywordChips.map((kw, idx) => (
                    <span key={idx} className={styles.keywordChip}>
                      {kw}
                      <button 
                        type="button" 
                        onClick={() => removeKeywordChip(idx)}
                        className={styles.chipRemove}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className={styles.fieldRow}>
              <div className={styles.field}>
                <label htmlFor="research_area">Research Area</label>
                <input
                  id="research_area"
                  type="text"
                  placeholder="e.g., Machine Learning, Bioinformatics"
                  value={formData.research_area}
                  onChange={(e) => handleInputChange('research_area', e.target.value)}
                  maxLength={200}
                  className={styles.input}
                />
              </div>

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
            </div>

            <div className={styles.field}>
              <label htmlFor="message_to_editor">Message to the Editor (Optional)</label>
              <textarea
                id="message_to_editor"
                placeholder="Any special notes or requests for the editor..."
                value={formData.message_to_editor}
                onChange={(e) => handleInputChange('message_to_editor', e.target.value)}
                maxLength={1000}
                rows={3}
                className={styles.textarea}
              />
            </div>
          </div>
        )}

        {/* Step 2: Author Details */}
        {currentStep === 2 && (
          <div>
            <h2>Step 2: Author Details</h2>
            
            {/* Primary Author */}
            <div className={styles.authorSection}>
              <h3 className={styles.authorSectionTitle}>
                <span className="material-symbols-rounded">person</span>
                Primary Author (You)
              </h3>
              
              <div className={styles.fieldRow}>
                <div className={styles.fieldSmall}>
                  <label htmlFor="author_salutation">Salutation</label>
                  <select
                    id="author_salutation"
                    value={formData.authorDetails.salutation}
                    onChange={(e) => handleAuthorChange('salutation', e.target.value)}
                    className={styles.select}
                  >
                    {SALUTATION_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div className={styles.field}>
                  <label htmlFor="author_fname">First Name *</label>
                  <input
                    id="author_fname"
                    type="text"
                    placeholder="First name"
                    value={formData.authorDetails.first_name}
                    onChange={(e) => handleAuthorChange('first_name', e.target.value)}
                    className={styles.input}
                  />
                </div>
                <div className={styles.field}>
                  <label htmlFor="author_mname">Middle Name</label>
                  <input
                    id="author_mname"
                    type="text"
                    placeholder="Middle name (optional)"
                    value={formData.authorDetails.middle_name}
                    onChange={(e) => handleAuthorChange('middle_name', e.target.value)}
                    className={styles.input}
                  />
                </div>
                <div className={styles.field}>
                  <label htmlFor="author_lname">Last Name *</label>
                  <input
                    id="author_lname"
                    type="text"
                    placeholder="Last name"
                    value={formData.authorDetails.last_name}
                    onChange={(e) => handleAuthorChange('last_name', e.target.value)}
                    className={styles.input}
                  />
                </div>
              </div>

              <div className={styles.fieldRow}>
                <div className={styles.field}>
                  <label htmlFor="author_designation">Designation/Occupation</label>
                  <input
                    id="author_designation"
                    type="text"
                    placeholder="e.g., Associate Professor"
                    value={formData.authorDetails.designation}
                    onChange={(e) => handleAuthorChange('designation', e.target.value)}
                    className={styles.input}
                  />
                </div>
                <div className={styles.field}>
                  <label htmlFor="author_department">Department</label>
                  <input
                    id="author_department"
                    type="text"
                    placeholder="e.g., Computer Science"
                    value={formData.authorDetails.department}
                    onChange={(e) => handleAuthorChange('department', e.target.value)}
                    className={styles.input}
                  />
                </div>
                <div className={styles.field}>
                  <label htmlFor="author_organisation">Organisation</label>
                  <input
                    id="author_organisation"
                    type="text"
                    placeholder="e.g., University of Technology"
                    value={formData.authorDetails.organisation}
                    onChange={(e) => handleAuthorChange('organisation', e.target.value)}
                    className={styles.input}
                  />
                </div>
              </div>
            </div>

            {/* Co-Authors */}
            <div className={styles.coAuthorsSection}>
              <div className={styles.coAuthorsHeader}>
                <h3 className={styles.authorSectionTitle}>
                  <span className="material-symbols-rounded">group</span>
                  Co-Authors
                </h3>
                <button type="button" onClick={addCoAuthor} className={styles.addCoAuthorBtn}>
                  <span className="material-symbols-rounded">add</span>
                  Add Co-Author
                </button>
              </div>

              {formData.coAuthors.length === 0 ? (
                <p className={styles.noCoAuthors}>No co-authors added. Click "Add Co-Author" to add one.</p>
              ) : (
                formData.coAuthors.map((coAuthor, index) => (
                  <div key={index} className={styles.coAuthorCard}>
                    <div className={styles.coAuthorHeader}>
                      <span className={styles.coAuthorNumber}>Co-Author {index + 1}</span>
                      <button 
                        type="button" 
                        onClick={() => removeCoAuthor(index)}
                        className={styles.removeCoAuthorBtn}
                      >
                        <span className="material-symbols-rounded">close</span>
                      </button>
                    </div>

                    <div className={styles.fieldRow}>
                      <div className={styles.fieldSmall}>
                        <label>Salutation</label>
                        <select
                          value={coAuthor.salutation}
                          onChange={(e) => updateCoAuthor(index, 'salutation', e.target.value)}
                          className={styles.select}
                        >
                          {SALUTATION_OPTIONS.map(opt => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                          ))}
                        </select>
                      </div>
                      <div className={styles.field}>
                        <label>First Name *</label>
                        <input
                          type="text"
                          placeholder="First name"
                          value={coAuthor.first_name}
                          onChange={(e) => updateCoAuthor(index, 'first_name', e.target.value)}
                          className={styles.input}
                        />
                      </div>
                      <div className={styles.field}>
                        <label>Middle Name</label>
                        <input
                          type="text"
                          placeholder="Middle name"
                          value={coAuthor.middle_name}
                          onChange={(e) => updateCoAuthor(index, 'middle_name', e.target.value)}
                          className={styles.input}
                        />
                      </div>
                      <div className={styles.field}>
                        <label>Last Name *</label>
                        <input
                          type="text"
                          placeholder="Last name"
                          value={coAuthor.last_name}
                          onChange={(e) => updateCoAuthor(index, 'last_name', e.target.value)}
                          className={styles.input}
                        />
                      </div>
                    </div>

                    <div className={styles.fieldRow}>
                      <div className={styles.field}>
                        <label>Email</label>
                        <input
                          type="email"
                          placeholder="Email address"
                          value={coAuthor.email}
                          onChange={(e) => updateCoAuthor(index, 'email', e.target.value)}
                          className={styles.input}
                        />
                      </div>
                      <div className={styles.field}>
                        <label>Designation</label>
                        <input
                          type="text"
                          placeholder="Designation"
                          value={coAuthor.designation}
                          onChange={(e) => updateCoAuthor(index, 'designation', e.target.value)}
                          className={styles.input}
                        />
                      </div>
                    </div>

                    <div className={styles.fieldRow}>
                      <div className={styles.field}>
                        <label>Department</label>
                        <input
                          type="text"
                          placeholder="Department"
                          value={coAuthor.department}
                          onChange={(e) => updateCoAuthor(index, 'department', e.target.value)}
                          className={styles.input}
                        />
                      </div>
                      <div className={styles.field}>
                        <label>Organisation</label>
                        <input
                          type="text"
                          placeholder="Organisation"
                          value={coAuthor.organisation}
                          onChange={(e) => updateCoAuthor(index, 'organisation', e.target.value)}
                          className={styles.input}
                        />
                      </div>
                    </div>

                    <div className={styles.checkboxField}>
                      <label className={styles.checkboxLabel}>
                        <input
                          type="checkbox"
                          checked={coAuthor.is_corresponding}
                          onChange={(e) => updateCoAuthor(index, 'is_corresponding', e.target.checked)}
                        />
                        <span>Corresponding Author</span>
                      </label>
                    </div>
                  </div>
                ))
              )}
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

        {/* Step 4: Review & Submit */}
        {currentStep === 4 && (
          <div>
            <h2>Step 4: Review & Submit</h2>
            <div className={styles.reviewBox}>
              {/* Paper Metadata */}
              <div className={styles.reviewSection}>
                <h3>Paper Information</h3>
                <div className={styles.reviewGrid}>
                  <div className={styles.reviewItem}>
                    <span className={styles.reviewLabel}>Title:</span>
                    <span className={styles.reviewValue}>{formData.title || 'Not provided'}</span>
                  </div>
                  <div className={styles.reviewItem}>
                    <span className={styles.reviewLabel}>Journal:</span>
                    <span className={styles.reviewValue}>
                      {journals.find(j => String(j.id) === String(formData.journal_id))?.name || 'Not selected'}
                    </span>
                  </div>
                  <div className={styles.reviewItem}>
                    <span className={styles.reviewLabel}>Research Area:</span>
                    <span className={styles.reviewValue}>{formData.research_area || 'Not specified'}</span>
                  </div>
                </div>
              </div>

              <div className={styles.reviewSection}>
                <h3>Abstract</h3>
                <p className={styles.abstractPreview}>{formData.abstract || 'Not provided'}</p>
              </div>

              <div className={styles.reviewSection}>
                <h3>Keywords</h3>
                <div className={styles.keywordChipsReview}>
                  {keywordChips.map((kw, idx) => (
                    <span key={idx} className={styles.keywordChipReview}>{kw}</span>
                  ))}
                </div>
              </div>

              {/* Author Details */}
              <div className={styles.reviewSection}>
                <h3>Primary Author</h3>
                <div className={styles.reviewGrid}>
                  <div className={styles.reviewItem}>
                    <span className={styles.reviewLabel}>Name:</span>
                    <span className={styles.reviewValue}>{formatAuthorName(formData.authorDetails)}</span>
                  </div>
                  <div className={styles.reviewItem}>
                    <span className={styles.reviewLabel}>Designation:</span>
                    <span className={styles.reviewValue}>{formData.authorDetails.designation || 'Not specified'}</span>
                  </div>
                  <div className={styles.reviewItem}>
                    <span className={styles.reviewLabel}>Department:</span>
                    <span className={styles.reviewValue}>{formData.authorDetails.department || 'Not specified'}</span>
                  </div>
                  <div className={styles.reviewItem}>
                    <span className={styles.reviewLabel}>Organisation:</span>
                    <span className={styles.reviewValue}>{formData.authorDetails.organisation || 'Not specified'}</span>
                  </div>
                </div>
              </div>

              {/* Co-Authors */}
              {formData.coAuthors.length > 0 && (
                <div className={styles.reviewSection}>
                  <h3>Co-Authors ({formData.coAuthors.length})</h3>
                  {formData.coAuthors.map((co, idx) => (
                    <div key={idx} className={styles.coAuthorReview}>
                      <strong>{idx + 1}. {formatAuthorName(co)}</strong>
                      {co.is_corresponding && <span className={styles.correspondingBadge}>Corresponding</span>}
                      <div className={styles.coAuthorDetails}>
                        {co.designation && <span>{co.designation}</span>}
                        {co.department && <span>{co.department}</span>}
                        {co.organisation && <span>{co.organisation}</span>}
                        {co.email && <span>{co.email}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* File */}
              <div className={styles.reviewSection}>
                <h3>Paper File</h3>
                <p>{formData.filePreview || 'Not uploaded'}</p>
              </div>

              {/* Message to Editor */}
              {formData.message_to_editor && (
                <div className={styles.reviewSection}>
                  <h3>Message to Editor</h3>
                  <p>{formData.message_to_editor}</p>
                </div>
              )}

              {/* Terms & Conditions */}
              <div className={styles.termsSection}>
                <label className={styles.termsLabel}>
                  <input
                    type="checkbox"
                    checked={formData.termsAccepted}
                    onChange={(e) => handleInputChange('termsAccepted', e.target.checked)}
                  />
                  <span>
                    I agree to the <a href="#terms" className={styles.termsLink}>Terms and Conditions</a>
                  </span>
                </label>
                <div className={styles.termsNote}>
                  <strong>By submitting, you confirm:</strong>
                  <ul>
                    <li>The paper is original and has not been published elsewhere</li>
                    <li>All authors have agreed to the submission</li>
                    <li>The paper complies with the journal's guidelines</li>
                    <li>You have read and agree to the terms and conditions</li>
                  </ul>
                </div>
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
            disabled={loading || !formData.termsAccepted}
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
