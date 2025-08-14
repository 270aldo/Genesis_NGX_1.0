import { renderHook, act, waitFor } from '@testing-library/react';
import { useFeatureFlags, FeatureFlags } from '../useFeatureFlags';
import { apiClient } from '@/services/api/client';

// Mock the API client
jest.mock('@/services/api/client', () => ({
  apiClient: {
    get: jest.fn()
  }
}));

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

// Mock console.warn to avoid noise in tests
const originalWarn = console.warn;
beforeAll(() => {
  console.warn = jest.fn();
});

afterAll(() => {
  console.warn = originalWarn;
});

describe('useFeatureFlags Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.clearAllTimers();

    // Clear cache before each test
    (global as any).cachedFlags = null;
    (global as any).cacheTimestamp = 0;
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  const mockSuccessResponse = {
    data: {
      success: true,
      data: {
        nexusOnlyMode: true,
        showAgentCollaboration: true,
        showAgentAttribution: true,
        showAgentActivity: true,
        enableVoiceReduction: true,
        teamCoordinationMode: true
      } as FeatureFlags,
      timestamp: '2024-01-01T00:00:00Z'
    }
  };

  describe('initialization', () => {
    it('returns default flags initially', () => {
      mockApiClient.get.mockImplementation(() => new Promise(() => {})); // Never resolves

      const { result } = renderHook(() => useFeatureFlags());

      expect(result.current.flags).toEqual({
        nexusOnlyMode: true,
        showAgentCollaboration: true,
        showAgentAttribution: true,
        showAgentActivity: true,
        enableVoiceReduction: true,
        teamCoordinationMode: true
      });
      expect(result.current.isLoading).toBe(true);
      expect(result.current.error).toBe(null);
    });

    it('fetches feature flags on mount', async () => {
      mockApiClient.get.mockResolvedValueOnce(mockSuccessResponse);

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/feature-flags/ngx-client');
      expect(result.current.flags).toEqual(mockSuccessResponse.data.data);
      expect(result.current.error).toBe(null);
    });
  });

  describe('successful API responses', () => {
    it('updates flags when API call succeeds', async () => {
      const customFlags = {
        nexusOnlyMode: false,
        showAgentCollaboration: false,
        showAgentAttribution: true,
        showAgentActivity: false,
        enableVoiceReduction: false,
        teamCoordinationMode: true
      };

      mockApiClient.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: customFlags,
          timestamp: '2024-01-01T00:00:00Z'
        }
      });

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.flags).toEqual(customFlags);
    });

    it('merges partial flags with defaults', async () => {
      const partialFlags = {
        nexusOnlyMode: false,
        showAgentCollaboration: false
        // Missing other flags
      };

      mockApiClient.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: partialFlags,
          timestamp: '2024-01-01T00:00:00Z'
        }
      });

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.flags).toEqual({
        nexusOnlyMode: false,
        showAgentCollaboration: false,
        showAgentAttribution: true, // Default
        showAgentActivity: true, // Default
        enableVoiceReduction: true, // Default
        teamCoordinationMode: true // Default
      });
    });
  });

  describe('error handling', () => {
    it('handles API errors and falls back to defaults', async () => {
      mockApiClient.get.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.flags).toEqual({
        nexusOnlyMode: true,
        showAgentCollaboration: true,
        showAgentAttribution: true,
        showAgentActivity: true,
        enableVoiceReduction: true,
        teamCoordinationMode: true
      });
      expect(result.current.error).toBe('Network error');
      expect(console.warn).toHaveBeenCalledWith('Failed to fetch feature flags, using defaults:', expect.any(Error));
    });

    it('handles invalid API responses', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        data: {
          success: false,
          data: null,
          timestamp: '2024-01-01T00:00:00Z'
        }
      });

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.flags).toEqual({
        nexusOnlyMode: true,
        showAgentCollaboration: true,
        showAgentAttribution: true,
        showAgentActivity: true,
        enableVoiceReduction: true,
        teamCoordinationMode: true
      });
      expect(result.current.error).toBe('Invalid feature flags response');
    });

    it('handles malformed API responses', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        invalidStructure: true
      });

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.flags).toEqual({
        nexusOnlyMode: true,
        showAgentCollaboration: true,
        showAgentAttribution: true,
        showAgentActivity: true,
        enableVoiceReduction: true,
        teamCoordinationMode: true
      });
      expect(result.current.error).toContain('Invalid feature flags response');
    });
  });

  describe('caching', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    it('uses cached data when available and fresh', async () => {
      // First call
      mockApiClient.get.mockResolvedValueOnce(mockSuccessResponse);

      const { result, unmount } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockApiClient.get).toHaveBeenCalledTimes(1);

      unmount();

      // Second call within cache duration (should use cache)
      jest.advanceTimersByTime(1000); // 1 second

      const { result: result2 } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result2.current.isLoading).toBe(false);
      });

      // Should not make another API call
      expect(mockApiClient.get).toHaveBeenCalledTimes(1);
      expect(result2.current.flags).toEqual(mockSuccessResponse.data.data);
    });

    it('fetches fresh data when cache is expired', async () => {
      // First call
      mockApiClient.get.mockResolvedValueOnce(mockSuccessResponse);

      const { result, unmount } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockApiClient.get).toHaveBeenCalledTimes(1);

      unmount();

      // Advance time beyond cache duration
      jest.advanceTimersByTime(6 * 60 * 1000); // 6 minutes

      const updatedFlags = {
        ...mockSuccessResponse.data.data,
        nexusOnlyMode: false
      };

      mockApiClient.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: updatedFlags,
          timestamp: '2024-01-01T00:06:00Z'
        }
      });

      const { result: result2 } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result2.current.isLoading).toBe(false);
      });

      // Should make another API call
      expect(mockApiClient.get).toHaveBeenCalledTimes(2);
      expect(result2.current.flags.nexusOnlyMode).toBe(false);
    });

    it('uses cached data as fallback when API fails', async () => {
      // First successful call to populate cache
      mockApiClient.get.mockResolvedValueOnce(mockSuccessResponse);

      const { result, unmount } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      unmount();

      // Advance time beyond cache duration
      jest.advanceTimersByTime(6 * 60 * 1000); // 6 minutes

      // Second call fails
      mockApiClient.get.mockRejectedValueOnce(new Error('Network error'));

      const { result: result2 } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result2.current.isLoading).toBe(false);
      });

      // Should use cached data even though API failed
      expect(result2.current.flags).toEqual(mockSuccessResponse.data.data);
      expect(result2.current.error).toBe('Network error');
    });
  });

  describe('refetch functionality', () => {
    it('refetch forces fresh data fetch', async () => {
      mockApiClient.get.mockResolvedValueOnce(mockSuccessResponse);

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockApiClient.get).toHaveBeenCalledTimes(1);

      const updatedFlags = {
        ...mockSuccessResponse.data.data,
        nexusOnlyMode: false
      };

      mockApiClient.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: updatedFlags,
          timestamp: '2024-01-01T00:01:00Z'
        }
      });

      await act(async () => {
        await result.current.refetch();
      });

      expect(mockApiClient.get).toHaveBeenCalledTimes(2);
      expect(result.current.flags.nexusOnlyMode).toBe(false);
    });

    it('refetch ignores cache', async () => {
      mockApiClient.get.mockResolvedValueOnce(mockSuccessResponse);

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Immediately call refetch (cache should still be fresh)
      const updatedResponse = {
        data: {
          success: true,
          data: {
            ...mockSuccessResponse.data.data,
            nexusOnlyMode: false
          },
          timestamp: '2024-01-01T00:01:00Z'
        }
      };

      mockApiClient.get.mockResolvedValueOnce(updatedResponse);

      await act(async () => {
        await result.current.refetch();
      });

      // Should have made second call despite cache being fresh
      expect(mockApiClient.get).toHaveBeenCalledTimes(2);
      expect(result.current.flags.nexusOnlyMode).toBe(false);
    });
  });

  describe('computed values', () => {
    it('computes isNexusOnlyMode correctly', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: {
            ...mockSuccessResponse.data.data,
            nexusOnlyMode: true
          },
          timestamp: '2024-01-01T00:00:00Z'
        }
      });

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.isNexusOnlyMode).toBe(true);
    });

    it('computes shouldShowCollaboration correctly', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: {
            nexusOnlyMode: true,
            showAgentCollaboration: true,
            showAgentAttribution: true,
            showAgentActivity: true,
            enableVoiceReduction: true,
            teamCoordinationMode: true
          },
          timestamp: '2024-01-01T00:00:00Z'
        }
      });

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.shouldShowCollaboration).toBe(true);
    });

    it('computes shouldShowCollaboration as false when nexusOnlyMode is false', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: {
            nexusOnlyMode: false,
            showAgentCollaboration: true,
            showAgentAttribution: true,
            showAgentActivity: true,
            enableVoiceReduction: true,
            teamCoordinationMode: true
          },
          timestamp: '2024-01-01T00:00:00Z'
        }
      });

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.shouldShowCollaboration).toBe(false);
      expect(result.current.shouldShowAttribution).toBe(false);
      expect(result.current.shouldShowActivity).toBe(false);
    });

    it('computes all conditional flags correctly', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: {
            nexusOnlyMode: true,
            showAgentCollaboration: false,
            showAgentAttribution: true,
            showAgentActivity: false,
            enableVoiceReduction: true,
            teamCoordinationMode: true
          },
          timestamp: '2024-01-01T00:00:00Z'
        }
      });

      const { result } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.shouldShowCollaboration).toBe(false); // false && true
      expect(result.current.shouldShowAttribution).toBe(true);    // true && true
      expect(result.current.shouldShowActivity).toBe(false);      // false && true
    });
  });

  describe('loading states', () => {
    it('sets loading state correctly during API call', async () => {
      let resolvePromise: (value: any) => void;
      const promise = new Promise((resolve) => {
        resolvePromise = resolve;
      });

      mockApiClient.get.mockReturnValueOnce(promise);

      const { result } = renderHook(() => useFeatureFlags());

      expect(result.current.isLoading).toBe(true);

      act(() => {
        resolvePromise!(mockSuccessResponse);
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });

    it('handles concurrent hook instances', async () => {
      mockApiClient.get.mockResolvedValue(mockSuccessResponse);

      const { result: result1 } = renderHook(() => useFeatureFlags());
      const { result: result2 } = renderHook(() => useFeatureFlags());

      await waitFor(() => {
        expect(result1.current.isLoading).toBe(false);
        expect(result2.current.isLoading).toBe(false);
      });

      expect(result1.current.flags).toEqual(result2.current.flags);
      expect(mockApiClient.get).toHaveBeenCalledTimes(2); // Each instance makes its own call initially
    });
  });
});
