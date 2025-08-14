/**
 * Lazy-loaded Components for GENESIS Frontend - FASE 6 Performance Optimization
 * =============================================================================
 *
 * This file defines all lazy-loaded components to reduce initial bundle size
 * and improve Time to Interactive (TTI).
 */

import { createLazyComponent } from '../utils/performanceOptimizations';

// ============================================================================
// PAGE-LEVEL COMPONENTS (Route-based code splitting)
// ============================================================================

// Main application pages
export const LazyDashboard = createLazyComponent(
  () => import('../pages/Dashboard'),
  'Dashboard'
);

export const LazyTrainingDashboard = createLazyComponent(
  () => import('../pages/TrainingDashboard'),
  'TrainingDashboard'
);

export const LazyNutritionDashboard = createLazyComponent(
  () => import('../pages/NutritionDashboard'),
  'NutritionDashboard'
);

export const LazyProgressDashboard = createLazyComponent(
  () => import('../pages/ProgressDashboard'),
  'ProgressDashboard'
);

export const LazyProfile = createLazyComponent(
  () => import('../pages/Profile'),
  'Profile'
);

export const LazySettings = createLazyComponent(
  () => import('../pages/Settings'),
  'Settings'
);

export const LazyQuickActions = createLazyComponent(
  () => import('../pages/QuickActions'),
  'QuickActions'
);

// Authentication pages
export const LazySignIn = createLazyComponent(
  () => import('../pages/SignIn'),
  'SignIn'
);

export const LazySignUp = createLazyComponent(
  () => import('../pages/SignUp'),
  'SignUp'
);

export const LazyForgotPassword = createLazyComponent(
  () => import('../pages/ForgotPassword'),
  'ForgotPassword'
);

// Special pages
export const LazyNotFound = createLazyComponent(
  () => import('../pages/NotFound'),
  'NotFound'
);

export const LazyCDNDemo = createLazyComponent(
  () => import('../pages/CDNDemo'),
  'CDNDemo'
);

export const LazyLazyComponentsPage = createLazyComponent(
  () => import('../pages/LazyComponents'),
  'LazyComponents'
);

// ============================================================================
// FEATURE-BASED COMPONENTS (Heavy/complex components)
// ============================================================================

// Charts and data visualization (heavy dependency: recharts)
export const LazyProgressChart = createLazyComponent(
  () => import('../components/charts/ProgressChart').then(module => ({ default: module.ProgressChart })),
  'ProgressChart'
);

export const LazyNutritionChart = createLazyComponent(
  () => import('../components/charts/NutritionChart').then(module => ({ default: module.NutritionChart })),
  'NutritionChart'
);

export const LazyWeightChart = createLazyComponent(
  () => import('../components/charts/WeightChart').then(module => ({ default: module.WeightChart })),
  'WeightChart'
);

// Voice interaction components (heavy: @elevenlabs/react)
export const LazyVoiceInteraction = createLazyComponent(
  () => import('../components/voice/VoiceInteraction').then(module => ({ default: module.VoiceInteraction })),
  'VoiceInteraction'
);

export const LazyVoiceSettings = createLazyComponent(
  () => import('../components/voice/VoiceSettings').then(module => ({ default: module.VoiceSettings })),
  'VoiceSettings'
);

// Advanced form components
export const LazyNutritionForm = createLazyComponent(
  () => import('../components/forms/NutritionForm').then(module => ({ default: module.NutritionForm })),
  'NutritionForm'
);

export const LazyTrainingForm = createLazyComponent(
  () => import('../components/forms/TrainingForm').then(module => ({ default: module.TrainingForm })),
  'TrainingForm'
);

export const LazyProfileForm = createLazyComponent(
  () => import('../components/forms/ProfileForm').then(module => ({ default: module.ProfileForm })),
  'ProfileForm'
);

// Media components
export const LazyImageGallery = createLazyComponent(
  () => import('../components/media/ImageGallery').then(module => ({ default: module.ImageGallery })),
  'ImageGallery'
);

export const LazyVideoPlayer = createLazyComponent(
  () => import('../components/media/VideoPlayer').then(module => ({ default: module.VideoPlayer })),
  'VideoPlayer'
);

// Advanced UI components
export const LazyDataTable = createLazyComponent(
  () => import('../components/ui/DataTable').then(module => ({ default: module.DataTable })),
  'DataTable'
);

export const LazyCalendar = createLazyComponent(
  () => import('../components/ui/Calendar').then(module => ({ default: module.Calendar })),
  'Calendar'
);

export const LazyRichTextEditor = createLazyComponent(
  () => import('../components/ui/RichTextEditor').then(module => ({ default: module.RichTextEditor })),
  'RichTextEditor'
);

// ============================================================================
// MODAL AND OVERLAY COMPONENTS
// ============================================================================

export const LazySettingsModal = createLazyComponent(
  () => import('../components/modals/SettingsModal').then(module => ({ default: module.SettingsModal })),
  'SettingsModal'
);

export const LazyAgentModal = createLazyComponent(
  () => import('../components/modals/AgentModal').then(module => ({ default: module.AgentModal })),
  'AgentModal'
);

export const LazyFeedbackModal = createLazyComponent(
  () => import('../components/modals/FeedbackModal').then(module => ({ default: module.FeedbackModal })),
  'FeedbackModal'
);

export const LazyConfirmDialog = createLazyComponent(
  () => import('../components/dialogs/ConfirmDialog').then(module => ({ default: module.ConfirmDialog })),
  'ConfirmDialog'
);

// ============================================================================
// WEARABLES AND INTEGRATIONS
// ============================================================================

export const LazyWearablesSync = createLazyComponent(
  () => import('../components/wearables/WearablesSync').then(module => ({ default: module.WearablesSync })),
  'WearablesSync'
);

export const LazyWearablesChart = createLazyComponent(
  () => import('../components/wearables/WearablesChart').then(module => ({ default: module.WearablesChart })),
  'WearablesChart'
);

export const LazyHealthMetrics = createLazyComponent(
  () => import('../components/health/HealthMetrics').then(module => ({ default: module.HealthMetrics })),
  'HealthMetrics'
);

// ============================================================================
// DEVELOPER AND ADMIN TOOLS
// ============================================================================

export const LazyPerformanceMonitor = createLazyComponent(
  () => import('../components/dev/PerformanceMonitor').then(module => ({ default: module.PerformanceMonitor })),
  'PerformanceMonitor'
);

export const LazyBundleAnalyzer = createLazyComponent(
  () => import('../components/dev/BundleAnalyzer').then(module => ({ default: module.BundleAnalyzer })),
  'BundleAnalyzer'
);

export const LazyDebugPanel = createLazyComponent(
  () => import('../components/dev/DebugPanel').then(module => ({ default: module.DebugPanel })),
  'DebugPanel'
);

// ============================================================================
// COMPONENT PRELOADING UTILITIES
// ============================================================================

/**
 * Preload critical components based on user behavior patterns
 */
export const preloadCriticalComponents = async () => {
  // Preload components likely to be used first
  const criticalComponents = [
    () => import('../pages/Dashboard'),
    () => import('../components/chat/ChatInterface'),
    () => import('../components/agents/AgentCard')
  ];

  await Promise.allSettled(criticalComponents.map(importFn => importFn()));
};

/**
 * Preload components based on current route
 */
export const preloadRouteComponents = async (currentRoute: string) => {
  const routePreloadMap: Record<string, () => Promise<any>[]> = {
    '/dashboard': [
      () => import('../pages/TrainingDashboard'),
      () => import('../pages/NutritionDashboard')
    ],
    '/training': [
      () => import('../components/charts/ProgressChart'),
      () => import('../components/forms/TrainingForm')
    ],
    '/nutrition': [
      () => import('../components/charts/NutritionChart'),
      () => import('../components/forms/NutritionForm')
    ],
    '/profile': [
      () => import('../components/forms/ProfileForm'),
      () => import('../pages/Settings')
    ]
  };

  const preloadFunctions = routePreloadMap[currentRoute];
  if (preloadFunctions) {
    await Promise.allSettled(preloadFunctions.map(fn => fn()));
  }
};

/**
 * Preload components on user interaction (hover, focus, etc.)
 */
export const setupInteractionPreloading = () => {
  // Set up intersection observer for component preloading
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
        const element = entry.target as HTMLElement;
        const preloadAttribute = element.getAttribute('data-preload');

        if (preloadAttribute) {
          // Preload component based on data attribute
          switch (preloadAttribute) {
            case 'training':
              import('../pages/TrainingDashboard');
              break;
            case 'nutrition':
              import('../pages/NutritionDashboard');
              break;
            case 'progress':
              import('../pages/ProgressDashboard');
              break;
            default:
              break;
          }
        }
      }
    });
  }, {
    rootMargin: '50px',
    threshold: 0.5
  });

  // Observe elements with preload attributes
  document.querySelectorAll('[data-preload]').forEach(el => {
    observer.observe(el);
  });

  return () => observer.disconnect();
};

// ============================================================================
// BUNDLE SPLITTING CONFIGURATION
// ============================================================================

/**
 * Component groups for manual chunk splitting (used in vite.config.ts)
 */
export const COMPONENT_CHUNKS = {
  // Core pages that should be in the main bundle
  CORE: [
    'Dashboard',
    'SignIn',
    'Landing'
  ],

  // Feature-specific chunks
  TRAINING: [
    'TrainingDashboard',
    'TrainingForm',
    'ProgressChart'
  ],

  NUTRITION: [
    'NutritionDashboard',
    'NutritionForm',
    'NutritionChart'
  ],

  PROFILE: [
    'Profile',
    'Settings',
    'ProfileForm'
  ],

  // Heavy dependencies
  CHARTS: [
    'ProgressChart',
    'NutritionChart',
    'WeightChart',
    'WearablesChart'
  ],

  VOICE: [
    'VoiceInteraction',
    'VoiceSettings'
  ],

  // Development tools
  DEV_TOOLS: [
    'PerformanceMonitor',
    'BundleAnalyzer',
    'DebugPanel'
  ]
};

// ============================================================================
// PERFORMANCE TRACKING
// ============================================================================

/**
 * Track lazy component loading performance
 */
export const trackLazyLoadPerformance = (componentName: string, loadTime: number) => {
  if (process.env.NODE_ENV === 'development') {
    console.log(`🚀 Lazy loaded ${componentName} in ${loadTime.toFixed(2)}ms`);

    // Store in performance metrics
    if ('performance' in window && 'mark' in performance) {
      performance.mark(`lazy-load-${componentName}`);
    }
  }
};

export default {
  // Pages
  LazyDashboard,
  LazyTrainingDashboard,
  LazyNutritionDashboard,
  LazyProgressDashboard,
  LazyProfile,
  LazySettings,
  LazyQuickActions,
  LazySignIn,
  LazySignUp,
  LazyForgotPassword,
  LazyNotFound,

  // Components
  LazyProgressChart,
  LazyNutritionChart,
  LazyWeightChart,
  LazyVoiceInteraction,
  LazyVoiceSettings,

  // Utilities
  preloadCriticalComponents,
  preloadRouteComponents,
  setupInteractionPreloading,
  trackLazyLoadPerformance,
  COMPONENT_CHUNKS
};
