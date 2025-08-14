/**
 * Type definitions for Chat Components
 * Extracted from PersonalizedChatInterface to improve maintainability
 */

export interface Message {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  agentId?: string;
  personalizationData?: {
    confidence: number;
    archetypeAlignment: string;
    physiologicalFactors: string[];
    adaptations: string[];
  };
  feedback?: {
    rating: number;
    helpful: boolean;
  };
}

export interface PersonalizedChatInterfaceProps {
  agentId: string;
  agentName: string;
  agentIcon: React.ComponentType<{ className?: string }>;
  agentColor: string;
  onClose?: () => void;
  className?: string;
}

export interface ActiveAgent {
  id: string;
  name: string;
  avatar: string;
  status: 'consulting' | 'analyzing' | 'responding' | 'completed';
  progress: number;
  task: string;
  startTime: Date;
}

export interface CollaborationData {
  activeAgents: ActiveAgent[];
  currentTask: string;
  estimatedTime: number;
}

export interface ChatState {
  messages: Message[];
  inputValue: string;
  isTyping: boolean;
  showPersonalizationDetails: boolean;
  collaborationData: CollaborationData;
}

export interface PersonalizationDetails {
  confidence: number;
  archetype: string;
  biometrics: any;
  adaptations: string[];
  recommendations: string[];
}

export interface ChatActions {
  sendMessage: (content: string) => Promise<void>;
  handleFeedback: (messageId: string, rating: number, helpful: boolean) => Promise<void>;
  togglePersonalizationDetails: () => void;
  clearMessages: () => void;
}
