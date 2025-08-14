import { renderHook, act } from '@testing-library/react';
import { useAgentStore } from '../agentStore';

// Mock zustand persist middleware
jest.mock('zustand/middleware', () => ({
  persist: (config: any, options: any) => config
}));

describe('AgentStore', () => {
  const mockAgent = {
    id: 'trainer',
    name: 'Personal Trainer',
    description: 'Your personal fitness coach',
    avatar: '/avatars/trainer.png',
    specialties: ['strength', 'cardio', 'nutrition'],
    personality: 'motivational',
    isActive: true
  };

  beforeEach(() => {
    // Reset store state before each test
    useAgentStore.setState({
      agents: [],
      activeAgentId: null,
      selectedAgent: null,
      conversations: [],
      isLoading: false,
      error: null
    });
  });

  describe('initial state', () => {
    it('has correct default values', () => {
      const { result } = renderHook(() => useAgentStore());

      expect(result.current.agents).toEqual([]);
      expect(result.current.activeAgentId).toBeNull();
      expect(result.current.selectedAgent).toBeNull();
      expect(result.current.conversations).toEqual([]);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe('agent management', () => {
    it('adds agent to store', () => {
      const { result } = renderHook(() => useAgentStore());

      act(() => {
        result.current.addAgent(mockAgent);
      });

      expect(result.current.agents).toContain(mockAgent);
    });

    it('removes agent from store', () => {
      const { result } = renderHook(() => useAgentStore());

      act(() => {
        result.current.addAgent(mockAgent);
        result.current.removeAgent('trainer');
      });

      expect(result.current.agents).not.toContain(mockAgent);
    });

    it('updates existing agent', () => {
      const { result } = renderHook(() => useAgentStore());

      act(() => {
        result.current.addAgent(mockAgent);
        result.current.updateAgent('trainer', { name: 'Updated Trainer' });
      });

      const updatedAgent = result.current.agents.find(a => a.id === 'trainer');
      expect(updatedAgent?.name).toBe('Updated Trainer');
    });

    it('sets active agent', () => {
      const { result } = renderHook(() => useAgentStore());

      act(() => {
        result.current.setActiveAgent('trainer');
      });

      expect(result.current.activeAgentId).toBe('trainer');
    });

    it('sets selected agent', () => {
      const { result } = renderHook(() => useAgentStore());

      act(() => {
        result.current.addAgent(mockAgent);
        result.current.setSelectedAgent(mockAgent);
      });

      expect(result.current.selectedAgent).toEqual(mockAgent);
    });
  });

  describe('conversation management', () => {
    const mockConversation = {
      id: 'conv-1',
      agentId: 'trainer',
      title: 'Workout Discussion',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    it('adds conversation', () => {
      const { result } = renderHook(() => useAgentStore());

      act(() => {
        result.current.addConversation(mockConversation);
      });

      expect(result.current.conversations).toContain(mockConversation);
    });

    it('updates conversation', () => {
      const { result } = renderHook(() => useAgentStore());

      act(() => {
        result.current.addConversation(mockConversation);
        result.current.updateConversation('conv-1', { title: 'Updated Title' });
      });

      const updated = result.current.conversations.find(c => c.id === 'conv-1');
      expect(updated?.title).toBe('Updated Title');
    });

    it('removes conversation', () => {
      const { result } = renderHook(() => useAgentStore());

      act(() => {
        result.current.addConversation(mockConversation);
        result.current.removeConversation('conv-1');
      });

      expect(result.current.conversations).not.toContain(mockConversation);
    });
  });

  describe('loading and error states', () => {
    it('sets loading state', () => {
      const { result } = renderHook(() => useAgentStore());

      act(() => {
        result.current.setLoading(true);
      });

      expect(result.current.isLoading).toBe(true);
    });

    it('sets error state', () => {
      const { result } = renderHook(() => useAgentStore());

      const error = 'Something went wrong';
      act(() => {
        result.current.setError(error);
      });

      expect(result.current.error).toBe(error);
    });

    it('clears error state', () => {
      const { result } = renderHook(() => useAgentStore());

      act(() => {
        result.current.setError('Error message');
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('edge cases', () => {
    it('handles removing non-existent agent', () => {
      const { result } = renderHook(() => useAgentStore());

      expect(() => {
        act(() => {
          result.current.removeAgent('non-existent');
        });
      }).not.toThrow();
    });

    it('handles updating non-existent agent', () => {
      const { result } = renderHook(() => useAgentStore());

      expect(() => {
        act(() => {
          result.current.updateAgent('non-existent', { name: 'Updated' });
        });
      }).not.toThrow();
    });

    it('prevents duplicate agents', () => {
      const { result } = renderHook(() => useAgentStore());

      act(() => {
        result.current.addAgent(mockAgent);
        result.current.addAgent(mockAgent);
      });

      const agentCount = result.current.agents.filter(a => a.id === 'trainer').length;
      expect(agentCount).toBe(1);
    });
  });
});
