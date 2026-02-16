import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useJournals } from '../../hooks/useJournals';
import { useToast } from '../../hooks/useToast';
import { useModal } from '../../hooks/useModal';
import { useRole } from '../../hooks/useRole';
import Breadcrumbs from '../../components/breadcrumbs/Breadcrumbs';
import './JournalDetailPage.css';

const JournalDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin, isEditor } = useRole();
  const { selectedJournal, loading, error, getJournalById, editJournal, removeJournal } = useJournals();
  const { success, error: showError, warning, info } = useToast();
  const { confirm } = useModal();
  const [isEditMode, setIsEditMode] = useState(false);
  const [editFormData, setEditFormData] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (id) {
      getJournalById(id);
    }
  }, [id, getJournalById]);

  useEffect(() => {
    if (selectedJournal && isEditMode) {
      setEditFormData({
        ...selectedJournal,
        // Strip HTML tags from description and guidelines for editing
        description: stripHtmlTags(selectedJournal.description),
        guidelines: stripHtmlTags(selectedJournal.guidelines),
      });
    }
  }, [isEditMode, selectedJournal]);

  // Function to strip HTML tags from description
  const stripHtmlTags = (html) => {
    if (!html) return 'No description available';
    const stripped = html.replace(/<[^>]*>/g, '');
    const decoded = new DOMParser().parseFromString(stripped, 'text/html').body.textContent || stripped;
    return decoded.trim();
  };

  // Function to convert HTML entities to plain text
  const decodeHtmlEntities = (html) => {
    if (!html) return '';
    const textarea = document.createElement('textarea');
    textarea.innerHTML = html;
    return textarea.value;
  };

  // Handle edit form input changes
  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setEditFormData({
      ...editFormData,
      [name]: value,
    });
  };

  // Handle update submission
  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await editJournal(id, editFormData);
      // Refresh the journal data after successful update
      await getJournalById(id);
      setIsEditMode(false);
      success('Journal updated successfully!', 4000);
    } catch (err) {
      showError('Failed to update journal: ' + err.message, 5000);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    confirm({
      title: 'Delete Journal',
      message: 'Are you sure you want to delete this journal? This action cannot be undone.',
      confirmText: 'Delete',
      cancelText: 'Cancel',
      type: 'error',
      onConfirm: async () => {
        try {
          setIsSubmitting(true);
          await removeJournal(id);
          success('Journal deleted successfully!', 4000);
          navigate('/journals');
        } catch (err) {
          showError('Failed to delete journal: ' + err.message, 5000);
        } finally {
          setIsSubmitting(false);
        }
      },
    });
  };

  if (loading) {
    return (
      <div className="journal-detail-page">
        <div className="journal-detail-loading">
          <div className="spinner"></div>
          <p>Loading journal details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="journal-detail-page">
        <div className="journal-detail-error">
          <p>{error}</p>
          <button className="btn-back" onClick={() => navigate('/journals')}>
            Back to Journals
          </button>
        </div>
      </div>
    );
  }

  if (!selectedJournal) {
    return (
      <div className="journal-detail-page">
        <div className="journal-detail-empty">
          <p>Journal not found</p>
          <button className="btn-back" onClick={() => navigate('/journals')}>
            Back to Journals
          </button>
        </div>
      </div>
    );
  }

  const journal = selectedJournal;

  const breadcrumbItems = [
    { label: 'Home', path: '/' },
    { label: 'Journals', path: '/journals' },
    { label: journal.name, path: `/journal/${id}` },
  ];

  return (
    <div className="journal-detail-page">
      <Breadcrumbs items={breadcrumbItems} />
      
      {/* Edit Mode */}
      {isEditMode ? (
        <div className="journal-edit-container">
          <h2>Edit Journal</h2>
          <form onSubmit={handleUpdateSubmit} className="journal-edit-form">
            <div className="form-group">
              <label htmlFor="name">Journal Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={editFormData.name || ''}
                onChange={handleEditInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="short_form">Short Form</label>
              <input
                type="text"
                id="short_form"
                name="short_form"
                value={editFormData.short_form || ''}
                onChange={handleEditInputChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="chief_editor">Chief Editor</label>
              <input
                type="text"
                id="chief_editor"
                name="chief_editor"
                value={editFormData.chief_editor || ''}
                onChange={handleEditInputChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="co_editor">Co Editor</label>
              <input
                type="text"
                id="co_editor"
                name="co_editor"
                value={editFormData.co_editor || ''}
                onChange={handleEditInputChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="issn_online">ISSN Online</label>
              <input
                type="text"
                id="issn_online"
                name="issn_online"
                value={editFormData.issn_online || ''}
                onChange={handleEditInputChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="issn_print">ISSN Print</label>
              <input
                type="text"
                id="issn_print"
                name="issn_print"
                value={editFormData.issn_print || ''}
                onChange={handleEditInputChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="publication_frequency">Publication Frequency</label>
              <input
                type="text"
                id="publication_frequency"
                name="publication_frequency"
                value={editFormData.publication_frequency || ''}
                onChange={handleEditInputChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="language">Language</label>
              <input
                type="text"
                id="language"
                name="language"
                value={editFormData.language || ''}
                onChange={handleEditInputChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="research_area">Research Area</label>
              <input
                type="text"
                id="research_area"
                name="research_area"
                value={editFormData.research_area || ''}
                onChange={handleEditInputChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <p className="form-help-text">HTML tags will be removed. Please enter plain text only.</p>
              <textarea
                id="description"
                name="description"
                value={editFormData.description || ''}
                onChange={handleEditInputChange}
                rows="5"
              />
            </div>

            <div className="form-group">
              <label htmlFor="guidelines">Guidelines</label>
              <p className="form-help-text">HTML tags will be removed. Please enter plain text only.</p>
              <textarea
                id="guidelines"
                name="guidelines"
                value={editFormData.guidelines || ''}
                onChange={handleEditInputChange}
                rows="5"
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setIsEditMode(false)}
                disabled={isSubmitting}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      ) : (
        <>
          {/* Header Banner */}
          <div className="journal-detail-header">
            <div className="journal-detail-header-content">
              
              <div className="journal-detail-title-section">
                <h1>{journal.name}</h1>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="journal-detail-container">
            <div className="journal-detail-main">
              {/* Description Section */}
              <section className="journal-detail-section">
                <h2>About</h2>
                <div className="journal-detail-description">
                  <p>{stripHtmlTags(journal.description)}</p>
                </div>
              </section>

              {/* Key Information */}
              <section className="journal-detail-section">
                <h2>Key Information</h2>
                <div className="journal-detail-info-grid">
                  <div className="info-card">
                    <label>Chief Editor</label>
                    <p>{journal.chief_editor || 'Not specified'}</p>
                  </div>
                  <div className="info-card">
                    <label>ISSN Online</label>
                    <p>{journal.issn_online || 'N/A'}</p>
                  </div>
                  <div className="info-card">
                    <label>ISSN Print</label>
                    <p>{journal.issn_print || 'N/A'}</p>
                  </div>
                </div>
              </section>

              {/* Submission Guidelines */}
              {journal.guidelines && (
                <section className="journal-detail-section">
                  <h2>Submission Guidelines</h2>
                  <div className="journal-detail-guidelines">
                    <p>{stripHtmlTags(journal.guidelines)}</p>
                  </div>
                </section>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default JournalDetailPage;
