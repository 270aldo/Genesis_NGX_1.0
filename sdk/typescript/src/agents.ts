/**
 * GENESIS Agents Client
 */

import { GenesisEcosystemClient } from './client'
import { GenesisConfig, GenesisResponse, GenesisAgent, PaginatedResponse } from './types'

export interface AgentRunRequest {
  prompt: string
  context?: Record<string, any>
  temperature?: number
  max_tokens?: number
  stream?: boolean
  personality?: 'PRIME' | 'LONGEVITY'
}

export interface AgentRunResponse {
  agent_id: string
  response: string
  session_id?: string
  metadata?: {
    execution_time: number
    confidence_score?: number
    tokens_used?: number
  }
}

export class GenesisAgentsClient extends GenesisEcosystemClient {
  constructor(config: Omit<GenesisConfig, 'app'>) {
    super({ ...config, app: 'main' })
  }

  /**
   * Get all available agents
   */
  async getAgents(
    page: number = 1,
    pageSize: number = 100
  ): Promise<GenesisResponse<PaginatedResponse<GenesisAgent>>> {
    return this.get<PaginatedResponse<GenesisAgent>>('/api/v1/agents', {
      params: { page, page_size: pageSize }
    })
  }

  /**
   * Get specific agent details
   */
  async getAgent(agentId: string): Promise<GenesisResponse<GenesisAgent>> {
    return this.get<GenesisAgent>(`/api/v1/agents/${agentId}`)
  }

  /**
   * Get agent capabilities
   */
  async getAgentCapabilities(agentId: string): Promise<GenesisResponse<string[]>> {
    return this.get<string[]>(`/api/v1/agents/${agentId}/capabilities`)
  }

  /**
   * Run an agent
   */
  async runAgent(
    agentId: string,
    request: AgentRunRequest
  ): Promise<GenesisResponse<AgentRunResponse>> {
    return this.post<AgentRunResponse>(`/api/v1/agents/${agentId}/run`, request)
  }

  /**
   * Get agent status
   */
  async getAgentStatus(agentId: string): Promise<GenesisResponse<any>> {
    return this.get(`/api/v1/agents/${agentId}/status`)
  }

  /**
   * Stream agent response
   */
  async streamAgent(
    agentId: string,
    request: AgentRunRequest,
    onChunk: (chunk: string) => void,
    onComplete?: () => void,
    onError?: (error: Error) => void
  ): Promise<EventSource> {
    const params = new URLSearchParams({
      agent_id: agentId,
      prompt: request.prompt,
      ...(request.temperature && { temperature: request.temperature.toString() }),
      ...(request.personality && { personality: request.personality })
    })

    const eventSource = new EventSource(
      `${this.config.baseURL}/api/v1/stream/agent?${params}`,
      {
        headers: {
          'X-API-Key': this.config.apiKey
        } as any
      }
    )

    eventSource.addEventListener('chunk', (event) => {
      onChunk(event.data)
    })

    eventSource.addEventListener('complete', () => {
      onComplete?.()
      eventSource.close()
    })

    eventSource.addEventListener('error', (event) => {
      onError?.(new Error('Stream error'))
      eventSource.close()
    })

    return eventSource
  }

  /**
   * Quick methods for specific agents
   */
  async askNexus(prompt: string, context?: Record<string, any>): Promise<GenesisResponse<AgentRunResponse>> {
    return this.runAgent('nexus', { prompt, context })
  }

  async askBlaze(prompt: string, context?: Record<string, any>): Promise<GenesisResponse<AgentRunResponse>> {
    return this.runAgent('blaze', { prompt, context })
  }

  async askSage(prompt: string, context?: Record<string, any>): Promise<GenesisResponse<AgentRunResponse>> {
    return this.runAgent('sage', { prompt, context })
  }

  async askWave(prompt: string, context?: Record<string, any>): Promise<GenesisResponse<AgentRunResponse>> {
    return this.runAgent('wave', { prompt, context })
  }

  async askLuna(prompt: string, context?: Record<string, any>): Promise<GenesisResponse<AgentRunResponse>> {
    return this.runAgent('luna', { prompt, context })
  }

  async askStella(prompt: string, context?: Record<string, any>): Promise<GenesisResponse<AgentRunResponse>> {
    return this.runAgent('stella', { prompt, context })
  }

  async askSpark(prompt: string, context?: Record<string, any>): Promise<GenesisResponse<AgentRunResponse>> {
    return this.runAgent('spark', { prompt, context })
  }

  async askNova(prompt: string, context?: Record<string, any>): Promise<GenesisResponse<AgentRunResponse>> {
    return this.runAgent('nova', { prompt, context })
  }

  async askCode(prompt: string, context?: Record<string, any>): Promise<GenesisResponse<AgentRunResponse>> {
    return this.runAgent('code', { prompt, context })
  }
}