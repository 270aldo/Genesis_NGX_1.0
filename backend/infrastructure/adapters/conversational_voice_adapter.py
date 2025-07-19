"""
Adaptador híbrido para voz conversacional con fallback inteligente.

Este adaptador integra ElevenLabs Conversational AI 2.0 con fallback automático
al sistema TTS tradicional, proporcionando la mejor experiencia de voz posible.
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable, Union
from enum import Enum
import logging

from clients.elevenlabs_conversational_client import (
    conversational_client,
    ConversationState,
)
from clients.elevenlabs_client import elevenlabs_client
from infrastructure.adapters.hybrid_voice_adapter import hybrid_voice_adapter
from core.logging_config import get_logger
from core.telemetry_loader import telemetry

# Configurar logger
logger = get_logger(__name__)


class ConversationalMode(str, Enum):
    """Modos de operación conversacional."""

    FULL_CONVERSATIONAL = "full_conversational"  # WebSocket bidireccional completo
    TTS_ONLY = "tts_only"  # Solo síntesis de texto a voz
    HYBRID = "hybrid"  # Conversacional con fallback a TTS
    DISABLED = "disabled"  # Deshabilitado


class ConversationalVoiceAdapter:
    """
    Adaptador híbrido para voz conversacional con fallback inteligente.

    Proporciona:
    - Conversaciones bidireccionales en tiempo real (ElevenLabs Conversational AI 2.0)
    - Fallback automático a TTS tradicional si Conversational AI falla
    - Detección inteligente de capacidades según el contexto
    - Monitoreo de rendimiento y calidad
    - Circuit breaker para resilencia
    """

    def __init__(self):
        """Inicializa el adaptador conversacional."""
        self.mode = ConversationalMode.HYBRID
        self.active_conversations = {}
        self.fallback_count = 0
        self.success_count = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_failures = 0
        self.last_failure_time = 0
        self.circuit_breaker_timeout = 300  # 5 minutos

        logger.info("Adaptador conversacional inicializado en modo híbrido")

    async def start_conversation(
        self,
        agent_id: str,
        program_type: str = "PRIME",
        conversation_mode: Optional[ConversationalMode] = None,
        on_audio_chunk: Optional[Callable] = None,
        on_transcript: Optional[Callable] = None,
        on_state_change: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Inicia una conversación con el agente especificado.

        Args:
            agent_id: ID del agente NGX
            program_type: Tipo de programa (PRIME/LONGEVITY)
            conversation_mode: Modo conversacional específico
            on_audio_chunk: Callback para chunks de audio
            on_transcript: Callback para transcripciones
            on_state_change: Callback para cambios de estado

        Returns:
            Dict[str, Any]: Resultado de la inicialización
        """
        start_time = time.time()
        span = None

        if telemetry:
            span = (
                telemetry.start_span("conversational_adapter_start")
                if hasattr(telemetry, "start_span")
                else None
            )
            if span and hasattr(telemetry, "add_span_attribute"):
                telemetry.add_span_attribute(span, "agent_id", agent_id)
                telemetry.add_span_attribute(span, "program_type", program_type)
                telemetry.add_span_attribute(
                    span, "mode", conversation_mode or self.mode.value
                )

        try:
            # Determinar modo de operación
            effective_mode = conversation_mode or self.mode

            # Verificar circuit breaker
            if self._is_circuit_breaker_open():
                logger.warning("Circuit breaker abierto - forzando modo TTS")
                effective_mode = ConversationalMode.TTS_ONLY

            # Intentar conversación completa
            if effective_mode in [
                ConversationalMode.FULL_CONVERSATIONAL,
                ConversationalMode.HYBRID,
            ] or (
                isinstance(effective_mode, str)
                and effective_mode.upper() in ["FULL_CONVERSATIONAL", "HYBRID"]
            ):
                try:
                    result = await conversational_client.start_conversation(
                        agent_id=agent_id,
                        program_type=program_type,
                        on_audio_chunk=on_audio_chunk,
                        on_transcript=on_transcript,
                        on_state_change=on_state_change,
                    )

                    if result.get("status") in ["success", "simulated"]:
                        # Conversación conversacional exitosa
                        conversation_id = result.get("conversation_id")
                        self.active_conversations[conversation_id] = {
                            "agent_id": agent_id,
                            "mode": ConversationalMode.FULL_CONVERSATIONAL,
                            "start_time": start_time,
                            "conversational_client": True,
                        }

                        self.success_count += 1
                        self._reset_circuit_breaker()

                        # Agregar información del adaptador
                        result.update(
                            {
                                "adapter_mode": ConversationalMode.FULL_CONVERSATIONAL.value,
                                "fallback_used": False,
                                "conversation_features": {
                                    "bidirectional": True,
                                    "real_time": True,
                                    "turn_detection": True,
                                    "asr_integrated": True,
                                    "low_latency": True,
                                },
                            }
                        )

                        # Telemetría de éxito
                        if telemetry and span:
                            if hasattr(telemetry, "add_span_attribute"):
                                telemetry.add_span_attribute(
                                    span, "adapter_mode", "conversational"
                                )
                                telemetry.add_span_attribute(span, "status", "success")
                            if hasattr(telemetry, "end_span"):
                                telemetry.end_span(span)

                        logger.info(
                            f"Conversación conversacional iniciada exitosamente para {agent_id}"
                        )
                        return result

                    else:
                        # Error en conversacional, intentar fallback si es modo híbrido
                        if effective_mode == ConversationalMode.HYBRID:
                            logger.warning(
                                f"Conversacional falló para {agent_id}, intentando fallback TTS"
                            )
                            self._record_circuit_breaker_failure()
                        else:
                            raise Exception(
                                f"Error en modo conversacional: {result.get('error')}"
                            )

                except Exception as conv_error:
                    logger.error(
                        f"Error en conversacional para {agent_id}: {conv_error}"
                    )
                    self._record_circuit_breaker_failure()

                    if effective_mode != ConversationalMode.HYBRID:
                        raise

            # Fallback a TTS tradicional
            if effective_mode in [
                ConversationalMode.TTS_ONLY,
                ConversationalMode.HYBRID,
            ] or (
                isinstance(effective_mode, str)
                and effective_mode.upper() in ["TTS_ONLY", "HYBRID"]
            ):
                logger.info(f"Usando modo TTS tradicional para {agent_id}")

                # Crear wrapper para callbacks de TTS
                tts_conversation_id = f"tts_{agent_id}_{int(start_time)}"

                self.active_conversations[tts_conversation_id] = {
                    "agent_id": agent_id,
                    "mode": ConversationalMode.TTS_ONLY,
                    "start_time": start_time,
                    "conversational_client": False,
                    "callbacks": {
                        "on_audio_chunk": on_audio_chunk,
                        "on_transcript": on_transcript,
                        "on_state_change": on_state_change,
                    },
                }

                self.fallback_count += 1

                # Resultado de fallback TTS
                duration = time.time() - start_time
                result = {
                    "status": "success",
                    "agent_id": agent_id,
                    "conversation_id": tts_conversation_id,
                    "state": "tts_ready",
                    "duration": duration,
                    "adapter_mode": ConversationalMode.TTS_ONLY.value,
                    "fallback_used": True,
                    "conversation_features": {
                        "bidirectional": False,
                        "real_time": False,
                        "turn_detection": False,
                        "asr_integrated": False,
                        "low_latency": False,
                    },
                }

                # Telemetría de fallback
                if telemetry and span:
                    if hasattr(telemetry, "add_span_attribute"):
                        telemetry.add_span_attribute(
                            span, "adapter_mode", "tts_fallback"
                        )
                        telemetry.add_span_attribute(span, "status", "fallback_success")
                    if hasattr(telemetry, "end_span"):
                        telemetry.end_span(span)

                logger.info(f"Fallback TTS configurado para {agent_id}")
                return result

            # Modo deshabilitado
            elif effective_mode == ConversationalMode.DISABLED or (
                isinstance(effective_mode, str) and effective_mode.upper() == "DISABLED"
            ):
                return {
                    "status": "disabled",
                    "agent_id": agent_id,
                    "message": "Conversaciones de voz deshabilitadas",
                }

            else:
                raise ValueError(f"Modo conversacional no válido: {effective_mode}")

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error en adaptador conversacional para {agent_id}: {e}", exc_info=True
            )

            # Telemetría de error
            if telemetry and span:
                if hasattr(telemetry, "record_exception"):
                    telemetry.record_exception(span, e)
                if hasattr(telemetry, "add_span_attribute"):
                    telemetry.add_span_attribute(span, "status", "error")
                if hasattr(telemetry, "end_span"):
                    telemetry.end_span(span)

            return {
                "status": "error",
                "error": str(e),
                "agent_id": agent_id,
                "duration": duration,
            }

    async def send_message(
        self, conversation_id: str, message: str, message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Envía un mensaje a una conversación activa.

        Args:
            conversation_id: ID de la conversación
            message: Contenido del mensaje
            message_type: Tipo de mensaje (text/audio)

        Returns:
            Dict[str, Any]: Resultado del envío
        """
        try:
            conversation = self.active_conversations.get(conversation_id)
            if not conversation:
                return {
                    "status": "error",
                    "error": "Conversación no encontrada",
                    "conversation_id": conversation_id,
                }

            # Conversación conversacional
            if conversation["conversational_client"]:
                if message_type == "text":
                    success = await conversational_client.send_text_message(message)
                    return {
                        "status": "success" if success else "error",
                        "conversation_id": conversation_id,
                        "message_sent": message,
                        "type": "conversational",
                    }
                else:
                    return {
                        "status": "error",
                        "error": "Tipo de mensaje no soportado en modo conversacional",
                        "conversation_id": conversation_id,
                    }

            # Conversación TTS (fallback)
            else:
                agent_id = conversation["agent_id"]

                # Generar respuesta TTS
                tts_result = await elevenlabs_client.synthesize_speech(
                    text=message,
                    agent_id=agent_id,
                    program_type="PRIME",  # TODO: Obtener del contexto
                )

                if tts_result.get("status") == "success":
                    # Simular callbacks de conversación
                    callbacks = conversation.get("callbacks", {})

                    # Transcript callback
                    if callbacks.get("on_transcript"):
                        await callbacks["on_transcript"](message, "user")
                        await callbacks["on_transcript"](
                            "Respuesta TTS generada", "agent"
                        )

                    # Audio chunk callback (audio en base64)
                    if callbacks.get("on_audio_chunk") and "audio_base64" in tts_result:
                        import base64

                        audio_bytes = base64.b64decode(tts_result["audio_base64"])
                        await callbacks["on_audio_chunk"](audio_bytes)

                    return {
                        "status": "success",
                        "conversation_id": conversation_id,
                        "message_sent": message,
                        "type": "tts_fallback",
                        "audio_generated": True,
                        "tts_result": tts_result,
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Error en TTS: {tts_result.get('error')}",
                        "conversation_id": conversation_id,
                    }

        except Exception as e:
            logger.error(
                f"Error enviando mensaje en conversación {conversation_id}: {e}"
            )
            return {
                "status": "error",
                "error": str(e),
                "conversation_id": conversation_id,
            }

    async def end_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Termina una conversación activa.

        Args:
            conversation_id: ID de la conversación

        Returns:
            Dict[str, Any]: Resultado de la terminación
        """
        try:
            conversation = self.active_conversations.get(conversation_id)
            if not conversation:
                return {
                    "status": "error",
                    "error": "Conversación no encontrada",
                    "conversation_id": conversation_id,
                }

            # Terminar conversación conversacional
            if conversation["conversational_client"]:
                result = await conversational_client.end_conversation()
            else:
                result = {"status": "ended", "type": "tts_fallback"}

            # Remover de conversaciones activas
            del self.active_conversations[conversation_id]

            # Calcular duración
            duration = time.time() - conversation["start_time"]
            result["duration"] = duration
            result["conversation_id"] = conversation_id

            logger.info(
                f"Conversación {conversation_id} terminada (duración: {duration:.2f}s)"
            )
            return result

        except Exception as e:
            logger.error(f"Error terminando conversación {conversation_id}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "conversation_id": conversation_id,
            }

    def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """Obtiene el estado de una conversación específica."""
        conversation = self.active_conversations.get(conversation_id)

        if not conversation:
            return {"status": "not_found", "conversation_id": conversation_id}

        base_status = {
            "conversation_id": conversation_id,
            "agent_id": conversation["agent_id"],
            "mode": conversation["mode"].value,
            "start_time": conversation["start_time"],
            "duration": time.time() - conversation["start_time"],
            "conversational_client": conversation["conversational_client"],
        }

        # Agregar estado específico de conversacional
        if conversation["conversational_client"]:
            conv_status = conversational_client.get_conversation_status()
            base_status.update(conv_status)
        else:
            base_status.update({"state": "tts_ready", "websocket_connected": False})

        return base_status

    def get_adapter_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del adaptador."""
        total_attempts = self.success_count + self.fallback_count

        return {
            "mode": self.mode.value,
            "active_conversations": len(self.active_conversations),
            "total_conversations": total_attempts,
            "successful_conversational": self.success_count,
            "fallback_to_tts": self.fallback_count,
            "success_rate": (
                (self.success_count / total_attempts * 100) if total_attempts > 0 else 0
            ),
            "circuit_breaker": {
                "is_open": self._is_circuit_breaker_open(),
                "failures": self.circuit_breaker_failures,
                "threshold": self.circuit_breaker_threshold,
                "last_failure": self.last_failure_time,
            },
            "conversations": {
                conv_id: {
                    "agent_id": conv["agent_id"],
                    "mode": conv["mode"].value,
                    "duration": time.time() - conv["start_time"],
                }
                for conv_id, conv in self.active_conversations.items()
            },
        }

    def set_mode(self, mode: ConversationalMode):
        """Cambia el modo de operación del adaptador."""
        old_mode = self.mode
        self.mode = mode
        logger.info(f"Modo del adaptador cambiado: {old_mode.value} → {mode.value}")

    def _is_circuit_breaker_open(self) -> bool:
        """Verifica si el circuit breaker está abierto."""
        if self.circuit_breaker_failures < self.circuit_breaker_threshold:
            return False

        # Verificar si ha pasado el tiempo de timeout
        if time.time() - self.last_failure_time > self.circuit_breaker_timeout:
            self._reset_circuit_breaker()
            return False

        return True

    def _record_circuit_breaker_failure(self):
        """Registra un fallo para el circuit breaker."""
        self.circuit_breaker_failures += 1
        self.last_failure_time = time.time()

        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            logger.warning(
                f"Circuit breaker activado después de {self.circuit_breaker_failures} fallos"
            )

    def _reset_circuit_breaker(self):
        """Resetea el circuit breaker."""
        if self.circuit_breaker_failures > 0:
            logger.info("Circuit breaker reseteado - servicio restaurado")
        self.circuit_breaker_failures = 0
        self.last_failure_time = 0


# Instancia global del adaptador conversacional
conversational_voice_adapter = ConversationalVoiceAdapter()
