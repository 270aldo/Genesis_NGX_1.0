
import React from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { Agent } from '@/types/agent';

interface EmptyStateProps {
  activeAgent?: Agent;
  onQuickMessage: (message: string) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ activeAgent, onQuickMessage }) => {
  // Get quick messages for active agent
  const getQuickMessages = () => {
    if (!activeAgent) return [];

    const agentSpecificMessages = {
      'blaze': [
        "Diseña mi rutina de hipertrofia",
        "Plan de fuerza personalizado",
        "Análisis biomecánico avanzado",
        "Periodización para ganancia muscular"
      ],
      'sage': [
        "Nutrición de precisión personalizada",
        "Protocolo de suplementación estratégica",
        "Timing nutricional óptimo",
        "Análisis nutrigenómico"
      ],
      'wave': [
        "Análisis HRV profundo",
        "Optimización circadiana",
        "Protocolos de recuperación avanzada",
        "Estrategias de sueño profundo"
      ],
      'luna': [
        "Entrenamiento por ciclos hormonales",
        "Nutrición femenina por fases",
        "Optimización hormonal natural",
        "Salud reproductiva integral"
      ],
      'spark': [
        "Psicología de hábitos duraderos",
        "Sistemas de motivación intrínseca",
        "Superar creencias limitantes",
        "Mentalidad NGX de élite"
      ],
      'stella': [
        "KPIs fisiológicos avanzados",
        "Análisis de progreso integral",
        "Bioestadística personalizada",
        "Dashboard de métricas NGX"
      ],
      'nova': [
        "Protocolos de biohacking cognitivo",
        "Optimización cronobiológica",
        "Stack de nootrópicos personalizados",
        "Tecnologías de optimización"
      ],
      'codex': [
        "Interpretación de test genético",
        "Análisis de polimorfismos",
        "Nutrigenómica personalizada",
        "Protocolo basado en ADN"
      ],
      'nexus': [
        "Crear plan integral NGX",
        "Coordinar todos los agentes",
        "Estrategia de éxito personalizada",
        "Análisis completo multiagente"
      ]
    };

    return agentSpecificMessages[activeAgent.id as keyof typeof agentSpecificMessages] || [];
  };

  const quickMessages = getQuickMessages();

  return (
    <div className="flex-1 flex items-center justify-center relative overflow-hidden chat-scroll-area">
      {/* Floating particles background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-purple-500/20 rounded-full floating-animation"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${3 + Math.random() * 2}s`
            }}
          />
        ))}
      </div>

      <div className="text-center space-y-8 max-w-2xl mx-auto p-8 relative z-10">
        {/* Main icon with premium effects */}
        <div className="relative mx-auto w-20 h-20">
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-purple-500/20 to-violet-500/20 pulse-ring"></div>
          <div className={cn(
            "relative w-20 h-20 rounded-full glass-premium flex items-center justify-center shadow-lg shadow-purple-500/20",
            "bg-gradient-to-br from-purple-600/20 to-violet-600/20 border border-purple-500/30"
          )}>
            <div className="text-2xl">{activeAgent?.avatar || '🧠'}</div>
          </div>
        </div>

        {/* Title and description */}
        <div className="space-y-4">
          <h1 className="text-4xl font-light tracking-tight bg-gradient-to-r from-white via-purple-100 to-violet-100 bg-clip-text text-transparent">
            {activeAgent?.name || 'NGX Agents'}
          </h1>
          <p className="text-lg text-muted-foreground font-light max-w-md mx-auto leading-relaxed">
            {activeAgent?.description || 'Experience the future of AI conversation with advanced agent intelligence.'}
          </p>
        </div>

        {/* Search hint */}
        <div className="text-xs text-white/30 font-light">
          Press Ctrl+F to search conversations
        </div>

        {/* Quick Messages */}
        <div className="flex flex-wrap gap-3 justify-center mt-12">
          {quickMessages.map((message, index) => (
            <Button
              key={index}
              onClick={() => onQuickMessage(message)}
              variant="ghost"
              className="px-6 py-3 text-sm font-medium rounded-full glass-ultra hover:glass-premium transition-all duration-300 border border-purple-500/10 hover:border-purple-500/20 hover:scale-105 shimmer-premium hover:bg-purple-500/5"
            >
              {message}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
};
