/**
 * GENESIS CRM Client for NEXUS-CRM integration
 */

import { GenesisEcosystemClient } from '../client'
import { GenesisConfig, GenesisResponse } from '../types'
import {
  CRMAnalysisRequest,
  CRMAnalysisResponse,
  EcosystemRequest
} from '../types/ecosystem'

export class GENESISCRMClient extends GenesisEcosystemClient {
  constructor(config: Omit<GenesisConfig, 'app'>) {
    super({ ...config, app: 'crm' })
  }

  /**
   * Analyze customer data using GENESIS agents
   */
  async analyzeCustomer(
    params: Omit<CRMAnalysisRequest, keyof EcosystemRequest>
  ): Promise<GenesisResponse<CRMAnalysisResponse>> {
    const request: CRMAnalysisRequest = {
      ...params,
      app_id: this.config.app,
      app_version: this.config.version || '1.0.0',
      request_id: this.generateRequestId(),
      timestamp: new Date(),
      metadata: params.metadata || {}
    }

    return this.post<CRMAnalysisResponse>('/api/v1/ecosystem/crm/analyze-customer', request)
  }

  /**
   * Analyze customer behavior patterns
   */
  async analyzeBehavior(
    customerId: string,
    customerData: Record<string, any>,
    includeHistory: boolean = true
  ): Promise<GenesisResponse<CRMAnalysisResponse>> {
    return this.analyzeCustomer({
      customer_id: customerId,
      analysis_type: 'behavior',
      include_history: includeHistory,
      prediction_window: 30,
      data: customerData
    })
  }

  /**
   * Calculate churn risk for a customer
   */
  async calculateChurnRisk(
    customerId: string,
    customerData: Record<string, any>,
    predictionWindow: number = 90
  ): Promise<GenesisResponse<CRMAnalysisResponse>> {
    return this.analyzeCustomer({
      customer_id: customerId,
      analysis_type: 'churn_risk',
      include_history: true,
      prediction_window: predictionWindow,
      data: customerData
    })
  }

  /**
   * Get upsell opportunities for a customer
   */
  async getUpsellOpportunities(
    customerId: string,
    customerData: Record<string, any>
  ): Promise<GenesisResponse<CRMAnalysisResponse>> {
    return this.analyzeCustomer({
      customer_id: customerId,
      analysis_type: 'upsell',
      include_history: true,
      prediction_window: 60,
      data: customerData
    })
  }

  /**
   * Analyze customer health score
   */
  async analyzeHealthScore(
    customerId: string,
    customerData: Record<string, any>
  ): Promise<GenesisResponse<CRMAnalysisResponse>> {
    return this.analyzeCustomer({
      customer_id: customerId,
      analysis_type: 'health',
      include_history: true,
      prediction_window: 30,
      data: customerData
    })
  }

  /**
   * Track agent usage for a customer
   */
  async trackAgentUsage(
    customerId: string,
    agentId: string,
    usage: {
      duration: number
      queries: number
      satisfaction?: number
    }
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/crm/track-usage', {
      customer_id: customerId,
      agent_id: agentId,
      usage,
      app_id: this.config.app,
      timestamp: new Date()
    })
  }

  /**
   * Get customer insights dashboard
   */
  async getCustomerInsights(
    customerId: string,
    timeRange: 'week' | 'month' | 'quarter' | 'year' = 'month'
  ): Promise<GenesisResponse<any>> {
    return this.get(`/api/v1/ecosystem/crm/insights/${customerId}`, {
      params: { time_range: timeRange }
    })
  }

  /**
   * Batch analyze multiple customers
   */
  async batchAnalyze(
    customers: Array<{
      customer_id: string
      data: Record<string, any>
      analysis_type: CRMAnalysisRequest['analysis_type']
    }>
  ): Promise<GenesisResponse<CRMAnalysisResponse[]>> {
    const requests = customers.map(customer => ({
      customer_id: customer.customer_id,
      analysis_type: customer.analysis_type,
      include_history: true,
      prediction_window: 30,
      data: customer.data,
      app_id: this.config.app,
      app_version: this.config.version || '1.0.0',
      request_id: this.generateRequestId(),
      timestamp: new Date()
    }))

    return this.post<CRMAnalysisResponse[]>('/api/v1/ecosystem/crm/batch-analyze', {
      requests
    })
  }

  /**
   * Set up webhook for real-time customer events
   */
  async setupWebhook(
    webhookUrl: string,
    events: string[] = ['agent_usage', 'churn_alert', 'upsell_opportunity']
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/crm/webhook', {
      webhook_url: webhookUrl,
      events,
      app_id: this.config.app
    })
  }
}