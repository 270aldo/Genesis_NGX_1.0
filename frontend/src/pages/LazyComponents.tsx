/**
 * Centralized lazy loading configuration for heavy components
 * 
 * This file exports lazy loaded versions of heavy components
 * to improve initial bundle size and performance
 */

import { lazyWithPreload, lazyWithRetry } from '@/utils/lazyWithPreload';

// Hybrid Intelligence Components (Large components)
export const HybridIntelligenceDashboard = lazyWithPreload(
  () => import('@/components/hybridIntelligence/HybridIntelligenceDashboard')
);

export const ArchetypeAssessment = lazyWithPreload(
  () => import('@/components/hybridIntelligence/ArchetypeAssessment')
);

export const BiometricDataInput = lazyWithPreload(
  () => import('@/components/hybridIntelligence/BiometricDataInput')
);

export const LearningFeedbackSystem = lazyWithPreload(
  () => import('@/components/feedback/LearningFeedbackSystem')
);

// Chat Components
export const PersonalizedChatInterface = lazyWithPreload(
  () => import('@/components/chat/PersonalizedChatInterface')
);

// Progress Components with retry (critical for user experience)
export const ProgressDashboard = lazyWithRetry(
  () => import('@/pages/ProgressDashboard'),
  3,
  1000
);

export const DetailedProgress = lazyWithRetry(
  () => import('@/pages/DetailedProgress'),
  3,
  1000
);

// Chart Components (Heavy visualization libraries)
export const BiometricsCharts = lazyWithPreload(
  () => import('@/components/charts/BiometricsCharts')
);

export const ProgressCharts = lazyWithPreload(
  () => import('@/components/charts/ProgressCharts')
);

// Export Components
export const ExportOptions = lazyWithPreload(
  () => import('@/components/export/ExportOptions')
);

export const PDFExport = lazyWithPreload(
  () => import('@/components/export/PDFExport')
);

// Voice Components
export const VoiceInterface = lazyWithPreload(
  () => import('@/components/voice/VoiceInterface')
);

export const VoiceEnergyBall = lazyWithPreload(
  () => import('@/components/voice/VoiceEnergyBall').then(module => ({ 
    default: module.VoiceEnergyBall 
  }))
);

// Settings Components
export const AdvancedSettings = lazyWithPreload(
  () => import('@/components/settings/AdvancedSettings')
);

export const IntegrationSettings = lazyWithPreload(
  () => import('@/components/settings/IntegrationSettings')
);

// Preload critical components when idle
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    // Preload components likely to be used soon
    PersonalizedChatInterface.preload();
    ProgressDashboard.preload();
  });
}

// Export preload functions for route-based preloading
export const preloadDashboardComponents = () => {
  return Promise.all([
    HybridIntelligenceDashboard.preload(),
    ProgressCharts.preload(),
  ]);
};

export const preloadChatComponents = () => {
  return Promise.all([
    PersonalizedChatInterface.preload(),
    VoiceInterface.preload(),
  ]);
};

export const preloadProgressComponents = () => {
  return Promise.all([
    ProgressDashboard.preload(),
    DetailedProgress.preload(),
    BiometricsCharts.preload(),
    ProgressCharts.preload(),
  ]);
};