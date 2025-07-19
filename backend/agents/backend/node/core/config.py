"""
Configuration for NODE Systems Integration agent.
Defines all configurable parameters for A+ level operation.
"""

import os
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class NodeConfig:
    """
    Configuration for NODE Systems Integration agent.

    Defines all configurable parameters including performance settings,
    integration options, and feature flags for optimal A+ level operation
    specialized for backend systems integration and API coordination.
    """

    # Performance settings
    max_response_time: float = 30.0
    retry_attempts: int = 3
    cache_ttl: int = 1800  # 30 minutes for integration data
    concurrent_integration_limit: int = 10

    # Circuit breaker settings
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout: int = 60
    circuit_breaker_half_open_max_calls: int = 3

    # Personality adaptation (INTJ - Analytical, systematic, strategic)
    enable_personality_adaptation: bool = True
    personality_cache_ttl: int = 3600  # Longer for backend agent
    intj_analytical_level: float = 0.9  # High analytical capability

    # Security settings (Backend infrastructure)
    enable_audit_logging: bool = True
    enable_request_validation: bool = True
    enable_rate_limiting: bool = True
    enable_api_key_validation: bool = True
    enable_ssl_verification: bool = True

    # Systems integration settings
    enable_real_integrations: bool = True  # Set to False for mock mode
    api_timeout: float = 15.0
    max_concurrent_api_calls: int = 20
    enable_async_processing: bool = True
    enable_batch_operations: bool = True

    # Feature flags - Integration capabilities
    enable_rest_api_integration: bool = True
    enable_graphql_integration: bool = True
    enable_websocket_integration: bool = True
    enable_message_queue_integration: bool = True
    enable_database_integration: bool = True
    enable_cloud_services_integration: bool = True
    enable_monitoring_integration: bool = True

    # Data pipeline settings
    enable_data_streaming: bool = True
    max_pipeline_stages: int = 10
    pipeline_timeout: float = 300.0  # 5 minutes
    enable_data_validation: bool = True

    # Infrastructure automation
    enable_infrastructure_automation: bool = True
    enable_deployment_automation: bool = True
    enable_scaling_automation: bool = True
    enable_backup_automation: bool = True

    # External service settings
    gemini_timeout: float = 20.0
    supabase_timeout: float = 10.0
    third_party_api_timeout: float = 30.0

    # Monitoring and telemetry
    enable_performance_monitoring: bool = True
    enable_integration_metrics: bool = True
    enable_health_checks: bool = True
    metrics_collection_interval: int = 30
    health_check_interval: int = 60

    # Debug settings
    debug_mode: bool = False
    log_level: str = "INFO"
    enable_integration_logging: bool = True

    @classmethod
    def from_environment(cls) -> "NodeConfig":
        """
        Create configuration from environment variables.

        Returns:
            NodeConfig: Configuration loaded from environment
        """
        return cls(
            # Performance
            max_response_time=float(os.getenv("NODE_MAX_RESPONSE_TIME", "30.0")),
            retry_attempts=int(os.getenv("NODE_RETRY_ATTEMPTS", "3")),
            cache_ttl=int(os.getenv("NODE_CACHE_TTL", "1800")),
            # Personality
            enable_personality_adaptation=os.getenv(
                "NODE_ENABLE_PERSONALITY", "true"
            ).lower()
            == "true",
            intj_analytical_level=float(os.getenv("NODE_INTJ_ANALYTICAL", "0.9")),
            # Security
            enable_audit_logging=os.getenv("NODE_ENABLE_AUDIT", "true").lower()
            == "true",
            enable_request_validation=os.getenv(
                "NODE_ENABLE_VALIDATION", "true"
            ).lower()
            == "true",
            enable_rate_limiting=os.getenv("NODE_ENABLE_RATE_LIMIT", "true").lower()
            == "true",
            # Integration
            enable_real_integrations=os.getenv(
                "NODE_ENABLE_REAL_INTEGRATIONS", "true"
            ).lower()
            == "true",
            api_timeout=float(os.getenv("NODE_API_TIMEOUT", "15.0")),
            # Feature flags
            enable_rest_api_integration=os.getenv("NODE_ENABLE_REST", "true").lower()
            == "true",
            enable_graphql_integration=os.getenv("NODE_ENABLE_GRAPHQL", "true").lower()
            == "true",
            enable_websocket_integration=os.getenv(
                "NODE_ENABLE_WEBSOCKET", "true"
            ).lower()
            == "true",
            enable_message_queue_integration=os.getenv("NODE_ENABLE_MQ", "true").lower()
            == "true",
            # Infrastructure
            enable_infrastructure_automation=os.getenv(
                "NODE_ENABLE_INFRASTRUCTURE", "true"
            ).lower()
            == "true",
            enable_deployment_automation=os.getenv(
                "NODE_ENABLE_DEPLOYMENT", "true"
            ).lower()
            == "true",
            # Debug
            debug_mode=os.getenv("NODE_DEBUG_MODE", "false").lower() == "true",
            log_level=os.getenv("NODE_LOG_LEVEL", "INFO").upper(),
        )

    def validate(self) -> None:
        """
        Validate configuration parameters.

        Raises:
            ValueError: If configuration is invalid
        """
        if self.max_response_time <= 0:
            raise ValueError("max_response_time must be positive")

        if self.retry_attempts < 0:
            raise ValueError("retry_attempts cannot be negative")

        if self.cache_ttl <= 0:
            raise ValueError("cache_ttl must be positive")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log_level: {self.log_level}")

        if not (0.0 <= self.intj_analytical_level <= 1.0):
            raise ValueError("intj_analytical_level must be between 0.0 and 1.0")

        if self.concurrent_integration_limit <= 0:
            raise ValueError("concurrent_integration_limit must be positive")

        if self.max_concurrent_api_calls <= 0:
            raise ValueError("max_concurrent_api_calls must be positive")

        if self.max_pipeline_stages <= 0:
            raise ValueError("max_pipeline_stages must be positive")

        # Security validation for production
        if not self.debug_mode:
            if not self.enable_audit_logging:
                raise ValueError("Audit logging must be enabled in production")
            if not self.enable_request_validation:
                raise ValueError("Request validation must be enabled in production")
            if not self.enable_ssl_verification:
                raise ValueError("SSL verification must be enabled in production")

    @property
    def is_production_ready(self) -> bool:
        """
        Check if configuration is ready for production.

        Returns:
            bool: True if configuration meets production standards
        """
        try:
            self.validate()
            return (
                self.enable_audit_logging
                and self.enable_request_validation
                and self.enable_rate_limiting
                and self.enable_ssl_verification
                and not self.debug_mode
            )
        except ValueError:
            return False

    def get_circuit_breaker_config(self) -> Dict[str, int]:
        """Get circuit breaker configuration."""
        return {
            "failure_threshold": self.circuit_breaker_failure_threshold,
            "timeout": self.circuit_breaker_timeout,
            "half_open_max_calls": self.circuit_breaker_half_open_max_calls,
        }

    def get_integration_timeouts(self) -> Dict[str, float]:
        """Get timeout configuration for different integration types."""
        return {
            "api_calls": self.api_timeout,
            "gemini": self.gemini_timeout,
            "supabase": self.supabase_timeout,
            "third_party": self.third_party_api_timeout,
            "pipeline": self.pipeline_timeout,
        }
