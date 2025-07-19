/**
 * Voice Interaction Hook
 * Provides high-level voice interaction capabilities for components
 * Integrates with backend voice services and real-time processing
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { voiceService, type VoiceActivityDetection, type ConversationalResponse } from '../services/api/voice.service';
import { useChatStore } from '../store/chatStore';
import { useAuthStore } from '../store/authStore';

export interface VoiceInteractionConfig {
  agentId?: string;
  autoStart?: boolean;
  enableRealTimeAnalysis?: boolean;
  maxRecordingDuration?: number; // in milliseconds
  silenceTimeout?: number; // in milliseconds
  language?: string;
  voice?: string;
}

export interface VoiceInteractionState {
  isInitialized: boolean;
  isRecording: boolean;
  isProcessing: boolean;
  isPlaying: boolean;
  voiceActivity: VoiceActivityDetection | null;
  lastTranscription: string | null;
  lastResponse: ConversationalResponse | null;
  error: string | null;
}

export const useVoiceInteraction = (config: VoiceInteractionConfig = {}) => {
  const {
    agentId,
    autoStart = false,
    enableRealTimeAnalysis = true,
    maxRecordingDuration = 60000, // 1 minute
    silenceTimeout = 3000, // 3 seconds
    language = 'es-ES',
    voice = 'default'
  } = config;

  // State
  const [state, setState] = useState<VoiceInteractionState>({
    isInitialized: false,
    isRecording: false,
    isProcessing: false,
    isPlaying: false,
    voiceActivity: null,
    lastTranscription: null,
    lastResponse: null,
    error: null
  });

  // Refs for managing timers and audio
  const recordingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Store hooks
  const { addMessage, getCurrentConversation } = useChatStore();
  const { user } = useAuthStore();

  // Initialize voice service
  const initialize = useCallback(async () => {
    if (state.isInitialized) return;

    try {
      setState(prev => ({ ...prev, error: null }));
      await voiceService.initialize();
      
      if (enableRealTimeAnalysis) {
        // Subscribe to voice activity detection
        voiceService.onVoiceActivity((activity) => {
          setState(prev => ({ ...prev, voiceActivity: activity }));
        });
      }

      setState(prev => ({ ...prev, isInitialized: true }));
    } catch (error: any) {
      setState(prev => ({ 
        ...prev, 
        error: error.message || 'Failed to initialize voice service',
        isInitialized: false 
      }));
    }
  }, [state.isInitialized, enableRealTimeAnalysis]);

  // Start recording
  const startRecording = useCallback(async () => {
    if (!state.isInitialized || state.isRecording) return;

    try {
      setState(prev => ({ ...prev, error: null, isRecording: true }));
      await voiceService.startRecording();

      // Set maximum recording duration
      recordingTimeoutRef.current = setTimeout(() => {
        stopRecording();
      }, maxRecordingDuration);

      // If real-time analysis is enabled, monitor for silence
      if (enableRealTimeAnalysis) {
        const checkSilence = () => {
          if (state.voiceActivity && !state.voiceActivity.isActive) {
            if (silenceTimeoutRef.current) {
              clearTimeout(silenceTimeoutRef.current);
            }
            silenceTimeoutRef.current = setTimeout(() => {
              stopRecording();
            }, silenceTimeout);
          } else if (silenceTimeoutRef.current) {
            clearTimeout(silenceTimeoutRef.current);
            silenceTimeoutRef.current = null;
          }
        };

        const intervalId = setInterval(checkSilence, 100);
        return () => clearInterval(intervalId);
      }
    } catch (error: any) {
      setState(prev => ({ 
        ...prev, 
        error: error.message || 'Failed to start recording',
        isRecording: false 
      }));
    }
  }, [state.isInitialized, state.isRecording, state.voiceActivity, maxRecordingDuration, enableRealTimeAnalysis, silenceTimeout]);

  // Stop recording and process
  const stopRecording = useCallback(async () => {
    if (!state.isRecording) return;

    try {
      // Clear timeouts
      if (recordingTimeoutRef.current) {
        clearTimeout(recordingTimeoutRef.current);
        recordingTimeoutRef.current = null;
      }
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
        silenceTimeoutRef.current = null;
      }

      setState(prev => ({ ...prev, isRecording: false, isProcessing: true }));
      
      const audioBlob = await voiceService.stopRecording();
      
      // Process the audio with conversational AI
      await processAudio(audioBlob);
    } catch (error: any) {
      setState(prev => ({ 
        ...prev, 
        error: error.message || 'Failed to stop recording',
        isRecording: false,
        isProcessing: false 
      }));
    }
  }, [state.isRecording]);

  // Process audio through conversational AI
  const processAudio = useCallback(async (audioData: Blob) => {
    if (!user || !agentId) {
      setState(prev => ({ 
        ...prev, 
        error: 'User not authenticated or agent not selected',
        isProcessing: false 
      }));
      return;
    }

    try {
      const conversation = getCurrentConversation();
      
      const response = await voiceService.conversationalInteraction({
        audioData,
        agentId,
        conversationId: conversation?.id,
        config: {
          enableRealTimeResponse: true,
          includeEmotions: true,
          contextAware: true,
          streamResponse: false
        }
      });

      // Add transcription as user message
      if (conversation && response.transcription.text) {
        addMessage(conversation.id, {
          content: response.transcription.text,
          role: 'user',
          metadata: {
            confidence: response.transcription.confidence,
            processingTime: response.transcription.metadata.processingTime,
            tokens: response.transcription.metadata.tokensUsed
          }
        });

        // Add agent response
        addMessage(conversation.id, {
          content: response.response.text,
          role: 'assistant',
          agentId,
          metadata: {
            confidence: response.response.confidence,
            processingTime: response.metadata.totalProcessingTime,
            tokens: response.metadata.tokensUsed,
            agentName: response.metadata.agentName
          }
        });
      }

      setState(prev => ({ 
        ...prev, 
        lastTranscription: response.transcription.text,
        lastResponse: response,
        isProcessing: false 
      }));

      // Play the response audio
      if (response.response.audio.audioUrl) {
        await playResponse(response.response.audio.audioUrl);
      }

    } catch (error: any) {
      setState(prev => ({ 
        ...prev, 
        error: error.message || 'Failed to process audio',
        isProcessing: false 
      }));
    }
  }, [user, agentId, getCurrentConversation, addMessage]);

  // Play audio response
  const playResponse = useCallback(async (audioUrl: string) => {
    try {
      setState(prev => ({ ...prev, isPlaying: true }));
      await voiceService.playAudio(audioUrl);
      setState(prev => ({ ...prev, isPlaying: false }));
    } catch (error: any) {
      setState(prev => ({ 
        ...prev, 
        error: error.message || 'Failed to play response',
        isPlaying: false 
      }));
    }
  }, []);

  // Quick voice message (one-shot recording and processing)
  const sendVoiceMessage = useCallback(async () => {
    if (!state.isInitialized) {
      await initialize();
    }
    
    await startRecording();
    
    // Auto-stop after a brief delay for one-shot messages
    setTimeout(() => {
      if (state.isRecording) {
        stopRecording();
      }
    }, 100);
  }, [state.isInitialized, state.isRecording, initialize, startRecording, stopRecording]);

  // Toggle recording state
  const toggleRecording = useCallback(async () => {
    if (state.isRecording) {
      await stopRecording();
    } else {
      if (!state.isInitialized) {
        await initialize();
      }
      await startRecording();
    }
  }, [state.isRecording, state.isInitialized, startRecording, stopRecording, initialize]);

  // Clear error
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Cleanup
  const cleanup = useCallback(() => {
    if (recordingTimeoutRef.current) {
      clearTimeout(recordingTimeoutRef.current);
    }
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
    }
    if (audioRef.current) {
      audioRef.current.pause();
    }
    voiceService.cleanup();
    setState({
      isInitialized: false,
      isRecording: false,
      isProcessing: false,
      isPlaying: false,
      voiceActivity: null,
      lastTranscription: null,
      lastResponse: null,
      error: null
    });
  }, []);

  // Auto-initialize if requested
  useEffect(() => {
    if (autoStart && !state.isInitialized) {
      initialize();
    }
    
    return cleanup;
  }, [autoStart, state.isInitialized, initialize, cleanup]);

  // Get voice activity metrics for visualization
  const getVoiceMetrics = useCallback(() => {
    if (!state.voiceActivity) {
      return {
        energy: 0,
        frequency: 0,
        isActive: false,
        normalizedEnergy: 0
      };
    }

    return {
      energy: state.voiceActivity.energy,
      frequency: state.voiceActivity.frequency,
      isActive: state.voiceActivity.isActive,
      normalizedEnergy: Math.min(100, Math.max(0, state.voiceActivity.energy / 2.55)) // Normalize to 0-100
    };
  }, [state.voiceActivity]);

  return {
    // State
    ...state,
    
    // Actions
    initialize,
    startRecording,
    stopRecording,
    toggleRecording,
    sendVoiceMessage,
    clearError,
    cleanup,
    
    // Utilities
    getVoiceMetrics,
    
    // Computed properties
    canRecord: state.isInitialized && !state.isProcessing && !state.isPlaying,
    isActive: state.isRecording || state.isProcessing || state.isPlaying,
    hasError: !!state.error
  };
};