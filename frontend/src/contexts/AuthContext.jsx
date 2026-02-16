import React, { createContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';
import { formatApiError } from '../utils/errorFormatter';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const initializeAuth = () => {
      try {
        const token = authService.getToken();
        const storedUser = authService.getStoredUser();

        if (token && storedUser) {
          setUser(storedUser);
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
        }
      } catch (err) {
        console.error('Error initializing auth:', err);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Login function
  const login = useCallback(async (email, password) => {
    try {
      setLoading(true);
      setError(null);

      const response = await authService.login(email, password);

      // Store user data
      const userData = {
        id: response.id || response.user?.id,
        email: response.email || response.user?.email,
        role: response.role || response.user?.role,
        fname: response.fname || response.user?.fname,
        lname: response.lname || response.user?.lname,
      };

      authService.storeUser(userData);
      setUser(userData);
      setIsAuthenticated(true);

      return userData;
    } catch (err) {
      const formattedError = formatApiError(err);
      setError(formattedError);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Signup function
  const signup = useCallback(async (formData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await authService.signup(formData);

      // Store user data
      const userData = {
        id: response.id || response.user?.id,
        email: response.email || response.user?.email,
        role: response.role || response.user?.role,
        fname: response.fname || response.user?.fname,
        lname: response.lname || response.user?.lname,
      };

      authService.storeUser(userData);
      setUser(userData);
      setIsAuthenticated(true);

      return userData;
    } catch (err) {
      const formattedError = formatApiError(err);
      setError(formattedError);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Logout function
  const logout = useCallback(() => {
    try {
      authService.logout();
      setUser(null);
      setIsAuthenticated(false);
      setError(null);
    } catch (err) {
      console.error('Error during logout:', err);
    }
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Refresh user data (sync with server)
  const refreshUser = useCallback(async () => {
    try {
      setLoading(true);
      const response = await authService.getCurrentUser();
      
      const userData = {
        id: response.id,
        email: response.email,
        role: response.role,
        fname: response.fname,
        lname: response.lname,
      };

      authService.storeUser(userData);
      setUser(userData);

      return userData;
    } catch (err) {
      console.error('Error refreshing user:', err);
      // If refresh fails, logout user
      logout();
      throw err;
    } finally {
      setLoading(false);
    }
  }, [logout]);

  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    signup,
    logout,
    clearError,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
