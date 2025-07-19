"""
Dependencies injection container for SPARK Motivation Behavior Coach.
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
class SparkDependencies:
    """
    Dependency injection container for SPARK Motivation Behavior Coach.

    Contains all external dependencies required by the agent including
    AI clients, database connections, personality systems, behavioral
    tracking services, and infrastructure adapters.
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
            "state_manager_adapter",
            "intent_analyzer_adapter",
            "a2a_adapter",
        ]

        for dep_name in required_deps:
            if getattr(self, dep_name) is None:
                raise ValueError(f"Required dependency '{dep_name}' cannot be None")

    def get_dependency_health(self) -> dict:
        """Check health status of all dependencies."""
        health_status = {}

        # Check AI services
        try:
            health_status["vertex_ai_client"] = (
                "healthy" if self.vertex_ai_client else "unavailable"
            )
        except Exception:
            health_status["vertex_ai_client"] = "error"

        try:
            health_status["personality_adapter"] = (
                "healthy" if self.personality_adapter else "unavailable"
            )
        except Exception:
            health_status["personality_adapter"] = "error"

        # Check database services
        try:
            health_status["supabase_client"] = (
                "healthy" if self.supabase_client else "unavailable"
            )
        except Exception:
            health_status["supabase_client"] = "error"

        # Check NGX services
        try:
            health_status["program_classification_service"] = (
                "healthy" if self.program_classification_service else "unavailable"
            )
        except Exception:
            health_status["program_classification_service"] = "error"

        try:
            health_status["mcp_toolkit"] = (
                "healthy" if self.mcp_toolkit else "unavailable"
            )
        except Exception:
            health_status["mcp_toolkit"] = "error"

        # Check infrastructure adapters
        try:
            health_status["state_manager_adapter"] = (
                "healthy" if self.state_manager_adapter else "unavailable"
            )
        except Exception:
            health_status["state_manager_adapter"] = "error"

        try:
            health_status["intent_analyzer_adapter"] = (
                "healthy" if self.intent_analyzer_adapter else "unavailable"
            )
        except Exception:
            health_status["intent_analyzer_adapter"] = "error"

        try:
            health_status["a2a_adapter"] = (
                "healthy" if self.a2a_adapter else "unavailable"
            )
        except Exception:
            health_status["a2a_adapter"] = "error"

        return health_status


def create_production_dependencies(
    vertex_ai_client: Optional[VertexAIClient] = None,
    personality_adapter: Optional[PersonalityAdapter] = None,
    supabase_client: Optional[SupabaseClient] = None,
    program_classification_service: Optional[ProgramClassificationService] = None,
    mcp_toolkit: Optional[MCPToolkit] = None,
    state_manager_adapter: Optional[StateManagerAdapter] = None,
    intent_analyzer_adapter: Optional[IntentAnalyzerAdapter] = None,
    a2a_adapter: Optional[A2AAdapter] = None,
) -> SparkDependencies:
    """
    Create production dependencies with default initialization.

    Args:
        vertex_ai_client: Pre-initialized Gemini client (optional)
        personality_adapter: Pre-initialized personality adapter (optional)
        supabase_client: Pre-initialized Supabase client (optional)
        program_classification_service: Pre-initialized program classification service (optional)
        mcp_toolkit: Pre-initialized MCP toolkit (optional)
        state_manager_adapter: Pre-initialized state manager adapter (optional)
        intent_analyzer_adapter: Pre-initialized intent analyzer adapter (optional)
        a2a_adapter: Pre-initialized A2A adapter (optional)

    Returns:
        SparkDependencies: Fully initialized dependency container

    Raises:
        ValueError: If required dependencies cannot be initialized
    """
    try:
        # Initialize Gemini client if not provided
        if vertex_ai_client is None:
            vertex_ai_client = VertexAIClient()

        # Initialize personality adapter if not provided
        if personality_adapter is None:
            personality_adapter = PersonalityAdapter()

        # Initialize Supabase client if not provided
        if supabase_client is None:
            supabase_client = SupabaseClient()

        # Initialize program classification service if not provided
        if program_classification_service is None:
            program_classification_service = ProgramClassificationService()

        # Initialize MCP toolkit if not provided
        if mcp_toolkit is None:
            mcp_toolkit = MCPToolkit()

        # Initialize state manager adapter if not provided
        if state_manager_adapter is None:
            from infrastructure.adapters.state_manager_adapter import (
                state_manager_adapter as sma,
            )

            state_manager_adapter = sma

        # Initialize intent analyzer adapter if not provided
        if intent_analyzer_adapter is None:
            intent_analyzer_adapter = IntentAnalyzerAdapter()

        # Initialize A2A adapter if not provided
        if a2a_adapter is None:
            a2a_adapter = A2AAdapter()

        return SparkDependencies(
            vertex_ai_client=vertex_ai_client,
            personality_adapter=personality_adapter,
            supabase_client=supabase_client,
            program_classification_service=program_classification_service,
            mcp_toolkit=mcp_toolkit,
            state_manager_adapter=state_manager_adapter,
            intent_analyzer_adapter=intent_analyzer_adapter,
            a2a_adapter=a2a_adapter,
        )

    except Exception as e:
        raise ValueError(f"Failed to create production dependencies: {str(e)}")


def create_test_dependencies(
    mock_gemini: bool = True,
    mock_personality: bool = True,
    mock_supabase: bool = True,
    mock_program_classification: bool = True,
    mock_mcp: bool = True,
    mock_adapters: bool = True,
) -> SparkDependencies:
    """
    Create test dependencies with mocked services.

    Args:
        mock_gemini: Whether to mock Gemini client
        mock_personality: Whether to mock personality adapter
        mock_supabase: Whether to mock Supabase client
        mock_program_classification: Whether to mock program classification service
        mock_mcp: Whether to mock MCP toolkit
        mock_adapters: Whether to mock infrastructure adapters

    Returns:
        SparkDependencies: Test dependency container with mocks
    """
    from unittest.mock import MagicMock

    # Create mocked or real dependencies based on flags
    vertex_ai_client = MagicMock() if mock_gemini else VertexAIClient()
    personality_adapter = MagicMock() if mock_personality else PersonalityAdapter()
    supabase_client = MagicMock() if mock_supabase else SupabaseClient()
    program_classification_service = (
        MagicMock() if mock_program_classification else ProgramClassificationService()
    )
    mcp_toolkit = MagicMock() if mock_mcp else MCPToolkit()

    if mock_adapters:
        state_manager_adapter = MagicMock()
        intent_analyzer_adapter = MagicMock()
        a2a_adapter = MagicMock()
    else:
        from infrastructure.adapters.state_manager_adapter import (
            state_manager_adapter as sma,
        )

        state_manager_adapter = sma
        intent_analyzer_adapter = IntentAnalyzerAdapter()
        a2a_adapter = A2AAdapter()

    return SparkDependencies(
        vertex_ai_client=vertex_ai_client,
        personality_adapter=personality_adapter,
        supabase_client=supabase_client,
        program_classification_service=program_classification_service,
        mcp_toolkit=mcp_toolkit,
        state_manager_adapter=state_manager_adapter,
        intent_analyzer_adapter=intent_analyzer_adapter,
        a2a_adapter=a2a_adapter,
    )
