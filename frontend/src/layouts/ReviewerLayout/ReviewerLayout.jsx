import React from 'react';
import { Link, useNavigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import SidebarNav from '../../components/SidebarNav/SidebarNav';
import './ReviewerLayout.css';

const ReviewerLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const reviewerNavItems = [
    { label: 'Dashboard', icon: 'dashboard', path: '/reviewer/dashboard' },
    { label: 'My Assignments', icon: 'assignment', path: '/reviewer/assignments' },
    { label: 'Review History', icon: 'history', path: '/reviewer/history' },
    { label: 'Profile', icon: 'person', path: '/reviewer/profile' },
    { label: 'Guidelines', icon: 'help', path: '/reviewer/guidelines' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="reviewer-layout">
      <SidebarNav 
        navigationItems={reviewerNavItems}
        theme="light"
        onLogout={handleLogout}
      />

      <main className="reviewer-main">
        <div className="reviewer-header">
          <div className="reviewer-header-left">
            <h1>Reviewer Portal</h1>
          </div>
          <div className="reviewer-header-right">
            <span className="welcome-text">Welcome, {user?.fname || 'Reviewer'}!</span>
          </div>
        </div>

        <div className="reviewer-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default ReviewerLayout;
