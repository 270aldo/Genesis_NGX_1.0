/**
 * GENESIS Conversations Client for NEXUS_Conversations integration
 */

import { GenesisEcosystemClient } from '../client'
import { GenesisConfig, GenesisResponse } from '../types'
import {
  ConversationInsightRequest,
  ConversationInsightResponse,
  EcosystemRequest
} from '../types/ecosystem'

export class GENESISConversationsClient extends GenesisEcosystemClient {
  constructor(config: Omit<GenesisConfig, 'app'>) {
    super({ ...config, app: 'conversations' })
  }

  /**
   * Get insights from a conversation session
   */
  async getInsights(
    params: Omit<ConversationInsightRequest, keyof EcosystemRequest>
  ): Promise<GenesisResponse<ConversationInsightResponse>> {
    const request: ConversationInsightRequest = {
      ...params,
      app_id: this.config.app,
      app_version: this.config.version || '1.0.0',
      request_id: this.generateRequestId(),
      timestamp: new Date(),
      metadata: params.metadata || {}
    }

    return this.post<ConversationInsightResponse>('/api/v1/ecosystem/conversations/insights', request)
  }

  /**
   * Get conversation summary
   */
  async getSummary(
    sessionId: string,
    includeMetrics: boolean = true
  ): Promise<GenesisResponse<ConversationInsightResponse>> {
    return this.getInsights({
      session_id: sessionId,
      insight_type: 'summary',
      include_metrics: includeMetrics
    })
  }

  /**
   * Analyze agent chemistry
   */
  async analyzeChemistry(
    sessionId: string
  ): Promise<GenesisResponse<ConversationInsightResponse>> {
    return this.getInsights({
      session_id: sessionId,
      insight_type: 'chemistry',
      include_metrics: true
    })
  }

  /**
   * Calculate virality potential
   */
  async calculateVirality(
    sessionId: string
  ): Promise<GenesisResponse<ConversationInsightResponse>> {
    return this.getInsights({
      session_id: sessionId,
      insight_type: 'virality',
      include_metrics: true
    })
  }

  /**
   * Assess content quality
   */
  async assessQuality(
    sessionId: string
  ): Promise<GenesisResponse<ConversationInsightResponse>> {
    return this.getInsights({
      session_id: sessionId,
      insight_type: 'quality',
      include_metrics: true
    })
  }

  /**
   * Get recommendations for improvement
   */
  async getRecommendations(
    sessionId: string
  ): Promise<GenesisResponse<ConversationInsightResponse>> {
    return this.getInsights({
      session_id: sessionId,
      insight_type: 'recommendations',
      include_metrics: false
    })
  }

  /**
   * Compare multiple sessions
   */
  async compareSessions(
    sessionIds: string[],
    metrics: string[] = ['chemistry', 'virality', 'quality', 'engagement']
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/conversations/compare', {
      session_ids: sessionIds,
      metrics,
      app_id: this.config.app
    })
  }

  /**
   * Get trending topics from conversations
   */
  async getTrendingTopics(
    timeRange: 'day' | 'week' | 'month' = 'week',
    limit: number = 10
  ): Promise<GenesisResponse<any>> {
    return this.get('/api/v1/ecosystem/conversations/trending', {
      params: {
        time_range: timeRange,
        limit
      }
    })
  }

  /**
   * Get best performing agent combinations
   */
  async getBestAgentCombos(
    metric: 'chemistry' | 'virality' | 'quality' = 'chemistry',
    limit: number = 5
  ): Promise<GenesisResponse<any>> {
    return this.get('/api/v1/ecosystem/conversations/best-combos', {
      params: {
        metric,
        limit
      }
    })
  }

  /**
   * Export conversation
   */
  async exportConversation(
    sessionId: string,
    format: 'pdf' | 'markdown' | 'json' = 'markdown'
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/conversations/export', {
      session_id: sessionId,
      format,
      app_id: this.config.app
    })
  }

  /**
   * Create conversation template
   */
  async createTemplate(
    name: string,
    description: string,
    config: {
      mode: string
      agents: string[]
      parameters: Record<string, any>
    }
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/conversations/template', {
      name,
      description,
      config,
      app_id: this.config.app
    })
  }

  /**
   * Get conversation analytics
   */
  async getAnalytics(
    filters: {
      start_date?: string
      end_date?: string
      mode?: string
      agents?: string[]
    } = {}
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/conversations/analytics', {
      filters,
      app_id: this.config.app
    })
  }
}