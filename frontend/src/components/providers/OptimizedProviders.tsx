/**
 * Optimized Context Providers with Performance Enhancements
 * ========================================================
 *
 * This module provides optimized context providers that minimize
 * re-renders and improve overall application performance.
 */

import React, { createContext, useContext, useMemo, useCallback, ReactNode, memo } from 'react';
import { usePerformanceMonitor } from '@/hooks/usePerformanceMonitor';

// ============================================================================
// PERFORMANCE CONTEXT
// ============================================================================

interface PerformanceContextValue {
  isOptimizationEnabled: boolean;
  enableVirtualization: boolean;
  prefetchOnHover: boolean;
  enableServiceWorker: boolean;
  debugPerformance: boolean;
  toggleOptimization: () => void;
  updateSettings: (settings: Partial<PerformanceSettings>) => void;
}

interface PerformanceSettings {
  isOptimizationEnabled: boolean;
  enableVirtualization: boolean;
  prefetchOnHover: boolean;
  enableServiceWorker: boolean;
  debugPerformance: boolean;
}

const PerformanceContext = createContext<PerformanceContextValue | null>(null);

interface PerformanceProviderProps {
  children: ReactNode;
  initialSettings?: Partial<PerformanceSettings>;
}

export const PerformanceProvider = memo<PerformanceProviderProps>(({
  children,
  initialSettings = {}
}) => {
  usePerformanceMonitor({ componentName: 'PerformanceProvider' });

  const [settings, setSettings] = React.useState<PerformanceSettings>({
    isOptimizationEnabled: true,
    enableVirtualization: true,
    prefetchOnHover: true,
    enableServiceWorker: true,
    debugPerformance: process.env.NODE_ENV === 'development',
    ...initialSettings,
  });

  const toggleOptimization = useCallback(() => {
    setSettings(prev => ({
      ...prev,
      isOptimizationEnabled: !prev.isOptimizationEnabled,
    }));
  }, []);

  const updateSettings = useCallback((newSettings: Partial<PerformanceSettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  }, []);

  // Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo<PerformanceContextValue>(() => ({
    ...settings,
    toggleOptimization,
    updateSettings,
  }), [settings, toggleOptimization, updateSettings]);

  return (
    <PerformanceContext.Provider value={contextValue}>
      {children}
    </PerformanceContext.Provider>
  );
});

PerformanceProvider.displayName = 'PerformanceProvider';

export const usePerformanceSettings = (): PerformanceContextValue => {
  const context = useContext(PerformanceContext);
  if (!context) {
    throw new Error('usePerformanceSettings must be used within a PerformanceProvider');
  }
  return context;
};

// ============================================================================
// FEATURE FLAGS CONTEXT (Optimized)
// ============================================================================

interface FeatureFlagsContextValue {
  flags: Record<string, boolean>;
  isFeatureEnabled: (key: string) => boolean;
  toggleFeature: (key: string) => void;
  updateFlags: (newFlags: Record<string, boolean>) => void;
}

const FeatureFlagsContext = createContext<FeatureFlagsContextValue | null>(null);

interface FeatureFlagsProviderProps {
  children: ReactNode;
  initialFlags?: Record<string, boolean>;
}

export const FeatureFlagsProvider = memo<FeatureFlagsProviderProps>(({
  children,
  initialFlags = {}
}) => {
  usePerformanceMonitor({ componentName: 'FeatureFlagsProvider' });

  const [flags, setFlags] = React.useState<Record<string, boolean>>(initialFlags);

  // Memoized selectors to prevent unnecessary re-renders
  const isFeatureEnabled = useCallback((key: string): boolean => {
    return flags[key] ?? false;
  }, [flags]);

  const toggleFeature = useCallback((key: string) => {
    setFlags(prev => ({ ...prev, [key]: !prev[key] }));
  }, []);

  const updateFlags = useCallback((newFlags: Record<string, boolean>) => {
    setFlags(prev => ({ ...prev, ...newFlags }));
  }, []);

  const contextValue = useMemo<FeatureFlagsContextValue>(() => ({
    flags,
    isFeatureEnabled,
    toggleFeature,
    updateFlags,
  }), [flags, isFeatureEnabled, toggleFeature, updateFlags]);

  return (
    <FeatureFlagsContext.Provider value={contextValue}>
      {children}
    </FeatureFlagsContext.Provider>
  );
});

FeatureFlagsProvider.displayName = 'FeatureFlagsProvider';

export const useFeatureFlags = (): FeatureFlagsContextValue => {
  const context = useContext(FeatureFlagsContext);
  if (!context) {
    throw new Error('useFeatureFlags must be used within a FeatureFlagsProvider');
  }
  return context;
};

// ============================================================================
// THEME CONTEXT (Optimized with split state)
// ============================================================================

interface ThemeContextValue {
  theme: 'light' | 'dark' | 'auto';
  resolvedTheme: 'light' | 'dark';
  isDarkMode: boolean;
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: 'light' | 'dark' | 'auto';
}

export const ThemeProvider = memo<ThemeProviderProps>(({
  children,
  defaultTheme = 'auto'
}) => {
  usePerformanceMonitor({ componentName: 'ThemeProvider' });

  const [theme, setThemeState] = React.useState<'light' | 'dark' | 'auto'>(defaultTheme);

  // Detect system theme preference
  const systemTheme = React.useMemo(() => {
    if (typeof window === 'undefined') return 'light';
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }, []);

  // Resolve actual theme
  const resolvedTheme = useMemo(() => {
    return theme === 'auto' ? systemTheme : theme;
  }, [theme, systemTheme]);

  const isDarkMode = useMemo(() => resolvedTheme === 'dark', [resolvedTheme]);

  const setTheme = useCallback((newTheme: 'light' | 'dark' | 'auto') => {
    setThemeState(newTheme);
    // Persist to localStorage
    localStorage.setItem('theme', newTheme);
  }, []);

  // Apply theme to document
  React.useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode);
  }, [isDarkMode]);

  const contextValue = useMemo<ThemeContextValue>(() => ({
    theme,
    resolvedTheme,
    isDarkMode,
    setTheme,
  }), [theme, resolvedTheme, isDarkMode, setTheme]);

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
});

ThemeProvider.displayName = 'ThemeProvider';

export const useTheme = (): ThemeContextValue => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// ============================================================================
// VIEWPORT CONTEXT (Optimized with debouncing)
// ============================================================================

interface ViewportContextValue {
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  orientation: 'portrait' | 'landscape';
}

const ViewportContext = createContext<ViewportContextValue | null>(null);

interface ViewportProviderProps {
  children: ReactNode;
  debounceMs?: number;
}

export const ViewportProvider = memo<ViewportProviderProps>(({
  children,
  debounceMs = 100
}) => {
  usePerformanceMonitor({ componentName: 'ViewportProvider' });

  const [viewport, setViewport] = React.useState<ViewportContextValue>(() => {
    if (typeof window === 'undefined') {
      return {
        width: 1024,
        height: 768,
        isMobile: false,
        isTablet: false,
        isDesktop: true,
        orientation: 'landscape',
      };
    }

    const width = window.innerWidth;
    const height = window.innerHeight;

    return {
      width,
      height,
      isMobile: width < 768,
      isTablet: width >= 768 && width < 1024,
      isDesktop: width >= 1024,
      orientation: width > height ? 'landscape' : 'portrait',
    };
  });

  // Debounced resize handler
  React.useEffect(() => {
    if (typeof window === 'undefined') return;

    let timeoutId: NodeJS.Timeout;

    const handleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        const width = window.innerWidth;
        const height = window.innerHeight;

        setViewport({
          width,
          height,
          isMobile: width < 768,
          isTablet: width >= 768 && width < 1024,
          isDesktop: width >= 1024,
          orientation: width > height ? 'landscape' : 'portrait',
        });
      }, debounceMs);
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      clearTimeout(timeoutId);
    };
  }, [debounceMs]);

  return (
    <ViewportContext.Provider value={viewport}>
      {children}
    </ViewportContext.Provider>
  );
});

ViewportProvider.displayName = 'ViewportProvider';

export const useViewport = (): ViewportContextValue => {
  const context = useContext(ViewportContext);
  if (!context) {
    throw new Error('useViewport must be used within a ViewportProvider');
  }
  return context;
};

// ============================================================================
// COMPOSITE PROVIDER (Optimized combination)
// ============================================================================

interface OptimizedProvidersProps {
  children: ReactNode;
  performanceSettings?: Partial<PerformanceSettings>;
  featureFlags?: Record<string, boolean>;
  defaultTheme?: 'light' | 'dark' | 'auto';
  viewportDebounceMs?: number;
}

export const OptimizedProviders = memo<OptimizedProvidersProps>(({
  children,
  performanceSettings,
  featureFlags,
  defaultTheme,
  viewportDebounceMs,
}) => {
  usePerformanceMonitor({ componentName: 'OptimizedProviders' });

  return (
    <PerformanceProvider initialSettings={performanceSettings}>
      <FeatureFlagsProvider initialFlags={featureFlags}>
        <ThemeProvider defaultTheme={defaultTheme}>
          <ViewportProvider debounceMs={viewportDebounceMs}>
            {children}
          </ViewportProvider>
        </ThemeProvider>
      </FeatureFlagsProvider>
    </PerformanceProvider>
  );
});

OptimizedProviders.displayName = 'OptimizedProviders';

// ============================================================================
// PERFORMANCE UTILITIES
// ============================================================================

/**
 * HOC to prevent unnecessary re-renders based on specific prop changes
 */
export function withStableProps<P extends object>(
  Component: React.ComponentType<P>,
  stableProps: (keyof P)[]
) {
  return memo(Component, (prevProps, nextProps) => {
    // Only compare non-stable props
    const prevStable = Object.fromEntries(
      Object.entries(prevProps).filter(([key]) => !stableProps.includes(key as keyof P))
    );
    const nextStable = Object.fromEntries(
      Object.entries(nextProps).filter(([key]) => !stableProps.includes(key as keyof P))
    );

    return JSON.stringify(prevStable) === JSON.stringify(nextStable);
  });
}

/**
 * Hook to create stable callback refs
 */
export function useStableCallback<T extends (...args: any[]) => any>(callback: T): T {
  const callbackRef = React.useRef(callback);
  callbackRef.current = callback;

  return useMemo(
    () => ((...args: Parameters<T>) => callbackRef.current(...args)) as T,
    []
  );
}
