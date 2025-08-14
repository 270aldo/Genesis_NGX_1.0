
import { useConversation } from '@elevenlabs/react';
import { useState, useCallback } from 'react';
import { useAgentStore } from '@/store/agentStore';
import { useChatStore } from '@/store/chatStore';
import { toastAI, toastSuccess, toastError } from '@/components/ui/enhanced-toast';

export const useVoiceConversation = () => {
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const { getActiveAgent } = useAgentStore();
  const { addMessage, createConversation, currentConversationId } = useChatStore();

  const conversation = useConversation({
    onConnect: () => {
      setIsVoiceActive(true);
      toastSuccess('Voice conversation started');
    },
    onDisconnect: () => {
      setIsVoiceActive(false);
      toastAI('Voice conversation ended');
    },
    onMessage: (message) => {

      // Add voice messages to chat history
      if (message.source === 'user' && message.message) {
        const chatId = currentConversationId || createConversation();
        addMessage(chatId, {
          content: message.message,
          role: 'user',
          agentId: getActiveAgent()?.id
        });
      }

      if (message.source === 'ai' && message.message) {
        const chatId = currentConversationId || createConversation();
        addMessage(chatId, {
          content: message.message,
          role: 'assistant',
          agentId: getActiveAgent()?.id,
          metadata: {
            confidence: 0.95
          }
        });
      }
    },
    onError: (error) => {
      console.error('Voice conversation error:', error);
      toastError('Voice conversation error', 'Please check your microphone and try again');
      setIsVoiceActive(false);
    }
  });

  const startVoiceConversation = useCallback(async (agentId?: string) => {
    try {
      // Request microphone access
      await navigator.mediaDevices.getUserMedia({ audio: true });

      // For now, we'll use a placeholder URL - in production, you'd need to:
      // 1. Create agents in ElevenLabs UI
      // 2. Get signed URLs from your backend
      const id = await conversation.startSession({
        agentId: agentId || 'default'
      });

      setConversationId(id);
      toastAI('Voice mode activated', 'Speak naturally with your AI agent');
    } catch (error) {
      console.error('Failed to start voice conversation:', error);
      toastError('Voice activation failed', 'Please ensure microphone access is granted');
    }
  }, [conversation]);

  const endVoiceConversation = useCallback(async () => {
    try {
      await conversation.endSession();
      setConversationId(null);
    } catch (error) {
      console.error('Failed to end voice conversation:', error);
    }
  }, [conversation]);

  const setVolume = useCallback(async (volume: number) => {
    try {
      await conversation.setVolume({ volume });
    } catch (error) {
      console.error('Failed to set volume:', error);
    }
  }, [conversation]);

  return {
    isVoiceActive,
    conversationId,
    isSpeaking: conversation.isSpeaking || false,
    status: conversation.status,
    startVoiceConversation,
    endVoiceConversation,
    setVolume
  };
};
