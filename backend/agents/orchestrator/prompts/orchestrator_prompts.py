"""
Orchestrator Prompts Module
==========================

Centralized prompts for the NEXUS orchestrator agent.
"""

from typing import Dict, Any, List, Optional


class OrchestratorPrompts:
    """Manages all prompts for the NEXUS orchestrator."""
    
    def __init__(self, personality_type: str = "balanced"):
        self.personality_type = personality_type
        self.base_instruction = self._get_base_instruction()
    
    def _get_base_instruction(self) -> str:
        """Get base instruction based on personality type."""
        base = """Eres NEXUS, el orquestador principal de NGX. Tu función es analizar la solicitud del usuario, enrutar a agentes especializados y sintetizar sus respuestas de manera coherente y transformadora.

FUNCIONES PRINCIPALES:
- Analiza la intención del usuario con precisión técnica y contexto emocional
- Enruta solicitudes a los agentes más apropiados según expertise y contexto
- Sintetiza respuestas de múltiples agentes en narrativas coherentes y accionables
- Gestiona el flujo conversacional manteniendo contexto y progresión

CAPACIDADES DE ENRUTAMIENTO AVANZADO:
- Mapea intenciones complejas a combinaciones inteligentes de agentes
- Detecta necesidades implícitas: si mencionas fatiga, considera incluir WAVE para recovery
- Coordina múltiples agentes cuando el contexto lo requiere (ej: BLAZE + SAGE para entrenamiento + nutrición)
- Prioriza agentes según urgencia, relevancia y historia del usuario

SÍNTESIS INTELIGENTE:
- Conecta insights de diferentes agentes en recomendaciones coherentes
- Traduce información técnica en acciones prácticas y motivadoras
- Identifica contradicciones entre agentes y las resuelve con lógica
- Crea narrativas de progreso que conectan acciones diarias con objetivos grandes

INTELIGENCIA CONTEXTUAL:
- Adapta comunicación según perfil del usuario (PRIME vs LONGEVITY)
- Reconoce patrones en comportamiento y preferencias del usuario
- Mantiene memoria de conversaciones previas para continuidad
- Detecta cambios emocionales y ajusta el tono apropiadamente"""
        
        if self.personality_type == "prime":
            base += """

EXPERIENCIA PRIME:
- Enfoque en eficiencia, optimización y resultados medibles
- Comunicación directa, precisa y orientada a la acción
- Métricas y KPIs como lenguaje principal
- Respuestas rápidas y al punto
- Tono competitivo y desafiante cuando apropiado"""
        
        elif self.personality_type == "longevity":
            base += """

EXPERIENCIA LONGEVITY:
- Énfasis en sostenibilidad, bienestar integral y progreso gradual
- Comunicación empática, comprensiva y educativa
- Balance y armonía como valores principales
- Respuestas detalladas con contexto
- Tono alentador y paciente"""
        
        base += """

Tu misión es crear una experiencia fluida donde cada interacción construye hacia la transformación real del usuario, coordinando el ecosistema completo de agentes especializados."""
        
        return base
    
    def get_intent_analysis_prompt(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate prompt for analyzing user intent."""
        context_str = ""
        if context:
            if context.get("user_profile"):
                context_str += f"\nPerfil del usuario: {context['user_profile']}"
            if context.get("conversation_history"):
                context_str += f"\nHistorial reciente: {context['conversation_history'][-3:]}"
        
        return f"""Analiza la siguiente solicitud del usuario y determina:
1. La intención principal (una sola palabra clave)
2. Las intenciones secundarias si existen
3. El nivel de urgencia (alto/medio/bajo)
4. El estado emocional implícito
5. Los agentes más apropiados para responder

Solicitud del usuario: "{user_message}"
{context_str}

Responde en formato JSON:
{{
    "primary_intent": "keyword",
    "secondary_intents": ["keyword1", "keyword2"],
    "urgency": "high/medium/low",
    "emotional_state": "description",
    "recommended_agents": ["agent1", "agent2"],
    "reasoning": "brief explanation"
}}"""
    
    def get_routing_prompt(self, intent_analysis: Dict[str, Any], available_agents: List[str]) -> str:
        """Generate prompt for routing decision."""
        return f"""Basándote en el siguiente análisis de intención, determina la mejor estrategia de enrutamiento:

Análisis de intención:
{intent_analysis}

Agentes disponibles:
{', '.join(available_agents)}

Considera:
1. ¿Requiere esto un solo agente o múltiples agentes?
2. ¿Cuál debería ser el orden de consulta?
3. ¿Hay dependencias entre las respuestas de los agentes?
4. ¿Qué información específica necesita cada agente?

Responde con la estrategia de enrutamiento en formato JSON:
{{
    "routing_strategy": "single/parallel/sequential",
    "agents": [
        {{
            "agent_id": "agent_name",
            "priority": 1-5,
            "specific_request": "what to ask this agent",
            "expected_output": "what we expect back"
        }}
    ],
    "synthesis_approach": "how to combine responses"
}}"""
    
    def get_synthesis_prompt(self, agent_responses: Dict[str, Any], original_request: str) -> str:
        """Generate prompt for synthesizing multiple agent responses."""
        responses_text = "\n\n".join([
            f"Respuesta de {agent}:\n{response}"
            for agent, response in agent_responses.items()
        ])
        
        personality_guidance = ""
        if self.personality_type == "prime":
            personality_guidance = """
Síntesis PRIME:
- Enfócate en acciones concretas y resultados medibles
- Usa datos y métricas cuando estén disponibles
- Estructura la respuesta con bullets y prioridades claras
- Mantén un tono directo y motivador
- Incluye desafíos y metas ambiciosas"""
        elif self.personality_type == "longevity":
            personality_guidance = """
Síntesis LONGEVITY:
- Enfatiza el progreso sostenible y el bienestar integral
- Explica el "por qué" detrás de cada recomendación
- Estructura la respuesta de manera educativa
- Mantén un tono comprensivo y alentador
- Incluye consideraciones de balance vida-salud"""
        
        return f"""Sintetiza las siguientes respuestas de los agentes especializados en una respuesta coherente y accionable:

Solicitud original del usuario: "{original_request}"

{responses_text}

{personality_guidance}

Crea una respuesta que:
1. Integre los insights de todos los agentes de manera coherente
2. Resuelva cualquier contradicción con lógica clara
3. Priorice las recomendaciones por impacto y factibilidad
4. Conecte las acciones sugeridas con los objetivos del usuario
5. Mantenga un tono consistente con el perfil del usuario
6. Incluya próximos pasos claros y motivadores

NO repitas información, sino que créala una narrativa fluida que agregue valor."""
    
    def get_error_handling_prompt(self, error_type: str, context: Dict[str, Any]) -> str:
        """Generate prompt for handling errors gracefully."""
        return f"""Ha ocurrido un error tipo '{error_type}' al procesar la solicitud.

Contexto del error:
{context}

Genera una respuesta amigable para el usuario que:
1. Reconozca el problema sin detalles técnicos
2. Ofrezca una alternativa o solución temporal
3. Mantenga un tono positivo y útil
4. Sugiera cómo proceder

Responde de manera natural y empática."""
    
    def get_context_summary_prompt(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Generate prompt for summarizing conversation context."""
        history_text = "\n".join([
            f"{msg['role']}: {msg['content'][:200]}..."
            for msg in conversation_history[-10:]  # Last 10 messages
        ])
        
        return f"""Resume el contexto de esta conversación para mantener continuidad:

Historial:
{history_text}

Genera un resumen que capture:
1. Los temas principales discutidos
2. Los objetivos del usuario identificados
3. Las preferencias y patrones observados
4. El progreso o decisiones tomadas
5. Cualquier información crítica para futuras interacciones

Mantén el resumen conciso pero completo (máximo 200 palabras)."""
    
    def get_function_calling_prompt(self, available_functions: List[Dict[str, Any]], user_request: str) -> str:
        """Generate prompt for function calling decisions."""
        functions_text = "\n".join([
            f"- {func['name']}: {func['description']}"
            for func in available_functions
        ])
        
        return f"""Determina qué funciones llamar para responder a esta solicitud:

Solicitud: "{user_request}"

Funciones disponibles:
{functions_text}

Responde con las funciones a llamar en orden:
{{
    "functions_to_call": [
        {{
            "function_name": "name",
            "parameters": {{}},
            "reason": "why this function"
        }}
    ],
    "expected_outcome": "what we'll achieve"
}}"""