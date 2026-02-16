import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import logo from '../../assets/aacs_logo_new.png';
import styles from './Header.module.css';

const Header = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    navigate('/');
  };

  const getInitials = () => {
    if (user?.fname && user?.lname) {
      return `${user.fname[0]}${user.lname[0]}`.toUpperCase();
    }
    return user?.email?.[0]?.toUpperCase() || 'U';
  };

  return (
    <nav className={styles.navbar}>
      <div className={styles.container}>
        <Link className={styles.brand} to="/">
          <img src={logo} alt="AACS Logo" className={styles.logo} />
        </Link>
        
        <ul className={styles.navList}>
          <li><Link className={styles.navLink} to="/">Home</Link></li>
          <li><Link className={styles.navLink} to="/journals">Journals</Link></li>
          <li><Link className={styles.navLink} to="/submit">Submit Paper</Link></li>
          
          {isAuthenticated && user?.role === 'admin' && (
            <li><Link className={styles.navLink} to="/admin">Dashboard</Link></li>
          )}

          {isAuthenticated && user?.role === 'editor' && (
            <li><Link className={styles.navLink} to="/editor">Dashboard</Link></li>
          )}

          {isAuthenticated && user?.role === 'reviewer' && (
            <li><Link className={styles.navLink} to="/reviewer">Dashboard</Link></li>
          )}

          {isAuthenticated ? (
            <li className={styles.userMenu}>
              <button 
                className={styles.userToggle}
                onClick={() => setMenuOpen(!menuOpen)}
              >
                <span className={styles.avatar}>{getInitials()}</span>
                <div className={styles.userInfo}>
                  <span className={styles.userName}>{user?.fname} {user?.lname}</span>
                  <span className={styles.userRole}>{user?.role}</span>
                </div>
              </button>
              {menuOpen && (
                <div className={styles.dropdown}>
                  {user?.role === 'admin' && (
                    <Link to="/admin" className={styles.dropdownItem} onClick={() => setMenuOpen(false)}>Admin Dashboard</Link>
                  )}
                  {user?.role === 'author' && (
                    <Link to="/author" className={styles.dropdownItem} onClick={() => setMenuOpen(false)}>My Submissions</Link>
                  )}
                  {user?.role === 'editor' && (
                    <Link to="/editor" className={styles.dropdownItem} onClick={() => setMenuOpen(false)}>Editor Panel</Link>
                  )}
                  {user?.role === 'reviewer' && (
                    <Link to="/reviewer" className={styles.dropdownItem} onClick={() => setMenuOpen(false)}>Review Panel</Link>
                  )}
                  <Link to="/profile" className={styles.dropdownItem} onClick={() => setMenuOpen(false)}>Profile</Link>
                  <button 
                    onClick={handleLogout} 
                    className={`${styles.dropdownItem} ${styles.logout}`}
                  >
                    Logout
                  </button>
                </div>
              )}
            </li>
          ) : (
            <>
              <li><Link className={styles.navLink} to="/login">Login</Link></li>
              <li>
                <Link className={`${styles.navLink} ${styles.signupBtn}`} to="/signup">
                  Sign Up
                </Link>
              </li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Header;