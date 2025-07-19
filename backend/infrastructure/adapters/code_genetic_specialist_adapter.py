"""
Adaptador para el agente HELIX - Genetic Performance Specialist
"""

import logging
from typing import Any, Dict, Optional

from agents.helix_genetic_specialist.agent import HelixGeneticSpecialist
from infrastructure.adapters.base_agent_adapter import BaseAgentAdapter

logger = logging.getLogger(__name__)


class HelixGeneticSpecialistAdapter(BaseAgentAdapter):
    """
    Adaptador para integrar HELIX con el sistema A2A.
    Maneja la comunicación entre el agente de genética y otros componentes.
    """

    def __init__(self):
        """Inicializa el adaptador con una instancia de HELIX"""
        super().__init__()
        self.agent = None
        self.agent_id = "helix_genetic_specialist"
        self.capabilities = [
            "analyze_genetic_profile",
            "genetic_risk_assessment",
            "personalize_by_genetics",
            "epigenetic_optimization",
            "nutrigenomics_analysis",
            "sport_genetics_analysis",
        ]

    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Inicializa el agente HELIX con la configuración proporcionada.

        Args:
            config: Configuración opcional para el agente
        """
        try:
            logger.info("Inicializando HELIX Genetic Specialist Adapter...")

            # Crear instancia del agente
            self.agent = HelixGeneticSpecialist(
                state_manager=config.get("state_manager") if config else None,
                mcp_toolkit=config.get("mcp_toolkit") if config else None,
            )

            # Registrar el agente en el sistema A2A si está disponible
            if config and "a2a_server" in config:
                await self._register_with_a2a(config["a2a_server"])

            logger.info("HELIX Genetic Specialist Adapter inicializado correctamente")

        except Exception as e:
            logger.error(f"Error inicializando HELIX adapter: {e}")
            raise

    async def process_request(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa una solicitud para el agente HELIX.

        Args:
            message: Mensaje del usuario
            context: Contexto adicional (user_id, program_type, etc.)

        Returns:
            Respuesta del agente con análisis genético
        """
        if not self.agent:
            raise RuntimeError("El agente HELIX no ha sido inicializado")

        try:
            # Extraer información del contexto
            user_id = context.get("user_id") if context else None
            program_type = context.get("program_type") if context else None
            session_id = context.get("session_id") if context else None

            # Preparar kwargs para el agente
            kwargs = {
                "program_type": program_type,
                "session_id": session_id,
                "context": context,
            }

            # Procesar con el agente
            result = await self.agent.run_async(
                input_text=message, user_id=user_id, **kwargs
            )

            # Enriquecer respuesta con metadatos del adaptador
            return {
                "agent_id": self.agent_id,
                "agent_name": "HELIX - Genetic Performance Specialist",
                "response": result.get("response", ""),
                "data": result.get("data", {}),
                "skills_used": result.get("skills_used", []),
                "visualizations": result.get("visualizations"),
                "action_plan": result.get("action_plan"),
                "personality": self.agent.PERSONALITY_CONFIG,
                "metadata": {
                    "capabilities": self.capabilities,
                    "specialization": "genetic_analysis",
                    "confidence": 0.95,
                },
            }

        except Exception as e:
            logger.error(f"Error procesando solicitud en HELIX adapter: {e}")
            return self._create_error_response(str(e))

    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Obtiene las capacidades del agente HELIX.

        Returns:
            Diccionario con las capacidades del agente
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": "HELIX - Genetic Performance Specialist",
            "description": "Especialista en análisis genético y medicina personalizada",
            "capabilities": self.capabilities,
            "supported_analyses": [
                "genetic_profile_analysis",
                "risk_assessment",
                "personalized_plans",
                "epigenetic_optimization",
                "nutrigenomics",
                "sport_genetics",
            ],
            "personality": self.agent.PERSONALITY_CONFIG if self.agent else {},
            "audience_adaptations": {
                "NGX_PRIME": "Consultor científico de performance élite",
                "NGX_LONGEVITY": "Especialista en medicina preventiva personalizada",
            },
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud del adaptador y el agente.

        Returns:
            Estado de salud del servicio
        """
        try:
            if not self.agent:
                return {
                    "status": "unhealthy",
                    "reason": "Agent not initialized",
                    "agent_id": self.agent_id,
                }

            # Verificar que el agente responde
            test_result = await self.agent.run_async(
                "test genetic analysis capabilities", user_id="health_check"
            )

            if test_result and "response" in test_result:
                return {
                    "status": "healthy",
                    "agent_id": self.agent_id,
                    "capabilities_count": len(self.capabilities),
                    "response_time": "fast",
                }
            else:
                return {
                    "status": "degraded",
                    "reason": "Agent responding slowly",
                    "agent_id": self.agent_id,
                }

        except Exception as e:
            return {"status": "unhealthy", "reason": str(e), "agent_id": self.agent_id}

    async def _register_with_a2a(self, a2a_server_url: str) -> None:
        """
        Registra el agente con el servidor A2A.

        Args:
            a2a_server_url: URL del servidor A2A
        """
        try:
            # Aquí iría la lógica de registro con el servidor A2A
            logger.info(f"Registrando HELIX con servidor A2A en {a2a_server_url}")
            # Por ahora es un placeholder
            pass
        except Exception as e:
            logger.error(f"Error registrando con A2A: {e}")

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Crea una respuesta de error formateada.

        Args:
            error_message: Mensaje de error

        Returns:
            Respuesta de error formateada
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": "HELIX - Genetic Performance Specialist",
            "response": f"Lo siento, encontré un problema al procesar tu solicitud genética: {error_message}",
            "error": True,
            "error_message": error_message,
            "suggestions": [
                "Intenta reformular tu pregunta sobre genética",
                "Especifica si buscas análisis de riesgo, personalización o nutrigenómica",
                "Contacta soporte si el problema persiste",
            ],
        }

    async def shutdown(self) -> None:
        """Cierra el adaptador y libera recursos"""
        try:
            logger.info("Cerrando HELIX Genetic Specialist Adapter...")

            # Limpiar recursos del agente si es necesario
            if self.agent:
                # Guardar cualquier estado pendiente
                if hasattr(self.agent, "analysis_history"):
                    # Aquí podrías guardar el historial en base de datos
                    pass

                # Limpiar caché
                if hasattr(self.agent, "genetic_profiles_cache"):
                    self.agent.genetic_profiles_cache.clear()

                self.agent = None

            logger.info("HELIX Genetic Specialist Adapter cerrado correctamente")

        except Exception as e:
            logger.error(f"Error cerrando HELIX adapter: {e}")


# Instancia singleton del adaptador
helix_genetic_specialist_adapter = HelixGeneticSpecialistAdapter()
