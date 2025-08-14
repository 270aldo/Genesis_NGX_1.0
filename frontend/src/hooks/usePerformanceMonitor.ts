/**
 * Performance Monitoring Hook for React Components
 * ==============================================
 *
 * Tracks component render times, re-renders, and performance metrics
 * to help identify performance bottlenecks during development.
 */

import { useRef, useEffect, useCallback } from 'react';

export interface PerformanceMetrics {
  renderCount: number;
  totalRenderTime: number;
  averageRenderTime: number;
  maxRenderTime: number;
  minRenderTime: number;
  slowRenderCount: number;
}

export interface UsePerformanceMonitorOptions {
  componentName?: string;
  slowRenderThreshold?: number;
  maxSamples?: number;
  enableInProduction?: boolean;
  onSlowRender?: (renderTime: number, componentName: string) => void;
  onMetricsUpdate?: (metrics: PerformanceMetrics) => void;
}

/**
 * Hook to monitor component performance
 */
export function usePerformanceMonitor(options: UsePerformanceMonitorOptions = {}) {
  const {
    componentName = 'Unknown',
    slowRenderThreshold = 16, // 16ms = 60fps threshold
    maxSamples = 100,
    enableInProduction = false,
    onSlowRender,
    onMetricsUpdate,
  } = options;

  const renderCount = useRef(0);
  const renderTimes = useRef<number[]>([]);
  const renderStartTime = useRef<number>(0);
  const isEnabled = useRef(
    process.env.NODE_ENV === 'development' || enableInProduction
  );

  // Start timing render
  const startRenderMeasurement = useCallback(() => {
    if (!isEnabled.current) return;
    renderStartTime.current = performance.now();
  }, []);

  // End timing render
  const endRenderMeasurement = useCallback(() => {
    if (!isEnabled.current || renderStartTime.current === 0) return;

    const renderTime = performance.now() - renderStartTime.current;
    renderCount.current += 1;

    // Store render time
    renderTimes.current.push(renderTime);

    // Keep only the most recent samples
    if (renderTimes.current.length > maxSamples) {
      renderTimes.current.shift();
    }

    // Check for slow renders
    if (renderTime > slowRenderThreshold) {
      console.warn(
        `🐌 Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms`
      );
      onSlowRender?.(renderTime, componentName);
    }

    // Reset start time
    renderStartTime.current = 0;

    return renderTime;
  }, [componentName, slowRenderThreshold, maxSamples, onSlowRender]);

  // Get performance metrics
  const getMetrics = useCallback((): PerformanceMetrics => {
    const times = renderTimes.current;
    const totalRenderTime = times.reduce((sum, time) => sum + time, 0);
    const slowRenderCount = times.filter(time => time > slowRenderThreshold).length;

    const metrics: PerformanceMetrics = {
      renderCount: renderCount.current,
      totalRenderTime,
      averageRenderTime: times.length > 0 ? totalRenderTime / times.length : 0,
      maxRenderTime: times.length > 0 ? Math.max(...times) : 0,
      minRenderTime: times.length > 0 ? Math.min(...times) : 0,
      slowRenderCount,
    };

    return metrics;
  }, [slowRenderThreshold]);

  // Log performance summary
  const logSummary = useCallback(() => {
    if (!isEnabled.current) return;

    const metrics = getMetrics();

    console.group(`📊 Performance Summary: ${componentName}`);
    console.log(`Total renders: ${metrics.renderCount}`);
    console.log(`Average render time: ${metrics.averageRenderTime.toFixed(2)}ms`);
    console.log(`Max render time: ${metrics.maxRenderTime.toFixed(2)}ms`);
    console.log(`Min render time: ${metrics.minRenderTime.toFixed(2)}ms`);
    console.log(`Slow renders: ${metrics.slowRenderCount}`);
    console.groupEnd();

    onMetricsUpdate?.(metrics);
  }, [componentName, getMetrics, onMetricsUpdate]);

  // Reset metrics
  const resetMetrics = useCallback(() => {
    renderCount.current = 0;
    renderTimes.current = [];
  }, []);

  // Auto-start measurement on each render
  useEffect(() => {
    startRenderMeasurement();
    return endRenderMeasurement;
  });

  // Mark component mount/unmount for profiling
  useEffect(() => {
    if (isEnabled.current && 'performance' in window && 'mark' in performance) {
      performance.mark(`${componentName}-mount`);
    }

    return () => {
      if (isEnabled.current && 'performance' in window && 'mark' in performance) {
        performance.mark(`${componentName}-unmount`);

        // Measure component lifetime
        try {
          performance.measure(
            `${componentName}-lifetime`,
            `${componentName}-mount`,
            `${componentName}-unmount`
          );
        } catch (error) {
          // Ignore measurement errors
        }
      }
    };
  }, [componentName]);

  return {
    getMetrics,
    logSummary,
    resetMetrics,
    isEnabled: isEnabled.current,
  };
}

/**
 * Higher-order component to wrap components with performance monitoring
 */
export function withPerformanceMonitoring<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options?: UsePerformanceMonitorOptions
) {
  const WithPerformanceMonitoring = (props: P) => {
    const componentName = options?.componentName || WrappedComponent.displayName || WrappedComponent.name;

    const { logSummary } = usePerformanceMonitor({
      ...options,
      componentName,
    });

    // Log summary on unmount in development
    useEffect(() => {
      return () => {
        if (process.env.NODE_ENV === 'development') {
          // Delay to ensure measurement is complete
          setTimeout(logSummary, 0);
        }
      };
    }, [logSummary]);

    return <WrappedComponent {...props} />;
  };

  WithPerformanceMonitoring.displayName = `withPerformanceMonitoring(${componentName})`;

  return WithPerformanceMonitoring;
}

/**
 * Hook to measure async operations
 */
export function useAsyncOperationMonitor() {
  const measureAsyncOperation = useCallback(async <T>(
    operation: () => Promise<T>,
    operationName: string
  ): Promise<T> => {
    const startTime = performance.now();

    try {
      const result = await operation();
      const duration = performance.now() - startTime;

      if (process.env.NODE_ENV === 'development') {
        console.log(`⚡ ${operationName} completed in ${duration.toFixed(2)}ms`);
      }

      // Mark performance event
      if ('performance' in window && 'mark' in performance) {
        performance.mark(`${operationName}-end`);
      }

      return result;
    } catch (error) {
      const duration = performance.now() - startTime;

      if (process.env.NODE_ENV === 'development') {
        console.error(`❌ ${operationName} failed after ${duration.toFixed(2)}ms`, error);
      }

      throw error;
    }
  }, []);

  return { measureAsyncOperation };
}

/**
 * Hook to monitor memory usage
 */
export function useMemoryMonitor() {
  const getMemoryInfo = useCallback(() => {
    if ('memory' in performance && (performance as any).memory) {
      const memory = (performance as any).memory;
      return {
        usedJSHeapSize: memory.usedJSHeapSize,
        totalJSHeapSize: memory.totalJSHeapSize,
        jsHeapSizeLimit: memory.jsHeapSizeLimit,
        usedPercentage: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100,
      };
    }
    return null;
  }, []);

  const logMemoryInfo = useCallback(() => {
    const memInfo = getMemoryInfo();
    if (memInfo && process.env.NODE_ENV === 'development') {
      console.group('🧠 Memory Usage');
      console.log(`Used: ${(memInfo.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`);
      console.log(`Total: ${(memInfo.totalJSHeapSize / 1024 / 1024).toFixed(2)} MB`);
      console.log(`Limit: ${(memInfo.jsHeapSizeLimit / 1024 / 1024).toFixed(2)} MB`);
      console.log(`Usage: ${memInfo.usedPercentage.toFixed(1)}%`);
      console.groupEnd();
    }
  }, [getMemoryInfo]);

  return { getMemoryInfo, logMemoryInfo };
}

/**
 * Global performance metrics store
 */
class PerformanceMetricsStore {
  private metrics = new Map<string, PerformanceMetrics>();

  updateMetrics(componentName: string, metrics: PerformanceMetrics) {
    this.metrics.set(componentName, metrics);
  }

  getMetrics(componentName: string): PerformanceMetrics | undefined {
    return this.metrics.get(componentName);
  }

  getAllMetrics(): Record<string, PerformanceMetrics> {
    return Object.fromEntries(this.metrics);
  }

  getWorstPerformers(count: number = 5): Array<{ name: string; metrics: PerformanceMetrics }> {
    return Array.from(this.metrics.entries())
      .map(([name, metrics]) => ({ name, metrics }))
      .sort((a, b) => b.metrics.averageRenderTime - a.metrics.averageRenderTime)
      .slice(0, count);
  }

  clear() {
    this.metrics.clear();
  }
}

export const globalPerformanceStore = new PerformanceMetricsStore();

// Auto-register global metrics in development
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  (window as any).getPerformanceMetrics = () => globalPerformanceStore.getAllMetrics();
  (window as any).getWorstPerformers = (count?: number) => globalPerformanceStore.getWorstPerformers(count);
}
