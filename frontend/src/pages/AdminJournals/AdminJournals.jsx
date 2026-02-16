import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import acsApi from '../../api/apiService';
import { useToast } from '../../hooks/useToast';
import { useModal } from '../../hooks/useModal';
import styles from './AdminJournals.module.css';

const AdminJournals = () => {
  const navigate = useNavigate();
  const { success, error: showError } = useToast();
  const { confirm } = useModal();
  const [journals, setJournals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [deletingId, setDeletingId] = useState(null);
  const journalsPerPage = 6;

  const fetchJournals = useCallback(async () => {
    try {
      setLoading(true);
      const response = await acsApi.admin.listAllJournals(0, 100, search);
      setJournals(response.journals || []);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load journals');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    fetchJournals();
  }, [fetchJournals]);

  // Get initials from journal name or editor name
  const getInitials = (name) => {
    if (!name) return 'JN';
    const words = name.split(' ').filter(w => w.length > 0);
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  // Generate avatar color based on name
  const getAvatarColor = (name, index) => {
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];
    return colors[index % colors.length];
  };

  const filteredJournals = journals.filter(j => {
    const matchesSearch = !search || 
      j.name?.toLowerCase().includes(search.toLowerCase()) ||
      j.issn_online?.toLowerCase().includes(search.toLowerCase()) ||
      j.issn_print?.toLowerCase().includes(search.toLowerCase()) ||
      j.short_form?.toLowerCase().includes(search.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || 
      (statusFilter === 'active' && j.status !== 'on_hold') ||
      (statusFilter === 'on_hold' && j.status === 'on_hold');
    
    return matchesSearch && matchesStatus;
  });

  // Pagination
  const totalPages = Math.ceil(filteredJournals.length / journalsPerPage);
  const startIndex = (currentPage - 1) * journalsPerPage;
  const paginatedJournals = filteredJournals.slice(startIndex, startIndex + journalsPerPage);

  const handleEdit = (journal) => {
    navigate(`/journal/${journal.id}`);
  };

  const handleDelete = (journal) => {
    confirm({
      title: 'Delete Journal',
      message: `Are you sure you want to delete "${journal.name}"? This action cannot be undone.`,
      confirmText: 'Delete',
      cancelText: 'Cancel',
      type: 'error',
      onConfirm: async () => {
        try {
          setDeletingId(journal.id);
          await acsApi.admin.deleteJournal(journal.id);
          // Remove the deleted journal from the list
          setJournals(journals.filter(j => j.id !== journal.id));
          success(`Journal "${journal.name}" deleted successfully!`, 4000);
        } catch (err) {
          showError(err.response?.data?.detail || `Failed to delete journal "${journal.name}"`, 5000);
        } finally {
          setDeletingId(null);
        }
      },
    });
  };

  const handleAddJournal = () => {
    console.log('Add new journal');
    // TODO: Implement add journal modal/page
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <h1>Journal Management</h1>
          <p>View and manage all journals in the system</p>
        </div>
        <button className={styles.addBtn} onClick={handleAddJournal}>
          <span className="material-symbols-rounded">add</span>
          Add Journal
        </button>
      </div>

      <div className={styles.filters}>
        <div className={styles.searchWrapper}>
          <span className={`material-symbols-rounded ${styles.searchIcon}`}>search</span>
          <input
            type="text"
            placeholder="Search by journal name or ISSN..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setCurrentPage(1);
            }}
            className={styles.searchInput}
          />
        </div>
        <select 
          className={styles.statusFilter}
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setCurrentPage(1);
          }}
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="on_hold">On Hold</option>
        </select>
      </div>

      {loading ? (
        <div className={styles.loading}>Loading journals...</div>
      ) : error ? (
        <div className={styles.error}>{error}</div>
      ) : filteredJournals.length === 0 ? (
        <div className={styles.empty}>No journals found</div>
      ) : (
        <>
          <div className={styles.journalGrid}>
            {paginatedJournals.map((journal, index) => (
              <div key={journal.id} className={styles.journalCard}>
                <div className={styles.cardTop}>
                  <div className={styles.cardInfo}>
                    <h3>{journal.name}</h3>
                    <span className={`${styles.statusBadge} ${journal.status === 'on_hold' ? styles.onHold : styles.active}`}>
                      {journal.status === 'on_hold' ? 'ON HOLD' : 'ACTIVE'}
                    </span>
                  </div>
                  <div className={styles.cardActions}>
                    <button 
                      className={styles.actionBtn} 
                      onClick={() => handleEdit(journal)}
                      title="Edit journal"
                      disabled={deletingId === journal.id}
                    >
                      <span className="material-symbols-rounded">edit</span>
                    </button>
                    <button 
                      className={`${styles.actionBtn} ${styles.deleteBtn}`}
                      onClick={() => handleDelete(journal)}
                      title="Delete journal"
                      disabled={deletingId === journal.id}
                    >
                      <span className="material-symbols-rounded">
                        {deletingId === journal.id ? 'hourglass_empty' : 'delete'}
                      </span>
                    </button>
                  </div>
                </div>
                
                <div className={styles.cardMeta}>
                  <span className={styles.issn}>
                    ISSN: {journal.issn_print || journal.issn_online || 'N/A'}
                  </span>
                </div>

                <div className={styles.cardFooter}>
                  <div className={styles.avatarGroup}>
                    {journal.chief_editor && (
                      <div 
                        className={styles.avatar}
                        style={{ backgroundColor: getAvatarColor(journal.chief_editor, 0) }}
                        title={journal.chief_editor}
                      >
                        {getInitials(journal.chief_editor)}
                      </div>
                    )}
                    {journal.co_editor && (
                      <div 
                        className={styles.avatar}
                        style={{ backgroundColor: getAvatarColor(journal.co_editor, 1) }}
                        title={journal.co_editor}
                      >
                        {getInitials(journal.co_editor)}
                      </div>
                    )}
                    {(journal.chief_editor || journal.co_editor) && (
                      <span className={styles.avatarCount}>
                        +{(journal.chief_editor ? 1 : 0) + (journal.co_editor ? 1 : 0)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className={styles.pagination}>
              <button 
                className={styles.pageBtn}
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                <span className="material-symbols-rounded">chevron_left</span>
              </button>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                <button
                  key={page}
                  className={`${styles.pageBtn} ${currentPage === page ? styles.activePage : ''}`}
                  onClick={() => setCurrentPage(page)}
                >
                  {page}
                </button>
              ))}
              
              <button 
                className={styles.pageBtn}
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
              >
                <span className="material-symbols-rounded">chevron_right</span>
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default AdminJournals;
