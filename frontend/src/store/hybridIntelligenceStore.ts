/**
 * Hybrid Intelligence Store
 * Global state management for revolutionary 2-layer personalization system
 * Layer 1: Archetype Adaptation (PRIME vs LONGEVITY strategic alignment)
 * Layer 2: Physiological Modulation (real-time bio-data personalization)
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { 
  hybridIntelligenceService,
  type UserProfile,
  type UserInsights,
  type PersonalizationResult,
  type UserArchetype,
  type PersonalizationMode,
  type UserBiometrics,
  type BiomarkerData,
  type LearningFeedback
} from '../services/api/hybridIntelligence.service';

export interface HybridIntelligenceState {
  // Core profile data
  profile: UserProfile | null;
  insights: UserInsights | null;
  
  // State management
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;
  
  // Personalization tracking
  recentPersonalizations: PersonalizationResult[];
  learningFeedback: LearningFeedback[];
  adaptationHistory: Array<{
    timestamp: string;
    agentId: string;
    adaptationType: string;
    confidence: number;
    effectiveness?: number;
  }>;
  
  // Real-time data
  currentBiometrics: UserBiometrics | null;
  biomarkers: BiomarkerData | null;
  lastDataUpdate: string | null;
  
  // Quick access computed properties
  archetype: UserArchetype | null;
  personalizationMode: PersonalizationMode;
  confidenceScore: number;
  adaptationCount: number;
  
  // Actions - Profile Management
  initializeProfile: (archetype: UserArchetype, initialData: Partial<UserProfile>) => Promise<void>;
  loadProfile: (forceRefresh?: boolean) => Promise<void>;
  updateBiometrics: (biometrics: UserBiometrics) => Promise<void>;
  updateBiomarkers: (biomarkers: BiomarkerData) => Promise<void>;
  
  // Actions - Personalization
  personalizeForAgent: (agentId: string, requestType: string, requestData: any) => Promise<PersonalizationResult>;
  trackPersonalization: (result: PersonalizationResult) => void;
  provideFeedback: (feedback: LearningFeedback) => Promise<void>;
  
  // Actions - Insights & Analysis
  loadInsights: (forceRefresh?: boolean) => Promise<void>;
  getAgentAffinity: (agentId: string) => number;
  getPersonalizedGreeting: () => string;
  getOptimalTiming: () => string[];
  
  // Actions - Utilities
  clearError: () => void;
  resetProfile: () => void;
  clearCache: () => void;
  
  // Computed helpers
  isArchetypeConfident: () => boolean;
  getBioDataQuality: () => number;
  getPersonalizationEffectiveness: () => number;
  getRecommendedAgents: () => string[];
}

export const useHybridIntelligenceStore = create<HybridIntelligenceState>()(
  persist(
    (set, get) => ({
      // Initial state
      profile: null,
      insights: null,
      isLoading: false,
      isInitialized: false,
      error: null,
      recentPersonalizations: [],
      learningFeedback: [],
      adaptationHistory: [],
      currentBiometrics: null,
      biomarkers: null,
      lastDataUpdate: null,
      archetype: null,
      personalizationMode: 'ADVANCED',
      confidenceScore: 0,
      adaptationCount: 0,

      // Initialize hybrid intelligence profile
      initializeProfile: async (archetype: UserArchetype, initialData: Partial<UserProfile>) => {
        set({ isLoading: true, error: null });
        
        try {
          const profile = await hybridIntelligenceService.initializeProfile(archetype, initialData);
          
          set({
            profile,
            archetype: profile.archetype,
            confidenceScore: profile.metadata?.confidenceScore || 0,
            isInitialized: true,
            isLoading: false
          });
          
          // Load insights after profile initialization
          await get().loadInsights();
        } catch (error: any) {
          console.error('Failed to initialize hybrid intelligence profile:', error);
          set({
            error: error.message || 'Failed to initialize profile',
            isLoading: false
          });
        }
      },

      // Load existing profile
      loadProfile: async (forceRefresh = false) => {
        set({ isLoading: true, error: null });
        
        try {
          const profile = await hybridIntelligenceService.getUserProfile(forceRefresh);
          
          set({
            profile,
            archetype: profile.archetype,
            confidenceScore: profile.metadata?.confidenceScore || 0,
            currentBiometrics: profile.biometrics,
            biomarkers: profile.biomarkers,
            adaptationCount: profile.historical_data?.adaptation_history?.length || 0,
            isInitialized: true,
            isLoading: false
          });
        } catch (error: any) {
          console.error('Failed to load hybrid intelligence profile:', error);
          set({
            error: error.message || 'Failed to load profile',
            isLoading: false,
            isInitialized: false
          });
        }
      },

      // Update biometric data
      updateBiometrics: async (biometrics: UserBiometrics) => {
        try {
          await hybridIntelligenceService.updateBiometrics(biometrics);
          
          set({
            currentBiometrics: biometrics,
            lastDataUpdate: new Date().toISOString()
          });
          
          // Update profile if it exists
          const currentProfile = get().profile;
          if (currentProfile) {
            set({
              profile: {
                ...currentProfile,
                biometrics: { ...currentProfile.biometrics, ...biometrics }
              }
            });
          }
        } catch (error: any) {
          console.error('Failed to update biometrics:', error);
          set({ error: error.message || 'Failed to update biometrics' });
        }
      },

      // Update biomarker data
      updateBiomarkers: async (biomarkers: BiomarkerData) => {
        try {
          await hybridIntelligenceService.updateBiomarkers(biomarkers);
          
          set({
            biomarkers,
            lastDataUpdate: new Date().toISOString()
          });
          
          // Update profile if it exists
          const currentProfile = get().profile;
          if (currentProfile) {
            set({
              profile: {
                ...currentProfile,
                biomarkers: { ...currentProfile.biomarkers, ...biomarkers }
              }
            });
          }
        } catch (error: any) {
          console.error('Failed to update biomarkers:', error);
          set({ error: error.message || 'Failed to update biomarkers' });
        }
      },

      // Personalize for specific agent
      personalizeForAgent: async (agentId: string, requestType: string, requestData: any) => {
        try {
          const result = await hybridIntelligenceService.getAgentPersonalization(
            agentId,
            requestType,
            requestData
          );
          
          // Track the personalization
          get().trackPersonalization(result);
          
          return result;
        } catch (error: any) {
          console.error('Failed to personalize for agent:', error);
          throw error;
        }
      },

      // Track personalization result
      trackPersonalization: (result: PersonalizationResult) => {
        set(state => ({
          recentPersonalizations: [result, ...state.recentPersonalizations.slice(0, 9)], // Keep last 10
          adaptationHistory: [
            {
              timestamp: new Date().toISOString(),
              agentId: result.metadata?.agentId || 'unknown',
              adaptationType: result.archetype_considerations.strategic_alignment,
              confidence: result.confidence_score
            },
            ...state.adaptationHistory.slice(0, 19) // Keep last 20
          ]
        }));
      },

      // Provide learning feedback
      provideFeedback: async (feedback: LearningFeedback) => {
        try {
          await hybridIntelligenceService.provideLearningFeedback(feedback);
          
          set(state => ({
            learningFeedback: [feedback, ...state.learningFeedback.slice(0, 19)] // Keep last 20
          }));
          
          // Update adaptation history with effectiveness
          const adaptationIndex = get().adaptationHistory.findIndex(
            adaptation => adaptation.timestamp.startsWith(feedback.interaction_id.split('_')[1])
          );
          
          if (adaptationIndex >= 0) {
            set(state => ({
              adaptationHistory: state.adaptationHistory.map((adaptation, index) => 
                index === adaptationIndex 
                  ? { ...adaptation, effectiveness: feedback.effectiveness_rating }
                  : adaptation
              )
            }));
          }
        } catch (error: any) {
          console.error('Failed to provide learning feedback:', error);
          // Don't throw error for feedback - it's optional
        }
      },

      // Load insights
      loadInsights: async (forceRefresh = false) => {
        try {
          const insights = await hybridIntelligenceService.getUserInsights(forceRefresh);
          set({ insights });
        } catch (error: any) {
          console.error('Failed to load insights:', error);
          // Don't set error state for insights - they're supplementary
        }
      },

      // Get agent affinity score
      getAgentAffinity: (agentId: string) => {
        const { insights, profile } = get();
        
        if (!insights || !profile) return 0.5; // Default neutral score
        
        // Get from insights if available
        const affinityScore = insights.personalization_recommendations.agent_affinities[agentId];
        if (affinityScore !== undefined) return affinityScore;
        
        // Calculate based on archetype and agent characteristics
        const { archetype } = profile;
        let score = 0.5;
        
        switch (agentId.toLowerCase()) {
          case 'blaze':
            score += archetype === 'PRIME' ? 0.3 : -0.1;
            break;
          case 'sage':
            score += archetype === 'LONGEVITY' ? 0.3 : 0.1;
            break;
          case 'nova':
            score += archetype === 'PRIME' ? 0.25 : -0.15;
            break;
          case 'wave':
            score += archetype === 'LONGEVITY' ? 0.2 : 0.1;
            break;
          case 'luna':
            score += profile.gender === 'female' ? 0.2 : 0;
            break;
          default:
            break;
        }
        
        return Math.max(0, Math.min(1, score));
      },

      // Get personalized greeting
      getPersonalizedGreeting: () => {
        const { profile, archetype } = get();
        if (!profile) return "¡Hola! ¿Cómo puedo ayudarte hoy?";
        
        const hour = new Date().getHours();
        const timeGreeting = hour < 12 ? "Buenos días" : hour < 18 ? "Buenas tardes" : "Buenas noches";
        
        const communicationStyle = profile.preferences.communication_style;
        
        switch (communicationStyle) {
          case 'direct':
            return `${timeGreeting}. ¿En qué nos enfocamos hoy?`;
          case 'supportive':
            return `${timeGreeting}! Espero que te sientas genial. ¿Cómo podemos optimizar tu día?`;
          case 'technical':
            return `${timeGreeting}. Analicemos tus datos y planifiquemos los próximos pasos.`;
          case 'motivational':
            return archetype === 'PRIME' 
              ? `${timeGreeting}, campeón! ¿Listo para romper límites hoy?`
              : `${timeGreeting}! Construyamos hábitos poderosos para tu bienestar.`;
          default:
            return archetype === 'PRIME' 
              ? `${timeGreeting}! ¿Listo para la acción?`
              : `${timeGreeting}. Cuidemos tu bienestar hoy.`;
        }
      },

      // Get optimal timing recommendations
      getOptimalTiming: () => {
        const { profile, currentBiometrics } = get();
        if (!profile || !currentBiometrics) return ['Mantén tu rutina habitual'];
        
        const recommendations: string[] = [];
        const hour = new Date().getHours();
        
        // Based on energy level
        if (currentBiometrics.energy_level && currentBiometrics.energy_level > 0.7) {
          recommendations.push('Perfecto momento para entrenamientos intensos');
        } else if (currentBiometrics.energy_level && currentBiometrics.energy_level < 0.4) {
          recommendations.push('Considera actividades de recuperación');
        }
        
        // Based on sleep quality
        if (currentBiometrics.sleep_quality && currentBiometrics.sleep_quality < 0.6) {
          recommendations.push('Prioriza descanso y recuperación hoy');
        }
        
        // Based on stress level
        if (currentBiometrics.stress_level && currentBiometrics.stress_level > 0.7) {
          recommendations.push('Incluye técnicas de manejo de estrés');
        }
        
        // Time-based recommendations
        if (hour >= 6 && hour <= 10) {
          recommendations.push('Ventana óptima para entrenamientos matutinos');
        } else if (hour >= 17 && hour <= 19) {
          recommendations.push('Buen momento para actividad física vespertina');
        }
        
        return recommendations.length > 0 ? recommendations : ['Mantén tu rutina habitual'];
      },

      // Clear error
      clearError: () => {
        set({ error: null });
      },

      // Reset profile
      resetProfile: () => {
        set({
          profile: null,
          insights: null,
          archetype: null,
          confidenceScore: 0,
          adaptationCount: 0,
          currentBiometrics: null,
          biomarkers: null,
          lastDataUpdate: null,
          isInitialized: false,
          recentPersonalizations: [],
          learningFeedback: [],
          adaptationHistory: []
        });
      },

      // Clear cache
      clearCache: () => {
        hybridIntelligenceService.clearCache();
      },

      // Computed helpers
      isArchetypeConfident: () => {
        const { confidenceScore } = get();
        return confidenceScore >= 0.7;
      },

      getBioDataQuality: () => {
        const { currentBiometrics, biomarkers } = get();
        let quality = 0;
        let factors = 0;
        
        if (currentBiometrics) {
          factors += 1;
          const biometricFields = Object.values(currentBiometrics).filter(v => v !== undefined).length;
          quality += biometricFields / 8; // 8 possible biometric fields
        }
        
        if (biomarkers) {
          factors += 1;
          const biomarkerFields = Object.values(biomarkers).filter(v => v !== undefined).length;
          quality += biomarkerFields / 7; // 7 possible biomarker fields
        }
        
        return factors > 0 ? quality / factors : 0;
      },

      getPersonalizationEffectiveness: () => {
        const { learningFeedback } = get();
        if (learningFeedback.length === 0) return 0;
        
        const avgEffectiveness = learningFeedback.reduce((sum, feedback) => 
          sum + feedback.effectiveness_rating, 0) / learningFeedback.length;
        
        return avgEffectiveness / 10; // Convert to 0-1 scale
      },

      getRecommendedAgents: () => {
        const { insights } = get();
        if (!insights) return [];
        
        return Object.entries(insights.personalization_recommendations.agent_affinities)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 3)
          .map(([agentId]) => agentId);
      }
    }),
    {
      name: 'ngx-agents-hybrid-intelligence',
      partialize: (state) => ({
        profile: state.profile,
        archetype: state.archetype,
        confidenceScore: state.confidenceScore,
        adaptationCount: state.adaptationCount,
        currentBiometrics: state.currentBiometrics,
        biomarkers: state.biomarkers,
        lastDataUpdate: state.lastDataUpdate,
        personalizationMode: state.personalizationMode,
        recentPersonalizations: state.recentPersonalizations.slice(0, 5), // Persist only last 5
        adaptationHistory: state.adaptationHistory.slice(0, 10), // Persist only last 10
        isInitialized: state.isInitialized
      }),
    }
  )
);