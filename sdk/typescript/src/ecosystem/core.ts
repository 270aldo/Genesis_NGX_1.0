/**
 * GENESIS Core Client for NEXUS_CORE integration
 */

import { GenesisEcosystemClient } from '../client'
import { GenesisConfig, GenesisResponse } from '../types'
import {
  CoreWorkflowRequest,
  CoreWorkflowResponse,
  EcosystemRequest
} from '../types/ecosystem'

export class GENESISCoreClient extends GenesisEcosystemClient {
  constructor(config: Omit<GenesisConfig, 'app'>) {
    super({ ...config, app: 'core' })
  }

  /**
   * Execute a workflow using GENESIS agents
   */
  async executeWorkflow(
    params: Omit<CoreWorkflowRequest, keyof EcosystemRequest>
  ): Promise<GenesisResponse<CoreWorkflowResponse>> {
    const request: CoreWorkflowRequest = {
      ...params,
      app_id: this.config.app,
      app_version: this.config.version || '1.0.0',
      request_id: this.generateRequestId(),
      timestamp: new Date(),
      metadata: params.metadata || {}
    }

    return this.post<CoreWorkflowResponse>('/api/v1/ecosystem/core/execute-workflow', request)
  }

  /**
   * Execute analysis workflow
   */
  async executeAnalysis(
    workflowId: string,
    parameters: Record<string, any>,
    async: boolean = false
  ): Promise<GenesisResponse<CoreWorkflowResponse>> {
    return this.executeWorkflow({
      workflow_id: workflowId,
      workflow_type: 'analysis',
      parameters,
      execute_async: async
    })
  }

  /**
   * Generate executive report
   */
  async generateReport(
    reportType: string,
    parameters: {
      time_range: string
      metrics: string[]
      format: 'pdf' | 'html' | 'json'
    }
  ): Promise<GenesisResponse<CoreWorkflowResponse>> {
    return this.executeWorkflow({
      workflow_id: `report_${reportType}`,
      workflow_type: 'report',
      parameters,
      execute_async: false
    })
  }

  /**
   * Create automation workflow
   */
  async createAutomation(
    name: string,
    trigger: {
      type: 'schedule' | 'event' | 'threshold'
      config: Record<string, any>
    },
    actions: Array<{
      agent_id: string
      action: string
      parameters: Record<string, any>
    }>
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/core/automation', {
      name,
      trigger,
      actions,
      app_id: this.config.app
    })
  }

  /**
   * Set up alert
   */
  async createAlert(
    name: string,
    condition: {
      metric: string
      operator: '>' | '<' | '=' | '>=' | '<='
      value: number
    },
    notifications: {
      email?: string[]
      webhook?: string
      sms?: string[]
    }
  ): Promise<GenesisResponse<any>> {
    return this.executeWorkflow({
      workflow_id: `alert_${name}`,
      workflow_type: 'alert',
      parameters: {
        condition,
        notifications
      },
      execute_async: true
    })
  }

  /**
   * Get workflow status
   */
  async getWorkflowStatus(
    workflowId: string
  ): Promise<GenesisResponse<CoreWorkflowResponse>> {
    return this.get<CoreWorkflowResponse>(`/api/v1/ecosystem/core/workflow/${workflowId}/status`)
  }

  /**
   * List available workflows
   */
  async listWorkflows(
    type?: CoreWorkflowRequest['workflow_type']
  ): Promise<GenesisResponse<any[]>> {
    return this.get<any[]>('/api/v1/ecosystem/core/workflows', {
      params: type ? { type } : {}
    })
  }

  /**
   * Get executive dashboard data
   */
  async getDashboardData(
    dashboardId: string,
    timeRange: 'day' | 'week' | 'month' | 'quarter' | 'year' = 'month'
  ): Promise<GenesisResponse<any>> {
    return this.get(`/api/v1/ecosystem/core/dashboard/${dashboardId}`, {
      params: { time_range: timeRange }
    })
  }

  /**
   * Execute custom query
   */
  async executeQuery(
    query: string,
    parameters: Record<string, any> = {}
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/core/query', {
      query,
      parameters,
      app_id: this.config.app
    })
  }

  /**
   * Schedule workflow
   */
  async scheduleWorkflow(
    workflowId: string,
    schedule: {
      cron?: string
      interval?: string
      start_date?: string
      end_date?: string
    }
  ): Promise<GenesisResponse<any>> {
    return this.post(`/api/v1/ecosystem/core/workflow/${workflowId}/schedule`, {
      schedule,
      app_id: this.config.app
    })
  }

  /**
   * Get analytics insights
   */
  async getAnalytics(
    category: 'usage' | 'performance' | 'cost' | 'health',
    filters: Record<string, any> = {}
  ): Promise<GenesisResponse<any>> {
    return this.post('/api/v1/ecosystem/core/analytics', {
      category,
      filters,
      app_id: this.config.app
    })
  }
}