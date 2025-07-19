/**
 * Hybrid Intelligence Personalization Hook
 * Real-time personalization hook for agent interactions
 * Integrates 2-layer personalization system with agent communication
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useHybridIntelligenceStore } from '@/store/hybridIntelligenceStore';
import { type PersonalizationResult, type LearningFeedback } from '@/services/api/hybridIntelligence.service';

export interface PersonalizationOptions {
  agentId: string;
  requestType: 'workout_recommendation' | 'nutrition_advice' | 'recovery_plan' | 'motivation' | 'general_chat';
  context?: {
    timeOfDay?: string;
    userMood?: string;
    availableTime?: number;
    currentGoal?: string;
    previousInteractions?: string[];
  };
  priority?: 'low' | 'medium' | 'high';
}

export interface PersonalizationState {
  isPersonalizing: boolean;
  result: PersonalizationResult | null;
  error: string | null;
  confidenceScore: number;
  recommendations: string[];
  isOptimalTime: boolean;
  agentAffinity: number;
}

export interface PersonalizationActions {
  personalizeContent: (options: PersonalizationOptions) => Promise<PersonalizationResult | null>;
  provideFeedback: (feedback: Omit<LearningFeedback, 'timestamp'>) => Promise<void>;
  resetPersonalization: () => void;
  getPersonalizedGreeting: (agentId: string) => string;
  getOptimalInteractionTiming: () => string[];
  checkAgentCompatibility: (agentId: string) => { compatible: boolean; reason?: string };
}

export const useHybridIntelligencePersonalization = (): PersonalizationState & PersonalizationActions => {
  const {
    profile,
    archetype,
    currentBiometrics,
    personalizeForAgent,
    provideFeedback: storeFeedback,
    getAgentAffinity,
    getPersonalizedGreeting,
    getOptimalTiming,
    isArchetypeConfident,
  } = useHybridIntelligenceStore();

  const [personalizationState, setPersonalizationState] = useState<PersonalizationState>({
    isPersonalizing: false,
    result: null,
    error: null,
    confidenceScore: 0,
    recommendations: [],
    isOptimalTime: false,
    agentAffinity: 0,
  });

  // Check if current time is optimal for interactions
  const isOptimalTime = useMemo(() => {
    const optimalTimes = getOptimalTiming();
    const currentHour = new Date().getHours();
    
    return optimalTimes.some(timeRange => {
      if (timeRange.includes(':')) {
        const [start, end] = timeRange.split('-').map(time => parseInt(time.split(':')[0]));
        return currentHour >= start && currentHour <= end;
      }
      return false;
    });
  }, [getOptimalTiming]);

  // Update state when profile changes
  useEffect(() => {
    setPersonalizationState(prev => ({
      ...prev,
      confidenceScore: profile?.metadata?.confidenceScore || 0,
      isOptimalTime,
    }));
  }, [profile, isOptimalTime]);

  // Personalize content for agent interaction
  const personalizeContent = useCallback(async (options: PersonalizationOptions): Promise<PersonalizationResult | null> => {
    if (!profile || !archetype) {
      setPersonalizationState(prev => ({
        ...prev,
        error: 'Profile not initialized. Please complete archetype assessment first.',
      }));
      return null;
    }

    setPersonalizationState(prev => ({
      ...prev,
      isPersonalizing: true,
      error: null,
    }));

    try {
      // Prepare request data with context
      const requestData = {
        ...options.context,
        archetype,
        currentBiometrics,
        userPreferences: profile.preferences,
        fitnessLevel: profile.fitness_level,
        age: profile.age,
        gender: profile.gender,
        constraints: profile.constraints,
        timestamp: new Date().toISOString(),
        priority: options.priority || 'medium',
      };

      // Get personalization from service
      const result = await personalizeForAgent(options.agentId, options.requestType, requestData);
      
      // Calculate agent affinity
      const agentAffinity = getAgentAffinity(options.agentId);
      
      // Generate recommendations based on result
      const recommendations = generateRecommendations(result, options.agentId);

      setPersonalizationState(prev => ({
        ...prev,
        result,
        agentAffinity,
        recommendations,
        confidenceScore: result.confidence_score,
        isPersonalizing: false,
      }));

      return result;
    } catch (error: any) {
      console.error('Personalization failed:', error);
      setPersonalizationState(prev => ({
        ...prev,
        error: error.message || 'Failed to personalize content',
        isPersonalizing: false,
      }));
      return null;
    }
  }, [profile, archetype, currentBiometrics, personalizeForAgent, getAgentAffinity]);

  // Provide feedback on personalization effectiveness
  const provideFeedback = useCallback(async (feedback: Omit<LearningFeedback, 'timestamp'>) => {
    try {
      const feedbackWithTimestamp: LearningFeedback = {
        ...feedback,
        timestamp: new Date().toISOString(),
      };
      
      await storeFeedback(feedbackWithTimestamp);
      
      // Update local state to reflect feedback
      setPersonalizationState(prev => ({
        ...prev,
        error: null,
      }));
    } catch (error: any) {
      console.error('Failed to provide feedback:', error);
      setPersonalizationState(prev => ({
        ...prev,
        error: error.message || 'Failed to provide feedback',
      }));
    }
  }, [storeFeedback]);

  // Reset personalization state
  const resetPersonalization = useCallback(() => {
    setPersonalizationState({
      isPersonalizing: false,
      result: null,
      error: null,
      confidenceScore: profile?.metadata?.confidenceScore || 0,
      recommendations: [],
      isOptimalTime,
      agentAffinity: 0,
    });
  }, [profile, isOptimalTime]);

  // Get personalized greeting for specific agent
  const getPersonalizedAgentGreeting = useCallback((agentId: string) => {
    if (!profile) return `¡Hola! Soy ${agentId.toUpperCase()}, ¿cómo puedo ayudarte?`;
    
    const baseGreeting = getPersonalizedGreeting();
    const agentPersonality = getAgentPersonality(agentId);
    
    return `${baseGreeting} ${agentPersonality}`;
  }, [profile, getPersonalizedGreeting]);

  // Get optimal interaction timing
  const getOptimalInteractionTiming = useCallback(() => {
    if (!profile || !currentBiometrics) return [];
    
    const timings = getOptimalTiming();
    const additionalRecommendations = [];
    
    // Add biometric-based recommendations
    if (currentBiometrics.energy_level && currentBiometrics.energy_level > 0.8) {
      additionalRecommendations.push('Energía alta - ideal para entrenamientos intensos');
    }
    
    if (currentBiometrics.stress_level && currentBiometrics.stress_level > 0.7) {
      additionalRecommendations.push('Estrés elevado - considera técnicas de relajación');
    }
    
    return [...timings, ...additionalRecommendations];
  }, [getOptimalTiming, currentBiometrics]);

  // Check agent compatibility
  const checkAgentCompatibility = useCallback((agentId: string) => {
    if (!profile || !archetype) {
      return { compatible: false, reason: 'Profile not initialized' };
    }
    
    const affinity = getAgentAffinity(agentId);
    const confidence = isArchetypeConfident();
    
    if (affinity < 0.3) {
      return { 
        compatible: false, 
        reason: `${agentId.toUpperCase()} tiene baja afinidad con tu arquetipo ${archetype}` 
      };
    }
    
    if (!confidence) {
      return { 
        compatible: true, 
        reason: 'Compatibilidad moderada - completa más datos para mejor personalización' 
      };
    }
    
    return { compatible: true };
  }, [profile, archetype, getAgentAffinity, isArchetypeConfident]);

  return {
    ...personalizationState,
    personalizeContent,
    provideFeedback,
    resetPersonalization,
    getPersonalizedGreeting: getPersonalizedAgentGreeting,
    getOptimalInteractionTiming,
    checkAgentCompatibility,
  };
};

// Helper functions

function generateRecommendations(result: PersonalizationResult, agentId: string): string[] {
  const recommendations: string[] = [];
  
  // Based on archetype considerations
  const { strategic_alignment, communication_style, intensity_preference } = result.archetype_considerations;
  
  if (strategic_alignment === 'performance_optimization') {
    recommendations.push('Enfócate en métricas de rendimiento y objetivos específicos');
  } else if (strategic_alignment === 'longevity_focus') {
    recommendations.push('Prioriza hábitos sostenibles y bienestar a largo plazo');
  }
  
  if (communication_style === 'direct') {
    recommendations.push('Usa comunicación directa y concisa');
  } else if (communication_style === 'supportive') {
    recommendations.push('Mantén un tono de apoyo y motivación');
  }
  
  if (intensity_preference === 'high') {
    recommendations.push('Sugiere entrenamientos de alta intensidad');
  } else if (intensity_preference === 'moderate') {
    recommendations.push('Recomienda actividades de intensidad moderada');
  }
  
  // Based on physiological modulations
  const { energy_level_factor, recovery_status_factor, stress_level_factor } = result.physiological_modulations;
  
  if (energy_level_factor > 0.8) {
    recommendations.push('Aprovecha los altos niveles de energía');
  } else if (energy_level_factor < 0.4) {
    recommendations.push('Considera actividades de baja intensidad');
  }
  
  if (recovery_status_factor < 0.5) {
    recommendations.push('Prioriza recuperación y descanso');
  }
  
  if (stress_level_factor > 0.7) {
    recommendations.push('Incluye técnicas de manejo de estrés');
  }
  
  // Agent-specific recommendations
  switch (agentId.toLowerCase()) {
    case 'blaze':
      recommendations.push('Enfócate en entrenamientos de fuerza y potencia');
      break;
    case 'nova':
      recommendations.push('Optimiza entrenamientos cardio y resistencia');
      break;
    case 'sage':
      recommendations.push('Integra sabiduría ancestral con ciencia moderna');
      break;
    case 'wave':
      recommendations.push('Incorpora movimientos fluidos y flexibilidad');
      break;
    case 'luna':
      recommendations.push('Considera aspectos hormonales y ciclos naturales');
      break;
  }
  
  return recommendations;
}

function getAgentPersonality(agentId: string): string {
  const personalities = {
    blaze: 'Vamos a quemar esos límites juntos! 🔥',
    nova: 'Listos para explorar nuevos horizontes de fitness! ⭐',
    sage: 'La sabiduría antigua encuentra la ciencia moderna. 🧠',
    wave: 'Fluyamos hacia el equilibrio perfecto. 🌊',
    luna: 'Conectemos con tu ritmo natural. 🌙',
    vox: 'Tu voz es el poder que necesitas. 🎤',
    echo: 'Escuchemos lo que tu cuerpo necesita. 👂',
    zen: 'Encontremos la paz en el movimiento. 🧘',
    apex: 'Hacia la cima de tu potencial. 🏔️',
  };
  
  return personalities[agentId.toLowerCase() as keyof typeof personalities] || 'Estoy aquí para ayudarte! 💪';
}