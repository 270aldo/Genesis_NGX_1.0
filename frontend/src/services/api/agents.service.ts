/**
 * Agents Service for NGX Agents
 * Handles agent operations, capabilities, and execution
 * Migrated from GENESIS backend architecture
 */

import { apiClient, API_ENDPOINTS } from './client';
import type { Agent } from '../../types/agent';

// Types for agent operations
export interface AgentCapability {
  id: string;
  name: string;
  description: string;
  category: 'analysis' | 'plan' | 'guidance' | 'assessment' | 'tracking';
  complexity: 'basic' | 'intermediate' | 'advanced';
  tokensRequired: number;
  estimatedTime: number; // in seconds
}

export interface AgentStatus {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'busy' | 'maintenance';
  load: number; // 0-100 percentage
  averageResponseTime: number; // in milliseconds
  successRate: number; // 0-100 percentage
  lastActivity: string;
  capabilities: AgentCapability[];
}

export interface AgentExecutionRequest {
  agentId: string;
  action: string;
  parameters?: Record<string, any>;
  context?: {
    userId?: string;
    conversationId?: string;
    includeHistory?: boolean;
    personalizedMode?: boolean;
  };
}

export interface AgentExecutionResponse {
  id: string;
  agentId: string;
  agentName: string;
  action: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
  executionTime: number;
  tokensUsed: number;
  timestamp: string;
  metadata?: {
    confidence: number;
    reasoning?: string;
    recommendations?: string[];
    nextSteps?: string[];
  };
}

export interface AgentQueryRequest {
  query: string;
  agentId?: string;
  filters?: {
    specialty?: string;
    capability?: string;
    personality?: string;
  };
  includeRecommendations?: boolean;
}

export interface AgentQueryResponse {
  recommendedAgent: Agent;
  confidence: number;
  reasoning: string;
  alternativeAgents: Array<{
    agent: Agent;
    relevanceScore: number;
    reason: string;
  }>;
  suggestedActions: Array<{
    id: string;
    label: string;
    description: string;
    agentId: string;
  }>;
}

/**
 * Agents Service Class
 * Central service for all agent operations
 */
export class AgentsService {
  private static instance: AgentsService;
  private agentsCache: Agent[] = [];
  private statusCache: Map<string, AgentStatus> = new Map();
  private cacheTimestamp: number = 0;
  private CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
  
  private constructor() {}
  
  static getInstance(): AgentsService {
    if (!AgentsService.instance) {
      AgentsService.instance = new AgentsService();
    }
    return AgentsService.instance;
  }

  /**
   * Get all available agents
   */
  async getAgents(forceRefresh: boolean = false): Promise<Agent[]> {
    try {
      const now = Date.now();
      
      // Return cached data if valid and not forcing refresh
      if (!forceRefresh && this.agentsCache.length > 0 && (now - this.cacheTimestamp) < this.CACHE_DURATION) {
        return this.agentsCache;
      }

      const response = await apiClient.get<Agent[]>(API_ENDPOINTS.AGENTS.LIST);
      
      // Update cache
      this.agentsCache = response.data;
      this.cacheTimestamp = now;
      
      return response.data;
    } catch (error: any) {
      console.error('Get agents error:', error);
      
      // Return cached data if available on error
      if (this.agentsCache.length > 0) {
        console.warn('Using cached agents data due to API error');
        return this.agentsCache;
      }
      
      throw {
        message: error.response?.data?.message || 'Failed to get agents',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Get specific agent by ID
   */
  async getAgent(agentId: string): Promise<Agent> {
    try {
      const agents = await this.getAgents();
      const agent = agents.find(a => a.id === agentId);
      
      if (!agent) {
        throw { message: 'Agent not found', code: 404 };
      }
      
      return agent;
    } catch (error: any) {
      console.error('Get agent error:', error);
      throw {
        message: error.message || 'Failed to get agent',
        code: error.code || 500,
      };
    }
  }

  /**
   * Get agents by specialty
   */
  async getAgentsBySpecialty(specialty: string): Promise<Agent[]> {
    try {
      const agents = await this.getAgents();
      return agents.filter(agent => 
        agent.specialty.toLowerCase().includes(specialty.toLowerCase()) ||
        agent.capabilities.some(cap => 
          cap.toLowerCase().includes(specialty.toLowerCase())
        )
      );
    } catch (error: any) {
      console.error('Get agents by specialty error:', error);
      throw {
        message: error.message || 'Failed to get agents by specialty',
        code: error.code || 500,
      };
    }
  }

  /**
   * Get agent status and performance metrics
   */
  async getAgentStatus(agentId: string, forceRefresh: boolean = false): Promise<AgentStatus> {
    try {
      const now = Date.now();
      const cached = this.statusCache.get(agentId);
      
      // Return cached status if valid and not forcing refresh
      if (!forceRefresh && cached && (now - this.cacheTimestamp) < this.CACHE_DURATION) {
        return cached;
      }

      const response = await apiClient.get<AgentStatus>(
        `${API_ENDPOINTS.AGENTS.STATUS}/${agentId}`
      );
      
      // Update cache
      this.statusCache.set(agentId, response.data);
      
      return response.data;
    } catch (error: any) {
      console.error('Get agent status error:', error);
      
      // Return cached status if available on error
      const cached = this.statusCache.get(agentId);
      if (cached) {
        console.warn('Using cached agent status due to API error');
        return cached;
      }
      
      throw {
        message: error.response?.data?.message || 'Failed to get agent status',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Get agent capabilities
   */
  async getAgentCapabilities(agentId: string): Promise<AgentCapability[]> {
    try {
      const response = await apiClient.get<AgentCapability[]>(
        `${API_ENDPOINTS.AGENTS.CAPABILITIES}/${agentId}`
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Get agent capabilities error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to get agent capabilities',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Execute agent action
   */
  async executeAgent(request: AgentExecutionRequest): Promise<AgentExecutionResponse> {
    try {
      const response = await apiClient.post<AgentExecutionResponse>(
        API_ENDPOINTS.AGENTS.EXECUTE,
        {
          agent_id: request.agentId,
          action: request.action,
          parameters: request.parameters,
          context: {
            user_id: request.context?.userId,
            conversation_id: request.context?.conversationId,
            include_history: request.context?.includeHistory ?? true,
            personalized_mode: request.context?.personalizedMode ?? true,
          },
        }
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Execute agent error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to execute agent',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Query for best agent recommendation
   */
  async queryAgent(request: AgentQueryRequest): Promise<AgentQueryResponse> {
    try {
      const response = await apiClient.post<AgentQueryResponse>(
        API_ENDPOINTS.AGENTS.QUERY,
        {
          query: request.query,
          agent_id: request.agentId,
          filters: {
            specialty: request.filters?.specialty,
            capability: request.filters?.capability,
            personality: request.filters?.personality,
          },
          include_recommendations: request.includeRecommendations ?? true,
        }
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Query agent error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to query agent',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Get agent execution history
   */
  async getAgentExecutionHistory(
    agentId?: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<{
    executions: AgentExecutionResponse[];
    total: number;
    hasMore: boolean;
  }> {
    try {
      const response = await apiClient.get('/api/v1/agents/executions', {
        params: {
          agent_id: agentId,
          limit,
          offset,
        },
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Get agent execution history error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to get execution history',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Get agent analytics
   */
  async getAgentAnalytics(
    agentId: string,
    timeframe: '24h' | '7d' | '30d' | '90d' = '7d'
  ): Promise<{
    executions: number;
    successRate: number;
    averageResponseTime: number;
    tokensUsed: number;
    topActions: Array<{
      action: string;
      count: number;
      percentage: number;
    }>;
    performanceMetrics: {
      uptime: number;
      throughput: number;
      errorRate: number;
    };
  }> {
    try {
      const response = await apiClient.get(`/api/v1/agents/${agentId}/analytics`, {
        params: { timeframe },
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Get agent analytics error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to get agent analytics',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Test agent connectivity
   */
  async testAgent(agentId: string): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    responseTime: number;
    details: {
      apiConnectivity: boolean;
      modelAvailability: boolean;
      databaseConnectivity: boolean;
    };
  }> {
    try {
      const response = await apiClient.get(`/api/v1/agents/${agentId}/health`);
      return response.data;
    } catch (error: any) {
      console.error('Test agent error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to test agent',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Get agent recommendations for user
   */
  async getPersonalizedAgentRecommendations(): Promise<{
    primary: Agent;
    secondary: Agent[];
    reasons: Record<string, string>;
  }> {
    try {
      const response = await apiClient.get('/api/v1/agents/recommendations');
      return response.data;
    } catch (error: any) {
      console.error('Get personalized recommendations error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to get recommendations',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.agentsCache = [];
    this.statusCache.clear();
    this.cacheTimestamp = 0;
  }

  /**
   * Get cached agents (for offline support)
   */
  getCachedAgents(): Agent[] {
    return this.agentsCache;
  }

  /**
   * Check if agent is available
   */
  async isAgentAvailable(agentId: string): Promise<boolean> {
    try {
      const status = await this.getAgentStatus(agentId);
      return status.status === 'online' && status.load < 90;
    } catch (error) {
      console.warn('Failed to check agent availability:', error);
      return false;
    }
  }

  /**
   * Get estimated execution time for action
   */
  async getEstimatedExecutionTime(
    agentId: string,
    action: string
  ): Promise<number> {
    try {
      const capabilities = await this.getAgentCapabilities(agentId);
      const capability = capabilities.find(cap => cap.id === action);
      return capability?.estimatedTime || 30; // Default 30 seconds
    } catch (error) {
      console.warn('Failed to get estimated execution time:', error);
      return 30; // Default fallback
    }
  }
}

// Export singleton instance
export const agentsService = AgentsService.getInstance();
export default agentsService;