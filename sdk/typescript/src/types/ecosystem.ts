/**
 * Ecosystem-specific types for GENESIS SDK
 */

// Base request type for all ecosystem calls
export interface EcosystemRequest {
  app_id: string
  app_version: string
  request_id: string
  timestamp?: Date
  metadata?: Record<string, any>
}

// Blog types
export interface BlogContentRequest extends EcosystemRequest {
  topic: string
  author_agent: string
  content_type: 'article' | 'tutorial' | 'guide' | 'news' | 'research'
  target_audience: 'general' | 'beginner' | 'intermediate' | 'advanced'
  word_count: number
  include_examples: boolean
  seo_keywords: string[]
}

export interface BlogContentResponse {
  request_id: string
  content: string
  agent_id: string
  metadata: {
    word_count: number
    execution_time: number
    app_id: string
  }
}

// CRM types
export interface CRMAnalysisRequest extends EcosystemRequest {
  customer_id: string
  analysis_type: 'behavior' | 'churn_risk' | 'upsell' | 'health' | 'engagement'
  include_history: boolean
  prediction_window: number
  data: Record<string, any>
}

export interface CRMAnalysisResponse {
  request_id: string
  customer_id: string
  analysis: string
  predictions: {
    churn_risk: number
    ltv_estimate: number
    next_best_action: string
    [key: string]: any
  }
  metadata: Record<string, any>
}

// Pulse types
export interface PulseBiometricRequest extends EcosystemRequest {
  user_id: string
  biometric_type: 'hrv' | 'sleep' | 'activity' | 'nutrition' | 'recovery' | 'stress'
  data_points: BiometricDataPoint[]
  analysis_depth: 'quick' | 'standard' | 'comprehensive'
  include_recommendations: boolean
}

export interface BiometricDataPoint {
  timestamp: string
  value: number
  unit: string
  device?: string
  metadata?: Record<string, any>
}

export interface PulseBiometricResponse {
  request_id: string
  user_id: string
  analysis: string
  metrics: {
    health_score: number
    trend: 'improving' | 'stable' | 'declining'
    risk_factors: string[]
    optimization_potential: number
  }
  metadata: Record<string, any>
}

// Core types
export interface CoreWorkflowRequest extends EcosystemRequest {
  workflow_id: string
  workflow_type: 'analysis' | 'report' | 'automation' | 'alert' | 'dashboard'
  parameters: Record<string, any>
  execute_async: boolean
}

export interface CoreWorkflowResponse {
  request_id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  workflow_id: string
  result?: any
  agents_used?: string[]
  metadata: Record<string, any>
}

// Conversations types
export interface ConversationInsightRequest extends EcosystemRequest {
  session_id: string
  insight_type: 'summary' | 'chemistry' | 'virality' | 'quality' | 'recommendations'
  include_metrics: boolean
}

export interface ConversationInsightResponse {
  request_id: string
  session_id: string
  insights: string
  metrics?: {
    chemistry_score: number
    virality_potential: number
    content_quality: number
    engagement_level: number
  }
  metadata: Record<string, any>
}

// Ecosystem status types
export interface EcosystemStatus {
  status: 'operational' | 'degraded' | 'down'
  integrations: Record<string, IntegrationStatus>
  rate_limits: Record<string, RateLimit>
  timestamp: string
}

export interface IntegrationStatus {
  status: 'active' | 'inactive' | 'error'
  version: string
  last_seen?: string
}

export interface RateLimit {
  requests_per_minute: number
  requests_per_hour: number
  current_usage?: {
    minute: number
    hour: number
  }
}

export interface EcosystemUsage {
  app_id?: string
  usage?: {
    requests_today: number
    requests_month: number
  }
  total_usage?: Record<string, any>
  cost_savings: {
    estimated_monthly: string
    percentage: string
  }
}