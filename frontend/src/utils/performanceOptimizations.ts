/**
 * Frontend Performance Optimization Utilities - FASE 6
 * ====================================================
 *
 * Collection of performance optimization utilities for the GENESIS frontend
 * including lazy loading, virtual scrolling, and bundle optimization helpers.
 */

import React, { lazy, ComponentType, Suspense, memo, useMemo, useCallback } from 'react';

// ============================================================================
// LAZY LOADING UTILITIES
// ============================================================================

/**
 * Enhanced lazy component loader with error boundary and preloading
 */
export function createLazyComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  componentName: string = 'Component'
) {
  const LazyComponent = lazy(async () => {
    try {
      console.time(`Loading ${componentName}`);
      const module = await importFn();
      console.timeEnd(`Loading ${componentName}`);
      return module;
    } catch (error) {
      console.error(`Failed to load ${componentName}:`, error);
      // Return fallback component
      return {
        default: (() => (
          <div className="p-4 text-center text-red-500">
            Failed to load {componentName}. Please try again.
            <button
              onClick={() => window.location.reload()}
              className="ml-2 underline"
            >
              Reload
            </button>
          </div>
        )) as T
      };
    }
  });

  LazyComponent.displayName = `Lazy(${componentName})`;
  return LazyComponent;
}

/**
 * Preload a lazy component
 */
export function preloadComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>
): Promise<{ default: T }> {
  return importFn();
}

/**
 * Lazy component with suspense wrapper and loading state
 */
export function LazyWithSuspense<T extends ComponentType<any>>({
  component: Component,
  fallback,
  ...props
}: {
  component: ComponentType<T>;
  fallback?: React.ReactNode;
  [key: string]: any;
}) {
  const defaultFallback = (
    <div className="flex items-center justify-center p-8">
      <div className="animate-pulse">Loading...</div>
    </div>
  );

  return (
    <Suspense fallback={fallback || defaultFallback}>
      <Component {...props} />
    </Suspense>
  );
}

// ============================================================================
// MEMOIZATION UTILITIES
// ============================================================================

/**
 * Enhanced memo with shallow comparison for props
 */
export function memoComponent<T extends ComponentType<any>>(
  Component: T,
  propsAreEqual?: (prevProps: any, nextProps: any) => boolean
): T {
  const MemoizedComponent = memo(Component, propsAreEqual);
  MemoizedComponent.displayName = `Memo(${Component.displayName || Component.name})`;
  return MemoizedComponent as T;
}

/**
 * Deep comparison for complex props
 */
export function deepEqual(prevProps: any, nextProps: any): boolean {
  return JSON.stringify(prevProps) === JSON.stringify(nextProps);
}

/**
 * Shallow comparison for props (faster than deep equal)
 */
export function shallowEqual(prevProps: any, nextProps: any): boolean {
  const prevKeys = Object.keys(prevProps);
  const nextKeys = Object.keys(nextProps);

  if (prevKeys.length !== nextKeys.length) {
    return false;
  }

  for (let key of prevKeys) {
    if (prevProps[key] !== nextProps[key]) {
      return false;
    }
  }

  return true;
}

// ============================================================================
// VIRTUAL SCROLLING UTILITIES
// ============================================================================

export interface VirtualScrollProps {
  items: any[];
  itemHeight: number;
  containerHeight: number;
  renderItem: (item: any, index: number) => React.ReactNode;
  overscan?: number;
}

/**
 * Virtual scrolling hook for large lists
 */
export function useVirtualScroll({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  overscan = 5
}: VirtualScrollProps) {
  const [scrollTop, setScrollTop] = React.useState(0);

  const visibleItems = useMemo(() => {
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(items.length, startIndex + visibleCount + overscan * 2);

    return {
      startIndex,
      endIndex,
      visibleCount,
      items: items.slice(startIndex, endIndex),
      offsetY: startIndex * itemHeight,
      totalHeight: items.length * itemHeight
    };
  }, [items, itemHeight, scrollTop, containerHeight, overscan]);

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  return {
    visibleItems,
    handleScroll,
    setScrollTop
  };
}

// ============================================================================
// IMAGE OPTIMIZATION UTILITIES
// ============================================================================

/**
 * Optimized image component with lazy loading and WebP support
 */
export interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  placeholder?: string;
  quality?: number;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  className = '',
  placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjY2NjIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkxvYWRpbmcuLi48L3RleHQ+PC9zdmc+',
  quality = 85
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = React.useState(false);
  const [hasError, setHasError] = React.useState(false);

  // Generate WebP version if supported
  const webpSrc = src.replace(/\.(jpg|jpeg|png)$/i, '.webp');

  const handleLoad = useCallback(() => setIsLoaded(true), []);
  const handleError = useCallback(() => setHasError(true), []);

  if (hasError) {
    return (
      <div className={`bg-gray-200 flex items-center justify-center ${className}`}>
        <span className="text-gray-500">Failed to load image</span>
      </div>
    );
  }

  return (
    <picture>
      {/* WebP version for modern browsers */}
      <source srcSet={webpSrc} type="image/webp" />

      {/* Fallback to original format */}
      <img
        src={isLoaded ? src : placeholder}
        alt={alt}
        width={width}
        height={height}
        className={`${className} ${isLoaded ? '' : 'blur-sm'} transition-all duration-300`}
        onLoad={handleLoad}
        onError={handleError}
        loading="lazy"
        decoding="async"
      />
    </picture>
  );
}

// ============================================================================
// DEBOUNCING AND THROTTLING
// ============================================================================

/**
 * Debounce hook for expensive operations
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = React.useState<T>(value);

  React.useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Throttle hook for frequent events
 */
export function useThrottle<T>(value: T, limit: number): T {
  const [throttledValue, setThrottledValue] = React.useState<T>(value);
  const lastRan = React.useRef(Date.now());

  React.useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }
    }, limit - (Date.now() - lastRan.current));

    return () => clearTimeout(handler);
  }, [value, limit]);

  return throttledValue;
}

// ============================================================================
// PERFORMANCE MONITORING
// ============================================================================

/**
 * Performance monitoring hook
 */
export function usePerformanceMonitor(componentName: string) {
  const renderCount = React.useRef(0);
  const renderTimes = React.useRef<number[]>([]);

  React.useEffect(() => {
    renderCount.current += 1;
    const renderStart = performance.now();

    return () => {
      const renderTime = performance.now() - renderStart;
      renderTimes.current.push(renderTime);

      // Keep only last 10 render times
      if (renderTimes.current.length > 10) {
        renderTimes.current.shift();
      }

      // Log slow renders
      if (renderTime > 16) { // More than 16ms indicates potential jank
        console.warn(`Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms`);
      }
    };
  });

  const getStats = useCallback(() => {
    const times = renderTimes.current;
    const avgRenderTime = times.length > 0 ? times.reduce((a, b) => a + b) / times.length : 0;

    return {
      renderCount: renderCount.current,
      avgRenderTime: avgRenderTime.toFixed(2),
      maxRenderTime: times.length > 0 ? Math.max(...times).toFixed(2) : 0,
      minRenderTime: times.length > 0 ? Math.min(...times).toFixed(2) : 0
    };
  }, []);

  return { getStats };
}

/**
 * Bundle size analyzer for development
 */
export function analyzeBundleSize() {
  if (process.env.NODE_ENV === 'development') {
    const scripts = document.querySelectorAll('script[src]');
    const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');

    console.group('Bundle Analysis');
    console.log(`JavaScript files: ${scripts.length}`);
    console.log(`CSS files: ${stylesheets.length}`);

    // Estimate total size (this is approximate)
    let totalSize = 0;
    scripts.forEach(script => {
      const src = (script as HTMLScriptElement).src;
      if (src.includes('assets')) {
        console.log(`JS: ${src}`);
      }
    });

    stylesheets.forEach(link => {
      const href = (link as HTMLLinkElement).href;
      if (href.includes('assets')) {
        console.log(`CSS: ${href}`);
      }
    });

    console.groupEnd();
  }
}

// ============================================================================
// PRELOADING UTILITIES
// ============================================================================

/**
 * Preload critical resources
 */
export function preloadCriticalResources(resources: string[]) {
  resources.forEach(resource => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = resource.endsWith('.js') ? 'script' : 'style';
    link.href = resource;
    document.head.appendChild(link);
  });
}

/**
 * Preload component on hover/interaction
 */
export function usePreloadOnHover<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>
) {
  const [isPreloaded, setIsPreloaded] = React.useState(false);

  const preload = useCallback(async () => {
    if (!isPreloaded) {
      try {
        await importFn();
        setIsPreloaded(true);
      } catch (error) {
        console.error('Failed to preload component:', error);
      }
    }
  }, [importFn, isPreloaded]);

  return { preload, isPreloaded };
}

// ============================================================================
// EXPORT ALL UTILITIES
// ============================================================================

export default {
  // Lazy loading
  createLazyComponent,
  preloadComponent,
  LazyWithSuspense,

  // Memoization
  memoComponent,
  deepEqual,
  shallowEqual,

  // Virtual scrolling
  useVirtualScroll,

  // Image optimization
  OptimizedImage,

  // Debouncing/throttling
  useDebounce,
  useThrottle,

  // Performance monitoring
  usePerformanceMonitor,
  analyzeBundleSize,

  // Preloading
  preloadCriticalResources,
  usePreloadOnHover
};
