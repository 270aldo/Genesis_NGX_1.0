/**
 * Enhanced lazy loading utility with preload support
 * 
 * This utility extends React.lazy with the ability to preload components
 * before they are actually rendered, improving perceived performance.
 */

import { ComponentType, lazy } from 'react';

export interface LazyComponent<T extends ComponentType<any>> {
  preload: () => Promise<void>;
  Component: T;
}

/**
 * Creates a lazy loaded component with preload capability
 * 
 * @param factory - Function that returns a dynamic import
 * @returns Object with Component and preload method
 * 
 * @example
 * const LazyDashboard = lazyWithPreload(() => import('./Dashboard'));
 * 
 * // Preload on hover
 * <Link onMouseEnter={() => LazyDashboard.preload()}>
 *   Dashboard
 * </Link>
 * 
 * // Use in route
 * <Route element={<LazyDashboard.Component />} />
 */
export function lazyWithPreload<T extends ComponentType<any>>(
  factory: () => Promise<{ default: T }>
): LazyComponent<T> {
  let promise: Promise<{ default: T }> | undefined;

  const load = () => {
    if (!promise) {
      promise = factory();
    }
    return promise;
  };

  const Component = lazy(load) as T;

  return {
    preload: load,
    Component,
  };
}

/**
 * Creates a lazy loaded component from a named export
 * 
 * @param factory - Function that returns a dynamic import
 * @param exportName - Name of the export to use
 * @returns Lazy loaded component
 * 
 * @example
 * const ProfileSection = lazyWithNamedExport(
 *   () => import('@/components/dashboard/ProfileSection'),
 *   'ProfileSection'
 * );
 */
export function lazyWithNamedExport<T extends ComponentType<any>>(
  factory: () => Promise<any>,
  exportName: string
): T {
  return lazy(() =>
    factory().then((module) => ({
      default: module[exportName],
    }))
  ) as T;
}

/**
 * Preloads multiple components in parallel
 * 
 * @param components - Array of components with preload method
 * @returns Promise that resolves when all components are loaded
 * 
 * @example
 * await preloadComponents([
 *   LazyDashboard,
 *   LazyProfile,
 *   LazySettings
 * ]);
 */
export async function preloadComponents(
  components: Array<{ preload: () => Promise<void> }>
): Promise<void> {
  await Promise.all(components.map((component) => component.preload()));
}

/**
 * Creates a lazy component that loads when it comes into viewport
 * 
 * @param factory - Function that returns a dynamic import
 * @param options - Intersection observer options
 * @returns Component that loads when visible
 */
export function lazyWithIntersection<T extends ComponentType<any>>(
  factory: () => Promise<{ default: T }>,
  options?: IntersectionObserverInit
): T {
  let hasLoaded = false;
  let Component: T | null = null;

  return ((props: any) => {
    if (!hasLoaded) {
      // Return a placeholder that sets up intersection observer
      return (
        <div
          ref={(ref) => {
            if (!ref) return;

            const observer = new IntersectionObserver(
              ([entry]) => {
                if (entry.isIntersecting && !hasLoaded) {
                  hasLoaded = true;
                  factory().then((module) => {
                    Component = module.default;
                    // Force re-render
                    ref.dispatchEvent(new Event('load'));
                  });
                  observer.disconnect();
                }
              },
              options || { rootMargin: '50px' }
            );

            observer.observe(ref);
          }}
        >
          Loading...
        </div>
      );
    }

    if (Component) {
      return <Component {...props} />;
    }

    return null;
  }) as T;
}

/**
 * Retry mechanism for lazy loading
 * 
 * @param factory - Function that returns a dynamic import
 * @param retries - Number of retries (default: 3)
 * @param delay - Delay between retries in ms (default: 1000)
 * @returns Lazy component with retry logic
 */
export function lazyWithRetry<T extends ComponentType<any>>(
  factory: () => Promise<{ default: T }>,
  retries = 3,
  delay = 1000
): T {
  return lazy(() =>
    factory().catch((error) => {
      if (retries > 0) {
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve(lazyWithRetry(factory, retries - 1, delay * 2));
          }, delay);
        });
      }
      throw error;
    })
  ) as T;
}