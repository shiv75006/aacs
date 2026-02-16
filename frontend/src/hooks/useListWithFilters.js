import { useState, useCallback, useEffect } from 'react';
import { useToast } from './useToast';

/**
 * Custom hook for managing list data with filtering, pagination, and error handling
 * @param {Function} fetchFn - Async function(skip, limit, filters) to fetch data
 * @param {Object} initialFilters - Initial filter values
 * @param {number} initialLimit - Items per page
 * @returns {Object} Data state, loading, error, filters, and pagination
 */
export const useListWithFilters = (
  fetchFn,
  initialFilters = {},
  initialLimit = 20
) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    skip: 0,
    limit: initialLimit,
    currentPage: 1,
  });
  const [filters, setFilters] = useState(initialFilters);
  const toast = useToast();

  /**
   * Fetch data with current filters and pagination
   */
  const fetchData = useCallback(
    async (skip = 0, currentFilters = filters) => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetchFn(skip, pagination.limit, currentFilters);

        if (response) {
          // Extract data array (could be under different keys)
          const dataArray = response.data ||
            response.papers ||
            response.users ||
            response.reviewers ||
            response.items ||
            response.history ||
            response.assignments ||
            [];

          setData(Array.isArray(dataArray) ? dataArray : []);

          // Update pagination
          if (response.total !== undefined) {
            setPagination((prev) => ({
              ...prev,
              total: response.total,
              skip: response.skip !== undefined ? response.skip : skip,
              currentPage: Math.floor((response.skip || skip) / pagination.limit) + 1,
            }));
          }
        }
      } catch (err) {
        const errorMessage = err.response?.data?.message || err.message || 'Failed to fetch data';
        setError(errorMessage);
        if (toast && toast.error) {
          toast.error(errorMessage);
        }
        setData([]);
      } finally {
        setLoading(false);
      }
    },
    [fetchFn, pagination.limit, filters, toast]
  );

  /**
   * Handle filter change and reset to page 1
   */
  const handleFilterChange = useCallback((filterKey, filterValue) => {
    setFilters((prev) => ({
      ...prev,
      [filterKey]: filterValue,
    }));
    // Reset to first page when filters change
    setPagination((prev) => ({
      ...prev,
      currentPage: 1,
      skip: 0,
    }));
  }, []);

  /**
   * Handle multiple filter changes at once
   */
  const setMultipleFilters = useCallback((newFilters) => {
    setFilters((prev) => ({
      ...prev,
      ...newFilters,
    }));
    setPagination((prev) => ({
      ...prev,
      currentPage: 1,
      skip: 0,
    }));
  }, []);

  /**
   * Clear all filters
   */
  const clearFilters = useCallback(() => {
    setFilters(initialFilters);
    setPagination((prev) => ({
      ...prev,
      currentPage: 1,
      skip: 0,
    }));
  }, [initialFilters]);

  /**
   * Go to specific page
   */
  const goToPage = useCallback((page) => {
    const newSkip = (page - 1) * pagination.limit;
    setPagination((prev) => ({
      ...prev,
      currentPage: page,
      skip: newSkip,
    }));
  }, [pagination.limit]);

  /**
   * Next page
   */
  const nextPage = useCallback(() => {
    const totalPages = Math.ceil(pagination.total / pagination.limit);
    if (pagination.currentPage < totalPages) {
      goToPage(pagination.currentPage + 1);
    }
  }, [pagination, goToPage]);

  /**
   * Previous page
   */
  const prevPage = useCallback(() => {
    if (pagination.currentPage > 1) {
      goToPage(pagination.currentPage - 1);
    }
  }, [pagination.currentPage, goToPage]);

  /**
   * Refresh data with current filters
   */
  const refresh = useCallback(() => {
    fetchData(pagination.skip, filters);
  }, [fetchData, pagination.skip, filters]);

  // Fetch data when filters or pagination changes
  useEffect(() => {
    fetchData(pagination.skip);
  }, [filters, pagination.skip]);

  const totalPages = Math.ceil(pagination.total / pagination.limit);

  return {
    data,
    loading,
    error,
    pagination: {
      ...pagination,
      totalPages,
    },
    filters,
    handleFilterChange,
    setMultipleFilters,
    clearFilters,
    goToPage,
    nextPage,
    prevPage,
    refresh,
  };
};

export default useListWithFilters;
