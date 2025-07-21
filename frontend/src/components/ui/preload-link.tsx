import React from 'react';
import { Link, LinkProps } from 'react-router-dom';
import { lazyWithPreload } from '@/utils/lazyWithPreload';

interface PreloadLinkProps extends LinkProps {
  preload?: () => Promise<void>;
  preloadDelay?: number;
}

/**
 * Link component that preloads the target route on hover
 * 
 * @example
 * <PreloadLink to="/dashboard" preload={Dashboard.preload}>
 *   Dashboard
 * </PreloadLink>
 */
export const PreloadLink: React.FC<PreloadLinkProps> = ({
  preload,
  preloadDelay = 50,
  onMouseEnter,
  onFocus,
  children,
  ...props
}) => {
  const timeoutRef = React.useRef<NodeJS.Timeout>();
  const hasPreloaded = React.useRef(false);

  const handlePreload = React.useCallback(() => {
    if (preload && !hasPreloaded.current) {
      timeoutRef.current = setTimeout(() => {
        hasPreloaded.current = true;
        preload().catch(console.error);
      }, preloadDelay);
    }
  }, [preload, preloadDelay]);

  const handleMouseEnter = React.useCallback(
    (e: React.MouseEvent<HTMLAnchorElement>) => {
      handlePreload();
      onMouseEnter?.(e);
    },
    [handlePreload, onMouseEnter]
  );

  const handleFocus = React.useCallback(
    (e: React.FocusEvent<HTMLAnchorElement>) => {
      handlePreload();
      onFocus?.(e);
    },
    [handlePreload, onFocus]
  );

  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return (
    <Link
      {...props}
      onMouseEnter={handleMouseEnter}
      onFocus={handleFocus}
    >
      {children}
    </Link>
  );
};

/**
 * Navigation item with preload support
 */
interface NavItemProps {
  to: string;
  label: string;
  icon?: React.ReactNode;
  preload?: () => Promise<void>;
  className?: string;
  activeClassName?: string;
  isActive?: boolean;
}

export const NavItem: React.FC<NavItemProps> = ({
  to,
  label,
  icon,
  preload,
  className = '',
  activeClassName = '',
  isActive = false,
}) => {
  return (
    <PreloadLink
      to={to}
      preload={preload}
      className={`
        flex items-center gap-2 px-3 py-2 rounded-lg transition-colors
        hover:bg-purple-500/10 hover:text-white
        ${isActive ? `bg-purple-500/20 text-white ${activeClassName}` : 'text-white/60'}
        ${className}
      `}
    >
      {icon}
      <span>{label}</span>
    </PreloadLink>
  );
};

/**
 * Route map with preload functions
 */
export const routePreloaders = {
  '/dashboard': () => import('@/pages/Dashboard'),
  '/dashboard/progress': () => import('@/pages/ProgressDashboard'),
  '/dashboard/training': () => import('@/pages/TrainingDashboard'),
  '/dashboard/nutrition': () => import('@/pages/NutritionDashboard'),
  '/chat': () => import('@/components/layout/ChatLayout'),
  '/settings': () => import('@/pages/Settings'),
  '/profile': () => import('@/pages/Profile'),
};

/**
 * Auto-preloading link that looks up preload function from route map
 */
export const AutoPreloadLink: React.FC<Omit<PreloadLinkProps, 'preload'>> = ({
  to,
  ...props
}) => {
  const preload = React.useMemo(() => {
    const route = typeof to === 'string' ? to : to.pathname || '';
    const preloader = routePreloaders[route as keyof typeof routePreloaders];
    return preloader ? () => preloader() : undefined;
  }, [to]);

  return <PreloadLink to={to} preload={preload} {...props} />;
};