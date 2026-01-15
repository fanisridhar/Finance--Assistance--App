import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// Auth API
export const authAPI = {
  register: (email: string, password: string, fullName?: string) =>
    api.post('/api/auth/register', { email, password, full_name: fullName }),
  
  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }),
  
  getMe: () => api.get('/api/auth/me'),
};

// Plaid API
export const plaidAPI = {
  createLinkToken: () => api.post('/api/plaid/link-token'),
  
  exchangeToken: (publicToken: string, institutionId?: string, institutionName?: string) =>
    api.post('/api/plaid/exchange-token', {
      public_token: publicToken,
      institution_id: institutionId,
      institution_name: institutionName,
    }),
  
  sync: () => api.post('/api/plaid/sync'),
};

// Transactions API
export const transactionsAPI = {
  getTransactions: (params?: {
    skip?: number;
    limit?: number;
    start_date?: string;
    end_date?: string;
    category?: string;
    account_id?: number;
  }) => api.get('/api/transactions/', { params }),
  
  getSummary: (days: number = 30) =>
    api.get('/api/transactions/summary', { params: { days } }),
  
  getCategories: () => api.get('/api/transactions/categories'),
};

// Budget API
export const budgetAPI = {
  getBudgets: (activeOnly: boolean = true) =>
    api.get('/api/budget/', { params: { active_only: activeOnly } }),
  
  createBudget: (data: {
    category: string;
    monthly_limit: number;
    period_start: string;
    period_end: string;
  }) => api.post('/api/budget/', data),
  
  updateBudget: (id: number, data: {
    category: string;
    monthly_limit: number;
    period_start: string;
    period_end: string;
  }) => api.put(`/api/budget/${id}`, data),
  
  deleteBudget: (id: number) => api.delete(`/api/budget/${id}`),
};

// Chat API
export const chatAPI = {
  sendMessage: (message: string, conversationId?: string) =>
    api.post('/api/chat/', { message, conversation_id: conversationId }),
};

