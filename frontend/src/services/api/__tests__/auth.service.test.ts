import { AuthService, authService } from '../auth.service';
import { apiClient, API_ENDPOINTS } from '../client';
import { useAuthStore } from '../../../store/authStore';
import type { LoginCredentials, RegisterCredentials, AuthResponse, User } from '../auth.service';

// Mock dependencies
jest.mock('../client', () => ({
  apiClient: {
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn()
  },
  API_ENDPOINTS: {
    AUTH: {
      LOGIN: '/api/v1/auth/login',
      REGISTER: '/api/v1/auth/register',
      LOGOUT: '/api/v1/auth/logout',
      REFRESH: '/api/v1/auth/refresh',
      VERIFY: '/api/v1/auth/verify'
    },
    USER: {
      PROFILE: '/api/v1/user/profile'
    }
  }
}));

jest.mock('../../../store/authStore', () => ({
  useAuthStore: {
    getState: jest.fn()
  }
}));

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;
const mockUseAuthStore = useAuthStore as jest.Mocked<typeof useAuthStore>;

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

// Mock console methods
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

beforeAll(() => {
  console.error = jest.fn();
  console.warn = jest.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
});

describe('AuthService', () => {
  let mockAuthStore: any;

  beforeEach(() => {
    jest.clearAllMocks();

    mockAuthStore = {
      setLoading: jest.fn(),
      setUser: jest.fn(),
      logout: jest.fn(),
      updateProfile: jest.fn(),
      isAuthenticated: false,
      user: null
    };

    mockUseAuthStore.getState.mockReturnValue(mockAuthStore);
  });

  describe('singleton pattern', () => {
    it('returns the same instance', () => {
      const instance1 = AuthService.getInstance();
      const instance2 = AuthService.getInstance();

      expect(instance1).toBe(instance2);
      expect(instance1).toBe(authService);
    });
  });

  describe('login', () => {
    const mockCredentials: LoginCredentials = {
      email: 'test@example.com',
      password: 'password123'
    };

    const mockAuthResponse: AuthResponse = {
      user: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'user'
      },
      token: 'mock-jwt-token',
      refreshToken: 'mock-refresh-token'
    };

    it('successfully logs in a user', async () => {
      mockApiClient.post.mockResolvedValueOnce({
        data: mockAuthResponse
      });

      const result = await authService.login(mockCredentials);

      expect(mockAuthStore.setLoading).toHaveBeenCalledWith(true);
      expect(mockApiClient.post).toHaveBeenCalledWith(
        API_ENDPOINTS.AUTH.LOGIN,
        mockCredentials
      );
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'ngx-agents-auth',
        JSON.stringify({
          state: {
            user: mockAuthResponse.user,
            token: mockAuthResponse.token,
            refreshToken: mockAuthResponse.refreshToken,
            isAuthenticated: true
          },
          version: 0
        })
      );
      expect(mockAuthStore.setUser).toHaveBeenCalledWith(mockAuthResponse.user);
      expect(mockAuthStore.setLoading).toHaveBeenCalledWith(false);
      expect(result).toEqual(mockAuthResponse);
    });

    it('handles API errors correctly', async () => {
      const apiError = {
        response: {
          data: { message: 'Invalid credentials' },
          status: 401
        }
      };

      mockApiClient.post.mockRejectedValueOnce(apiError);

      await expect(authService.login(mockCredentials)).rejects.toEqual({
        message: 'Invalid credentials',
        code: 401
      });

      expect(mockAuthStore.setLoading).toHaveBeenCalledWith(true);
      expect(mockAuthStore.setLoading).toHaveBeenCalledWith(false);
      expect(console.error).toHaveBeenCalledWith('Login error:', apiError);
    });

    it('handles network errors without response', async () => {
      const networkError = new Error('Network error');
      mockApiClient.post.mockRejectedValueOnce(networkError);

      await expect(authService.login(mockCredentials)).rejects.toEqual({
        message: 'Login failed',
        code: 500
      });

      expect(mockAuthStore.setLoading).toHaveBeenCalledWith(false);
    });
  });

  describe('register', () => {
    const mockCredentials: RegisterCredentials = {
      email: 'test@example.com',
      password: 'password123',
      confirmPassword: 'password123',
      name: 'Test User'
    };

    const mockAuthResponse: AuthResponse = {
      user: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'user'
      },
      token: 'mock-jwt-token',
      refreshToken: 'mock-refresh-token'
    };

    it('successfully registers a user', async () => {
      mockApiClient.post.mockResolvedValueOnce({
        data: mockAuthResponse
      });

      const result = await authService.register(mockCredentials);

      expect(mockAuthStore.setLoading).toHaveBeenCalledWith(true);
      expect(mockApiClient.post).toHaveBeenCalledWith(
        API_ENDPOINTS.AUTH.REGISTER,
        {
          email: mockCredentials.email,
          password: mockCredentials.password,
          name: mockCredentials.name
        }
      );
      expect(mockLocalStorage.setItem).toHaveBeenCalled();
      expect(mockAuthStore.setUser).toHaveBeenCalledWith(mockAuthResponse.user);
      expect(result).toEqual(mockAuthResponse);
    });

    it('validates password confirmation', async () => {
      const invalidCredentials = {
        ...mockCredentials,
        confirmPassword: 'different-password'
      };

      await expect(authService.register(invalidCredentials)).rejects.toEqual({
        message: 'Passwords do not match',
        code: 400
      });

      expect(mockApiClient.post).not.toHaveBeenCalled();
      expect(mockAuthStore.setLoading).toHaveBeenCalledWith(false);
    });

    it('handles registration API errors', async () => {
      const apiError = {
        response: {
          data: { message: 'Email already exists' },
          status: 409
        }
      };

      mockApiClient.post.mockRejectedValueOnce(apiError);

      await expect(authService.register(mockCredentials)).rejects.toEqual({
        message: 'Email already exists',
        code: 409
      });

      expect(console.error).toHaveBeenCalledWith('Registration error:', apiError);
    });
  });

  describe('logout', () => {
    it('successfully logs out with backend call', async () => {
      mockApiClient.post.mockResolvedValueOnce({ data: {} });

      await authService.logout();

      expect(mockApiClient.post).toHaveBeenCalledWith(API_ENDPOINTS.AUTH.LOGOUT);
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('ngx-agents-auth');
      expect(mockAuthStore.logout).toHaveBeenCalled();
    });

    it('clears local data even if backend call fails', async () => {
      const apiError = new Error('Backend error');
      mockApiClient.post.mockRejectedValueOnce(apiError);

      await authService.logout();

      expect(console.warn).toHaveBeenCalledWith('Logout endpoint error:', apiError);
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('ngx-agents-auth');
      expect(mockAuthStore.logout).toHaveBeenCalled();
    });
  });

  describe('refreshToken', () => {
    const mockRefreshResponse = {
      access_token: 'new-access-token',
      refresh_token: 'new-refresh-token'
    };

    it('successfully refreshes token', async () => {
      const authStorage = {
        state: {
          user: { id: '1', email: 'test@example.com' },
          token: 'old-token',
          refreshToken: 'old-refresh-token',
          isAuthenticated: true
        },
        version: 0
      };

      mockLocalStorage.getItem.mockReturnValueOnce(JSON.stringify(authStorage));
      mockApiClient.post.mockResolvedValueOnce({ data: mockRefreshResponse });

      const result = await authService.refreshToken();

      expect(mockApiClient.post).toHaveBeenCalledWith(
        API_ENDPOINTS.AUTH.REFRESH,
        { refresh_token: 'old-refresh-token' }
      );
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'ngx-agents-auth',
        JSON.stringify({
          ...authStorage,
          state: {
            ...authStorage.state,
            token: 'new-access-token',
            refreshToken: 'new-refresh-token'
          }
        })
      );
      expect(result).toBe('new-access-token');
    });

    it('handles missing refresh token', async () => {
      mockLocalStorage.getItem.mockReturnValueOnce(null);

      await expect(authService.refreshToken()).rejects.toThrow('No refresh token available');

      expect(mockApiClient.post).not.toHaveBeenCalled();
    });

    it('handles refresh token API errors and logs out', async () => {
      const authStorage = {
        state: { refreshToken: 'invalid-token' }
      };

      mockLocalStorage.getItem.mockReturnValueOnce(JSON.stringify(authStorage));
      const apiError = new Error('Invalid refresh token');
      mockApiClient.post.mockRejectedValueOnce(apiError);

      // Mock logout method
      const logoutSpy = jest.spyOn(authService, 'logout').mockResolvedValueOnce();

      await expect(authService.refreshToken()).rejects.toThrow(apiError);

      expect(console.error).toHaveBeenCalledWith('Token refresh error:', apiError);
      expect(logoutSpy).toHaveBeenCalled();

      logoutSpy.mockRestore();
    });

    it('updates token without new refresh token', async () => {
      const authStorage = {
        state: {
          refreshToken: 'old-refresh-token',
          token: 'old-token'
        }
      };

      const refreshResponse = {
        access_token: 'new-access-token'
        // No new refresh token
      };

      mockLocalStorage.getItem.mockReturnValueOnce(JSON.stringify(authStorage));
      mockApiClient.post.mockResolvedValueOnce({ data: refreshResponse });

      await authService.refreshToken();

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'ngx-agents-auth',
        JSON.stringify({
          state: {
            refreshToken: 'old-refresh-token',
            token: 'new-access-token'
          }
        })
      );
    });
  });

  describe('verifyEmail', () => {
    const verificationData = {
      email: 'test@example.com',
      code: '123456'
    };

    it('successfully verifies email', async () => {
      const mockResponse = { message: 'Email verified successfully' };
      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await authService.verifyEmail(verificationData);

      expect(mockApiClient.post).toHaveBeenCalledWith(
        API_ENDPOINTS.AUTH.VERIFY,
        verificationData
      );
      expect(result).toEqual(mockResponse);
    });

    it('handles verification errors', async () => {
      const apiError = {
        response: {
          data: { message: 'Invalid verification code' },
          status: 400
        }
      };

      mockApiClient.post.mockRejectedValueOnce(apiError);

      await expect(authService.verifyEmail(verificationData)).rejects.toEqual({
        message: 'Invalid verification code',
        code: 400
      });
    });
  });

  describe('requestPasswordReset', () => {
    it('successfully requests password reset', async () => {
      const mockResponse = { message: 'Reset email sent' };
      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await authService.requestPasswordReset('test@example.com');

      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/v1/auth/forgot-password',
        { email: 'test@example.com' }
      );
      expect(result).toEqual(mockResponse);
    });

    it('handles password reset request errors', async () => {
      const apiError = {
        response: {
          data: { message: 'User not found' },
          status: 404
        }
      };

      mockApiClient.post.mockRejectedValueOnce(apiError);

      await expect(authService.requestPasswordReset('test@example.com')).rejects.toEqual({
        message: 'User not found',
        code: 404
      });
    });
  });

  describe('resetPassword', () => {
    const resetData = {
      email: 'test@example.com',
      token: 'reset-token',
      newPassword: 'newpassword123'
    };

    it('successfully resets password', async () => {
      const mockResponse = { message: 'Password reset successfully' };
      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await authService.resetPassword(resetData);

      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/v1/auth/reset-password',
        resetData
      );
      expect(result).toEqual(mockResponse);
    });

    it('handles password reset errors', async () => {
      const apiError = {
        response: {
          data: { message: 'Invalid reset token' },
          status: 400
        }
      };

      mockApiClient.post.mockRejectedValueOnce(apiError);

      await expect(authService.resetPassword(resetData)).rejects.toEqual({
        message: 'Invalid reset token',
        code: 400
      });
    });
  });

  describe('getCurrentUser', () => {
    const mockUser: User = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      role: 'user'
    };

    it('successfully gets current user', async () => {
      mockApiClient.get.mockResolvedValueOnce({ data: mockUser });

      const result = await authService.getCurrentUser();

      expect(mockApiClient.get).toHaveBeenCalledWith(API_ENDPOINTS.USER.PROFILE);
      expect(mockAuthStore.setUser).toHaveBeenCalledWith(mockUser);
      expect(result).toEqual(mockUser);
    });

    it('handles get user errors', async () => {
      const apiError = {
        response: {
          data: { message: 'Unauthorized' },
          status: 401
        }
      };

      mockApiClient.get.mockRejectedValueOnce(apiError);

      await expect(authService.getCurrentUser()).rejects.toEqual({
        message: 'Unauthorized',
        code: 401
      });
    });
  });

  describe('updateProfile', () => {
    const mockUser: User = {
      id: '1',
      email: 'test@example.com',
      name: 'Updated Name',
      role: 'user'
    };

    const updates = { name: 'Updated Name' };

    it('successfully updates profile', async () => {
      mockApiClient.put.mockResolvedValueOnce({ data: mockUser });

      const result = await authService.updateProfile(updates);

      expect(mockApiClient.put).toHaveBeenCalledWith(
        API_ENDPOINTS.USER.PROFILE,
        updates
      );
      expect(mockAuthStore.updateProfile).toHaveBeenCalledWith(mockUser);
      expect(result).toEqual(mockUser);
    });

    it('handles update profile errors', async () => {
      const apiError = {
        response: {
          data: { message: 'Validation error' },
          status: 400
        }
      };

      mockApiClient.put.mockRejectedValueOnce(apiError);

      await expect(authService.updateProfile(updates)).rejects.toEqual({
        message: 'Validation error',
        code: 400
      });
    });
  });

  describe('utility methods', () => {
    it('checks authentication status', () => {
      mockAuthStore.isAuthenticated = true;
      expect(authService.isAuthenticated()).toBe(true);

      mockAuthStore.isAuthenticated = false;
      expect(authService.isAuthenticated()).toBe(false);
    });

    it('gets current user from store', () => {
      const mockUser = { id: '1', email: 'test@example.com' };
      mockAuthStore.user = mockUser;

      expect(authService.getCurrentUserFromStore()).toEqual(mockUser);

      mockAuthStore.user = null;
      expect(authService.getCurrentUserFromStore()).toBe(null);
    });
  });

  describe('initializeAuth', () => {
    it('initializes with valid stored auth data', async () => {
      const authStorage = {
        state: {
          user: { id: '1', email: 'test@example.com' },
          token: 'valid-token',
          isAuthenticated: true
        }
      };

      mockLocalStorage.getItem.mockReturnValueOnce(JSON.stringify(authStorage));
      mockApiClient.get.mockResolvedValueOnce({ data: authStorage.state.user });

      await authService.initializeAuth();

      expect(mockApiClient.get).toHaveBeenCalledWith(API_ENDPOINTS.USER.PROFILE);
    });

    it('clears invalid stored auth data', async () => {
      const authStorage = {
        state: {
          user: { id: '1', email: 'test@example.com' },
          token: 'invalid-token',
          isAuthenticated: true
        }
      };

      mockLocalStorage.getItem.mockReturnValueOnce(JSON.stringify(authStorage));
      mockApiClient.get.mockRejectedValueOnce(new Error('Unauthorized'));

      const logoutSpy = jest.spyOn(authService, 'logout').mockResolvedValueOnce();

      await authService.initializeAuth();

      expect(console.warn).toHaveBeenCalledWith('Invalid token found, clearing authentication');
      expect(logoutSpy).toHaveBeenCalled();

      logoutSpy.mockRestore();
    });

    it('handles missing auth storage', async () => {
      mockLocalStorage.getItem.mockReturnValueOnce(null);

      await authService.initializeAuth();

      expect(mockApiClient.get).not.toHaveBeenCalled();
    });

    it('handles corrupted auth storage', async () => {
      mockLocalStorage.getItem.mockReturnValueOnce('invalid-json');

      await authService.initializeAuth();

      expect(console.error).toHaveBeenCalledWith('Auth initialization error:', expect.any(Error));
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('ngx-agents-auth');
      expect(mockAuthStore.logout).toHaveBeenCalled();
    });

    it('handles incomplete auth data', async () => {
      const incompleteAuthStorage = {
        state: {
          user: null,
          token: null,
          isAuthenticated: false
        }
      };

      mockLocalStorage.getItem.mockReturnValueOnce(JSON.stringify(incompleteAuthStorage));

      await authService.initializeAuth();

      expect(mockApiClient.get).not.toHaveBeenCalled();
    });
  });

  describe('error handling edge cases', () => {
    it('handles errors without response data', async () => {
      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'password'
      };

      const errorWithoutResponse = new Error('Network error');
      mockApiClient.post.mockRejectedValueOnce(errorWithoutResponse);

      await expect(authService.login(credentials)).rejects.toEqual({
        message: 'Login failed',
        code: 500
      });
    });

    it('handles errors with empty response data', async () => {
      const credentials: LoginCredentials = {
        email: 'test@example.com',
        password: 'password'
      };

      const errorWithEmptyResponse = {
        response: {
          data: {},
          status: 500
        }
      };

      mockApiClient.post.mockRejectedValueOnce(errorWithEmptyResponse);

      await expect(authService.login(credentials)).rejects.toEqual({
        message: 'Login failed',
        code: 500
      });
    });
  });
});
