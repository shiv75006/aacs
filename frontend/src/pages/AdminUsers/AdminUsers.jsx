import { useState, useEffect, useCallback } from 'react';
import acsApi from '../../api/apiService';
import styles from './AdminUsers.module.css';

const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [pagination, setPagination] = useState({ total: 0, skip: 0, limit: 20 });
  const [editingUser, setEditingUser] = useState(null);

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

  const handleRoleChange = async (userId, newRole) => {
    try {
      await acsApi.admin.updateUserRole(userId, newRole);
      setEditingUser(null);
      fetchUsers(pagination.skip);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update role');
    }
  };

  const handleDelete = async (userId, email) => {
    if (!confirm(`Are you sure you want to delete user ${email}?`)) return;
    
    try {
      await acsApi.admin.deleteUser(userId);
      fetchUsers(pagination.skip);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete user');
    }
  };

  const handlePageChange = (direction) => {
    const newSkip = direction === 'next' 
      ? pagination.skip + pagination.limit 
      : Math.max(0, pagination.skip - pagination.limit);
    fetchUsers(newSkip);
  };

  const roles = ['admin', 'author', 'editor', 'reviewer'];

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
                  <th>Role</th>
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
                        {editingUser === user.id ? (
                          <select 
                            defaultValue={user.role}
                            onChange={(e) => handleRoleChange(user.id, e.target.value)}
                            onBlur={() => setEditingUser(null)}
                            autoFocus
                            className={styles.roleSelect}
                          >
                            {roles.map(role => (
                              <option key={role} value={role}>{role}</option>
                            ))}
                          </select>
                        ) : (
                          <span 
                            className={`${styles.roleBadge} ${styles[user.role]}`}
                            onClick={() => setEditingUser(user.id)}
                            title="Click to change role"
                          >
                            {user.role}
                          </span>
                        )}
                      </td>
                      <td>{user.added_on ? new Date(user.added_on).toLocaleDateString() : 'N/A'}</td>
                      <td>
                        <button 
                          onClick={() => setEditingUser(user.id)}
                          className={styles.editBtn}
                          title="Edit Role"
                        >
                          <span className="material-symbols-rounded">edit</span>
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
    </div>
  );
};

export default AdminUsers;
