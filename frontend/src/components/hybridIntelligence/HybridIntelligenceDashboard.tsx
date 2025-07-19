/**
 * Hybrid Intelligence Dashboard
 * Comprehensive dashboard for revolutionary 2-layer personalization system
 * Displays archetype analysis, physiological insights, and personalization effectiveness
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { useHybridIntelligenceStore } from '@/store/hybridIntelligenceStore';
import { 
  Brain, 
  Target, 
  Activity, 
  TrendingUp, 
  Zap, 
  Heart, 
  Shield, 
  BarChart3,
  RefreshCw,
  Star,
  Clock,
  Users,
  Award,
  AlertCircle,
  CheckCircle,
  Settings
} from 'lucide-react';

interface HybridIntelligenceDashboardProps {
  className?: string;
}

export const HybridIntelligenceDashboard: React.FC<HybridIntelligenceDashboardProps> = ({
  className
}) => {
  const {
    profile,
    insights,
    archetype,
    confidenceScore,
    adaptationCount,
    currentBiometrics,
    biomarkers,
    isLoading,
    error,
    loadProfile,
    loadInsights,
    isArchetypeConfident,
    getBioDataQuality,
    getPersonalizationEffectiveness,
    getRecommendedAgents,
    getPersonalizedGreeting,
    getOptimalTiming,
    clearError
  } = useHybridIntelligenceStore();

  const [activeTab, setActiveTab] = useState('overview');

  // Load data on mount
  useEffect(() => {
    if (!profile) {
      loadProfile();
    }
    if (!insights) {
      loadInsights();
    }
  }, [profile, insights, loadProfile, loadInsights]);

  // Get archetype display information
  const getArchetypeDisplay = () => {
    if (!archetype) return null;
    
    if (archetype === 'PRIME') {
      return {
        color: 'from-orange-500 to-red-500',
        bgColor: 'bg-orange-50 border-orange-200',
        textColor: 'text-orange-700',
        icon: Zap,
        label: 'PRIME',
        description: 'Optimizador de rendimiento y eficiencia',
        traits: ['Orientado a resultados', 'Competitivo', 'Eficiente', 'Ambicioso']
      };
    } else {
      return {
        color: 'from-green-500 to-emerald-500',
        bgColor: 'bg-green-50 border-green-200',
        textColor: 'text-green-700',
        icon: Heart,
        label: 'LONGEVITY',
        description: 'Arquitecto de bienestar sostenible',
        traits: ['Preventivo', 'Sostenible', 'Holístico', 'Equilibrado']
      };
    }
  };

  const archetypeDisplay = getArchetypeDisplay();
  const bioDataQuality = getBioDataQuality();
  const personalizationEffectiveness = getPersonalizationEffectiveness();
  const recommendedAgents = getRecommendedAgents();
  const personalizedGreeting = getPersonalizedGreeting();
  const optimalTiming = getOptimalTiming();

  if (isLoading) {
    return (
      <Card className={cn("p-8", className)}>
        <div className="flex items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mr-3" />
          <span className="text-lg">Cargando Hybrid Intelligence...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={cn("p-8", className)}>
        <div className="text-center">
          <AlertCircle className="w-16 h-16 mx-auto text-red-500 mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            Error en Hybrid Intelligence
          </h3>
          <p className="text-gray-500 mb-4">{error}</p>
          <Button onClick={clearError} variant="outline">
            Intentar de nuevo
          </Button>
        </div>
      </Card>
    );
  }

  if (!profile) {
    return (
      <Card className={cn("p-8", className)}>
        <div className="text-center">
          <Brain className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            Hybrid Intelligence No Configurado
          </h3>
          <p className="text-gray-500 mb-4">
            Configura tu perfil de Hybrid Intelligence para obtener personalización revolucionaria.
          </p>
          <Button>
            Configurar Perfil
          </Button>
        </div>
      </Card>
    );
  }

  const ArchetypeIcon = archetypeDisplay?.icon || Brain;

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header with Personalized Greeting */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">
                Hybrid Intelligence Engine
              </h2>
              <p className="text-gray-600 mt-1">{personalizedGreeting}</p>
            </div>
            <div className="flex items-center gap-3">
              <Badge 
                className={cn("bg-gradient-to-r text-white", archetypeDisplay?.color)}
              >
                {archetypeDisplay?.label}
              </Badge>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Configurar
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Main Dashboard */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Resumen</TabsTrigger>
          <TabsTrigger value="archetype">Arquetipo</TabsTrigger>
          <TabsTrigger value="biometrics">Biometría</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6 text-center">
                <Brain className="w-8 h-8 mx-auto text-purple-500 mb-2" />
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round(confidenceScore * 100)}%
                </div>
                <div className="text-sm text-gray-600">Confianza del Perfil</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <Activity className="w-8 h-8 mx-auto text-blue-500 mb-2" />
                <div className="text-2xl font-bold text-blue-600">
                  {Math.round(bioDataQuality * 100)}%
                </div>
                <div className="text-sm text-gray-600">Calidad Bio-datos</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <TrendingUp className="w-8 h-8 mx-auto text-green-500 mb-2" />
                <div className="text-2xl font-bold text-green-600">
                  {Math.round(personalizationEffectiveness * 100)}%
                </div>
                <div className="text-sm text-gray-600">Efectividad</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <RefreshCw className="w-8 h-8 mx-auto text-orange-500 mb-2" />
                <div className="text-2xl font-bold text-orange-600">
                  {adaptationCount}
                </div>
                <div className="text-sm text-gray-600">Adaptaciones</div>
              </CardContent>
            </Card>
          </div>

          {/* Current Status */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Archetype Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ArchetypeIcon className="w-5 h-5" />
                  Arquetipo Actual
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={cn("p-4 rounded-lg mb-4", archetypeDisplay?.bgColor)}>
                  <div className="flex items-center gap-3 mb-2">
                    <ArchetypeIcon className={cn("w-6 h-6", archetypeDisplay?.textColor)} />
                    <span className={cn("font-semibold", archetypeDisplay?.textColor)}>
                      {archetypeDisplay?.label}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      {isArchetypeConfident() ? 'Alta confianza' : 'Confianza media'}
                    </Badge>
                  </div>
                  <p className={cn("text-sm", archetypeDisplay?.textColor)}>
                    {archetypeDisplay?.description}
                  </p>
                </div>
                
                <div className="space-y-2">
                  <h4 className="font-medium text-gray-700">Rasgos principales:</h4>
                  <div className="flex flex-wrap gap-2">
                    {archetypeDisplay?.traits.map((trait, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {trait}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recommended Agents */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Agentes Recomendados
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recommendedAgents.slice(0, 3).map((agentId, index) => (
                    <div key={agentId} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                          {agentId.charAt(0).toUpperCase()}
                        </div>
                        <span className="font-medium">{agentId.toUpperCase()}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex">
                          {[...Array(5)].map((_, i) => (
                            <Star 
                              key={i} 
                              className={cn(
                                "w-4 h-4",
                                i < (5 - index) ? "text-yellow-400 fill-current" : "text-gray-300"
                              )} 
                            />
                          ))}
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {index === 0 ? 'Óptimo' : index === 1 ? 'Muy bueno' : 'Bueno'}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Optimal Timing */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Recomendaciones de Timing Óptimo
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3">
                {optimalTiming.map((recommendation, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <CheckCircle className="w-5 h-5 text-blue-500" />
                    <span className="text-blue-700">{recommendation}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Archetype Tab */}
        <TabsContent value="archetype" className="space-y-6">
          {insights && (
            <Card>
              <CardHeader>
                <CardTitle>Análisis Detallado del Arquetipo</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Confidence Score */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">Confianza del Arquetipo</span>
                      <span className="text-sm text-gray-600">
                        {Math.round(insights.archetype_analysis.confidence * 100)}%
                      </span>
                    </div>
                    <Progress value={insights.archetype_analysis.confidence * 100} className="h-2" />
                  </div>

                  {/* Primary Traits */}
                  <div>
                    <h4 className="font-medium mb-3">Rasgos Primarios</h4>
                    <div className="grid gap-2">
                      {insights.archetype_analysis.primary_traits.map((trait, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <Star className="w-4 h-4 text-yellow-500" />
                          <span className="text-gray-700">{trait}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Behavioral Patterns */}
                  <div>
                    <h4 className="font-medium mb-3">Patrones de Comportamiento</h4>
                    <div className="grid gap-2">
                      {insights.archetype_analysis.behavioral_patterns.map((pattern, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <TrendingUp className="w-4 h-4 text-blue-500" />
                          <span className="text-gray-700">{pattern}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Optimization Opportunities */}
                  <div>
                    <h4 className="font-medium mb-3">Oportunidades de Optimización</h4>
                    <div className="grid gap-2">
                      {insights.archetype_analysis.optimization_opportunities.map((opportunity, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <Target className="w-4 h-4 text-green-500" />
                          <span className="text-gray-700">{opportunity}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Biometrics Tab */}
        <TabsContent value="biometrics" className="space-y-6">
          {/* Current Biometrics */}
          <Card>
            <CardHeader>
              <CardTitle>Datos Biométricos Actuales</CardTitle>
            </CardHeader>
            <CardContent>
              {currentBiometrics ? (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(currentBiometrics).map(([key, value]) => {
                    if (value === undefined || value === null) return null;
                    
                    const getMetricDisplay = (metric: string, val: number) => {
                      switch (metric) {
                        case 'sleep_quality':
                          return { label: 'Calidad del Sueño', value: `${Math.round(val * 100)}%`, color: val > 0.7 ? 'text-green-600' : val > 0.4 ? 'text-yellow-600' : 'text-red-600' };
                        case 'sleep_duration':
                          return { label: 'Duración del Sueño', value: `${val.toFixed(1)}h`, color: val > 7 ? 'text-green-600' : val > 5 ? 'text-yellow-600' : 'text-red-600' };
                        case 'stress_level':
                          return { label: 'Nivel de Estrés', value: `${Math.round(val * 100)}%`, color: val < 0.3 ? 'text-green-600' : val < 0.7 ? 'text-yellow-600' : 'text-red-600' };
                        case 'energy_level':
                          return { label: 'Nivel de Energía', value: `${Math.round(val * 100)}%`, color: val > 0.7 ? 'text-green-600' : val > 0.4 ? 'text-yellow-600' : 'text-red-600' };
                        case 'recovery_status':
                          return { label: 'Estado de Recuperación', value: `${Math.round(val * 100)}%`, color: val > 0.7 ? 'text-green-600' : val > 0.4 ? 'text-yellow-600' : 'text-red-600' };
                        case 'heart_rate_variability':
                          return { label: 'HRV', value: `${Math.round(val)}ms`, color: 'text-blue-600' };
                        case 'resting_heart_rate':
                          return { label: 'FC Reposo', value: `${Math.round(val)} bpm`, color: 'text-purple-600' };
                        case 'readiness_score':
                          return { label: 'Puntuación Readiness', value: `${Math.round(val)}`, color: val > 70 ? 'text-green-600' : val > 40 ? 'text-yellow-600' : 'text-red-600' };
                        default:
                          return { label: metric, value: val.toString(), color: 'text-gray-600' };
                      }
                    };
                    
                    const display = getMetricDisplay(key, value as number);
                    
                    return (
                      <div key={key} className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className={cn("text-2xl font-bold", display.color)}>
                          {display.value}
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          {display.label}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Activity className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-500">No hay datos biométricos disponibles</p>
                  <Button className="mt-4" variant="outline">
                    Conectar Dispositivo
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Biomarkers */}
          {biomarkers && (
            <Card>
              <CardHeader>
                <CardTitle>Biomarcadores</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.entries(biomarkers).map(([key, value]) => {
                    if (value === undefined || value === null || key === 'last_updated') return null;
                    
                    return (
                      <div key={key} className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className="text-xl font-bold text-blue-600">
                          {typeof value === 'number' ? value.toFixed(1) : value}
                        </div>
                        <div className="text-sm text-gray-600 mt-1 capitalize">
                          {key.replace('_', ' ')}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights" className="space-y-6">
          {insights && (
            <>
              {/* Physiological Insights */}
              <Card>
                <CardHeader>
                  <CardTitle>Insights Fisiológicos</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Patrones de Recuperación</h4>
                      <div className="space-y-1">
                        {insights.physiological_insights.recovery_patterns.map((pattern, index) => (
                          <div key={index} className="text-sm text-gray-600">• {pattern}</div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Indicadores de Rendimiento</h4>
                      <div className="space-y-1">
                        {insights.physiological_insights.performance_indicators.map((indicator, index) => (
                          <div key={index} className="text-sm text-gray-600">• {indicator}</div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Recomendaciones de Salud</h4>
                      <div className="space-y-1">
                        {insights.physiological_insights.health_recommendations.map((recommendation, index) => (
                          <div key={index} className="text-sm text-gray-600">• {recommendation}</div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Predictive Insights */}
              <Card>
                <CardHeader>
                  <CardTitle>Insights Predictivos</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium">Probabilidad de Logro de Objetivos</span>
                        <span className="text-lg font-bold text-green-600">
                          {Math.round(insights.predictive_insights.goal_achievement_probability * 100)}%
                        </span>
                      </div>
                      <Progress value={insights.predictive_insights.goal_achievement_probability * 100} className="h-2" />
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Factores de Éxito</h4>
                      <div className="space-y-1">
                        {insights.predictive_insights.success_factors.map((factor, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            <span className="text-sm text-gray-600">{factor}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Factores de Riesgo</h4>
                      <div className="space-y-1">
                        {insights.predictive_insights.risk_factors.map((factor, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <AlertCircle className="w-4 h-4 text-yellow-500" />
                            <span className="text-sm text-gray-600">{factor}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};