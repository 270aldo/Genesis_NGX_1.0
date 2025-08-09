/**
 * Personalized Chat Interface Component
 * Chat interface that adapts messages and responses based on Hybrid Intelligence
 * Integrates real-time personalization with agent conversations
 * NEXUS-ONLY MODE: Routes all agent interactions through NEXUS
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { useHybridIntelligencePersonalization } from '@/hooks/useHybridIntelligencePersonalization';
import { useHybridIntelligenceStore } from '@/store/hybridIntelligenceStore';
import { useFeatureFlags } from '@/hooks/useFeatureFlags';
import { AgentCollaborationIndicator } from '@/components/collaboration';
import { FITNESS_AGENTS } from '@/data/agents';
import {
  Send,
  User,
  Bot,
  Star,
  ThumbsUp,
  ThumbsDown,
  Zap,
  Heart,
  Brain,
  TrendingUp,
  Clock,
  Sparkles,
  Target,
  AlertCircle,
  Users,
  Workflow
} from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  agentId?: string;
  personalizationData?: {
    confidence: number;
    archetypeAlignment: string;
    physiologicalFactors: string[];
    adaptations: string[];
  };
  feedback?: {
    rating: number;
    helpful: boolean;
  };
}

interface PersonalizedChatInterfaceProps {
  agentId: string;
  agentName: string;
  agentIcon: React.ComponentType<{ className?: string }>;
  agentColor: string;
  onClose?: () => void;
  className?: string;
}

interface ActiveAgent {
  id: string;
  name: string;
  avatar: string;
  status: 'consulting' | 'analyzing' | 'responding' | 'completed';
  progress: number;
  task: string;
  startTime: Date;
}

interface CollaborationData {
  activeAgents: ActiveAgent[];
  currentTask: string;
  estimatedTime: number;
}

export const PersonalizedChatInterface: React.FC<PersonalizedChatInterfaceProps> = ({
  agentId,
  agentName,
  agentIcon: AgentIcon,
  agentColor,
  onClose,
  className
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showPersonalizationDetails, setShowPersonalizationDetails] = useState(false);
  const [collaborationData, setCollaborationData] = useState<CollaborationData>({
    activeAgents: [],
    currentTask: '',
    estimatedTime: 0
  });

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    personalizeContent,
    provideFeedback,
    getPersonalizedGreeting,
    checkAgentCompatibility,
    agentAffinity,
    confidenceScore,
    recommendations,
    isOptimalTime
  } = useHybridIntelligencePersonalization();

  const {
    archetype,
    currentBiometrics,
    isArchetypeConfident
  } = useHybridIntelligenceStore();

  const {
    flags,
    isNexusOnlyMode,
    shouldShowCollaboration,
    shouldShowAttribution
  } = useFeatureFlags();

  // Override agentId to use NEXUS in NEXUS-only mode
  const effectiveAgentId = isNexusOnlyMode ? 'nexus' : agentId;
  const effectiveAgentName = isNexusOnlyMode ? 'NEXUS' : agentName;
  const effectiveAgentIcon = isNexusOnlyMode ? Brain : AgentIcon;
  const effectiveAgentColor = isNexusOnlyMode ? 'purple' : agentColor;

  // Get NEXUS data if needed
  const nexusAgent = FITNESS_AGENTS.find(a => a.id === 'nexus');

  // Initialize chat with personalized greeting
  useEffect(() => {
    initializeChat();
  }, [agentId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const initializeChat = async () => {
    try {
      // Get personalized greeting
      const greeting = isNexusOnlyMode
        ? getPersonalizedNexusGreeting()
        : getPersonalizedGreeting(effectiveAgentId);

      // Check compatibility
      const compatibility = checkAgentCompatibility(effectiveAgentId);

      // Create initial messages
      const initialMessages: Message[] = [
        {
          id: 'greeting',
          type: 'agent',
          content: greeting,
          timestamp: new Date().toISOString(),
          agentId: effectiveAgentId,
          personalizationData: {
            confidence: confidenceScore,
            archetypeAlignment: archetype || 'unknown',
            physiologicalFactors: getCurrentPhysiologicalFactors(),
            adaptations: isNexusOnlyMode
              ? ['Modo NEXUS activado', 'Coordinación de equipo habilitada', 'Estilo de comunicación adaptado']
              : ['Saludo personalizado', 'Estilo de comunicación adaptado'],
          }
        }
      ];

      // Add NEXUS-only mode notification
      if (isNexusOnlyMode && agentId !== 'nexus') {
        initialMessages.push({
          id: 'nexus-mode-notification',
          type: 'system',
          content: `🧠 NEXUS está coordinando tu consulta sobre ${getFriendlyAgentName(agentId)}. Tu equipo NGX trabajará en conjunto para darte la mejor respuesta.`,
          timestamp: new Date().toISOString(),
        });
      }

      // Add compatibility warning if needed
      if (!compatibility.compatible) {
        initialMessages.push({
          id: 'compatibility-warning',
          type: 'system',
          content: `⚠️ ${compatibility.reason} - Las recomendaciones pueden ser menos precisas.`,
          timestamp: new Date().toISOString(),
        });
      }

      // Add optimal timing notification
      if (isOptimalTime) {
        initialMessages.push({
          id: 'optimal-timing',
          type: 'system',
          content: '🎯 Este es un momento óptimo para interactuar según tu perfil biométrico.',
          timestamp: new Date().toISOString(),
        });
      }

      setMessages(initialMessages);
    } catch (error) {
      console.error('Failed to initialize chat:', error);

      // Fallback greeting
      setMessages([{
        id: 'fallback-greeting',
        type: 'agent',
        content: `¡Hola! Soy ${effectiveAgentName}. ¿Cómo puedo ayudarte hoy?`,
        timestamp: new Date().toISOString(),
        agentId: effectiveAgentId,
      }]);
    }
  };

  const handleSendMessage = useCallback(async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Simulate collaboration if NEXUS-only mode and asking about specific agent
      if (isNexusOnlyMode && shouldShowCollaboration && agentId !== 'nexus') {
        simulateAgentCollaboration(inputValue.trim());
      }

      // Get personalized response
      const personalizationResult = await personalizeContent({
        agentId: effectiveAgentId,
        requestType: 'general_chat',
        context: {
          timeOfDay: new Date().toISOString(),
          userMessage: inputValue.trim(),
          previousInteractions: messages.slice(-5).map(m => m.content), // Last 5 messages
          currentGoal: 'conversation',
          originalAgentId: agentId, // Pass original agent for context
        },
        priority: 'high',
      });

      if (personalizationResult) {
        const agentResponse: Message = {
          id: `agent-${Date.now()}`,
          type: 'agent',
          content: personalizationResult.personalized_content,
          timestamp: new Date().toISOString(),
          agentId: effectiveAgentId,
          personalizationData: {
            confidence: personalizationResult.confidence_score,
            archetypeAlignment: personalizationResult.archetype_considerations.strategic_alignment,
            physiologicalFactors: extractPhysiologicalFactors(personalizationResult.physiological_modulations),
            adaptations: extractAdaptations(personalizationResult),
          }
        };

        setMessages(prev => [...prev, agentResponse]);

        // Clear collaboration data after response
        if (collaborationData.activeAgents.length > 0) {
          setTimeout(() => {
            setCollaborationData({
              activeAgents: [],
              currentTask: '',
              estimatedTime: 0
            });
          }, 2000);
        }
      }
    } catch (error) {
      console.error('Failed to get personalized response:', error);

      // Fallback response
      const fallbackResponse: Message = {
        id: `agent-fallback-${Date.now()}`,
        type: 'agent',
        content: 'Lo siento, estoy teniendo problemas para procesar tu mensaje. ¿Podrías intentarlo de nuevo?',
        timestamp: new Date().toISOString(),
        agentId: effectiveAgentId,
      };

      setMessages(prev => [...prev, fallbackResponse]);
    } finally {
      setIsTyping(false);
    }
  }, [inputValue, messages, effectiveAgentId, personalizeContent, isNexusOnlyMode, shouldShowCollaboration]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFeedback = async (messageId: string, rating: number, helpful: boolean) => {
    try {
      await provideFeedback({
        interaction_id: messageId,
        user_response: helpful ? 'positive' : 'negative',
        effectiveness_rating: rating,
        feedback_text: helpful ? 'Helpful response' : 'Not helpful',
      });

      // Update message with feedback
      setMessages(prev => prev.map(msg =>
        msg.id === messageId
          ? { ...msg, feedback: { rating, helpful } }
          : msg
      ));
    } catch (error) {
      console.error('Failed to provide feedback:', error);
    }
  };

  const simulateAgentCollaboration = (message: string) => {
    // This would be replaced with real collaboration data from backend
    const relevantAgents = getRelevantAgentsForMessage(message);

    const mockActiveAgents: ActiveAgent[] = relevantAgents.map(agent => ({
      id: agent.id,
      name: agent.name,
      avatar: agent.avatar,
      status: 'consulting' as const,
      progress: Math.random() * 100,
      task: `Analizando tu consulta sobre ${agent.specialty.toLowerCase()}`,
      startTime: new Date()
    }));

    setCollaborationData({
      activeAgents: mockActiveAgents,
      currentTask: 'Coordinando respuesta integral',
      estimatedTime: 15000
    });
  };

  const getCurrentPhysiologicalFactors = (): string[] => {
    if (!currentBiometrics) return [];

    const factors: string[] = [];

    if (currentBiometrics.energy_level !== undefined) {
      factors.push(`Energía: ${Math.round(currentBiometrics.energy_level * 100)}%`);
    }

    if (currentBiometrics.stress_level !== undefined) {
      factors.push(`Estrés: ${Math.round(currentBiometrics.stress_level * 100)}%`);
    }

    if (currentBiometrics.recovery_status !== undefined) {
      factors.push(`Recuperación: ${Math.round(currentBiometrics.recovery_status * 100)}%`);
    }

    return factors;
  };

  const getPersonalizationQuality = (confidence: number) => {
    if (confidence > 0.8) return { label: 'Excelente', color: 'text-green-600' };
    if (confidence > 0.6) return { label: 'Buena', color: 'text-blue-600' };
    if (confidence > 0.4) return { label: 'Moderada', color: 'text-yellow-600' };
    return { label: 'Básica', color: 'text-red-600' };
  };

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* Header */}
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn("p-2 rounded-lg", `bg-${effectiveAgentColor}-100`)}>
              <effectiveAgentIcon className={cn("w-6 h-6", `text-${effectiveAgentColor}-600`)} />
            </div>
            <div>
              <CardTitle className="text-xl">
                {isNexusOnlyMode ? (
                  <div className="flex items-center gap-2">
                    <span>NEXUS</span>
                    <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700 border-purple-200">
                      Director de Orquesta Personal
                    </Badge>
                  </div>
                ) : (
                  effectiveAgentName
                )}
              </CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline" className="text-xs">
                  {archetype || 'Sin arquetipo'}
                </Badge>
                <Badge
                  variant="outline"
                  className={cn("text-xs", getPersonalizationQuality(confidenceScore).color)}
                >
                  {getPersonalizationQuality(confidenceScore).label}
                </Badge>
                {agentAffinity > 0 && (
                  <Badge variant="outline" className="text-xs">
                    {Math.round(agentAffinity * 100)}% afinidad
                  </Badge>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {isNexusOnlyMode && (
              <Badge variant="outline" className="text-xs bg-gradient-to-r from-purple-50 to-indigo-50 text-purple-700 border-purple-200">
                <Users className="w-3 h-3 mr-1" />
                Equipo Coordinado
              </Badge>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowPersonalizationDetails(!showPersonalizationDetails)}
            >
              <Brain className="w-4 h-4" />
            </Button>
            {onClose && (
              <Button variant="ghost" size="sm" onClick={onClose}>
                ×
              </Button>
            )}
          </div>
        </div>

        {/* NEXUS Team Info */}
        {isNexusOnlyMode && agentId !== 'nexus' && (
          <div className="mt-4 p-3 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200">
            <div className="flex items-center gap-2 mb-2">
              <Workflow className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-900">
                Consultando especialidad de {getFriendlyAgentName(agentId)}
              </span>
            </div>
            <p className="text-xs text-purple-700">
              NEXUS está coordinando con tu equipo NGX para darte la respuesta más completa y personalizada.
            </p>
          </div>
        )}

        {/* Collaboration Indicator */}
        {shouldShowCollaboration && collaborationData.activeAgents.length > 0 && (
          <div className="mt-4">
            <AgentCollaborationIndicator
              activeAgents={collaborationData.activeAgents}
              currentTask={collaborationData.currentTask}
              estimatedTime={collaborationData.estimatedTime}
            />
          </div>
        )}

        {/* Personalization Details */}
        {showPersonalizationDetails && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 p-3 bg-gray-50 rounded-lg"
          >
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">Arquetipo:</span> {archetype}
              </div>
              <div>
                <span className="font-medium">Confianza:</span> {Math.round(confidenceScore * 100)}%
              </div>
              <div>
                <span className="font-medium">Momento óptimo:</span> {isOptimalTime ? 'Sí' : 'No'}
              </div>
              <div>
                <span className="font-medium">Afinidad:</span> {Math.round(agentAffinity * 100)}%
              </div>
            </div>

            {recommendations.length > 0 && (
              <div className="mt-3">
                <span className="font-medium">Recomendaciones:</span>
                <ul className="mt-1 space-y-1">
                  {recommendations.slice(0, 3).map((rec, index) => (
                    <li key={index} className="text-xs text-gray-600">• {rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}
      </CardHeader>

      {/* Messages */}
      <CardContent className="flex-1 flex flex-col">
        <ScrollArea ref={scrollAreaRef} className="flex-1 pr-4">
          <div className="space-y-4">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={cn(
                    "flex",
                    message.type === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  <div
                    className={cn(
                      "max-w-[80%] p-3 rounded-lg",
                      message.type === 'user'
                        ? 'bg-blue-500 text-white'
                        : message.type === 'system'
                          ? 'bg-yellow-50 text-yellow-800 border border-yellow-200'
                          : 'bg-gray-100 text-gray-800'
                    )}
                  >
                    {/* Message Header */}
                    <div className="flex items-center gap-2 mb-1">
                      {message.type === 'user' ? (
                        <User className="w-4 h-4" />
                      ) : message.type === 'agent' ? (
                        <Bot className="w-4 h-4" />
                      ) : (
                        <AlertCircle className="w-4 h-4" />
                      )}
                      <span className="text-xs opacity-75">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                    </div>

                    {/* Message Content */}
                    <div className="text-sm">{message.content}</div>

                    {/* Personalization Data */}
                    {message.personalizationData && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <div className="flex items-center gap-2 mb-1">
                          <Sparkles className="w-3 h-3 text-purple-500" />
                          <span className="text-xs font-medium">Personalización</span>
                          <Badge variant="secondary" className="text-xs">
                            {Math.round(message.personalizationData.confidence * 100)}%
                          </Badge>
                        </div>

                        <div className="space-y-1">
                          <div className="text-xs">
                            <span className="font-medium">Arquetipo:</span> {message.personalizationData.archetypeAlignment}
                          </div>

                          {message.personalizationData.physiologicalFactors.length > 0 && (
                            <div className="text-xs">
                              <span className="font-medium">Factores fisiológicos:</span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {message.personalizationData.physiologicalFactors.map((factor, index) => (
                                  <Badge key={index} variant="outline" className="text-xs">
                                    {factor}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}

                          {message.personalizationData.adaptations.length > 0 && (
                            <div className="text-xs">
                              <span className="font-medium">Adaptaciones:</span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {message.personalizationData.adaptations.map((adaptation, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs">
                                    {adaptation}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Feedback Buttons */}
                    {message.type === 'agent' && message.agentId && !message.feedback && (
                      <div className="flex items-center gap-2 mt-2 pt-2 border-t border-gray-200">
                        <span className="text-xs">¿Fue útil?</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleFeedback(message.id, 8, true)}
                          className="h-6 w-6 p-0"
                        >
                          <ThumbsUp className="w-3 h-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleFeedback(message.id, 3, false)}
                          className="h-6 w-6 p-0"
                        >
                          <ThumbsDown className="w-3 h-3" />
                        </Button>
                      </div>
                    )}

                    {/* Feedback Status */}
                    {message.feedback && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <div className="flex items-center gap-2">
                          {message.feedback.helpful ? (
                            <ThumbsUp className="w-3 h-3 text-green-500" />
                          ) : (
                            <ThumbsDown className="w-3 h-3 text-red-500" />
                          )}
                          <span className="text-xs">
                            Feedback enviado - {message.feedback.rating}/10
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Typing Indicator */}
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-start"
              >
                <div className="bg-gray-100 text-gray-800 p-3 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Bot className="w-4 h-4" />
                    <span className="text-sm">{effectiveAgentName} está escribiendo...</span>
                    <div className="flex space-x-1">
                      {[0, 1, 2].map((i) => (
                        <motion.div
                          key={i}
                          className="w-2 h-2 bg-gray-400 rounded-full"
                          animate={{
                            scale: [1, 1.2, 1],
                            opacity: [0.5, 1, 0.5],
                          }}
                          transition={{
                            duration: 1,
                            repeat: Infinity,
                            delay: i * 0.2,
                          }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="flex gap-2 mt-4">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isNexusOnlyMode ? `Escribe tu consulta a NEXUS...` : `Escribe un mensaje a ${effectiveAgentName}...`}
            disabled={isTyping}
            className="flex-1"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isTyping}
            className={cn("px-4", `bg-${effectiveAgentColor}-500 hover:bg-${effectiveAgentColor}-600`)}
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </div>
  );
};

// Helper functions

function getPersonalizedNexusGreeting(): string {
  const greetings = [
    "¡Hola! Soy NEXUS, tu Director de Orquesta Personal. Coordino todo tu equipo NGX para darte respuestas integrales.",
    "¡Bienvenido! NEXUS aquí. Tengo a tu disposición todo el equipo de especialistas NGX. ¿En qué puedo coordinar para ayudarte?",
    "¡Hola! Soy NEXUS, coordinando tu equipo personal de 11 especialistas. Juntos lograremos tus objetivos de forma más eficiente."
  ];
  return greetings[Math.floor(Math.random() * greetings.length)];
}

function getFriendlyAgentName(agentId: string): string {
  const agent = FITNESS_AGENTS.find(a => a.id === agentId);
  return agent ? agent.name : agentId.toUpperCase();
}

function getRelevantAgentsForMessage(message: string): any[] {
  const lowerMessage = message.toLowerCase();
  const relevantAgents = [];

  if (lowerMessage.includes('entrenam') || lowerMessage.includes('ejercicio') || lowerMessage.includes('músculo')) {
    relevantAgents.push(FITNESS_AGENTS.find(a => a.id === 'blaze'));
  }

  if (lowerMessage.includes('nutrición') || lowerMessage.includes('comida') || lowerMessage.includes('diet')) {
    relevantAgents.push(FITNESS_AGENTS.find(a => a.id === 'sage'));
  }

  if (lowerMessage.includes('sueño') || lowerMessage.includes('descanso') || lowerMessage.includes('recuper')) {
    relevantAgents.push(FITNESS_AGENTS.find(a => a.id === 'wave'));
  }

  if (lowerMessage.includes('mujer') || lowerMessage.includes('ciclo') || lowerMessage.includes('hormona')) {
    relevantAgents.push(FITNESS_AGENTS.find(a => a.id === 'luna'));
  }

  return relevantAgents.filter(Boolean).slice(0, 3); // Max 3 agents
}

function extractPhysiologicalFactors(physiologicalModulations: any): string[] {
  const factors: string[] = [];

  if (physiologicalModulations.energy_level_factor !== undefined) {
    factors.push(`Energía: ${Math.round(physiologicalModulations.energy_level_factor * 100)}%`);
  }

  if (physiologicalModulations.stress_level_factor !== undefined) {
    factors.push(`Estrés: ${Math.round(physiologicalModulations.stress_level_factor * 100)}%`);
  }

  if (physiologicalModulations.recovery_status_factor !== undefined) {
    factors.push(`Recuperación: ${Math.round(physiologicalModulations.recovery_status_factor * 100)}%`);
  }

  return factors;
}

function extractAdaptations(personalizationResult: any): string[] {
  const adaptations: string[] = [];

  if (personalizationResult.archetype_considerations.communication_style) {
    adaptations.push(`Comunicación ${personalizationResult.archetype_considerations.communication_style}`);
  }

  if (personalizationResult.archetype_considerations.intensity_preference) {
    adaptations.push(`Intensidad ${personalizationResult.archetype_considerations.intensity_preference}`);
  }

  if (personalizationResult.physiological_modulations.energy_level_factor > 0.7) {
    adaptations.push('Ajuste por alta energía');
  }

  if (personalizationResult.physiological_modulations.stress_level_factor > 0.7) {
    adaptations.push('Ajuste por estrés elevado');
  }

  return adaptations;
}
