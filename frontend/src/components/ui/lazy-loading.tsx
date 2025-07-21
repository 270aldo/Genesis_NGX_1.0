import React, { Suspense, SuspenseProps, ReactNode } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LazyLoadProps extends Omit<SuspenseProps, 'fallback'> {
  fallback?: ReactNode;
  type?: 'skeleton' | 'spinner' | 'custom';
  height?: string | number;
  className?: string;
  delay?: number;
}

/**
 * Enhanced Suspense wrapper with built-in loading states
 */
export const LazyLoad: React.FC<LazyLoadProps> = ({
  children,
  fallback,
  type = 'skeleton',
  height = 200,
  className,
  delay = 0,
  ...suspenseProps
}) => {
  const [showFallback, setShowFallback] = React.useState(delay === 0);

  React.useEffect(() => {
    if (delay > 0) {
      const timer = setTimeout(() => setShowFallback(true), delay);
      return () => clearTimeout(timer);
    }
  }, [delay]);

  const getFallback = () => {
    if (fallback) return fallback;
    if (!showFallback) return null;

    switch (type) {
      case 'spinner':
        return <SpinnerFallback className={className} />;
      case 'skeleton':
        return <SkeletonFallback height={height} className={className} />;
      default:
        return null;
    }
  };

  return (
    <Suspense fallback={getFallback()} {...suspenseProps}>
      {children}
    </Suspense>
  );
};

/**
 * Skeleton loading fallback
 */
export const SkeletonFallback: React.FC<{
  height?: string | number;
  className?: string;
  count?: number;
}> = ({ height = 200, className, count = 1 }) => {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton
          key={i}
          className={cn('bg-white/5', className)}
          style={{ height: typeof height === 'number' ? `${height}px` : height }}
        />
      ))}
    </div>
  );
};

/**
 * Spinner loading fallback
 */
export const SpinnerFallback: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('flex items-center justify-center py-8', className)}>
      <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
    </div>
  );
};

/**
 * Card skeleton for dashboard components
 */
export const CardSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('rounded-xl border border-purple-500/20 bg-white/5 p-6', className)}>
      <div className="space-y-3">
        <Skeleton className="h-4 w-1/3 bg-white/10" />
        <Skeleton className="h-8 w-2/3 bg-white/10" />
        <div className="space-y-2 pt-4">
          <Skeleton className="h-3 w-full bg-white/10" />
          <Skeleton className="h-3 w-4/5 bg-white/10" />
        </div>
      </div>
    </div>
  );
};

/**
 * Stats card skeleton
 */
export const StatsCardSkeleton: React.FC<{ count?: number }> = ({ count = 4 }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
};

/**
 * List skeleton for activity feeds
 */
export const ListSkeleton: React.FC<{
  count?: number;
  className?: string;
}> = ({ count = 5, className }) => {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-start gap-4 p-4 rounded-lg bg-white/5">
          <Skeleton className="h-10 w-10 rounded-full bg-white/10 flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-1/3 bg-white/10" />
            <Skeleton className="h-3 w-full bg-white/10" />
            <Skeleton className="h-3 w-2/3 bg-white/10" />
          </div>
        </div>
      ))}
    </div>
  );
};

/**
 * Chart skeleton for data visualizations
 */
export const ChartSkeleton: React.FC<{
  height?: number;
  className?: string;
}> = ({ height = 300, className }) => {
  return (
    <div className={cn('rounded-xl border border-purple-500/20 bg-white/5 p-6', className)}>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-6 w-1/3 bg-white/10" />
          <Skeleton className="h-8 w-24 bg-white/10" />
        </div>
        <div className="relative" style={{ height }}>
          <div className="absolute inset-0 flex items-end justify-between gap-2">
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="flex-1 flex flex-col justify-end">
                <Skeleton
                  className="bg-white/10"
                  style={{
                    height: `${Math.random() * 80 + 20}%`,
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Profile skeleton
 */
export const ProfileSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('rounded-xl border border-purple-500/20 bg-white/5 p-6', className)}>
      <div className="flex items-center gap-4">
        <Skeleton className="h-16 w-16 rounded-full bg-white/10" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-5 w-1/3 bg-white/10" />
          <Skeleton className="h-4 w-1/2 bg-white/10" />
        </div>
      </div>
      <div className="mt-6 space-y-3">
        <Skeleton className="h-10 w-full bg-white/10" />
        <Skeleton className="h-10 w-full bg-white/10" />
      </div>
    </div>
  );
};

/**
 * Loading boundary with error handling
 */
export class LazyBoundary extends React.Component<
  {
    children: ReactNode;
    fallback?: ReactNode;
    onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  },
  { hasError: boolean; error?: Error }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Lazy loading error:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-6 text-center">
          <p className="text-red-400 mb-2">Failed to load component</p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="text-sm text-white/60 hover:text-white underline"
          >
            Try again
          </button>
        </div>
      );
    }

    return (
      <Suspense fallback={this.props.fallback || <SpinnerFallback />}>
        {this.props.children}
      </Suspense>
    );
  }
}