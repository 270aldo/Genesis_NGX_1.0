/**
 * Feature Flags Hook
 * Manages feature flags for NGX frontend, particularly NEXUS-only mode
 * Fetches configuration from backend and provides reactive state
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/services/api/client';

export interface FeatureFlags {
  nexusOnlyMode: boolean;
  showAgentCollaboration: boolean;
  showAgentAttribution: boolean;
  showAgentActivity: boolean;
  enableVoiceReduction: boolean;
  teamCoordinationMode: boolean;
}

interface FeatureFlagsResponse {
  success: boolean;
  data: FeatureFlags;
  timestamp: string;
}

interface UseFeatureFlagsReturn {
  flags: FeatureFlags;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  isNexusOnlyMode: boolean;
  shouldShowCollaboration: boolean;
  shouldShowAttribution: boolean;
  shouldShowActivity: boolean;
}

// Default feature flags (fallback)
const DEFAULT_FLAGS: FeatureFlags = {
  nexusOnlyMode: true, // Default to new NEXUS model
  showAgentCollaboration: true,
  showAgentAttribution: true,
  showAgentActivity: true,
  enableVoiceReduction: true,
  teamCoordinationMode: true,
};

// Cache for feature flags
let cachedFlags: FeatureFlags | null = null;
let cacheTimestamp: number = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export const useFeatureFlags = (): UseFeatureFlagsReturn => {
  const [flags, setFlags] = useState<FeatureFlags>(DEFAULT_FLAGS);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFeatureFlags = useCallback(async (useCache = true) => {
    try {
      const now = Date.now();

      // Use cached data if available and fresh
      if (useCache && cachedFlags && (now - cacheTimestamp) < CACHE_DURATION) {
        setFlags(cachedFlags);
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      const response = await apiClient.get<FeatureFlagsResponse>('/api/v1/feature-flags/ngx-client');

      if (response.data.success && response.data.data) {
        const newFlags = { ...DEFAULT_FLAGS, ...response.data.data };
        setFlags(newFlags);

        // Update cache
        cachedFlags = newFlags;
        cacheTimestamp = now;
      } else {
        throw new Error('Invalid feature flags response');
      }
    } catch (err: any) {
      console.warn('Failed to fetch feature flags, using defaults:', err);
      setError(err.message || 'Failed to load feature flags');

      // Use cached data if available, otherwise use defaults
      if (cachedFlags) {
        setFlags(cachedFlags);
      } else {
        setFlags(DEFAULT_FLAGS);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refetch = useCallback(async () => {
    await fetchFeatureFlags(false); // Force fresh fetch
  }, [fetchFeatureFlags]);

  // Load feature flags on mount
  useEffect(() => {
    fetchFeatureFlags();
  }, [fetchFeatureFlags]);

  // Computed values for easier access
  const isNexusOnlyMode = flags.nexusOnlyMode;
  const shouldShowCollaboration = flags.showAgentCollaboration && isNexusOnlyMode;
  const shouldShowAttribution = flags.showAgentAttribution && isNexusOnlyMode;
  const shouldShowActivity = flags.showAgentActivity && isNexusOnlyMode;

  return {
    flags,
    isLoading,
    error,
    refetch,
    isNexusOnlyMode,
    shouldShowCollaboration,
    shouldShowAttribution,
    shouldShowActivity,
  };
};

export default useFeatureFlags;
