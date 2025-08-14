/**
 * Authentication Utilities for K6 Load Tests
 *
 * Handles user authentication and token management
 * for load testing scenarios.
 */

import http from 'k6/http';
import { check } from 'k6';

/**
 * Authenticate user and get JWT token
 * @param {string} baseUrl - API base URL
 * @param {Object} credentials - User credentials {email, password}
 * @returns {string|null} JWT token or null if authentication failed
 */
export function authenticateUser(baseUrl, credentials) {
  const loginUrl = `${baseUrl}/auth/signin`;

  const payload = JSON.stringify({
    email: credentials.email,
    password: credentials.password
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    tags: { name: 'auth_signin' },
  };

  const response = http.post(loginUrl, payload, params);

  const authSuccess = check(response, {
    'authentication successful': (r) => r.status === 200,
    'auth response has token': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.access_token !== undefined;
      } catch (e) {
        return false;
      }
    },
  });

  if (authSuccess && response.status === 200) {
    try {
      const body = JSON.parse(response.body);
      return body.access_token;
    } catch (e) {
      console.error('Failed to parse authentication response:', e);
      return null;
    }
  }

  console.error(`Authentication failed for ${credentials.email}: ${response.status}`);
  return null;
}

/**
 * Get authentication headers with JWT token
 * @param {string} token - JWT token
 * @returns {Object} Headers object with Authorization
 */
export function getAuthHeaders(token) {
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}

/**
 * Refresh JWT token
 * @param {string} baseUrl - API base URL
 * @param {string} refreshToken - Refresh token
 * @returns {string|null} New JWT token or null if refresh failed
 */
export function refreshToken(baseUrl, refreshToken) {
  const refreshUrl = `${baseUrl}/auth/refresh`;

  const payload = JSON.stringify({
    refresh_token: refreshToken
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    tags: { name: 'auth_refresh' },
  };

  const response = http.post(refreshUrl, payload, params);

  const refreshSuccess = check(response, {
    'token refresh successful': (r) => r.status === 200,
  });

  if (refreshSuccess && response.status === 200) {
    try {
      const body = JSON.parse(response.body);
      return body.access_token;
    } catch (e) {
      console.error('Failed to parse refresh response:', e);
      return null;
    }
  }

  return null;
}

/**
 * Setup authentication for a virtual user
 * Manages token lifecycle including refresh
 */
export class AuthManager {
  constructor(baseUrl, credentials) {
    this.baseUrl = baseUrl;
    this.credentials = credentials;
    this.token = null;
    this.refreshToken = null;
    this.tokenExpiry = null;
  }

  /**
   * Initialize authentication
   */
  async init() {
    this.token = authenticateUser(this.baseUrl, this.credentials);

    if (this.token) {
      // Decode JWT to get expiry (basic parsing)
      try {
        const tokenParts = this.token.split('.');
        const payload = JSON.parse(atob(tokenParts[1]));
        this.tokenExpiry = payload.exp * 1000; // Convert to milliseconds
      } catch (e) {
        // Fallback to 1 hour expiry if parsing fails
        this.tokenExpiry = Date.now() + (60 * 60 * 1000);
      }
    }

    return this.token !== null;
  }

  /**
   * Get valid authentication headers
   * Automatically refreshes token if needed
   */
  getHeaders() {
    // Check if token needs refresh (5 minutes before expiry)
    if (this.tokenExpiry && Date.now() > (this.tokenExpiry - 5 * 60 * 1000)) {
      if (this.refreshToken) {
        const newToken = refreshToken(this.baseUrl, this.refreshToken);
        if (newToken) {
          this.token = newToken;
          // Update expiry
          try {
            const tokenParts = this.token.split('.');
            const payload = JSON.parse(atob(tokenParts[1]));
            this.tokenExpiry = payload.exp * 1000;
          } catch (e) {
            this.tokenExpiry = Date.now() + (60 * 60 * 1000);
          }
        } else {
          // Refresh failed, need to re-authenticate
          this.init();
        }
      } else {
        // No refresh token, re-authenticate
        this.init();
      }
    }

    return getAuthHeaders(this.token);
  }

  /**
   * Check if authentication is valid
   */
  isAuthenticated() {
    return this.token !== null && Date.now() < this.tokenExpiry;
  }
}

/**
 * Create multiple authenticated users for load testing
 * @param {string} baseUrl - API base URL
 * @param {Array} userCredentials - Array of user credential objects
 * @returns {Array} Array of AuthManager instances
 */
export function createAuthenticatedUsers(baseUrl, userCredentials) {
  return userCredentials.map(credentials => {
    const authManager = new AuthManager(baseUrl, credentials);
    authManager.init();
    return authManager;
  });
}
