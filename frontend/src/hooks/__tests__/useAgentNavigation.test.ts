import { renderHook, act } from '@testing-library/react';
import { useNavigate } from 'react-router-dom';
import { useAgentNavigation } from '../useAgentNavigation';
import { useAgentStore } from '@/store/agentStore';
import { useFeatureFlags } from '@/hooks/useFeatureFlags';
import { FITNESS_AGENTS } from '@/data/agents';

// Mock dependencies
jest.mock('react-router-dom', () => ({
  useNavigate: jest.fn()
}));

jest.mock('@/store/agentStore', () => ({
  useAgentStore: jest.fn()
}));

jest.mock('@/hooks/useFeatureFlags', () => ({
  useFeatureFlags: jest.fn()
}));

jest.mock('@/data/agents', () => ({
  FITNESS_AGENTS: [
    { id: 'nexus', specialty: 'Coordination' },
    { id: 'trainer', specialty: 'Personal Training' },
    { id: 'nutritionist', specialty: 'Nutrition' },
    { id: 'progress', specialty: 'Progress Tracking' }
  ]
}));

const mockNavigate = jest.fn();
const mockSetActiveAgent = jest.fn();
const mockUseAgentStore = useAgentStore as jest.MockedFunction<typeof useAgentStore>;
const mockUseFeatureFlags = useFeatureFlags as jest.MockedFunction<typeof useFeatureFlags>;
const mockUseNavigate = useNavigate as jest.MockedFunction<typeof useNavigate>;

describe('useAgentNavigation Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    mockUseNavigate.mockReturnValue(mockNavigate);
    mockUseAgentStore.mockReturnValue({
      setActiveAgent: mockSetActiveAgent,
      activeAgentId: 'nexus',
      agents: [],
      isLoading: false,
      error: null,
      selectedAgent: null,
      conversations: [],
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
  });

  describe('navigateToAgent', () => {
    it('navigates directly to agent when NEXUS-only mode is disabled', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: false,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      act(() => {
        result.current.navigateToAgent('trainer');
      });

      expect(mockSetActiveAgent).toHaveBeenCalledWith('trainer');
      expect(mockNavigate).toHaveBeenCalledWith('/chat/trainer');
    });

    it('routes to NEXUS when NEXUS-only mode is enabled and agent is not nexus', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: true,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      act(() => {
        result.current.navigateToAgent('trainer');
      });

      expect(mockSetActiveAgent).toHaveBeenCalledWith('nexus');
      expect(mockNavigate).toHaveBeenCalledWith('/chat/nexus', {
        state: {
          originalAgentId: 'trainer',
          nexusCoordination: true,
          agentSpecialty: 'Personal Training'
        }
      });
    });

    it('navigates directly to nexus when requested in NEXUS-only mode', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: true,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      act(() => {
        result.current.navigateToAgent('nexus');
      });

      expect(mockSetActiveAgent).toHaveBeenCalledWith('nexus');
      expect(mockNavigate).toHaveBeenCalledWith('/chat/nexus');
    });

    it('preserves original agent context when provided', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: true,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      act(() => {
        result.current.navigateToAgent('trainer', { originalAgentId: 'nutritionist' });
      });

      expect(mockNavigate).toHaveBeenCalledWith('/chat/nexus', {
        state: {
          originalAgentId: 'nutritionist',
          nexusCoordination: true,
          agentSpecialty: 'Nutrition'
        }
      });
    });
  });

  describe('navigateToAgentSpecialty', () => {
    it('navigates to agent specialty when NEXUS-only mode is disabled', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: false,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      act(() => {
        result.current.navigateToAgentSpecialty('nutritionist');
      });

      expect(mockSetActiveAgent).toHaveBeenCalledWith('nutritionist');
      expect(mockNavigate).toHaveBeenCalledWith('/chat/nutritionist');
    });

    it('routes to NEXUS with specialty info when NEXUS-only mode is enabled', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: true,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      act(() => {
        result.current.navigateToAgentSpecialty('nutritionist');
      });

      expect(mockSetActiveAgent).toHaveBeenCalledWith('nexus');
      expect(mockNavigate).toHaveBeenCalledWith('/chat/nexus', {
        state: {
          originalAgentId: 'nutritionist',
          nexusCoordination: true,
          agentSpecialty: 'Nutrition',
          showSpecialtyInfo: true
        }
      });
    });
  });

  describe('navigateToNexusWithContext', () => {
    it('navigates to NEXUS with provided context', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: false,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());
      const additionalContext = { customField: 'value', isSpecialCase: true };

      act(() => {
        result.current.navigateToNexusWithContext('trainer', additionalContext);
      });

      expect(mockSetActiveAgent).toHaveBeenCalledWith('nexus');
      expect(mockNavigate).toHaveBeenCalledWith('/chat/nexus', {
        state: {
          originalAgentId: 'trainer',
          nexusCoordination: true,
          agentSpecialty: 'Personal Training',
          customField: 'value',
          isSpecialCase: true
        }
      });
    });

    it('works without additional context', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: false,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      act(() => {
        result.current.navigateToNexusWithContext('progress');
      });

      expect(mockSetActiveAgent).toHaveBeenCalledWith('nexus');
      expect(mockNavigate).toHaveBeenCalledWith('/chat/nexus', {
        state: {
          originalAgentId: 'progress',
          nexusCoordination: true,
          agentSpecialty: 'Progress Tracking'
        }
      });
    });
  });

  describe('getEffectiveAgentId', () => {
    it('returns original agent ID when NEXUS-only mode is disabled', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: false,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      expect(result.current.getEffectiveAgentId('trainer')).toBe('trainer');
      expect(result.current.getEffectiveAgentId('nexus')).toBe('nexus');
    });

    it('returns nexus for non-nexus agents when NEXUS-only mode is enabled', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: true,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      expect(result.current.getEffectiveAgentId('trainer')).toBe('nexus');
      expect(result.current.getEffectiveAgentId('nutritionist')).toBe('nexus');
      expect(result.current.getEffectiveAgentId('nexus')).toBe('nexus');
    });
  });

  describe('isNavigatingToNexus', () => {
    it('returns false when NEXUS-only mode is disabled', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: false,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      expect(result.current.isNavigatingToNexus('trainer')).toBe(false);
      expect(result.current.isNavigatingToNexus('nexus')).toBe(false);
    });

    it('returns true for non-nexus agents when NEXUS-only mode is enabled', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: true,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      expect(result.current.isNavigatingToNexus('trainer')).toBe(true);
      expect(result.current.isNavigatingToNexus('nutritionist')).toBe(true);
      expect(result.current.isNavigatingToNexus('nexus')).toBe(false);
    });
  });

  describe('isNexusOnlyMode property', () => {
    it('exposes the NEXUS-only mode state', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: true,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      expect(result.current.isNexusOnlyMode).toBe(true);
    });

    it('updates when NEXUS-only mode changes', () => {
      const mockFeatureFlags = {
        isNexusOnlyMode: false,
        flags: {}
      };

      mockUseFeatureFlags.mockReturnValue(mockFeatureFlags);

      const { result, rerender } = renderHook(() => useAgentNavigation());

      expect(result.current.isNexusOnlyMode).toBe(false);

      // Update the mock return value
      mockFeatureFlags.isNexusOnlyMode = true;
      mockUseFeatureFlags.mockReturnValue(mockFeatureFlags);

      rerender();

      expect(result.current.isNexusOnlyMode).toBe(true);
    });
  });

  describe('helper function getAgentSpecialty', () => {
    it('returns correct specialty for known agents', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: true,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      act(() => {
        result.current.navigateToAgent('trainer');
      });

      expect(mockNavigate).toHaveBeenCalledWith('/chat/nexus', {
        state: expect.objectContaining({
          agentSpecialty: 'Personal Training'
        })
      });
    });

    it('returns General for unknown agents', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: true,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      act(() => {
        result.current.navigateToAgent('unknown-agent');
      });

      expect(mockNavigate).toHaveBeenCalledWith('/chat/nexus', {
        state: expect.objectContaining({
          agentSpecialty: 'General'
        })
      });
    });
  });

  describe('integration scenarios', () => {
    it('handles agent navigation flow in NEXUS-only mode', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: true,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      // User tries to navigate to trainer
      act(() => {
        result.current.navigateToAgent('trainer');
      });

      expect(result.current.getEffectiveAgentId('trainer')).toBe('nexus');
      expect(result.current.isNavigatingToNexus('trainer')).toBe(true);
      expect(mockSetActiveAgent).toHaveBeenCalledWith('nexus');
      expect(mockNavigate).toHaveBeenCalledWith('/chat/nexus', {
        state: {
          originalAgentId: 'trainer',
          nexusCoordination: true,
          agentSpecialty: 'Personal Training'
        }
      });
    });

    it('handles direct agent navigation when NEXUS-only mode is disabled', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: false,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      // User navigates to nutritionist
      act(() => {
        result.current.navigateToAgent('nutritionist');
      });

      expect(result.current.getEffectiveAgentId('nutritionist')).toBe('nutritionist');
      expect(result.current.isNavigatingToNexus('nutritionist')).toBe(false);
      expect(mockSetActiveAgent).toHaveBeenCalledWith('nutritionist');
      expect(mockNavigate).toHaveBeenCalledWith('/chat/nutritionist');
    });
  });

  describe('error handling', () => {
    it('handles missing agent data gracefully', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: true,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      act(() => {
        result.current.navigateToAgent(null as any);
      });

      expect(mockSetActiveAgent).toHaveBeenCalledWith('nexus');
      expect(mockNavigate).toHaveBeenCalledWith('/chat/nexus', {
        state: {
          originalAgentId: null,
          nexusCoordination: true,
          agentSpecialty: 'General'
        }
      });
    });

    it('handles undefined agent ID', () => {
      mockUseFeatureFlags.mockReturnValue({
        isNexusOnlyMode: false,
        flags: {}
      });

      const { result } = renderHook(() => useAgentNavigation());

      act(() => {
        result.current.navigateToAgent(undefined as any);
      });

      expect(mockSetActiveAgent).toHaveBeenCalledWith(undefined);
      expect(mockNavigate).toHaveBeenCalledWith('/chat/undefined');
    });
  });
});
