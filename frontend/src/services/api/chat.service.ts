/**
 * Chat Service for NGX Agents
 * Handles chat operations, message sending, and conversation management
 * Migrated from GENESIS backend architecture
 */

import { apiClient, API_ENDPOINTS } from './client';
import { useChatStore, type Message, type Conversation, type FileAttachment } from '../../store/chatStore';
import { useAuthStore } from '../../store/authStore';

// Types for chat operations
export interface SendMessageRequest {
  message: string;
  agentId?: string;
  conversationId?: string;
  attachments?: FileAttachment[];
  context?: {
    previousMessages?: number;
    includeProfile?: boolean;
    includeProgress?: boolean;
  };
}

export interface SendMessageResponse {
  id: string;
  content: string;
  agentId: string;
  agentName: string;
  agentAvatar?: string;
  metadata: {
    confidence: number;
    processingTime: number;
    tokens: number;
    modelUsed?: string;
  };
  attachments?: FileAttachment[];
}

export interface ConversationResponse {
  id: string;
  title: string;
  agentId?: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  lastMessage?: {
    content: string;
    timestamp: string;
    role: 'user' | 'assistant';
  };
}

export interface ChatHistoryRequest {
  conversationId?: string;
  agentId?: string;
  limit?: number;
  offset?: number;
  startDate?: string;
  endDate?: string;
}

export interface ChatSearchRequest {
  query: string;
  conversationId?: string;
  agentId?: string;
  limit?: number;
}

export interface StreamMessage {
  id: string;
  content: string;
  finished: boolean;
  metadata?: {
    tokens?: number;
    confidence?: number;
  };
}

/**
 * Chat Service Class
 * Central service for all chat operations
 */
export class ChatService {
  private static instance: ChatService;
  private eventSource: EventSource | null = null;
  
  private constructor() {}
  
  static getInstance(): ChatService {
    if (!ChatService.instance) {
      ChatService.instance = new ChatService();
    }
    return ChatService.instance;
  }

  /**
   * Send a message to an agent
   */
  async sendMessage(request: SendMessageRequest): Promise<SendMessageResponse> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      // Deduct tokens for message sending
      const tokensRequired = this.calculateTokensRequired(request.message, request.attachments);
      const hasEnoughTokens = useAuthStore.getState().useTokens(tokensRequired);
      
      if (!hasEnoughTokens) {
        throw { message: 'Insufficient tokens', code: 402 };
      }

      const response = await apiClient.post<SendMessageResponse>(
        API_ENDPOINTS.CHAT.SEND,
        {
          message: request.message,
          agent_id: request.agentId,
          conversation_id: request.conversationId,
          attachments: request.attachments,
          context: {
            previous_messages: request.context?.previousMessages || 5,
            include_profile: request.context?.includeProfile ?? true,
            include_progress: request.context?.includeProgress ?? true,
          },
        }
      );

      return response.data;
    } catch (error: any) {
      console.error('Send message error:', error);
      
      // Refund tokens on error
      if (error.code !== 402) {
        const tokensRequired = this.calculateTokensRequired(request.message, request.attachments);
        useAuthStore.getState().addTokens(tokensRequired);
      }
      
      throw {
        message: error.response?.data?.message || 'Failed to send message',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Send a message with streaming response
   */
  async sendMessageStream(
    request: SendMessageRequest,
    onMessage: (message: StreamMessage) => void,
    onError?: (error: any) => void,
    onComplete?: () => void
  ): Promise<void> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      // Deduct tokens for message sending
      const tokensRequired = this.calculateTokensRequired(request.message, request.attachments);
      const hasEnoughTokens = useAuthStore.getState().useTokens(tokensRequired);
      
      if (!hasEnoughTokens) {
        throw { message: 'Insufficient tokens', code: 402 };
      }

      // Close existing stream if any
      this.closeStream();

      // Create EventSource for streaming
      const streamUrl = new URL(API_ENDPOINTS.CHAT.STREAM, apiClient.defaults.baseURL);
      streamUrl.searchParams.set('message', request.message);
      if (request.agentId) streamUrl.searchParams.set('agent_id', request.agentId);
      if (request.conversationId) streamUrl.searchParams.set('conversation_id', request.conversationId);

      // Get auth token for EventSource
      const authStorage = localStorage.getItem('ngx-agents-auth');
      let token = null;
      if (authStorage) {
        const parsedStorage = JSON.parse(authStorage);
        token = parsedStorage.state?.token || parsedStorage.token;
      }

      this.eventSource = new EventSource(streamUrl.toString());

      // Add auth header (EventSource doesn't support custom headers, so we use query param)
      if (token) {
        streamUrl.searchParams.set('token', token);
        this.eventSource = new EventSource(streamUrl.toString());
      }

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('Error parsing stream message:', error);
        }
      };

      this.eventSource.onerror = (error) => {
        console.error('Stream error:', error);
        
        // Refund tokens on error
        useAuthStore.getState().addTokens(tokensRequired);
        
        if (onError) {
          onError(error);
        }
        this.closeStream();
      };

      this.eventSource.addEventListener('complete', () => {
        if (onComplete) {
          onComplete();
        }
        this.closeStream();
      });

    } catch (error: any) {
      console.error('Stream setup error:', error);
      throw {
        message: error.message || 'Failed to setup message stream',
        code: error.code || 500,
      };
    }
  }

  /**
   * Close the current stream
   */
  closeStream(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  /**
   * Get chat history
   */
  async getChatHistory(request: ChatHistoryRequest): Promise<{
    conversations: ConversationResponse[];
    total: number;
    hasMore: boolean;
  }> {
    try {
      const response = await apiClient.get(API_ENDPOINTS.CHAT.HISTORY, {
        params: {
          conversation_id: request.conversationId,
          agent_id: request.agentId,
          limit: request.limit || 20,
          offset: request.offset || 0,
          start_date: request.startDate,
          end_date: request.endDate,
        },
      });

      return response.data;
    } catch (error: any) {
      console.error('Get chat history error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to get chat history',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Search chat messages
   */
  async searchChats(request: ChatSearchRequest): Promise<{
    results: Array<{
      conversationId: string;
      messageId: string;
      content: string;
      agentName: string;
      timestamp: string;
      relevanceScore: number;
    }>;
    total: number;
  }> {
    try {
      const response = await apiClient.get(API_ENDPOINTS.CHAT.SEARCH, {
        params: {
          query: request.query,
          conversation_id: request.conversationId,
          agent_id: request.agentId,
          limit: request.limit || 10,
        },
      });

      return response.data;
    } catch (error: any) {
      console.error('Search chats error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to search chats',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Export chat conversation
   */
  async exportConversation(conversationId: string, format: 'pdf' | 'txt' | 'json' = 'pdf'): Promise<Blob> {
    try {
      const response = await apiClient.get(API_ENDPOINTS.CHAT.EXPORT, {
        params: {
          conversation_id: conversationId,
          format,
        },
        responseType: 'blob',
      });

      return response.data;
    } catch (error: any) {
      console.error('Export conversation error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to export conversation',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: string): Promise<void> {
    try {
      await apiClient.delete(`${API_ENDPOINTS.CHAT.HISTORY}/${conversationId}`);
      
      // Update local store
      useChatStore.getState().deleteConversation(conversationId);
    } catch (error: any) {
      console.error('Delete conversation error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to delete conversation',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Calculate tokens required for a message
   */
  private calculateTokensRequired(message: string, attachments?: FileAttachment[]): number {
    let tokens = Math.ceil(message.length / 4); // Rough approximation: 4 chars = 1 token
    
    // Add tokens for attachments
    if (attachments) {
      tokens += attachments.length * 10; // 10 tokens per attachment
    }
    
    // Minimum of 1 token
    return Math.max(1, tokens);
  }

  /**
   * Upload file attachment
   */
  async uploadAttachment(file: File): Promise<FileAttachment> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post('/api/v1/chat/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return {
        id: response.data.id,
        name: file.name,
        type: file.type,
        size: file.size,
        url: response.data.url,
        preview: response.data.preview,
      };
    } catch (error: any) {
      console.error('Upload attachment error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to upload attachment',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Get conversation analytics
   */
  async getConversationAnalytics(conversationId: string): Promise<{
    messageCount: number;
    tokensUsed: number;
    averageResponseTime: number;
    agentsUsed: string[];
    timeSpent: number;
    topTopics: Array<{ topic: string; frequency: number }>;
  }> {
    try {
      const response = await apiClient.get(`/api/v1/chat/analytics/${conversationId}`);
      return response.data;
    } catch (error: any) {
      console.error('Get conversation analytics error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to get conversation analytics',
        code: error.response?.status || 500,
      };
    }
  }
}

// Export singleton instance
export const chatService = ChatService.getInstance();
export default chatService;