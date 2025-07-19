/**
 * WebSocket Service for NGX Agents
 * Handles A2A (Agent-to-Agent) WebSocket communication for real-time interactions
 * Integrates with GENESIS backend A2A server on port 9000
 */

// WebSocket configuration
const WS_CONFIG = {
  url: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
  a2aUrl: import.meta.env.VITE_A2A_WS_URL || 'ws://localhost:8001',
  reconnectInterval: 5000,
  maxReconnectAttempts: 5,
};
import { useChatStore } from '../../store/chatStore';
import { useAuthStore } from '../../store/authStore';

// WebSocket message types
export type WSMessageType = 
  | 'agent_response'
  | 'agent_collaboration'
  | 'agent_status_update'
  | 'user_presence'
  | 'system_notification'
  | 'typing_indicator'
  | 'error'
  | 'heartbeat';

// WebSocket message structure
export interface WSMessage {
  id: string;
  type: WSMessageType;
  timestamp: string;
  data: any;
  from?: string;
  to?: string;
  conversationId?: string;
  userId?: string;
}

// Agent status information
export interface AgentStatus {
  agentId: string;
  status: 'online' | 'offline' | 'busy' | 'processing';
  load: number; // 0-100 percentage
  activeConversations: number;
  lastActivity: string;
}

// Agent collaboration event
export interface AgentCollaboration {
  initiatorAgent: string;
  participantAgents: string[];
  collaborationType: 'workshop' | 'debate' | 'consultation' | 'handoff';
  topic: string;
  conversationId: string;
  status: 'proposed' | 'active' | 'completed' | 'cancelled';
}

// Typing indicator
export interface TypingIndicator {
  agentId: string;
  agentName: string;
  conversationId: string;
  isTyping: boolean;
}

// WebSocket connection state
export interface WSConnectionState {
  isConnected: boolean;
  isConnecting: boolean;
  isReconnecting: boolean;
  reconnectAttempts: number;
  lastConnected: Date | null;
  connectionId: string | null;
}

/**
 * WebSocket Service Class
 * Manages real-time communication with A2A server
 */
export class WebSocketService {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private connectionState: WSConnectionState = {
    isConnected: false,
    isConnecting: false,
    isReconnecting: false,
    reconnectAttempts: 0,
    lastConnected: null,
    connectionId: null
  };
  
  // Event listeners
  private messageListeners: Map<WSMessageType, Array<(message: WSMessage) => void>> = new Map();
  private statusListeners: Array<(state: WSConnectionState) => void> = [];
  private agentStatusListeners: Array<(status: AgentStatus) => void> = [];
  private typingListeners: Array<(typing: TypingIndicator) => void> = [];
  private collaborationListeners: Array<(collaboration: AgentCollaboration) => void> = [];
  
  // Timers and intervals
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  
  // Configuration
  private readonly HEARTBEAT_INTERVAL = 30000; // 30 seconds
  private readonly MAX_RECONNECT_ATTEMPTS = 10;
  private readonly RECONNECT_DELAY_BASE = 1000; // Base delay: 1 second
  
  private constructor() {}
  
  static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  /**
   * Connect to WebSocket server
   */
  async connect(): Promise<void> {
    if (this.connectionState.isConnected || this.connectionState.isConnecting) {
      return;
    }

    this.updateConnectionState({ isConnecting: true });

    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw new Error('User not authenticated');
      }

      // Build WebSocket URL with authentication
      const wsUrl = new URL(WS_CONFIG.url);
      wsUrl.searchParams.set('userId', user.id);
      wsUrl.searchParams.set('clientType', 'web');
      
      // Add auth token if available
      const authStorage = localStorage.getItem('ngx-agents-auth');
      if (authStorage) {
        try {
          const parsedStorage = JSON.parse(authStorage);
          const token = parsedStorage.state?.token || parsedStorage.token;
          if (token) {
            wsUrl.searchParams.set('token', token);
          }
        } catch (e) {
          console.warn('Error parsing auth storage for WebSocket:', e);
        }
      }

      this.ws = new WebSocket(wsUrl.toString());
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);

    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.updateConnectionState({ 
        isConnecting: false,
        reconnectAttempts: this.connectionState.reconnectAttempts + 1
      });
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
    }
    
    this.clearTimers();
    this.updateConnectionState({
      isConnected: false,
      isConnecting: false,
      isReconnecting: false,
      connectionId: null
    });
  }

  /**
   * Send message through WebSocket
   */
  send(message: Omit<WSMessage, 'id' | 'timestamp'>): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, cannot send message');
      return false;
    }

    const fullMessage: WSMessage = {
      ...message,
      id: this.generateMessageId(),
      timestamp: new Date().toISOString()
    };

    try {
      this.ws.send(JSON.stringify(fullMessage));
      return true;
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
      return false;
    }
  }

  /**
   * Subscribe to specific message types
   */
  onMessage(type: WSMessageType, callback: (message: WSMessage) => void): () => void {
    if (!this.messageListeners.has(type)) {
      this.messageListeners.set(type, []);
    }
    
    this.messageListeners.get(type)!.push(callback);
    
    // Return unsubscribe function
    return () => {
      const listeners = this.messageListeners.get(type);
      if (listeners) {
        const index = listeners.indexOf(callback);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      }
    };
  }

  /**
   * Subscribe to connection status changes
   */
  onConnectionStatusChange(callback: (state: WSConnectionState) => void): () => void {
    this.statusListeners.push(callback);
    
    // Return unsubscribe function
    return () => {
      const index = this.statusListeners.indexOf(callback);
      if (index > -1) {
        this.statusListeners.splice(index, 1);
      }
    };
  }

  /**
   * Subscribe to agent status updates
   */
  onAgentStatus(callback: (status: AgentStatus) => void): () => void {
    this.agentStatusListeners.push(callback);
    
    return () => {
      const index = this.agentStatusListeners.indexOf(callback);
      if (index > -1) {
        this.agentStatusListeners.splice(index, 1);
      }
    };
  }

  /**
   * Subscribe to typing indicators
   */
  onTyping(callback: (typing: TypingIndicator) => void): () => void {
    this.typingListeners.push(callback);
    
    return () => {
      const index = this.typingListeners.indexOf(callback);
      if (index > -1) {
        this.typingListeners.splice(index, 1);
      }
    };
  }

  /**
   * Subscribe to agent collaborations
   */
  onCollaboration(callback: (collaboration: AgentCollaboration) => void): () => void {
    this.collaborationListeners.push(callback);
    
    return () => {
      const index = this.collaborationListeners.indexOf(callback);
      if (index > -1) {
        this.collaborationListeners.splice(index, 1);
      }
    };
  }

  /**
   * Send typing indicator
   */
  sendTyping(conversationId: string, isTyping: boolean): void {
    this.send({
      type: 'typing_indicator',
      data: {
        conversationId,
        isTyping,
        timestamp: new Date().toISOString()
      }
    });
  }

  /**
   * Send agent collaboration request
   */
  sendCollaborationRequest(
    targetAgents: string[],
    collaborationType: AgentCollaboration['collaborationType'],
    topic: string,
    conversationId: string
  ): void {
    this.send({
      type: 'agent_collaboration',
      data: {
        targetAgents,
        collaborationType,
        topic,
        conversationId,
        action: 'request'
      },
      conversationId
    });
  }

  /**
   * Get current connection state
   */
  getConnectionState(): WSConnectionState {
    return { ...this.connectionState };
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.connectionState.isConnected;
  }

  // Private methods

  private handleOpen(): void {
    console.log('WebSocket connected to A2A server');
    
    this.updateConnectionState({
      isConnected: true,
      isConnecting: false,
      isReconnecting: false,
      reconnectAttempts: 0,
      lastConnected: new Date(),
      connectionId: this.generateConnectionId()
    });

    this.startHeartbeat();
    
    // Send initial presence
    this.send({
      type: 'user_presence',
      data: {
        status: 'online',
        clientInfo: {
          type: 'web',
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString()
        }
      }
    });
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WSMessage = JSON.parse(event.data);
      
      // Handle system messages
      if (message.type === 'heartbeat') {
        this.send({ type: 'heartbeat', data: { pong: true } });
        return;
      }
      
      // Dispatch to appropriate listeners
      this.dispatchMessage(message);
      
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log('WebSocket disconnected:', event.code, event.reason);
    
    this.updateConnectionState({
      isConnected: false,
      isConnecting: false,
      connectionId: null
    });

    this.clearTimers();
    
    // Attempt reconnection if not intentional disconnect
    if (event.code !== 1000) {
      this.scheduleReconnect();
    }
  }

  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    
    this.updateConnectionState({
      isConnected: false,
      isConnecting: false
    });
  }

  private dispatchMessage(message: WSMessage): void {
    // Dispatch to specific message type listeners
    const listeners = this.messageListeners.get(message.type);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(message);
        } catch (error) {
          console.error('Error in message listener:', error);
        }
      });
    }

    // Handle specific message types with dedicated listeners
    switch (message.type) {
      case 'agent_status_update':
        this.agentStatusListeners.forEach(callback => callback(message.data));
        break;
        
      case 'typing_indicator':
        this.typingListeners.forEach(callback => callback(message.data));
        break;
        
      case 'agent_collaboration':
        this.collaborationListeners.forEach(callback => callback(message.data));
        break;
        
      case 'agent_response':
        // Integration with chat store
        this.handleAgentResponse(message);
        break;
    }
  }

  private handleAgentResponse(message: WSMessage): void {
    const { addMessage } = useChatStore.getState();
    const { data, conversationId } = message;
    
    if (conversationId && data.content) {
      addMessage(conversationId, {
        content: data.content,
        role: 'assistant',
        agentId: data.agentId,
        metadata: {
          confidence: data.confidence,
          processingTime: data.processingTime,
          tokens: data.tokens,
          agentName: data.agentName,
          agentAvatar: data.agentAvatar,
          isRealTime: true
        }
      });
    }
  }

  private scheduleReconnect(): void {
    if (this.connectionState.reconnectAttempts >= this.MAX_RECONNECT_ATTEMPTS) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.updateConnectionState({ isReconnecting: true });
    
    const delay = this.RECONNECT_DELAY_BASE * Math.pow(2, this.connectionState.reconnectAttempts);
    
    this.reconnectTimeout = setTimeout(() => {
      console.log(`Attempting to reconnect (${this.connectionState.reconnectAttempts + 1}/${this.MAX_RECONNECT_ATTEMPTS})`);
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: 'heartbeat', data: { ping: true } });
      }
    }, this.HEARTBEAT_INTERVAL);
  }

  private clearTimers(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }

  private updateConnectionState(updates: Partial<WSConnectionState>): void {
    this.connectionState = { ...this.connectionState, ...updates };
    
    // Notify status listeners
    this.statusListeners.forEach(callback => {
      try {
        callback(this.connectionState);
      } catch (error) {
        console.error('Error in status listener:', error);
      }
    });
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateConnectionId(): string {
    return `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Export singleton instance
export const webSocketService = WebSocketService.getInstance();
export default webSocketService;