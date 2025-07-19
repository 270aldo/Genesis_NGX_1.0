"""
Core module for NODE Systems Integration.
Provides foundational components for A+ level architecture.
"""

from .config import NodeConfig
from .constants import (
    AGENT_ID,
    AGENT_NAME,
    AGENT_VERSION,
    PERSONALITY_CONFIG,
    CORE_SKILLS,
    VISUAL_SKILLS,
    CONVERSATIONAL_SKILLS,
    INTEGRATION_TYPES,
    CIRCUIT_BREAKER_CONFIG,
    AUTOMATION_WORKFLOWS,
)
from .dependencies import NodeDependencies, create_node_dependencies
from .exceptions import (
    NodeIntegrationError,
    NodeValidationError,
    SystemIntegrationError,
    ApiConnectionError,
    CircuitBreakerError,
    DataPipelineError,
    InfrastructureAutomationError,
    ExternalServiceError,
    PersonalityAdaptationError,
    IntegrationAuthenticationError,
    IntegrationConfigurationError,
    RateLimitExceededError,
    WebSocketConnectionError,
    MessageQueueError,
    DatabaseIntegrationError,
    CloudServiceIntegrationError,
)

__all__ = [
    # Config
    "NodeConfig",
    # Constants
    "AGENT_ID",
    "AGENT_NAME",
    "AGENT_VERSION",
    "PERSONALITY_CONFIG",
    "CORE_SKILLS",
    "VISUAL_SKILLS",
    "CONVERSATIONAL_SKILLS",
    "INTEGRATION_TYPES",
    "CIRCUIT_BREAKER_CONFIG",
    "AUTOMATION_WORKFLOWS",
    # Dependencies
    "NodeDependencies",
    "create_node_dependencies",
    # Exceptions
    "NodeIntegrationError",
    "NodeValidationError",
    "SystemIntegrationError",
    "ApiConnectionError",
    "CircuitBreakerError",
    "DataPipelineError",
    "InfrastructureAutomationError",
    "ExternalServiceError",
    "PersonalityAdaptationError",
    "IntegrationAuthenticationError",
    "IntegrationConfigurationError",
    "RateLimitExceededError",
    "WebSocketConnectionError",
    "MessageQueueError",
    "DatabaseIntegrationError",
    "CloudServiceIntegrationError",
]
