"""
NEXUS ENHANCED - Domain-Specific Exception Hierarchy
===================================================

Sistema de excepciones específicas para orchestration y client success.
Permite manejo granular de errores con contexto específico del dominio.

Arquitectura A+ - Módulo Core
Líneas objetivo: <300
"""

from typing import Dict, Any, Optional, List
import traceback
from datetime import datetime


class NexusError(Exception):
    """
    Excepción base para todos los errores de NEXUS Enhanced.

    Proporciona contexto común y capacidades de logging estructurado
    para orchestration y client success errors.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "NEXUS_UNKNOWN",
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        recoverable: bool = True,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}
        self.user_message = (
            user_message
            or "Ocurrió un error en el sistema. Por favor intenta nuevamente."
        )
        self.recoverable = recoverable
        self.timestamp = datetime.now()
        self.traceback_str = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a diccionario para logging estructurado."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": str(self),
            "user_message": self.user_message,
            "context": self.context,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback_str,
        }


# ===== ORCHESTRATION ERRORS =====


class OrchestrationError(NexusError):
    """Error base para problemas de orchestration."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "ORCHESTRATION_ERROR"),
            user_message=kwargs.get(
                "user_message",
                "Problemas con la coordinación de servicios. Reintentando...",
            ),
            **kwargs,
        )


class IntentAnalysisError(OrchestrationError):
    """Error en análisis de intención del usuario."""

    def __init__(self, user_input: str, confidence: float = 0.0, **kwargs):
        context = kwargs.get("context", {})
        context.update({"user_input": user_input, "confidence": confidence})

        super().__init__(
            f"No se pudo analizar la intención del usuario: {user_input[:50]}...",
            error_code="INTENT_ANALYSIS_FAILED",
            context=context,
            user_message="No entendí tu consulta. ¿Podrías reformularla de otra manera?",
            **kwargs,
        )


class AgentRoutingError(OrchestrationError):
    """Error en routing a agentes especializados."""

    def __init__(self, intent: str, available_agents: List[str], **kwargs):
        context = kwargs.get("context", {})
        context.update({"intent": intent, "available_agents": available_agents})

        super().__init__(
            f"No se encontró agente apropiado para intención: {intent}",
            error_code="AGENT_ROUTING_FAILED",
            context=context,
            user_message="No estoy seguro de cómo ayudarte con esa consulta específica. ¿Podrías ser más específico?",
            **kwargs,
        )


class AgentCommunicationError(OrchestrationError):
    """Error en comunicación con agentes especializados."""

    def __init__(self, agent_id: str, operation: str, **kwargs):
        context = kwargs.get("context", {})
        context.update({"agent_id": agent_id, "operation": operation})

        super().__init__(
            f"Error comunicándose con agente {agent_id} para operación: {operation}",
            error_code="AGENT_COMMUNICATION_ERROR",
            context=context,
            user_message="Problemas temporales conectando con nuestros especialistas. Reintentando...",
            **kwargs,
        )


class ResponseSynthesisError(OrchestrationError):
    """Error en síntesis de respuestas de múltiples agentes."""

    def __init__(self, agent_responses: Dict[str, Any], **kwargs):
        context = kwargs.get("context", {})
        context.update(
            {
                "agent_count": len(agent_responses),
                "agents": list(agent_responses.keys()),
            }
        )

        super().__init__(
            f"Error sintetizando respuestas de {len(agent_responses)} agentes",
            error_code="RESPONSE_SYNTHESIS_ERROR",
            context=context,
            user_message="Tuve dificultades consolidando la información. Por favor, intenta de nuevo.",
            **kwargs,
        )


# ===== CLIENT SUCCESS ERRORS =====


class ClientSuccessError(NexusError):
    """Error base para problemas de client success."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "CLIENT_SUCCESS_ERROR"),
            user_message=kwargs.get(
                "user_message",
                "Problemas con el sistema de soporte. Nuestro equipo está trabajando en ello.",
            ),
            **kwargs,
        )


class OnboardingError(ClientSuccessError):
    """Error durante proceso de onboarding."""

    def __init__(self, user_id: str, onboarding_stage: str, **kwargs):
        context = kwargs.get("context", {})
        context.update({"user_id": user_id, "onboarding_stage": onboarding_stage})

        super().__init__(
            f"Error en onboarding para usuario {user_id} en stage: {onboarding_stage}",
            error_code="ONBOARDING_ERROR",
            context=context,
            user_message="Problemas con tu proceso de bienvenida. Te ayudaré de otra manera.",
            **kwargs,
        )


class MilestoneCelebrationError(ClientSuccessError):
    """Error en celebración de hitos del usuario."""

    def __init__(self, user_id: str, milestone_type: str, **kwargs):
        context = kwargs.get("context", {})
        context.update({"user_id": user_id, "milestone_type": milestone_type})

        super().__init__(
            f"Error celebrando milestone {milestone_type} para usuario {user_id}",
            error_code="MILESTONE_CELEBRATION_ERROR",
            context=context,
            user_message="¡Felicitaciones por tu logro! Aunque tuve problemas con la celebración formal.",
            recoverable=True,
            **kwargs,
        )


class ProactiveCheckInError(ClientSuccessError):
    """Error en check-ins proactivos."""

    def __init__(self, user_id: str, check_in_type: str, **kwargs):
        context = kwargs.get("context", {})
        context.update({"user_id": user_id, "check_in_type": check_in_type})

        super().__init__(
            f"Error en check-in proactivo {check_in_type} para usuario {user_id}",
            error_code="PROACTIVE_CHECKIN_ERROR",
            context=context,
            user_message="Quería conectar contigo pero tengo problemas técnicos. ¿Cómo va todo?",
            **kwargs,
        )


class CommunityFacilitationError(ClientSuccessError):
    """Error en facilitación de comunidad."""

    def __init__(self, operation: str, **kwargs):
        context = kwargs.get("context", {})
        context.update({"operation": operation})

        super().__init__(
            f"Error en facilitación de comunidad: {operation}",
            error_code="COMMUNITY_FACILITATION_ERROR",
            context=context,
            user_message="Problemas conectando con la comunidad en este momento.",
            **kwargs,
        )


# ===== CONVERSATIONAL ERRORS =====


class ConversationalError(NexusError):
    """Error base para capacidades conversacionales."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "CONVERSATIONAL_ERROR"),
            user_message=kwargs.get(
                "user_message",
                "Problemas con la conversación de voz. Continuemos por texto.",
            ),
            **kwargs,
        )


class VoiceProcessingError(ConversationalError):
    """Error en procesamiento de voz."""

    def __init__(self, operation: str, provider: str = "elevenlabs", **kwargs):
        context = kwargs.get("context", {})
        context.update({"operation": operation, "provider": provider})

        super().__init__(
            f"Error en procesamiento de voz: {operation} con {provider}",
            error_code="VOICE_PROCESSING_ERROR",
            context=context,
            user_message="Problemas con el audio. Puedo continuar ayudándote por texto.",
            **kwargs,
        )


class ConversationFlowError(ConversationalError):
    """Error en flujo de conversación."""

    def __init__(self, conversation_id: str, flow_stage: str, **kwargs):
        context = kwargs.get("context", {})
        context.update({"conversation_id": conversation_id, "flow_stage": flow_stage})

        super().__init__(
            f"Error en flujo de conversación {conversation_id} en stage: {flow_stage}",
            error_code="CONVERSATION_FLOW_ERROR",
            context=context,
            user_message="Problema con la conversación. ¿Podemos reiniciar?",
            **kwargs,
        )


# ===== CONFIGURATION AND SYSTEM ERRORS =====


class ConfigurationError(NexusError):
    """Error en configuración del sistema."""

    def __init__(self, config_key: str, expected_value: Any = None, **kwargs):
        context = kwargs.get("context", {})
        context.update({"config_key": config_key, "expected_value": expected_value})

        super().__init__(
            f"Error de configuración: {config_key}",
            error_code="CONFIGURATION_ERROR",
            context=context,
            user_message="Problemas de configuración del sistema. El equipo técnico está revisando.",
            recoverable=False,
            **kwargs,
        )


class DependencyError(NexusError):
    """Error en dependencias del sistema."""

    def __init__(self, dependency_name: str, operation: str, **kwargs):
        context = kwargs.get("context", {})
        context.update({"dependency": dependency_name, "operation": operation})

        super().__init__(
            f"Dependencia {dependency_name} no disponible para: {operation}",
            error_code="DEPENDENCY_ERROR",
            context=context,
            user_message="Servicios temporalmente no disponibles. Reintentando en un momento.",
            **kwargs,
        )


class TimeoutError(NexusError):
    """Error por timeout en operaciones."""

    def __init__(self, operation: str, timeout_seconds: float, **kwargs):
        context = kwargs.get("context", {})
        context.update({"operation": operation, "timeout_seconds": timeout_seconds})

        super().__init__(
            f"Timeout en operación {operation} después de {timeout_seconds}s",
            error_code="OPERATION_TIMEOUT",
            context=context,
            user_message="La operación está tomando más tiempo del esperado. Por favor intenta nuevamente.",
            **kwargs,
        )


# ===== UTILITY FUNCTIONS =====


def create_error_response(
    error: NexusError, include_debug: bool = False
) -> Dict[str, Any]:
    """
    Crea respuesta estructurada para errores de NEXUS.

    Args:
        error: La excepción de NEXUS
        include_debug: Si incluir información de debugging

    Returns:
        Dict[str, Any]: Respuesta estructurada para el cliente
    """
    response = {
        "status": "error",
        "error_code": error.error_code,
        "message": error.user_message,
        "recoverable": error.recoverable,
        "timestamp": error.timestamp.isoformat(),
    }

    if include_debug:
        response["debug"] = {
            "technical_message": str(error),
            "context": error.context,
            "error_type": error.__class__.__name__,
        }

    return response


def is_recoverable_error(error: Exception) -> bool:
    """
    Determina si un error es recuperable.

    Args:
        error: La excepción a evaluar

    Returns:
        bool: True si el error es recuperable
    """
    if isinstance(error, NexusError):
        return error.recoverable

    # Errores comunes que son generalmente recuperables
    recoverable_types = (
        ConnectionError,
        TimeoutError,
        OSError,
    )

    return isinstance(error, recoverable_types)
