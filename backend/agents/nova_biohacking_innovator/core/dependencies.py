"""
NOVA Biohacking Innovator Dependencies.
Dependency injection container for A+ standardized biohacking capabilities.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from core.logging_config import get_logger

from clients.vertex_ai.client import VertexAIClient
from clients.supabase_client import SupabaseClient
from clients.gcs_client import GCSClient
from core.personality.personality_adapter import PersonalityAdapter
from services.program_classification_service import ProgramClassificationService
from tools.mcp_toolkit import MCPToolkit
from infrastructure.adapters.state_manager_adapter import StateManagerAdapter
from infrastructure.adapters.intent_analyzer_adapter import IntentAnalyzerAdapter
from infrastructure.adapters.a2a_adapter import A2AAdapter
from infrastructure.adapters.multimodal_adapter import MultimodalAdapter
from tools.vision_processor import VisionProcessor

logger = get_logger(__name__)


@dataclass
class NovaDependencies:
    """
    Dependency injection container for NOVA Biohacking Innovator.

    Contains all external dependencies required for comprehensive biohacking innovation:
    - AI clients for analysis and recommendations
    - Data storage and processing services
    - Biohacking research and protocol services
    - Vision processing for wearable and biomarker analysis
    - Integration adapters for external systems
    """

    # AI and Analysis Services
    vertex_ai_client: VertexAIClient
    personality_adapter: PersonalityAdapter

    # Data and Storage Services
    supabase_client: SupabaseClient
    gcs_client: GCSClient

    # Biohacking-Specific Services
    program_classification_service: ProgramClassificationService
    vision_processor: VisionProcessor
    multimodal_adapter: MultimodalAdapter

    # Integration Adapters
    mcp_toolkit: MCPToolkit
    state_manager_adapter: StateManagerAdapter
    intent_analyzer_adapter: IntentAnalyzerAdapter
    a2a_adapter: A2AAdapter

    def get_dependency_health(self) -> Dict[str, str]:
        """
        Check health status of all dependencies.

        Returns:
            Dict mapping dependency names to their health status
        """
        health_status = {}

        try:
            # Check AI services
            health_status["vertex_ai_client"] = (
                "healthy" if self.vertex_ai_client else "unavailable"
            )
            health_status["personality_adapter"] = (
                "healthy" if self.personality_adapter else "unavailable"
            )

            # Check data services
            health_status["supabase_client"] = (
                "healthy" if self.supabase_client else "unavailable"
            )
            health_status["gcs_client"] = (
                "healthy" if self.gcs_client else "unavailable"
            )

            # Check biohacking services
            health_status["program_classification_service"] = (
                "healthy" if self.program_classification_service else "unavailable"
            )
            health_status["vision_processor"] = (
                "healthy" if self.vision_processor else "unavailable"
            )
            health_status["multimodal_adapter"] = (
                "healthy" if self.multimodal_adapter else "unavailable"
            )

            # Check integration adapters
            health_status["mcp_toolkit"] = (
                "healthy" if self.mcp_toolkit else "unavailable"
            )
            health_status["state_manager_adapter"] = (
                "healthy" if self.state_manager_adapter else "unavailable"
            )
            health_status["intent_analyzer_adapter"] = (
                "healthy" if self.intent_analyzer_adapter else "unavailable"
            )
            health_status["a2a_adapter"] = (
                "healthy" if self.a2a_adapter else "unavailable"
            )

        except Exception as e:
            logger.error(f"Error checking dependency health: {str(e)}")
            health_status["health_check"] = f"error: {str(e)}"

        return health_status

    def validate_biohacking_capabilities(self) -> Dict[str, bool]:
        """
        Validate that all biohacking-specific capabilities are available.

        Returns:
            Dict mapping capability names to availability status
        """
        capabilities = {}

        try:
            # Core biohacking analysis capabilities
            capabilities["longevity_optimization"] = (
                self.vertex_ai_client is not None
                and self.program_classification_service is not None
            )

            capabilities["cognitive_enhancement"] = (
                self.vertex_ai_client is not None and self.supabase_client is not None
            )

            capabilities["hormonal_optimization"] = (
                self.vertex_ai_client is not None and self.personality_adapter is not None
            )

            capabilities["wearable_analysis"] = (
                self.vision_processor is not None
                and self.multimodal_adapter is not None
            )

            capabilities["biomarker_analysis"] = (
                self.vision_processor is not None and self.vertex_ai_client is not None
            )

            capabilities["technology_integration"] = (
                self.mcp_toolkit is not None and self.gcs_client is not None
            )

            capabilities["experimental_protocols"] = (
                self.vertex_ai_client is not None
                and self.supabase_client is not None
                and self.program_classification_service is not None
            )

            capabilities["research_synthesis"] = (
                self.vertex_ai_client is not None and self.multimodal_adapter is not None
            )

        except Exception as e:
            logger.error(f"Error validating biohacking capabilities: {str(e)}")
            capabilities["validation_error"] = False

        return capabilities


def create_production_dependencies() -> NovaDependencies:
    """
    Create production dependencies for NOVA Biohacking Innovator.

    Returns:
        Configured NovaDependencies instance for production use
    """
    try:
        logger.info("Creating production dependencies for NOVA Biohacking Innovator")

        # Initialize AI and analysis services
        vertex_ai_client = VertexAIClient()
        personality_adapter = PersonalityAdapter()

        # Initialize data and storage services
        supabase_client = SupabaseClient()
        gcs_client = GCSClient()

        # Initialize biohacking-specific services
        program_classification_service = ProgramClassificationService()
        vision_processor = VisionProcessor()
        multimodal_adapter = MultimodalAdapter()

        # Initialize integration adapters
        mcp_toolkit = MCPToolkit()
        state_manager_adapter = StateManagerAdapter()
        intent_analyzer_adapter = IntentAnalyzerAdapter()
        a2a_adapter = A2AAdapter()

        dependencies = NovaDependencies(
            vertex_ai_client=vertex_ai_client,
            personality_adapter=personality_adapter,
            supabase_client=supabase_client,
            gcs_client=gcs_client,
            program_classification_service=program_classification_service,
            vision_processor=vision_processor,
            multimodal_adapter=multimodal_adapter,
            mcp_toolkit=mcp_toolkit,
            state_manager_adapter=state_manager_adapter,
            intent_analyzer_adapter=intent_analyzer_adapter,
            a2a_adapter=a2a_adapter,
        )

        # Validate dependencies
        health_status = dependencies.get_dependency_health()
        unhealthy_services = [
            service for service, status in health_status.items() if status != "healthy"
        ]

        if unhealthy_services:
            logger.warning(f"Some dependencies are unhealthy: {unhealthy_services}")

        capabilities = dependencies.validate_biohacking_capabilities()
        missing_capabilities = [
            cap for cap, available in capabilities.items() if not available
        ]

        if missing_capabilities:
            logger.warning(
                f"Some biohacking capabilities unavailable: {missing_capabilities}"
            )

        logger.info("NOVA production dependencies created successfully")
        return dependencies

    except Exception as e:
        logger.error(f"Failed to create production dependencies: {str(e)}")
        raise RuntimeError(f"NOVA dependency initialization failed: {str(e)}")


def create_test_dependencies() -> NovaDependencies:
    """
    Create test dependencies for NOVA Biohacking Innovator.

    Returns:
        Configured NovaDependencies instance for testing
    """
    from unittest.mock import MagicMock, AsyncMock

    logger.info("Creating test dependencies for NOVA Biohacking Innovator")

    # Create mock dependencies for testing
    mock_gemini = MagicMock()
    mock_gemini.generate_content = AsyncMock(
        return_value={
            "success": True,
            "content": "🔬 Fascinating biohacking analysis! Your innovative approach to optimization shows incredible potential for enhancing human performance!",
            "tokens_used": 150,
            "model": "gemini-pro",
        }
    )

    mock_personality_adapter = MagicMock()
    mock_personality_adapter.adapt_response = AsyncMock(
        return_value={
            "success": True,
            "adapted_message": "💡 This is absolutely groundbreaking! The experimental potential here is extraordinary! Your curiosity about cutting-edge optimization is inspiring! 🚀",
            "confidence_score": 0.91,
            "personality_type": "ENTP",
            "program_type": "LONGEVITY",
        }
    )

    mock_supabase = MagicMock()
    mock_gcs = MagicMock()
    mock_program_classification = MagicMock()
    mock_vision_processor = MagicMock()
    mock_multimodal_adapter = MagicMock()
    mock_mcp_toolkit = MagicMock()
    mock_state_manager = MagicMock()
    mock_intent_analyzer = MagicMock()
    mock_a2a_adapter = MagicMock()

    return NovaDependencies(
        vertex_ai_client=mock_gemini,
        personality_adapter=mock_personality_adapter,
        supabase_client=mock_supabase,
        gcs_client=mock_gcs,
        program_classification_service=mock_program_classification,
        vision_processor=mock_vision_processor,
        multimodal_adapter=mock_multimodal_adapter,
        mcp_toolkit=mock_mcp_toolkit,
        state_manager_adapter=mock_state_manager,
        intent_analyzer_adapter=mock_intent_analyzer,
        a2a_adapter=mock_a2a_adapter,
    )
