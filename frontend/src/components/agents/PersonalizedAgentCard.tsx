/**
 * Personalized Agent Card Component
 * Agent card that adapts based on Hybrid Intelligence personalization
 * Shows agent affinity, compatibility, and personalized messaging
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { useHybridIntelligencePersonalization } from '@/hooks/useHybridIntelligencePersonalization';
import { useHybridIntelligenceStore } from '@/store/hybridIntelligenceStore';
import { useFeatureFlags } from '@/hooks/useFeatureFlags';
import {
  Star,
  Zap,
  Heart,
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle,
  MessageSquare,
  User,
  Target,
  Eye,
  Brain,
  Users,
  ArrowRight,
  Workflow
} from 'lucide-react';

interface PersonalizedAgentCardProps {
  agentId: string;
  agentName: string;
  agentDescription: string;
  agentIcon: React.ComponentType<{ className?: string }>;
  agentColor: string;
  isActive?: boolean;
  onSelect?: (agentId: string) => void;
  onStartChat?: (agentId: string, context?: any) => void;
  className?: string;
}

export const PersonalizedAgentCard: React.FC<PersonalizedAgentCardProps> = ({
  agentId,
  agentName,
  agentDescription,
  agentIcon: AgentIcon,
  agentColor,
  isActive = false,
  onSelect,
  onStartChat,
  className
}) => {
  const {
    personalizeContent,
    getPersonalizedGreeting,
    checkAgentCompatibility,
    agentAffinity
  } = useHybridIntelligencePersonalization();

  const {
    archetype,
    currentBiometrics,
    getAgentAffinity,
    isArchetypeConfident
  } = useHybridIntelligenceStore();

  const {
    flags,
    isNexusOnlyMode,
    shouldShowCollaboration
  } = useFeatureFlags();

  const [personalizedData, setPersonalizedData] = useState<{
    greeting: string;
    compatibility: { compatible: boolean; reason?: string };
    affinity: number;
    recommendations: string[];
    optimalTiming: boolean;
  }>({
    greeting: '',
    compatibility: { compatible: true },
    affinity: 0,
    recommendations: [],
    optimalTiming: false,
  });

  const [isPersonalizing, setIsPersonalizing] = useState(false);

  // Load personalized data on mount and when archetype changes
  useEffect(() => {
    if (archetype) {
      loadPersonalizedData();
    }
  }, [agentId, archetype]);

  const loadPersonalizedData = async () => {
    setIsPersonalizing(true);

    try {
      // Get personalized greeting
      const greeting = getPersonalizedGreeting(agentId);

      // Check compatibility
      const compatibility = checkAgentCompatibility(agentId);

      // Get affinity score
      const affinity = getAgentAffinity(agentId);

      // Get personalized recommendations
      const personalizationResult = await personalizeContent({
        agentId,
        requestType: 'general_chat',
        context: {
          timeOfDay: new Date().toISOString(),
          currentGoal: 'introduction',
        },
        priority: 'low',
      });

      // Check if current time is optimal
      const currentHour = new Date().getHours();
      const optimalTiming = isOptimalTimeForAgent(agentId, currentHour);

      setPersonalizedData({
        greeting,
        compatibility,
        affinity,
        recommendations: personalizationResult?.archetype_considerations ?
          extractRecommendations(personalizationResult) : [],
        optimalTiming,
      });
    } catch (error) {
      console.error('Failed to load personalized data:', error);
    } finally {
      setIsPersonalizing(false);
    }
  };

  const handleCardClick = () => {
    if (onSelect) {
      onSelect(agentId);
    }
  };

  const handleStartChat = () => {
    if (onStartChat) {
      // In NEXUS-only mode, always start chat with NEXUS but pass original agent context
      const chatAgentId = isNexusOnlyMode ? 'nexus' : agentId;
      onStartChat(chatAgentId, isNexusOnlyMode ? { originalAgentId: agentId } : undefined);
    }
  };

  const handleViewSpecialty = () => {
    // In NEXUS-only mode, show agent info but initiate NEXUS chat
    if (isNexusOnlyMode) {
      handleStartChat();
    } else if (onSelect) {
      onSelect(agentId);
    }
  };

  const getAffinityColor = (affinity: number) => {
    if (affinity > 0.7) return 'text-green-600 bg-green-50';
    if (affinity > 0.5) return 'text-blue-600 bg-blue-50';
    if (affinity > 0.3) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getAffinityLabel = (affinity: number) => {
    if (affinity > 0.7) return 'Excelente';
    if (affinity > 0.5) return 'Buena';
    if (affinity > 0.3) return 'Moderada';
    return 'Baja';
  };

  const getArchetypeAlignment = () => {
    if (!archetype) return null;

    const archetypeAgentAlignment = {
      PRIME: ['blaze', 'nova', 'apex', 'vox'],
      LONGEVITY: ['sage', 'wave', 'luna', 'zen', 'echo'],
    };

    const isAligned = archetypeAgentAlignment[archetype]?.includes(agentId.toLowerCase());

    return {
      isAligned,
      label: isAligned ? 'Alineado con tu arquetipo' : 'Arquetipo complementario',
      color: isAligned ? 'text-green-600' : 'text-blue-600',
    };
  };

  const archetypeAlignment = getArchetypeAlignment();

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(className)}
    >
      <Card
        className={cn(
          "cursor-pointer transition-all duration-200 hover:shadow-lg",
          isActive ? "ring-2 ring-blue-500 shadow-lg" : "",
          !personalizedData.compatibility.compatible ? "opacity-75" : ""
        )}
        onClick={handleCardClick}
      >
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={cn("p-2 rounded-lg", `bg-${agentColor}-100`)}>
                <AgentIcon className={cn("w-8 h-8", `text-${agentColor}-600`)} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-lg">{agentName}</h3>
                  {isNexusOnlyMode && (
                    <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700 border-purple-200">
                      <Brain className="w-3 h-3 mr-1" />
                      Coordinado por NEXUS
                    </Badge>
                  )}
                </div>
                <p className="text-sm text-gray-600">{agentDescription}</p>
              </div>
            </div>

            {/* Affinity Score */}
            <div className="text-right">
              <div className={cn("text-2xl font-bold", getAffinityColor(personalizedData.affinity))}>
                {Math.round(personalizedData.affinity * 100)}%
              </div>
              <div className="text-xs text-gray-500">
                {getAffinityLabel(personalizedData.affinity)}
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Personalized Greeting */}
          {personalizedData.greeting && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-700 italic">
                "{personalizedData.greeting}"
              </p>
            </div>
          )}

          {/* NEXUS Coordination Info */}
          {isNexusOnlyMode && (
            <div className="p-3 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200 mb-3">
              <div className="flex items-center gap-2 mb-1">
                <Workflow className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium text-purple-900">Tu Equipo NGX</span>
              </div>
              <p className="text-xs text-purple-700">
                NEXUS coordinará con {agentName} y otros especialistas para darte respuestas integrales.
              </p>
            </div>
          )}

          {/* Compatibility Status */}
          <div className="flex items-center gap-2">
            {personalizedData.compatibility.compatible ? (
              <CheckCircle className="w-4 h-4 text-green-500" />
            ) : (
              <AlertCircle className="w-4 h-4 text-red-500" />
            )}
            <span className={cn(
              "text-sm",
              personalizedData.compatibility.compatible ? "text-green-700" : "text-red-700"
            )}>
              {personalizedData.compatibility.reason || "Compatible con tu perfil"}
            </span>
          </div>

          {/* Archetype Alignment */}
          {archetypeAlignment && (
            <div className="flex items-center gap-2">
              <Target className={cn("w-4 h-4", archetypeAlignment.color)} />
              <span className={cn("text-sm", archetypeAlignment.color)}>
                {archetypeAlignment.label}
              </span>
            </div>
          )}

          {/* Affinity Progress */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Afinidad</span>
              <span className="text-sm text-gray-600">
                {Math.round(personalizedData.affinity * 100)}%
              </span>
            </div>
            <Progress
              value={personalizedData.affinity * 100}
              className="h-2"
            />
          </div>

          {/* Optimal Timing Indicator */}
          {personalizedData.optimalTiming && (
            <div className="flex items-center gap-2 p-2 bg-green-50 rounded-lg">
              <Clock className="w-4 h-4 text-green-600" />
              <span className="text-sm text-green-700">
                Momento óptimo para interactuar
              </span>
            </div>
          )}

          {/* Personalized Recommendations */}
          {personalizedData.recommendations.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Recomendaciones:</h4>
              <div className="space-y-1">
                {personalizedData.recommendations.slice(0, 2).map((rec, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <Star className="w-3 h-3 text-yellow-500 mt-1 flex-shrink-0" />
                    <span className="text-xs text-gray-600">{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Biometric-based Insights */}
          {currentBiometrics && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Estado actual:</h4>
              <div className="grid grid-cols-2 gap-2">
                {currentBiometrics.energy_level !== undefined && (
                  <div className="flex items-center gap-1">
                    <Zap className="w-3 h-3 text-yellow-500" />
                    <span className="text-xs text-gray-600">
                      Energía: {Math.round(currentBiometrics.energy_level * 100)}%
                    </span>
                  </div>
                )}
                {currentBiometrics.recovery_status !== undefined && (
                  <div className="flex items-center gap-1">
                    <Heart className="w-3 h-3 text-red-500" />
                    <span className="text-xs text-gray-600">
                      Recuperación: {Math.round(currentBiometrics.recovery_status * 100)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2">
            {isNexusOnlyMode ? (
              <>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleViewSpecialty();
                  }}
                  className="flex-1"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Ver Especialidad
                </Button>

                <Button
                  size="sm"
                  variant="default"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleStartChat();
                  }}
                  disabled={!personalizedData.compatibility.compatible}
                  className="flex-1 bg-purple-500 hover:bg-purple-600"
                >
                  <Users className="w-4 h-4 mr-2" />
                  Consultar con NEXUS
                </Button>
              </>
            ) : (
              <Button
                size="sm"
                variant="outline"
                onClick={(e) => {
                  e.stopPropagation();
                  handleStartChat();
                }}
                disabled={!personalizedData.compatibility.compatible}
                className="flex-1"
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                Chatear
              </Button>
            )}

            {isPersonalizing && (
              <Button size="sm" variant="ghost" disabled>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <TrendingUp className="w-4 h-4" />
                </motion.div>
              </Button>
            )}
          </div>

          {/* NEXUS Flow Indicator */}
          {isNexusOnlyMode && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex items-center justify-center gap-2 text-xs text-purple-600">
                <span>{agentName}</span>
                <ArrowRight className="w-3 h-3" />
                <span className="font-medium">NEXUS</span>
                <ArrowRight className="w-3 h-3" />
                <span>Respuesta Integral</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Helper functions

function extractRecommendations(personalizationResult: any): string[] {
  const recommendations: string[] = [];

  if (personalizationResult.archetype_considerations) {
    const { strategic_alignment, communication_style, intensity_preference } = personalizationResult.archetype_considerations;

    if (strategic_alignment === 'performance_optimization') {
      recommendations.push('Enfoque en optimización de rendimiento');
    } else if (strategic_alignment === 'longevity_focus') {
      recommendations.push('Enfoque en bienestar a largo plazo');
    }

    if (communication_style === 'direct') {
      recommendations.push('Comunicación directa y eficiente');
    } else if (communication_style === 'supportive') {
      recommendations.push('Comunicación de apoyo y motivación');
    }

    if (intensity_preference === 'high') {
      recommendations.push('Entrenamientos de alta intensidad');
    } else if (intensity_preference === 'moderate') {
      recommendations.push('Entrenamientos de intensidad moderada');
    }
  }

  return recommendations;
}

function isOptimalTimeForAgent(agentId: string, currentHour: number): boolean {
  const agentOptimalTimes = {
    blaze: [6, 7, 8, 18, 19, 20], // Morning and evening workouts
    nova: [7, 8, 9, 17, 18, 19], // Cardio times
    sage: [6, 7, 8, 9, 21, 22], // Meditation and wisdom times
    wave: [10, 11, 16, 17, 18], // Flow and flexibility times
    luna: [20, 21, 22, 23], // Evening and night
    vox: [9, 10, 11, 14, 15, 16], // Communication peak times
    echo: [8, 9, 10, 19, 20, 21], // Listening and feedback times
    zen: [6, 7, 8, 21, 22, 23], // Meditation times
    apex: [7, 8, 9, 17, 18, 19], // Peak performance times
  };

  const optimalHours = agentOptimalTimes[agentId.toLowerCase() as keyof typeof agentOptimalTimes];
  return optimalHours ? optimalHours.includes(currentHour) : false;
}
