/**
 * Subdomain Detection Utilities
 * 
 * Handles detection and management of journal-specific subdomains
 * for the Breakthrough Publishers platform.
 * 
 * Production URLs: ijest.breakthroughpublishers.com, ijrm.breakthroughpublishers.com, etc.
 * Development: localhost:5173?journal=ijest or ijest.localhost:5173
 */

// Base domain for production
const BASE_DOMAIN = 'breakthroughpublishers.com';

// Subdomains that are reserved and not journal-specific
const EXCLUDED_SUBDOMAINS = ['www', 'api', 'admin', 'static', 'mail', 'smtp', 'ftp'];

/**
 * Get the current subdomain (journal short_form) from the URL
 * 
 * @returns {string|null} The subdomain/journal identifier or null if on main site
 * 
 * @example
 * // On ijest.breakthroughpublishers.com
 * getSubdomain() // returns 'ijest'
 * 
 * // On www.breakthroughpublishers.com or breakthroughpublishers.com
 * getSubdomain() // returns null
 * 
 * // On localhost:5173?journal=ijest (dev mode)
 * getSubdomain() // returns 'ijest'
 */
export const getSubdomain = () => {
  const hostname = window.location.hostname.toLowerCase();
  
  // Development mode: check URL params or localStorage
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    const urlParams = new URLSearchParams(window.location.search);
    const journalParam = urlParams.get('journal');
    
    if (journalParam) {
      return journalParam.toLowerCase();
    }
    
    // Check localStorage for persisted dev journal
    const devJournal = localStorage.getItem('devJournal');
    if (devJournal) {
      return devJournal.toLowerCase();
    }
    
    return null;
  }
  
  // Production mode: extract from hostname
  if (hostname.includes(BASE_DOMAIN)) {
    // Remove base domain from hostname
    const prefix = hostname.replace(BASE_DOMAIN, '').replace(/\.+$/, '');
    
    if (!prefix) {
      return null;
    }
    
    // Get the subdomain (the part before the base domain)
    const parts = prefix.split('.');
    const subdomain = parts[parts.length - 1];
    
    // Exclude reserved subdomains
    if (subdomain && !EXCLUDED_SUBDOMAINS.includes(subdomain.toLowerCase())) {
      return subdomain.toLowerCase();
    }
  }
  
  return null;
};

/**
 * Check if the current site is a journal-specific subdomain
 * 
 * @returns {boolean} True if on a journal subdomain, false if on main site
 */
export const isJournalSubdomain = () => {
  return getSubdomain() !== null;
};

/**
 * Generate a URL for a specific journal's subdomain site
 * 
 * @param {string} shortForm - The journal's short_form identifier
 * @returns {string} The full URL to the journal's subdomain
 * 
 * @example
 * getJournalUrl('ijest')
 * // Production: 'https://ijest.breakthroughpublishers.com'
 * // Development: 'http://localhost:5173?journal=ijest'
 */
export const getJournalUrl = (shortForm) => {
  if (!shortForm) {
    console.warn('getJournalUrl called without shortForm');
    return '/';
  }
  
  const normalizedShortForm = shortForm.toLowerCase();
  
  // Development mode
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    const port = window.location.port ? `:${window.location.port}` : '';
    return `http://${window.location.hostname}${port}?journal=${normalizedShortForm}`;
  }
  
  // Production mode
  return `https://${normalizedShortForm}.${BASE_DOMAIN}`;
};

/**
 * Get the main site URL (removes subdomain context)
 * 
 * @returns {string} The main site URL
 */
export const getMainSiteUrl = () => {
  // Development mode
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    const port = window.location.port ? `:${window.location.port}` : '';
    return `http://${window.location.hostname}${port}`;
  }
  
  // Production mode
  return `https://www.${BASE_DOMAIN}`;
};

/**
 * Set the development journal (for testing subdomain behavior locally)
 * 
 * @param {string|null} shortForm - The journal short_form to simulate, or null to clear
 */
export const setDevJournal = (shortForm) => {
  if (shortForm) {
    localStorage.setItem('devJournal', shortForm.toLowerCase());
  } else {
    localStorage.removeItem('devJournal');
  }
};

/**
 * Clear the development journal setting
 */
export const clearDevJournal = () => {
  localStorage.removeItem('devJournal');
  // Remove journal param from URL if present
  const url = new URL(window.location.href);
  url.searchParams.delete('journal');
  window.history.replaceState({}, '', url.toString());
};

/**
 * Navigate to a specific journal's subdomain
 * Opens in the same window
 * 
 * @param {string} shortForm - The journal's short_form identifier
 */
export const navigateToJournal = (shortForm) => {
  const url = getJournalUrl(shortForm);
  window.location.href = url;
};

/**
 * Navigate back to the main site
 */
export const navigateToMainSite = () => {
  // Development mode
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    clearDevJournal();
    window.location.href = getMainSiteUrl();
  } else {
    window.location.href = getMainSiteUrl();
  }
};

export default {
  getSubdomain,
  isJournalSubdomain,
  getJournalUrl,
  getMainSiteUrl,
  setDevJournal,
  clearDevJournal,
  navigateToJournal,
  navigateToMainSite
};
