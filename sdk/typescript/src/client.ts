/**
 * Main GENESIS Ecosystem Client
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { GenesisConfig, GenesisResponse, GenesisError } from './types'
import { GenesisAPIError, handleAxiosError } from './utils/errors'
import { Logger } from './utils/logger'
import { RateLimiter } from './utils/rate-limiter'

export class GenesisEcosystemClient {
  protected client: AxiosInstance
  protected config: GenesisConfig
  protected logger: Logger
  protected rateLimiter: RateLimiter
  private requestIdCounter = 0

  constructor(config: GenesisConfig) {
    this.config = {
      version: '1.0.0',
      timeout: 30000,
      maxRetries: 3,
      debug: false,
      ...config
    }

    this.logger = new Logger(this.config.debug)
    this.rateLimiter = new RateLimiter(this.config.app)

    // Create axios instance
    this.client = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.config.apiKey,
        'X-App-ID': this.config.app,
        'X-App-Version': this.config.version || '1.0.0',
      }
    })

    this.setupInterceptors()
  }

  /**
   * Setup request and response interceptors
   */
  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      async (config) => {
        // Add request ID
        config.headers['X-Request-ID'] = this.generateRequestId()

        // Check rate limits
        await this.rateLimiter.checkLimit()

        // Log request if debug
        this.logger.debug('Request:', {
          method: config.method,
          url: config.url,
          headers: config.headers
        })

        return config
      },
      (error) => {
        this.logger.error('Request error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Log response if debug
        this.logger.debug('Response:', {
          status: response.status,
          data: response.data
        })

        return response
      },
      async (error) => {
        // Handle errors
        const genesisError = handleAxiosError(error)

        // Retry logic for certain errors
        if (this.shouldRetry(error) && error.config.__retryCount < this.config.maxRetries) {
          error.config.__retryCount = (error.config.__retryCount || 0) + 1
          const delay = this.getRetryDelay(error.config.__retryCount)
          
          this.logger.warn(`Retrying request (attempt ${error.config.__retryCount}/${this.config.maxRetries}) after ${delay}ms`)
          
          await new Promise(resolve => setTimeout(resolve, delay))
          return this.client.request(error.config)
        }

        this.logger.error('Response error:', genesisError)
        throw genesisError
      }
    )
  }

  /**
   * Generate unique request ID
   */
  protected generateRequestId(): string {
    const timestamp = Date.now()
    const counter = ++this.requestIdCounter
    return `${this.config.app}-${timestamp}-${counter}`
  }

  /**
   * Check if request should be retried
   */
  private shouldRetry(error: any): boolean {
    if (!error.config || !error.response) return false
    
    const status = error.response.status
    const method = error.config.method?.toLowerCase()

    // Only retry idempotent methods
    if (!['get', 'put', 'delete', 'head', 'options'].includes(method)) {
      return false
    }

    // Retry on specific status codes
    return [408, 429, 500, 502, 503, 504].includes(status)
  }

  /**
   * Get retry delay with exponential backoff
   */
  private getRetryDelay(retryCount: number): number {
    return Math.min(1000 * Math.pow(2, retryCount - 1), 10000)
  }

  /**
   * Make a GET request
   */
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<GenesisResponse<T>> {
    try {
      const response = await this.client.get<T>(url, config)
      return this.formatResponse(response)
    } catch (error) {
      return this.formatError(error as GenesisAPIError)
    }
  }

  /**
   * Make a POST request
   */
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<GenesisResponse<T>> {
    try {
      const response = await this.client.post<T>(url, data, config)
      return this.formatResponse(response)
    } catch (error) {
      return this.formatError(error as GenesisAPIError)
    }
  }

  /**
   * Make a PUT request
   */
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<GenesisResponse<T>> {
    try {
      const response = await this.client.put<T>(url, data, config)
      return this.formatResponse(response)
    } catch (error) {
      return this.formatError(error as GenesisAPIError)
    }
  }

  /**
   * Make a DELETE request
   */
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<GenesisResponse<T>> {
    try {
      const response = await this.client.delete<T>(url, config)
      return this.formatResponse(response)
    } catch (error) {
      return this.formatError(error as GenesisAPIError)
    }
  }

  /**
   * Format successful response
   */
  private formatResponse<T>(response: AxiosResponse<T>): GenesisResponse<T> {
    return {
      success: true,
      data: response.data,
      metadata: {
        request_id: response.headers['x-request-id'],
        execution_time: parseFloat(response.headers['x-process-time'] || '0'),
        app_id: this.config.app,
        version: this.config.version || '1.0.0'
      }
    }
  }

  /**
   * Format error response
   */
  private formatError(error: GenesisAPIError): GenesisResponse {
    return {
      success: false,
      error: {
        code: error.code,
        message: error.message,
        details: error.details,
        timestamp: new Date().toISOString()
      }
    }
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<GenesisConfig>) {
    this.config = { ...this.config, ...newConfig }
    
    // Update axios headers
    if (newConfig.apiKey) {
      this.client.defaults.headers.common['X-API-Key'] = newConfig.apiKey
    }
    if (newConfig.baseURL) {
      this.client.defaults.baseURL = newConfig.baseURL
    }
  }

  /**
   * Get current configuration
   */
  getConfig(): GenesisConfig {
    return { ...this.config }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<GenesisResponse<any>> {
    return this.get('/health')
  }

  /**
   * Get ecosystem status
   */
  async getEcosystemStatus(): Promise<GenesisResponse<any>> {
    return this.get('/api/v1/ecosystem/status')
  }

  /**
   * Get ecosystem usage
   */
  async getEcosystemUsage(appId?: string): Promise<GenesisResponse<any>> {
    const params = appId ? { app_id: appId } : {}
    return this.get('/api/v1/ecosystem/usage', { params })
  }
}