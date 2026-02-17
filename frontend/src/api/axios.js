import axios from 'axios';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // FastAPI backend URL
  timeout: 300000, // 5 minutes timeout for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add authentication token if available
apiClient.interceptors.request.use(
  (config) => {
    // Check if skipAuth flag is set
    if (!config.skipAuth) {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    // Remove the skipAuth flag from config before sending
    delete config.skipAuth;
    
    // Let axios handle Content-Type for multipart/form-data (remove default JSON header)
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    
    console.log(`[Axios] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[Axios Response] ${response.status} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error(`[Axios Error] ${error.response?.status || 'Network'} ${error.config?.url}`, error.response?.data || error.message);
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      // Optionally redirect to login page
    }
    return Promise.reject(error);
  }
);

export default apiClient;