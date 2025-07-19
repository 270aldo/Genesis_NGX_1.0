/**
 * API Client Configuration for NGX Agents
 * Central HTTP client with interceptors and error handling
 * Migrated from GENESIS backend architecture
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API Configuration
const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
};

// Create axios instance
export const apiClient: AxiosInstance = axios.create(API_CONFIG);

// Request interceptor - Add auth token to requests
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // Get token from localStorage (integrated with Zustand authStore)
    const authStorage = localStorage.getItem('ngx-agents-auth');
    let token = null;
    
    if (authStorage) {
      try {
        const parsedStorage = JSON.parse(authStorage);
        token = parsedStorage.state?.token || parsedStorage.token;
      } catch (e) {
        console.warn('Error parsing auth storage:', e);
      }
    }
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add timestamp for cache busting
    if (config.params) {
      config.params._t = Date.now();
    } else {
      config.params = { _t: Date.now() };
    }
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - Handle auth errors and refresh tokens
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Get refresh token from storage
        const authStorage = localStorage.getItem('ngx-agents-auth');
        let refreshToken = null;
        
        if (authStorage) {
          try {
            const parsedStorage = JSON.parse(authStorage);
            refreshToken = parsedStorage.state?.refreshToken || parsedStorage.refreshToken;
          } catch (e) {
            console.warn('Error parsing refresh token:', e);
          }
        }
        
        if (refreshToken) {
          const response = await axios.post(`${API_CONFIG.baseURL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token } = response.data;
          
          // Update auth storage with new token
          if (authStorage) {
            const parsedStorage = JSON.parse(authStorage);
            parsedStorage.state.token = access_token;
            localStorage.setItem('ngx-agents-auth', JSON.stringify(parsedStorage));
          }
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear storage and redirect to login
        localStorage.removeItem('ngx-agents-auth');
        window.location.href = '/signin';
        return Promise.reject(refreshError);
      }
    }
    
    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error);
      return Promise.reject({
        message: 'Network error. Please check your connection.',
        type: 'network_error',
      });
    }
    
    // Handle rate limiting
    if (error.response.status === 429) {
      const retryAfter = error.response.headers['retry-after'] || 60;
      return Promise.reject({
        message: `Rate limit exceeded. Please try again in ${retryAfter} seconds.`,
        type: 'rate_limit',
        retryAfter,
      });
    }
    
    return Promise.reject(error);
  }
);

// WebSocket configuration for real-time features
export const WS_CONFIG = {
  url: import.meta.env.VITE_WS_URL || 'ws://localhost:9000', // A2A Server port
  reconnectInterval: 5000,
  maxReconnectAttempts: 5,
};

// API endpoints configuration (aligned with GENESIS backend)
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    REFRESH: '/api/v1/auth/refresh',
    LOGOUT: '/api/v1/auth/logout',
    VERIFY: '/api/v1/auth/verify',
  },
  
  // Agents (11 specialized agents)
  AGENTS: {
    LIST: '/api/v1/agents',
    EXECUTE: '/api/v1/agents/execute',
    STATUS: '/api/v1/agents/status',
    CAPABILITIES: '/api/v1/agents/capabilities',
    QUERY: '/api/v1/agents/query',
  },
  
  // Chat
  CHAT: {
    SEND: '/api/v1/chat',
    HISTORY: '/api/v1/chat/history',
    STREAM: '/api/v1/chat/stream',
    SEARCH: '/api/v1/chat/search',
    EXPORT: '/api/v1/chat/export',
  },
  
  // User & Profile
  USER: {
    PROFILE: '/api/v1/user/profile',
    PREFERENCES: '/api/v1/user/preferences',
    BIOMETRICS: '/api/v1/user/biometrics',
    PROGRESS: '/api/v1/user/progress',
  },
  
  // Wearables Integration
  WEARABLES: {
    SYNC: '/api/v1/wearables/sync',
    DEVICES: '/api/v1/wearables/devices',
    DATA: '/api/v1/wearables/data',
  },
  
  // Voice & Conversational AI
  VOICE: {
    TRANSCRIBE: '/api/v1/voice/transcribe',
    SYNTHESIZE: '/api/v1/voice/synthesize',
    CONVERSATION: '/api/v1/voice/conversation',
    CONVERSATIONAL: '/api/v1/conversational',
  },
  
  // Visualization
  VISUALIZATION: {
    CHARTS: '/api/v1/visualization/charts',
    REPORTS: '/api/v1/visualization/reports',
    INFOGRAPHICS: '/api/v1/visualization/infographics',
  },
  
  // Notifications
  NOTIFICATIONS: {
    LIST: '/api/v1/notifications',
    MARK_READ: '/api/v1/notifications/read',
    PREFERENCES: '/api/v1/notifications/preferences',
  },
  
  // Feedback
  FEEDBACK: {
    SUBMIT: '/api/v1/feedback',
    ANALYTICS: '/api/v1/feedback/analytics',
  },
  
  // Personality Adapter (PRIME/LONGEVITY)
  PERSONALITY: {
    ADAPT: '/api/v1/personality/adapt',
    PROFILE: '/api/v1/personality/profile',
  },
  
  // Health & Monitoring
  HEALTH: {
    STATUS: '/health',
    SYSTEM: '/api/v1/system/status',
  },
};

export default apiClient;