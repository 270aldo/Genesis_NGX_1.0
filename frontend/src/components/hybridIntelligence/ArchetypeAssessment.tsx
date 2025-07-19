/**
 * Archetype Assessment Component
 * Determines user archetype (PRIME vs LONGEVITY) for Hybrid Intelligence Engine
 * Scientific assessment based on psychological and behavioral factors
 */

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useHybridIntelligenceStore } from '@/store/hybridIntelligenceStore';
import { type UserArchetype } from '@/services/api/hybridIntelligence.service';
import { 
  Target, 
  Heart, 
  Zap, 
  Shield, 
  Brain, 
  TrendingUp,
  Users,
  Star,
  Activity,
  Clock,
  Award,
  Lightbulb,
  BarChart3
} from 'lucide-react';

// Assessment questions for archetype determination
const ARCHETYPE_QUESTIONS = [
  {
    id: 'primary_motivation',
    category: 'core_drive',
    question: '¿Cuál describe mejor tu motivación principal en fitness y salud?',
    type: 'single_choice',
    options: [
      { 
        id: 'optimize_performance', 
        text: 'Optimizar mi rendimiento y superar mis límites constantemente',
        icon: Target,
        archetype_weight: { PRIME: 3, LONGEVITY: -1 }
      },
      { 
        id: 'maintain_health', 
        text: 'Mantener mi salud y prevenir problemas a largo plazo',
        icon: Shield,
        archetype_weight: { PRIME: -1, LONGEVITY: 3 }
      },
      { 
        id: 'feel_energetic', 
        text: 'Sentirme con energía y vitalidad en mi día a día',
        icon: Zap,
        archetype_weight: { PRIME: 1, LONGEVITY: 2 }
      },
      { 
        id: 'achieve_goals', 
        text: 'Lograr objetivos específicos y medibles rápidamente',
        icon: Award,
        archetype_weight: { PRIME: 2, LONGEVITY: 0 }
      }
    ]
  },
  {
    id: 'time_perspective',
    category: 'temporal_focus',
    question: '¿En qué horizonte temporal prefieres pensar?',
    type: 'single_choice',
    options: [
      {
        id: 'immediate_results',
        text: 'Resultados inmediatos y cambios rápidos (3-6 meses)',
        icon: Zap,
        archetype_weight: { PRIME: 3, LONGEVITY: -1 }
      },
      {
        id: 'annual_goals',
        text: 'Objetivos anuales con hitos claros y medibles',
        icon: Target,
        archetype_weight: { PRIME: 2, LONGEVITY: 1 }
      },
      {
        id: 'lifestyle_building',
        text: 'Construcción de hábitos y estilo de vida (5-10 años)',
        icon: TrendingUp,
        archetype_weight: { PRIME: 0, LONGEVITY: 2 }
      },
      {
        id: 'lifetime_wellness',
        text: 'Bienestar y salud para toda la vida (20+ años)',
        icon: Heart,
        archetype_weight: { PRIME: -1, LONGEVITY: 3 }
      }
    ]
  },
  {
    id: 'approach_style',
    category: 'methodology',
    question: '¿Cómo prefieres abordar nuevos desafíos?',
    type: 'single_choice',
    options: [
      {
        id: 'aggressive_direct',
        text: 'De forma agresiva y directa, con intensidad máxima',
        icon: Zap,
        archetype_weight: { PRIME: 3, LONGEVITY: -2 }
      },
      {
        id: 'systematic_efficient',
        text: 'Con un sistema eficiente y optimizado',
        icon: Brain,
        archetype_weight: { PRIME: 2, LONGEVITY: 0 }
      },
      {
        id: 'gradual_sustainable',
        text: 'Gradualmente, priorizando sostenibilidad',
        icon: Shield,
        archetype_weight: { PRIME: -1, LONGEVITY: 3 }
      },
      {
        id: 'balanced_holistic',
        text: 'De manera equilibrada y holística',
        icon: Heart,
        archetype_weight: { PRIME: 0, LONGEVITY: 2 }
      }
    ]
  },
  {
    id: 'risk_tolerance',
    category: 'risk_assessment',
    question: '¿Cómo te sientes sobre probar métodos nuevos o experimentales?',
    type: 'single_choice',
    options: [
      {
        id: 'high_risk_early_adopter',
        text: 'Me emociona ser early adopter de nuevas tecnologías y métodos',
        icon: Lightbulb,
        archetype_weight: { PRIME: 3, LONGEVITY: -1 }
      },
      {
        id: 'calculated_risk',
        text: 'Los pruebo si hay evidencia científica sólida',
        icon: BarChart3,
        archetype_weight: { PRIME: 1, LONGEVITY: 1 }
      },
      {
        id: 'conservative_proven',
        text: 'Prefiero métodos probados y tradicionales',
        icon: Shield,
        archetype_weight: { PRIME: -1, LONGEVITY: 2 }
      },
      {
        id: 'very_conservative',
        text: 'Solo uso métodos validados por años de investigación',
        icon: Award,
        archetype_weight: { PRIME: -2, LONGEVITY: 3 }
      }
    ]
  },
  {
    id: 'competition_orientation',
    category: 'social_dynamics',
    question: '¿Cómo te motiva la competencia?',
    type: 'single_choice',
    options: [
      {
        id: 'thrive_competition',
        text: 'Prospero en competencia directa, me motiva ganar',
        icon: Award,
        archetype_weight: { PRIME: 3, LONGEVITY: -1 }
      },
      {
        id: 'enjoy_challenges',
        text: 'Disfruto los desafíos pero no necesito ganar siempre',
        icon: Target,
        archetype_weight: { PRIME: 2, LONGEVITY: 0 }
      },
      {
        id: 'prefer_collaboration',
        text: 'Prefiero colaboración y apoyo mutuo',
        icon: Users,
        archetype_weight: { PRIME: 0, LONGEVITY: 2 }
      },
      {
        id: 'avoid_competition',
        text: 'Evito la competencia, prefiero mi propio ritmo',
        icon: Heart,
        archetype_weight: { PRIME: -2, LONGEVITY: 3 }
      }
    ]
  },
  {
    id: 'data_engagement',
    category: 'analytical_preference',
    question: '¿Qué tan importante es para ti el tracking detallado?',
    type: 'single_choice',
    options: [
      {
        id: 'data_obsessed',
        text: 'Esencial - analizo todo: HRV, VO2Max, macros, etc.',
        icon: BarChart3,
        archetype_weight: { PRIME: 3, LONGEVITY: 1 }
      },
      {
        id: 'key_metrics',
        text: 'Importante - track métricas clave para mis objetivos',
        icon: Target,
        archetype_weight: { PRIME: 2, LONGEVITY: 1 }
      },
      {
        id: 'basic_tracking',
        text: 'Útil - seguimiento básico de progreso',
        icon: TrendingUp,
        archetype_weight: { PRIME: 1, LONGEVITY: 2 }
      },
      {
        id: 'intuitive_approach',
        text: 'Me guío por cómo me siento más que por números',
        icon: Heart,
        archetype_weight: { PRIME: -1, LONGEVITY: 3 }
      }
    ]
  },
  {
    id: 'intensity_preference',
    category: 'training_style',
    question: '¿Cuál describe mejor tu preferencia de intensidad?',
    type: 'single_choice',
    options: [
      {
        id: 'max_intensity',
        text: 'Máxima intensidad - sin límites',
        icon: Zap,
        archetype_weight: { PRIME: 3, LONGEVITY: -2 }
      },
      {
        id: 'high_smart',
        text: 'Alta intensidad pero inteligente',
        icon: Brain,
        archetype_weight: { PRIME: 2, LONGEVITY: 0 }
      },
      {
        id: 'moderate_consistent',
        text: 'Intensidad moderada y consistente',
        icon: TrendingUp,
        archetype_weight: { PRIME: 0, LONGEVITY: 2 }
      },
      {
        id: 'gentle_sustainable',
        text: 'Intensidad suave y sostenible',
        icon: Heart,
        archetype_weight: { PRIME: -2, LONGEVITY: 3 }
      }
    ]
  }
];

interface ArchetypeAssessmentProps {
  onComplete?: (archetype: UserArchetype) => void;
  className?: string;
}

export const ArchetypeAssessment: React.FC<ArchetypeAssessmentProps> = ({
  onComplete,
  className
}) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [responses, setResponses] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [calculatedArchetype, setCalculatedArchetype] = useState<UserArchetype | null>(null);
  const [archetypeScores, setArchetypeScores] = useState<{ PRIME: number; LONGEVITY: number } | null>(null);
  
  const { initializeProfile, isLoading } = useHybridIntelligenceStore();

  // Calculate progress
  const progress = ((currentQuestion + 1) / ARCHETYPE_QUESTIONS.length) * 100;

  // Handle answer selection
  const handleAnswer = useCallback((questionId: string, answer: string) => {
    setResponses(prev => ({ ...prev, [questionId]: answer }));
  }, []);

  // Navigate to next question
  const handleNext = useCallback(() => {
    if (currentQuestion < ARCHETYPE_QUESTIONS.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    } else {
      calculateArchetype();
    }
  }, [currentQuestion, responses]);

  // Navigate to previous question
  const handlePrevious = useCallback(() => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  }, [currentQuestion]);

  // Calculate archetype based on responses
  const calculateArchetype = useCallback(() => {
    setIsSubmitting(true);
    
    const scores = { PRIME: 0, LONGEVITY: 0 };
    
    // Calculate weighted scores
    ARCHETYPE_QUESTIONS.forEach(question => {
      const selectedAnswerId = responses[question.id];
      if (selectedAnswerId) {
        const selectedOption = question.options.find(opt => opt.id === selectedAnswerId);
        if (selectedOption) {
          scores.PRIME += selectedOption.archetype_weight.PRIME;
          scores.LONGEVITY += selectedOption.archetype_weight.LONGEVITY;
        }
      }
    });
    
    // Determine archetype
    const determinedArchetype: UserArchetype = scores.PRIME > scores.LONGEVITY ? 'PRIME' : 'LONGEVITY';
    
    setArchetypeScores(scores);
    setCalculatedArchetype(determinedArchetype);
    setShowResults(true);
    setIsSubmitting(false);
  }, [responses]);

  // Confirm archetype and initialize profile
  const handleConfirmArchetype = useCallback(async () => {
    if (!calculatedArchetype) return;
    
    try {
      // Create initial profile data
      const initialData = {
        user_id: '', // Will be set by the service
        archetype: calculatedArchetype,
        fitness_level: 'INTERMEDIATE' as const,
        age: 30, // Default, should be collected separately
        gender: 'other' as const, // Default, should be collected separately
        biometrics: {},
        constraints: {
          goals: []
        },
        preferences: {
          communication_style: calculatedArchetype === 'PRIME' ? 'direct' as const : 'supportive' as const,
          detail_level: calculatedArchetype === 'PRIME' ? 'detailed' as const : 'moderate' as const,
          feedback_frequency: calculatedArchetype === 'PRIME' ? 'real_time' as const : 'daily' as const
        }
      };
      
      await initializeProfile(calculatedArchetype, initialData);
      onComplete?.(calculatedArchetype);
    } catch (error) {
      console.error('Failed to initialize profile:', error);
    }
  }, [calculatedArchetype, initializeProfile, onComplete]);

  // Get archetype display information
  const getArchetypeDisplay = (archetype: UserArchetype) => {
    if (archetype === 'PRIME') {
      return {
        color: 'from-orange-500 to-red-500',
        bgColor: 'bg-orange-50 border-orange-200',
        textColor: 'text-orange-700',
        icon: Zap,
        label: 'PRIME',
        title: 'Optimizador de Rendimiento',
        description: 'Eres un optimizador nato que busca maximizar el rendimiento y la eficiencia. Te motivan los desafíos, la competencia y los resultados medibles.',
        traits: [
          'Orientado a resultados',
          'Competitivo por naturaleza',
          'Busca eficiencia máxima',
          'Abraza la innovación',
          'Enfocado en el rendimiento'
        ],
        approach: 'Te beneficiarás de entrenamientos intensos, métricas detalladas, y desafíos progresivos que te permitan superar constantemente tus límites.'
      };
    } else {
      return {
        color: 'from-green-500 to-emerald-500',
        bgColor: 'bg-green-50 border-green-200',
        textColor: 'text-green-700',
        icon: Heart,
        label: 'LONGEVITY',
        title: 'Arquitecto de Bienestar',
        description: 'Eres un arquitecto del bienestar que construye salud sostenible a largo plazo. Priorizas la prevención, el equilibrio y la calidad de vida.',
        traits: [
          'Enfocado en sostenibilidad',
          'Preventivo y prudente',
          'Busca equilibrio holístico',
          'Valora la consistencia',
          'Orientado al bienestar'
        ],
        approach: 'Te beneficiarás de enfoques graduales, hábitos sostenibles, y estrategias que promuevan la salud integral y la longevidad.'
      };
    }
  };

  if (showResults && calculatedArchetype) {
    const archetypeDisplay = getArchetypeDisplay(calculatedArchetype);
    const ArchetypeIcon = archetypeDisplay.icon;
    const confidence = archetypeScores ? Math.abs(archetypeScores.PRIME - archetypeScores.LONGEVITY) / (Math.abs(archetypeScores.PRIME) + Math.abs(archetypeScores.LONGEVITY)) : 0;

    return (
      <div className={cn("max-w-4xl mx-auto p-6", className)}>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center mb-8"
        >
          <div className={cn("inline-flex p-6 rounded-full mb-6", archetypeDisplay.bgColor)}>
            <ArchetypeIcon className={cn("w-16 h-16", archetypeDisplay.textColor)} />
          </div>
          
          <Badge className={cn("bg-gradient-to-r text-white text-lg px-6 py-2 mb-4", archetypeDisplay.color)}>
            {archetypeDisplay.label}
          </Badge>
          
          <h1 className="text-3xl font-bold mb-2">{archetypeDisplay.title}</h1>
          <p className="text-gray-600 text-lg max-w-2xl mx-auto">
            {archetypeDisplay.description}
          </p>
        </motion.div>

        {/* Confidence Score */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 mb-2">
                {Math.round(confidence * 100)}% de confianza
              </div>
              <Progress value={confidence * 100} className="h-3 mb-2" />
              <p className="text-sm text-gray-600">
                Basado en tus respuestas, tenemos una {confidence > 0.7 ? 'alta' : confidence > 0.4 ? 'moderada' : 'baja'} confianza en esta determinación
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Archetype Details */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Traits */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="w-5 h-5" />
                Tus Características
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {archetypeDisplay.traits.map((trait, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className={cn("w-2 h-2 rounded-full bg-gradient-to-r", archetypeDisplay.color)} />
                    <span className="text-gray-700">{trait}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Approach */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Tu Enfoque Óptimo
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 leading-relaxed">
                {archetypeDisplay.approach}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Score Breakdown */}
        {archetypeScores && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Desglose de Puntuación</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="flex items-center gap-2">
                      <Zap className="w-4 h-4 text-orange-500" />
                      PRIME (Optimizador)
                    </span>
                    <span className="font-bold">{archetypeScores.PRIME}</span>
                  </div>
                  <Progress 
                    value={Math.max(0, archetypeScores.PRIME) * 10} 
                    className="h-2"
                  />
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="flex items-center gap-2">
                      <Heart className="w-4 h-4 text-green-500" />
                      LONGEVITY (Arquitecto)
                    </span>
                    <span className="font-bold">{archetypeScores.LONGEVITY}</span>
                  </div>
                  <Progress 
                    value={Math.max(0, archetypeScores.LONGEVITY) * 10} 
                    className="h-2"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        <div className="flex gap-4 justify-center">
          <Button
            variant="outline"
            onClick={() => {
              setShowResults(false);
              setCurrentQuestion(0);
              setResponses({});
              setCalculatedArchetype(null);
              setArchetypeScores(null);
            }}
          >
            Repetir Evaluación
          </Button>
          
          <Button
            onClick={handleConfirmArchetype}
            disabled={isLoading}
            className={cn("bg-gradient-to-r text-white", archetypeDisplay.color)}
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Configurando...
              </div>
            ) : (
              'Confirmar y Continuar'
            )}
          </Button>
        </div>
      </div>
    );
  }

  const currentQ = ARCHETYPE_QUESTIONS[currentQuestion];
  const currentAnswer = responses[currentQ.id];
  const canProceed = currentAnswer !== undefined;

  return (
    <div className={cn("max-w-4xl mx-auto p-6", className)}>
      {/* Header */}
      <div className="text-center mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-500 via-purple-500 to-green-500 bg-clip-text text-transparent">
            Evaluación de Arquetipo NGX
          </h1>
          <p className="text-gray-600 mt-2">
            Descubre si eres <strong>PRIME</strong> (Optimizador) o <strong>LONGEVITY</strong> (Arquitecto de Bienestar)
          </p>
        </motion.div>
        
        {/* Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-500">
            <span>Pregunta {currentQuestion + 1} de {ARCHETYPE_QUESTIONS.length}</span>
            <span>{Math.round(progress)}% completado</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      </div>

      {/* Question Card */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentQuestion}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -50 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="text-xl flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-500 to-green-500 flex items-center justify-center text-white text-sm font-bold">
                  {currentQuestion + 1}
                </div>
                {currentQ.question}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {currentQ.options.map((option) => {
                  const Icon = option.icon;
                  const isSelected = currentAnswer === option.id;
                  
                  return (
                    <motion.button
                      key={option.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleAnswer(currentQ.id, option.id)}
                      className={cn(
                        "p-4 rounded-lg border-2 text-left transition-all duration-200 hover:shadow-md",
                        isSelected 
                          ? "border-blue-500 bg-blue-50 shadow-md" 
                          : "border-gray-200 hover:border-gray-300"
                      )}
                    >
                      <div className="flex items-start gap-4">
                        <div className={cn(
                          "p-2 rounded-lg",
                          isSelected ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-600"
                        )}>
                          <Icon size={20} />
                        </div>
                        <div className="flex-1">
                          <p className={cn(
                            "font-medium",
                            isSelected ? "text-blue-700" : "text-gray-700"
                          )}>
                            {option.text}
                          </p>
                          {/* Archetype indicators */}
                          <div className="flex gap-2 mt-2">
                            {option.archetype_weight.PRIME > 0 && (
                              <Badge 
                                variant="outline" 
                                className="text-xs bg-orange-50 text-orange-600 border-orange-200"
                              >
                                PRIME +{option.archetype_weight.PRIME}
                              </Badge>
                            )}
                            {option.archetype_weight.LONGEVITY > 0 && (
                              <Badge 
                                variant="outline" 
                                className="text-xs bg-green-50 text-green-600 border-green-200"
                              >
                                LONGEVITY +{option.archetype_weight.LONGEVITY}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </motion.button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentQuestion === 0}
          className="px-6"
        >
          Anterior
        </Button>
        
        <div className="flex gap-2">
          {ARCHETYPE_QUESTIONS.map((_, index) => (
            <div
              key={index}
              className={cn(
                "w-2 h-2 rounded-full transition-colors",
                index <= currentQuestion ? "bg-blue-500" : "bg-gray-300"
              )}
            />
          ))}
        </div>
        
        <Button
          onClick={handleNext}
          disabled={!canProceed || isSubmitting}
          className="px-6 bg-gradient-to-r from-orange-500 to-green-500 hover:from-orange-600 hover:to-green-600"
        >
          {isSubmitting ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Analizando...
            </div>
          ) : currentQuestion === ARCHETYPE_QUESTIONS.length - 1 ? (
            "Ver Resultado"
          ) : (
            "Siguiente"
          )}
        </Button>
      </div>

      {/* Info Card */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-8 p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-blue-200"
      >
        <h3 className="font-semibold text-blue-800 mb-2">Hybrid Intelligence Engine</h3>
        <p className="text-blue-700 text-sm">
          Esta evaluación determina tu arquetipo para el sistema de <strong>personalización de 2 capas</strong>: 
          <strong> Capa 1</strong> (adaptación estratégica por arquetipo) + 
          <strong> Capa 2</strong> (modulación fisiológica en tiempo real). 
          Este sistema revolucionario adapta cada interacción a tu perfil único.
        </p>
      </motion.div>
    </div>
  );
};