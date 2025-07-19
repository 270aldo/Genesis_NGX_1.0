"""
NEXUS ENHANCED - Configuration Management
========================================

Sistema de configuración para el orquestador maestro con capacidades de concierge.
Maneja configuración de orchestration, client success, performance, y security.

Arquitectura A+ - Módulo Core
Líneas objetivo: <300
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class OrchestratorMode(Enum):
    """Modos de operación del orquestador."""

    ORCHESTRATION_ONLY = "orchestration_only"
    CONCIERGE_ONLY = "concierge_only"
    HYBRID = "hybrid"  # Default: orchestration + concierge según contexto


class ClientSuccessLevel(Enum):
    """Niveles de intensidad para client success."""

    MINIMAL = "minimal"
    STANDARD = "standard"
    PREMIUM = "premium"
    WHITE_GLOVE = "white_glove"


class IntentAnalysisMode(Enum):
    """Modos de análisis de intención."""

    BASIC = "basic"
    ENHANCED = "enhanced"  # Incluye client success context
    AI_POWERED = "ai_powered"  # Con predicción de necesidades


@dataclass
class NexusConfig:
    """
    Configuración completa para NEXUS Enhanced.

    Centraliza toda la configuración para orchestration, concierge mode,
    client success capabilities, y performance optimization.
    """

    # ===== ORCHESTRATION CONFIGURATION =====

    # Core Orchestration Settings
    max_response_time: float = 30.0
    max_concurrent_agents: int = 5
    orchestrator_mode: OrchestratorMode = OrchestratorMode.HYBRID

    # Intent Analysis Configuration
    intent_analysis_mode: IntentAnalysisMode = IntentAnalysisMode.ENHANCED
    intent_confidence_threshold: float = 0.7
    fallback_to_general_agent: bool = True

    # Agent Routing Settings
    enable_agent_load_balancing: bool = True
    agent_timeout_seconds: float = 25.0
    max_retry_attempts: int = 3
    retry_backoff_factor: float = 1.5

    # Response Synthesis Configuration
    enable_response_enhancement: bool = True
    personality_adaptation_enabled: bool = True
    program_classification_enabled: bool = True

    # ===== CONCIERGE MODE CONFIGURATION =====

    # Client Success Settings
    client_success_level: ClientSuccessLevel = ClientSuccessLevel.PREMIUM
    enable_proactive_check_ins: bool = True
    enable_milestone_celebrations: bool = True
    enable_retention_analytics: bool = True

    # Onboarding Configuration
    onboarding_duration_days: int = 7
    onboarding_touchpoints: List[str] = field(
        default_factory=lambda: [
            "welcome_message",
            "profile_setup",
            "goal_setting",
            "first_interaction",
            "week_one_check_in",
        ]
    )

    # Community Features
    enable_community_facilitation: bool = True
    community_engagement_frequency: str = "weekly"
    enable_peer_connections: bool = True

    # ===== PERFORMANCE CONFIGURATION =====

    # Caching Settings
    enable_intent_caching: bool = True
    intent_cache_ttl_seconds: int = 300
    enable_response_caching: bool = True
    response_cache_ttl_seconds: int = 600

    # Monitoring and Metrics
    enable_performance_monitoring: bool = True
    enable_conversation_analytics: bool = True
    metrics_collection_interval: int = 60

    # Health Checks
    health_check_interval_seconds: int = 30
    dependency_health_check_timeout: float = 5.0

    # ===== CONVERSATIONAL CAPABILITIES =====

    # ElevenLabs Conversational AI 2.0
    enable_conversational_mode: bool = True
    conversational_timeout_seconds: float = 120.0
    enable_voice_interruption: bool = True
    voice_activity_detection: bool = True

    # Turn-taking and Flow
    turn_taking_sensitivity: float = 0.8
    response_delay_ms: int = 300
    enable_contextual_responses: bool = True

    # ===== SECURITY AND COMPLIANCE =====

    # Data Protection
    enable_conversation_encryption: bool = True
    enable_audit_logging: bool = True
    data_retention_days: int = 90

    # Privacy Settings
    enable_gdpr_compliance: bool = True
    enable_data_anonymization: bool = True
    consent_required_for_analytics: bool = True

    # ===== CLIENT SUCCESS ANALYTICS =====

    # Engagement Tracking
    track_user_engagement: bool = True
    engagement_scoring_enabled: bool = True
    churn_prediction_enabled: bool = True

    # Journey Analytics
    track_user_journey: bool = True
    milestone_tracking_enabled: bool = True
    goal_progress_analytics: bool = True

    # Satisfaction Monitoring
    enable_sentiment_analysis: bool = True
    nps_collection_enabled: bool = True
    feedback_collection_frequency: str = "monthly"

    @classmethod
    def from_environment(cls) -> "NexusConfig":
        """
        Crea configuración desde variables de entorno.

        Permite override de configuración mediante variables de entorno
        para diferentes ambientes (development, staging, production).

        Returns:
            NexusConfig: Configuración construida desde ambiente
        """
        logger.info(
            "Cargando configuración de NEXUS Enhanced desde variables de entorno"
        )

        # Core orchestration settings
        max_response_time = float(os.getenv("NEXUS_MAX_RESPONSE_TIME", "30.0"))
        max_concurrent_agents = int(os.getenv("NEXUS_MAX_CONCURRENT_AGENTS", "5"))

        # Mode configuration
        mode_str = os.getenv("NEXUS_ORCHESTRATOR_MODE", "hybrid").lower()
        orchestrator_mode = OrchestratorMode.HYBRID
        try:
            orchestrator_mode = OrchestratorMode(mode_str)
        except ValueError:
            logger.warning(f"Invalid orchestrator mode: {mode_str}, using hybrid")

        # Client success configuration
        client_success_str = os.getenv("NEXUS_CLIENT_SUCCESS_LEVEL", "premium").lower()
        client_success_level = ClientSuccessLevel.PREMIUM
        try:
            client_success_level = ClientSuccessLevel(client_success_str)
        except ValueError:
            logger.warning(
                f"Invalid client success level: {client_success_str}, using premium"
            )

        # Intent analysis configuration
        intent_mode_str = os.getenv("NEXUS_INTENT_ANALYSIS_MODE", "enhanced").lower()
        intent_analysis_mode = IntentAnalysisMode.ENHANCED
        try:
            intent_analysis_mode = IntentAnalysisMode(intent_mode_str)
        except ValueError:
            logger.warning(
                f"Invalid intent analysis mode: {intent_mode_str}, using enhanced"
            )

        # Feature flags
        enable_conversational = (
            os.getenv("NEXUS_ENABLE_CONVERSATIONAL", "true").lower() == "true"
        )
        enable_proactive_checkins = (
            os.getenv("NEXUS_ENABLE_PROACTIVE_CHECKINS", "true").lower() == "true"
        )
        enable_milestone_celebrations = (
            os.getenv("NEXUS_ENABLE_MILESTONE_CELEBRATIONS", "true").lower() == "true"
        )

        # Performance settings
        intent_cache_ttl = int(os.getenv("NEXUS_INTENT_CACHE_TTL", "300"))
        response_cache_ttl = int(os.getenv("NEXUS_RESPONSE_CACHE_TTL", "600"))

        # Security settings
        enable_encryption = (
            os.getenv("NEXUS_ENABLE_ENCRYPTION", "true").lower() == "true"
        )
        enable_audit_logging = (
            os.getenv("NEXUS_ENABLE_AUDIT_LOGGING", "true").lower() == "true"
        )
        data_retention_days = int(os.getenv("NEXUS_DATA_RETENTION_DAYS", "90"))

        config = cls(
            max_response_time=max_response_time,
            max_concurrent_agents=max_concurrent_agents,
            orchestrator_mode=orchestrator_mode,
            intent_analysis_mode=intent_analysis_mode,
            client_success_level=client_success_level,
            enable_conversational_mode=enable_conversational,
            enable_proactive_check_ins=enable_proactive_checkins,
            enable_milestone_celebrations=enable_milestone_celebrations,
            intent_cache_ttl_seconds=intent_cache_ttl,
            response_cache_ttl_seconds=response_cache_ttl,
            enable_conversation_encryption=enable_encryption,
            enable_audit_logging=enable_audit_logging,
            data_retention_days=data_retention_days,
        )

        logger.info(f"NEXUS Enhanced configurado en modo: {orchestrator_mode.value}")
        logger.info(f"Client success level: {client_success_level.value}")
        logger.info(f"Intent analysis mode: {intent_analysis_mode.value}")

        return config

    @classmethod
    def create_development(cls) -> "NexusConfig":
        """
        Crea configuración optimizada para desarrollo.

        Configuración con debugging habilitado, timeouts relajados,
        y features experimentales activas.

        Returns:
            NexusConfig: Configuración para desarrollo
        """
        return cls(
            max_response_time=60.0,  # Timeouts más relajados
            orchestrator_mode=OrchestratorMode.HYBRID,
            intent_analysis_mode=IntentAnalysisMode.AI_POWERED,
            client_success_level=ClientSuccessLevel.PREMIUM,
            enable_conversational_mode=True,
            enable_performance_monitoring=True,
            enable_conversation_analytics=True,
            health_check_interval_seconds=10,  # Checks más frecuentes
            enable_audit_logging=True,
            data_retention_days=30,  # Menor retención para desarrollo
        )

    @classmethod
    def create_production(cls) -> "NexusConfig":
        """
        Crea configuración optimizada para producción.

        Configuración con security máximo, performance optimizado,
        y monitoring completo.

        Returns:
            NexusConfig: Configuración para producción
        """
        return cls(
            max_response_time=25.0,  # Timeouts estrictos
            orchestrator_mode=OrchestratorMode.HYBRID,
            intent_analysis_mode=IntentAnalysisMode.ENHANCED,
            client_success_level=ClientSuccessLevel.PREMIUM,
            enable_conversational_mode=True,
            enable_performance_monitoring=True,
            enable_conversation_analytics=True,
            enable_conversation_encryption=True,
            enable_audit_logging=True,
            enable_gdpr_compliance=True,
            data_retention_days=90,
            health_check_interval_seconds=30,
            metrics_collection_interval=30,  # Metrics más frecuentes en prod
        )

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Valida la configuración actual.

        Returns:
            Dict[str, Any]: Resultado de validación con warnings/errors
        """
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": [],
        }

        # Validate response times
        if self.max_response_time > 60.0:
            validation_result["warnings"].append(
                f"Max response time muy alto: {self.max_response_time}s"
            )

        if self.agent_timeout_seconds >= self.max_response_time:
            validation_result["errors"].append(
                "Agent timeout debe ser menor que max_response_time"
            )
            validation_result["valid"] = False

        # Validate cache settings
        if self.intent_cache_ttl_seconds > 3600:
            validation_result["warnings"].append(
                "Intent cache TTL muy alto, puede causar stale data"
            )

        # Validate security settings
        if not self.enable_conversation_encryption and self.enable_audit_logging:
            validation_result["recommendations"].append(
                "Considerar habilitar encriptación con audit logging activo"
            )

        # Validate client success settings
        if (
            self.client_success_level == ClientSuccessLevel.WHITE_GLOVE
            and not self.enable_proactive_check_ins
        ):
            validation_result["warnings"].append(
                "White glove service debería incluir proactive check-ins"
            )

        return validation_result

    def get_effective_settings(self) -> Dict[str, Any]:
        """
        Obtiene configuración efectiva aplicada.

        Returns:
            Dict[str, Any]: Configuración efectiva con valores calculados
        """
        return {
            "orchestrator_mode": self.orchestrator_mode.value,
            "client_success_level": self.client_success_level.value,
            "intent_analysis_mode": self.intent_analysis_mode.value,
            "performance_settings": {
                "max_response_time": self.max_response_time,
                "max_concurrent_agents": self.max_concurrent_agents,
                "agent_timeout": self.agent_timeout_seconds,
            },
            "capabilities": {
                "orchestration": True,
                "concierge_mode": self.orchestrator_mode
                in [OrchestratorMode.CONCIERGE_ONLY, OrchestratorMode.HYBRID],
                "conversational": self.enable_conversational_mode,
                "proactive_engagement": self.enable_proactive_check_ins,
                "milestone_tracking": self.enable_milestone_celebrations,
                "community_features": self.enable_community_facilitation,
            },
            "security": {
                "encryption_enabled": self.enable_conversation_encryption,
                "audit_logging": self.enable_audit_logging,
                "gdpr_compliance": self.enable_gdpr_compliance,
                "data_retention_days": self.data_retention_days,
            },
        }
