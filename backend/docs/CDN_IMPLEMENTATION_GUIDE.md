# CDN Implementation Guide

## Overview

GENESIS uses a comprehensive CDN (Content Delivery Network) strategy to optimize asset delivery and improve performance across the globe. The implementation includes both backend and frontend components working together to provide automatic optimization, caching, and responsive image delivery.

## Architecture

### Backend Components

1. **CDNConfig** (`/backend/core/cdn_config.py`)
   - Manages CDN URLs and cache policies
   - Handles image optimization parameters
   - Provides cache invalidation capabilities
   - Implements edge computing configuration

2. **ImageOptimizer** 
   - Optimizes images for web delivery
   - Supports WebP/AVIF conversion
   - Handles responsive resizing
   - Maintains quality settings per format

3. **CacheManager**
   - Implements cache strategies per content type
   - Manages cache headers
   - Handles user-specific caching rules

### Frontend Components

1. **CDN Configuration** (`/frontend/src/config/cdn.ts`)
   - Environment-based CDN URLs
   - Helper functions for asset URLs
   - Responsive image srcset generation
   - Asset preloading utilities

2. **CDN Components** (`/frontend/src/components/cdn/`)
   - `CDNImage`: Optimized image component
   - `CDNAvatar`: Avatar-specific optimization
   - `CDNBackgroundImage`: Background image handling
   - `CDNPicture`: Art direction support

3. **Service Worker** (`/frontend/public/sw.js`)
   - Offline-first caching strategy
   - Background sync for updates
   - Intelligent cache management

## Usage Examples

### Basic Image Optimization

```tsx
import { CDNImage } from '@/components/cdn';

// Automatic format selection and responsive srcset
<CDNImage 
  src="hero-banner.jpg" 
  alt="Hero Banner"
  width={1200}
  height={600}
  quality={90}
/>
```

### Avatar Components

```tsx
import { CDNAvatar } from '@/components/cdn';

// Pre-configured sizes with automatic optimization
<CDNAvatar 
  src="user-profile.jpg" 
  alt="User" 
  size="lg" 
/>
```

### Background Images

```tsx
import { CDNBackgroundImage } from '@/components/cdn';

// Optimized background with overlay support
<CDNBackgroundImage 
  src="hero-bg.jpg" 
  overlay
>
  <h1>Content over optimized background</h1>
</CDNBackgroundImage>
```

### Art Direction

```tsx
import { CDNPicture } from '@/components/cdn';

// Different images for different breakpoints
<CDNPicture
  sources={[
    { media: '(max-width: 640px)', src: 'mobile.jpg' },
    { media: '(max-width: 1024px)', src: 'tablet.jpg' }
  ]}
  fallbackSrc="desktop.jpg"
  alt="Responsive image"
/>
```

### Preloading Critical Assets

```tsx
import { preloadAssets } from '@/config/cdn';

// Preload critical assets on page load
useEffect(() => {
  preloadAssets([
    'logo.png',
    'hero-background.jpg',
    'fonts/inter-var.woff2'
  ]);
}, []);
```

## Configuration

### Environment Variables

```env
# Backend CDN Configuration
CDN_ENABLED=true
CDN_URL=https://cdn.ngx-agents.com
ORIGIN_URL=https://api.ngx-agents.com
COMPRESSION_ENABLED=true

# Frontend CDN URLs (vite.config.ts)
VITE_CDN_BASE_URL=https://cdn.ngx-agents.com
VITE_CDN_IMAGE_URL=https://cdn.ngx-agents.com/images
VITE_CDN_STATIC_URL=https://cdn.ngx-agents.com/static
```

### Cache Policies

The system implements different cache strategies based on content type:

1. **Static Assets** (JS, CSS, fonts)
   - Max age: 1 year
   - Immutable caching for versioned assets
   - Public caching allowed

2. **Images**
   - Max age: 30 days
   - Vary by Accept header for format negotiation
   - Stale-while-revalidate for performance

3. **API Responses**
   - Max age: 5 minutes
   - Private caching only
   - Vary by Authorization header

4. **Real-time Data**
   - No caching
   - No-store directive

## Image Optimization

### Automatic Format Selection

The system automatically serves the best image format based on browser support:

1. **AVIF**: For modern browsers (best compression)
2. **WebP**: For broad browser support
3. **JPEG/PNG**: Fallback for older browsers

### Responsive Images

All images automatically generate srcset with multiple resolutions:
- 640w, 750w, 828w, 1080w, 1200w, 1920w

### Quality Settings

Default quality settings per format:
- AVIF: 80
- WebP: 85
- JPEG: 85
- PNG: Lossless with max compression

## Performance Benefits

1. **Reduced Latency**: Global edge locations
2. **Bandwidth Savings**: 60-80% with modern formats
3. **Improved LCP**: Preloading and priority hints
4. **Offline Support**: Service Worker caching
5. **Automatic Optimization**: No manual intervention needed

## Monitoring

### Metrics to Track

1. **Cache Hit Rate**: Target > 90%
2. **Bandwidth Savings**: Monitor compression ratios
3. **Image Load Times**: Track p75 and p95
4. **Format Distribution**: WebP/AVIF adoption

### Cache Invalidation

```python
from core.cdn_config import cdn_config

# Invalidate specific paths
result = cdn_config.invalidate_cache([
    '/images/hero-banner.jpg',
    '/static/app.*.js'
])
```

## Best Practices

1. **Always use CDN components** instead of native img tags
2. **Specify dimensions** to prevent layout shift
3. **Use appropriate loading strategies** (lazy vs eager)
4. **Preload critical images** above the fold
5. **Monitor cache performance** regularly
6. **Version static assets** for cache busting

## Troubleshooting

### Images not loading from CDN

1. Check CDN_ENABLED environment variable
2. Verify CDN URLs are correctly configured
3. Check browser console for CORS errors
4. Ensure Service Worker is registered

### Poor cache hit rates

1. Review cache headers configuration
2. Check for unnecessary cache busting
3. Verify CDN edge locations
4. Monitor origin server load

### Format negotiation issues

1. Verify Accept headers are being sent
2. Check image optimization service
3. Review fallback format availability
4. Test across different browsers

## Future Enhancements

1. **AI-powered optimization**: Smart cropping and quality adjustment
2. **Blurhash placeholders**: Better perceived performance
3. **AVIF support expansion**: Broader device coverage
4. **Edge computing**: Real-time image transformations
5. **WebP2 preparation**: Next-gen format readiness