import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

/**
 * Custom hook to access auth context
 * Usage: const { user, isAuthenticated, login, logout } = useAuth();
 */
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    console.error('useAuth must be used within AuthProvider. Context is undefined.');
    throw new Error('useAuth must be used within AuthProvider');
  }

  return context;
};
