"""
Dependency injection container for Precision Nutrition Architect Agent.
Provides centralized management of all agent dependencies following A+ standards.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging
from pathlib import Path

# Core imports
from core.personality.personality_adapter import PersonalityAdapter
from clients.vertex_ai.client import VertexAIClient

# Simplify imports to avoid dependency issues

logger = logging.getLogger(__name__)


@dataclass
class NutritionAgentDependencies:
    """
    Centralized dependency container for SAGE agent.
    Follows dependency injection pattern for testability and maintainability.
    """

    # Core AI/ML clients
    personality_adapter: PersonalityAdapter
    vertex_ai_client: VertexAIClient

    # Database and caching (simplified)
    supabase_client: Optional[Any] = None
    cache: Optional[Any] = None

    # Service management (simplified)
    circuit_breaker: Optional[Any] = None
    telemetry: Optional[Any] = None

    # Nutrition-specific services (to be injected)
    nutrition_analyzer: Optional[Any] = None
    biomarker_analyzer: Optional[Any] = None
    meal_planner: Optional[Any] = None
    supplement_advisor: Optional[Any] = None

    @classmethod
    def create_default(cls) -> "NutritionAgentDependencies":
        """
        Factory method to create dependencies with default configuration.
        Used for production instances.
        """
        try:
            # Initialize core dependencies
            personality_adapter = PersonalityAdapter()
            vertex_ai_client = VertexAIClient()

            # Optional dependencies simplified
            supabase_client = None
            cache = None
            circuit_breaker = None
            telemetry = None

            return cls(
                personality_adapter=personality_adapter,
                vertex_ai_client=vertex_ai_client,
                supabase_client=supabase_client,
                cache=cache,
                circuit_breaker=circuit_breaker,
                telemetry=telemetry,
            )

        except Exception as e:
            logger.error(f"Failed to create default dependencies: {e}")
            raise

    @classmethod
    def create_for_testing(cls, **overrides) -> "NutritionAgentDependencies":
        """
        Factory method for creating test dependencies with mocks.
        Allows selective override of specific dependencies.
        """
        # Create minimal test dependencies
        defaults = {
            "personality_adapter": PersonalityAdapter(),
            "vertex_ai_client": None,  # Should be mocked in tests
            "supabase_client": None,
            "cache": None,
            "circuit_breaker": None,
            "telemetry": None,
        }

        # Apply overrides
        defaults.update(overrides)

        return cls(**defaults)

    def inject_nutrition_services(
        self,
        nutrition_analyzer: Any,
        biomarker_analyzer: Any,
        meal_planner: Any,
        supplement_advisor: Any,
    ) -> None:
        """
        Inject nutrition-specific service implementations.
        Called after core dependencies are initialized.
        """
        self.nutrition_analyzer = nutrition_analyzer
        self.biomarker_analyzer = biomarker_analyzer
        self.meal_planner = meal_planner
        self.supplement_advisor = supplement_advisor

        logger.info("Nutrition services injected successfully")

    def validate_dependencies(self) -> bool:
        """
        Validate that all required dependencies are properly initialized.
        Returns True if all critical dependencies are present.
        """
        critical_deps = [
            ("personality_adapter", self.personality_adapter),
            ("vertex_ai_client", self.vertex_ai_client),
        ]

        for name, dep in critical_deps:
            if dep is None:
                logger.error(f"Critical dependency '{name}' is not initialized")
                return False

        # Warn about optional dependencies
        optional_deps = [
            ("supabase_client", self.supabase_client),
            ("nutrition_analyzer", self.nutrition_analyzer),
            ("biomarker_analyzer", self.biomarker_analyzer),
        ]

        for name, dep in optional_deps:
            if dep is None:
                logger.warning(f"Optional dependency '{name}' is not initialized")

        return True

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of all dependencies.
        Used for monitoring and diagnostics.
        """
        status = {
            "core_dependencies": {
                "personality_adapter": self.personality_adapter is not None,
                "vertex_ai_client": self.vertex_ai_client is not None,
            },
            "optional_dependencies": {
                "supabase": self.supabase_client is not None,
                "cache": self.cache is not None,
                "circuit_breaker": self.circuit_breaker is not None,
            },
            "nutrition_services": {
                "nutrition_analyzer": self.nutrition_analyzer is not None,
                "biomarker_analyzer": self.biomarker_analyzer is not None,
                "meal_planner": self.meal_planner is not None,
                "supplement_advisor": self.supplement_advisor is not None,
            },
        }

        # Add cache stats if available
        if self.cache:
            try:
                status["cache_stats"] = self.cache.get_stats()
            except Exception:
                status["cache_stats"] = "unavailable"

        # Add circuit breaker status if available
        if self.circuit_breaker:
            try:
                status["circuit_breaker_state"] = str(self.circuit_breaker.state)
            except Exception:
                status["circuit_breaker_state"] = "unavailable"

        return status
