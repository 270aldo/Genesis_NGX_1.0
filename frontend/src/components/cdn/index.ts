/**
 * CDN Components and Utilities
 * 
 * Export all CDN-related components and utilities for easy importing
 */

// Components
export { 
  CDNImage, 
  CDNAvatar, 
  CDNBackgroundImage, 
  CDNPicture 
} from './CDNImage';

// Configuration and utilities
export { 
  cdnConfig,
  getCDNUrl,
  getOptimizedImageUrl,
  generateSrcSet,
  preloadAssets,
  configureCDNCaching
} from '@/config/cdn';