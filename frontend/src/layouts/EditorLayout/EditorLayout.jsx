import React from 'react';
import { useNavigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import SidebarNav from '../../components/SidebarNav/SidebarNav';
import './EditorLayout.css';

const EditorLayout = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const editorSections = [
    {
      items: [
        { icon: 'dashboard', label: 'Dashboard', path: '/editor/dashboard' }
      ]
    },
    {
      title: 'Papers',
      items: [
        { icon: 'assignment', label: 'Paper Queue', path: '/editor/papers' },
        { icon: 'done_all', label: 'Pending Decision', path: '/editor/papers/pending-decision' }
      ]
    },
    {
      title: 'Reviewers',
      items: [
        { icon: 'group', label: 'Available Reviewers', path: '/editor/reviewers' }
      ]
    }
  ];

  return (
    <div className="editor-layout">
      {/* Editor Sidebar with dark theme */}
      <SidebarNav 
        sections={editorSections}
        theme="dark"
        onLogout={handleLogout}
      />

      <main className="editor-main">
        <div className="editor-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default EditorLayout;
