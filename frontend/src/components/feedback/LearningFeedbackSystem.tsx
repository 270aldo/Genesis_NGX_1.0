/**
 * Learning Feedback System Component
 * Continuous improvement system for Hybrid Intelligence Engine
 * Collects user feedback to enhance personalization accuracy
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import { cn } from '@/lib/utils';
import { useHybridIntelligencePersonalization } from '@/hooks/useHybridIntelligencePersonalization';
import { useHybridIntelligenceStore } from '@/store/hybridIntelligenceStore';
import { type LearningFeedback } from '@/services/api/hybridIntelligence.service';
import {
  ThumbsUp,
  ThumbsDown,
  Star,
  TrendingUp,
  Target,
  Brain,
  Heart,
  Zap,
  MessageSquare,
  CheckCircle,
  AlertCircle,
  RotateCcw,
  Send,
  Lightbulb,
  Award,
  Clock
} from 'lucide-react';

interface FeedbackPrompt {
  id: string;
  type: 'interaction_rating' | 'personalization_accuracy' | 'agent_performance' | 'general_satisfaction';
  title: string;
  description: string;
  agentId?: string;
  interactionId?: string;
  context?: {
    message?: string;
    recommendation?: string;
    timing?: string;
  };
  priority: 'low' | 'medium' | 'high';
  expiresAt: string;
}

interface LearningFeedbackSystemProps {
  className?: string;
  autoPrompt?: boolean; // Show feedback prompts automatically
  showStats?: boolean; // Show feedback statistics
}

export const LearningFeedbackSystem: React.FC<LearningFeedbackSystemProps> = ({
  className,
  autoPrompt = true,
  showStats = true
}) => {
  const [currentPrompt, setCurrentPrompt] = useState<FeedbackPrompt | null>(null);
  const [feedbackQueue, setFeedbackQueue] = useState<FeedbackPrompt[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackData, setFeedbackData] = useState<Partial<LearningFeedback>>({});
  const [statistics, setStatistics] = useState({
    totalFeedback: 0,
    averageRating: 0,
    improvementTrend: 0,
    lastFeedback: null as string | null,
  });

  const { provideFeedback } = useHybridIntelligencePersonalization();
  const { 
    learningFeedback, 
    recentPersonalizations, 
    adaptationHistory,
    getPersonalizationEffectiveness 
  } = useHybridIntelligenceStore();

  // Generate feedback prompts based on interactions
  useEffect(() => {
    if (autoPrompt) {
      generateFeedbackPrompts();
    }
  }, [recentPersonalizations, adaptationHistory, autoPrompt]);

  // Update statistics when feedback changes
  useEffect(() => {
    updateStatistics();
  }, [learningFeedback]);

  // Process feedback queue
  useEffect(() => {
    if (feedbackQueue.length > 0 && !currentPrompt) {
      const nextPrompt = feedbackQueue.find(p => new Date(p.expiresAt) > new Date());
      if (nextPrompt) {
        setCurrentPrompt(nextPrompt);
        setFeedbackQueue(prev => prev.filter(p => p.id !== nextPrompt.id));
      }
    }
  }, [feedbackQueue, currentPrompt]);

  const generateFeedbackPrompts = useCallback(() => {
    const prompts: FeedbackPrompt[] = [];
    const now = new Date();
    const expirationTime = new Date(now.getTime() + 30 * 60 * 1000); // 30 minutes

    // Check recent personalizations for feedback opportunities
    recentPersonalizations.forEach((personalization, index) => {
      if (index < 3) { // Only check last 3 personalizations
        const agentId = personalization.metadata?.agentId;
        const interactionId = `personalization_${personalization.metadata?.timestamp || Date.now()}`;
        
        // Don't prompt if we already have feedback for this interaction
        const hasFeedback = learningFeedback.some(f => f.interaction_id === interactionId);
        
        if (!hasFeedback && agentId) {
          prompts.push({
            id: `rating_${interactionId}`,
            type: 'interaction_rating',
            title: `¿Cómo fue tu interacción con ${agentId.toUpperCase()}?`,
            description: 'Tu feedback nos ayuda a mejorar la personalización',
            agentId,
            interactionId,
            context: {
              message: personalization.personalized_content?.substring(0, 100) + '...',
            },
            priority: personalization.confidence_score > 0.8 ? 'high' : 'medium',
            expiresAt: expirationTime.toISOString(),
          });
        }
      }
    });

    // Check for general satisfaction feedback (once per day)
    const lastGeneralFeedback = learningFeedback
      .filter(f => f.feedback_text?.includes('general_satisfaction'))
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0];
    
    const shouldPromptGeneral = !lastGeneralFeedback || 
      new Date().getTime() - new Date(lastGeneralFeedback.timestamp).getTime() > 24 * 60 * 60 * 1000;
    
    if (shouldPromptGeneral && learningFeedback.length >= 3) {
      prompts.push({
        id: 'general_satisfaction',
        type: 'general_satisfaction',
        title: '¿Cómo ha sido tu experiencia general con NGX Agents?',
        description: 'Ayúdanos a entender qué funciona bien y qué podemos mejorar',
        priority: 'low',
        expiresAt: expirationTime.toISOString(),
      });
    }

    // Add prompts to queue (avoid duplicates)
    setFeedbackQueue(prev => {
      const existingIds = prev.map(p => p.id);
      const newPrompts = prompts.filter(p => !existingIds.includes(p.id));
      return [...prev, ...newPrompts];
    });
  }, [recentPersonalizations, learningFeedback]);

  const updateStatistics = useCallback(() => {
    const total = learningFeedback.length;
    const avgRating = total > 0 
      ? learningFeedback.reduce((sum, f) => sum + f.effectiveness_rating, 0) / total 
      : 0;
    
    // Calculate improvement trend (last 5 vs previous 5)
    const recent = learningFeedback.slice(0, 5);
    const previous = learningFeedback.slice(5, 10);
    
    const recentAvg = recent.length > 0 
      ? recent.reduce((sum, f) => sum + f.effectiveness_rating, 0) / recent.length 
      : 0;
    const previousAvg = previous.length > 0 
      ? previous.reduce((sum, f) => sum + f.effectiveness_rating, 0) / previous.length 
      : 0;
    
    const trend = previous.length > 0 ? ((recentAvg - previousAvg) / previousAvg) * 100 : 0;
    
    setStatistics({
      totalFeedback: total,
      averageRating: avgRating,
      improvementTrend: trend,
      lastFeedback: learningFeedback[0]?.timestamp || null,
    });
  }, [learningFeedback]);

  const handleQuickFeedback = async (rating: number, helpful: boolean) => {
    if (!currentPrompt) return;
    
    setIsSubmitting(true);
    
    try {
      const feedback: Omit<LearningFeedback, 'timestamp'> = {
        interaction_id: currentPrompt.interactionId || currentPrompt.id,
        user_response: helpful ? 'positive' : 'negative',
        effectiveness_rating: rating,
        feedback_text: `Quick feedback: ${helpful ? 'helpful' : 'not helpful'} (${rating}/10)`,
      };
      
      await provideFeedback(feedback);
      setCurrentPrompt(null);
    } catch (error) {
      console.error('Failed to submit quick feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDetailedFeedback = async () => {
    if (!currentPrompt || !feedbackData.effectiveness_rating) return;
    
    setIsSubmitting(true);
    
    try {
      const feedback: Omit<LearningFeedback, 'timestamp'> = {
        interaction_id: currentPrompt.interactionId || currentPrompt.id,
        user_response: feedbackData.user_response || 'neutral',
        effectiveness_rating: feedbackData.effectiveness_rating,
        feedback_text: feedbackData.feedback_text || 'Detailed feedback provided',
      };
      
      await provideFeedback(feedback);
      setCurrentPrompt(null);
      setShowFeedbackForm(false);
      setFeedbackData({});
    } catch (error) {
      console.error('Failed to submit detailed feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const dismissPrompt = () => {
    setCurrentPrompt(null);
    setShowFeedbackForm(false);
  };

  const skipAllFeedback = () => {
    setCurrentPrompt(null);
    setFeedbackQueue([]);
    setShowFeedbackForm(false);
  };

  const getRatingColor = (rating: number) => {
    if (rating >= 8) return 'text-green-600';
    if (rating >= 6) return 'text-blue-600';
    if (rating >= 4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTrendColor = (trend: number) => {
    if (trend > 5) return 'text-green-600';
    if (trend > -5) return 'text-blue-600';
    return 'text-red-600';
  };

  return (
    <div className={cn("space-y-6", className)}>
      {/* Statistics */}
      {showStats && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Estadísticas de Aprendizaje
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {statistics.totalFeedback}
                </div>
                <div className="text-sm text-gray-600">Total Feedback</div>
              </div>
              
              <div className="text-center">
                <div className={cn("text-2xl font-bold", getRatingColor(statistics.averageRating))}>
                  {statistics.averageRating.toFixed(1)}/10
                </div>
                <div className="text-sm text-gray-600">Rating Promedio</div>
              </div>
              
              <div className="text-center">
                <div className={cn("text-2xl font-bold", getTrendColor(statistics.improvementTrend))}>
                  {statistics.improvementTrend > 0 ? '+' : ''}{statistics.improvementTrend.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Tendencia</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round(getPersonalizationEffectiveness() * 100)}%
                </div>
                <div className="text-sm text-gray-600">Efectividad</div>
              </div>
            </div>
            
            {statistics.lastFeedback && (
              <div className="mt-4 text-sm text-gray-500 text-center">
                Último feedback: {new Date(statistics.lastFeedback).toLocaleDateString()}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Feedback Queue Indicator */}
      {feedbackQueue.length > 0 && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-blue-600" />
                <span className="text-blue-800">
                  {feedbackQueue.length} feedback{feedbackQueue.length !== 1 ? 's' : ''} pendiente{feedbackQueue.length !== 1 ? 's' : ''}
                </span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPrompt(feedbackQueue[0])}
              >
                Responder
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Active Feedback Prompt */}
      <AnimatePresence>
        {currentPrompt && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-purple-600" />
                    <CardTitle className="text-purple-800">
                      {currentPrompt.title}
                    </CardTitle>
                  </div>
                  <Badge variant="outline" className={cn(
                    "text-xs",
                    currentPrompt.priority === 'high' ? 'border-red-300 text-red-700' :
                    currentPrompt.priority === 'medium' ? 'border-yellow-300 text-yellow-700' :
                    'border-blue-300 text-blue-700'
                  )}>
                    {currentPrompt.priority}
                  </Badge>
                </div>
                <p className="text-purple-700">{currentPrompt.description}</p>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Context Information */}
                {currentPrompt.context && (
                  <div className="p-3 bg-white/50 rounded-lg">
                    {currentPrompt.agentId && (
                      <div className="flex items-center gap-2 mb-2">
                        <Bot className="w-4 h-4 text-gray-600" />
                        <span className="text-sm font-medium">
                          Agente: {currentPrompt.agentId.toUpperCase()}
                        </span>
                      </div>
                    )}
                    {currentPrompt.context.message && (
                      <div className="text-sm text-gray-700 italic">
                        "{currentPrompt.context.message}"
                      </div>
                    )}
                  </div>
                )}
                
                {!showFeedbackForm ? (
                  /* Quick Feedback */
                  <div className="space-y-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-600 mb-4">
                        ¿Qué tan útil fue esta interacción?
                      </p>
                      
                      <div className="flex justify-center gap-2 mb-4">
                        {[1, 2, 3, 4, 5].map((rating) => (
                          <Button
                            key={rating}
                            variant="outline"
                            size="sm"
                            onClick={() => handleQuickFeedback(rating * 2, rating >= 3)}
                            disabled={isSubmitting}
                            className="flex items-center gap-1"
                          >
                            <Star className={cn(
                              "w-4 h-4",
                              rating <= 2 ? "text-red-500" :
                              rating <= 3 ? "text-yellow-500" :
                              "text-green-500"
                            )} />
                            {rating * 2}
                          </Button>
                        ))}
                      </div>
                      
                      <div className="flex justify-center gap-2">
                        <Button
                          variant="outline"
                          onClick={() => handleQuickFeedback(8, true)}
                          disabled={isSubmitting}
                          className="flex items-center gap-2"
                        >
                          <ThumbsUp className="w-4 h-4 text-green-600" />
                          Útil
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => handleQuickFeedback(3, false)}
                          disabled={isSubmitting}
                          className="flex items-center gap-2"
                        >
                          <ThumbsDown className="w-4 h-4 text-red-600" />
                          No útil
                        </Button>
                      </div>
                    </div>
                    
                    <div className="flex justify-center gap-2 pt-4 border-t">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowFeedbackForm(true)}
                      >
                        Feedback Detallado
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={dismissPrompt}
                      >
                        Saltar
                      </Button>
                    </div>
                  </div>
                ) : (
                  /* Detailed Feedback Form */
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        Rating de Efectividad (1-10)
                      </label>
                      <Slider
                        value={[feedbackData.effectiveness_rating || 5]}
                        onValueChange={([value]) => 
                          setFeedbackData(prev => ({ ...prev, effectiveness_rating: value }))
                        }
                        max={10}
                        min={1}
                        step={1}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>No útil (1)</span>
                        <span className="font-medium">
                          {feedbackData.effectiveness_rating || 5}/10
                        </span>
                        <span>Muy útil (10)</span>
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        ¿Fue una experiencia positiva?
                      </label>
                      <div className="flex gap-2">
                        <Button
                          variant={feedbackData.user_response === 'positive' ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => 
                            setFeedbackData(prev => ({ ...prev, user_response: 'positive' }))
                          }
                        >
                          <ThumbsUp className="w-4 h-4 mr-2" />
                          Positiva
                        </Button>
                        <Button
                          variant={feedbackData.user_response === 'neutral' ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => 
                            setFeedbackData(prev => ({ ...prev, user_response: 'neutral' }))
                          }
                        >
                          Neutral
                        </Button>
                        <Button
                          variant={feedbackData.user_response === 'negative' ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => 
                            setFeedbackData(prev => ({ ...prev, user_response: 'negative' }))
                          }
                        >
                          <ThumbsDown className="w-4 h-4 mr-2" />
                          Negativa
                        </Button>
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        Comentarios adicionales (opcional)
                      </label>
                      <Textarea
                        value={feedbackData.feedback_text || ''}
                        onChange={(e) => 
                          setFeedbackData(prev => ({ ...prev, feedback_text: e.target.value }))
                        }
                        placeholder="¿Qué funcionó bien? ¿Qué podría mejorar?"
                        rows={3}
                      />
                    </div>
                    
                    <div className="flex justify-between pt-4 border-t">
                      <Button
                        variant="outline"
                        onClick={() => setShowFeedbackForm(false)}
                      >
                        Volver
                      </Button>
                      <Button
                        onClick={handleDetailedFeedback}
                        disabled={isSubmitting || !feedbackData.effectiveness_rating}
                        className="flex items-center gap-2"
                      >
                        {isSubmitting ? (
                          <RotateCcw className="w-4 h-4 animate-spin" />
                        ) : (
                          <Send className="w-4 h-4" />
                        )}
                        Enviar Feedback
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Manual Feedback Trigger */}
      {!currentPrompt && feedbackQueue.length === 0 && (
        <Card className="border-dashed border-gray-300">
          <CardContent className="pt-6">
            <div className="text-center">
              <Lightbulb className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <h3 className="font-semibold text-gray-700 mb-2">
                ¿Tienes feedback para nosotros?
              </h3>
              <p className="text-gray-500 text-sm mb-4">
                Tu feedback nos ayuda a mejorar la personalización del sistema
              </p>
              <Button
                variant="outline"
                onClick={() => {
                  setCurrentPrompt({
                    id: 'manual_feedback',
                    type: 'general_satisfaction',
                    title: 'Comparte tu feedback',
                    description: 'Ayúdanos a mejorar tu experiencia',
                    priority: 'medium',
                    expiresAt: new Date(Date.now() + 60 * 60 * 1000).toISOString(),
                  });
                  setShowFeedbackForm(true);
                }}
              >
                Dar Feedback
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};