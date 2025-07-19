"""
Dependencies injection container for NODE Systems Integration.
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
from infrastructure.adapters.vision_adapter import VisionAdapter
from infrastructure.adapters.multimodal_adapter import MultimodalAdapter


@dataclass
class NodeDependencies:
    """
    Dependency injection container for NODE Systems Integration.

    Contains all external dependencies required by the backend agent including
    AI clients, database connections, infrastructure adapters, and integration
    services. This pattern enables better testing and modularity for system
    integration tasks.
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

    # Vision and multimodal capabilities
    vision_adapter: VisionAdapter
    multimodal_adapter: MultimodalAdapter

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


def create_node_dependencies() -> NodeDependencies:
    """
    Factory function to create NodeDependencies with default implementations.

    Returns:
        NodeDependencies: Configured dependencies container for systems integration

    Raises:
        RuntimeError: If required environment variables are missing
    """
    try:
        return NodeDependencies(
            vertex_ai_client=VertexAIClient(),
            personality_adapter=PersonalityAdapter(),
            supabase_client=SupabaseClient(),
            program_classification_service=ProgramClassificationService(),
            mcp_toolkit=MCPToolkit(),
            state_manager_adapter=StateManagerAdapter(),
            intent_analyzer_adapter=IntentAnalyzerAdapter(),
            a2a_adapter=A2AAdapter(),
            vision_adapter=VisionAdapter(),
            multimodal_adapter=MultimodalAdapter(),
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create NODE dependencies: {e}")
