import { useState, useEffect, useRef } from 'react';

interface LazyImageOptions {
  threshold?: number;
  rootMargin?: string;
  placeholder?: string;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Custom hook for lazy loading images with intersection observer
 * 
 * @param src - Image source URL
 * @param options - Configuration options
 * @returns Object with image props and loading state
 * 
 * @example
 * const { imgProps, isLoading } = useLazyImage(imageSrc, {
 *   placeholder: '/placeholder.jpg',
 *   threshold: 0.1
 * });
 * 
 * <img {...imgProps} className={isLoading ? 'blur' : ''} />
 */
export function useLazyImage(
  src: string,
  options: LazyImageOptions = {}
) {
  const {
    threshold = 0.1,
    rootMargin = '50px',
    placeholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1" height="1"%3E%3C/svg%3E',
    onLoad,
    onError,
  } = options;

  const [imageSrc, setImageSrc] = useState<string>(placeholder);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const imageElement = imgRef.current;
    if (!imageElement || !src) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          // Preload image
          const img = new Image();
          
          img.onload = () => {
            setImageSrc(src);
            setIsLoading(false);
            onLoad?.();
          };

          img.onerror = () => {
            const error = new Error(`Failed to load image: ${src}`);
            setError(error);
            setIsLoading(false);
            onError?.(error);
          };

          img.src = src;
          observer.disconnect();
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(imageElement);

    return () => {
      observer.disconnect();
    };
  }, [src, threshold, rootMargin, onLoad, onError]);

  return {
    imgProps: {
      ref: imgRef,
      src: imageSrc,
      'data-src': src,
    },
    isLoading,
    error,
  };
}

/**
 * Component for lazy loaded images
 */
export interface LazyImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  placeholder?: string;
  threshold?: number;
  rootMargin?: string;
  blurPlaceholder?: boolean;
}

export const LazyImage: React.FC<LazyImageProps> = ({
  src,
  placeholder,
  threshold,
  rootMargin,
  blurPlaceholder = true,
  className = '',
  alt = '',
  ...props
}) => {
  const { imgProps, isLoading } = useLazyImage(src, {
    placeholder,
    threshold,
    rootMargin,
  });

  return (
    <img
      {...imgProps}
      {...props}
      alt={alt}
      className={`${className} ${
        isLoading && blurPlaceholder ? 'blur-sm animate-pulse' : ''
      } transition-all duration-300`}
      loading="lazy"
    />
  );
};