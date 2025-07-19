import { useAgentStore } from '@/store/agentStore';
import { useChatStore } from '@/store/chatStore';
import { toastAI } from '@/components/ui/enhanced-toast';
import type { Agent } from '@/types/agent';

export const useChatMessageHandlers = () => {
  const {
    createConversation,
    addMessage,
    setTyping,
    currentConversationId,
    updateMessage,
  } = useChatStore();
  
  const { getActiveAgent, analyzeUserIntent, setActiveAgent } = useAgentStore();

  const handleSendMessage = async (content: string) => {
    let conversationId = currentConversationId;
    
    if (!conversationId) {
      conversationId = createConversation();
    }

    const relevantAgents = analyzeUserIntent(content);
    const activeAgent = getActiveAgent();
    
    if (activeAgent?.id === 'orchestrator' && relevantAgents.length > 0) {
      setActiveAgent(relevantAgents[0]);
      toastAI('Agent switched', `Switched to ${relevantAgents[0]} for better assistance`);
    }

    const isBiometricsQuery = content.toLowerCase().includes('biometric') || 
                            content.toLowerCase().includes('hrv') ||
                            content.toLowerCase().includes('heart rate') ||
                            content.toLowerCase().includes('sleep') ||
                            content.toLowerCase().includes('recovery');

    if (isBiometricsQuery) {
      toastAI('Biometrics Dashboard', 'Showing your latest health metrics');
    }

    addMessage(conversationId, {
      content,
      role: 'user',
      agentId: getActiveAgent()?.id
    });

    setTyping(true);
    
    const typingMessageId = addMessage(conversationId, {
      content: '',
      role: 'assistant',
      isTyping: true,
      agentId: getActiveAgent()?.id
    });

    const response = generateAgentResponse(content, getActiveAgent() || null);
    
    setTimeout(() => {
      updateMessage(conversationId!, typingMessageId, {
        content: response.content,
        isTyping: false,
        metadata: {
          confidence: 0.95,
          processingTime: Math.floor(Math.random() * 1000) + 500,
          tokens: Math.floor(Math.random() * 100) + 50,
          agentName: getActiveAgent()?.name,
          agentAvatar: getActiveAgent()?.avatar
        },
      });
      
      setTyping(false);
    }, 2000 + Math.random() * 1500);

    return isBiometricsQuery;
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
      'luna': [
        `Como especialista en salud femenina, tu consulta sobre "${userMessage.toLowerCase()}" es fundamental. Voy a personalizar mis recomendaciones considerando tus ciclos hormonales, fase de vida y necesidades específicas como mujer. La fisiología femenina requiere un enfoque especializado.`,
        `Excelente pregunta sobre "${userMessage.toLowerCase()}". La salud femenina tiene complejidades únicas que requieren expertise especializado. Te voy a guiar considerando factores hormonales, ciclos menstruales y optimización específica para tu biología femenina.`
      ],
      'spark': [
        `Tu consulta sobre "${userMessage.toLowerCase()}" toca el núcleo del cambio comportamental. Usando neurociencia aplicada y psicología de hábitos, voy a diseñarte un sistema que transforme tu mentalidad y cree adherencia genuina a largo plazo.`,
        `Perfecto enfoque en "${userMessage.toLowerCase()}". La motivación sostenible requiere más que willpower. Te voy a explicar cómo crear sistemas de hábitos basados en neurociencia que generen cambios automáticos y duraderos en tu estilo de vida.`
      ],
      'stella': [
        `Analizando tu pregunta sobre "${userMessage.toLowerCase()}", veo una oportunidad para implementar métricas de alto nivel. Usando bioestadística y KPIs fisiológicos, voy a crear un sistema de tracking que te permita tomar decisiones basadas en datos objetivos.`,
        `Excelente consulta sobre "${userMessage.toLowerCase()}". Los datos no mienten, y mi especialidad es convertir métricas complejas en insights accionables. Te voy a mostrar cómo medir tu progreso de manera científica y predecir resultados futuros.`
      ],
      'nova': [
        `Tu interés en "${userMessage.toLowerCase()}" abre la puerta al biohacking de élite. Voy a compartir protocolos avanzados de optimización que van más allá del fitness convencional. Prepárate para técnicas de vanguardia que maximizarán tu potencial humano.`,
        `Perfecto timing para explorar "${userMessage.toLowerCase()}". El biohacking estratégico puede acelerar dramáticamente tus resultados. Te voy a explicar protocolos de cronobiología, nootrópicos y tecnologías de optimización que usan los atletas de élite.`
      ],
      'codex': [
        `Fascinante consulta sobre "${userMessage.toLowerCase()}". Tu genética contiene el blueprint para optimización personalizada. Basándome en análisis de polimorfismos y nutrigenómica, voy a decodificar tu ADN para crear estrategias ultra-personalizadas.`,
        `Excelente pregunta sobre "${userMessage.toLowerCase()}". La genética es el futuro de la personalización. Te voy a explicar cómo interpretar tus datos genéticos y convertir esa información en protocolos específicos para tu código genético único.`
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

  return { handleSendMessage };
};
