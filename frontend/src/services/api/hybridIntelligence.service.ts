/**
 * Hybrid Intelligence Service for NGX Agents
 * Revolutionary 2-layer personalization system
 * Layer 1: Archetype Adaptation (PRIME vs LONGEVITY strategic alignment)
 * Layer 2: Physiological Modulation (real-time bio-data personalization)
 */

import { apiClient, API_ENDPOINTS } from './client';
import { useAuthStore } from '../../store/authStore';

// Core types from backend
export type UserArchetype = 'PRIME' | 'LONGEVITY';
export type PersonalizationMode = 'BASIC' | 'ADVANCED' | 'EXPERT';
export type FitnessLevel = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'ELITE';
export type WorkoutIntensity = 'LOW' | 'MODERATE' | 'HIGH' | 'EXTREME';

// Biometric data structure
export interface UserBiometrics {
  sleep_quality?: number; // 0-1 scale
  sleep_duration?: number; // hours
  stress_level?: number; // 0-1 scale
  energy_level?: number; // 0-1 scale
  recovery_status?: number; // 0-1 scale
  heart_rate_variability?: number; // ms
  resting_heart_rate?: number; // bpm
  readiness_score?: number; // 0-100 scale
}

// Biomarker data for advanced personalization
export interface BiomarkerData {
  testosterone?: number;
  cortisol?: number;
  vitamin_d?: number;
  b12?: number;
  inflammation_markers?: number;
  glucose?: number;
  last_updated?: string;
}

// User constraints and preferences
export interface UserConstraints {
  injuries?: string[];
  medical_conditions?: string[];
  equipment_available?: string[];
  time_constraints?: number; // minutes available
  intensity_preference?: WorkoutIntensity;
  goals?: string[];
}

// Complete user profile for hybrid intelligence
export interface UserProfile {
  user_id: string;
  archetype: UserArchetype;
  fitness_level: FitnessLevel;
  age: number;
  gender: 'male' | 'female' | 'other';
  biometrics: UserBiometrics;
  biomarkers?: BiomarkerData;
  constraints: UserConstraints;
  preferences: {
    communication_style: 'direct' | 'supportive' | 'technical' | 'motivational';
    detail_level: 'minimal' | 'moderate' | 'detailed' | 'comprehensive';
    feedback_frequency: 'real_time' | 'session_end' | 'daily' | 'weekly';
  };
  historical_data?: {
    workout_history?: any[];
    progress_data?: any[];
    adaptation_history?: any[];
  };
}

// Personalization context for requests
export interface PersonalizationContext {
  user_profile: UserProfile;
  agent_type: string;
  request_type: string;
  session_context?: {
    time_of_day?: string;
    location?: string;
    device_type?: string;
    previous_interactions?: any[];
  };
  real_time_data?: {
    current_mood?: number;
    current_energy?: number;
    immediate_goals?: string[];
  };
}

// Personalization result from hybrid intelligence
export interface PersonalizationResult {
  personalized_content: {
    communication_style: string;
    content_adaptation: any;
    intensity_modulation: number;
    timing_optimization: any;
    motivational_framing: string;
  };
  archetype_considerations: {
    strategic_alignment: string;
    preference_matching: string[];
    approach_optimization: string;
  };
  physiological_modulation: {
    bio_data_insights: string[];
    recovery_considerations: string[];
    timing_recommendations: string[];
    intensity_adjustments: any;
  };
  confidence_score: number; // 0-1 scale
  metadata: {
    personalization_mode: PersonalizationMode;
    processing_time_ms: number;
    data_quality_score: number;
    adaptation_reasons: string[];
  };
}

// Learning feedback for continuous improvement
export interface LearningFeedback {
  interaction_id: string;
  user_satisfaction: number; // 0-10 scale
  effectiveness_rating: number; // 0-10 scale
  specific_feedback: {
    communication_quality: number;
    content_relevance: number;
    personalization_accuracy: number;
    goal_alignment: number;
  };
  behavioral_outcomes?: {
    action_taken: boolean;
    goal_progress: number;
    engagement_duration: number;
  };
}

// User insights from hybrid intelligence analysis
export interface UserInsights {
  archetype_analysis: {
    confidence: number;
    primary_traits: string[];
    behavioral_patterns: string[];
    optimization_opportunities: string[];
  };
  physiological_insights: {
    recovery_patterns: string[];
    performance_indicators: string[];
    health_recommendations: string[];
    biomarker_interpretations: string[];
  };
  personalization_recommendations: {
    agent_affinities: Record<string, number>;
    communication_optimizations: string[];
    content_preferences: string[];
    timing_preferences: string[];
  };
  predictive_insights: {
    goal_achievement_probability: number;
    optimal_intervention_timing: string[];
    risk_factors: string[];
    success_factors: string[];
  };
}

/**
 * Hybrid Intelligence Service Class
 * Central service for revolutionary personalization
 */
export class HybridIntelligenceService {
  private static instance: HybridIntelligenceService;
  private profileCache: UserProfile | null = null;
  private insightsCache: UserInsights | null = null;
  private cacheTimestamp: number = 0;
  private CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
  
  private constructor() {}
  
  static getInstance(): HybridIntelligenceService {
    if (!HybridIntelligenceService.instance) {
      HybridIntelligenceService.instance = new HybridIntelligenceService();
    }
    return HybridIntelligenceService.instance;
  }

  /**
   * Get user's hybrid intelligence profile
   */
  async getUserProfile(forceRefresh: boolean = false): Promise<UserProfile> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      const now = Date.now();
      
      // Return cached profile if valid and not forcing refresh
      if (!forceRefresh && this.profileCache && (now - this.cacheTimestamp) < this.CACHE_DURATION) {
        return this.profileCache;
      }

      const response = await apiClient.get<UserProfile>(
        '/api/v1/hybrid-intelligence/profile'
      );
      
      // Update cache
      this.profileCache = response.data;
      this.cacheTimestamp = now;
      
      return response.data;
    } catch (error: any) {
      console.error('Get hybrid intelligence profile error:', error);
      
      // Return cached profile if available on error
      if (this.profileCache) {
        console.warn('Using cached hybrid intelligence profile due to API error');
        return this.profileCache;
      }
      
      throw {
        message: error.response?.data?.message || 'Failed to get hybrid intelligence profile',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Personalize content using hybrid intelligence
   */
  async personalizeForUser(
    context: PersonalizationContext,
    mode: PersonalizationMode = 'ADVANCED'
  ): Promise<PersonalizationResult> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      const response = await apiClient.post<PersonalizationResult>(
        '/api/v1/hybrid-intelligence/personalize',
        {
          context,
          mode,
          timestamp: new Date().toISOString(),
        }
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Hybrid intelligence personalization error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to personalize using hybrid intelligence',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Update biometric data for physiological modulation
   */
  async updateBiometrics(biometrics: UserBiometrics): Promise<void> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      await apiClient.post('/api/v1/hybrid-intelligence/biometrics', {
        biometrics,
        timestamp: new Date().toISOString(),
      });
      
      // Invalidate cache to force refresh on next request
      this.cacheTimestamp = 0;
    } catch (error: any) {
      console.error('Update biometrics error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to update biometrics',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Update biomarker data for advanced personalization
   */
  async updateBiomarkers(biomarkers: BiomarkerData): Promise<void> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      await apiClient.post('/api/v1/hybrid-intelligence/biomarkers', {
        biomarkers,
        timestamp: new Date().toISOString(),
      });
      
      // Invalidate cache to force refresh on next request
      this.cacheTimestamp = 0;
    } catch (error: any) {
      console.error('Update biomarkers error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to update biomarkers',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Provide learning feedback for continuous improvement
   */
  async provideLearningFeedback(feedback: LearningFeedback): Promise<void> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      await apiClient.post('/api/v1/hybrid-intelligence/learning-feedback', {
        ...feedback,
        user_id: user.id,
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      console.error('Learning feedback error:', error);
      // Don't throw error for feedback - it's optional
      console.warn('Failed to provide learning feedback:', error.message);
    }
  }

  /**
   * Get comprehensive user insights
   */
  async getUserInsights(forceRefresh: boolean = false): Promise<UserInsights> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      const now = Date.now();
      
      // Return cached insights if valid and not forcing refresh
      if (!forceRefresh && this.insightsCache && (now - this.cacheTimestamp) < this.CACHE_DURATION) {
        return this.insightsCache;
      }

      const response = await apiClient.get<UserInsights>(
        '/api/v1/hybrid-intelligence/insights'
      );
      
      // Update cache
      this.insightsCache = response.data;
      
      return response.data;
    } catch (error: any) {
      console.error('Get user insights error:', error);
      
      // Return cached insights if available on error
      if (this.insightsCache) {
        console.warn('Using cached user insights due to API error');
        return this.insightsCache;
      }
      
      throw {
        message: error.response?.data?.message || 'Failed to get user insights',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Initialize hybrid intelligence profile
   */
  async initializeProfile(
    archetype: UserArchetype,
    initialData: Partial<UserProfile>
  ): Promise<UserProfile> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      const response = await apiClient.post<UserProfile>(
        '/api/v1/hybrid-intelligence/initialize',
        {
          archetype,
          initial_data: initialData,
          user_id: user.id,
        }
      );
      
      // Update cache with new profile
      this.profileCache = response.data;
      this.cacheTimestamp = Date.now();
      
      return response.data;
    } catch (error: any) {
      console.error('Initialize hybrid intelligence profile error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to initialize hybrid intelligence profile',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Get agent-specific personalization
   */
  async getAgentPersonalization(
    agentId: string,
    requestType: string,
    requestData: any
  ): Promise<PersonalizationResult> {
    try {
      const profile = await this.getUserProfile();
      
      const context: PersonalizationContext = {
        user_profile: profile,
        agent_type: agentId,
        request_type: requestType,
        session_context: {
          time_of_day: new Date().toISOString(),
          device_type: 'web',
        },
        real_time_data: requestData
      };
      
      return await this.personalizeForUser(context, 'ADVANCED');
    } catch (error: any) {
      console.error('Get agent personalization error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to get agent personalization',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Test hybrid intelligence with sample data
   */
  async testPersonalization(
    testArchetype: UserArchetype,
    testBiometrics: UserBiometrics
  ): Promise<PersonalizationResult> {
    try {
      const response = await apiClient.post<PersonalizationResult>(
        '/api/v1/hybrid-intelligence/test',
        {
          archetype: testArchetype,
          biometrics: testBiometrics,
          agent_type: 'blaze',
          request_type: 'workout_plan',
        }
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Test personalization error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to test personalization',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.profileCache = null;
    this.insightsCache = null;
    this.cacheTimestamp = 0;
  }

  /**
   * Get cached profile (for offline support)
   */
  getCachedProfile(): UserProfile | null {
    return this.profileCache;
  }

  /**
   * Get cached insights (for offline support)
   */
  getCachedInsights(): UserInsights | null {
    return this.insightsCache;
  }

  /**
   * Check if user has hybrid intelligence profile
   */
  async hasHybridIntelligenceProfile(): Promise<boolean> {
    try {
      await this.getUserProfile();
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get archetype determination confidence
   */
  async getArchetypeConfidence(): Promise<{
    archetype: UserArchetype;
    confidence: number;
    reasoning: string[];
  }> {
    try {
      const response = await apiClient.get(
        '/api/v1/hybrid-intelligence/archetype-analysis'
      );
      return response.data;
    } catch (error: any) {
      console.error('Get archetype confidence error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to get archetype confidence',
        code: error.response?.status || 500,
      };
    }
  }
}

// Export singleton instance
export const hybridIntelligenceService = HybridIntelligenceService.getInstance();
export default hybridIntelligenceService;