import { renderHook, act, waitFor } from '@testing-library/react';
import { useVoiceConversation } from '../useVoiceConversation';
import { useConversation } from '@elevenlabs/react';
import { useAgentStore } from '@/store/agentStore';
import { useChatStore } from '@/store/chatStore';
import { toastAI, toastSuccess, toastError } from '@/components/ui/enhanced-toast';

// Mock dependencies
jest.mock('@elevenlabs/react', () => ({
  useConversation: jest.fn()
}));

jest.mock('@/store/agentStore', () => ({
  useAgentStore: jest.fn()
}));

jest.mock('@/store/chatStore', () => ({
  useChatStore: jest.fn()
}));

jest.mock('@/components/ui/enhanced-toast', () => ({
  toastAI: jest.fn(),
  toastSuccess: jest.fn(),
  toastError: jest.fn()
}));

// Mock navigator.mediaDevices
const mockGetUserMedia = jest.fn();
Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: mockGetUserMedia
  },
  writable: true
});

const mockConversation = {
  startSession: jest.fn(),
  endSession: jest.fn(),
  setVolume: jest.fn(),
  isSpeaking: false,
  status: 'idle'
};

const mockUseConversation = useConversation as jest.MockedFunction<typeof useConversation>;
const mockUseAgentStore = useAgentStore as jest.MockedFunction<typeof useAgentStore>;
const mockUseChatStore = useChatStore as jest.MockedFunction<typeof useChatStore>;

const mockGetActiveAgent = jest.fn();
const mockAddMessage = jest.fn();
const mockCreateConversation = jest.fn();

describe('useVoiceConversation Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    mockUseConversation.mockImplementation((callbacks) => {
      // Store callbacks for testing
      (mockConversation as any).callbacks = callbacks;
      return mockConversation;
    });

    mockUseAgentStore.mockReturnValue({
      getActiveAgent: mockGetActiveAgent,
      activeAgentId: 'nexus',
      agents: [],
      isLoading: false,
      error: null,
      selectedAgent: null,
      conversations: [],
      setActiveAgent: jest.fn(),
      addAgent: jest.fn(),
      removeAgent: jest.fn(),
      updateAgent: jest.fn(),
      setSelectedAgent: jest.fn(),
      addConversation: jest.fn(),
      updateConversation: jest.fn(),
      removeConversation: jest.fn(),
      setLoading: jest.fn(),
      setError: jest.fn(),
      clearError: jest.fn()
    });

    mockUseChatStore.mockReturnValue({
      addMessage: mockAddMessage,
      createConversation: mockCreateConversation,
      currentConversationId: 'conversation-123',
      conversations: [],
      currentConversation: null,
      isLoading: false,
      error: null,
      setCurrentConversationId: jest.fn(),
      updateMessage: jest.fn(),
      removeMessage: jest.fn(),
      clearConversation: jest.fn(),
      removeConversation: jest.fn(),
      setLoading: jest.fn(),
      setError: jest.fn(),
      clearError: jest.fn()
    });

    mockGetActiveAgent.mockReturnValue({
      id: 'nexus',
      name: 'NEXUS',
      specialty: 'Coordination'
    });

    mockCreateConversation.mockReturnValue('new-conversation-123');
  });

  describe('initialization', () => {
    it('initializes with correct default values', () => {
      const { result } = renderHook(() => useVoiceConversation());

      expect(result.current.isVoiceActive).toBe(false);
      expect(result.current.conversationId).toBe(null);
      expect(result.current.isSpeaking).toBe(false);
      expect(result.current.status).toBe('idle');
    });

    it('sets up conversation callbacks correctly', () => {
      renderHook(() => useVoiceConversation());

      expect(mockUseConversation).toHaveBeenCalledWith({
        onConnect: expect.any(Function),
        onDisconnect: expect.any(Function),
        onMessage: expect.any(Function),
        onError: expect.any(Function)
      });
    });
  });

  describe('conversation callbacks', () => {
    it('handles onConnect callback', () => {
      const { result } = renderHook(() => useVoiceConversation());
      const callbacks = (mockConversation as any).callbacks;

      act(() => {
        callbacks.onConnect();
      });

      expect(result.current.isVoiceActive).toBe(true);
      expect(toastSuccess).toHaveBeenCalledWith('Voice conversation started');
    });

    it('handles onDisconnect callback', () => {
      const { result } = renderHook(() => useVoiceConversation());
      const callbacks = (mockConversation as any).callbacks;

      // First connect
      act(() => {
        callbacks.onConnect();
      });

      expect(result.current.isVoiceActive).toBe(true);

      // Then disconnect
      act(() => {
        callbacks.onDisconnect();
      });

      expect(result.current.isVoiceActive).toBe(false);
      expect(toastAI).toHaveBeenCalledWith('Voice conversation ended');
    });

    it('handles user messages in onMessage callback', () => {
      renderHook(() => useVoiceConversation());
      const callbacks = (mockConversation as any).callbacks;

      const userMessage = {
        source: 'user',
        message: 'Hello, how are you?'
      };

      act(() => {
        callbacks.onMessage(userMessage);
      });

      expect(mockAddMessage).toHaveBeenCalledWith('conversation-123', {
        content: 'Hello, how are you?',
        role: 'user',
        agentId: 'nexus'
      });
    });

    it('handles AI messages in onMessage callback', () => {
      renderHook(() => useVoiceConversation());
      const callbacks = (mockConversation as any).callbacks;

      const aiMessage = {
        source: 'ai',
        message: 'I am doing well, thank you!'
      };

      act(() => {
        callbacks.onMessage(aiMessage);
      });

      expect(mockAddMessage).toHaveBeenCalledWith('conversation-123', {
        content: 'I am doing well, thank you!',
        role: 'assistant',
        agentId: 'nexus',
        metadata: {
          confidence: 0.95
        }
      });
    });

    it('creates new conversation when currentConversationId is null', () => {
      mockUseChatStore.mockReturnValue({
        ...mockUseChatStore(),
        currentConversationId: null
      });

      renderHook(() => useVoiceConversation());
      const callbacks = (mockConversation as any).callbacks;

      const userMessage = {
        source: 'user',
        message: 'Hello'
      };

      act(() => {
        callbacks.onMessage(userMessage);
      });

      expect(mockCreateConversation).toHaveBeenCalled();
      expect(mockAddMessage).toHaveBeenCalledWith('new-conversation-123', {
        content: 'Hello',
        role: 'user',
        agentId: 'nexus'
      });
    });

    it('ignores messages without content', () => {
      renderHook(() => useVoiceConversation());
      const callbacks = (mockConversation as any).callbacks;

      const emptyMessage = {
        source: 'user',
        message: ''
      };

      act(() => {
        callbacks.onMessage(emptyMessage);
      });

      expect(mockAddMessage).not.toHaveBeenCalled();
    });

    it('handles error callback', () => {
      const { result } = renderHook(() => useVoiceConversation());
      const callbacks = (mockConversation as any).callbacks;

      // First connect
      act(() => {
        callbacks.onConnect();
      });

      expect(result.current.isVoiceActive).toBe(true);

      const error = new Error('Microphone access denied');
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      act(() => {
        callbacks.onError(error);
      });

      expect(result.current.isVoiceActive).toBe(false);
      expect(consoleSpy).toHaveBeenCalledWith('Voice conversation error:', error);
      expect(toastError).toHaveBeenCalledWith('Voice conversation error', 'Please check your microphone and try again');

      consoleSpy.mockRestore();
    });
  });

  describe('startVoiceConversation', () => {
    it('successfully starts voice conversation', async () => {
      mockGetUserMedia.mockResolvedValueOnce(new MediaStream());
      mockConversation.startSession.mockResolvedValueOnce('session-123');

      const { result } = renderHook(() => useVoiceConversation());

      await act(async () => {
        await result.current.startVoiceConversation();
      });

      expect(mockGetUserMedia).toHaveBeenCalledWith({ audio: true });
      expect(mockConversation.startSession).toHaveBeenCalledWith({
        agentId: 'default'
      });
      expect(result.current.conversationId).toBe('session-123');
      expect(toastAI).toHaveBeenCalledWith('Voice mode activated', 'Speak naturally with your AI agent');
    });

    it('starts conversation with specific agent ID', async () => {
      mockGetUserMedia.mockResolvedValueOnce(new MediaStream());
      mockConversation.startSession.mockResolvedValueOnce('session-456');

      const { result } = renderHook(() => useVoiceConversation());

      await act(async () => {
        await result.current.startVoiceConversation('trainer');
      });

      expect(mockConversation.startSession).toHaveBeenCalledWith({
        agentId: 'trainer'
      });
      expect(result.current.conversationId).toBe('session-456');
    });

    it('handles microphone access denial', async () => {
      const error = new Error('Permission denied');
      mockGetUserMedia.mockRejectedValueOnce(error);
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      const { result } = renderHook(() => useVoiceConversation());

      await act(async () => {
        await result.current.startVoiceConversation();
      });

      expect(mockConversation.startSession).not.toHaveBeenCalled();
      expect(result.current.conversationId).toBe(null);
      expect(consoleSpy).toHaveBeenCalledWith('Failed to start voice conversation:', error);
      expect(toastError).toHaveBeenCalledWith('Voice activation failed', 'Please ensure microphone access is granted');

      consoleSpy.mockRestore();
    });

    it('handles session start failure', async () => {
      mockGetUserMedia.mockResolvedValueOnce(new MediaStream());
      const error = new Error('Session start failed');
      mockConversation.startSession.mockRejectedValueOnce(error);
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      const { result } = renderHook(() => useVoiceConversation());

      await act(async () => {
        await result.current.startVoiceConversation();
      });

      expect(result.current.conversationId).toBe(null);
      expect(consoleSpy).toHaveBeenCalledWith('Failed to start voice conversation:', error);
      expect(toastError).toHaveBeenCalledWith('Voice activation failed', 'Please ensure microphone access is granted');

      consoleSpy.mockRestore();
    });
  });

  describe('endVoiceConversation', () => {
    it('successfully ends voice conversation', async () => {
      mockConversation.endSession.mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => useVoiceConversation());

      // Set conversation ID first
      act(() => {
        (result.current as any).setConversationId('session-123');
      });

      await act(async () => {
        await result.current.endVoiceConversation();
      });

      expect(mockConversation.endSession).toHaveBeenCalled();
      expect(result.current.conversationId).toBe(null);
    });

    it('handles end session failure', async () => {
      const error = new Error('End session failed');
      mockConversation.endSession.mockRejectedValueOnce(error);
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      const { result } = renderHook(() => useVoiceConversation());

      await act(async () => {
        await result.current.endVoiceConversation();
      });

      expect(consoleSpy).toHaveBeenCalledWith('Failed to end voice conversation:', error);

      consoleSpy.mockRestore();
    });
  });

  describe('setVolume', () => {
    it('successfully sets volume', async () => {
      mockConversation.setVolume.mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => useVoiceConversation());

      await act(async () => {
        await result.current.setVolume(0.8);
      });

      expect(mockConversation.setVolume).toHaveBeenCalledWith({ volume: 0.8 });
    });

    it('handles set volume failure', async () => {
      const error = new Error('Set volume failed');
      mockConversation.setVolume.mockRejectedValueOnce(error);
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      const { result } = renderHook(() => useVoiceConversation());

      await act(async () => {
        await result.current.setVolume(0.5);
      });

      expect(consoleSpy).toHaveBeenCalledWith('Failed to set volume:', error);

      consoleSpy.mockRestore();
    });
  });

  describe('conversation status and speaking state', () => {
    it('reflects conversation speaking state', () => {
      mockConversation.isSpeaking = true;

      const { result } = renderHook(() => useVoiceConversation());

      expect(result.current.isSpeaking).toBe(true);
    });

    it('reflects conversation status', () => {
      mockConversation.status = 'connected';

      const { result } = renderHook(() => useVoiceConversation());

      expect(result.current.status).toBe('connected');
    });

    it('handles undefined conversation properties', () => {
      mockConversation.isSpeaking = undefined;
      mockConversation.status = undefined;

      const { result } = renderHook(() => useVoiceConversation());

      expect(result.current.isSpeaking).toBe(false);
      expect(result.current.status).toBeUndefined();
    });
  });

  describe('integration scenarios', () => {
    it('handles full voice conversation flow', async () => {
      mockGetUserMedia.mockResolvedValueOnce(new MediaStream());
      mockConversation.startSession.mockResolvedValueOnce('session-123');
      mockConversation.endSession.mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => useVoiceConversation());
      const callbacks = (mockConversation as any).callbacks;

      // Start conversation
      await act(async () => {
        await result.current.startVoiceConversation('trainer');
      });

      expect(result.current.conversationId).toBe('session-123');

      // Simulate connection
      act(() => {
        callbacks.onConnect();
      });

      expect(result.current.isVoiceActive).toBe(true);
      expect(toastSuccess).toHaveBeenCalledWith('Voice conversation started');

      // Simulate user message
      act(() => {
        callbacks.onMessage({
          source: 'user',
          message: 'Create a workout plan'
        });
      });

      expect(mockAddMessage).toHaveBeenCalledWith('conversation-123', {
        content: 'Create a workout plan',
        role: 'user',
        agentId: 'nexus'
      });

      // Simulate AI response
      act(() => {
        callbacks.onMessage({
          source: 'ai',
          message: 'I will create a personalized workout plan for you.'
        });
      });

      expect(mockAddMessage).toHaveBeenCalledWith('conversation-123', {
        content: 'I will create a personalized workout plan for you.',
        role: 'assistant',
        agentId: 'nexus',
        metadata: {
          confidence: 0.95
        }
      });

      // End conversation
      await act(async () => {
        await result.current.endVoiceConversation();
      });

      expect(result.current.conversationId).toBe(null);

      // Simulate disconnect
      act(() => {
        callbacks.onDisconnect();
      });

      expect(result.current.isVoiceActive).toBe(false);
      expect(toastAI).toHaveBeenCalledWith('Voice conversation ended');
    });
  });
});
