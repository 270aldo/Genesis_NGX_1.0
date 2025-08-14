/**
 * Chunk preloading utilities for optimizing load performance
 */

interface ChunkConfig {
  name: string;
  priority: 'high' | 'medium' | 'low';
  routes?: string[];
  condition?: () => boolean;
}

// Define chunk loading priorities
const chunkConfigs: ChunkConfig[] = [
  {
    name: 'react-core',
    priority: 'high',
    routes: ['*'], // Always needed
  },
  {
    name: 'ui-components',
    priority: 'high',
    routes: ['*'], // UI components used everywhere
  },
  {
    name: 'state-management',
    priority: 'high',
    routes: ['*'], // State needed globally
  },
  {
    name: 'data-fetching',
    priority: 'high',
    routes: ['/dashboard', '/chat', '/profile'],
  },
  {
    name: 'forms',
    priority: 'medium',
    routes: ['/signin', '/signup', '/settings', '/profile'],
  },
  {
    name: 'data-viz',
    priority: 'medium',
    routes: ['/dashboard', '/dashboard/progress', '/dashboard/training'],
    condition: () => window.innerWidth > 768, // Only on desktop
  },
  {
    name: 'icons',
    priority: 'medium',
    routes: ['*'],
  },
  {
    name: 'utilities',
    priority: 'low',
    routes: ['*'],
  },
  {
    name: 'animations',
    priority: 'low',
    condition: () => !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  },
  {
    name: 'media',
    priority: 'low',
    routes: ['/chat', '/dashboard/training'],
  },
];

/**
 * Preload chunks based on route and priority
 */
export function preloadChunksForRoute(route: string): void {
  const chunksToLoad = chunkConfigs.filter(config => {
    // Check if chunk should be loaded for this route
    const routeMatch = !config.routes ||
                      config.routes.includes('*') ||
                      config.routes.some(r => route.startsWith(r));

    // Check conditional loading
    const conditionMatch = !config.condition || config.condition();

    return routeMatch && conditionMatch;
  });

  // Sort by priority
  const sortedChunks = chunksToLoad.sort((a, b) => {
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    return priorityOrder[a.priority] - priorityOrder[b.priority];
  });

  // Preload chunks
  sortedChunks.forEach((chunk, index) => {
    // Delay low priority chunks
    const delay = chunk.priority === 'low' ? 2000 + (index * 500) : index * 100;

    setTimeout(() => {
      preloadChunk(chunk.name);
    }, delay);
  });
}

/**
 * Preload a specific chunk
 */
function preloadChunk(chunkName: string): void {
  // Create link element for preloading
  const link = document.createElement('link');
  link.rel = 'preload';
  link.as = 'script';
  link.href = `/assets/js/${chunkName}.*.js`; // Pattern will be resolved by build

  // Check if already preloading
  const existing = document.querySelector(`link[href*="${chunkName}"]`);
  if (!existing) {
    document.head.appendChild(link);
  }
}

/**
 * Preload critical chunks on app start
 */
export function preloadCriticalChunks(): void {
  const criticalChunks = chunkConfigs
    .filter(c => c.priority === 'high')
    .map(c => c.name);

  criticalChunks.forEach(chunk => preloadChunk(chunk));
}

/**
 * Dynamic chunk loading based on user interaction
 */
export function setupInteractionBasedLoading(): void {
  // Preload data visualization on dashboard hover
  document.addEventListener('mouseover', (e) => {
    const target = e.target as HTMLElement;
    if (target.closest('[data-preload="charts"]')) {
      preloadChunk('data-viz');
    }
  });

  // Preload forms on input focus
  document.addEventListener('focusin', (e) => {
    const target = e.target as HTMLElement;
    if (target.matches('input, textarea, select')) {
      preloadChunk('forms');
    }
  });

  // Preload media on relevant section visibility
  const mediaObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          preloadChunk('media');
          mediaObserver.disconnect();
        }
      });
    },
    { rootMargin: '100px' }
  );

  // Observe elements that might need media
  document.querySelectorAll('[data-requires="media"]').forEach(el => {
    mediaObserver.observe(el);
  });
}

/**
 * Monitor chunk loading performance
 */
export function monitorChunkPerformance(): void {
  if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'resource' && entry.name.includes('/assets/js/')) {
          const chunkName = entry.name.split('/').pop()?.split('.')[0] || 'unknown';

          // Send to analytics if needed
          if (window.gtag) {
            window.gtag('event', 'chunk_load', {
              chunk_name: chunkName,
              load_time: entry.duration,
              size: entry.transferSize,
            });
          }
        }
      });
    });

    observer.observe({ entryTypes: ['resource'] });
  }
}

/**
 * Prefetch chunks for likely next routes
 */
export function prefetchNextRoutes(currentRoute: string): void {
  const routeTransitions: Record<string, string[]> = {
    '/dashboard': ['/dashboard/progress', '/chat', '/settings'],
    '/dashboard/progress': ['/dashboard/training', '/dashboard/nutrition'],
    '/chat': ['/dashboard', '/profile'],
    '/signin': ['/signup', '/forgot-password'],
    '/signup': ['/signin'],
  };

  const nextRoutes = routeTransitions[currentRoute] || [];

  // Prefetch chunks for likely next routes after a delay
  setTimeout(() => {
    nextRoutes.forEach(route => {
      preloadChunksForRoute(route);
    });
  }, 3000);
}

// Auto-initialize on load
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    preloadCriticalChunks();
    setupInteractionBasedLoading();

    if (process.env.NODE_ENV === 'development') {
      monitorChunkPerformance();
    }
  });
}
