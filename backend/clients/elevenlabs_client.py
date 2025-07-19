"""
Cliente de ElevenLabs para síntesis de voz con personalidades únicas.

Este módulo proporciona un cliente especializado para interactuar con ElevenLabs,
permitiendo generar voces personalizadas para cada agente NGX con tonos y
personalidades específicas según el programa (PRIME/LONGEVITY).
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional, Union, BinaryIO
from io import BytesIO
from enum import Enum

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

from core.logging_config import get_logger
from core.telemetry_loader import telemetry

# Configurar logger
logger = get_logger(__name__)


class NGXVoicePersonality(str, Enum):
    """Personalidades vocales específicas para cada agente NGX."""

    # Agentes Principales con voces únicas
    NEXUS_ORCHESTRATOR = "nexus_orchestrator"  # INTJ - Autoridad profesional
    BLAZE_ELITE_TRAINING = "blaze_elite_training"  # ESTP - Energía motivacional
    SAGE_NUTRITION = "sage_nutrition"  # ISFJ - Calidez científica
    FLUX_BIOMETRICS = "flux_biometrics"  # INTP - Analítico reflexivo
    SPARK_MOTIVATION = "spark_motivation"  # ENFJ - Motivador empático
    STELLA_PROGRESS = "stella_progress"  # ESFJ - Entusiasta celebratorio
    WAVE_RECOVERY = "wave_recovery"  # ISFP - Sanador equilibrado
    GUARDIAN_SECURITY = "guardian_security"  # ISTJ - Autoridad tranquilizadora
    LINK_INTEGRATION = "link_integration"  # ENTP - Ingeniero eficiente
    PHOENIX_BIOHACKING = "phoenix_biohacking"  # ENTP - Explorador científico
    AURA_CLIENT_SUCCESS = "aura_client_success"  # ESFP - Compañía amistosa
    LUNA_FEMALE_WELLNESS = "luna_female_wellness"  # ENFJ - Empoderamiento maternal
    HELIX_GENETIC = "helix_genetic"  # INTJ - Precisión controlada


class ElevenLabsVoiceClient:
    """
    Cliente avanzado para síntesis de voz con ElevenLabs.

    Proporciona voces personalizadas para cada agente NGX con personalidades
    únicas, adaptación por programa (PRIME/LONGEVITY) y calidad premium.
    """

    # Mapeo de agentes a IDs de voz en ElevenLabs
    # Voces oficiales de ElevenLabs v3 alpha configuradas para GENESIS BETA
    AGENT_VOICE_MAPPING = {
        # NEXUS - Agente Orquestador - Voz de autoridad profesional
        "nexus_orchestrator": {
            "voice_id": "EkK5I93UQWFDigLMpZcX",  # James - Voz masculina autoritaria
            "voice_name": "James",
            "personality": "Consultor profesional con autoridad cálida",
            "style": "Analítico, estratégico, confiado",
            "stability": 0.75,
            "similarity_boost": 0.8,
            "style_exaggeration": 0.2,
        },
        # BLAZE - Elite Training Strategist - Voz energética y motivacional
        "blaze_elite_training": {
            "voice_id": "iP95p4xoKVk53GoZ742B",  # Chris - Voz masculina enérgica
            "voice_name": "Chris",
            "personality": "Entrenador atlético con energía dinámica",
            "style": "Motivacional, enérgico, empoderador",
            "stability": 0.6,
            "similarity_boost": 0.7,
            "style_exaggeration": 0.6,
        },
        # SAGE - Precision Nutrition Architect - Voz científica cálida
        "sage_nutrition": {
            "voice_id": "5l5f8iK3YPeGga21rQIX",  # Adelina - Voz femenina educativa
            "voice_name": "Adelina",
            "personality": "Chef científico con calidez mediterránea",
            "style": "Educativo, nutritivo, cálido",
            "stability": 0.8,
            "similarity_boost": 0.75,
            "style_exaggeration": 0.3,
        },
        # VOLT - Biometrics Insight Engine - Voz analítica reflexiva
        "volt_biometrics": {
            "voice_id": "SOYHLrjzK2X1ezoPC6cr",  # Harry - Voz masculina analítica
            "voice_name": "Harry",
            "personality": "Detective de datos con pausas reflexivas",
            "style": "Analítico, curioso, intelectual",
            "stability": 0.85,
            "similarity_boost": 0.6,
            "style_exaggeration": 0.1,
        },
        # SPARK - Motivation Behavior Coach - Voz empática motivadora
        "spark_motivation": {
            "voice_id": "scOwDtmlUjD3prqpp97I",  # Sam - Voz masculina empática
            "voice_name": "Sam",
            "personality": "Catalizador de cambio con energía adaptativa",
            "style": "Empático, motivador, adaptativo",
            "stability": 0.7,
            "similarity_boost": 0.8,
            "style_exaggeration": 0.5,
        },
        # STELLA - Progress Tracker - Voz entusiasta celebratoria
        "stella_progress": {
            "voice_id": "BZgkqPqms7Kj9ulSkVzn",  # Eve - Voz femenina entusiasta
            "voice_name": "Eve",
            "personality": "Celebrador de logros optimista",
            "style": "Entusiasta, optimista, celebratorio",
            "stability": 0.65,
            "similarity_boost": 0.75,
            "style_exaggeration": 0.7,
        },
        # WAVE - Performance Analytics - Voz analítica equilibrada
        "wave_analytics": {
            "voice_id": "SOYHLrjzK2X1ezoPC6cr",  # Harry - Voz masculina analítica
            "voice_name": "Harry",
            "personality": "Sanador sabio con equilibrio holístico",
            "style": "Tranquilo, equilibrado, sanador",
            "stability": 0.9,
            "similarity_boost": 0.7,
            "style_exaggeration": 0.1,
        },
        # NOVA - Biohacking Innovator - Voz exploradora científica
        "nova_biohacking": {
            "voice_id": "aMSt68OGf4xUZAnLpTU8",  # Juniper - Voz femenina innovadora
            "voice_name": "Juniper",
            "personality": "Explorador del futuro científico",
            "style": "Fascinado, innovador, científico",
            "stability": 0.7,
            "similarity_boost": 0.6,
            "style_exaggeration": 0.6,
        },
        # LUNA - Female Wellness Coach - Voz maternal empoderadora
        "luna_female_wellness": {
            "voice_id": "kdmDKE6EkgrWrrykO9Qt",  # Alexandra - Voz femenina maternal
            "voice_name": "Alexandra",
            "personality": "Compañera de bienestar femenino",
            "style": "Maternal, empoderador, nutritivo",
            "stability": 0.8,
            "similarity_boost": 0.85,
            "style_exaggeration": 0.3,
        },
        # CODE - Genetic Performance Specialist - Voz científica precisa
        "code_genetic": {
            "voice_id": "1SM7GgM6IMuvQlz2BwM3",  # Mark - Voz masculina científica
            "voice_name": "Mark",
            "personality": "Decodificador genético preciso",
            "style": "Científico, preciso, controlado",
            "stability": 0.9,
            "similarity_boost": 0.7,
            "style_exaggeration": 0.2,
        },
    }

    # Adaptaciones por programa
    PROGRAM_ADAPTATIONS = {
        "PRIME": {
            "style_modifier": 0.1,  # Más enérgico y directo
            "stability_modifier": -0.05,  # Menos estable para más dinamismo
            "tone_description": "Estratégico, orientado a performance, directo",
        },
        "LONGEVITY": {
            "style_modifier": -0.1,  # Más tranquilo y preventivo
            "stability_modifier": 0.05,  # Más estable para tranquilidad
            "tone_description": "Preventivo, equilibrado, sostenible",
        },
        "GENERAL": {
            "style_modifier": 0.0,  # Sin modificaciones
            "stability_modifier": 0.0,
            "tone_description": "Equilibrado, adaptativo, versátil",
        },
    }

    def __init__(self):
        """Inicializa el cliente de ElevenLabs."""
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.mock_mode = False

        if not self.api_key:
            logger.warning(
                "Variable de entorno ELEVENLABS_API_KEY no encontrada - activando modo simulado"
            )
            self.mock_mode = True

        # Inicializar cliente si no estamos en modo simulado
        if not self.mock_mode:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
                logger.info("Cliente ElevenLabs inicializado correctamente")
            except Exception as e:
                logger.warning(
                    f"Error al inicializar ElevenLabs: {e} - activando modo simulado"
                )
                self.mock_mode = True

        if self.mock_mode:
            logger.info("Cliente ElevenLabs en MODO SIMULADO")

    def get_agent_voice_config(
        self, agent_id: str, program_type: str = "PRIME"
    ) -> Dict[str, Any]:
        """
        Obtiene la configuración de voz para un agente específico.

        Args:
            agent_id: ID del agente (ej: "blaze_elite_training")
            program_type: Tipo de programa ("PRIME", "LONGEVITY", "GENERAL")

        Returns:
            Dict[str, Any]: Configuración de voz para el agente
        """
        # Obtener configuración base del agente
        base_config = self.AGENT_VOICE_MAPPING.get(agent_id)

        if not base_config:
            logger.warning(
                f"Configuración de voz no encontrada para agente {agent_id}, usando configuración por defecto"
            )
            base_config = self.AGENT_VOICE_MAPPING["nexus_orchestrator"]

        # Obtener adaptaciones del programa
        program_adaptation = self.PROGRAM_ADAPTATIONS.get(
            program_type, self.PROGRAM_ADAPTATIONS["GENERAL"]
        )

        # Aplicar adaptaciones
        adapted_config = base_config.copy()
        adapted_config["stability"] = max(
            0.0,
            min(
                1.0, base_config["stability"] + program_adaptation["stability_modifier"]
            ),
        )
        adapted_config["style_exaggeration"] = max(
            0.0,
            min(
                1.0,
                base_config["style_exaggeration"]
                + program_adaptation["style_modifier"],
            ),
        )
        adapted_config["program_tone"] = program_adaptation["tone_description"]

        return adapted_config

    async def synthesize_speech(
        self,
        text: str,
        agent_id: str,
        program_type: str = "PRIME",
        emotion_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sintetiza texto a voz con la personalidad específica del agente.

        Args:
            text: Texto a sintetizar
            agent_id: ID del agente (ej: "blaze_elite_training")
            program_type: Tipo de programa ("PRIME", "LONGEVITY", "GENERAL")
            emotion_context: Contexto emocional opcional para adaptar el tono

        Returns:
            Dict[str, Any]: Resultados de la síntesis incluyendo audio en base64
        """
        # Iniciar telemetría
        span = None
        start_time = time.time()

        if telemetry:
            span = (
                telemetry.start_span("elevenlabs_speech_synthesis")
                if hasattr(telemetry, "start_span")
                else None
            )
            if span and hasattr(telemetry, "add_span_attribute"):
                telemetry.add_span_attribute(span, "agent_id", agent_id)
                telemetry.add_span_attribute(span, "program_type", program_type)
                telemetry.add_span_attribute(span, "text_length", len(text))
                if emotion_context:
                    telemetry.add_span_attribute(
                        span, "emotion_context", emotion_context
                    )

        try:
            # Si estamos en modo simulado
            if self.mock_mode:
                logger.info(
                    f"MODO SIMULADO - Síntesis para agente {agent_id}: {text[:50]}..."
                )
                duration = time.time() - start_time
                return {
                    "audio_base64": "audio_simulado_elevenlabs",
                    "audio_format": "mp3",
                    "agent_id": agent_id,
                    "voice_personality": f"Simulado para {agent_id}",
                    "program_adaptation": program_type,
                    "text_length": len(text),
                    "duration": duration,
                    "status": "simulated",
                    "provider": "elevenlabs",
                }

            # Obtener configuración de voz para el agente
            voice_config = self.get_agent_voice_config(agent_id, program_type)

            # Crear configuración de voz personalizada
            voice_settings = VoiceSettings(
                stability=voice_config["stability"],
                similarity_boost=voice_config["similarity_boost"],
                style=voice_config["style_exaggeration"],
                use_speaker_boost=True,
            )

            # Adaptar texto si hay contexto emocional
            adapted_text = self._adapt_text_for_emotion(
                text, emotion_context, voice_config
            )

            # Generar audio con ElevenLabs
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_config["voice_id"],
                text=adapted_text,
                model_id="eleven_flash_v2_5",
                output_format="mp3_44100_128",
                voice_settings=voice_settings,
            )

            # Procesar respuesta de audio
            audio_bytes = b""
            try:
                # Si es un generador, combinar fragmentos
                for chunk in audio_generator:
                    if chunk:
                        audio_bytes += chunk
            except TypeError:
                # Si ya es bytes, usar directamente
                audio_bytes = audio_generator

            # Convertir a base64
            import base64

            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

            # Calcular duración
            duration = time.time() - start_time

            # Crear resultado
            result = {
                "audio_base64": audio_base64,
                "audio_format": "mp3",
                "agent_id": agent_id,
                "voice_personality": voice_config["personality"],
                "voice_style": voice_config["style"],
                "program_adaptation": voice_config["program_tone"],
                "emotion_context": emotion_context,
                "text_length": len(text),
                "adapted_text_length": len(adapted_text),
                "voice_settings": {
                    "stability": voice_config["stability"],
                    "similarity_boost": voice_config["similarity_boost"],
                    "style_exaggeration": voice_config["style_exaggeration"],
                },
                "duration": duration,
                "status": "success",
                "provider": "elevenlabs",
            }

            # Registrar en telemetría
            if telemetry and span:
                if hasattr(telemetry, "add_span_attribute"):
                    telemetry.add_span_attribute(span, "duration", duration)
                    telemetry.add_span_attribute(span, "status", "success")
                    telemetry.add_span_attribute(
                        span, "audio_size_bytes", len(audio_bytes)
                    )
                if hasattr(telemetry, "end_span"):
                    telemetry.end_span(span)

                # Métricas
                if hasattr(telemetry, "record_metric"):
                    telemetry.record_metric("elevenlabs_synthesis_duration", duration)
                    telemetry.record_metric("elevenlabs_synthesis_count", 1)
                    telemetry.record_metric("elevenlabs_audio_bytes", len(audio_bytes))

            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error en síntesis de voz ElevenLabs para agente {agent_id}: {e}",
                exc_info=True,
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
                    telemetry.record_metric("elevenlabs_synthesis_error_count", 1)

            return {
                "error": str(e),
                "agent_id": agent_id,
                "program_type": program_type,
                "text_length": len(text),
                "duration": duration,
                "status": "error",
                "provider": "elevenlabs",
            }

    def _adapt_text_for_emotion(
        self, text: str, emotion_context: Optional[str], voice_config: Dict[str, Any]
    ) -> str:
        """
        Adapta el texto según el contexto emocional y la personalidad del agente.

        Args:
            text: Texto original
            emotion_context: Contexto emocional
            voice_config: Configuración de voz del agente

        Returns:
            str: Texto adaptado
        """
        if not emotion_context:
            return text

        # Adaptaciones básicas según emoción
        adaptations = {
            "motivated": {
                "prefix": "",
                "suffix": "",
                "pace": "slightly faster",
            },
            "fatigued": {
                "prefix": "",
                "suffix": ". Tómate tu tiempo.",
                "pace": "slower",
            },
            "frustrated": {
                "prefix": "",
                "suffix": ". Respira profundo.",
                "pace": "calmer",
            },
            "excited": {
                "prefix": "¡",
                "suffix": "!",
                "pace": "energetic",
            },
            "calm": {
                "prefix": "",
                "suffix": "",
                "pace": "steady",
            },
        }

        adaptation = adaptations.get(emotion_context, adaptations["calm"])
        adapted_text = f"{adaptation['prefix']}{text}{adaptation['suffix']}"

        # Log de adaptación para debugging
        if adaptation["prefix"] or adaptation["suffix"]:
            logger.debug(
                f"Texto adaptado para emoción {emotion_context}: {adapted_text}"
            )

        return adapted_text

    async def get_available_voices(self) -> Dict[str, Any]:
        """
        Obtiene las voces disponibles en ElevenLabs.

        Returns:
            Dict[str, Any]: Lista de voces disponibles
        """
        try:
            if self.mock_mode:
                return {
                    "voices": [
                        {
                            "voice_id": voice_id,
                            "name": f"Voz simulada {i}",
                            "language": "es",
                        }
                        for i, voice_id in enumerate(self.AGENT_VOICE_MAPPING.keys())
                    ],
                    "status": "simulated",
                }

            # Obtener voces de ElevenLabs
            voices = self.client.voices.get_all()

            return {
                "voices": [
                    {
                        "voice_id": voice.voice_id,
                        "name": voice.name,
                        "language": getattr(voice, "language", "unknown"),
                        "description": getattr(voice, "description", ""),
                        "preview_url": getattr(voice, "preview_url", None),
                    }
                    for voice in voices.voices
                ],
                "status": "success",
            }

        except Exception as e:
            logger.error(f"Error al obtener voces disponibles: {e}", exc_info=True)
            return {"error": str(e), "status": "error"}

    async def get_agent_voice_preview(
        self, agent_id: str, sample_text: str = None
    ) -> Dict[str, Any]:
        """
        Genera una preview de la voz de un agente específico.

        Args:
            agent_id: ID del agente
            sample_text: Texto de muestra (opcional)

        Returns:
            Dict[str, Any]: Preview de audio del agente
        """
        if not sample_text:
            # Textos de muestra por agente
            sample_texts = {
                "nexus_orchestrator": "Hola, soy NEXUS, tu coordinador estratégico. Analizo tu consulta y te conecto con el especialista perfecto.",
                "blaze_elite_training": "¡Soy BLAZE! Tu entrenador élite. ¡Vamos a llevar tu rendimiento al siguiente nivel con estrategias avanzadas!",
                "sage_nutrition": "Soy SAGE, tu arquitecto nutricional. Te ayudo a crear planes alimentarios personalizados basados en ciencia.",
                "flux_biometrics": "Soy FLUX, especialista en análisis de datos biométricos. Interpreto tus métricas para optimizar tu progreso.",
                "spark_motivation": "¡Hola! Soy SPARK, tu coach motivacional. Estoy aquí para impulsar tu transformación personal.",
                "luna_female_wellness": "Soy LUNA, especialista en bienestar femenino. Te acompaño en cada etapa de tu viaje de salud.",
            }
            sample_text = sample_texts.get(
                agent_id, "Hola, soy tu agente NGX personalizado."
            )

        return await self.synthesize_speech(
            text=sample_text, agent_id=agent_id, program_type="PRIME"
        )


# Instancia global del cliente
elevenlabs_client = ElevenLabsVoiceClient()
