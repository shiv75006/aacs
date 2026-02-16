import apiClient from './axios';

// Export the API client instance
export const getApiClient = () => apiClient;

// API service functions for common HTTP operations
export const apiService = {
  // GET request
  get: async (endpoint, config = {}) => {
    try {
      const response = await apiClient.get(endpoint, config);
      return response.data;
    } catch (error) {
      console.error('GET request failed:', error);
      throw error;
    }
  },

  // POST request
  post: async (endpoint, data, config = {}) => {
    try {
      const response = await apiClient.post(endpoint, data, config);
      return response.data;
    } catch (error) {
      console.error('POST request failed:', error);
      throw error;
    }
  },

  // PUT request
  put: async (endpoint, data) => {
    try {
      const response = await apiClient.put(endpoint, data);
      return response.data;
    } catch (error) {
      console.error('PUT request failed:', error);
      throw error;
    }
  },

  // DELETE request
  delete: async (endpoint) => {
    try {
      const response = await apiClient.delete(endpoint);
      return response.data;
    } catch (error) {
      console.error('DELETE request failed:', error);
      throw error;
    }
  },

  // PATCH request
  patch: async (endpoint, data) => {
    try {
      const response = await apiClient.patch(endpoint, data);
      return response.data;
    } catch (error) {
      console.error('PATCH request failed:', error);
      throw error;
    }
  }
};

// Example specific API functions for AACS system
export const acsApi = {
  // Authentication
  login: (credentials) => apiService.post('auth/login/', credentials),
  logout: () => apiService.post('auth/logout/'),
  register: (userData) => apiService.post('auth/register/', userData),

  // User management
  getUserProfile: () => apiService.get('users/profile/'),
  updateUserProfile: (data) => apiService.put('users/profile/', data),

  // Journals
  journals: {
    list: (skip = 0, limit = 10) => 
      apiService.get(`/api/v1/journals/?skip=${skip}&limit=${limit}`),
    listJournals: (skip = 0, limit = 3) => 
      apiService.get(`/api/v1/journals/?skip=${skip}&limit=${limit}`),
    getDetail: (id) => apiService.get(`/api/v1/journals/${id}`),
  },

  // Articles/News
  articles: {
    list: (skip = 0, limit = 10) => 
      apiService.get(`/api/v1/articles/?skip=${skip}&limit=${limit}`),
    latest: (limit = 5) => 
      apiService.get(`/api/v1/articles/latest?limit=${limit}`),
    getDetail: (id) => apiService.get(`/api/v1/articles/${id}`),
    getByJournal: (journalId, skip = 0, limit = 10) => 
      apiService.get(`/api/v1/articles/journal/${journalId}?skip=${skip}&limit=${limit}`),
  },

  // Legacy methods for backwards compatibility
  getJournals: (skip = 0, limit = 20, search = '') => 
    apiService.get(`/api/v1/journals/?skip=${skip}&limit=${limit}${search ? `&search=${search}` : ''}`),
  getJournalDetail: (id) => apiService.get(`/api/v1/journals/${id}`),

  // Admin endpoints
  admin: {
    getDashboardStats: () => apiService.get('/api/v1/admin/dashboard/stats'),
    listUsers: (skip = 0, limit = 20, search = '', role = '') =>
      apiService.get(`/api/v1/admin/users?skip=${skip}&limit=${limit}${search ? `&search=${search}` : ''}${role ? `&role=${role}` : ''}`),
    updateUserRole: (userId, role) => apiService.post(`/api/v1/admin/users/${userId}/role`, { role }),
    deleteUser: (userId) => apiService.delete(`/api/v1/admin/users/${userId}`),
    listAllJournals: (skip = 0, limit = 20, search = '') =>
      apiService.get(`/api/v1/admin/journals?skip=${skip}&limit=${limit}${search ? `&search=${search}` : ''}`),
    deleteJournal: (journalId) => apiService.delete(`/api/v1/journals/${journalId}`),
    listAllPapers: (skip = 0, limit = 50, status = '') =>
      apiService.get(`/api/v1/admin/papers?skip=${skip}&limit=${limit}${status ? `&status=${status}` : ''}`),
    getPaperDetail: (paperId) => apiService.get(`/api/v1/admin/papers/${paperId}`),
    getRecentActivity: (limit = 20) => apiService.get(`/api/v1/admin/activity?limit=${limit}`),
    getPapersByStatus: () => apiService.get('/api/v1/admin/stats/papers-by-status'),
  },

  // Author endpoints
  author: {
    getDashboardStats: () => apiService.get('/api/v1/author/dashboard/stats'),
    listSubmissions: (skip = 0, limit = 20, statusFilter = '') =>
      apiService.get(`/api/v1/author/submissions?skip=${skip}&limit=${limit}${statusFilter ? `&status_filter=${statusFilter}` : ''}`),
    getSubmissionDetail: (paperId) => apiService.get(`/api/v1/author/submissions/${paperId}`),
    submitPaper: ({ title, abstract, keywords, journal_id, file }) => {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('abstract', abstract);
      formData.append('keywords', keywords);
      formData.append('journal_id', journal_id);
      formData.append('file', file);
      // Let axios interceptor handle Content-Type for FormData
      return apiService.post('/api/v1/author/submit-paper', formData);
    },
    getPaperComments: (paperId) => apiService.get(`/api/v1/author/submissions/${paperId}/comments`),
  },

  // Editor endpoints
  editor: {
    getDashboardStats: () => apiService.get('/api/v1/editor/dashboard/stats'),
    getPaperQueue: (skip = 0, limit = 20, statusFilter = '') =>
      apiService.get(`/api/v1/editor/paper-queue?skip=${skip}&limit=${limit}${statusFilter ? `&status_filter=${statusFilter}` : ''}`),
    assignReviewer: (paperId, reviewerId) =>
      apiService.post(`/api/v1/editor/papers/${paperId}/assign-reviewer`, { reviewer_id: reviewerId }),
    updatePaperStatus: (paperId, status, comments = '') =>
      apiService.post(`/api/v1/editor/papers/${paperId}/status`, { status, comments }),
    getPaperReviews: (paperId) => apiService.get(`/api/v1/editor/papers/${paperId}/reviews`),
    listReviewers: (skip = 0, limit = 50, search = '') =>
      apiService.get(`/api/v1/editor/reviewers?skip=${skip}&limit=${limit}${search ? `&search=${search}` : ''}`),
    getPendingActions: () => apiService.get('/api/v1/editor/pending-actions'),
    // Invitation endpoints
    inviteReviewer: (paperId, reviewerEmail, dueDays = 14) =>
      apiService.post(`/api/v1/editor/papers/${paperId}/invite-reviewer?reviewer_email=${encodeURIComponent(reviewerEmail)}&due_days=${dueDays}`),
    assignReviewerToPaper: (paperId, reviewerId, dueDays = 14) =>
      apiService.post(`/api/v1/editor/papers/${paperId}/assign-reviewer`, { reviewer_id: reviewerId, due_days: dueDays }),
    
    // Phase 6: Editor Decision Panel
    getPapersPendingDecision: (skip = 0, limit = 20) =>
      apiService.get(`/api/v1/editor/papers-pending-decision?skip=${skip}&limit=${limit}`),
    makePaperDecision: (paperId, decisionData) =>
      apiService.post(`/api/v1/editor/papers/${paperId}/decision`, decisionData),
    getPaperDecision: (paperId) =>
      apiService.get(`/api/v1/editor/papers/${paperId}/decision`),
  },

  // Invitation endpoints (public, no auth required)
  invitations: {
    getInvitationStatus: (token) => 
      apiService.get(`/api/v1/editor/invitations/status/${token}`, { skipAuth: true }),
    acceptInvitation: (token) =>
      apiService.post(`/api/v1/editor/invitations/${token}/accept`, {}, { skipAuth: true }),
    declineInvitation: (token, reason = '') =>
      apiService.post(`/api/v1/editor/invitations/${token}/decline?${reason ? `reason=${encodeURIComponent(reason)}` : ''}`, {}, { skipAuth: true }),
  },

  // Reviewer endpoints
  reviewer: {
    getDashboardStats: () => apiService.get('/api/v1/reviewer/dashboard/stats'),
    listAssignments: (skip = 0, limit = 20, statusFilter = '', sortBy = 'due_soon') =>
      apiService.get(`/api/v1/reviewer/assignments?skip=${skip}&limit=${limit}${statusFilter ? `&status_filter=${statusFilter}` : ''}&sort_by=${sortBy}`),
    getAssignmentDetail: (reviewId) => apiService.get(`/api/v1/reviewer/assignments/${reviewId}`),
    submitReview: (reviewId, reviewData) =>
      apiService.post(`/api/v1/reviewer/assignments/${reviewId}/submit-review`, {
        technical_quality: reviewData.technicalQuality,
        clarity: reviewData.clarity,
        originality: reviewData.originality,
        significance: reviewData.significance,
        overall_rating: reviewData.overallRating,
        author_comments: reviewData.authorComments,
        confidential_comments: reviewData.confidentialComments,
        recommendation: reviewData.recommendation
      }),
    getReviewHistory: () => apiService.get('/api/v1/reviewer/history'),
    getReviewerProfile: () => apiService.get('/api/v1/reviewer/profile'),
  },
};

export default acsApi;