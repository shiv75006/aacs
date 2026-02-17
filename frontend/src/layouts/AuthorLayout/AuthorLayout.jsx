import React from 'react';
import { Link, useNavigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './AuthorLayout.css';

const AuthorLayout = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="author-layout">
      <aside className="author-sidebar">
        <div className="author-logo">
          <h2>Author Portal</h2>
        </div>

        <nav className="author-nav">
          <div className="nav-section">
            <h4>My Work</h4>
            <Link to="/author/submissions" className="nav-link">
               My Submissions
            </Link>
          </div>
        </nav>
      </aside>

      <main className="author-main">
        <div className="author-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default AuthorLayout;
