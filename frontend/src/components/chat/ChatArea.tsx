
import { useRef, useEffect } from 'react';
import { ChatInput } from './ChatInput';
import { MessageList } from './MessageList';
import { WelcomeState } from './WelcomeState';
import { useChatStore } from '@/store/chatStore';
import { useAgentStore } from '@/store/agentStore';
import { useIsMobile } from '@/hooks/use-mobile';
import { cn } from '@/lib/utils';
import type { Agent } from '@/types/agent';

export const ChatArea = () => {
  const { getCurrentConversation, deleteMessage, createConversation, addMessage, updateMessage } = useChatStore();
  const { getActiveAgent } = useAgentStore();
  const isMobile = useIsMobile();
  const conversation = getCurrentConversation();
  const activeAgent = getActiveAgent();
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleEditMessage = (messageId: string) => {
    const message = conversation?.messages.find(m => m.id === messageId);
    if (message && inputRef.current) {
      inputRef.current.value = message.content;
      inputRef.current.focus();
    }
  };

  const handleDeleteMessage = (messageId: string) => {
    if (conversation) {
      deleteMessage(conversation.id, messageId);
    }
  };

  const handleSendMessage = async (content: string) => {
    let conversationId = conversation?.id;
    
    if (!conversationId) {
      conversationId = createConversation();
    }

    // Add user message
    addMessage(conversationId, {
      content,
      role: 'user',
      agentId: activeAgent?.id
    });

    // Add typing indicator
    const typingMessageId = addMessage(conversationId, {
      content: '',
      role: 'assistant',
      isTyping: true,
      agentId: activeAgent?.id
    });

    // Simulate response after delay
    setTimeout(() => {
      const response = generateAgentResponse(content, activeAgent || null);
      
      updateMessage(conversationId!, typingMessageId, {
        content: response.content,
        isTyping: false,
        metadata: {
          confidence: 0.95,
          processingTime: Math.floor(Math.random() * 1000) + 500,
          tokens: Math.floor(Math.random() * 100) + 50,
          agentName: activeAgent?.name,
          agentAvatar: activeAgent?.avatar
        },
      });
    }, 2000 + Math.random() * 1500);
  };

  const generateAgentResponse = (userMessage: string, agent: Agent | null) => {
    const responses = {
      'blaze': [
        `Excelente consulta sobre "${userMessage.toLowerCase()}". Como especialista en hipertrofia y fuerza, voy a diseñar un programa personalizado que maximice tu desarrollo muscular. Basándome en la ciencia del entrenamiento y periodización avanzada, aquí tienes mi recomendación estratégica.`,
        `Perfecto timing para esta pregunta sobre "${userMessage.toLowerCase()}". La ciencia de la hipertrofia requiere precisión en la programación. Te voy a explicar cómo optimizar tu entrenamiento usando principios biomecánicos y periodización que garantizarán resultados superiores.`
      ],
      'sage': [
        `Analizando tu consulta nutricional sobre "${userMessage.toLowerCase()}", puedo ver una oportunidad perfecta para implementar nutrición de precisión. Basándome en principios de nutrigenómica y timing nutricional, aquí está mi protocolo personalizado para optimizar tu rendimiento.`,
        `Excelente pregunta sobre "${userMessage.toLowerCase()}". La nutrición estratégica va más allá de macros básicos. Te voy a explicar cómo personalizar tu alimentación según tu fenotipo y objetivos, incluyendo suplementación basada en evidencia científica.`
      ],
      'wave': [
        `Tus datos biométricos muestran patrones interesantes relacionados con "${userMessage.toLowerCase()}". He analizado tus métricas de HRV, sueño y recuperación para proporcionarte insights accionables. Aquí está lo que tu cuerpo nos está comunicando y cómo optimizarlo.`,
        `Perfecto momento para esta consulta sobre "${userMessage.toLowerCase()}". La fusión de análisis biométrico y protocolos de recuperación me permite darte recomendaciones precisas basadas en tus ritmos circadianos y patrones de recuperación.`
      ],
      'nexus': [
        `Entiendo tu consulta sobre "${userMessage.toLowerCase()}". Como coordinador NGX, voy a analizar qué especialistas necesitas y orquestar una respuesta integral. Mi filosofía es garantizar que obtengas exactamente lo que necesitas del ecosistema de agentes.`,
        `Excelente pregunta sobre "${userMessage.toLowerCase()}". Mi rol es asegurar tu éxito coordinando todos los recursos NGX. Voy a analizar tu consulta desde múltiples perspectivas y conectarte con los especialistas que maximizarán tu progreso.`
      ]
    };

    const agentResponses = responses[agent?.id as keyof typeof responses] || responses['nexus'];
    return {
      content: agentResponses[Math.floor(Math.random() * agentResponses.length)]
    };
  };

  if (!conversation) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <WelcomeState />
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col relative">
      {/* Message Area */}
      <div className="flex-1 flex flex-col min-h-0">
        {conversation.messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <WelcomeState />
          </div>
        ) : (
          <MessageList
            conversation={conversation}
            onEditMessage={handleEditMessage}
            onDeleteMessage={handleDeleteMessage}
          />
        )}
      </div>

      {/* Chat Input */}
      <div className={cn(
        "relative z-20 border-t border-white/5 bg-black/20 backdrop-blur-xl",
        isMobile ? "p-3" : "p-4 sm:p-6"
      )}>
        <div className="max-w-5xl mx-auto">
          <ChatInput 
            onSendMessage={handleSendMessage}
          />
        </div>
      </div>
    </div>
  );
};
