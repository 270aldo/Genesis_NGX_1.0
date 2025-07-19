/**
 * Authentication Service for NGX Agents
 * Handles user authentication, registration, and session management
 * Migrated from GENESIS backend architecture
 */

import { apiClient, API_ENDPOINTS } from './client';
import { useAuthStore } from '../../store/authStore';
import { User } from '../../store/authStore';

// Types for authentication
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  name: string;
  confirmPassword: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  refreshToken: string;
  message?: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token?: string;
}

export interface VerificationData {
  email: string;
  code: string;
}

export interface PasswordResetData {
  email: string;
  token: string;
  newPassword: string;
}

/**
 * Authentication Service Class
 * Central service for all authentication operations
 */
export class AuthService {
  private static instance: AuthService;
  
  private constructor() {}
  
  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  /**
   * Login user with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      useAuthStore.getState().setLoading(true);
      
      const response = await apiClient.post<AuthResponse>(
        API_ENDPOINTS.AUTH.LOGIN,
        credentials
      );
      
      const { user, token, refreshToken } = response.data;
      
      // Store tokens in localStorage for API client interceptors
      const authStorage = {
        state: {
          user,
          token,
          refreshToken,
          isAuthenticated: true,
        },
        version: 0,
      };
      
      localStorage.setItem('ngx-agents-auth', JSON.stringify(authStorage));
      
      // Update auth store
      useAuthStore.getState().setUser(user);
      
      return response.data;
    } catch (error: any) {
      console.error('Login error:', error);
      throw {
        message: error.response?.data?.message || 'Login failed',
        code: error.response?.status || 500,
      };
    } finally {
      useAuthStore.getState().setLoading(false);
    }
  }

  /**
   * Register new user account
   */
  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    try {
      useAuthStore.getState().setLoading(true);
      
      // Validate passwords match
      if (credentials.password !== credentials.confirmPassword) {
        throw { message: 'Passwords do not match', code: 400 };
      }
      
      const response = await apiClient.post<AuthResponse>(
        API_ENDPOINTS.AUTH.REGISTER,
        {
          email: credentials.email,
          password: credentials.password,
          name: credentials.name,
        }
      );
      
      const { user, token, refreshToken } = response.data;
      
      // Store tokens in localStorage for API client interceptors
      const authStorage = {
        state: {
          user,
          token,
          refreshToken,
          isAuthenticated: true,
        },
        version: 0,
      };
      
      localStorage.setItem('ngx-agents-auth', JSON.stringify(authStorage));
      
      // Update auth store
      useAuthStore.getState().setUser(user);
      
      return response.data;
    } catch (error: any) {
      console.error('Registration error:', error);
      throw {
        message: error.response?.data?.message || 'Registration failed',
        code: error.response?.status || 500,
      };
    } finally {
      useAuthStore.getState().setLoading(false);
    }
  }

  /**
   * Logout user and clear session
   */
  async logout(): Promise<void> {
    try {
      // Call backend logout endpoint
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.warn('Logout endpoint error:', error);
    } finally {
      // Clear local storage and auth store regardless of backend response
      localStorage.removeItem('ngx-agents-auth');
      useAuthStore.getState().logout();
    }
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshToken(): Promise<string> {
    try {
      const authStorage = localStorage.getItem('ngx-agents-auth');
      let refreshToken = null;
      
      if (authStorage) {
        const parsedStorage = JSON.parse(authStorage);
        refreshToken = parsedStorage.state?.refreshToken || parsedStorage.refreshToken;
      }
      
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await apiClient.post<RefreshTokenResponse>(
        API_ENDPOINTS.AUTH.REFRESH,
        { refresh_token: refreshToken }
      );
      
      const { access_token, refresh_token: newRefreshToken } = response.data;
      
      // Update stored tokens
      if (authStorage) {
        const parsedStorage = JSON.parse(authStorage);
        parsedStorage.state.token = access_token;
        if (newRefreshToken) {
          parsedStorage.state.refreshToken = newRefreshToken;
        }
        localStorage.setItem('ngx-agents-auth', JSON.stringify(parsedStorage));
      }
      
      return access_token;
    } catch (error: any) {
      console.error('Token refresh error:', error);
      // If refresh fails, logout user
      this.logout();
      throw error;
    }
  }

  /**
   * Verify email with verification code
   */
  async verifyEmail(verificationData: VerificationData): Promise<{ message: string }> {
    try {
      const response = await apiClient.post(
        API_ENDPOINTS.AUTH.VERIFY,
        verificationData
      );
      return response.data;
    } catch (error: any) {
      console.error('Email verification error:', error);
      throw {
        message: error.response?.data?.message || 'Email verification failed',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<{ message: string }> {
    try {
      const response = await apiClient.post('/api/v1/auth/forgot-password', { email });
      return response.data;
    } catch (error: any) {
      console.error('Password reset request error:', error);
      throw {
        message: error.response?.data?.message || 'Password reset request failed',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Reset password with token
   */
  async resetPassword(resetData: PasswordResetData): Promise<{ message: string }> {
    try {
      const response = await apiClient.post('/api/v1/auth/reset-password', resetData);
      return response.data;
    } catch (error: any) {
      console.error('Password reset error:', error);
      throw {
        message: error.response?.data?.message || 'Password reset failed',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await apiClient.get<User>(API_ENDPOINTS.USER.PROFILE);
      
      // Update auth store with latest user data
      useAuthStore.getState().setUser(response.data);
      
      return response.data;
    } catch (error: any) {
      console.error('Get current user error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to get user profile',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(updates: Partial<User>): Promise<User> {
    try {
      const response = await apiClient.put<User>(
        API_ENDPOINTS.USER.PROFILE,
        updates
      );
      
      // Update auth store with updated user data
      useAuthStore.getState().updateProfile(response.data);
      
      return response.data;
    } catch (error: any) {
      console.error('Update profile error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to update profile',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return useAuthStore.getState().isAuthenticated;
  }

  /**
   * Get current user from store
   */
  getCurrentUserFromStore(): User | null {
    return useAuthStore.getState().user;
  }

  /**
   * Initialize authentication state from localStorage
   */
  async initializeAuth(): Promise<void> {
    try {
      const authStorage = localStorage.getItem('ngx-agents-auth');
      
      if (authStorage) {
        const parsedStorage = JSON.parse(authStorage);
        const { user, token, isAuthenticated } = parsedStorage.state || {};
        
        if (isAuthenticated && user && token) {
          // Verify token is still valid by fetching current user
          try {
            const currentUser = await this.getCurrentUser();
            // User data refreshed successfully, authentication is valid
            console.log('Authentication initialized successfully');
          } catch (error) {
            // Token is invalid, clear storage
            console.warn('Invalid token found, clearing authentication');
            this.logout();
          }
        }
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      // Clear potentially corrupted auth data
      localStorage.removeItem('ngx-agents-auth');
      useAuthStore.getState().logout();
    }
  }
}

// Export singleton instance
export const authService = AuthService.getInstance();
export default authService;