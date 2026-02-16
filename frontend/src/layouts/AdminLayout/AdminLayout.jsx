import React from 'react';
import { useNavigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import SidebarNav from '../../components/SidebarNav/SidebarNav';
import './AdminLayout.css';

const AdminLayout = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const adminSections = [
    {
      items: [
        { icon: 'dashboard', label: 'Dashboard', path: '/admin' }
      ]
    },
    {
      title: 'Management',
      items: [
        { icon: 'group', label: 'Users', path: '/admin/users' },
        { icon: 'library_books', label: 'Journals', path: '/admin/journals' },
        { icon: 'assignment', label: 'All Submissions', path: '/admin/submissions' }
      ]
    },
    {
      title: 'System',
      items: [
        { icon: 'settings', label: 'Settings', path: '/admin/settings' }
      ]
    }
  ];

  return (
    <div className="admin-layout">
      {/* Admin Sidebar */}
      <SidebarNav 
        sections={adminSections}
        theme="light"
        onLogout={handleLogout}
      />

      {/* Main Content */}
      <main className="admin-main">
        <div className="admin-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default AdminLayout;
