"""
Smart Handoffs Engine - FASE 12 POINT 2
========================================

Sistema inteligente de transferencias entre agentes especializados que preserva
contexto y optimiza la experiencia del usuario mediante handoffs seamless.

FUNCIONALIDADES CLAVE:
- Transferencias contextuales inteligentes entre agentes
- Preservación y adaptación de contexto conversacional
- Routing inteligente basado en expertise y capacidad
- Briefings automáticos para agentes receptores
- Continuidad conversacional optimizada
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

from core.logging_config import get_logger
from core.memory_cache_optimizer import cache_get, cache_set, cache_invalidate, CachePriority
from core.agent_collaboration_hub import (
    AgentRole, AgentCapability, CollaborationType, ConflictResolution
)

logger = get_logger(__name__)


class HandoffTrigger(Enum):
    """Triggers que inician un handoff"""
    USER_REQUEST = "user_request"           # Usuario solicita específicamente otro agente
    EXPERTISE_MISMATCH = "expertise_mismatch"  # Query fuera del expertise del agente actual
    CAPABILITY_NEEDED = "capability_needed"    # Se necesita capability específica
    LOAD_BALANCING = "load_balancing"          # Balanceo de carga entre agentes
    ESCALATION = "escalation"                  # Escalación por complejidad
    CONVERSATION_FLOW = "conversation_flow"    # Flujo natural de conversación
    EMERGENCY = "emergency"                    # Situación de emergencia/crítica


class HandoffStrategy(Enum):
    """Estrategias de handoff"""
    IMMEDIATE = "immediate"                 # Transferencia inmediata
    GRADUAL = "gradual"                    # Transición gradual con overlap
    CONSULTATION = "consultation"          # Consulta manteniendo agente principal
    ESCALATION_TREE = "escalation_tree"    # Escalación jerárquica
    ROUND_ROBIN = "round_robin"           # Rotación balanceada
    EXPERTISE_WEIGHTED = "expertise_weighted"  # Basado en expertise scores


class HandoffQuality(Enum):
    """Niveles de calidad de handoff"""
    SEAMLESS = "seamless"      # Handoff perfecto, usuario no lo nota
    SMOOTH = "smooth"          # Handoff suave con mínima fricción
    VISIBLE = "visible"        # Handoff visible pero bien ejecutado
    ABRUPT = "abrupt"         # Handoff abrupto con alguna fricción
    FAILED = "failed"         # Handoff fallido, requiere intervención


@dataclass
class HandoffRequest:
    """Solicitud de handoff entre agentes"""
    handoff_id: str
    from_agent: AgentRole
    to_agent: AgentRole
    trigger: HandoffTrigger
    strategy: HandoffStrategy
    context: Dict[str, Any]
    user_id: str
    session_id: Optional[str]
    priority: int  # 1-10, 10 = crítico
    reason: str
    expected_duration: Optional[timedelta]
    success_criteria: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        data = asdict(self)
        data['from_agent'] = self.from_agent.value
        data['to_agent'] = self.to_agent.value
        data['trigger'] = self.trigger.value
        data['strategy'] = self.strategy.value
        data['created_at'] = self.created_at.isoformat()
        data['expected_duration'] = self.expected_duration.total_seconds() if self.expected_duration else None
        return data


@dataclass
class ContextualBriefing:
    """Briefing contextual para agente receptor"""
    briefing_id: str
    target_agent: AgentRole
    user_context: Dict[str, Any]
    conversation_history: List[str]
    current_objectives: List[str]
    relevant_data: Dict[str, Any]
    suggested_approach: str
    potential_challenges: List[str]
    success_metrics: List[str]
    handoff_context: str
    priority_items: List[str]
    generated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        data = asdict(self)
        data['target_agent'] = self.target_agent.value
        data['generated_at'] = self.generated_at.isoformat()
        return data


@dataclass
class HandoffResult:
    """Resultado de un handoff ejecutado"""
    handoff_id: str
    success: bool
    quality: HandoffQuality
    execution_time: float  # segundos
    context_preserved: float  # 0.0-1.0
    user_satisfaction: Optional[float]  # 0.0-1.0 si disponible
    issues_encountered: List[str]
    lessons_learned: List[str]
    performance_metrics: Dict[str, Any]
    completed_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        data = asdict(self)
        data['quality'] = self.quality.value
        data['completed_at'] = self.completed_at.isoformat()
        return data


class SmartHandoffEngine:
    """
    Motor inteligente de transferencias entre agentes especializados
    
    CAPACIDADES AVANZADAS:
    - Análisis de compatibilidad para handoffs óptimos
    - Preservación inteligente de contexto conversacional
    - Generación automática de briefings contextuales
    - Optimización de estrategias basada en experiencia
    - Monitoreo de calidad y mejora continua
    """
    
    def __init__(self):
        self.cache_prefix = "smart_handoffs"
        self.handoff_history = {}
        self.performance_metrics = {}
        
        # Matriz de compatibilidad para handoffs
        self.handoff_compatibility = self._initialize_handoff_compatibility()
        
        # Patrones de contexto que se deben preservar
        self.context_preservation_patterns = self._initialize_context_patterns()
        
        # Estrategias de handoff por tipo de trigger
        self.strategy_mapping = self._initialize_strategy_mapping()
    
    def _initialize_handoff_compatibility(self) -> Dict[Tuple[AgentRole, AgentRole], float]:
        """Inicializa matriz de compatibilidad para handoffs entre agentes"""
        compatibility = {}
        
        # Handoffs de alta compatibilidad (expertise complementario)
        high_compatibility = [
            (AgentRole.SAGE_NUTRITION, AgentRole.BLAZE_TRAINING),     # Nutrición → Entrenamiento
            (AgentRole.BLAZE_TRAINING, AgentRole.SAGE_NUTRITION),     # Entrenamiento → Nutrición
            (AgentRole.WAVE_ANALYTICS, AgentRole.STELLA_PROGRESS),    # Analytics → Progress
            (AgentRole.STELLA_PROGRESS, AgentRole.WAVE_ANALYTICS),    # Progress → Analytics
            (AgentRole.NOVA_BIOHACKING, AgentRole.LUNA_WELLNESS),     # Biohacking → Female Wellness
            (AgentRole.LUNA_WELLNESS, AgentRole.NOVA_BIOHACKING),     # Female Wellness → Biohacking
            (AgentRole.HELIX_GENETICS, AgentRole.VOLT_BIOMETRICS),    # Genetics → Biometrics
            (AgentRole.VOLT_BIOMETRICS, AgentRole.HELIX_GENETICS),    # Biometrics → Genetics
        ]
        
        # Asignar alta compatibilidad
        for from_agent, to_agent in high_compatibility:
            compatibility[(from_agent, to_agent)] = 0.95
        
        # Handoffs naturales (flujo lógico)
        natural_flows = [
            (AgentRole.NEXUS_MOTIVATION, AgentRole.BLAZE_TRAINING),   # Motivación → Entrenamiento
            (AgentRole.BLAZE_TRAINING, AgentRole.STELLA_PROGRESS),    # Entrenamiento → Progress
            (AgentRole.SAGE_NUTRITION, AgentRole.VOLT_BIOMETRICS),    # Nutrición → Biometrics
            (AgentRole.VOLT_BIOMETRICS, AgentRole.WAVE_ANALYTICS),    # Biometrics → Analytics
        ]
        
        # Asignar compatibilidad natural
        for from_agent, to_agent in natural_flows:
            compatibility[(from_agent, to_agent)] = 0.85
        
        # Compatibilidad media por defecto
        all_agents = list(AgentRole)
        for from_agent in all_agents:
            for to_agent in all_agents:
                if from_agent != to_agent and (from_agent, to_agent) not in compatibility:
                    compatibility[(from_agent, to_agent)] = 0.65
        
        return compatibility
    
    def _initialize_context_patterns(self) -> Dict[str, List[str]]:
        """Inicializa patrones de contexto que deben preservarse"""
        return {
            'user_profile': [
                'name', 'age', 'fitness_level', 'goals', 'preferences',
                'medical_conditions', 'dietary_restrictions', 'program_type'
            ],
            'conversation_state': [
                'current_topic', 'conversation_phase', 'user_mood',
                'engagement_level', 'last_recommendations', 'pending_actions'
            ],
            'domain_specific': [
                'workout_history', 'nutrition_logs', 'biometric_data',
                'progress_metrics', 'genetic_info', 'wellness_goals'
            ],
            'technical_context': [
                'session_id', 'device_info', 'app_version',
                'feature_flags', 'A/B_test_groups', 'personalization_settings'
            ]
        }
    
    def _initialize_strategy_mapping(self) -> Dict[HandoffTrigger, HandoffStrategy]:
        """Inicializa mapping de triggers a estrategias recomendadas"""
        return {
            HandoffTrigger.USER_REQUEST: HandoffStrategy.IMMEDIATE,
            HandoffTrigger.EXPERTISE_MISMATCH: HandoffStrategy.EXPERTISE_WEIGHTED,
            HandoffTrigger.CAPABILITY_NEEDED: HandoffStrategy.CONSULTATION,
            HandoffTrigger.LOAD_BALANCING: HandoffStrategy.ROUND_ROBIN,
            HandoffTrigger.ESCALATION: HandoffStrategy.ESCALATION_TREE,
            HandoffTrigger.CONVERSATION_FLOW: HandoffStrategy.GRADUAL,
            HandoffTrigger.EMERGENCY: HandoffStrategy.IMMEDIATE
        }
    
    async def request_handoff(
        self,
        from_agent: AgentRole,
        to_agent: AgentRole,
        trigger: HandoffTrigger,
        context: Dict[str, Any],
        user_id: str,
        reason: str,
        session_id: Optional[str] = None,
        priority: int = 5
    ) -> HandoffRequest:
        """
        Solicita un handoff inteligente entre agentes
        
        Args:
            from_agent: Agente que transfiere
            to_agent: Agente que recibe
            trigger: Razón del handoff
            context: Contexto completo del usuario/conversación
            user_id: ID del usuario
            reason: Descripción específica del handoff
            session_id: ID de la sesión
            priority: Prioridad 1-10
        
        Returns:
            HandoffRequest configurada y validada
        """
        try:
            handoff_id = str(uuid.uuid4())
            
            # Determinar estrategia basada en trigger
            strategy = self.strategy_mapping.get(trigger, HandoffStrategy.EXPERTISE_WEIGHTED)
            
            # Evaluar compatibilidad de handoff
            compatibility = self.handoff_compatibility.get((from_agent, to_agent), 0.65)
            
            if compatibility < 0.5:
                logger.warning(f"Baja compatibilidad ({compatibility}) para handoff {from_agent.value} → {to_agent.value}")
            
            # Estimar duración esperada
            expected_duration = await self._estimate_handoff_duration(
                from_agent, to_agent, strategy, context
            )
            
            # Definir criterios de éxito
            success_criteria = await self._generate_success_criteria(
                from_agent, to_agent, trigger, context
            )
            
            handoff_request = HandoffRequest(
                handoff_id=handoff_id,
                from_agent=from_agent,
                to_agent=to_agent,
                trigger=trigger,
                strategy=strategy,
                context=context,
                user_id=user_id,
                session_id=session_id,
                priority=priority,
                reason=reason,
                expected_duration=expected_duration,
                success_criteria=success_criteria,
                metadata={
                    'compatibility_score': compatibility,
                    'context_complexity': len(context),
                    'estimated_quality': self._estimate_handoff_quality(compatibility, strategy)
                },
                created_at=datetime.utcnow()
            )
            
            # Cachear solicitud
            await self._cache_handoff_request(handoff_request)
            
            logger.info(f"Handoff solicitado: {handoff_id} - {from_agent.value} → {to_agent.value}")
            
            return handoff_request
            
        except Exception as e:
            logger.error(f"Error solicitando handoff: {e}")
            raise
    
    async def execute_handoff(
        self,
        handoff_request: HandoffRequest
    ) -> Tuple[ContextualBriefing, HandoffResult]:
        """
        Ejecuta un handoff inteligente con preservación de contexto
        
        Args:
            handoff_request: Solicitud de handoff a ejecutar
        
        Returns:
            Tuple[ContextualBriefing, HandoffResult]: Briefing y resultado
        """
        try:
            start_time = datetime.utcnow()
            
            # 1. Generar briefing contextual para agente receptor
            briefing = await self._generate_contextual_briefing(handoff_request)
            
            # 2. Preparar contexto adaptado
            adapted_context = await self._adapt_context_for_target(
                handoff_request.context,
                handoff_request.from_agent,
                handoff_request.to_agent
            )
            
            # 3. Ejecutar estrategia específica
            execution_result = await self._execute_handoff_strategy(
                handoff_request, adapted_context
            )
            
            # 4. Validar preservación de contexto
            context_preservation = self._validate_context_preservation(
                handoff_request.context, adapted_context
            )
            
            # 5. Calcular métricas de calidad
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            quality = self._assess_handoff_quality(
                execution_result, context_preservation, execution_time
            )
            
            # 6. Crear resultado
            handoff_result = HandoffResult(
                handoff_id=handoff_request.handoff_id,
                success=execution_result.get('success', True),
                quality=quality,
                execution_time=execution_time,
                context_preserved=context_preservation,
                user_satisfaction=None,  # Se actualizará con feedback
                issues_encountered=execution_result.get('issues', []),
                lessons_learned=execution_result.get('lessons', []),
                performance_metrics={
                    'compatibility_used': handoff_request.metadata.get('compatibility_score'),
                    'strategy_used': handoff_request.strategy.value,
                    'context_complexity': len(handoff_request.context),
                    'priority_level': handoff_request.priority
                },
                completed_at=datetime.utcnow()
            )
            
            # 7. Cachear resultado y actualizar métricas
            await self._cache_handoff_result(handoff_result)
            await self._update_performance_metrics(handoff_request, handoff_result)
            
            logger.info(f"Handoff ejecutado: {handoff_request.handoff_id} - Calidad: {quality.value}")
            
            return briefing, handoff_result
            
        except Exception as e:
            logger.error(f"Error ejecutando handoff: {e}")
            
            # Crear resultado de fallo
            failed_result = HandoffResult(
                handoff_id=handoff_request.handoff_id,
                success=False,
                quality=HandoffQuality.FAILED,
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                context_preserved=0.0,
                user_satisfaction=None,
                issues_encountered=[str(e)],
                lessons_learned=['Handoff failed due to system error'],
                performance_metrics={},
                completed_at=datetime.utcnow()
            )
            
            # Generar briefing básico para fallback
            fallback_briefing = await self._generate_fallback_briefing(handoff_request)
            
            return fallback_briefing, failed_result
    
    async def _generate_contextual_briefing(
        self, 
        handoff_request: HandoffRequest
    ) -> ContextualBriefing:
        """Genera briefing contextual completo para agente receptor"""
        try:
            briefing_id = str(uuid.uuid4())
            context = handoff_request.context
            
            # Extraer información relevante del contexto
            user_context = self._extract_user_context(context)
            conversation_history = self._extract_conversation_history(context)
            relevant_data = self._extract_relevant_data(context, handoff_request.to_agent)
            
            # Generar objetivos actuales
            current_objectives = self._infer_current_objectives(
                handoff_request, user_context
            )
            
            # Generar enfoque sugerido
            suggested_approach = await self._generate_suggested_approach(
                handoff_request.to_agent, user_context, handoff_request.reason
            )
            
            # Identificar desafíos potenciales
            potential_challenges = self._identify_potential_challenges(
                handoff_request.from_agent, handoff_request.to_agent, context
            )
            
            # Definir métricas de éxito
            success_metrics = handoff_request.success_criteria
            
            # Crear contexto de handoff
            handoff_context = self._create_handoff_context_description(handoff_request)
            
            # Priorizar elementos importantes
            priority_items = self._prioritize_briefing_items(
                user_context, current_objectives, handoff_request.priority
            )
            
            briefing = ContextualBriefing(
                briefing_id=briefing_id,
                target_agent=handoff_request.to_agent,
                user_context=user_context,
                conversation_history=conversation_history,
                current_objectives=current_objectives,
                relevant_data=relevant_data,
                suggested_approach=suggested_approach,
                potential_challenges=potential_challenges,
                success_metrics=success_metrics,
                handoff_context=handoff_context,
                priority_items=priority_items,
                generated_at=datetime.utcnow()
            )
            
            # Cachear briefing
            await self._cache_briefing(briefing)
            
            return briefing
            
        except Exception as e:
            logger.error(f"Error generando briefing contextual: {e}")
            raise
    
    def _extract_user_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae contexto del usuario relevante"""
        user_context = {}
        
        # Extraer patrones de contexto de usuario
        for pattern_key in self.context_preservation_patterns['user_profile']:
            if pattern_key in context:
                user_context[pattern_key] = context[pattern_key]
        
        # Agregar información derivada
        user_context['engagement_signals'] = self._analyze_engagement_signals(context)
        user_context['expertise_level'] = self._infer_expertise_level(context)
        user_context['communication_style'] = self._infer_communication_style(context)
        
        return user_context
    
    def _extract_conversation_history(self, context: Dict[str, Any]) -> List[str]:
        """Extrae historial conversacional relevante"""
        history = []
        
        # Buscar historial en contexto
        if 'conversation_history' in context:
            raw_history = context['conversation_history']
            
            # Procesar y filtrar historial
            if isinstance(raw_history, list):
                # Tomar últimas 10 interacciones para brevedad
                recent_history = raw_history[-10:] if len(raw_history) > 10 else raw_history
                
                for item in recent_history:
                    if isinstance(item, dict):
                        # Extraer mensaje de estructura compleja
                        message = item.get('message', item.get('content', str(item)))
                        history.append(str(message))
                    else:
                        history.append(str(item))
        
        # Si no hay historial explícito, inferir de otros campos
        if not history:
            if 'last_user_message' in context:
                history.append(f"Usuario: {context['last_user_message']}")
            if 'last_agent_response' in context:
                history.append(f"Agente: {context['last_agent_response']}")
        
        return history
    
    def _extract_relevant_data(
        self, 
        context: Dict[str, Any], 
        target_agent: AgentRole
    ) -> Dict[str, Any]:
        """Extrae datos relevantes para el agente objetivo"""
        relevant_data = {}
        
        # Mapeo de agentes a tipos de datos relevantes
        agent_data_mapping = {
            AgentRole.SAGE_NUTRITION: ['nutrition_data', 'meal_logs', 'dietary_preferences'],
            AgentRole.BLAZE_TRAINING: ['workout_data', 'fitness_level', 'exercise_preferences'],
            AgentRole.WAVE_ANALYTICS: ['performance_metrics', 'trends', 'analytics_data'],
            AgentRole.STELLA_PROGRESS: ['goals', 'milestones', 'achievements', 'progress_data'],
            AgentRole.NOVA_BIOHACKING: ['biometric_data', 'optimization_goals', 'experiments'],
            AgentRole.LUNA_WELLNESS: ['wellness_data', 'cycle_data', 'health_metrics'],
            AgentRole.HELIX_GENETICS: ['genetic_data', 'dna_analysis', 'family_history'],
            AgentRole.VOLT_BIOMETRICS: ['biometric_data', 'device_data', 'health_metrics'],
            AgentRole.NEXUS_MOTIVATION: ['motivation_factors', 'behavioral_data', 'psychology']
        }
        
        # Extraer datos específicos para el agente
        relevant_keys = agent_data_mapping.get(target_agent, [])
        for key in relevant_keys:
            if key in context:
                relevant_data[key] = context[key]
        
        # Agregar datos sempre relevantes
        always_relevant = ['user_id', 'session_id', 'timestamp', 'device_info']
        for key in always_relevant:
            if key in context:
                relevant_data[key] = context[key]
        
        return relevant_data
    
    def _infer_current_objectives(
        self, 
        handoff_request: HandoffRequest, 
        user_context: Dict[str, Any]
    ) -> List[str]:
        """Infiere objetivos actuales basados en contexto"""
        objectives = []
        
        # Objetivos basados en el trigger del handoff
        trigger_objectives = {
            HandoffTrigger.EXPERTISE_MISMATCH: [
                f"Obtener expertise especializada de {handoff_request.to_agent.value}",
                "Resolver query específica fuera del dominio anterior"
            ],
            HandoffTrigger.CAPABILITY_NEEDED: [
                f"Utilizar capacidades específicas de {handoff_request.to_agent.value}",
                "Completar tarea que requiere expertise especializada"
            ],
            HandoffTrigger.CONVERSATION_FLOW: [
                "Continuar conversación de manera natural",
                f"Aprovechar expertise de {handoff_request.to_agent.value}"
            ],
            HandoffTrigger.USER_REQUEST: [
                "Cumplir solicitud específica del usuario",
                f"Conectar con {handoff_request.to_agent.value} según pedido"
            ]
        }
        
        objectives.extend(trigger_objectives.get(handoff_request.trigger, [
            "Proporcionar asistencia especializada",
            "Mantener experiencia de usuario fluida"
        ]))
        
        # Objetivos basados en contexto de usuario
        if 'goals' in user_context:
            user_goals = user_context['goals']
            if isinstance(user_goals, list):
                objectives.extend([f"Apoyar objetivo: {goal}" for goal in user_goals[:2]])
            elif isinstance(user_goals, str):
                objectives.append(f"Apoyar objetivo: {user_goals}")
        
        return objectives[:5]  # Limitar a 5 objetivos principales
    
    async def _generate_suggested_approach(
        self, 
        target_agent: AgentRole, 
        user_context: Dict[str, Any], 
        reason: str
    ) -> str:
        """Genera enfoque sugerido para el agente receptor"""
        
        # Enfoques base por agente
        agent_approaches = {
            AgentRole.SAGE_NUTRITION: "Analizar preferencias nutricionales y crear plan personalizado",
            AgentRole.BLAZE_TRAINING: "Evaluar nivel fitness y diseñar programa de entrenamiento",
            AgentRole.WAVE_ANALYTICS: "Revisar métricas de rendimiento y identificar patrones",
            AgentRole.STELLA_PROGRESS: "Analizar progreso actual y celebrar logros alcanzados",
            AgentRole.NOVA_BIOHACKING: "Explorar oportunidades de optimización biológica",
            AgentRole.LUNA_WELLNESS: "Proporcionar guidance especializada en wellness femenino",
            AgentRole.HELIX_GENETICS: "Interpretar información genética para personalización",
            AgentRole.VOLT_BIOMETRICS: "Analizar datos biométricos y proporcionar insights",
            AgentRole.NEXUS_MOTIVATION: "Evaluar factores motivacionales y proporcionar coaching"
        }
        
        base_approach = agent_approaches.get(target_agent, "Proporcionar asistencia especializada")
        
        # Personalizar basado en contexto
        if 'expertise_level' in user_context:
            level = user_context['expertise_level']
            if level == 'beginner':
                base_approach += ". Usar lenguaje simple y explicaciones básicas."
            elif level == 'advanced':
                base_approach += ". Proporcionar insights técnicos y detalles avanzados."
        
        if 'communication_style' in user_context:
            style = user_context['communication_style']
            if style == 'direct':
                base_approach += " Ser directo y conciso en las recomendaciones."
            elif style == 'detailed':
                base_approach += " Proporcionar explicaciones detalladas y contexto."
        
        # Agregar contexto de la razón del handoff
        base_approach += f" Contexto del handoff: {reason}"
        
        return base_approach
    
    def _identify_potential_challenges(
        self, 
        from_agent: AgentRole, 
        to_agent: AgentRole, 
        context: Dict[str, Any]
    ) -> List[str]:
        """Identifica desafíos potenciales del handoff"""
        challenges = []
        
        # Desafíos basados en compatibilidad
        compatibility = self.handoff_compatibility.get((from_agent, to_agent), 0.65)
        if compatibility < 0.7:
            challenges.append("Baja compatibilidad entre dominios de expertise")
        
        # Desafíos basados en complejidad del contexto
        if len(context) > 20:
            challenges.append("Contexto complejo que requiere procesamiento cuidadoso")
        
        # Desafíos específicos por transición de agente
        transition_challenges = {
            (AgentRole.BLAZE_TRAINING, AgentRole.SAGE_NUTRITION): [
                "Coordinar recommendations de ejercicio con nutrition"
            ],
            (AgentRole.SAGE_NUTRITION, AgentRole.BLAZE_TRAINING): [
                "Alinear plan nutricional con demandas de entrenamiento"
            ],
            (AgentRole.WAVE_ANALYTICS, AgentRole.STELLA_PROGRESS): [
                "Traducir analytics complejos a insights de progreso claros"
            ]
        }
        
        specific_challenges = transition_challenges.get((from_agent, to_agent), [])
        challenges.extend(specific_challenges)
        
        # Desafíos basados en contexto de usuario
        if context.get('user_mood') == 'frustrated':
            challenges.append("Usuario potencialmente frustrado, requiere empatía extra")
        
        if context.get('engagement_level') == 'low':
            challenges.append("Bajo engagement, necesita motivación y activación")
        
        return challenges[:5]  # Limitar a 5 desafíos principales
    
    def _create_handoff_context_description(self, handoff_request: HandoffRequest) -> str:
        """Crea descripción del contexto de handoff"""
        
        description = f"""
CONTEXTO DE HANDOFF:
Transferencia: {handoff_request.from_agent.value} → {handoff_request.to_agent.value}
Trigger: {handoff_request.trigger.value}
Estrategia: {handoff_request.strategy.value}
Prioridad: {handoff_request.priority}/10
Razón: {handoff_request.reason}

EXPECTATIVAS:
- Duración estimada: {handoff_request.expected_duration.total_seconds() if handoff_request.expected_duration else 'N/A'} segundos
- Criterios de éxito: {', '.join(handoff_request.success_criteria)}
- Compatibilidad: {handoff_request.metadata.get('compatibility_score', 'N/A')}

RECOMENDACIONES:
- Mantener continuidad conversacional
- Preservar contexto crítico del usuario
- Aprovechar expertise específica del agente receptor
        """.strip()
        
        return description
    
    def _prioritize_briefing_items(
        self, 
        user_context: Dict[str, Any], 
        objectives: List[str], 
        priority: int
    ) -> List[str]:
        """Prioriza elementos importantes del briefing"""
        priority_items = []
        
        # Items de alta prioridad basados en priority level
        if priority >= 8:
            priority_items.extend([
                "🔥 ALTA PRIORIDAD: Respuesta rápida requerida",
                "🎯 Enfocarse en resolver query específica inmediatamente"
            ])
        
        # Items basados en contexto de usuario
        if user_context.get('engagement_level') == 'low':
            priority_items.append("⚡ Activar engagement del usuario")
        
        if 'goals' in user_context:
            priority_items.append(f"🎯 Alinearse con objetivos: {user_context['goals']}")
        
        # Items basados en objetivos
        if objectives:
            primary_objective = objectives[0]
            priority_items.append(f"📋 Objetivo principal: {primary_objective}")
        
        # Items siempre importantes
        priority_items.extend([
            "🤝 Mantener experiencia de usuario fluida",
            "💡 Aprovechar expertise especializada",
            "📊 Proporcionar value añadido inmediato"
        ])
        
        return priority_items[:7]  # Limitar a 7 items prioritarios
    
    async def _adapt_context_for_target(
        self, 
        context: Dict[str, Any], 
        from_agent: AgentRole, 
        to_agent: AgentRole
    ) -> Dict[str, Any]:
        """Adapta contexto para el agente objetivo"""
        try:
            adapted_context = context.copy()
            
            # Agregar metadata de handoff
            adapted_context['handoff_metadata'] = {
                'transferred_from': from_agent.value,
                'transfer_timestamp': datetime.utcnow().isoformat(),
                'target_agent_expertise': self._get_agent_expertise(to_agent),
                'handoff_reason': f"Transferencia desde {from_agent.value} para expertise especializada"
            }
            
            # Filtrar datos relevantes para el agente objetivo
            relevant_data = self._extract_relevant_data(context, to_agent)
            adapted_context['relevant_data'] = relevant_data
            
            # Agregar guidance específica para el agente
            adapted_context['agent_guidance'] = self._generate_agent_guidance(to_agent, context)
            
            return adapted_context
            
        except Exception as e:
            logger.error(f"Error adaptando contexto: {e}")
            return context
    
    def _get_agent_expertise(self, agent: AgentRole) -> List[str]:
        """Obtiene áreas de expertise de un agente"""
        expertise_mapping = {
            AgentRole.SAGE_NUTRITION: ['nutrition', 'meal_planning', 'supplements'],
            AgentRole.BLAZE_TRAINING: ['exercise', 'training_programs', 'fitness'],
            AgentRole.WAVE_ANALYTICS: ['performance_analysis', 'data_insights', 'trends'],
            AgentRole.STELLA_PROGRESS: ['goal_tracking', 'achievements', 'motivation'],
            AgentRole.NOVA_BIOHACKING: ['optimization', 'biohacking', 'cutting_edge'],
            AgentRole.LUNA_WELLNESS: ['female_health', 'hormones', 'wellness'],
            AgentRole.HELIX_GENETICS: ['genetics', 'dna_analysis', 'personalization'],
            AgentRole.VOLT_BIOMETRICS: ['biometrics', 'health_data', 'monitoring'],
            AgentRole.NEXUS_MOTIVATION: ['motivation', 'behavior_change', 'psychology']
        }
        
        return expertise_mapping.get(agent, ['general_assistance'])
    
    def _generate_agent_guidance(self, agent: AgentRole, context: Dict[str, Any]) -> str:
        """Genera guidance específica para el agente"""
        
        base_guidance = {
            AgentRole.SAGE_NUTRITION: "Enfócate en análisis nutricional y recomendaciones de alimentación",
            AgentRole.BLAZE_TRAINING: "Prioriza programas de ejercicio y optimización de entrenamiento", 
            AgentRole.WAVE_ANALYTICS: "Analiza patrones en los datos y proporciona insights accionables",
            AgentRole.STELLA_PROGRESS: "Celebra logros y motiva hacia objetivos futuros",
            AgentRole.NOVA_BIOHACKING: "Explora técnicas avanzadas de optimización biológica",
            AgentRole.LUNA_WELLNESS: "Proporciona guidance especializada en salud femenina",
            AgentRole.HELIX_GENETICS: "Interpreta información genética para personalización",
            AgentRole.VOLT_BIOMETRICS: "Analiza datos biométricos y tendencias de salud",
            AgentRole.NEXUS_MOTIVATION: "Proporciona coaching motivacional y cambio de comportamiento"
        }
        
        guidance = base_guidance.get(agent, "Proporciona asistencia especializada")
        
        # Personalizar basado en contexto
        if context.get('user_mood') == 'motivated':
            guidance += ". El usuario está motivado, aprovecha su energía positiva."
        elif context.get('user_mood') == 'frustrated':
            guidance += ". El usuario puede estar frustrado, usa empatía y paciencia."
        
        return guidance
    
    async def _execute_handoff_strategy(
        self, 
        handoff_request: HandoffRequest, 
        adapted_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta la estrategia específica de handoff"""
        
        strategy = handoff_request.strategy
        result = {'success': True, 'issues': [], 'lessons': []}
        
        try:
            if strategy == HandoffStrategy.IMMEDIATE:
                # Transferencia inmediata sin overlap
                result['execution_type'] = 'immediate_transfer'
                result['lessons'].append('Handoff inmediato ejecutado exitosamente')
                
            elif strategy == HandoffStrategy.GRADUAL:
                # Transición gradual con overlap
                result['execution_type'] = 'gradual_transition'
                result['overlap_duration'] = 30  # segundos
                result['lessons'].append('Transición gradual con overlap de 30 segundos')
                
            elif strategy == HandoffStrategy.CONSULTATION:
                # Consulta manteniendo agente principal
                result['execution_type'] = 'consultation_mode'
                result['primary_agent'] = handoff_request.from_agent.value
                result['consultant_agent'] = handoff_request.to_agent.value
                result['lessons'].append('Modo consulta activado correctamente')
                
            elif strategy == HandoffStrategy.EXPERTISE_WEIGHTED:
                # Basado en scores de expertise
                expertise_score = self._calculate_expertise_score(
                    handoff_request.to_agent, adapted_context
                )
                result['execution_type'] = 'expertise_weighted'
                result['expertise_score'] = expertise_score
                result['lessons'].append(f'Handoff basado en expertise score: {expertise_score}')
                
            else:
                # Estrategia por defecto
                result['execution_type'] = 'default_strategy'
                result['lessons'].append('Estrategia por defecto aplicada')
            
            # Simular tiempo de procesamiento
            await asyncio.sleep(0.1)
            
        except Exception as e:
            result['success'] = False
            result['issues'].append(f"Error en ejecución de estrategia: {e}")
            logger.error(f"Error ejecutando estrategia {strategy.value}: {e}")
        
        return result
    
    def _calculate_expertise_score(self, agent: AgentRole, context: Dict[str, Any]) -> float:
        """Calcula score de expertise para el contexto específico"""
        
        # Base score por agente
        base_scores = {
            AgentRole.SAGE_NUTRITION: 0.9,
            AgentRole.BLAZE_TRAINING: 0.9,
            AgentRole.WAVE_ANALYTICS: 0.85,
            AgentRole.STELLA_PROGRESS: 0.8,
            AgentRole.NOVA_BIOHACKING: 0.85,
            AgentRole.LUNA_WELLNESS: 0.85,
            AgentRole.HELIX_GENETICS: 0.9,
            AgentRole.VOLT_BIOMETRICS: 0.85,
            AgentRole.NEXUS_MOTIVATION: 0.8
        }
        
        base_score = base_scores.get(agent, 0.7)
        
        # Ajustar basado en contexto relevante
        relevant_data = context.get('relevant_data', {})
        if relevant_data:
            # Más datos relevantes = mayor score
            relevance_bonus = min(0.1, len(relevant_data) * 0.02)
            base_score += relevance_bonus
        
        return min(1.0, base_score)
    
    def _validate_context_preservation(
        self, 
        original_context: Dict[str, Any], 
        adapted_context: Dict[str, Any]
    ) -> float:
        """Valida qué tan bien se preservó el contexto"""
        
        # Elementos críticos que deben preservarse
        critical_elements = [
            'user_id', 'session_id', 'goals', 'preferences',
            'current_conversation', 'user_state'
        ]
        
        preserved_count = 0
        total_critical = len(critical_elements)
        
        for element in critical_elements:
            if element in original_context and element in adapted_context:
                # Verificar que el valor se preservó
                if original_context[element] == adapted_context.get(element):
                    preserved_count += 1
            elif element not in original_context:
                # Si no existía originalmente, no cuenta contra preservation
                total_critical -= 1
        
        if total_critical == 0:
            return 1.0
        
        preservation_score = preserved_count / total_critical
        
        # Bonus por contexto adicional útil
        if 'handoff_metadata' in adapted_context:
            preservation_score += 0.1
        
        if 'agent_guidance' in adapted_context:
            preservation_score += 0.05
        
        return min(1.0, preservation_score)
    
    def _assess_handoff_quality(
        self, 
        execution_result: Dict[str, Any], 
        context_preservation: float, 
        execution_time: float
    ) -> HandoffQuality:
        """Evalúa la calidad del handoff ejecutado"""
        
        # Factores de calidad
        success = execution_result.get('success', False)
        issues_count = len(execution_result.get('issues', []))
        
        # Calcular score base
        quality_score = 0.0
        
        if success:
            quality_score += 0.4
        
        # Bonus por preservación de contexto
        quality_score += context_preservation * 0.3
        
        # Penalty por tiempo de ejecución
        if execution_time < 1.0:
            quality_score += 0.2
        elif execution_time < 3.0:
            quality_score += 0.1
        else:
            quality_score -= 0.1
        
        # Penalty por issues
        quality_score -= issues_count * 0.1
        
        # Determinar calidad basada en score
        if quality_score >= 0.9:
            return HandoffQuality.SEAMLESS
        elif quality_score >= 0.75:
            return HandoffQuality.SMOOTH
        elif quality_score >= 0.6:
            return HandoffQuality.VISIBLE
        elif quality_score >= 0.4:
            return HandoffQuality.ABRUPT
        else:
            return HandoffQuality.FAILED
    
    async def _estimate_handoff_duration(
        self, 
        from_agent: AgentRole, 
        to_agent: AgentRole, 
        strategy: HandoffStrategy, 
        context: Dict[str, Any]
    ) -> timedelta:
        """Estima duración del handoff"""
        
        # Tiempos base por estrategia
        base_times = {
            HandoffStrategy.IMMEDIATE: 2,      # 2 segundos
            HandoffStrategy.GRADUAL: 45,       # 45 segundos
            HandoffStrategy.CONSULTATION: 10,  # 10 segundos
            HandoffStrategy.ESCALATION_TREE: 15,  # 15 segundos
            HandoffStrategy.ROUND_ROBIN: 5,    # 5 segundos
            HandoffStrategy.EXPERTISE_WEIGHTED: 8  # 8 segundos
        }
        
        base_time = base_times.get(strategy, 10)
        
        # Ajustar por complejidad del contexto
        context_complexity = len(context)
        if context_complexity > 20:
            base_time += 5
        elif context_complexity > 10:
            base_time += 2
        
        # Ajustar por compatibilidad
        compatibility = self.handoff_compatibility.get((from_agent, to_agent), 0.65)
        if compatibility < 0.7:
            base_time += 10  # Handoffs difíciles toman más tiempo
        
        return timedelta(seconds=base_time)
    
    async def _generate_success_criteria(
        self, 
        from_agent: AgentRole, 
        to_agent: AgentRole, 
        trigger: HandoffTrigger, 
        context: Dict[str, Any]
    ) -> List[str]:
        """Genera criterios de éxito para el handoff"""
        
        criteria = [
            "Contexto de usuario preservado completamente",
            "Continuidad conversacional mantenida",
            f"Expertise de {to_agent.value} efectivamente aplicada"
        ]
        
        # Criterios específicos por trigger
        trigger_criteria = {
            HandoffTrigger.EXPERTISE_MISMATCH: [
                "Query especializada resuelta satisfactoriamente"
            ],
            HandoffTrigger.USER_REQUEST: [
                "Solicitud específica del usuario cumplida"
            ],
            HandoffTrigger.CAPABILITY_NEEDED: [
                "Capacidad específica utilizada exitosamente"
            ],
            HandoffTrigger.EMERGENCY: [
                "Situación crítica manejada apropiadamente"
            ]
        }
        
        criteria.extend(trigger_criteria.get(trigger, []))
        
        # Criterios basados en contexto
        if context.get('user_mood') == 'frustrated':
            criteria.append("Frustración del usuario aliviada")
        
        if 'goals' in context:
            criteria.append("Progreso hacia objetivos del usuario")
        
        return criteria[:5]  # Limitar a 5 criterios principales
    
    def _estimate_handoff_quality(self, compatibility: float, strategy: HandoffStrategy) -> str:
        """Estima calidad esperada del handoff"""
        
        # Estrategias de alta calidad
        high_quality_strategies = [
            HandoffStrategy.GRADUAL, 
            HandoffStrategy.EXPERTISE_WEIGHTED
        ]
        
        if strategy in high_quality_strategies and compatibility > 0.8:
            return "seamless"
        elif compatibility > 0.7:
            return "smooth"
        elif compatibility > 0.5:
            return "visible"
        else:
            return "abrupt"
    
    def _analyze_engagement_signals(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza señales de engagement del usuario"""
        signals = {
            'level': 'medium',
            'indicators': [],
            'recommendations': []
        }
        
        # Analizar indicadores de engagement
        if 'response_time' in context:
            response_time = context['response_time']
            if response_time < 5:
                signals['indicators'].append('quick_responses')
                signals['level'] = 'high'
            elif response_time > 30:
                signals['indicators'].append('slow_responses')
                signals['level'] = 'low'
        
        if context.get('message_length', 0) > 100:
            signals['indicators'].append('detailed_messages')
            signals['level'] = 'high'
        elif context.get('message_length', 0) < 20:
            signals['indicators'].append('short_messages')
            if signals['level'] != 'high':
                signals['level'] = 'low'
        
        # Generar recomendaciones
        if signals['level'] == 'low':
            signals['recommendations'] = [
                'increase_interaction_frequency',
                'use_engaging_content',
                'ask_direct_questions'
            ]
        elif signals['level'] == 'high':
            signals['recommendations'] = [
                'maintain_momentum',
                'provide_detailed_responses',
                'offer_advanced_options'
            ]
        
        return signals
    
    def _infer_expertise_level(self, context: Dict[str, Any]) -> str:
        """Infiere nivel de expertise del usuario"""
        
        # Indicadores de expertise
        advanced_keywords = [
            'macros', 'periodization', 'progressive_overload',
            'vo2_max', 'lactate_threshold', 'periodization'
        ]
        
        beginner_keywords = [
            'start', 'begin', 'new', 'basic', 'simple', 'help'
        ]
        
        content = str(context.get('last_user_message', '')).lower()
        
        advanced_count = sum(1 for keyword in advanced_keywords if keyword in content)
        beginner_count = sum(1 for keyword in beginner_keywords if keyword in content)
        
        if advanced_count > beginner_count and advanced_count > 0:
            return 'advanced'
        elif beginner_count > 0:
            return 'beginner'
        else:
            return 'intermediate'
    
    def _infer_communication_style(self, context: Dict[str, Any]) -> str:
        """Infiere estilo de comunicación preferido del usuario"""
        
        message = str(context.get('last_user_message', ''))
        
        if len(message) > 200:
            return 'detailed'
        elif len(message) < 50:
            return 'direct'
        elif '?' in message:
            return 'inquisitive'
        else:
            return 'conversational'
    
    async def _generate_fallback_briefing(
        self, 
        handoff_request: HandoffRequest
    ) -> ContextualBriefing:
        """Genera briefing básico para casos de fallo"""
        
        return ContextualBriefing(
            briefing_id=str(uuid.uuid4()),
            target_agent=handoff_request.to_agent,
            user_context={'user_id': handoff_request.user_id},
            conversation_history=['Error en handoff - contexto limitado'],
            current_objectives=['Recuperar conversación', 'Proporcionar asistencia básica'],
            relevant_data={},
            suggested_approach="Iniciar conversación fresh con el usuario",
            potential_challenges=['Falta de contexto debido a error en handoff'],
            success_metrics=['Reestablecer comunicación con usuario'],
            handoff_context=f"Handoff fallido desde {handoff_request.from_agent.value}",
            priority_items=['🚨 Recuperar engagement del usuario'],
            generated_at=datetime.utcnow()
        )
    
    async def _cache_handoff_request(self, request: HandoffRequest) -> None:
        """Cachea solicitud de handoff"""
        try:
            cache_key = f"{self.cache_prefix}:request:{request.handoff_id}"
            await cache_set(
                cache_key,
                request.to_dict(),
                ttl=3600,  # 1 hora
                priority=CachePriority.HIGH
            )
        except Exception as e:
            logger.error(f"Error cacheando solicitud de handoff: {e}")
    
    async def _cache_briefing(self, briefing: ContextualBriefing) -> None:
        """Cachea briefing contextual"""
        try:
            cache_key = f"{self.cache_prefix}:briefing:{briefing.briefing_id}"
            await cache_set(
                cache_key,
                briefing.to_dict(),
                ttl=1800,  # 30 minutos
                priority=CachePriority.HIGH
            )
        except Exception as e:
            logger.error(f"Error cacheando briefing: {e}")
    
    async def _cache_handoff_result(self, result: HandoffResult) -> None:
        """Cachea resultado de handoff"""
        try:
            cache_key = f"{self.cache_prefix}:result:{result.handoff_id}"
            await cache_set(
                cache_key,
                result.to_dict(),
                ttl=7200,  # 2 horas
                priority=CachePriority.MEDIUM
            )
        except Exception as e:
            logger.error(f"Error cacheando resultado de handoff: {e}")
    
    async def _update_performance_metrics(
        self, 
        request: HandoffRequest, 
        result: HandoffResult
    ) -> None:
        """Actualiza métricas de rendimiento"""
        try:
            # Actualizar métricas por usuario
            if request.user_id not in self.performance_metrics:
                self.performance_metrics[request.user_id] = {
                    'total_handoffs': 0,
                    'successful_handoffs': 0,
                    'average_quality': 0.0,
                    'average_execution_time': 0.0
                }
            
            user_metrics = self.performance_metrics[request.user_id]
            user_metrics['total_handoffs'] += 1
            
            if result.success:
                user_metrics['successful_handoffs'] += 1
            
            # Actualizar promedios
            quality_score = self._quality_to_score(result.quality)
            total = user_metrics['total_handoffs']
            
            user_metrics['average_quality'] = (
                (user_metrics['average_quality'] * (total - 1) + quality_score) / total
            )
            
            user_metrics['average_execution_time'] = (
                (user_metrics['average_execution_time'] * (total - 1) + result.execution_time) / total
            )
            
            # Actualizar historial
            if request.user_id not in self.handoff_history:
                self.handoff_history[request.user_id] = []
            
            self.handoff_history[request.user_id].append({
                'handoff_id': request.handoff_id,
                'from_agent': request.from_agent.value,
                'to_agent': request.to_agent.value,
                'quality': result.quality.value,
                'success': result.success,
                'timestamp': result.completed_at.isoformat()
            })
            
            # Mantener solo últimos 50 handoffs
            self.handoff_history[request.user_id] = self.handoff_history[request.user_id][-50:]
            
        except Exception as e:
            logger.error(f"Error actualizando métricas de performance: {e}")
    
    def _quality_to_score(self, quality: HandoffQuality) -> float:
        """Convierte calidad a score numérico"""
        quality_scores = {
            HandoffQuality.SEAMLESS: 1.0,
            HandoffQuality.SMOOTH: 0.8,
            HandoffQuality.VISIBLE: 0.6,
            HandoffQuality.ABRUPT: 0.4,
            HandoffQuality.FAILED: 0.0
        }
        return quality_scores.get(quality, 0.5)
    
    async def get_handoff_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene analíticas de handoffs"""
        try:
            if user_id:
                # Analíticas específicas de usuario
                user_metrics = self.performance_metrics.get(user_id, {})
                user_history = self.handoff_history.get(user_id, [])
                
                return {
                    'user_id': user_id,
                    'metrics': user_metrics,
                    'recent_handoffs': user_history[-10:],  # Últimos 10
                    'quality_trend': self._calculate_quality_trend(user_history),
                    'most_common_transitions': self._analyze_common_transitions(user_history)
                }
            else:
                # Analíticas globales
                total_handoffs = sum(
                    metrics.get('total_handoffs', 0) 
                    for metrics in self.performance_metrics.values()
                )
                
                successful_handoffs = sum(
                    metrics.get('successful_handoffs', 0)
                    for metrics in self.performance_metrics.values()
                )
                
                success_rate = successful_handoffs / total_handoffs if total_handoffs > 0 else 0
                
                return {
                    'total_users': len(self.performance_metrics),
                    'total_handoffs': total_handoffs,
                    'success_rate': success_rate,
                    'average_quality': self._calculate_global_quality(),
                    'most_active_users': self._get_most_active_users(),
                    'common_transitions': self._analyze_all_transitions()
                }
        
        except Exception as e:
            logger.error(f"Error obteniendo analíticas de handoffs: {e}")
            return {}
    
    def _calculate_quality_trend(self, history: List[Dict]) -> List[float]:
        """Calcula tendencia de calidad de handoffs"""
        if not history:
            return []
        
        # Obtener últimos 10 handoffs
        recent = history[-10:]
        quality_scores = []
        
        for handoff in recent:
            quality = HandoffQuality(handoff.get('quality', 'failed'))
            score = self._quality_to_score(quality)
            quality_scores.append(score)
        
        return quality_scores
    
    def _analyze_common_transitions(self, history: List[Dict]) -> List[Dict]:
        """Analiza transiciones comunes para un usuario"""
        transitions = {}
        
        for handoff in history:
            transition = f"{handoff.get('from_agent')} → {handoff.get('to_agent')}"
            transitions[transition] = transitions.get(transition, 0) + 1
        
        # Ordenar por frecuencia
        sorted_transitions = sorted(
            transitions.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [
            {'transition': transition, 'count': count}
            for transition, count in sorted_transitions[:5]
        ]
    
    def _calculate_global_quality(self) -> float:
        """Calcula calidad promedio global"""
        all_qualities = []
        
        for metrics in self.performance_metrics.values():
            if 'average_quality' in metrics:
                all_qualities.append(metrics['average_quality'])
        
        return sum(all_qualities) / len(all_qualities) if all_qualities else 0.0
    
    def _get_most_active_users(self, limit: int = 5) -> List[Dict]:
        """Obtiene usuarios más activos en handoffs"""
        user_activity = [
            {
                'user_id': user_id,
                'total_handoffs': metrics.get('total_handoffs', 0),
                'success_rate': (
                    metrics.get('successful_handoffs', 0) / 
                    metrics.get('total_handoffs', 1)
                )
            }
            for user_id, metrics in self.performance_metrics.items()
        ]
        
        # Ordenar por total de handoffs
        user_activity.sort(key=lambda x: x['total_handoffs'], reverse=True)
        
        return user_activity[:limit]
    
    def _analyze_all_transitions(self) -> List[Dict]:
        """Analiza todas las transiciones del sistema"""
        all_transitions = {}
        
        for history in self.handoff_history.values():
            for handoff in history:
                transition = f"{handoff.get('from_agent')} → {handoff.get('to_agent')}"
                all_transitions[transition] = all_transitions.get(transition, 0) + 1
        
        # Ordenar por frecuencia
        sorted_transitions = sorted(
            all_transitions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {'transition': transition, 'count': count}
            for transition, count in sorted_transitions[:10]
        ]


# Instancia global del motor de handoffs
handoff_engine = SmartHandoffEngine()


# Funciones helper para uso sencillo
async def request_smart_handoff(
    from_agent: AgentRole,
    to_agent: AgentRole,
    trigger: HandoffTrigger,
    context: Dict[str, Any],
    user_id: str,
    reason: str,
    session_id: Optional[str] = None,
    priority: int = 5
) -> Tuple[ContextualBriefing, HandoffResult]:
    """Función helper para solicitar y ejecutar handoff"""
    
    # Solicitar handoff
    handoff_request = await handoff_engine.request_handoff(
        from_agent=from_agent,
        to_agent=to_agent,
        trigger=trigger,
        context=context,
        user_id=user_id,
        reason=reason,
        session_id=session_id,
        priority=priority
    )
    
    # Ejecutar handoff
    briefing, result = await handoff_engine.execute_handoff(handoff_request)
    
    return briefing, result


async def get_handoff_analytics(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Función helper para obtener analíticas de handoffs"""
    return await handoff_engine.get_handoff_analytics(user_id)