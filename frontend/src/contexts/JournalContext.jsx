/**
 * Journal Context Provider
 * 
 * Provides journal context based on subdomain detection.
 * When accessing the site via a journal subdomain (e.g., ijest.breakthroughpublishers.com),
 * this context provides the journal data to all child components.
 */

import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import { getSubdomain, isJournalSubdomain } from '../utils/subdomain';
import { acsApi } from '../api/apiService';

// Create the context
export const JournalContext = createContext(null);

/**
 * JournalProvider Component
 * 
 * Wraps the application and provides journal context based on subdomain.
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Child components
 */
export const JournalProvider = ({ children }) => {
  // Current journal data (if on a subdomain)
  const [currentJournal, setCurrentJournal] = useState(null);
  // Extended journal details (about, scope, guidelines, etc.)
  const [journalDetails, setJournalDetails] = useState(null);
  // Loading state
  const [loading, setLoading] = useState(true);
  // Error state
  const [error, setError] = useState(null);
  // Whether we're on a journal subdomain
  const [isJournalSite, setIsJournalSite] = useState(false);
  // The detected subdomain
  const [subdomain, setSubdomain] = useState(null);

  /**
   * Fetch journal data by subdomain (short_form)
   */
  const fetchJournalBySubdomain = useCallback(async (subdomainValue) => {
    if (!subdomainValue) {
      setLoading(false);
      return;
    }

    try {
      setError(null);
      const response = await acsApi.journals.getBySubdomain(subdomainValue);
      setCurrentJournal(response);
      setIsJournalSite(true);
      
      // Also fetch extended details
      try {
        const details = await acsApi.journals.getDetails(response.id);
        setJournalDetails(details);
      } catch (detailsErr) {
        console.warn('Could not fetch journal details:', detailsErr);
        // Non-critical error, don't set main error state
      }
    } catch (err) {
      console.error('Failed to fetch journal for subdomain:', subdomainValue, err);
      setError(`Journal "${subdomainValue}" not found`);
      setCurrentJournal(null);
      setIsJournalSite(false);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Refresh journal data
   */
  const refreshJournal = useCallback(async () => {
    if (subdomain) {
      setLoading(true);
      await fetchJournalBySubdomain(subdomain);
    }
  }, [subdomain, fetchJournalBySubdomain]);

  // Initialize on mount - detect subdomain and fetch journal
  useEffect(() => {
    const detectedSubdomain = getSubdomain();
    setSubdomain(detectedSubdomain);

    if (detectedSubdomain) {
      fetchJournalBySubdomain(detectedSubdomain);
    } else {
      setIsJournalSite(false);
      setLoading(false);
    }
  }, [fetchJournalBySubdomain]);

  // Context value
  const value = {
    // Journal data
    currentJournal,
    journalDetails,
    
    // State flags
    loading,
    error,
    isJournalSite,
    subdomain,
    
    // Actions
    refreshJournal,
    
    // Computed values
    journalId: currentJournal?.id || null,
    journalName: currentJournal?.name || null,
    journalShortForm: currentJournal?.short_form || subdomain,
  };

  return (
    <JournalContext.Provider value={value}>
      {children}
    </JournalContext.Provider>
  );
};

/**
 * Custom hook to access journal context
 * 
 * @returns {Object} Journal context value
 * @throws {Error} If used outside of JournalProvider
 * 
 * @example
 * const { currentJournal, isJournalSite, loading } = useJournalContext();
 * 
 * if (isJournalSite && currentJournal) {
 *   return <JournalHomePage journal={currentJournal} />;
 * }
 */
export const useJournalContext = () => {
  const context = useContext(JournalContext);
  
  if (context === undefined) {
    throw new Error('useJournalContext must be used within a JournalProvider');
  }
  
  return context;
};

export default JournalProvider;
