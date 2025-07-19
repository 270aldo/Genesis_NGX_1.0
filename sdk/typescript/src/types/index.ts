/**
 * Core types for GENESIS SDK
 */

export interface GenesisConfig {
  baseURL: string
  apiKey: string
  app: 'blog' | 'crm' | 'pulse' | 'core' | 'conversations' | 'main'
  version?: string
  timeout?: number
  maxRetries?: number
  debug?: boolean
}

export interface GenesisAgent {
  agent_id: string
  name: string
  description: string
  capabilities: string[]
  status?: 'available' | 'busy' | 'offline'
  personality?: 'PRIME' | 'LONGEVITY'
  enhanced?: boolean
}

export interface GenesisResponse<T = any> {
  success: boolean
  data?: T
  error?: GenesisError
  metadata?: ResponseMetadata
}

export interface GenesisError {
  code: string
  message: string
  details?: any
  timestamp: string
}

export interface ResponseMetadata {
  request_id: string
  execution_time: number
  app_id: string
  version: string
  [key: string]: any
}

export interface PaginatedResponse<T> {
  items: T[]
  total_items: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
}

export interface User {
  id: string
  email: string
  name?: string
  role?: string
  created_at: string
  updated_at: string
}