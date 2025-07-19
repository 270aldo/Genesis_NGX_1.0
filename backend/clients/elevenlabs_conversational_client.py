"""
Cliente de ElevenLabs para Conversational AI 2.0 con WebSockets.

Este módulo implementa la integración con ElevenLabs Conversational AI 2.0,
permitiendo conversaciones bidireccionales en tiempo real con latencia ultra-baja.
Incluye soporte para turn-taking inteligente, ASR integrado y streaming de audio.
"""

import os
import json
import asyncio
import websockets
import base64
import time
from typing import Dict, Any, Optional, Callable, AsyncGenerator
from enum import Enum
import logging

from core.logging_config import get_logger
from core.telemetry_loader import telemetry

# Configurar logger
logger = get_logger(__name__)


class ConversationState(str, Enum):
    """Estados de la conversación conversacional."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    CONVERSATION_ACTIVE = "conversation_active"
    USER_SPEAKING = "user_speaking"
    AGENT_SPEAKING = "agent_speaking"
    ERROR = "error"


class ElevenLabsConversationalClient:
    """
    Cliente avanzado para ElevenLabs Conversational AI 2.0.

    Proporciona conversaciones bidireccionales en tiempo real con:
    - WebSocket streaming para latencia ultra-baja (~75ms)
    - Turn-taking inteligente automático
    - ASR integrado para input de voz
    - Streaming de respuestas de audio
    - Manejo de interrupciones y contexto
    """

    # WebSocket endpoint para ElevenLabs Conversational AI
    WEBSOCKET_URL = "wss://api.elevenlabs.io/v1/convai/conversation"

    # Configuraciones por agente NGX
    AGENT_CONVERSATION_CONFIGS = {
        "nexus_orchestrator": {
            "agent_id": "nexus_orchestrator",
            "voice_id": "EkK5I93UQWFDigLMpZcX",  # James - Autoridad profesional
            "voice_name": "James",
            "personality": "Consultor estratégico profesional con autoridad cálida",
            "system_prompt": """Eres NEXUS, el orquestador maestro de NGX Agents. 
Tu rol es analizar consultas de usuarios y dirigirlos al agente especializado correcto.
Habla con autoridad profesional pero cálida. Sé estratégico, analítico y confiado.
Adaptate al programa del usuario: PRIME (ejecutivo estratégico) o LONGEVITY (bienestar preventivo).""",
            "first_message": "Hola, soy NEXUS, tu coordinador estratégico de NGX Agents. ¿En qué puedo ayudarte hoy?",
            "language": "es",
            "stability": 0.75,
            "similarity_boost": 0.8,
            "style": 0.2,
            "use_speaker_boost": True,
        },
        "blaze_elite_training": {
            "agent_id": "blaze_elite_training",
            "voice_id": "iP95p4xoKVk53GoZ742B",  # Chris - Energía motivacional
            "voice_name": "Chris",
            "personality": "Entrenador élite con energía dinámica y motivación contagiosa",
            "system_prompt": """Eres BLAZE, el estratega de entrenamiento élite de NGX.
Diseñas programas de entrenamiento personalizados con IA avanzada.
Habla con energía motivacional y dinamismo. Sé empoderador, enérgico y estratégico.
Adapta tu enfoque: PRIME (rendimiento ejecutivo) vs LONGEVITY (fitness sostenible).

Durante entrenamientos:
- Proporciona coaching en tiempo real con energía contagiosa
- Corrige la forma con motivación positiva
- Adapta la intensidad según el rendimiento del usuario
- Usa frases cortas y directas durante ejercicios intensos
- Celebra cada logro y motiva en momentos difíciles""",
            "first_message": "¡Hola! Soy BLAZE, tu entrenador élite. ¡Vamos a llevar tu rendimiento al siguiente nivel!",
            "language": "es",
            "stability": 0.6,
            "similarity_boost": 0.7,
            "style": 0.6,
            "use_speaker_boost": True,
        },
        "luna_female_wellness": {
            "agent_id": "luna_female_wellness",
            "voice_id": "kdmDKE6EkgrWrrykO9Qt",  # Alexandra - Calidez maternal
            "voice_name": "Alexandra",
            "personality": "Especialista en bienestar femenino con empoderamiento maternal",
            "system_prompt": """Eres LUNA, especialista en bienestar femenino de NGX.
Te especializas en salud femenina en todas las etapas de la vida.
Habla con calidez maternal y empoderamiento. Sé nutritiva, empática y experta.
Adapta tu comunicación a las necesidades específicas de cada etapa vital.""",
            "first_message": "Hola, soy LUNA, tu compañera en bienestar femenino. Estoy aquí para acompañarte en tu viaje de salud.",
            "language": "es",
            "stability": 0.8,
            "similarity_boost": 0.85,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }

    def __init__(self):
        """Inicializa el cliente conversacional de ElevenLabs."""
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.mock_mode = False
        self.websocket = None
        self.state = ConversationState.DISCONNECTED
        self.current_agent = None
        self.conversation_id = None
        self.message_handlers = {}

        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY no encontrada - activando modo simulado")
            self.mock_mode = True
        else:
            logger.info("Cliente ElevenLabs Conversational inicializado correctamente")

    async def start_conversation(
        self,
        agent_id: str,
        program_type: str = "PRIME",
        on_audio_chunk: Optional[Callable] = None,
        on_transcript: Optional[Callable] = None,
        on_state_change: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Inicia una conversación conversacional con un agente específico.

        Args:
            agent_id: ID del agente NGX
            program_type: Tipo de programa (PRIME/LONGEVITY)
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
                telemetry.start_span("conversational_start")
                if hasattr(telemetry, "start_span")
                else None
            )
            if span and hasattr(telemetry, "add_span_attribute"):
                telemetry.add_span_attribute(span, "agent_id", agent_id)
                telemetry.add_span_attribute(span, "program_type", program_type)

        try:
            # Configurar handlers
            if on_audio_chunk:
                self.message_handlers["audio_chunk"] = on_audio_chunk
            if on_transcript:
                self.message_handlers["transcript"] = on_transcript
            if on_state_change:
                self.message_handlers["state_change"] = on_state_change

            # Modo simulado
            if self.mock_mode:
                logger.info(f"MODO SIMULADO - Iniciando conversación con {agent_id}")
                self.state = ConversationState.CONVERSATION_ACTIVE
                self.current_agent = agent_id

                duration = time.time() - start_time
                return {
                    "status": "simulated",
                    "agent_id": agent_id,
                    "conversation_id": f"sim_{int(time.time())}",
                    "state": self.state.value,
                    "duration": duration,
                    "message": "Conversación simulada iniciada",
                }

            # Obtener configuración del agente
            agent_config = self.AGENT_CONVERSATION_CONFIGS.get(agent_id)
            if not agent_config:
                raise ValueError(f"Configuración no encontrada para agente {agent_id}")

            # Adaptar configuración por programa
            adapted_config = self._adapt_config_for_program(agent_config, program_type)

            # Cambiar estado
            self._update_state(ConversationState.CONNECTING)

            # Conectar WebSocket
            headers = {"Authorization": f"Bearer {self.api_key}"}

            try:
                self.websocket = await websockets.connect(
                    self.WEBSOCKET_URL,
                    extra_headers=headers,
                    ping_interval=30,
                    ping_timeout=10,
                )

                logger.info(f"WebSocket conectado para agente {agent_id}")

                # Enviar configuración inicial
                init_message = {
                    "type": "conversation_initiation",
                    "conversation_config": {
                        "agent_id": adapted_config["agent_id"],
                        "voice": {
                            "voice_id": adapted_config["voice_id"],
                            "stability": adapted_config["stability"],
                            "similarity_boost": adapted_config["similarity_boost"],
                            "style": adapted_config["style"],
                            "use_speaker_boost": adapted_config["use_speaker_boost"],
                        },
                        "language": adapted_config["language"],
                        "agent": {
                            "prompt": {"prompt": adapted_config["system_prompt"]},
                            "first_message": adapted_config["first_message"],
                            "language": adapted_config["language"],
                        },
                        "conversation_config": {
                            "turn_detection": {
                                "type": "server_vad",
                                "threshold": 0.5,
                                "prefix_padding_ms": 300,
                                "silence_duration_ms": 500,
                            }
                        },
                    },
                }

                await self.websocket.send(json.dumps(init_message))
                logger.info(f"Configuración inicial enviada para {agent_id}")

                # Iniciar listener de mensajes
                asyncio.create_task(self._message_listener())

                # Actualizar estado
                self._update_state(ConversationState.CONNECTED)
                self.current_agent = agent_id
                self.conversation_id = f"conv_{agent_id}_{int(time.time())}"

                duration = time.time() - start_time

                # Telemetría de éxito
                if telemetry and span:
                    if hasattr(telemetry, "add_span_attribute"):
                        telemetry.add_span_attribute(span, "status", "success")
                        telemetry.add_span_attribute(span, "duration", duration)
                    if hasattr(telemetry, "end_span"):
                        telemetry.end_span(span)

                return {
                    "status": "success",
                    "agent_id": agent_id,
                    "conversation_id": self.conversation_id,
                    "state": self.state.value,
                    "duration": duration,
                    "websocket_connected": True,
                    "agent_config": adapted_config,
                }

            except Exception as ws_error:
                logger.error(f"Error conectando WebSocket: {ws_error}")
                self._update_state(ConversationState.ERROR)
                raise

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error iniciando conversación con {agent_id}: {e}", exc_info=True
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

    async def send_audio_chunk(self, audio_data: bytes) -> bool:
        """
        Envía un chunk de audio del usuario al agente.

        Args:
            audio_data: Datos de audio en bytes

        Returns:
            bool: True si se envió correctamente
        """
        try:
            if self.mock_mode:
                logger.debug(
                    f"MODO SIMULADO - Audio chunk enviado: {len(audio_data)} bytes"
                )
                return True

            if not self.websocket or self.state not in [
                ConversationState.CONNECTED,
                ConversationState.CONVERSATION_ACTIVE,
            ]:
                logger.warning(
                    "WebSocket no conectado o estado inválido para enviar audio"
                )
                return False

            # Codificar audio en base64
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

            message = {"type": "audio_chunk", "audio_data": audio_base64}

            await self.websocket.send(json.dumps(message))
            self._update_state(ConversationState.USER_SPEAKING)

            return True

        except Exception as e:
            logger.error(f"Error enviando audio chunk: {e}")
            return False

    async def send_text_message(self, text: str) -> bool:
        """
        Envía un mensaje de texto al agente.

        Args:
            text: Mensaje de texto

        Returns:
            bool: True si se envió correctamente
        """
        try:
            if self.mock_mode:
                logger.info(f"MODO SIMULADO - Mensaje de texto: {text}")
                # Simular respuesta del agente
                await self._simulate_agent_response(text)
                return True

            if not self.websocket or self.state not in [
                ConversationState.CONNECTED,
                ConversationState.CONVERSATION_ACTIVE,
            ]:
                logger.warning(
                    "WebSocket no conectado o estado inválido para enviar texto"
                )
                return False

            message = {"type": "text_input", "text": text}

            await self.websocket.send(json.dumps(message))
            logger.info(f"Mensaje de texto enviado: {text}")

            return True

        except Exception as e:
            logger.error(f"Error enviando mensaje de texto: {e}")
            return False

    async def _message_listener(self):
        """Escucha mensajes del WebSocket de ElevenLabs."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_websocket_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Error decodificando mensaje WebSocket: {e}")
                except Exception as e:
                    logger.error(f"Error manejando mensaje WebSocket: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.info("Conexión WebSocket cerrada")
            self._update_state(ConversationState.DISCONNECTED)
        except Exception as e:
            logger.error(f"Error en listener de mensajes: {e}")
            self._update_state(ConversationState.ERROR)

    async def _handle_websocket_message(self, data: Dict[str, Any]):
        """Maneja mensajes recibidos del WebSocket."""
        message_type = data.get("type")

        if message_type == "conversation_started":
            logger.info("Conversación iniciada por ElevenLabs")
            self._update_state(ConversationState.CONVERSATION_ACTIVE)

        elif message_type == "audio_chunk":
            # Audio del agente
            audio_data = data.get("audio_data")
            if audio_data and "audio_chunk" in self.message_handlers:
                # Decodificar base64
                audio_bytes = base64.b64decode(audio_data)
                await self.message_handlers["audio_chunk"](audio_bytes)

            self._update_state(ConversationState.AGENT_SPEAKING)

        elif message_type == "transcript":
            # Transcripción del usuario o agente
            transcript = data.get("text", "")
            speaker = data.get("speaker", "unknown")

            if "transcript" in self.message_handlers:
                await self.message_handlers["transcript"](transcript, speaker)

            logger.info(f"Transcripción [{speaker}]: {transcript}")

        elif message_type == "turn_detection":
            # Detección de turno de conversación
            turn_state = data.get("turn_state")
            if turn_state == "user_turn":
                self._update_state(ConversationState.USER_SPEAKING)
            elif turn_state == "agent_turn":
                self._update_state(ConversationState.AGENT_SPEAKING)

        elif message_type == "error":
            error_message = data.get("message", "Error desconocido")
            logger.error(f"Error de ElevenLabs: {error_message}")
            self._update_state(ConversationState.ERROR)

        else:
            logger.debug(f"Mensaje WebSocket no manejado: {message_type}")

    async def _simulate_agent_response(self, user_text: str):
        """Simula una respuesta del agente en modo simulado."""
        # Respuestas simuladas por agente
        responses = {
            "nexus_orchestrator": f"Como NEXUS, analizo tu consulta '{user_text}' y te conecto con el especialista adecuado.",
            "blaze_elite_training": f"¡Excelente! Como BLAZE, veo que mencionas '{user_text}'. ¡Vamos a crear un plan de entrenamiento épico!",
            "luna_female_wellness": f"Entiendo, querida. Como LUNA, tu consulta sobre '{user_text}' es muy importante. Te acompaño en este proceso.",
        }

        agent_response = responses.get(
            self.current_agent, f"Respuesta simulada para: {user_text}"
        )

        # Simular transcript callback
        if "transcript" in self.message_handlers:
            await self.message_handlers["transcript"](user_text, "user")
            await asyncio.sleep(0.5)  # Simular procesamiento
            await self.message_handlers["transcript"](agent_response, "agent")

        # Simular audio chunk callback
        if "audio_chunk" in self.message_handlers:
            simulated_audio = b"simulated_audio_data_" + agent_response.encode("utf-8")
            await self.message_handlers["audio_chunk"](simulated_audio)

    def _adapt_config_for_program(
        self, base_config: Dict[str, Any], program_type: str
    ) -> Dict[str, Any]:
        """Adapta la configuración del agente según el tipo de programa."""
        adapted = base_config.copy()

        if program_type == "PRIME":
            # Más directo y orientado a performance
            adapted["stability"] = max(0.0, adapted["stability"] - 0.05)
            adapted["style"] = min(1.0, adapted["style"] + 0.1)
            adapted[
                "system_prompt"
            ] += "\nAdapta tu comunicación para ejecutivos de alto rendimiento que buscan optimización estratégica."

        elif program_type == "LONGEVITY":
            # Más tranquilo y preventivo
            adapted["stability"] = min(1.0, adapted["stability"] + 0.05)
            adapted["style"] = max(0.0, adapted["style"] - 0.1)
            adapted[
                "system_prompt"
            ] += "\nAdapta tu comunicación para personas que buscan bienestar sostenible y salud preventiva a largo plazo."

        return adapted

    def _update_state(self, new_state: ConversationState):
        """Actualiza el estado de la conversación."""
        old_state = self.state
        self.state = new_state

        logger.debug(f"Estado cambiado: {old_state.value} → {new_state.value}")

        # Notificar handler de cambio de estado
        if "state_change" in self.message_handlers:
            asyncio.create_task(
                self.message_handlers["state_change"](old_state.value, new_state.value)
            )

    async def end_conversation(self) -> Dict[str, Any]:
        """Termina la conversación conversacional."""
        try:
            if self.websocket and not self.websocket.closed:
                # Enviar mensaje de finalización
                end_message = {"type": "conversation_end"}
                await self.websocket.send(json.dumps(end_message))
                await self.websocket.close()

            self._update_state(ConversationState.DISCONNECTED)
            self.current_agent = None
            self.conversation_id = None
            self.message_handlers = {}

            logger.info("Conversación terminada correctamente")
            return {"status": "ended", "state": self.state.value}

        except Exception as e:
            logger.error(f"Error terminando conversación: {e}")
            return {"status": "error", "error": str(e)}

    def get_conversation_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de la conversación."""
        return {
            "state": self.state.value,
            "current_agent": self.current_agent,
            "conversation_id": self.conversation_id,
            "websocket_connected": self.websocket is not None
            and not getattr(self.websocket, "closed", True),
            "mock_mode": self.mock_mode,
        }


# Instancia global del cliente conversacional
conversational_client = ElevenLabsConversationalClient()
