import { useState, useEffect, useCallback } from 'react';
import acsApi from '../../api/apiService';
import { useToast } from '../../hooks/useToast';
import styles from './AdminUsers.module.css';

const AdminUsers = () => {
  const { success: showSuccess, error: showError } = useToast();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [pagination, setPagination] = useState({ total: 0, skip: 0, limit: 20 });
  
  // Role management modal state
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userRoles, setUserRoles] = useState([]);
  const [loadingRoles, setLoadingRoles] = useState(false);
  const [savingRoles, setSavingRoles] = useState(false);

  const roles = ['admin', 'author', 'editor', 'reviewer'];

  const fetchUsers = useCallback(async (skip = 0) => {
    try {
      setLoading(true);
      const response = await acsApi.admin.listUsers(skip, pagination.limit, search, roleFilter);
      setUsers(response.users || []);
      setPagination({ total: response.total, skip: response.skip, limit: response.limit });
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [pagination.limit, search, roleFilter]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchUsers(0);
  };

  // Open role management modal
  const openRoleModal = async (user) => {
    setSelectedUser(user);
    setShowRoleModal(true);
    setLoadingRoles(true);
    
    try {
      const response = await acsApi.admin.getUserRoles(user.id);
      // Get roles from the response
      const assignedRoles = response.roles?.map(r => r.role) || [];
      // If no roles in user_role table, use the primary role from user
      if (assignedRoles.length === 0 && user.role) {
        setUserRoles([user.role]);
      } else {
        setUserRoles(assignedRoles);
      }
    } catch (err) {
      // If endpoint fails, fall back to primary role
      setUserRoles(user.role ? [user.role] : []);
    } finally {
      setLoadingRoles(false);
    }
  };

  // Toggle role selection
  const toggleRole = (role) => {
    setUserRoles(prev => {
      if (prev.includes(role)) {
        // Don't allow removing the last role
        if (prev.length === 1) {
          showError('User must have at least one role');
          return prev;
        }
        return prev.filter(r => r !== role);
      } else {
        return [...prev, role];
      }
    });
  };

  // Save roles
  const handleSaveRoles = async () => {
    if (userRoles.length === 0) {
      showError('Please select at least one role');
      return;
    }
    
    setSavingRoles(true);
    try {
      await acsApi.admin.updateUserRoles(selectedUser.id, userRoles);
      showSuccess(`Roles updated for ${selectedUser.email}`);
      setShowRoleModal(false);
      setSelectedUser(null);
      fetchUsers(pagination.skip);
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to update roles');
    } finally {
      setSavingRoles(false);
    }
  };

  // Close modal
  const closeRoleModal = () => {
    setShowRoleModal(false);
    setSelectedUser(null);
    setUserRoles([]);
  };

  const handleDelete = async (userId, email) => {
    if (!confirm(`Are you sure you want to delete user ${email}?`)) return;
    
    try {
      await acsApi.admin.deleteUser(userId);
      showSuccess(`User ${email} deleted successfully`);
      fetchUsers(pagination.skip);
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to delete user');
    }
  };

  const handlePageChange = (direction) => {
    const newSkip = direction === 'next' 
      ? pagination.skip + pagination.limit 
      : Math.max(0, pagination.skip - pagination.limit);
    fetchUsers(newSkip);
  };

  // Get role badge color class
  const getRoleBadgeClass = (role) => {
    return styles[role] || '';
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>User Management</h1>
        <p>Manage system users and their roles</p>
      </div>

      <div className={styles.filters}>
        <form onSubmit={handleSearch} className={styles.searchForm}>
          <input
            type="text"
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={styles.searchInput}
          />
          <button type="submit" className={styles.searchBtn}>Search</button>
        </form>
        
        <select 
          value={roleFilter} 
          onChange={(e) => setRoleFilter(e.target.value)}
          className={styles.roleFilter}
        >
          <option value="">All Roles</option>
          {roles.map(role => (
            <option key={role} value={role}>{role}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className={styles.loading}>Loading users...</div>
      ) : error ? (
        <div className={styles.error}>{error}</div>
      ) : (
        <>
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role(s)</th>
                  <th>Registered</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan="6" className={styles.empty}>No users found</td>
                  </tr>
                ) : (
                  users.map(user => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>{user.fname} {user.lname}</td>
                      <td>{user.email}</td>
                      <td>
                        <span 
                          className={`${styles.roleBadge} ${getRoleBadgeClass(user.role)}`}
                          onClick={() => openRoleModal(user)}
                          title="Click to manage roles"
                        >
                          {user.role}
                        </span>
                      </td>
                      <td>{user.added_on ? new Date(user.added_on).toLocaleDateString() : 'N/A'}</td>
                      <td>
                        <button 
                          onClick={() => openRoleModal(user)}
                          className={styles.editBtn}
                          title="Manage Roles"
                        >
                          <span className="material-symbols-rounded">manage_accounts</span>
                        </button>
                        <button 
                          onClick={() => handleDelete(user.id, user.email)}
                          className={styles.deleteBtn}
                          title="Delete User"
                        >
                          <span className="material-symbols-rounded">delete</span>
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className={styles.pagination}>
            <span>Showing {pagination.skip + 1} - {Math.min(pagination.skip + pagination.limit, pagination.total)} of {pagination.total}</span>
            <div className={styles.pageButtons}>
              <button 
                onClick={() => handlePageChange('prev')} 
                disabled={pagination.skip === 0}
                className={styles.pageBtn}
              >
                Previous
              </button>
              <button 
                onClick={() => handlePageChange('next')} 
                disabled={pagination.skip + pagination.limit >= pagination.total}
                className={styles.pageBtn}
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}

      {/* Role Management Modal */}
      {showRoleModal && selectedUser && (
        <div className={styles.modalOverlay} onClick={closeRoleModal}>
          <div className={styles.modal} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Manage User Roles</h2>
              <button className={styles.closeBtn} onClick={closeRoleModal}>&times;</button>
            </div>
            
            <div className={styles.modalBody}>
              <div className={styles.userInfo}>
                <div className={styles.userAvatar}>
                  {selectedUser.fname?.[0]?.toUpperCase() || selectedUser.email[0].toUpperCase()}
                </div>
                <div className={styles.userDetails}>
                  <h3>{selectedUser.fname} {selectedUser.lname}</h3>
                  <p>{selectedUser.email}</p>
                </div>
              </div>
              
              {loadingRoles ? (
                <div className={styles.loadingRoles}>Loading roles...</div>
              ) : (
                <>
                  <p className={styles.roleInstructions}>
                    Select one or more roles for this user. The highest priority role will be set as the primary role.
                  </p>
                  
                  <div className={styles.roleGrid}>
                    {roles.map(role => (
                      <div 
                        key={role}
                        className={`${styles.roleCard} ${userRoles.includes(role) ? styles.roleSelected : ''}`}
                        onClick={() => toggleRole(role)}
                      >
                        <div className={styles.roleIcon}>
                          {role === 'admin' && <span className="material-symbols-rounded">admin_panel_settings</span>}
                          {role === 'editor' && <span className="material-symbols-rounded">edit_note</span>}
                          {role === 'reviewer' && <span className="material-symbols-rounded">rate_review</span>}
                          {role === 'author' && <span className="material-symbols-rounded">person</span>}
                        </div>
                        <div className={styles.roleInfo}>
                          <h4>{role.charAt(0).toUpperCase() + role.slice(1)}</h4>
                          <p>
                            {role === 'admin' && 'Full system access and management'}
                            {role === 'editor' && 'Manage papers and reviewers'}
                            {role === 'reviewer' && 'Review submitted papers'}
                            {role === 'author' && 'Submit and manage papers'}
                          </p>
                        </div>
                        <div className={styles.roleCheck}>
                          {userRoles.includes(role) ? (
                            <span className="material-symbols-rounded">check_circle</span>
                          ) : (
                            <span className="material-symbols-rounded">radio_button_unchecked</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {userRoles.length > 0 && (
                    <div className={styles.selectedRoles}>
                      <span className={styles.selectedLabel}>Selected roles:</span>
                      <div className={styles.selectedBadges}>
                        {userRoles.map(role => (
                          <span 
                            key={role} 
                            className={`${styles.selectedBadge} ${styles[role]}`}
                          >
                            {role}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
            
            <div className={styles.modalFooter}>
              <button 
                className={styles.cancelBtn} 
                onClick={closeRoleModal}
                disabled={savingRoles}
              >
                Cancel
              </button>
              <button 
                className={styles.saveBtn}
                onClick={handleSaveRoles}
                disabled={savingRoles || loadingRoles || userRoles.length === 0}
              >
                {savingRoles ? 'Saving...' : 'Save Roles'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminUsers;
