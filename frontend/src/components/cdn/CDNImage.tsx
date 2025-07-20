import React, { useEffect } from 'react';
import { getOptimizedImageUrl, generateSrcSet, preloadAssets } from '@/config/cdn';

interface CDNImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  quality?: number;
  format?: 'webp' | 'avif' | 'auto';
  sizes?: string;
  loading?: 'lazy' | 'eager';
  priority?: boolean;
  className?: string;
  onLoad?: () => void;
  onError?: () => void;
}

/**
 * CDN-optimized image component with automatic format selection and responsive srcset
 * 
 * @example
 * // Basic usage
 * <CDNImage src="hero-banner.jpg" alt="Hero Banner" />
 * 
 * // With specific dimensions and quality
 * <CDNImage 
 *   src="product.jpg" 
 *   alt="Product" 
 *   width={800} 
 *   height={600} 
 *   quality={90}
 *   format="webp"
 * />
 * 
 * // Responsive with sizes
 * <CDNImage
 *   src="responsive-image.jpg"
 *   alt="Responsive"
 *   sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
 * />
 */
export const CDNImage: React.FC<CDNImageProps> = ({
  src,
  alt,
  width,
  height,
  quality = 85,
  format = 'auto',
  sizes = '100vw',
  loading = 'lazy',
  priority = false,
  className = '',
  onLoad,
  onError,
}) => {
  // Preload high-priority images
  useEffect(() => {
    if (priority) {
      preloadAssets([src]);
    }
  }, [src, priority]);

  // Generate optimized URL
  const optimizedUrl = getOptimizedImageUrl(src, {
    width,
    height,
    quality,
    format,
  });

  // Generate srcset for responsive images
  const srcSet = generateSrcSet(src);

  return (
    <img
      src={optimizedUrl}
      srcSet={srcSet}
      sizes={sizes}
      alt={alt}
      width={width}
      height={height}
      loading={loading}
      className={className}
      onLoad={onLoad}
      onError={onError}
    />
  );
};

// Specialized component for avatar images
export const CDNAvatar: React.FC<{
  src: string;
  alt: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}> = ({ src, alt, size = 'md', className = '' }) => {
  const sizeMap = {
    sm: { width: 32, height: 32 },
    md: { width: 48, height: 48 },
    lg: { width: 64, height: 64 },
    xl: { width: 96, height: 96 },
  };

  const { width, height } = sizeMap[size];

  return (
    <CDNImage
      src={src}
      alt={alt}
      width={width}
      height={height}
      quality={90}
      className={`rounded-full object-cover ${className}`}
      loading="eager"
    />
  );
};

// Background image component with CDN optimization
export const CDNBackgroundImage: React.FC<{
  src: string;
  children: React.ReactNode;
  className?: string;
  overlay?: boolean;
}> = ({ src, children, className = '', overlay = false }) => {
  const optimizedUrl = getOptimizedImageUrl(src, {
    width: 1920,
    quality: 85,
    format: 'webp',
  });

  return (
    <div
      className={`relative bg-cover bg-center ${className}`}
      style={{ backgroundImage: `url(${optimizedUrl})` }}
    >
      {overlay && (
        <div className="absolute inset-0 bg-black/50" />
      )}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
};

// Picture element for art direction
export const CDNPicture: React.FC<{
  sources: Array<{
    media: string;
    src: string;
    format?: 'webp' | 'avif';
  }>;
  fallbackSrc: string;
  alt: string;
  className?: string;
}> = ({ sources, fallbackSrc, alt, className }) => {
  return (
    <picture>
      {sources.map((source, index) => (
        <source
          key={index}
          media={source.media}
          srcSet={generateSrcSet(source.src)}
          type={source.format ? `image/${source.format}` : undefined}
        />
      ))}
      <CDNImage
        src={fallbackSrc}
        alt={alt}
        className={className}
      />
    </picture>
  );
};