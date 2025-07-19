
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { useAgentStore } from '@/store/agentStore';
import { cn } from '@/lib/utils';
import { Zap, ChevronDown, ChevronUp } from 'lucide-react';

interface QuickMessagesProps {
  onSelectMessage: (message: string) => void;
}

export const QuickMessages: React.FC<QuickMessagesProps> = ({ onSelectMessage }) => {
  const { getActiveAgent } = useAgentStore();
  const activeAgent = getActiveAgent();
  const [isExpanded, setIsExpanded] = useState(false);

  const getQuickMessages = () => {
    if (!activeAgent) return [];

    const commonMessages = [
      "¿Cómo puedo empezar?",
      "Dame una recomendación",
      "Explícame los fundamentos",
      "¿Cuál es el siguiente paso?"
    ];

    const agentSpecificMessages = {
      'training-strategist': [
        "Diseña un plan de entrenamiento para principiantes",
        "¿Cómo mejoro mi fuerza?",
        "Rutina para ganar músculo",
        "Ejercicios para quemar grasa",
        "¿Cómo evitar lesiones?",
        "Plan de entrenamiento en casa"
      ],
      'nutrition-architect': [
        "Calcula mis macros diarios",
        "Plan de comidas para ganar músculo",
        "¿Qué suplementos necesito?",
        "Dieta para bajar de peso",
        "Recetas saludables y fáciles",
        "¿Cuánta agua debo tomar?"
      ],
      'biometrics-engine': [
        "Analiza mis métricas de sueño",
        "¿Cómo mejorar mi recuperación?",
        "Interpreta mi variabilidad cardíaca",
        "Optimiza mis horarios de entrenamiento",
        "¿Qué indican mis niveles de estrés?",
        "Configura mis objetivos de pasos"
      ],
      'orchestrator': [
        "Crea un plan integral de fitness",
        "Coordina mis objetivos",
        "¿Qué agente necesito para esto?",
        "Plan completo de transformación",
        "Optimiza toda mi rutina",
        "Análisis completo de mi progreso"
      ]
    };

    const specific = agentSpecificMessages[activeAgent.id as keyof typeof agentSpecificMessages] || [];
    return [...commonMessages, ...specific];
  };

  const quickMessages = getQuickMessages();

  return (
    <div className="border-b border-white/5 bg-white/5 backdrop-blur-xl">
      <div className="px-4 py-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-white/80">Mensajes Rápidos</span>
            <Badge variant="secondary" className="bg-blue-500/20 text-blue-300 text-xs">
              {quickMessages.length}
            </Badge>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-white/60 hover:text-white hover:bg-white/10 h-6 px-2"
          >
            {isExpanded ? (
              <ChevronUp className="w-3 h-3" />
            ) : (
              <ChevronDown className="w-3 h-3" />
            )}
          </Button>
        </div>

        <div className={cn(
          "transition-all duration-300 ease-in-out overflow-hidden",
          isExpanded ? "max-h-48 opacity-100" : "max-h-12 opacity-100"
        )}>
          <ScrollArea className="w-full">
            <div className={cn(
              "gap-2",
              isExpanded ? "grid grid-cols-1 sm:grid-cols-2" : "flex overflow-x-auto pb-2"
            )}>
              {quickMessages.slice(0, isExpanded ? quickMessages.length : 6).map((message, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  size="sm"
                  onClick={() => onSelectMessage(message)}
                  className={cn(
                    "transition-all duration-200 rounded-lg text-left justify-start",
                    isExpanded 
                      ? "h-auto p-3 whitespace-normal" 
                      : "flex-shrink-0 h-8 px-3 whitespace-nowrap",
                    "bg-white/5 hover:bg-white/10 text-white/70 hover:text-white border border-white/10 hover:border-white/20"
                  )}
                >
                  <span className={cn(
                    "truncate",
                    isExpanded ? "text-sm leading-relaxed" : "text-xs"
                  )}>
                    {message}
                  </span>
                </Button>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>
    </div>
  );
};
