"""
Dependencies injection container for LUNA Female Wellness Specialist.
Provides centralized dependency management for A+ level architecture.
"""

from dataclasses import dataclass
from typing import Optional

from clients.vertex_ai.client import VertexAIClient
from clients.supabase_client import SupabaseClient
from core.personality.personality_adapter import PersonalityAdapter
from services.program_classification_service import ProgramClassificationService
from tools.mcp_toolkit import MCPToolkit
from infrastructure.adapters.state_manager_adapter import StateManagerAdapter
from infrastructure.adapters.intent_analyzer_adapter import IntentAnalyzerAdapter
from infrastructure.adapters.a2a_adapter import A2AAdapter


@dataclass
class LunaDependencies:
    """
    Dependency injection container for LUNA Female Wellness Specialist.

    Contains all external dependencies required by the agent including
    AI clients, database connections, personality systems, and infrastructure
    adapters specialized for female wellness. This pattern enables better
    testing and modularity while maintaining GDPR/HIPAA compliance.
    """

    # AI and ML services
    vertex_ai_client: VertexAIClient
    personality_adapter: PersonalityAdapter

    # Database and storage
    supabase_client: SupabaseClient

    # NGX platform services
    program_classification_service: ProgramClassificationService
    mcp_toolkit: MCPToolkit

    # Infrastructure adapters
    state_manager_adapter: StateManagerAdapter
    intent_analyzer_adapter: IntentAnalyzerAdapter
    a2a_adapter: A2AAdapter

    def __post_init__(self):
        """Validate dependencies after initialization."""
        required_deps = [
            "vertex_ai_client",
            "personality_adapter",
            "supabase_client",
            "program_classification_service",
            "mcp_toolkit",
        ]

        for dep_name in required_deps:
            if getattr(self, dep_name) is None:
                raise ValueError(f"Required dependency '{dep_name}' cannot be None")


def create_luna_dependencies() -> LunaDependencies:
    """
    Factory function to create LunaDependencies with default implementations.

    Returns:
        LunaDependencies: Configured dependencies container for female wellness

    Raises:
        RuntimeError: If required environment variables are missing
    """
    try:
        return LunaDependencies(
            vertex_ai_client=VertexAIClient(),
            personality_adapter=PersonalityAdapter(),
            supabase_client=SupabaseClient(),
            program_classification_service=ProgramClassificationService(),
            mcp_toolkit=MCPToolkit(),
            state_manager_adapter=StateManagerAdapter(),
            intent_analyzer_adapter=IntentAnalyzerAdapter(),
            a2a_adapter=A2AAdapter(),
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create LUNA dependencies: {e}")
