"""
API endpoints para conversaciones de voz bidireccionales con ElevenLabs Conversational AI 2.0.

Este módulo proporciona endpoints REST para gestionar conversaciones en tiempo real
con agentes NGX usando WebSockets de ElevenLabs.
"""

import asyncio
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import uuid
import time
import json

from core.logging_config import get_logger
from infrastructure.adapters.conversational_voice_adapter import (
    conversational_voice_adapter,
    ConversationalMode,
)
from agents.orchestrator.agent import NGXNexusOrchestrator
from app.auth import get_current_user

# Configurar logger
logger = get_logger(__name__)

# Router para endpoints conversacionales
router = APIRouter(prefix="/conversational", tags=["Conversational AI"])


# =============================================================================
# MODELOS PYDANTIC PARA REQUESTS/RESPONSES
# =============================================================================


class StartConversationRequest(BaseModel):
    """Request para iniciar una conversación conversacional."""

    agent_id: str = Field(default="nexus_orchestrator", description="ID del agente NGX")
    program_type: str = Field(
        default="PRIME", description="Tipo de programa (PRIME/LONGEVITY)"
    )
    conversation_mode: Optional[str] = Field(
        None, description="Modo conversacional específico"
    )
    user_preferences: Optional[Dict[str, Any]] = Field(
        None, description="Preferencias del usuario"
    )


class SendMessageRequest(BaseModel):
    """Request para enviar un mensaje durante la conversación."""

    conversation_id: str = Field(..., description="ID de la conversación")
    message: str = Field(..., description="Contenido del mensaje")
    message_type: str = Field(
        default="text", description="Tipo de mensaje (text/audio)"
    )


class ConversationStatusResponse(BaseModel):
    """Response con el estado de una conversación."""

    conversation_id: str
    agent_id: str
    state: str
    websocket_connected: bool
    duration: float
    features: Dict[str, bool]


class ConversationListResponse(BaseModel):
    """Response con lista de conversaciones activas."""

    active_conversations: List[ConversationStatusResponse]
    total_count: int
    adapter_statistics: Dict[str, Any]


# =============================================================================
# ENDPOINTS REST PARA GESTIÓN DE CONVERSACIONES
# =============================================================================


@router.post("/start", response_model=Dict[str, Any])
async def start_conversation(
    request: StartConversationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Inicia una nueva conversación de voz bidireccional.

    Esta función inicia una conversación WebSocket con ElevenLabs Conversational AI 2.0,
    proporcionando capacidades de conversación en tiempo real con latencia ultra-baja.
    """
    try:
        logger.info(
            f"Iniciando conversación para usuario {current_user.get('user_id')} con agente {request.agent_id}"
        )

        # Inicializar agente NEXUS
        nexus_agent = NGXNexusOrchestrator()

        # Verificar capacidades conversacionales
        conv_status = nexus_agent.get_conversational_status()
        if not conv_status.get("conversational_available"):
            raise HTTPException(
                status_code=503, detail="Conversational capabilities not available"
            )

        # Iniciar conversación usando el skill del agente
        result = await nexus_agent._skill_start_conversation(
            program_type=request.program_type,
            conversation_mode=request.conversation_mode,
        )

        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start conversation: {result.get('error')}",
            )

        # Agregar metadatos del usuario
        result["user_id"] = current_user.get("user_id")
        result["user_preferences"] = request.user_preferences
        result["api_endpoint"] = "conversational/start"

        logger.info(
            f"Conversación iniciada exitosamente: {result.get('conversation_id')}"
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error iniciando conversación: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/send-message", response_model=Dict[str, Any])
async def send_message(
    request: SendMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Envía un mensaje durante una conversación activa.

    Permite enviar mensajes de texto que serán procesados por el agente
    y respondidos a través del WebSocket conversacional.
    """
    try:
        logger.info(f"Enviando mensaje en conversación {request.conversation_id}")

        # Enviar mensaje a través del adaptador conversacional
        result = await conversational_voice_adapter.send_message(
            conversation_id=request.conversation_id,
            message=request.message,
            message_type=request.message_type,
        )

        if result.get("status") == "error":
            raise HTTPException(
                status_code=400, detail=f"Failed to send message: {result.get('error')}"
            )

        # Agregar metadatos
        result["user_id"] = current_user.get("user_id")
        result["timestamp"] = time.time()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enviando mensaje: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/end/{conversation_id}", response_model=Dict[str, Any])
async def end_conversation(
    conversation_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Termina una conversación conversacional activa.

    Cierra la conexión WebSocket y limpia los recursos asociados.
    """
    try:
        logger.info(f"Terminando conversación {conversation_id}")

        # Terminar conversación a través del adaptador
        result = await conversational_voice_adapter.end_conversation(conversation_id)

        # Agregar metadatos
        result["user_id"] = current_user.get("user_id")
        result["ended_at"] = time.time()

        logger.info(f"Conversación {conversation_id} terminada exitosamente")
        return result

    except Exception as e:
        logger.error(
            f"Error terminando conversación {conversation_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to end conversation: {str(e)}"
        )


@router.get("/status/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation_status(
    conversation_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene el estado actual de una conversación específica.

    Proporciona información detallada sobre el estado de la conversación,
    conexión WebSocket, y estadísticas de rendimiento.
    """
    try:
        # Obtener estado de la conversación
        status = conversational_voice_adapter.get_conversation_status(conversation_id)

        if status.get("status") == "not_found":
            raise HTTPException(
                status_code=404, detail=f"Conversation {conversation_id} not found"
            )

        # Agregar metadatos del usuario
        status["user_id"] = current_user.get("user_id")
        status["checked_at"] = time.time()

        return status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estado de conversación {conversation_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get conversation status: {str(e)}"
        )


@router.get("/list", response_model=Dict[str, Any])
async def list_conversations(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Lista todas las conversaciones activas del usuario.

    Proporciona una vista general de todas las conversaciones en progreso
    y estadísticas del adaptador conversacional.
    """
    try:
        # Obtener estadísticas del adaptador
        adapter_stats = conversational_voice_adapter.get_adapter_statistics()

        # Filtrar conversaciones (en un entorno real, filtrar por user_id)
        conversations = adapter_stats.get("conversations", {})

        # Convertir a formato de respuesta
        conversation_list = []
        for conv_id, conv_data in conversations.items():
            conversation_list.append(
                {
                    "conversation_id": conv_id,
                    "agent_id": conv_data.get("agent_id"),
                    "mode": conv_data.get("mode"),
                    "duration": conv_data.get("duration"),
                    "state": "active",  # Simplificado
                }
            )

        response = {
            "active_conversations": conversation_list,
            "total_count": len(conversation_list),
            "adapter_statistics": {
                "mode": adapter_stats.get("mode"),
                "success_rate": adapter_stats.get("success_rate"),
                "total_conversations": adapter_stats.get("total_conversations"),
                "circuit_breaker": adapter_stats.get("circuit_breaker"),
            },
            "user_id": current_user.get("user_id"),
            "retrieved_at": time.time(),
        }

        return response

    except Exception as e:
        logger.error(f"Error listando conversaciones: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to list conversations: {str(e)}"
        )


@router.get("/capabilities", response_model=Dict[str, Any])
async def get_conversational_capabilities(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Obtiene las capacidades conversacionales disponibles.

    Proporciona información sobre agentes disponibles, modos de conversación,
    y características técnicas del sistema conversacional.
    """
    try:
        # Inicializar agente NEXUS para obtener capacidades
        nexus_agent = NGXNexusOrchestrator()
        nexus_status = nexus_agent.get_conversational_status()

        # Obtener estadísticas del adaptador
        adapter_stats = conversational_voice_adapter.get_adapter_statistics()

        capabilities = {
            "conversational_available": nexus_status.get(
                "conversational_available", False
            ),
            "nexus_personality": nexus_status.get("nexus_personality", {}),
            "supported_agents": [
                {
                    "agent_id": "nexus_orchestrator",
                    "name": "NEXUS - Strategic Orchestrator",
                    "description": "Master coordinator with intent analysis and agent routing",
                    "personality": "INTJ - The Architect",
                    "specialization": "Strategic coordination and conversation management",
                },
                {
                    "agent_id": "blaze_elite_training",
                    "name": "BLAZE - Elite Training Strategist",
                    "description": "High-performance training coach with real-time workout guidance",
                    "personality": "ESTP - The Entrepreneur",
                    "specialization": "Real-time workout coaching, form correction, motivational training",
                },
                {
                    "agent_id": "aura_client_success",
                    "name": "AURA - Client Success Liaison",
                    "description": "Warm client success specialist with 24/7 support and community building",
                    "personality": "ESFP - The Entertainer",
                    "specialization": "Onboarding, 24/7 support, celebration, retention, community building",
                },
                {
                    "agent_id": "luna_female_wellness",
                    "name": "LUNA - Female Wellness Coach",
                    "description": "Maternal wellness specialist for all stages of feminine health",
                    "personality": "ENFJ - The Protagonist (maternal variant)",
                    "specialization": "Menstrual cycle support, hormonal guidance, pregnancy wellness, menopause coaching, female training adaptation",
                },
            ],
            "conversation_modes": [
                {
                    "mode": "FULL_CONVERSATIONAL",
                    "description": "Complete bidirectional real-time conversation",
                    "features": [
                        "WebSocket streaming",
                        "Turn detection",
                        "ASR integrated",
                        "Ultra-low latency",
                    ],
                },
                {
                    "mode": "HYBRID",
                    "description": "Conversational with TTS fallback",
                    "features": [
                        "Intelligent fallback",
                        "Circuit breaker protection",
                        "High reliability",
                    ],
                },
                {
                    "mode": "TTS_ONLY",
                    "description": "Traditional text-to-speech only",
                    "features": ["Voice synthesis", "Reliable", "Lower bandwidth"],
                },
            ],
            "technical_features": {
                "latency": "~75ms (flash_v2_5 model)",
                "languages": ["Spanish", "English"],
                "audio_format": "MP3 44.1kHz",
                "websocket_endpoint": "wss://api.elevenlabs.io/v1/convai/conversation",
                "fallback_available": True,
                "circuit_breaker": True,
            },
            "adapter_mode": adapter_stats.get("mode"),
            "system_health": {
                "circuit_breaker_open": adapter_stats.get("circuit_breaker", {}).get(
                    "is_open", False
                ),
                "success_rate": adapter_stats.get("success_rate", 0),
                "active_conversations": adapter_stats.get("active_conversations", 0),
            },
            "user_id": current_user.get("user_id"),
            "queried_at": time.time(),
        }

        return capabilities

    except Exception as e:
        logger.error(
            f"Error obteniendo capacidades conversacionales: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get conversational capabilities: {str(e)}",
        )


# =============================================================================
# WEBSOCKET ENDPOINT PARA EVENTOS EN TIEMPO REAL
# =============================================================================


@router.websocket("/ws/{conversation_id}")
async def conversational_websocket(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint para eventos de conversación en tiempo real.

    Proporciona actualizaciones en tiempo real sobre el estado de la conversación,
    transcripciones, y eventos del sistema conversacional.

    Nota: Este es un WebSocket de monitoreo, no el WebSocket conversacional principal
    que se maneja directamente con ElevenLabs.
    """
    await websocket.accept()
    logger.info(f"WebSocket conectado para conversación {conversation_id}")

    try:
        # Enviar estado inicial
        initial_status = conversational_voice_adapter.get_conversation_status(
            conversation_id
        )
        await websocket.send_json(
            {
                "type": "status_update",
                "conversation_id": conversation_id,
                "data": initial_status,
                "timestamp": time.time(),
            }
        )

        # Loop de monitoreo (simplificado para demo)
        while True:
            try:
                # Esperar mensaje del cliente (heartbeat, comandos, etc.)
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)

                try:
                    data = json.loads(message)
                    message_type = data.get("type")

                    if message_type == "heartbeat":
                        await websocket.send_json(
                            {"type": "heartbeat_response", "timestamp": time.time()}
                        )
                    elif message_type == "get_status":
                        status = conversational_voice_adapter.get_conversation_status(
                            conversation_id
                        )
                        await websocket.send_json(
                            {
                                "type": "status_update",
                                "conversation_id": conversation_id,
                                "data": status,
                                "timestamp": time.time(),
                            }
                        )
                    else:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": f"Unknown message type: {message_type}",
                                "timestamp": time.time(),
                            }
                        )

                except json.JSONDecodeError:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": "Invalid JSON format",
                            "timestamp": time.time(),
                        }
                    )

            except asyncio.TimeoutError:
                # Timeout - enviar heartbeat
                await websocket.send_json(
                    {"type": "heartbeat", "timestamp": time.time()}
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado para conversación {conversation_id}")
    except Exception as e:
        logger.error(f"Error en WebSocket para conversación {conversation_id}: {e}")
        try:
            await websocket.send_json(
                {"type": "error", "message": str(e), "timestamp": time.time()}
            )
        except Exception:
            pass  # WebSocket ya cerrado
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


# =============================================================================
# ENDPOINTS DE ADMINISTRACIÓN
# =============================================================================


@router.post("/admin/set-mode", response_model=Dict[str, Any])
async def set_adapter_mode(
    mode: str, current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Cambia el modo del adaptador conversacional (admin).

    Permite cambiar entre modos FULL_CONVERSATIONAL, HYBRID, TTS_ONLY, DISABLED.
    Requiere permisos de administrador.
    """
    try:
        # TODO: Verificar permisos de admin
        # if not current_user.get("is_admin"):
        #     raise HTTPException(status_code=403, detail="Admin access required")

        # Validar modo
        try:
            conversation_mode = ConversationalMode(mode)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode: {mode}. Available: {[m.value for m in ConversationalMode]}",
            )

        # Cambiar modo
        conversational_voice_adapter.set_mode(conversation_mode)

        logger.info(
            f"Modo del adaptador cambiado a {mode} por usuario {current_user.get('user_id')}"
        )

        return {
            "status": "success",
            "new_mode": mode,
            "changed_by": current_user.get("user_id"),
            "changed_at": time.time(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cambiando modo del adaptador: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to change adapter mode: {str(e)}"
        )


@router.get("/admin/statistics", response_model=Dict[str, Any])
async def get_adapter_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Obtiene estadísticas detalladas del adaptador conversacional (admin).

    Proporciona métricas completas sobre rendimiento, errores, y uso.
    """
    try:
        # TODO: Verificar permisos de admin
        # if not current_user.get("is_admin"):
        #     raise HTTPException(status_code=403, detail="Admin access required")

        stats = conversational_voice_adapter.get_adapter_statistics()

        # Agregar metadatos adicionales
        stats["retrieved_by"] = current_user.get("user_id")
        stats["retrieved_at"] = time.time()

        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get adapter statistics: {str(e)}"
        )


# =============================================================================
# ENDPOINTS ESPECÍFICOS PARA AURA (CLIENT SUCCESS)
# =============================================================================


class AuraOnboardingRequest(BaseModel):
    """Request para iniciar onboarding conversacional con AURA."""

    user_type: str = Field(
        default="new_user",
        description="Tipo de usuario (new_user, returning_user, premium_user)",
    )
    program_type: str = Field(
        default="PRIME", description="Tipo de programa (PRIME/LONGEVITY)"
    )
    user_goals: Optional[List[str]] = Field(
        None, description="Objetivos específicos del usuario"
    )


class AuraSupportRequest(BaseModel):
    """Request para soporte 24/7 con AURA."""

    conversation_id: str = Field(..., description="ID de la conversación activa")
    issue_type: str = Field(
        ..., description="Tipo de problema (technical, billing, feature, guidance)"
    )
    urgency_level: str = Field(
        default="medium", description="Nivel de urgencia (low, medium, high, critical)"
    )
    user_context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto del usuario"
    )


class AuraCelebrationRequest(BaseModel):
    """Request para celebración de logros con AURA."""

    conversation_id: str = Field(..., description="ID de la conversación")
    achievement_type: str = Field(
        ..., description="Tipo de logro (goal_reached, streak, upgrade, completion)"
    )
    milestone_details: Dict[str, Any] = Field(
        ..., description="Detalles específicos del logro"
    )


class AuraRetentionRequest(BaseModel):
    """Request para conversación de retención con AURA."""

    conversation_id: str = Field(..., description="ID de la conversación")
    user_engagement_state: str = Field(
        ..., description="Estado del usuario (declining, inactive, at_risk, churning)"
    )
    retention_strategy: str = Field(
        default="proactive", description="Estrategia de retención"
    )


class AuraCommunityRequest(BaseModel):
    """Request para construcción de comunidad con AURA."""

    conversation_id: str = Field(..., description="ID de la conversación")
    community_action: str = Field(
        ..., description="Acción de comunidad (welcome, event, discussion, connection)"
    )
    community_context: Optional[Dict[str, Any]] = Field(
        None, description="Contexto de la comunidad"
    )


@router.post("/aura/onboarding", response_model=Dict[str, Any])
async def start_aura_onboarding(
    request: AuraOnboardingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Inicia una conversación de onboarding personalizada con AURA.

    AURA proporciona una experiencia de onboarding cálida y acompañante,
    adaptada al tipo de usuario y sus objetivos específicos.
    """
    try:
        logger.info(
            f"Iniciando onboarding AURA para usuario {current_user.get('user_id')}"
        )

        # Importar agente AURA
        from agents.client_success_liaison.agent import ClientSuccessLiaison

        aura_agent = ClientSuccessLiaison()

        # Verificar capacidades conversacionales
        if not aura_agent.conversational_adapter:
            raise HTTPException(
                status_code=503, detail="AURA conversational capabilities not available"
            )

        # Iniciar onboarding conversacional
        result = await aura_agent._skill_start_onboarding_conversation(
            user_type=request.user_type,
            program_type=request.program_type,
            user_goals=request.user_goals,
        )

        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start AURA onboarding: {result.get('error')}",
            )

        # Agregar metadatos del usuario
        result["user_id"] = current_user.get("user_id")
        result["onboarding_type"] = "conversational"
        result["agent_personality"] = "AURA - Warm & Professional Companion"

        logger.info(
            f"Onboarding AURA iniciado exitosamente: {result.get('conversation_id')}"
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error iniciando onboarding AURA: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to start AURA onboarding: {str(e)}"
        )


@router.post("/aura/support", response_model=Dict[str, Any])
async def aura_24_7_support(
    request: AuraSupportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Proporciona soporte conversacional 24/7 con AURA.

    AURA ofrece soporte empático y eficiente, adaptando su respuesta
    al tipo de problema y nivel de urgencia.
    """
    try:
        from agents.client_success_liaison.agent import ClientSuccessLiaison

        aura_agent = ClientSuccessLiaison()

        result = await aura_agent._skill_support_24_7_conversation(
            conversation_id=request.conversation_id,
            issue_type=request.issue_type,
            urgency_level=request.urgency_level,
            user_context=request.user_context,
        )

        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to provide AURA support: {result.get('error')}",
            )

        result["user_id"] = current_user.get("user_id")
        result["support_type"] = "conversational_24_7"

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en soporte AURA: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to provide AURA support: {str(e)}"
        )


@router.post("/aura/celebration", response_model=Dict[str, Any])
async def aura_celebration(
    request: AuraCelebrationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Celebra logros y hitos con AURA.

    AURA celebra los logros del usuario con energía genuina y cálida,
    fortaleciendo la motivación y el engagement.
    """
    try:
        from agents.client_success_liaison.agent import ClientSuccessLiaison

        aura_agent = ClientSuccessLiaison()

        result = await aura_agent._skill_celebration_conversation(
            conversation_id=request.conversation_id,
            achievement_type=request.achievement_type,
            milestone_details=request.milestone_details,
        )

        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start AURA celebration: {result.get('error')}",
            )

        result["user_id"] = current_user.get("user_id")
        result["celebration_style"] = "warm_genuine"

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en celebración AURA: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start AURA celebration: {str(e)}"
        )


@router.post("/aura/retention", response_model=Dict[str, Any])
async def aura_retention(
    request: AuraRetentionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Gestiona conversaciones de retención con AURA.

    AURA aborda la retención con enfoque empático y centrado en valor,
    entendiendo las necesidades del usuario y ofreciendo soluciones.
    """
    try:
        from agents.client_success_liaison.agent import ClientSuccessLiaison

        aura_agent = ClientSuccessLiaison()

        result = await aura_agent._skill_retention_conversation(
            conversation_id=request.conversation_id,
            user_engagement_state=request.user_engagement_state,
            retention_strategy=request.retention_strategy,
        )

        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start AURA retention: {result.get('error')}",
            )

        result["user_id"] = current_user.get("user_id")
        result["retention_approach"] = "empathetic_value_focused"

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en retención AURA: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start AURA retention: {str(e)}"
        )


@router.post("/aura/community", response_model=Dict[str, Any])
async def aura_community_building(
    request: AuraCommunityRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Facilita construcción de comunidad con AURA.

    AURA conecta usuarios, facilita discusiones, y construye una comunidad
    vibrante y comprometida.
    """
    try:
        from agents.client_success_liaison.agent import ClientSuccessLiaison

        aura_agent = ClientSuccessLiaison()

        result = await aura_agent._skill_community_building_conversation(
            conversation_id=request.conversation_id,
            community_action=request.community_action,
            community_context=request.community_context,
        )

        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start AURA community building: {result.get('error')}",
            )

        result["user_id"] = current_user.get("user_id")
        result["community_approach"] = "inclusive_engaging"

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en construcción de comunidad AURA: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start AURA community building: {str(e)}"
        )


# ===== ENDPOINTS CONVERSACIONALES LUNA =====


class LunaMenstrualRequest(BaseModel):
    """Request model para conversación menstrual con LUNA."""

    user_text: str = Field(..., description="Texto del usuario sobre ciclo menstrual")
    menstrual_cycle_day: Optional[int] = Field(
        None, description="Día del ciclo actual (1-28)"
    )
    current_symptoms: Optional[List[str]] = Field(None, description="Síntomas actuales")
    conversation_context: Optional[str] = Field(
        None, description="Contexto de la conversación"
    )
    user_emotion: Optional[str] = Field(None, description="Emoción detectada")


class LunaHormonalRequest(BaseModel):
    """Request model para guía hormonal con LUNA."""

    user_text: str = Field(..., description="Consulta sobre salud hormonal")
    hormonal_concerns: Optional[List[str]] = Field(
        None, description="Preocupaciones específicas"
    )
    life_stage: Optional[str] = Field(None, description="Etapa de vida actual")
    current_treatments: Optional[List[str]] = Field(
        None, description="Tratamientos actuales"
    )
    conversation_id: Optional[str] = Field(None, description="ID de conversación")


class LunaPregnancyRequest(BaseModel):
    """Request model para bienestar en embarazo con LUNA."""

    user_text: str = Field(..., description="Consulta sobre embarazo")
    pregnancy_stage: Optional[str] = Field(None, description="Trimestre o etapa")
    specific_concerns: Optional[List[str]] = Field(
        None, description="Preocupaciones específicas"
    )
    previous_pregnancies: Optional[int] = Field(None, description="Embarazos previos")
    conversation_id: Optional[str] = Field(None, description="ID de conversación")


class LunaMenopauseRequest(BaseModel):
    """Request model para coaching de menopausia con LUNA."""

    user_text: str = Field(..., description="Consulta sobre menopausia")
    menopause_stage: Optional[str] = Field(None, description="Etapa de menopausia")
    symptoms_experienced: Optional[List[str]] = Field(
        None, description="Síntomas experimentados"
    )
    current_management: Optional[List[str]] = Field(None, description="Manejo actual")
    conversation_id: Optional[str] = Field(None, description="ID de conversación")


class LunaTrainingRequest(BaseModel):
    """Request model para adaptación de entrenamiento con LUNA."""

    user_text: str = Field(..., description="Consulta sobre entrenamiento femenino")
    current_cycle_phase: Optional[str] = Field(
        None, description="Fase del ciclo actual"
    )
    fitness_level: Optional[str] = Field(None, description="Nivel de fitness")
    training_goals: Optional[List[str]] = Field(
        None, description="Objetivos de entrenamiento"
    )
    physical_limitations: Optional[List[str]] = Field(
        None, description="Limitaciones físicas"
    )
    conversation_id: Optional[str] = Field(None, description="ID de conversación")


@router.post("/luna/menstrual", response_model=Dict[str, Any])
async def luna_menstrual_conversation(
    request: LunaMenstrualRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Inicia conversación empática sobre ciclo menstrual con LUNA.

    LUNA proporciona apoyo maternal y educación especializada sobre
    el ciclo menstrual, adaptándose a la fase actual y síntomas.
    """
    try:
        from agents.female_wellness_coach.agent import FemaleWellnessCoach
        from agents.female_wellness_coach.schemas import StartMenstrualConversationInput

        luna_agent = FemaleWellnessCoach()

        input_data = StartMenstrualConversationInput(
            user_text=request.user_text,
            menstrual_cycle_day=request.menstrual_cycle_day,
            current_symptoms=request.current_symptoms,
            conversation_context=request.conversation_context,
            user_emotion=request.user_emotion,
        )

        result = await luna_agent._skill_start_menstrual_conversation(input_data)

        # Convertir a dict para respuesta
        response = {
            "conversation_response": result.conversation_response,
            "conversation_id": result.conversation_id,
            "suggested_topics": result.suggested_topics,
            "phase_specific_guidance": result.phase_specific_guidance,
            "user_id": current_user.get("user_id"),
            "agent_personality": "ENFJ - Maternal Empowerment",
            "specialization": "menstrual_cycle_support",
        }

        return response

    except Exception as e:
        logger.error(f"Error en conversación menstrual LUNA: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start LUNA menstrual conversation: {str(e)}",
        )


@router.post("/luna/hormonal", response_model=Dict[str, Any])
async def luna_hormonal_guidance(
    request: LunaHormonalRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Proporciona guía conversacional sobre salud hormonal con LUNA.

    LUNA ofrece educación empática y apoyo sobre desequilibrios hormonales,
    adaptándose a la etapa de vida y preocupaciones específicas.
    """
    try:
        from agents.female_wellness_coach.agent import FemaleWellnessCoach
        from agents.female_wellness_coach.schemas import (
            HormonalGuidanceConversationInput,
        )

        luna_agent = FemaleWellnessCoach()

        input_data = HormonalGuidanceConversationInput(
            user_text=request.user_text,
            hormonal_concerns=request.hormonal_concerns,
            life_stage=request.life_stage,
            current_treatments=request.current_treatments,
            conversation_id=request.conversation_id,
        )

        result = await luna_agent._skill_hormonal_guidance_conversation(input_data)

        response = {
            "guidance_response": result.guidance_response,
            "educational_content": result.educational_content,
            "lifestyle_recommendations": result.lifestyle_recommendations,
            "follow_up_questions": result.follow_up_questions,
            "user_id": current_user.get("user_id"),
            "agent_personality": "ENFJ - Wise Educator",
            "specialization": "hormonal_health_guidance",
        }

        return response

    except Exception as e:
        logger.error(f"Error en guía hormonal LUNA: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start LUNA hormonal guidance: {str(e)}"
        )


@router.post("/luna/pregnancy", response_model=Dict[str, Any])
async def luna_pregnancy_wellness(
    request: LunaPregnancyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Conversación de apoyo para bienestar en embarazo con LUNA.

    LUNA proporciona apoyo maternal experto para todas las etapas
    del embarazo, con guías de seguridad y celebración del proceso.
    """
    try:
        from agents.female_wellness_coach.agent import FemaleWellnessCoach
        from agents.female_wellness_coach.schemas import (
            PregnancyWellnessConversationInput,
        )

        luna_agent = FemaleWellnessCoach()

        input_data = PregnancyWellnessConversationInput(
            user_text=request.user_text,
            pregnancy_stage=request.pregnancy_stage,
            specific_concerns=request.specific_concerns,
            previous_pregnancies=request.previous_pregnancies,
            conversation_id=request.conversation_id,
        )

        result = await luna_agent._skill_pregnancy_wellness_conversation(input_data)

        response = {
            "wellness_response": result.wellness_response,
            "safety_guidelines": result.safety_guidelines,
            "nutrition_tips": result.nutrition_tips,
            "exercise_recommendations": result.exercise_recommendations,
            "user_id": current_user.get("user_id"),
            "agent_personality": "ENFJ - Maternal Support",
            "specialization": "pregnancy_wellness_support",
        }

        return response

    except Exception as e:
        logger.error(f"Error en bienestar de embarazo LUNA: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start LUNA pregnancy wellness: {str(e)}"
        )


@router.post("/luna/menopause", response_model=Dict[str, Any])
async def luna_menopause_coaching(
    request: LunaMenopauseRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Coaching conversacional para manejo de menopausia con LUNA.

    LUNA reencuadra la menopausia como una transición poderosa,
    proporcionando estrategias de manejo y empoderamiento.
    """
    try:
        from agents.female_wellness_coach.agent import FemaleWellnessCoach
        from agents.female_wellness_coach.schemas import (
            MenopauseCoachingConversationInput,
        )

        luna_agent = FemaleWellnessCoach()

        input_data = MenopauseCoachingConversationInput(
            user_text=request.user_text,
            menopause_stage=request.menopause_stage,
            symptoms_experienced=request.symptoms_experienced,
            current_management=request.current_management,
            conversation_id=request.conversation_id,
        )

        result = await luna_agent._skill_menopause_coaching_conversation(input_data)

        response = {
            "coaching_response": result.coaching_response,
            "symptom_management": result.symptom_management,
            "lifestyle_adaptations": result.lifestyle_adaptations,
            "empowerment_message": result.empowerment_message,
            "user_id": current_user.get("user_id"),
            "agent_personality": "ENFJ - Empowering Transition Coach",
            "specialization": "menopause_empowerment_coaching",
        }

        return response

    except Exception as e:
        logger.error(f"Error en coaching de menopausia LUNA: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start LUNA menopause coaching: {str(e)}"
        )


@router.post("/luna/training", response_model=Dict[str, Any])
async def luna_training_adaptation(
    request: LunaTrainingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Conversación sobre adaptación de entrenamiento femenino con LUNA.

    LUNA adapta los entrenamientos al ciclo hormonal natural,
    maximizando resultados mientras honra las necesidades del cuerpo.
    """
    try:
        from agents.female_wellness_coach.agent import FemaleWellnessCoach
        from agents.female_wellness_coach.schemas import (
            FemaleTrainingAdaptationConversationInput,
        )

        luna_agent = FemaleWellnessCoach()

        input_data = FemaleTrainingAdaptationConversationInput(
            user_text=request.user_text,
            current_cycle_phase=request.current_cycle_phase,
            fitness_level=request.fitness_level,
            training_goals=request.training_goals,
            physical_limitations=request.physical_limitations,
            conversation_id=request.conversation_id,
        )

        result = await luna_agent._skill_female_training_adaptation_conversation(
            input_data
        )

        response = {
            "training_response": result.training_response,
            "cycle_specific_workout": result.cycle_specific_workout,
            "intensity_recommendations": result.intensity_recommendations,
            "recovery_guidance": result.recovery_guidance,
            "user_id": current_user.get("user_id"),
            "agent_personality": "ENFJ - Cycle-Wise Trainer",
            "specialization": "female_training_adaptation",
        }

        return response

    except Exception as e:
        logger.error(f"Error en adaptación de entrenamiento LUNA: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start LUNA training adaptation: {str(e)}",
        )
