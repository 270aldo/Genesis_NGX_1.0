"""
NEXUS ENHANCED - Skills Manager
==============================

Sistema unificado de gestión de skills para orchestration y client success.
Combina capacidades de coordinación estratégica con funciones de concierge empáticas.

Arquitectura A+ - Skills Layer
Líneas objetivo: <300
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from .core.dependencies import NexusDependencies
from .core.config import NexusConfig, OrchestratorMode, ClientSuccessLevel
from .core.exceptions import (
    NexusError,
    IntentAnalysisError,
    AgentRoutingError,
    OnboardingError,
    MilestoneCelebrationError,
    ProactiveCheckInError,
)
from .core.constants import (
    INTENT_TO_AGENT_MAP,
    CLIENT_SUCCESS_KEYWORDS,
    ProgramType,
    OnboardingStage,
    MilestoneType,
    ClientSuccessEvent,
)

logger = logging.getLogger(__name__)


class NexusSkillsManager:
    """
    Gestor de skills unificado para NEXUS Enhanced.

    Combina orchestration (INTJ - The Architect) con client success (ESFP - The Entertainer)
    para crear experiencias coordinadas estratégicamente pero entregadas con calidez empática.

    Skills implementadas:
    1. analyze_intent_enhanced - Análisis de intención con contexto de client success
    2. synthesize_response_enhanced - Síntesis con toque empático
    3. concierge_onboarding - Onboarding personalizado y cálido
    4. proactive_check_in - Check-ins inteligentes basados en journey
    5. milestone_celebration - Celebración auténtica de logros
    6. support_escalation - Soporte empático con eficiencia
    7. community_facilitation - Facilitación de conexiones genuinas
    """

    def __init__(self, dependencies: NexusDependencies, config: NexusConfig):
        """
        Inicializa el skills manager.

        Args:
            dependencies: Container de dependencias inyectadas
            config: Configuración del orquestador
        """
        self.dependencies = dependencies
        self.config = config
        self._skill_metrics: Dict[str, Dict[str, Any]] = {}
        logger.info("NEXUS Enhanced Skills Manager inicializado")

    async def analyze_intent_enhanced(
        self, user_input: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analiza intención del usuario con contexto de client success.

        Detecta tanto intenciones de orchestration como oportunidades de client success
        para proporcionar el tipo de experiencia más apropiada.

        Args:
            user_input: Input del usuario
            user_id: ID del usuario para contexto

        Returns:
            Dict[str, Any]: Análisis completo con contexto de client success
        """
        start_time = time.time()

        try:
            # Análisis estándar de intención
            intent_result = (
                await self.dependencies.intent_analyzer_adapter.analyze_content(
                    user_input
                )
            )

            # Detectar contexto de client success
            client_success_context = self._analyze_client_success_context(
                user_input, user_id
            )

            # Determinar modo apropiado (orchestration vs concierge)
            recommended_mode = self._determine_response_mode(
                intent_result, client_success_context
            )

            # Enriquecer resultado con contexto de client success
            enhanced_result = {
                "primary_intent": intent_result.get("primary_intent", "general"),
                "secondary_intents": intent_result.get("secondary_intents", []),
                "confidence": intent_result.get("confidence", 0.5),
                "client_success_context": client_success_context,
                "recommended_mode": recommended_mode,
                "requires_empathy": client_success_context.get(
                    "emotional_indicators", False
                ),
                "urgency_level": self._assess_urgency(
                    intent_result, client_success_context
                ),
            }

            # Métricas de performance
            processing_time = (time.time() - start_time) * 1000
            self._record_skill_metric("analyze_intent_enhanced", processing_time, True)

            logger.debug(
                f"Intent analysis enhanced completado en {processing_time:.2f}ms"
            )
            return enhanced_result

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._record_skill_metric("analyze_intent_enhanced", processing_time, False)
            logger.error(f"Error en analyze_intent_enhanced: {e}")
            raise IntentAnalysisError(user_input, context={"error": str(e)})

    async def synthesize_response_enhanced(
        self,
        user_input: str,
        agent_responses: Optional[Dict[str, Dict[str, Any]]] = None,
        client_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Sintetiza respuestas con toque empático y personalización.

        Combina información técnica de agentes especializados con calidez
        empática apropiada para el contexto del usuario.

        Args:
            user_input: Input original del usuario
            agent_responses: Respuestas de agentes especializados
            client_context: Contexto adicional del cliente

        Returns:
            str: Respuesta sintetizada con toque empático
        """
        start_time = time.time()

        try:
            if not agent_responses:
                # Fallback con toque empático
                return await self._generate_empathetic_fallback(
                    user_input, client_context
                )

            # Determinar el tono apropiado basado en contexto
            tone_context = self._determine_response_tone(client_context)

            # Construir respuesta sintetizada
            synthesized_response = ""

            # Intro empático
            if tone_context.get("needs_warmth", False):
                synthesized_response += (
                    "✨ Aquí tienes exactamente lo que necesitas:\n\n"
                )
            else:
                synthesized_response += "**Análisis Completo:**\n\n"

            # Sintetizar respuestas de agentes
            for agent_id, response_data in agent_responses.items():
                if response_data.get("status") == "success" and response_data.get(
                    "output"
                ):
                    # Aplicar adaptación de personalidad si está disponible
                    agent_output = response_data.get("output")
                    if self.dependencies.personality_adapter and client_context:
                        try:
                            from core.personality.personality_adapter import (
                                PersonalityProfile,
                            )

                            profile = PersonalityProfile(
                                program_type=client_context.get(
                                    "program_type", "PRIME"
                                ),
                                preferences=client_context.get("preferences"),
                                emotional_patterns=client_context.get(
                                    "emotional_state"
                                ),
                            )
                            adaptation_result = (
                                self.dependencies.personality_adapter.adapt_response(
                                    agent_id, agent_output, profile, client_context
                                )
                            )
                            agent_output = adaptation_result["adapted_message"]
                        except Exception as e:
                            logger.warning(f"Error aplicando PersonalityAdapter: {e}")

                    synthesized_response += f"{agent_output}\n\n"

            # Closing empático basado en contexto
            closing = self._generate_empathetic_closing(tone_context, client_context)
            synthesized_response += closing

            # Métricas
            processing_time = (time.time() - start_time) * 1000
            self._record_skill_metric(
                "synthesize_response_enhanced", processing_time, True
            )

            return synthesized_response.strip()

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._record_skill_metric(
                "synthesize_response_enhanced", processing_time, False
            )
            logger.error(f"Error en synthesize_response_enhanced: {e}")

            # Fallback empático
            return await self._generate_empathetic_fallback(user_input, client_context)

    async def concierge_onboarding(
        self, user_id: str, program_type: str = "PRIME", stage: str = "welcome"
    ) -> Dict[str, Any]:
        """
        Proporciona onboarding personalizado con nivel concierge.

        Crea experiencia de bienvenida cálida pero profesional,
        adaptada al programa y stage específico del usuario.

        Args:
            user_id: ID del usuario
            program_type: Tipo de programa (PRIME/LONGEVITY)
            stage: Stage del onboarding

        Returns:
            Dict[str, Any]: Plan de onboarding personalizado
        """
        start_time = time.time()

        try:
            # Generar mensaje de bienvenida personalizado
            welcome_message = await self._generate_personalized_welcome(
                program_type, stage
            )

            # Crear roadmap de onboarding
            onboarding_plan = {
                "user_id": user_id,
                "program_type": program_type,
                "current_stage": stage,
                "welcome_message": welcome_message,
                "next_steps": self._get_onboarding_next_steps(stage, program_type),
                "timeline": "Próximos 7 días",
                "support_level": "Concierge 24/7",
                "personalization": {
                    "tone": (
                        "warm_professional"
                        if program_type == "PRIME"
                        else "nurturing_supportive"
                    ),
                    "pace": "efficient" if program_type == "PRIME" else "gradual",
                    "focus": (
                        "results_optimization"
                        if program_type == "PRIME"
                        else "wellness_journey"
                    ),
                },
            }

            # Log evento de onboarding
            if hasattr(self.dependencies, "orchestration_security_service"):
                self.dependencies.orchestration_security_service.log_orchestration_event(
                    event_type="client_success",
                    operation="onboarding_start",
                    user_id=user_id,
                    success=True,
                    response_time_ms=(time.time() - start_time) * 1000,
                )

            processing_time = (time.time() - start_time) * 1000
            self._record_skill_metric("concierge_onboarding", processing_time, True)

            return {
                "status": "success",
                "onboarding_plan": onboarding_plan,
                "next_touchpoint": self._schedule_next_touchpoint(stage),
            }

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._record_skill_metric("concierge_onboarding", processing_time, False)
            logger.error(f"Error en concierge_onboarding: {e}")
            raise OnboardingError(user_id, stage, context={"error": str(e)})

    async def milestone_celebration(
        self, user_id: str, milestone_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Celebra hitos del usuario con entusiasmo genuino.

        Reconoce logros de manera auténtica y motivadora,
        creando momentum positivo para continuar el journey.

        Args:
            user_id: ID del usuario
            milestone_data: Datos del hito alcanzado

        Returns:
            Dict[str, Any]: Celebración personalizada
        """
        start_time = time.time()

        try:
            milestone_type = milestone_data.get("type", "general")
            achievement = milestone_data.get("achievement", "progreso")

            # Generar mensaje de celebración auténtico
            celebration_message = await self._generate_celebration_message(
                milestone_data
            )

            # Crear experiencia de celebración
            celebration_response = {
                "user_id": user_id,
                "milestone_type": milestone_type,
                "celebration_message": celebration_message,
                "achievement_summary": achievement,
                "impact_recognition": self._analyze_achievement_impact(milestone_data),
                "next_goal_suggestion": self._suggest_next_milestone(
                    milestone_type, milestone_data
                ),
                "sharing_opportunity": {
                    "enabled": True,
                    "message": "¿Te gustaría compartir este logro con la comunidad NGX?",
                    "platforms": ["community", "social"],
                },
                "reward_unlock": self._check_reward_eligibility(milestone_data),
            }

            processing_time = (time.time() - start_time) * 1000
            self._record_skill_metric("milestone_celebration", processing_time, True)

            return {
                "status": "success",
                "celebration": celebration_response,
                "follow_up_scheduled": True,
            }

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._record_skill_metric("milestone_celebration", processing_time, False)
            logger.error(f"Error en milestone_celebration: {e}")
            raise MilestoneCelebrationError(
                user_id, milestone_data.get("type", "unknown")
            )

    def _analyze_client_success_context(
        self, user_input: str, user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Analiza contexto de client success en el input del usuario."""
        context = {
            "needs_onboarding": any(
                word in user_input.lower()
                for word in ["new", "getting started", "help", "how to"]
            ),
            "needs_support": any(
                word in user_input.lower()
                for word in ["problem", "issue", "stuck", "error", "help"]
            ),
            "celebration_opportunity": any(
                word in user_input.lower()
                for word in ["achieved", "completed", "goal", "milestone"]
            ),
            "community_engagement": any(
                word in user_input.lower()
                for word in ["community", "connect", "share", "others"]
            ),
            "retention_risk": any(
                word in user_input.lower()
                for word in ["cancel", "quit", "stop", "frustrated"]
            ),
            "emotional_indicators": any(
                word in user_input.lower()
                for word in ["excited", "frustrated", "confused", "happy", "sad"]
            ),
        }

        return context

    def _determine_response_mode(
        self, intent_result: Dict[str, Any], client_context: Dict[str, Any]
    ) -> str:
        """Determina el modo de respuesta apropiado."""
        if any(client_context.values()):
            return "concierge"
        elif intent_result.get("confidence", 0) < 0.7:
            return "hybrid"
        else:
            return "orchestration"

    def _assess_urgency(
        self, intent_result: Dict[str, Any], client_context: Dict[str, Any]
    ) -> str:
        """Evalúa el nivel de urgencia de la consulta."""
        if client_context.get("retention_risk") or client_context.get("needs_support"):
            return "high"
        elif client_context.get("celebration_opportunity"):
            return "medium"
        else:
            return "low"

    async def _generate_empathetic_fallback(
        self, user_input: str, context: Optional[Dict[str, Any]]
    ) -> str:
        """Genera respuesta fallback empática."""
        program_type = context.get("program_type", "PRIME") if context else "PRIME"

        if program_type == "PRIME":
            return f"""Entiendo tu consulta sobre "{user_input[:50]}..." y quiero asegurarme de coordinar la respuesta más estratégica para ti.

**Próximos pasos:**
• Conectarte con el especialista más eficiente
• Proporcionarte información accionable
• Optimizar tu tiempo de respuesta

¿Qué aspecto específico requiere prioridad inmediata? 🎯"""
        else:
            return f"""Entiendo tu consulta sobre "{user_input[:50]}..." y quiero acompañarte para darte exactamente lo que necesitas.

**Opciones disponibles:**
• Guía paso a paso personalizada
• Conexión con nuestro experto apropiado  
• Exploración de alternativas que funcionen para ti

¿Te gustaría que profundice en algún aspecto específico? 💫"""

    def _record_skill_metric(
        self, skill_name: str, processing_time: float, success: bool
    ):
        """Registra métricas de performance de skills."""
        if skill_name not in self._skill_metrics:
            self._skill_metrics[skill_name] = {
                "total_calls": 0,
                "success_calls": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
            }

        metrics = self._skill_metrics[skill_name]
        metrics["total_calls"] += 1
        metrics["total_time"] += processing_time
        metrics["avg_time"] = metrics["total_time"] / metrics["total_calls"]

        if success:
            metrics["success_calls"] += 1

    def get_skills_performance(self) -> Dict[str, Any]:
        """Obtiene métricas de performance de todas las skills."""
        return {
            "skills_metrics": self._skill_metrics,
            "summary": {
                "total_skills": len(self._skill_metrics),
                "total_calls": sum(
                    m["total_calls"] for m in self._skill_metrics.values()
                ),
                "overall_success_rate": sum(
                    m["success_calls"] for m in self._skill_metrics.values()
                )
                / max(sum(m["total_calls"] for m in self._skill_metrics.values()), 1),
                "avg_response_time": sum(
                    m["avg_time"] for m in self._skill_metrics.values()
                )
                / max(len(self._skill_metrics), 1),
            },
        }
