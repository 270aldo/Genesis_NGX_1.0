"""
Adaptador híbrido de voz que combina ElevenLabs y Vertex AI.

Este adaptador proporciona síntesis de voz de alta calidad utilizando
ElevenLabs como proveedor principal y Vertex AI como respaldo, optimizando
para personalidades de agentes y adaptación por programa.
"""

import time
from typing import Dict, Any, Optional, Union
from enum import Enum

from clients.elevenlabs_client import elevenlabs_client
from clients.vertex_ai.speech_client import speech_client
from core.logging_config import get_logger
from core.telemetry_loader import telemetry

# Configurar logger
logger = get_logger(__name__)


class VoiceProvider(str, Enum):
    """Proveedores de síntesis de voz disponibles."""

    ELEVENLABS = "elevenlabs"
    VERTEX_AI = "vertex_ai"
    AUTO = "auto"  # Selección automática


class VoiceQuality(str, Enum):
    """Niveles de calidad de voz."""

    PREMIUM = "premium"  # ElevenLabs con personalidad completa
    STANDARD = "standard"  # ElevenLabs estándar
    BASIC = "basic"  # Vertex AI como respaldo


class HybridVoiceAdapter:
    """
    Adaptador híbrido para síntesis de voz con múltiples proveedores.

    Proporciona síntesis de voz inteligente que:
    - Prioriza ElevenLabs para calidad premium y personalidad
    - Usa Vertex AI como respaldo confiable
    - Adapta automáticamente según disponibilidad y contexto
    - Mantiene consistencia de agente y programa
    """

    def __init__(self):
        """Inicializa el adaptador híbrido."""
        self.elevenlabs_client = elevenlabs_client
        self.vertex_ai_client = speech_client
        self.is_initialized = False

        # Estadísticas de uso
        self.usage_stats = {
            "elevenlabs_calls": 0,
            "vertex_ai_calls": 0,
            "elevenlabs_errors": 0,
            "vertex_ai_errors": 0,
            "total_synthesis_time": 0.0,
            "average_response_time": 0.0,
        }

        logger.info("Adaptador híbrido de voz inicializado")

    async def initialize(self):
        """Inicializa el adaptador y verifica disponibilidad de proveedores."""
        if self.is_initialized:
            return

        try:
            # Verificar disponibilidad de ElevenLabs
            elevenlabs_available = not self.elevenlabs_client.mock_mode

            # Verificar disponibilidad de Vertex AI
            vertex_ai_available = self.vertex_ai_client.vertex_ai_initialized

            logger.info(
                f"Proveedores disponibles - ElevenLabs: {elevenlabs_available}, Vertex AI: {vertex_ai_available}"
            )

            if not elevenlabs_available and not vertex_ai_available:
                logger.warning(
                    "Ningún proveedor de voz está disponible - funcionando en modo simulado"
                )

            self.is_initialized = True

        except Exception as e:
            logger.error(
                f"Error al inicializar adaptador híbrido de voz: {e}", exc_info=True
            )
            raise

    async def synthesize_speech(
        self,
        text: str,
        agent_id: str,
        program_type: str = "PRIME",
        voice_provider: VoiceProvider = VoiceProvider.AUTO,
        voice_quality: VoiceQuality = VoiceQuality.PREMIUM,
        emotion_context: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Sintetiza texto a voz utilizando el mejor proveedor disponible.

        Args:
            text: Texto a sintetizar
            agent_id: ID del agente (para personalidad de voz)
            program_type: Tipo de programa ("PRIME", "LONGEVITY", "GENERAL")
            voice_provider: Proveedor preferido de voz
            voice_quality: Calidad de voz deseada
            emotion_context: Contexto emocional opcional
            **kwargs: Argumentos adicionales para proveedores específicos

        Returns:
            Dict[str, Any]: Resultado de síntesis con metadatos
        """
        if not self.is_initialized:
            await self.initialize()

        # Iniciar telemetría
        span = None
        start_time = time.time()

        if telemetry:
            span = (
                telemetry.start_span("hybrid_voice_synthesis")
                if hasattr(telemetry, "start_span")
                else None
            )
            if span and hasattr(telemetry, "add_span_attribute"):
                telemetry.add_span_attribute(span, "agent_id", agent_id)
                telemetry.add_span_attribute(span, "program_type", program_type)
                telemetry.add_span_attribute(span, "voice_quality", voice_quality.value)
                telemetry.add_span_attribute(span, "text_length", len(text))

        try:
            # Determinar el mejor proveedor
            selected_provider = self._select_optimal_provider(
                voice_provider, voice_quality, agent_id
            )

            logger.debug(
                f"Síntesis de voz para agente {agent_id} usando proveedor {selected_provider}"
            )

            result = None

            # Intentar síntesis con ElevenLabs
            if selected_provider == VoiceProvider.ELEVENLABS:
                try:
                    result = await self._synthesize_with_elevenlabs(
                        text, agent_id, program_type, emotion_context, **kwargs
                    )
                    self.usage_stats["elevenlabs_calls"] += 1

                except Exception as e:
                    logger.warning(f"Error con ElevenLabs, intentando Vertex AI: {e}")
                    self.usage_stats["elevenlabs_errors"] += 1
                    result = await self._synthesize_with_vertex_ai(
                        text, agent_id, program_type, **kwargs
                    )
                    self.usage_stats["vertex_ai_calls"] += 1

            # Intentar síntesis con Vertex AI
            elif selected_provider == VoiceProvider.VERTEX_AI:
                try:
                    result = await self._synthesize_with_vertex_ai(
                        text, agent_id, program_type, **kwargs
                    )
                    self.usage_stats["vertex_ai_calls"] += 1

                except Exception as e:
                    logger.warning(f"Error con Vertex AI, intentando ElevenLabs: {e}")
                    self.usage_stats["vertex_ai_errors"] += 1
                    result = await self._synthesize_with_elevenlabs(
                        text, agent_id, program_type, emotion_context, **kwargs
                    )
                    self.usage_stats["elevenlabs_calls"] += 1

            # Selección automática (ElevenLabs primero)
            else:
                try:
                    result = await self._synthesize_with_elevenlabs(
                        text, agent_id, program_type, emotion_context, **kwargs
                    )
                    self.usage_stats["elevenlabs_calls"] += 1

                except Exception as e:
                    logger.info(f"ElevenLabs no disponible, usando Vertex AI: {e}")
                    self.usage_stats["elevenlabs_errors"] += 1
                    result = await self._synthesize_with_vertex_ai(
                        text, agent_id, program_type, **kwargs
                    )
                    self.usage_stats["vertex_ai_calls"] += 1

            # Actualizar estadísticas
            duration = time.time() - start_time
            self.usage_stats["total_synthesis_time"] += duration
            total_calls = (
                self.usage_stats["elevenlabs_calls"]
                + self.usage_stats["vertex_ai_calls"]
            )
            if total_calls > 0:
                self.usage_stats["average_response_time"] = (
                    self.usage_stats["total_synthesis_time"] / total_calls
                )

            # Agregar metadatos del adaptador
            if result:
                result.update(
                    {
                        "hybrid_adapter": {
                            "selected_provider": selected_provider.value,
                            "quality_level": voice_quality.value,
                            "adapter_duration": duration,
                            "usage_stats": self.usage_stats.copy(),
                        }
                    }
                )

            # Registrar en telemetría
            if telemetry and span:
                if hasattr(telemetry, "add_span_attribute"):
                    telemetry.add_span_attribute(
                        span, "selected_provider", selected_provider.value
                    )
                    telemetry.add_span_attribute(span, "adapter_duration", duration)
                    telemetry.add_span_attribute(span, "status", "success")
                if hasattr(telemetry, "end_span"):
                    telemetry.end_span(span)

                # Métricas
                if hasattr(telemetry, "record_metric"):
                    telemetry.record_metric("hybrid_voice_synthesis_duration", duration)
                    telemetry.record_metric("hybrid_voice_synthesis_count", 1)

            return result or {
                "error": "Todos los proveedores de voz fallaron",
                "status": "error",
                "provider": "none",
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error crítico en adaptador híbrido de voz: {e}", exc_info=True
            )

            # Registrar error en telemetría
            if telemetry and span:
                if hasattr(telemetry, "record_exception"):
                    telemetry.record_exception(span, e)
                if hasattr(telemetry, "add_span_attribute"):
                    telemetry.add_span_attribute(span, "status", "error")
                if hasattr(telemetry, "end_span"):
                    telemetry.end_span(span)
                if hasattr(telemetry, "record_metric"):
                    telemetry.record_metric("hybrid_voice_synthesis_error_count", 1)

            return {
                "error": str(e),
                "agent_id": agent_id,
                "duration": duration,
                "status": "error",
                "provider": "hybrid_adapter",
            }

    async def _synthesize_with_elevenlabs(
        self,
        text: str,
        agent_id: str,
        program_type: str,
        emotion_context: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Sintetiza voz usando ElevenLabs."""
        return await self.elevenlabs_client.synthesize_speech(
            text=text,
            agent_id=agent_id,
            program_type=program_type,
            emotion_context=emotion_context,
        )

    async def _synthesize_with_vertex_ai(
        self, text: str, agent_id: str, program_type: str, **kwargs
    ) -> Dict[str, Any]:
        """Sintetiza voz usando Vertex AI con adaptación para agente."""
        # Mapear agente a voz de Vertex AI
        agent_to_vertex_voice = {
            "nexus_orchestrator": "es-ES-Standard-B",
            "blaze_elite_training": "es-ES-Standard-A",
            "sage_nutrition": "es-ES-Standard-C",
            "volt_biometrics": "es-ES-Standard-D",
            "spark_motivation": "es-ES-Wavenet-B",
            "stella_progress": "es-ES-Wavenet-C",
            "wave_recovery": "es-ES-Standard-A",
            "guardian_security": "es-ES-Standard-B",
            "node_integration": "es-ES-Standard-C",
            "nova_biohacking": "es-ES-Wavenet-B",
            "aura_client_success": "es-ES-Wavenet-C",
            "luna_female_wellness": "es-ES-Standard-A",
            "code_genetic": "es-ES-Standard-D",
        }

        voice_name = agent_to_vertex_voice.get(agent_id, "es-ES-Standard-B")

        result = await self.vertex_ai_client.synthesize_speech(
            text=text, voice_name=voice_name, language_code="es-ES"
        )

        # Adaptar formato de respuesta para consistencia
        if result.get("status") == "success":
            result.update(
                {
                    "agent_id": agent_id,
                    "voice_personality": f"Vertex AI voice for {agent_id}",
                    "program_adaptation": program_type,
                    "provider": "vertex_ai",
                }
            )

        return result

    def _select_optimal_provider(
        self, voice_provider: VoiceProvider, voice_quality: VoiceQuality, agent_id: str
    ) -> VoiceProvider:
        """
        Selecciona el proveedor óptimo basado en preferencias y disponibilidad.

        Args:
            voice_provider: Proveedor preferido
            voice_quality: Calidad deseada
            agent_id: ID del agente

        Returns:
            VoiceProvider: Proveedor seleccionado
        """
        # Si se especifica un proveedor específico
        if voice_provider in [VoiceProvider.ELEVENLABS, VoiceProvider.VERTEX_AI]:
            return voice_provider

        # Selección automática basada en calidad
        if voice_quality == VoiceQuality.PREMIUM:
            # Para calidad premium, preferir ElevenLabs
            if not self.elevenlabs_client.mock_mode:
                return VoiceProvider.ELEVENLABS
            else:
                return VoiceProvider.VERTEX_AI

        elif voice_quality == VoiceQuality.BASIC:
            # Para calidad básica, usar Vertex AI
            if self.vertex_ai_client.vertex_ai_initialized:
                return VoiceProvider.VERTEX_AI
            else:
                return VoiceProvider.ELEVENLABS

        else:  # STANDARD
            # Para calidad estándar, preferir ElevenLabs pero aceptar Vertex AI
            if not self.elevenlabs_client.mock_mode:
                return VoiceProvider.ELEVENLABS
            else:
                return VoiceProvider.VERTEX_AI

    async def get_voice_capabilities(self) -> Dict[str, Any]:
        """
        Obtiene las capacidades disponibles de ambos proveedores.

        Returns:
            Dict[str, Any]: Capacidades de voz disponibles
        """
        capabilities = {
            "providers": {},
            "agents_supported": list(self.elevenlabs_client.AGENT_VOICE_MAPPING.keys()),
            "programs_supported": ["PRIME", "LONGEVITY", "GENERAL"],
            "emotion_contexts": [
                "motivated",
                "fatigued",
                "frustrated",
                "excited",
                "calm",
            ],
            "quality_levels": [q.value for q in VoiceQuality],
        }

        # Capacidades de ElevenLabs
        try:
            elevenlabs_voices = await self.elevenlabs_client.get_available_voices()
            capabilities["providers"]["elevenlabs"] = {
                "available": not self.elevenlabs_client.mock_mode,
                "voices": elevenlabs_voices.get("voices", []),
                "features": [
                    "personality_adaptation",
                    "emotion_context",
                    "program_adaptation",
                    "premium_quality",
                ],
            }
        except Exception as e:
            logger.error(f"Error obteniendo capacidades de ElevenLabs: {e}")
            capabilities["providers"]["elevenlabs"] = {
                "available": False,
                "error": str(e),
            }

        # Capacidades de Vertex AI
        capabilities["providers"]["vertex_ai"] = {
            "available": self.vertex_ai_client.vertex_ai_initialized,
            "voices": [
                "es-ES-Standard-A",
                "es-ES-Standard-B",
                "es-ES-Standard-C",
                "es-ES-Standard-D",
                "es-ES-Wavenet-B",
                "es-ES-Wavenet-C",
            ],
            "features": ["reliable_fallback", "standard_quality", "low_latency"],
        }

        return capabilities

    async def test_all_agent_voices(
        self, sample_text: str = "Hola, soy tu asistente NGX personalizado."
    ) -> Dict[str, Any]:
        """
        Prueba las voces de todos los agentes para verificación.

        Args:
            sample_text: Texto de prueba

        Returns:
            Dict[str, Any]: Resultados de prueba para todos los agentes
        """
        test_results = {}

        for agent_id in self.elevenlabs_client.AGENT_VOICE_MAPPING.keys():
            try:
                result = await self.synthesize_speech(
                    text=sample_text,
                    agent_id=agent_id,
                    program_type="PRIME",
                    voice_quality=VoiceQuality.PREMIUM,
                )

                test_results[agent_id] = {
                    "status": result.get("status", "unknown"),
                    "provider": result.get("provider", "unknown"),
                    "voice_personality": result.get("voice_personality", "N/A"),
                    "duration": result.get("duration", 0),
                    "has_audio": bool(result.get("audio_base64")),
                }

            except Exception as e:
                test_results[agent_id] = {"status": "error", "error": str(e)}

        return {
            "test_results": test_results,
            "total_agents": len(test_results),
            "successful_tests": len(
                [r for r in test_results.values() if r.get("status") == "success"]
            ),
            "usage_stats": self.usage_stats.copy(),
        }


# Instancia global del adaptador híbrido
hybrid_voice_adapter = HybridVoiceAdapter()
