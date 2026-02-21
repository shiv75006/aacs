import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import './RoleSwitcher.css';

const ROLE_CONFIG = {
  author: {
    label: 'Author',
    icon: 'edit_document',
    color: '#3b82f6',
    dashboardPath: '/author',
    description: 'Submit and manage papers'
  },
  reviewer: {
    label: 'Reviewer',
    icon: 'rate_review',
    color: '#10b981',
    dashboardPath: '/reviewer',
    description: 'Review assigned papers'
  },
  editor: {
    label: 'Editor',
    icon: 'edit_note',
    color: '#f59e0b',
    dashboardPath: '/editor',
    description: 'Manage journal submissions'
  },
  admin: {
    label: 'Admin',
    icon: 'admin_panel_settings',
    color: '#ef4444',
    dashboardPath: '/admin',
    description: 'System administration'
  }
};

const RoleSwitcher = () => {
  const { roles, activeRole, switchRole } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [switching, setSwitching] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Don't render if user has only one role or no roles
  const approvedRoles = roles.filter(r => r.status === 'approved');
  if (approvedRoles.length <= 1) {
    return null;
  }

  const currentRoleConfig = ROLE_CONFIG[activeRole?.toLowerCase()] || ROLE_CONFIG.author;

  const handleRoleSwitch = async (newRole) => {
    if (newRole === activeRole?.toLowerCase() || switching) return;

    try {
      setSwitching(true);
      await switchRole(newRole);
      setIsOpen(false);
      
      // Navigate to the new role's dashboard
      const config = ROLE_CONFIG[newRole];
      if (config?.dashboardPath) {
        navigate(config.dashboardPath);
      }
    } catch (err) {
      console.error('Failed to switch role:', err);
    } finally {
      setSwitching(false);
    }
  };

  return (
    <div className="role-switcher" ref={dropdownRef}>
      <button 
        className="role-switcher-trigger"
        onClick={() => setIsOpen(!isOpen)}
        disabled={switching}
        style={{ '--role-color': currentRoleConfig.color }}
      >
        <span className="material-symbols-rounded">{currentRoleConfig.icon}</span>
        <span className="role-name">{currentRoleConfig.label}</span>
        <span className={`material-symbols-rounded chevron ${isOpen ? 'open' : ''}`}>
          expand_more
        </span>
      </button>

      {isOpen && (
        <div className="role-dropdown">
          <div className="dropdown-header">
            <span>Switch Role</span>
          </div>
          <div className="dropdown-options">
            {approvedRoles.map((roleItem) => {
              const roleName = roleItem.role?.toLowerCase();
              const config = ROLE_CONFIG[roleName];
              if (!config) return null;

              const isActive = activeRole?.toLowerCase() === roleName;

              return (
                <button
                  key={roleItem.id}
                  className={`role-option ${isActive ? 'active' : ''}`}
                  onClick={() => handleRoleSwitch(roleName)}
                  disabled={isActive || switching}
                  style={{ '--role-color': config.color }}
                >
                  <div className="role-option-icon">
                    <span className="material-symbols-rounded">{config.icon}</span>
                  </div>
                  <div className="role-option-info">
                    <span className="role-option-label">{config.label}</span>
                    <span className="role-option-desc">{config.description}</span>
                  </div>
                  {isActive && (
                    <span className="material-symbols-rounded role-check">check</span>
                  )}
                  {switching && !isActive && (
                    <span className="material-symbols-rounded role-loading">sync</span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default RoleSwitcher;
