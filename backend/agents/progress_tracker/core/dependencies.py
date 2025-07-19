"""
STELLA Progress Tracker Dependencies.
Dependency injection container for A+ architecture with progress tracking capabilities.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

try:
    from clients.vertex_ai.client import VertexAIClient
    from adapters.personality_adapter import PersonalityAdapter
    from clients.supabase_client import SupabaseClient
    from services.program_classification_service import ProgramClassificationService
    from adapters.mcp_toolkit import MCPToolkit
    from adapters.state_manager_adapter import StateManagerAdapter
    from adapters.intent_analyzer_adapter import IntentAnalyzerAdapter
    from adapters.a2a_adapter import A2AAdapter
    from clients.gcs_client import GCSClient
    from processors.vision_processor import VisionProcessor
    from adapters.multimodal_adapter import MultimodalAdapter
except ImportError:
    # For testing or when imports are not available
    VertexAIClient = object
    PersonalityAdapter = object
    SupabaseClient = object
    ProgramClassificationService = object
    MCPToolkit = object
    StateManagerAdapter = object
    IntentAnalyzerAdapter = object
    A2AAdapter = object
    GCSClient = object
    VisionProcessor = object
    MultimodalAdapter = object


@dataclass
class StellaDependencies:
    """
    Dependency injection container for STELLA Progress Tracker.
    Contains all external dependencies with validation and health checking.
    """

    # Core AI and Personality
    vertex_ai_client: VertexAIClient
    personality_adapter: PersonalityAdapter

    # Data and Storage
    supabase_client: SupabaseClient
    gcs_client: GCSClient

    # Specialized Services
    program_classification_service: ProgramClassificationService
    vision_processor: VisionProcessor
    multimodal_adapter: MultimodalAdapter

    # Infrastructure Adapters
    mcp_toolkit: MCPToolkit
    state_manager_adapter: StateManagerAdapter
    intent_analyzer_adapter: IntentAnalyzerAdapter
    a2a_adapter: A2AAdapter

    def __post_init__(self):
        """Validate dependencies after initialization."""
        required_deps = {
            "vertex_ai_client": self.vertex_ai_client,
            "personality_adapter": self.personality_adapter,
            "supabase_client": self.supabase_client,
            "gcs_client": self.gcs_client,
            "program_classification_service": self.program_classification_service,
            "vision_processor": self.vision_processor,
            "multimodal_adapter": self.multimodal_adapter,
            "mcp_toolkit": self.mcp_toolkit,
            "state_manager_adapter": self.state_manager_adapter,
            "intent_analyzer_adapter": self.intent_analyzer_adapter,
            "a2a_adapter": self.a2a_adapter,
        }

        for name, dependency in required_deps.items():
            if dependency is None:
                raise ValueError(f"Required dependency '{name}' cannot be None")

    def get_dependency_health(self) -> Dict[str, str]:
        """
        Check health status of all dependencies.

        Returns:
            Dict mapping dependency name to health status
        """
        health_status = {}

        # Check core dependencies
        dependencies_to_check = [
            ("vertex_ai_client", self.vertex_ai_client),
            ("personality_adapter", self.personality_adapter),
            ("supabase_client", self.supabase_client),
            ("gcs_client", self.gcs_client),
            ("program_classification_service", self.program_classification_service),
            ("vision_processor", self.vision_processor),
            ("multimodal_adapter", self.multimodal_adapter),
            ("mcp_toolkit", self.mcp_toolkit),
            ("state_manager_adapter", self.state_manager_adapter),
            ("intent_analyzer_adapter", self.intent_analyzer_adapter),
            ("a2a_adapter", self.a2a_adapter),
        ]

        for name, dependency in dependencies_to_check:
            try:
                if hasattr(dependency, "health_check"):
                    health_status[name] = dependency.health_check()
                elif hasattr(dependency, "is_healthy"):
                    health_status[name] = (
                        "healthy" if dependency.is_healthy() else "unhealthy"
                    )
                else:
                    # Assume healthy if no health check method
                    health_status[name] = "healthy"
            except Exception:
                health_status[name] = "error"

        return health_status

    def validate_progress_tracking_capabilities(self) -> Dict[str, bool]:
        """
        Validate specific capabilities required for progress tracking.

        Returns:
            Dict mapping capability to availability status
        """
        capabilities = {}

        # AI Analysis Capability
        try:
            capabilities["ai_analysis"] = hasattr(
                self.vertex_ai_client, "generate_content"
            )
        except Exception:
            capabilities["ai_analysis"] = False

        # Vision Processing Capability
        try:
            capabilities["vision_processing"] = hasattr(
                self.vision_processor, "analyze_image"
            )
        except Exception:
            capabilities["vision_processing"] = False

        # Personality Adaptation Capability
        try:
            capabilities["personality_adaptation"] = hasattr(
                self.personality_adapter, "adapt_response"
            )
        except Exception:
            capabilities["personality_adaptation"] = False

        # Data Storage Capability
        try:
            capabilities["data_storage"] = hasattr(self.supabase_client, "table")
        except Exception:
            capabilities["data_storage"] = False

        # File Storage Capability
        try:
            capabilities["file_storage"] = hasattr(self.gcs_client, "upload_file")
        except Exception:
            capabilities["file_storage"] = False

        # Program Classification Capability
        try:
            capabilities["program_classification"] = hasattr(
                self.program_classification_service, "classify_user_program"
            )
        except Exception:
            capabilities["program_classification"] = False

        return capabilities


def create_production_dependencies() -> StellaDependencies:
    """
    Create production dependencies with real implementations.

    Returns:
        Configured StellaDependencies for production use
    """
    try:
        from clients.vertex_ai.client import VertexAIClient
        from adapters.personality_adapter import PersonalityAdapter
        from clients.supabase_client import SupabaseClient
        from services.program_classification_service import ProgramClassificationService
        from adapters.mcp_toolkit import MCPToolkit
        from adapters.state_manager_adapter import StateManagerAdapter
        from adapters.intent_analyzer_adapter import IntentAnalyzerAdapter
        from adapters.a2a_adapter import A2AAdapter
        from clients.gcs_client import GCSClient
        from processors.vision_processor import VisionProcessor
        from adapters.multimodal_adapter import MultimodalAdapter

        return StellaDependencies(
            vertex_ai_client=VertexAIClient(),
            personality_adapter=PersonalityAdapter(),
            supabase_client=SupabaseClient(),
            gcs_client=GCSClient(),
            program_classification_service=ProgramClassificationService(),
            vision_processor=VisionProcessor(),
            multimodal_adapter=MultimodalAdapter(),
            mcp_toolkit=MCPToolkit(),
            state_manager_adapter=StateManagerAdapter(),
            intent_analyzer_adapter=IntentAnalyzerAdapter(),
            a2a_adapter=A2AAdapter(),
        )

    except ImportError as e:
        raise ImportError(f"Failed to import production dependencies: {e}")


def create_test_dependencies() -> StellaDependencies:
    """
    Create test dependencies with mock implementations.

    Returns:
        Configured StellaDependencies for testing
    """
    from unittest.mock import MagicMock

    # Create mock dependencies
    mock_gemini = MagicMock()
    mock_gemini.generate_content.return_value = {
        "success": True,
        "content": "Test AI response for progress analysis",
    }

    mock_personality = MagicMock()
    mock_personality.adapt_response.return_value = {
        "success": True,
        "adapted_message": "STELLA-adapted response",
        "confidence_score": 0.9,
    }

    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_supabase
    mock_supabase.insert.return_value = mock_supabase
    mock_supabase.select.return_value = mock_supabase
    mock_supabase.execute.return_value = {"data": [], "error": None}

    mock_gcs = MagicMock()
    mock_gcs.upload_file.return_value = "gs://test-bucket/test-file.png"

    mock_vision = MagicMock()
    mock_vision.analyze_image.return_value = {
        "success": True,
        "analysis": "Test image analysis result",
    }

    mock_multimodal = MagicMock()
    mock_multimodal.process_inputs.return_value = {
        "success": True,
        "processed_data": "Test multimodal processing",
    }

    mock_program_classification = MagicMock()
    mock_program_classification.classify_user_program.return_value = {
        "program_type": "PRIME",
        "confidence_score": 0.95,
    }

    return StellaDependencies(
        vertex_ai_client=mock_gemini,
        personality_adapter=mock_personality,
        supabase_client=mock_supabase,
        gcs_client=mock_gcs,
        program_classification_service=mock_program_classification,
        vision_processor=mock_vision,
        multimodal_adapter=mock_multimodal,
        mcp_toolkit=MagicMock(),
        state_manager_adapter=MagicMock(),
        intent_analyzer_adapter=MagicMock(),
        a2a_adapter=MagicMock(),
    )
