/**
 * Optimized Image Component with Progressive Loading and WebP Support
 * ==================================================================
 *
 * Features:
 * - Progressive loading with blur-up effect
 * - WebP/AVIF format support with fallbacks
 * - Intersection Observer for lazy loading
 * - Error handling and retry logic
 * - Responsive srcset generation
 * - CDN optimization
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { getCDNUrl, getOptimizedImageUrl, generateSrcSet } from '@/config/cdn';

export interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  sizes?: string;
  quality?: number;
  format?: 'webp' | 'avif' | 'auto';
  placeholder?: 'blur' | 'empty' | string;
  blurDataURL?: string;
  priority?: boolean;
  loading?: 'lazy' | 'eager';
  onLoad?: () => void;
  onError?: () => void;
  fallbackSrc?: string;
  responsive?: boolean;
  objectFit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down';
}

// Generate a simple blur placeholder
function generateBlurPlaceholder(width: number = 10, height: number = 10): string {
  return `data:image/svg+xml;base64,${btoa(`
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f0f0f0"/>
      <circle cx="50%" cy="50%" r="3" fill="#d0d0d0" opacity="0.5"/>
    </svg>
  `)}`;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width,
  height,
  className,
  sizes = '100vw',
  quality = 85,
  format = 'auto',
  placeholder = 'blur',
  blurDataURL,
  priority = false,
  loading = 'lazy',
  onLoad,
  onError,
  fallbackSrc,
  responsive = true,
  objectFit = 'cover',
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(priority);
  const [hasError, setHasError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const imgRef = useRef<HTMLImageElement>(null);
  const intersectionRef = useRef<HTMLDivElement>(null);

  // Generate optimized URLs
  const optimizedSrc = getOptimizedImageUrl(src, {
    width,
    height,
    quality,
    format: format === 'auto' ? 'webp' : format
  });

  const fallbackUrl = format !== 'auto' ? getOptimizedImageUrl(src, { width, height, quality }) : src;

  const srcSet = responsive ? generateSrcSet(src) : undefined;

  const placeholderSrc = placeholder === 'blur'
    ? blurDataURL || generateBlurPlaceholder(width, height)
    : placeholder === 'empty'
    ? 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
    : placeholder;

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (priority || !intersectionRef.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        rootMargin: '50px',
        threshold: 0.1,
      }
    );

    observer.observe(intersectionRef.current);

    return () => observer.disconnect();
  }, [priority]);

  // Handle image load
  const handleLoad = useCallback(() => {
    setIsLoaded(true);
    setHasError(false);
    onLoad?.();
  }, [onLoad]);

  // Handle image error with retry logic
  const handleError = useCallback(() => {
    if (retryCount < 2) {
      setRetryCount(prev => prev + 1);
      // Retry after a delay
      setTimeout(() => {
        if (imgRef.current) {
          imgRef.current.src = imgRef.current.src;
        }
      }, 1000 * Math.pow(2, retryCount));
    } else {
      setHasError(true);
      onError?.();

      // Try fallback source
      if (fallbackSrc && imgRef.current) {
        imgRef.current.src = fallbackSrc;
      }
    }
  }, [retryCount, fallbackSrc, onError]);

  // Progressive image loading hook
  useEffect(() => {
    if (!isInView || !imgRef.current) return;

    const img = imgRef.current;

    // If image is already loaded (from cache), trigger load immediately
    if (img.complete && img.naturalHeight !== 0) {
      handleLoad();
    }
  }, [isInView, handleLoad]);

  // Render error fallback
  if (hasError) {
    return (
      <div
        className={cn(
          'flex items-center justify-center bg-gray-100 text-gray-500',
          className
        )}
        style={{
          width: width || '100%',
          height: height || 'auto',
          aspectRatio: width && height ? `${width}/${height}` : undefined
        }}
      >
        <div className="text-center p-4">
          <svg
            className="w-8 h-8 mx-auto mb-2 opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.232 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
          <p className="text-sm">Failed to load image</p>
          {fallbackSrc && (
            <button
              onClick={() => window.location.reload()}
              className="text-xs underline mt-1"
            >
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div ref={intersectionRef} className="relative overflow-hidden">
      {/* Placeholder/blur image */}
      {placeholder !== 'empty' && !isLoaded && (
        <img
          src={placeholderSrc}
          alt=""
          className={cn(
            'absolute inset-0 w-full h-full transition-opacity duration-300',
            isLoaded ? 'opacity-0' : 'opacity-100',
            objectFit === 'cover' ? 'object-cover' : `object-${objectFit}`,
            placeholder === 'blur' && 'scale-110 blur-sm',
            className
          )}
          style={{
            width: width || '100%',
            height: height || 'auto',
          }}
        />
      )}

      {/* Main image */}
      {isInView && (
        <picture>
          {/* AVIF format for modern browsers */}
          {format === 'auto' && (
            <source
              srcSet={getOptimizedImageUrl(src, { width, height, quality, format: 'avif' })}
              type="image/avif"
              sizes={sizes}
            />
          )}

          {/* WebP format */}
          {(format === 'auto' || format === 'webp') && (
            <source
              srcSet={responsive ? generateSrcSet(src) : optimizedSrc}
              type="image/webp"
              sizes={sizes}
            />
          )}

          {/* Fallback image */}
          <img
            ref={imgRef}
            src={optimizedSrc}
            srcSet={srcSet}
            sizes={sizes}
            alt={alt}
            loading={loading}
            decoding="async"
            onLoad={handleLoad}
            onError={handleError}
            className={cn(
              'transition-opacity duration-300',
              isLoaded ? 'opacity-100' : 'opacity-0',
              objectFit === 'cover' ? 'object-cover' : `object-${objectFit}`,
              className
            )}
            style={{
              width: width || '100%',
              height: height || 'auto',
            }}
          />
        </picture>
      )}
    </div>
  );
};

/**
 * Responsive Image Component with automatic size detection
 */
export interface ResponsiveImageProps extends Omit<OptimizedImageProps, 'width' | 'height' | 'sizes'> {
  aspectRatio?: number;
  breakpoints?: {
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
}

export const ResponsiveImage: React.FC<ResponsiveImageProps> = ({
  aspectRatio = 16 / 9,
  breakpoints = { sm: 640, md: 768, lg: 1024, xl: 1280 },
  sizes,
  ...props
}) => {
  const responsiveSizes = sizes ||
    `(max-width: ${breakpoints.sm}px) 100vw, ` +
    `(max-width: ${breakpoints.md}px) 50vw, ` +
    `(max-width: ${breakpoints.lg}px) 33vw, ` +
    `25vw`;

  return (
    <div
      className="relative w-full"
      style={{ aspectRatio: aspectRatio.toString() }}
    >
      <OptimizedImage
        {...props}
        sizes={responsiveSizes}
        responsive={true}
        className={cn('absolute inset-0 w-full h-full', props.className)}
      />
    </div>
  );
};

/**
 * Gallery Image with zoom and lightbox support
 */
export interface GalleryImageProps extends OptimizedImageProps {
  zoomable?: boolean;
  showLightbox?: boolean;
  onZoom?: () => void;
}

export const GalleryImage: React.FC<GalleryImageProps> = ({
  zoomable = false,
  showLightbox = false,
  onZoom,
  ...props
}) => {
  const [isZoomed, setIsZoomed] = useState(false);

  const handleClick = useCallback(() => {
    if (zoomable) {
      setIsZoomed(prev => !prev);
      onZoom?.();
    }
  }, [zoomable, onZoom]);

  return (
    <div className={cn(
      'relative group',
      zoomable && 'cursor-zoom-in'
    )}>
      <OptimizedImage
        {...props}
        className={cn(
          'transition-transform duration-300',
          isZoomed && 'scale-110',
          zoomable && 'hover:scale-105',
          props.className
        )}
        onClick={handleClick}
      />

      {zoomable && (
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center">
          <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
            </svg>
          </div>
        </div>
      )}
    </div>
  );
};

export default OptimizedImage;
