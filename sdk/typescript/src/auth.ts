/**
 * GENESIS Authentication Client
 */

import { GenesisEcosystemClient } from './client'
import { GenesisConfig, GenesisResponse, AuthTokens, User } from './types'

export class GenesisAuthClient extends GenesisEcosystemClient {
  private tokens?: AuthTokens

  constructor(config: Omit<GenesisConfig, 'app'>) {
    super({ ...config, app: 'main' })
  }

  /**
   * Login with email and password
   */
  async login(email: string, password: string): Promise<GenesisResponse<AuthTokens>> {
    const response = await this.post<AuthTokens>('/api/v1/auth/login', {
      email,
      password
    })

    if (response.success && response.data) {
      this.tokens = response.data
      // Update API key for future requests
      this.updateConfig({ apiKey: response.data.access_token })
    }

    return response
  }

  /**
   * Register new user
   */
  async register(
    email: string,
    password: string,
    name?: string
  ): Promise<GenesisResponse<AuthTokens>> {
    const response = await this.post<AuthTokens>('/api/v1/auth/register', {
      email,
      password,
      name
    })

    if (response.success && response.data) {
      this.tokens = response.data
      this.updateConfig({ apiKey: response.data.access_token })
    }

    return response
  }

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken?: string): Promise<GenesisResponse<AuthTokens>> {
    const token = refreshToken || this.tokens?.refresh_token
    if (!token) {
      throw new Error('No refresh token available')
    }

    const response = await this.post<AuthTokens>('/api/v1/auth/refresh', {
      refresh_token: token
    })

    if (response.success && response.data) {
      this.tokens = response.data
      this.updateConfig({ apiKey: response.data.access_token })
    }

    return response
  }

  /**
   * Logout
   */
  async logout(): Promise<GenesisResponse<void>> {
    const response = await this.post<void>('/api/v1/auth/logout')
    this.tokens = undefined
    return response
  }

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<GenesisResponse<User>> {
    return this.get<User>('/api/v1/auth/me')
  }

  /**
   * Update user profile
   */
  async updateProfile(updates: Partial<User>): Promise<GenesisResponse<User>> {
    return this.put<User>('/api/v1/auth/profile', updates)
  }

  /**
   * Change password
   */
  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<GenesisResponse<void>> {
    return this.post<void>('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<GenesisResponse<void>> {
    return this.post<void>('/api/v1/auth/forgot-password', { email })
  }

  /**
   * Reset password with token
   */
  async resetPassword(
    token: string,
    newPassword: string
  ): Promise<GenesisResponse<void>> {
    return this.post<void>('/api/v1/auth/reset-password', {
      token,
      new_password: newPassword
    })
  }

  /**
   * Get current tokens
   */
  getTokens(): AuthTokens | undefined {
    return this.tokens
  }

  /**
   * Check if authenticated
   */
  isAuthenticated(): boolean {
    return !!this.tokens?.access_token
  }
}