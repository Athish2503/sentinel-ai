import axios from 'axios';

// Get backend URL from localStorage if available (helps configure settings dynamically)
const getBaseURL = () => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('sentinel_backend_url');
    if (saved) return saved;
  }
  return 'http://localhost:8000/api/v1';
};

export const apiClient = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Interceptor to dynamically update the base URL on request if localStorage changes
apiClient.interceptors.request.use((config) => {
  const currentBaseURL = getBaseURL();
  if (config.baseURL !== currentBaseURL) {
    config.baseURL = currentBaseURL;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});
