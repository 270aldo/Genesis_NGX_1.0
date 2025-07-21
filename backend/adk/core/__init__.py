"""
NGX Agent Development Kit (ADK) Core Module
==========================================

This module provides the foundational components for building
standardized AI agents in the GENESIS platform.
"""

from .base_agent import BaseADKAgent, AgentRequest, AgentResponse
from .exceptions import (
    ADKError,
    AgentValidationError,
    AgentExecutionError,
    AgentTimeoutError,
    AgentRateLimitError,
    AgentConfigurationError
)
from .types import (
    AgentType,
    AgentStatus,
    ResponseFormat,
    ConversationContext,
    AgentMetadata
)

__all__ = [
    # Base Classes
    "BaseADKAgent",
    "AgentRequest", 
    "AgentResponse",
    
    # Exceptions
    "ADKError",
    "AgentValidationError",
    "AgentExecutionError", 
    "AgentTimeoutError",
    "AgentRateLimitError",
    "AgentConfigurationError",
    
    # Types
    "AgentType",
    "AgentStatus",
    "ResponseFormat",
    "ConversationContext",
    "AgentMetadata"
]

__version__ = "2.0.0"