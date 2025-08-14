import { apiClient, API_ENDPOINTS } from '../client';
import axios from 'axios';

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  }))
}));

const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('apiClient configuration', () => {
    it('creates axios instance with correct base configuration', () => {
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: expect.any(String),
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('uses environment variable for base URL when available', () => {
      const originalEnv = process.env.VITE_API_URL;
      process.env.VITE_API_URL = 'https://test-api.example.com';

      // Re-import to get new configuration
      jest.resetModules();
      require('../client');

      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: 'https://test-api.example.com'
        })
      );

      process.env.VITE_API_URL = originalEnv;
    });

    it('falls back to default URL when environment variable is not set', () => {
      const originalEnv = process.env.VITE_API_URL;
      delete process.env.VITE_API_URL;

      jest.resetModules();
      require('../client');

      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: 'http://localhost:8000'
        })
      );

      process.env.VITE_API_URL = originalEnv;
    });
  });

  describe('API_ENDPOINTS', () => {
    it('contains all required authentication endpoints', () => {
      expect(API_ENDPOINTS.AUTH).toEqual({
        LOGIN: '/api/v1/auth/login',
        REGISTER: '/api/v1/auth/register',
        REFRESH: '/api/v1/auth/refresh',
        LOGOUT: '/api/v1/auth/logout',
        VERIFY_EMAIL: '/api/v1/auth/verify-email',
        FORGOT_PASSWORD: '/api/v1/auth/forgot-password',
        RESET_PASSWORD: '/api/v1/auth/reset-password',
        PROFILE: '/api/v1/auth/profile'
      });
    });

    it('contains all required agent endpoints', () => {
      expect(API_ENDPOINTS.AGENTS).toEqual({
        LIST: '/api/v1/agents',
        DETAIL: (id: string) => `/api/v1/agents/${id}`,
        CHAT: '/api/v1/agents/chat',
        ORCHESTRATOR: '/api/v1/agents/orchestrator',
        STATUS: '/api/v1/agents/status',
        HISTORY: '/api/v1/agents/history',
        ANALYTICS: '/api/v1/agents/analytics'
      });
    });

    it('contains all required chat endpoints', () => {
      expect(API_ENDPOINTS.CHAT).toEqual({
        CONVERSATIONS: '/api/v1/chat/conversations',
        CONVERSATION: (id: string) => `/api/v1/chat/conversations/${id}`,
        MESSAGES: (conversationId: string) => `/api/v1/chat/conversations/${conversationId}/messages`,
        STREAM: '/api/v1/chat/stream',
        EXPORT: (conversationId: string) => `/api/v1/chat/conversations/${conversationId}/export`,
        SEARCH: '/api/v1/chat/search'
      });
    });

    it('contains all required voice endpoints', () => {
      expect(API_ENDPOINTS.VOICE).toEqual({
        TRANSCRIBE: '/api/v1/voice/transcribe',
        SYNTHESIZE: '/api/v1/voice/synthesize',
        CONVERSATIONAL: '/api/v1/voice/conversational',
        VOICES: '/api/v1/voice/voices',
        SETTINGS: '/api/v1/voice/settings'
      });
    });

    it('contains all required biometrics endpoints', () => {
      expect(API_ENDPOINTS.BIOMETRICS).toEqual({
        PROFILE: '/api/v1/biometrics/profile',
        UPDATE: '/api/v1/biometrics/update',
        HISTORY: '/api/v1/biometrics/history',
        SYNC: '/api/v1/biometrics/sync',
        DEVICES: '/api/v1/biometrics/devices',
        ANALYTICS: '/api/v1/biometrics/analytics'
      });
    });

    it('contains all required nutrition endpoints', () => {
      expect(API_ENDPOINTS.NUTRITION).toEqual({
        PLANS: '/api/v1/nutrition/plans',
        PLAN: (id: string) => `/api/v1/nutrition/plans/${id}`,
        LOG: '/api/v1/nutrition/log',
        ANALYSIS: '/api/v1/nutrition/analysis',
        GOALS: '/api/v1/nutrition/goals',
        RECOMMENDATIONS: '/api/v1/nutrition/recommendations'
      });
    });

    it('contains all required training endpoints', () => {
      expect(API_ENDPOINTS.TRAINING).toEqual({
        WORKOUTS: '/api/v1/training/workouts',
        WORKOUT: (id: string) => `/api/v1/training/workouts/${id}`,
        EXERCISES: '/api/v1/training/exercises',
        PROGRESS: '/api/v1/training/progress',
        RECOMMENDATIONS: '/api/v1/training/recommendations',
        ANALYTICS: '/api/v1/training/analytics'
      });
    });

    it('generates dynamic URLs correctly', () => {
      expect(API_ENDPOINTS.AGENTS.DETAIL('test-agent')).toBe('/api/v1/agents/test-agent');
      expect(API_ENDPOINTS.CHAT.CONVERSATION('conv-123')).toBe('/api/v1/chat/conversations/conv-123');
      expect(API_ENDPOINTS.CHAT.MESSAGES('conv-123')).toBe('/api/v1/chat/conversations/conv-123/messages');
      expect(API_ENDPOINTS.NUTRITION.PLAN('plan-456')).toBe('/api/v1/nutrition/plans/plan-456');
      expect(API_ENDPOINTS.TRAINING.WORKOUT('workout-789')).toBe('/api/v1/training/workouts/workout-789');
    });

    it('handles special characters in dynamic URLs', () => {
      expect(API_ENDPOINTS.AGENTS.DETAIL('agent-with-special_chars.123')).toBe('/api/v1/agents/agent-with-special_chars.123');
      expect(API_ENDPOINTS.CHAT.CONVERSATION('conv-with-uuid-123e4567-e89b-12d3-a456-426614174000')).toBe('/api/v1/chat/conversations/conv-with-uuid-123e4567-e89b-12d3-a456-426614174000');
    });
  });

  describe('Request/Response interceptors', () => {
    let mockAxiosInstance: any;

    beforeEach(() => {
      mockAxiosInstance = {
        get: jest.fn(),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() }
        }
      };
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
    });

    it('sets up request interceptors', () => {
      require('../client');
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
    });

    it('sets up response interceptors', () => {
      require('../client');
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });

    it('adds authorization header when token exists', () => {
      // Mock localStorage
      const mockToken = 'mock-jwt-token';
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: jest.fn(() => mockToken),
          setItem: jest.fn(),
          removeItem: jest.fn()
        },
        writable: true
      });

      jest.resetModules();
      require('../client');

      // Get the request interceptor function
      const requestInterceptor = mockAxiosInstance.interceptors.request.use.mock.calls[0][0];
      const config = { headers: {} };

      const result = requestInterceptor(config);

      expect(result.headers.Authorization).toBe(`Bearer ${mockToken}`);
    });

    it('does not add authorization header when token does not exist', () => {
      // Mock localStorage with no token
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: jest.fn(() => null),
          setItem: jest.fn(),
          removeItem: jest.fn()
        },
        writable: true
      });

      jest.resetModules();
      require('../client');

      const requestInterceptor = mockAxiosInstance.interceptors.request.use.mock.calls[0][0];
      const config = { headers: {} };

      const result = requestInterceptor(config);

      expect(result.headers.Authorization).toBeUndefined();
    });

    it('handles response errors appropriately', () => {
      jest.resetModules();
      require('../client');

      const responseErrorHandler = mockAxiosInstance.interceptors.response.use.mock.calls[0][1];
      const error = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        }
      };

      expect(() => responseErrorHandler(error)).toThrow();
    });
  });

  describe('Error handling', () => {
    let mockAxiosInstance: any;

    beforeEach(() => {
      mockAxiosInstance = {
        get: jest.fn(),
        post: jest.fn(),
        put: jest.fn(),
        delete: jest.fn(),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() }
        }
      };
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
    });

    it('handles 401 unauthorized errors', () => {
      jest.resetModules();
      require('../client');

      const responseErrorHandler = mockAxiosInstance.interceptors.response.use.mock.calls[0][1];
      const error = {
        response: {
          status: 401,
          data: { message: 'Token expired' }
        }
      };

      // Should reject the promise
      expect(responseErrorHandler(error)).rejects.toEqual(error);
    });

    it('handles 403 forbidden errors', () => {
      jest.resetModules();
      require('../client');

      const responseErrorHandler = mockAxiosInstance.interceptors.response.use.mock.calls[0][1];
      const error = {
        response: {
          status: 403,
          data: { message: 'Insufficient permissions' }
        }
      };

      expect(responseErrorHandler(error)).rejects.toEqual(error);
    });

    it('handles 500 server errors', () => {
      jest.resetModules();
      require('../client');

      const responseErrorHandler = mockAxiosInstance.interceptors.response.use.mock.calls[0][1];
      const error = {
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      };

      expect(responseErrorHandler(error)).rejects.toEqual(error);
    });

    it('handles network errors', () => {
      jest.resetModules();
      require('../client');

      const responseErrorHandler = mockAxiosInstance.interceptors.response.use.mock.calls[0][1];
      const error = {
        message: 'Network Error',
        code: 'NETWORK_ERROR'
      };

      expect(responseErrorHandler(error)).rejects.toEqual(error);
    });
  });

  describe('API client usage patterns', () => {
    let mockAxiosInstance: any;

    beforeEach(() => {
      mockAxiosInstance = {
        get: jest.fn().mockResolvedValue({ data: { success: true } }),
        post: jest.fn().mockResolvedValue({ data: { success: true } }),
        put: jest.fn().mockResolvedValue({ data: { success: true } }),
        delete: jest.fn().mockResolvedValue({ data: { success: true } }),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() }
        }
      };
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
    });

    it('supports GET requests', async () => {
      jest.resetModules();
      const { apiClient } = require('../client');

      await apiClient.get('/test-endpoint');

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/test-endpoint');
    });

    it('supports POST requests with data', async () => {
      jest.resetModules();
      const { apiClient } = require('../client');

      const testData = { name: 'test', value: 123 };
      await apiClient.post('/test-endpoint', testData);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/test-endpoint', testData);
    });

    it('supports PUT requests with data', async () => {
      jest.resetModules();
      const { apiClient } = require('../client');

      const testData = { id: 1, name: 'updated' };
      await apiClient.put('/test-endpoint/1', testData);

      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/test-endpoint/1', testData);
    });

    it('supports DELETE requests', async () => {
      jest.resetModules();
      const { apiClient } = require('../client');

      await apiClient.delete('/test-endpoint/1');

      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/test-endpoint/1');
    });

    it('supports request configuration options', async () => {
      jest.resetModules();
      const { apiClient } = require('../client');

      const config = {
        headers: { 'Custom-Header': 'value' },
        timeout: 5000
      };

      await apiClient.get('/test-endpoint', config);

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/test-endpoint', config);
    });
  });

  describe('TypeScript support', () => {
    it('provides proper typing for endpoint functions', () => {
      // Test that dynamic endpoint functions have correct parameter types
      expect(typeof API_ENDPOINTS.AGENTS.DETAIL).toBe('function');
      expect(typeof API_ENDPOINTS.CHAT.CONVERSATION).toBe('function');
      expect(typeof API_ENDPOINTS.NUTRITION.PLAN).toBe('function');
      expect(typeof API_ENDPOINTS.TRAINING.WORKOUT).toBe('function');

      // Test that they return strings
      expect(typeof API_ENDPOINTS.AGENTS.DETAIL('test')).toBe('string');
      expect(typeof API_ENDPOINTS.CHAT.CONVERSATION('test')).toBe('string');
      expect(typeof API_ENDPOINTS.NUTRITION.PLAN('test')).toBe('string');
      expect(typeof API_ENDPOINTS.TRAINING.WORKOUT('test')).toBe('string');
    });

    it('maintains type safety for static endpoints', () => {
      // Test that static endpoints are strings
      expect(typeof API_ENDPOINTS.AUTH.LOGIN).toBe('string');
      expect(typeof API_ENDPOINTS.CHAT.CONVERSATIONS).toBe('string');
      expect(typeof API_ENDPOINTS.VOICE.TRANSCRIBE).toBe('string');
      expect(typeof API_ENDPOINTS.BIOMETRICS.PROFILE).toBe('string');
    });
  });

  describe('Environment configuration', () => {
    it('respects different environment configurations', () => {
      const environments = [
        { VITE_API_URL: 'https://api.production.com', expected: 'https://api.production.com' },
        { VITE_API_URL: 'https://api.staging.com', expected: 'https://api.staging.com' },
        { VITE_API_URL: 'http://localhost:3001', expected: 'http://localhost:3001' },
        { VITE_API_URL: undefined, expected: 'http://localhost:8000' }
      ];

      environments.forEach(({ VITE_API_URL, expected }) => {
        // Reset modules and environment
        jest.resetModules();
        if (VITE_API_URL) {
          process.env.VITE_API_URL = VITE_API_URL;
        } else {
          delete process.env.VITE_API_URL;
        }

        // Clear previous mock calls
        mockedAxios.create.mockClear();

        require('../client');

        expect(mockedAxios.create).toHaveBeenCalledWith(
          expect.objectContaining({
            baseURL: expected
          })
        );
      });
    });
  });
});
