/**
 * CDN Configuration for Frontend Assets
 * 
 * This module configures CDN URLs for static assets, images, and API endpoints
 * to optimize performance and reduce load on the origin server.
 */

interface CDNConfig {
  enabled: boolean;
  baseUrl: string;
  imageUrl: string;
  staticUrl: string;
  apiUrl: string;
}

// Environment-based CDN configuration
const CDN_CONFIG: Record<string, CDNConfig> = {
  production: {
    enabled: true,
    baseUrl: 'https://cdn.ngx-agents.com',
    imageUrl: 'https://cdn.ngx-agents.com/images',
    staticUrl: 'https://cdn.ngx-agents.com/static',
    apiUrl: 'https://api.ngx-agents.com'
  },
  staging: {
    enabled: true,
    baseUrl: 'https://staging-cdn.ngx-agents.com',
    imageUrl: 'https://staging-cdn.ngx-agents.com/images',
    staticUrl: 'https://staging-cdn.ngx-agents.com/static',
    apiUrl: 'https://staging-api.ngx-agents.com'
  },
  development: {
    enabled: false,
    baseUrl: '',
    imageUrl: '/images',
    staticUrl: '/static',
    apiUrl: 'http://localhost:8000'
  }
};

// Get current environment
const ENV = import.meta.env.MODE || 'development';

// Export current CDN configuration
export const cdnConfig = CDN_CONFIG[ENV] || CDN_CONFIG.development;

/**
 * Get CDN URL for an asset
 * @param path - Asset path
 * @param type - Asset type (image, static, etc)
 * @returns Full CDN URL
 */
export function getCDNUrl(path: string, type: 'image' | 'static' | 'api' = 'static'): string {
  if (!cdnConfig.enabled) {
    return path;
  }

  // Remove leading slash if present
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;

  switch (type) {
    case 'image':
      return `${cdnConfig.imageUrl}/${cleanPath}`;
    case 'api':
      return `${cdnConfig.apiUrl}/${cleanPath}`;
    default:
      return `${cdnConfig.staticUrl}/${cleanPath}`;
  }
}

/**
 * Get optimized image URL with responsive parameters
 * @param path - Image path
 * @param options - Image optimization options
 * @returns Optimized CDN URL
 */
export function getOptimizedImageUrl(
  path: string,
  options: {
    width?: number;
    height?: number;
    quality?: number;
    format?: 'webp' | 'avif' | 'auto';
  } = {}
): string {
  const baseUrl = getCDNUrl(path, 'image');
  
  if (!cdnConfig.enabled) {
    return baseUrl;
  }

  const params = new URLSearchParams();
  
  if (options.width) params.append('w', options.width.toString());
  if (options.height) params.append('h', options.height.toString());
  if (options.quality) params.append('q', options.quality.toString());
  if (options.format) params.append('f', options.format);
  
  // Add cache busting parameter based on build version
  params.append('v', import.meta.env.VITE_APP_VERSION || '1.0.0');
  
  return `${baseUrl}?${params.toString()}`;
}

/**
 * Generate srcset for responsive images
 * @param path - Image path
 * @param widths - Array of widths
 * @returns srcset string
 */
export function generateSrcSet(path: string, widths: number[] = [640, 750, 828, 1080, 1200, 1920]): string {
  return widths
    .map(width => `${getOptimizedImageUrl(path, { width })} ${width}w`)
    .join(', ');
}

/**
 * Preload critical assets
 * @param assets - Array of asset paths to preload
 */
export function preloadAssets(assets: string[]): void {
  assets.forEach(asset => {
    const link = document.createElement('link');
    link.rel = 'preload';
    
    // Determine asset type
    if (asset.match(/\.(jpg|jpeg|png|webp|avif)$/i)) {
      link.as = 'image';
      link.href = getCDNUrl(asset, 'image');
    } else if (asset.match(/\.css$/i)) {
      link.as = 'style';
      link.href = getCDNUrl(asset, 'static');
    } else if (asset.match(/\.js$/i)) {
      link.as = 'script';
      link.href = getCDNUrl(asset, 'static');
    } else if (asset.match(/\.(woff|woff2|ttf|otf)$/i)) {
      link.as = 'font';
      link.href = getCDNUrl(asset, 'static');
      link.crossOrigin = 'anonymous';
    }
    
    document.head.appendChild(link);
  });
}

/**
 * Configure Service Worker for CDN caching
 */
export function configureCDNCaching(): void {
  if ('serviceWorker' in navigator && cdnConfig.enabled) {
    navigator.serviceWorker.register('/sw.js').then(registration => {
      console.log('Service Worker registered for CDN caching');
      
      // Send CDN config to service worker
      if (registration.active) {
        registration.active.postMessage({
          type: 'CDN_CONFIG',
          config: cdnConfig
        });
      }
    });
  }
}

// Export config for use in other modules
export default {
  cdnConfig,
  getCDNUrl,
  getOptimizedImageUrl,
  generateSrcSet,
  preloadAssets,
  configureCDNCaching
};