/**
 * Hybrid Intelligence Integration Tests
 * Tests the complete 2-layer personalization system integration
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useHybridIntelligenceStore } from '@/store/hybridIntelligenceStore';
import { HybridIntelligenceDashboard } from '../HybridIntelligenceDashboard';
import { ArchetypeAssessment } from '../ArchetypeAssessment';
import { BiometricDataInput } from '../BiometricDataInput';
import { hybridIntelligenceService } from '@/services/api/hybridIntelligence.service';

// Mock the service
jest.mock('@/services/api/hybridIntelligence.service', () => ({
  hybridIntelligenceService: {
    initializeProfile: jest.fn(),
    getUserProfile: jest.fn(),
    updateBiometrics: jest.fn(),
    updateBiomarkers: jest.fn(),
    getUserInsights: jest.fn(),
    getAgentPersonalization: jest.fn(),
    provideLearningFeedback: jest.fn(),
    clearCache: jest.fn(),
  },
}));

// Mock Zustand store
jest.mock('@/store/hybridIntelligenceStore', () => ({
  useHybridIntelligenceStore: jest.fn(),
}));

describe('Hybrid Intelligence Integration', () => {
  const mockStoreData = {
    profile: {
      user_id: 'test-user',
      archetype: 'PRIME',
      fitness_level: 'INTERMEDIATE',
      age: 28,
      gender: 'male',
      biometrics: {
        sleep_quality: 0.8,
        sleep_duration: 7.5,
        stress_level: 0.3,
        energy_level: 0.85,
        recovery_status: 0.9,
        heart_rate_variability: 45,
        resting_heart_rate: 62,
        readiness_score: 85,
      },
      biomarkers: {
        testosterone: 650,
        cortisol: 12,
        vitamin_d: 35,
        b12: 450,
        inflammation_markers: 1.2,
        glucose: 95,
        last_updated: '2024-01-15T10:00:00Z',
      },
      constraints: { goals: ['build_muscle', 'increase_strength'] },
      preferences: {
        communication_style: 'direct',
        detail_level: 'detailed',
        feedback_frequency: 'real_time',
      },
    },
    insights: {
      archetype_analysis: {
        confidence: 0.85,
        primary_traits: ['Competitivo', 'Orientado a resultados', 'Eficiente'],
        behavioral_patterns: ['Prefiere entrenamientos intensos', 'Busca métricas detalladas'],
        optimization_opportunities: ['Mejorar recuperación', 'Optimizar timing'],
      },
      physiological_insights: {
        recovery_patterns: ['Recuperación rápida después de entrenamientos intensos'],
        performance_indicators: ['HRV alto indica buena capacidad de recuperación'],
        health_recommendations: ['Mantener rutina de sueño consistente'],
      },
      predictive_insights: {
        goal_achievement_probability: 0.78,
        success_factors: ['Consistencia en entrenamientos', 'Monitoreo de métricas'],
        risk_factors: ['Posible sobreentrenamiento si no se gestiona el estrés'],
      },
      personalization_recommendations: {
        agent_affinities: {
          blaze: 0.9,
          nova: 0.8,
          sage: 0.6,
          wave: 0.5,
          luna: 0.4,
        },
        optimal_interaction_times: ['06:00-08:00', '18:00-20:00'],
        communication_adjustments: ['Uso de lenguaje directo', 'Enfoque en resultados'],
      },
    },
    archetype: 'PRIME',
    confidenceScore: 0.85,
    adaptationCount: 12,
    currentBiometrics: {
      sleep_quality: 0.8,
      energy_level: 0.85,
      stress_level: 0.3,
    },
    biomarkers: {
      testosterone: 650,
      cortisol: 12,
    },
    isLoading: false,
    error: null,
    isInitialized: true,
  };

  const mockActions = {
    initializeProfile: jest.fn(),
    loadProfile: jest.fn(),
    updateBiometrics: jest.fn(),
    updateBiomarkers: jest.fn(),
    personalizeForAgent: jest.fn(),
    trackPersonalization: jest.fn(),
    provideFeedback: jest.fn(),
    loadInsights: jest.fn(),
    getAgentAffinity: jest.fn(),
    getPersonalizedGreeting: jest.fn(),
    getOptimalTiming: jest.fn(),
    clearError: jest.fn(),
    resetProfile: jest.fn(),
    clearCache: jest.fn(),
    isArchetypeConfident: jest.fn(),
    getBioDataQuality: jest.fn(),
    getPersonalizationEffectiveness: jest.fn(),
    getRecommendedAgents: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (useHybridIntelligenceStore as any).mockReturnValue({
      ...mockStoreData,
      ...mockActions,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('HybridIntelligenceDashboard', () => {
    it('renders dashboard with PRIME archetype correctly', () => {
      render(<HybridIntelligenceDashboard />);
      
      expect(screen.getByText('Hybrid Intelligence Engine')).toBeInTheDocument();
      expect(screen.getByText('PRIME')).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument(); // Confidence score
    });

    it('displays biometric data correctly', () => {
      render(<HybridIntelligenceDashboard />);
      
      // Switch to biometrics tab
      fireEvent.click(screen.getByText('Biometría'));
      
      expect(screen.getByText('80%')).toBeInTheDocument(); // Sleep quality
      expect(screen.getByText('7.5h')).toBeInTheDocument(); // Sleep duration
      expect(screen.getByText('85%')).toBeInTheDocument(); // Energy level
    });

    it('shows recommended agents based on archetype', () => {
      mockActions.getRecommendedAgents.mockReturnValue(['blaze', 'nova', 'sage']);
      
      render(<HybridIntelligenceDashboard />);
      
      expect(screen.getByText('Agentes Recomendados')).toBeInTheDocument();
      expect(screen.getByText('BLAZE')).toBeInTheDocument();
      expect(screen.getByText('NOVA')).toBeInTheDocument();
      expect(screen.getByText('SAGE')).toBeInTheDocument();
    });

    it('displays personalized greeting correctly', () => {
      mockActions.getPersonalizedGreeting.mockReturnValue('¡Buenos días! ¿En qué nos enfocamos hoy?');
      
      render(<HybridIntelligenceDashboard />);
      
      expect(screen.getByText('¡Buenos días! ¿En qué nos enfocamos hoy?')).toBeInTheDocument();
    });
  });

  describe('ArchetypeAssessment', () => {
    it('completes assessment flow correctly', async () => {
      const mockOnComplete = jest.fn();
      mockActions.initializeProfile.mockResolvedValue(mockStoreData.profile);
      
      render(<ArchetypeAssessment onComplete={mockOnComplete} />);
      
      // Should start with first question
      expect(screen.getByText('Pregunta 1 de 7')).toBeInTheDocument();
      
      // Answer first question
      const firstOption = screen.getByText('Optimizar mi rendimiento y superar mis límites constantemente');
      fireEvent.click(firstOption);
      
      // Click next
      fireEvent.click(screen.getByText('Siguiente'));
      
      // Should progress to next question
      expect(screen.getByText('Pregunta 2 de 7')).toBeInTheDocument();
    });

    it('calculates archetype correctly based on responses', async () => {
      const mockOnComplete = jest.fn();
      mockActions.initializeProfile.mockResolvedValue(mockStoreData.profile);
      
      render(<ArchetypeAssessment onComplete={mockOnComplete} />);
      
      // Answer all questions with PRIME-leaning responses
      const primeOptions = [
        'Optimizar mi rendimiento y superar mis límites constantemente',
        'Resultados inmediatos y cambios rápidos (3-6 meses)',
        'De forma agresiva y directa, con intensidad máxima',
        'Me emociona ser early adopter de nuevas tecnologías y métodos',
        'Prospero en competencia directa, me motiva ganar',
        'Esencial - analizo todo: HRV, VO2Max, macros, etc.',
        'Máxima intensidad - sin límites',
      ];
      
      for (let i = 0; i < primeOptions.length; i++) {
        const option = screen.getByText(primeOptions[i]);
        fireEvent.click(option);
        
        if (i < primeOptions.length - 1) {
          fireEvent.click(screen.getByText('Siguiente'));
        } else {
          fireEvent.click(screen.getByText('Ver Resultado'));
        }
      }
      
      // Should show PRIME result
      await waitFor(() => {
        expect(screen.getByText('Optimizador de Rendimiento')).toBeInTheDocument();
        expect(screen.getByText('PRIME')).toBeInTheDocument();
      });
    });
  });

  describe('BiometricDataInput', () => {
    it('updates biometric data correctly', async () => {
      mockActions.updateBiometrics.mockResolvedValue(undefined);
      
      render(<BiometricDataInput />);
      
      // Update sleep quality
      const sleepQualitySlider = screen.getByRole('slider', { name: /calidad del sueño/i });
      fireEvent.change(sleepQualitySlider, { target: { value: '85' } });
      
      // Update heart rate
      const hrInput = screen.getByPlaceholderText('ej. 65');
      fireEvent.change(hrInput, { target: { value: '65' } });
      
      // Submit biometrics
      fireEvent.click(screen.getByText('Actualizar Biométricos'));
      
      await waitFor(() => {
        expect(mockActions.updateBiometrics).toHaveBeenCalledWith(
          expect.objectContaining({
            sleep_quality: 0.85,
            resting_heart_rate: 65,
          })
        );
      });
    });

    it('updates biomarker data correctly', async () => {
      mockActions.updateBiomarkers.mockResolvedValue(undefined);
      
      render(<BiometricDataInput />);
      
      // Switch to biomarkers tab
      fireEvent.click(screen.getByText('Biomarcadores'));
      
      // Update testosterone
      const testosteroneInput = screen.getByPlaceholderText('ej. 650');
      fireEvent.change(testosteroneInput, { target: { value: '700' } });
      
      // Update cortisol
      const cortisolInput = screen.getByPlaceholderText('ej. 12');
      fireEvent.change(cortisolInput, { target: { value: '10' } });
      
      // Submit biomarkers
      fireEvent.click(screen.getByText('Actualizar Biomarcadores'));
      
      await waitFor(() => {
        expect(mockActions.updateBiomarkers).toHaveBeenCalledWith(
          expect.objectContaining({
            testosterone: 700,
            cortisol: 10,
            last_updated: expect.any(String),
          })
        );
      });
    });
  });

  describe('Service Integration', () => {
    it('initializes profile correctly', async () => {
      const mockProfile = { ...mockStoreData.profile };
      (hybridIntelligenceService.initializeProfile as any).mockResolvedValue(mockProfile);
      
      const { initializeProfile } = useHybridIntelligenceStore();
      
      await initializeProfile('PRIME', {
        fitness_level: 'INTERMEDIATE',
        age: 28,
        gender: 'male',
      });
      
      expect(hybridIntelligenceService.initializeProfile).toHaveBeenCalledWith(
        'PRIME',
        expect.objectContaining({
          fitness_level: 'INTERMEDIATE',
          age: 28,
          gender: 'male',
        })
      );
    });

    it('handles personalization requests correctly', async () => {
      const mockPersonalization = {
        personalized_content: 'Personalizado para PRIME',
        archetype_considerations: {
          strategic_alignment: 'performance_optimization',
          communication_style: 'direct',
          intensity_preference: 'high',
        },
        physiological_modulations: {
          energy_level_factor: 0.85,
          recovery_status_factor: 0.9,
          stress_level_factor: 0.3,
        },
        confidence_score: 0.87,
        metadata: {
          agentId: 'blaze',
          timestamp: '2024-01-15T10:00:00Z',
        },
      };
      
      (hybridIntelligenceService.getAgentPersonalization as any).mockResolvedValue(mockPersonalization);
      
      const { personalizeForAgent } = useHybridIntelligenceStore();
      
      const result = await personalizeForAgent('blaze', 'workout_recommendation', {
        goal: 'build_muscle',
        available_time: 60,
      });
      
      expect(result).toEqual(mockPersonalization);
      expect(hybridIntelligenceService.getAgentPersonalization).toHaveBeenCalledWith(
        'blaze',
        'workout_recommendation',
        { goal: 'build_muscle', available_time: 60 }
      );
    });

    it('provides learning feedback correctly', async () => {
      const mockFeedback = {
        interaction_id: 'test_interaction_123',
        user_response: 'positive',
        effectiveness_rating: 8,
        feedback_text: 'Great recommendation!',
        timestamp: '2024-01-15T10:00:00Z',
      };
      
      (hybridIntelligenceService.provideLearningFeedback as any).mockResolvedValue(undefined);
      
      const { provideFeedback } = useHybridIntelligenceStore();
      
      await provideFeedback(mockFeedback);
      
      expect(hybridIntelligenceService.provideLearningFeedback).toHaveBeenCalledWith(mockFeedback);
    });
  });

  describe('Error Handling', () => {
    it('handles service errors gracefully', async () => {
      const mockError = new Error('Service unavailable');
      (hybridIntelligenceService.getUserProfile as any).mockRejectedValue(mockError);
      
      const mockStoreWithError = {
        ...mockStoreData,
        error: 'Service unavailable',
        isLoading: false,
      };
      
      (useHybridIntelligenceStore as any).mockReturnValue({
        ...mockStoreWithError,
        ...mockActions,
      });
      
      render(<HybridIntelligenceDashboard />);
      
      expect(screen.getByText('Error en Hybrid Intelligence')).toBeInTheDocument();
      expect(screen.getByText('Service unavailable')).toBeInTheDocument();
    });

    it('shows loading state correctly', () => {
      const mockStoreLoading = {
        ...mockStoreData,
        isLoading: true,
        profile: null,
      };
      
      (useHybridIntelligenceStore as any).mockReturnValue({
        ...mockStoreLoading,
        ...mockActions,
      });
      
      render(<HybridIntelligenceDashboard />);
      
      expect(screen.getByText('Cargando Hybrid Intelligence...')).toBeInTheDocument();
    });
  });

  describe('Real-time Updates', () => {
    it('updates dashboard when biometric data changes', async () => {
      const { rerender } = render(<HybridIntelligenceDashboard />);
      
      // Update store with new biometric data
      const updatedStore = {
        ...mockStoreData,
        currentBiometrics: {
          ...mockStoreData.currentBiometrics,
          energy_level: 0.95, // Increased energy
        },
      };
      
      (useHybridIntelligenceStore as any).mockReturnValue({
        ...updatedStore,
        ...mockActions,
      });
      
      rerender(<HybridIntelligenceDashboard />);
      
      // Switch to biometrics tab
      fireEvent.click(screen.getByText('Biometría'));
      
      // Should show updated energy level
      expect(screen.getByText('95%')).toBeInTheDocument();
    });
  });
});