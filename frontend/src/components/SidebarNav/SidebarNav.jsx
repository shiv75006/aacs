import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import styles from './SidebarNav.module.css';

/**
 * Reusable Sidebar Navigation component for dashboards
 * @param {Array} navigationItems - Array of nav items with icon, label, path
 * @param {Array} sections - Optional: array of section objects with title and items
 * @param {String} theme - 'light' (default) or 'dark'
 * @param {Function} onLogout - Callback for logout action
 */
const SidebarNav = ({ navigationItems = [], sections = [], theme = 'light', onLogout }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const isActive = (path) => {
    if (path === '/admin' || path === '/editor' || path === '/author' || path === '/reviewer') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  const handleNavClick = () => {
    setIsMobileOpen(false);
  };

  return (
    <>
      {/* Mobile toggle button */}
      <button
        className={`${styles.mobileToggle} ${theme === 'dark' ? styles.darkTheme : ''}`}
        onClick={() => setIsMobileOpen(!isMobileOpen)}
      >
        <span className="material-symbols-rounded">menu</span>
      </button>

      {/* Sidebar */}
      <aside className={`${styles.sidebar} ${styles[theme]} ${isMobileOpen ? styles.mobileOpen : ''}`}>
        <nav className={styles.nav}>
          {sections && sections.length > 0 ? (
            // Render sections
            sections.map((section, idx) => (
              <div key={idx}>
                {section.title && <div className={styles.sectionTitle}>{section.title}</div>}
                <div className={styles.navSection}>
                  {section.items.map((item, itemIdx) => (
                    <Link
                      key={itemIdx}
                      to={item.path}
                      className={`${styles.navLink} ${isActive(item.path) ? styles.active : ''}`}
                      onClick={handleNavClick}
                      title={item.label}
                    >
                      <span className={`${styles.icon} material-symbols-rounded`}>
                        {item.icon}
                      </span>
                      <span className={styles.label}>{item.label}</span>
                      {item.badge && <span className={styles.badge}>{item.badge}</span>}
                    </Link>
                  ))}
                </div>
              </div>
            ))
          ) : (
            // Render flat navigation items
            <div className={styles.navSection}>
              {navigationItems.map((item, idx) => (
                <Link
                  key={idx}
                  to={item.path}
                  className={`${styles.navLink} ${isActive(item.path) ? styles.active : ''}`}
                  onClick={handleNavClick}
                  title={item.label}
                >
                  <span className={`${styles.icon} material-symbols-rounded`}>
                    {item.icon}
                  </span>
                  <span className={styles.label}>{item.label}</span>
                  {item.badge && <span className={styles.badge}>{item.badge}</span>}
                </Link>
              ))}
            </div>
          )}
        </nav>
      </aside>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div
          className={styles.overlay}
          onClick={() => setIsMobileOpen(false)}
        />
      )}
    </>
  );
};

export default SidebarNav;
