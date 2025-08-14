/**
 * Custom hook for Personalized Chat Logic
 * Extracted from PersonalizedChatInterface for better separation of concerns
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { useHybridIntelligencePersonalization } from '@/hooks/useHybridIntelligencePersonalization';
import { useHybridIntelligenceStore } from '@/store/hybridIntelligenceStore';
import { useFeatureFlags } from '@/hooks/useFeatureFlags';
import { Message, ChatState, CollaborationData, ChatActions } from './types';

interface UsePersonalizedChatProps {
  agentId: string;
  agentName: string;
}

interface UsePersonalizedChatReturn extends ChatState, ChatActions {
  // Additional computed values
  effectiveAgentId: string;
  personalizationHooks: {
    personalizeContent: any;
    provideFeedback: any;
    getPersonalizedGreeting: any;
    checkAgentCompatibility: any;
    agentAffinity: any;
    confidenceScore: any;
    recommendations: any;
    isOptimalTime: any;
  };
  hybridIntelligence: {
    archetype: any;
    currentBiometrics: any;
    isArchetypeConfident: any;
  };
  featureFlags: {
    flags: any;
    isNexusOnlyMode: any;
    shouldShowCollaboration: any;
    shouldShowAttribution: any;
  };
  refs: {
    scrollAreaRef: React.RefObject<HTMLDivElement>;
    inputRef: React.RefObject<HTMLInputElement>;
  };
}

export const usePersonalizedChat = ({
  agentId,
  agentName,
}: UsePersonalizedChatProps): UsePersonalizedChatReturn => {
  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showPersonalizationDetails, setShowPersonalizationDetails] = useState(false);
  const [collaborationData, setCollaborationData] = useState<CollaborationData>({
    activeAgents: [],
    currentTask: '',
    estimatedTime: 0
  });

  // Refs
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Hooks
  const personalizationHooks = useHybridIntelligencePersonalization();

  const hybridIntelligence = useHybridIntelligenceStore();

  const featureFlags = useFeatureFlags();

  // Override agentId to use NEXUS in NEXUS-only mode
  const effectiveAgentId = featureFlags.isNexusOnlyMode ? 'nexus' : agentId;

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  }, [messages]);

  // Initialize with personalized greeting
  useEffect(() => {
    if (messages.length === 0 && personalizationHooks.getPersonalizedGreeting) {
      const greeting = personalizationHooks.getPersonalizedGreeting(effectiveAgentId, agentName);
      if (greeting) {
        const initialMessage: Message = {
          id: `greeting-${Date.now()}`,
          type: 'agent',
          content: greeting,
          timestamp: new Date().toISOString(),
          agentId: effectiveAgentId,
          personalizationData: {
            confidence: personalizationHooks.confidenceScore || 0.8,
            archetypeAlignment: hybridIntelligence.archetype?.name || 'balanced',
            physiologicalFactors: hybridIntelligence.currentBiometrics ?
              Object.keys(hybridIntelligence.currentBiometrics) : [],
            adaptations: personalizationHooks.recommendations || []
          }
        };
        setMessages([initialMessage]);
      }
    }
  }, [
    effectiveAgentId,
    agentName,
    messages.length,
    personalizationHooks,
    hybridIntelligence
  ]);

  // Actions
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Simulate collaboration data update
      if (featureFlags.shouldShowCollaboration) {
        setCollaborationData({
          activeAgents: [
            {
              id: effectiveAgentId,
              name: agentName,
              avatar: '',
              status: 'analyzing',
              progress: 30,
              task: 'Processing your request',
              startTime: new Date()
            }
          ],
          currentTask: 'Analyzing request with Hybrid Intelligence',
          estimatedTime: 15
        });

        // Update progress
        setTimeout(() => {
          setCollaborationData(prev => ({
            ...prev,
            activeAgents: prev.activeAgents.map(agent => ({
              ...agent,
              status: 'responding',
              progress: 80
            }))
          }));
        }, 2000);
      }

      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Generate personalized response
      let responseContent = `I understand your request: "${content}". Let me provide a personalized response based on your profile.`;

      if (personalizationHooks.personalizeContent) {
        const personalizedResponse = await personalizationHooks.personalizeContent(
          responseContent,
          effectiveAgentId
        );
        responseContent = personalizedResponse.content || responseContent;
      }

      const agentMessage: Message = {
        id: `agent-${Date.now()}`,
        type: 'agent',
        content: responseContent,
        timestamp: new Date().toISOString(),
        agentId: effectiveAgentId,
        personalizationData: {
          confidence: personalizationHooks.confidenceScore || 0.85,
          archetypeAlignment: hybridIntelligence.archetype?.name || 'balanced',
          physiologicalFactors: hybridIntelligence.currentBiometrics ?
            Object.keys(hybridIntelligence.currentBiometrics) : [],
          adaptations: personalizationHooks.recommendations || []
        }
      };

      setMessages(prev => [...prev, agentMessage]);

      // Complete collaboration
      if (featureFlags.shouldShowCollaboration) {
        setCollaborationData(prev => ({
          ...prev,
          activeAgents: prev.activeAgents.map(agent => ({
            ...agent,
            status: 'completed',
            progress: 100
          }))
        }));

        // Clear after delay
        setTimeout(() => {
          setCollaborationData({
            activeAgents: [],
            currentTask: '',
            estimatedTime: 0
          });
        }, 3000);
      }

    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'system',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [
    effectiveAgentId,
    agentName,
    personalizationHooks,
    hybridIntelligence,
    featureFlags
  ]);

  const handleFeedback = useCallback(async (
    messageId: string,
    rating: number,
    helpful: boolean
  ) => {
    try {
      // Update message with feedback
      setMessages(prev => prev.map(msg =>
        msg.id === messageId
          ? { ...msg, feedback: { rating, helpful } }
          : msg
      ));

      // Provide feedback to personalization system
      if (personalizationHooks.provideFeedback) {
        await personalizationHooks.provideFeedback({
          messageId,
          agentId: effectiveAgentId,
          rating,
          helpful,
          timestamp: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error('Error providing feedback:', error);
    }
  }, [effectiveAgentId, personalizationHooks]);

  const togglePersonalizationDetails = useCallback(() => {
    setShowPersonalizationDetails(prev => !prev);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCollaborationData({
      activeAgents: [],
      currentTask: '',
      estimatedTime: 0
    });
  }, []);

  return {
    // State
    messages,
    inputValue,
    isTyping,
    showPersonalizationDetails,
    collaborationData,

    // Actions
    sendMessage,
    handleFeedback,
    togglePersonalizationDetails,
    clearMessages,

    // Computed values
    effectiveAgentId,
    personalizationHooks,
    hybridIntelligence,
    featureFlags,

    // Refs
    refs: {
      scrollAreaRef,
      inputRef
    },

    // State setters for direct access if needed
    setInputValue,
    setIsTyping,
    setShowPersonalizationDetails,
    setCollaborationData,
  };
};
