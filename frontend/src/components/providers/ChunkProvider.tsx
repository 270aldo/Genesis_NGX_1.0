import React, { createContext, useContext, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  preloadChunksForRoute, 
  prefetchNextRoutes,
  monitorChunkPerformance 
} from '@/utils/chunkPreload';

interface ChunkContextValue {
  preloadRoute: (route: string) => void;
  preloadChunk: (chunkName: string) => void;
}

const ChunkContext = createContext<ChunkContextValue | null>(null);

export const useChunkPreload = () => {
  const context = useContext(ChunkContext);
  if (!context) {
    throw new Error('useChunkPreload must be used within ChunkProvider');
  }
  return context;
};

interface ChunkProviderProps {
  children: React.ReactNode;
}

/**
 * Provider component that manages chunk loading strategies
 */
export const ChunkProvider: React.FC<ChunkProviderProps> = ({ children }) => {
  const location = useLocation();

  // Preload chunks for current route
  useEffect(() => {
    preloadChunksForRoute(location.pathname);
    
    // Prefetch likely next routes after a delay
    const timer = setTimeout(() => {
      prefetchNextRoutes(location.pathname);
    }, 2000);

    return () => clearTimeout(timer);
  }, [location.pathname]);

  // Setup performance monitoring in development
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      monitorChunkPerformance();
    }
  }, []);

  const preloadRoute = useCallback((route: string) => {
    preloadChunksForRoute(route);
  }, []);

  const preloadChunk = useCallback((chunkName: string) => {
    const link = document.createElement('link');
    link.rel = 'modulepreload';
    link.href = `/assets/js/${chunkName}.js`;
    
    if (!document.querySelector(`link[href="${link.href}"]`)) {
      document.head.appendChild(link);
    }
  }, []);

  return (
    <ChunkContext.Provider value={{ preloadRoute, preloadChunk }}>
      {children}
    </ChunkContext.Provider>
  );
};

/**
 * HOC to add chunk preloading to components
 */
export function withChunkPreload<P extends object>(
  Component: React.ComponentType<P>,
  chunks: string[]
): React.ComponentType<P> {
  return (props: P) => {
    const { preloadChunk } = useChunkPreload();

    useEffect(() => {
      chunks.forEach(chunk => preloadChunk(chunk));
    }, [preloadChunk]);

    return <Component {...props} />;
  };
}

/**
 * Hook to preload chunks based on user actions
 */
export function useActionBasedPreload() {
  const { preloadChunk } = useChunkPreload();

  const preloadOnHover = useCallback((chunks: string[]) => {
    return {
      onMouseEnter: () => {
        chunks.forEach(chunk => preloadChunk(chunk));
      },
    };
  }, [preloadChunk]);

  const preloadOnFocus = useCallback((chunks: string[]) => {
    return {
      onFocus: () => {
        chunks.forEach(chunk => preloadChunk(chunk));
      },
    };
  }, [preloadChunk]);

  return { preloadOnHover, preloadOnFocus };
}