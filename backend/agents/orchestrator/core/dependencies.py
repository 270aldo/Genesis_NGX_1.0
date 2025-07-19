"""
NEXUS ENHANCED - Dependency Injection Container
===============================================

Sistema de inyección de dependencias para el orquestador maestro con capacidades
de concierge integradas. Maneja todas las dependencias necesarias para orchestration
y client success de manera centralizada y testeable.

Arquitectura A+ - Módulo Core
Líneas objetivo: <300
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

from clients.vertex_ai.client import VertexAIClient
from clients.supabase_client import SupabaseClient
from core.personality.personality_adapter import PersonalityAdapter
from core.state_manager_optimized import StateManager
from infrastructure.adapters.state_manager_adapter import state_manager_adapter
from infrastructure.adapters.intent_analyzer_adapter import intent_analyzer_adapter
from infrastructure.adapters.a2a_adapter import a2a_adapter
from infrastructure.adapters.conversational_voice_adapter import (
    ConversationalVoiceAdapter,
)
from services.program_classification_service import ProgramClassificationService
from tools.mcp_toolkit import MCPToolkit

logger = logging.getLogger(__name__)


@dataclass
class NexusDependencies:
    """
    Container de dependencias para NEXUS Enhanced.

    Centraliza todas las dependencias necesarias para:
    - Orchestration (análisis de intención, routing, síntesis)
    - Concierge Mode (onboarding, soporte, celebración, comunidad)
    - Client Success (check-ins proactivos, retención, milestone tracking)
    """

    # Core AI Services
    vertex_ai_client: VertexAIClient
    personality_adapter: PersonalityAdapter
    program_classification_service: ProgramClassificationService

    # State and Data Management
    state_manager: Optional[StateManager]
    supabase_client: Optional[SupabaseClient]

    # Communication and Integration
    a2a_adapter: Any  # A2A communication for agent routing
    intent_analyzer_adapter: Any  # Intent analysis service
    state_manager_adapter: Any  # State management service

    # Voice and Conversational Capabilities
    conversational_adapter: Optional[ConversationalVoiceAdapter]

    # Tools and Utilities
    mcp_toolkit: MCPToolkit

    # Configuration and Environment
    a2a_server_url: str
    orchestrator_model_id: str

    @classmethod
    def create_production(cls) -> "NexusDependencies":
        """
        Factory method para crear dependencias de producción.

        Inicializa todos los servicios con configuración de producción
        optimizada para orchestration y client success.

        Returns:
            NexusDependencies: Container configurado para producción
        """
        logger.info("Inicializando dependencias de producción para NEXUS Enhanced")

        try:
            # Core AI Services
            vertex_ai_client = VertexAIClient()
            personality_adapter = PersonalityAdapter()
            program_classification_service = ProgramClassificationService(vertex_ai_client)

            # State and Data Management
            supabase_client = None
            state_manager = None

            try:
                from clients.supabase_client import SupabaseClient

                supabase_client = SupabaseClient()
                if supabase_client and supabase_client.client:
                    state_manager = StateManager(supabase_client.client)
                    logger.info("Supabase y StateManager inicializados correctamente")
            except Exception as e:
                logger.warning(
                    f"Supabase no disponible: {e}. Continuando sin state management persistente."
                )

            # Voice and Conversational Capabilities
            conversational_adapter = None
            try:
                conversational_adapter = ConversationalVoiceAdapter()
                logger.info("Adaptador conversacional ElevenLabs 2.0 inicializado")
            except Exception as e:
                logger.warning(f"Adaptador conversacional no disponible: {e}")

            # Configuration
            from core.settings import Settings
settings = Settings()

            a2a_server_url = f"http://{settings.A2A_HOST}:{settings.A2A_PORT}"
            orchestrator_model_id = settings.ORCHESTRATOR_DEFAULT_MODEL_ID

            dependencies = cls(
                vertex_ai_client=vertex_ai_client,
                personality_adapter=personality_adapter,
                program_classification_service=program_classification_service,
                state_manager=state_manager,
                supabase_client=supabase_client,
                a2a_adapter=a2a_adapter,
                intent_analyzer_adapter=intent_analyzer_adapter,
                state_manager_adapter=state_manager_adapter,
                conversational_adapter=conversational_adapter,
                mcp_toolkit=MCPToolkit(),
                a2a_server_url=a2a_server_url,
                orchestrator_model_id=orchestrator_model_id,
            )

            logger.info("NEXUS Enhanced dependencies creadas exitosamente")
            return dependencies

        except Exception as e:
            logger.error(
                f"Error creando dependencias de producción: {e}", exc_info=True
            )
            raise

    @classmethod
    def create_testing(cls, **overrides) -> "NexusDependencies":
        """
        Factory method para crear dependencias de testing.

        Crea mocks y stubs necesarios para testing unitario e integración.
        Permite override de dependencias específicas para casos de prueba.

        Args:
            **overrides: Dependencias específicas para override en tests

        Returns:
            NexusDependencies: Container configurado para testing
        """
        logger.info("Inicializando dependencias de testing para NEXUS Enhanced")

        try:
            # Mock implementations para testing
            from unittest.mock import Mock, MagicMock

            # Default test dependencies
            defaults = {
                "vertex_ai_client": Mock(spec=VertexAIClient),
                "personality_adapter": Mock(spec=PersonalityAdapter),
                "program_classification_service": Mock(
                    spec=ProgramClassificationService
                ),
                "state_manager": None,
                "supabase_client": None,
                "a2a_adapter": MagicMock(),
                "intent_analyzer_adapter": MagicMock(),
                "state_manager_adapter": MagicMock(),
                "conversational_adapter": Mock(spec=ConversationalVoiceAdapter),
                "mcp_toolkit": Mock(spec=MCPToolkit),
                "a2a_server_url": "http://localhost:8001",
                "orchestrator_model_id": "gemini-pro",
            }

            # Apply overrides
            defaults.update(overrides)

            dependencies = cls(**defaults)
            logger.info("NEXUS Enhanced testing dependencies creadas exitosamente")
            return dependencies

        except Exception as e:
            logger.error(f"Error creando dependencias de testing: {e}", exc_info=True)
            raise

    def validate_dependencies(self) -> Dict[str, bool]:
        """
        Valida que las dependencias críticas estén disponibles y funcionales.

        Returns:
            Dict[str, bool]: Estado de cada dependencia crítica
        """
        validation_results = {}

        # Core AI Services - Críticos
        validation_results["vertex_ai_client"] = self.vertex_ai_client is not None
        validation_results["personality_adapter"] = self.personality_adapter is not None
        validation_results["program_classification_service"] = (
            self.program_classification_service is not None
        )

        # Communication - Críticos para orchestration
        validation_results["a2a_adapter"] = self.a2a_adapter is not None
        validation_results["intent_analyzer_adapter"] = (
            self.intent_analyzer_adapter is not None
        )

        # State Management - Opcionales pero recomendados
        validation_results["state_manager"] = self.state_manager is not None
        validation_results["supabase_client"] = self.supabase_client is not None

        # Voice Capabilities - Opcionales para enhanced features
        validation_results["conversational_adapter"] = (
            self.conversational_adapter is not None
        )

        # Tools - Requeridos
        validation_results["mcp_toolkit"] = self.mcp_toolkit is not None

        # Log validation results
        critical_missing = [
            k
            for k, v in validation_results.items()
            if not v
            and k
            in [
                "vertex_ai_client",
                "personality_adapter",
                "a2a_adapter",
                "intent_analyzer_adapter",
                "mcp_toolkit",
            ]
        ]

        if critical_missing:
            logger.warning(f"Dependencias críticas faltantes: {critical_missing}")
        else:
            logger.info("Todas las dependencias críticas están disponibles")

        optional_missing = [
            k
            for k, v in validation_results.items()
            if not v and k not in critical_missing
        ]
        if optional_missing:
            logger.info(f"Dependencias opcionales no disponibles: {optional_missing}")

        return validation_results

    def get_health_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado de salud de todas las dependencias.

        Returns:
            Dict[str, Any]: Estado detallado de salud del sistema
        """
        validation_results = self.validate_dependencies()

        health_status = {
            "overall_health": (
                "healthy"
                if all(
                    validation_results[k]
                    for k in [
                        "vertex_ai_client",
                        "personality_adapter",
                        "a2a_adapter",
                        "intent_analyzer_adapter",
                        "mcp_toolkit",
                    ]
                )
                else "degraded"
            ),
            "dependencies": validation_results,
            "capabilities": {
                "orchestration": validation_results["a2a_adapter"]
                and validation_results["intent_analyzer_adapter"],
                "personality_adaptation": validation_results["personality_adapter"],
                "ai_processing": validation_results["vertex_ai_client"],
                "state_management": validation_results["state_manager"],
                "conversational": validation_results["conversational_adapter"],
                "client_success": validation_results["personality_adapter"]
                and validation_results["vertex_ai_client"],
            },
            "recommended_actions": [],
        }

        # Add recommendations for missing critical dependencies
        if not validation_results["state_manager"]:
            health_status["recommended_actions"].append(
                "Configure Supabase for persistent state management"
            )

        if not validation_results["conversational_adapter"]:
            health_status["recommended_actions"].append(
                "Configure ElevenLabs for conversational capabilities"
            )

        return health_status
