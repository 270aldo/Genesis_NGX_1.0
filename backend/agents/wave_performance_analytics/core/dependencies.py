"""
Dependency injection container for WAVE Performance Analytics Agent.
Manages dependencies for the consolidated WAVE+VOLT fusion agent.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path

# Core imports
from core.personality.personality_adapter import PersonalityAdapter
from clients.vertex_ai.client_optimized import VertexAIClient
from clients.vertex_ai.vertex_ai_client import VertexAIClient
from clients.vertex_ai.vertex_search_client import VertexSearchClient
from clients.supabase_client import get_client as get_supabase_client
from core.cache_strategies import InMemoryCache
from core.circuit_breaker_service import CircuitBreakerService
from core.telemetry import TelemetryService

logger = logging.getLogger(__name__)


@dataclass
class WaveAnalyticsAgentDependencies:
    """
    Centralized dependency container for WAVE Performance Analytics fusion agent.
    Handles dependencies for both recovery (WAVE) and analytics (VOLT) capabilities.
    """

    # Core AI/ML clients
    personality_adapter: PersonalityAdapter
    vertex_ai_client: VertexAIClient
    vertex_client: VertexAIClient
    vertex_search_client: Optional[VertexSearchClient] = None

    # Database and caching
    supabase_client: Optional[Any] = None
    cache: Optional[InMemoryCache] = None

    # Service management
    circuit_breaker: Optional[CircuitBreakerService] = None
    telemetry: Optional[TelemetryService] = None

    # Recovery-specific services (from WAVE)
    injury_prevention_service: Optional[Any] = None
    rehabilitation_service: Optional[Any] = None
    sleep_optimization_service: Optional[Any] = None
    mobility_assessment_service: Optional[Any] = None

    # Analytics-specific services (from VOLT)
    biometric_analyzer: Optional[Any] = None
    pattern_recognition_service: Optional[Any] = None
    trend_analysis_service: Optional[Any] = None
    data_visualization_service: Optional[Any] = None

    # Hybrid fusion services (new)
    recovery_analytics_fusion_service: Optional[Any] = None
    injury_prediction_service: Optional[Any] = None
    performance_optimizer: Optional[Any] = None

    @classmethod
    def create_default(cls) -> "WaveAnalyticsAgentDependencies":
        """
        Factory method to create dependencies with default configuration.
        Used for production instances of the fusion agent.
        """
        try:
            # Initialize core dependencies
            personality_adapter = PersonalityAdapter()
            vertex_ai_client = VertexAIClient()
            vertex_client = VertexAIClient()

            # Initialize optional dependencies with error handling
            try:
                vertex_search_client = VertexSearchClient()
            except Exception as e:
                logger.warning(f"Failed to initialize VertexSearchClient: {e}")
                vertex_search_client = None

            try:
                supabase_client = get_supabase_client()
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}")
                supabase_client = None

            # Initialize cache with fusion-specific configuration
            cache = InMemoryCache(
                max_size=2000,  # Larger cache for analytics data
                ttl=1800,  # 30 minutes for recovery/analytics data
                eviction_policy="lru",
            )

            # Initialize service management
            circuit_breaker = CircuitBreakerService(
                failure_threshold=3,  # More sensitive for health data
                recovery_timeout=30,
                expected_exception_types=(Exception,),
            )

            telemetry = TelemetryService(service_name="wave_performance_analytics")

            return cls(
                personality_adapter=personality_adapter,
                vertex_ai_client=vertex_ai_client,
                vertex_client=vertex_client,
                vertex_search_client=vertex_search_client,
                supabase_client=supabase_client,
                cache=cache,
                circuit_breaker=circuit_breaker,
                telemetry=telemetry,
            )

        except Exception as e:
            logger.error(f"Failed to create default dependencies: {e}")
            raise

    @classmethod
    def create_for_testing(cls, **overrides) -> "WaveAnalyticsAgentDependencies":
        """
        Factory method for creating test dependencies with mocks.
        Allows selective override of specific dependencies.
        """
        # Create minimal test dependencies
        defaults = {
            "personality_adapter": PersonalityAdapter(),
            "vertex_ai_client": None,  # Should be mocked in tests
            "vertex_client": None,  # Should be mocked in tests
            "vertex_search_client": None,
            "supabase_client": None,
            "cache": InMemoryCache(max_size=100, ttl=60),
            "circuit_breaker": None,
            "telemetry": None,
        }

        # Apply overrides
        defaults.update(overrides)

        return cls(**defaults)

    def inject_recovery_services(
        self,
        injury_prevention: Any,
        rehabilitation: Any,
        sleep_optimization: Any,
        mobility_assessment: Any,
    ) -> None:
        """
        Inject recovery-specific service implementations (from WAVE).
        Called after core dependencies are initialized.
        """
        self.injury_prevention_service = injury_prevention
        self.rehabilitation_service = rehabilitation
        self.sleep_optimization_service = sleep_optimization
        self.mobility_assessment_service = mobility_assessment

        logger.info("Recovery services injected successfully")

    def inject_analytics_services(
        self,
        biometric_analyzer: Any,
        pattern_recognition: Any,
        trend_analysis: Any,
        data_visualization: Any,
    ) -> None:
        """
        Inject analytics-specific service implementations (from VOLT).
        Called after core dependencies are initialized.
        """
        self.biometric_analyzer = biometric_analyzer
        self.pattern_recognition_service = pattern_recognition
        self.trend_analysis_service = trend_analysis
        self.data_visualization_service = data_visualization

        logger.info("Analytics services injected successfully")

    def inject_fusion_services(
        self,
        recovery_analytics_fusion: Any,
        injury_prediction: Any,
        performance_optimizer: Any,
    ) -> None:
        """
        Inject hybrid fusion service implementations (new capabilities).
        These services combine recovery and analytics for enhanced insights.
        """
        self.recovery_analytics_fusion_service = recovery_analytics_fusion
        self.injury_prediction_service = injury_prediction
        self.performance_optimizer = performance_optimizer

        logger.info("Fusion services injected successfully")

    def validate_dependencies(self) -> bool:
        """
        Validate that all required dependencies are properly initialized.
        Returns True if all critical dependencies are present.
        """
        critical_deps = [
            ("personality_adapter", self.personality_adapter),
            ("vertex_ai_client", self.vertex_ai_client),
            ("vertex_client", self.vertex_client),
        ]

        for name, dep in critical_deps:
            if dep is None:
                logger.error(f"Critical dependency '{name}' is not initialized")
                return False

        # Warn about optional dependencies
        recovery_deps = [
            ("injury_prevention_service", self.injury_prevention_service),
            ("rehabilitation_service", self.rehabilitation_service),
            ("sleep_optimization_service", self.sleep_optimization_service),
            ("mobility_assessment_service", self.mobility_assessment_service),
        ]

        analytics_deps = [
            ("biometric_analyzer", self.biometric_analyzer),
            ("pattern_recognition_service", self.pattern_recognition_service),
            ("trend_analysis_service", self.trend_analysis_service),
            ("data_visualization_service", self.data_visualization_service),
        ]

        fusion_deps = [
            (
                "recovery_analytics_fusion_service",
                self.recovery_analytics_fusion_service,
            ),
            ("injury_prediction_service", self.injury_prediction_service),
            ("performance_optimizer", self.performance_optimizer),
        ]

        for category, deps in [
            ("Recovery", recovery_deps),
            ("Analytics", analytics_deps),
            ("Fusion", fusion_deps),
        ]:
            missing_count = sum(1 for name, dep in deps if dep is None)
            if missing_count > 0:
                logger.warning(
                    f"{category} services: {missing_count}/{len(deps)} not initialized"
                )

        return True

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of all dependencies including fusion-specific services.
        Used for monitoring and diagnostics.
        """
        status = {
            "core_dependencies": {
                "personality_adapter": self.personality_adapter is not None,
                "vertex_ai_client": self.vertex_ai_client is not None,
                "vertex_client": self.vertex_client is not None,
            },
            "optional_dependencies": {
                "vertex_search": self.vertex_search_client is not None,
                "supabase": self.supabase_client is not None,
                "cache": self.cache is not None,
                "circuit_breaker": self.circuit_breaker is not None,
            },
            "recovery_services": {
                "injury_prevention": self.injury_prevention_service is not None,
                "rehabilitation": self.rehabilitation_service is not None,
                "sleep_optimization": self.sleep_optimization_service is not None,
                "mobility_assessment": self.mobility_assessment_service is not None,
            },
            "analytics_services": {
                "biometric_analyzer": self.biometric_analyzer is not None,
                "pattern_recognition": self.pattern_recognition_service is not None,
                "trend_analysis": self.trend_analysis_service is not None,
                "data_visualization": self.data_visualization_service is not None,
            },
            "fusion_services": {
                "recovery_analytics_fusion": self.recovery_analytics_fusion_service
                is not None,
                "injury_prediction": self.injury_prediction_service is not None,
                "performance_optimizer": self.performance_optimizer is not None,
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

        # Calculate service readiness percentages
        recovery_ready = sum(
            1 for service in status["recovery_services"].values() if service
        )
        analytics_ready = sum(
            1 for service in status["analytics_services"].values() if service
        )
        fusion_ready = sum(
            1 for service in status["fusion_services"].values() if service
        )

        status["readiness_metrics"] = {
            "recovery_services_ready": f"{recovery_ready}/4 ({recovery_ready/4*100:.0f}%)",
            "analytics_services_ready": f"{analytics_ready}/4 ({analytics_ready/4*100:.0f}%)",
            "fusion_services_ready": f"{fusion_ready}/3 ({fusion_ready/3*100:.0f}%)",
            "overall_fusion_readiness": f"{(recovery_ready + analytics_ready + fusion_ready)}/11 ({(recovery_ready + analytics_ready + fusion_ready)/11*100:.0f}%)",
        }

        return status

    def get_fusion_capabilities(self) -> Dict[str, bool]:
        """
        Get status of fusion-specific capabilities.
        Indicates which advanced features are available.
        """
        return {
            "recovery_analytics_fusion": (
                self.recovery_analytics_fusion_service is not None
                and self.biometric_analyzer is not None
                and self.rehabilitation_service is not None
            ),
            "injury_prediction": (
                self.injury_prediction_service is not None
                and self.pattern_recognition_service is not None
                and self.injury_prevention_service is not None
            ),
            "performance_optimization": (
                self.performance_optimizer is not None
                and self.trend_analysis_service is not None
                and self.sleep_optimization_service is not None
            ),
            "holistic_analytics": (
                self.data_visualization_service is not None
                and self.mobility_assessment_service is not None
                and self.biometric_analyzer is not None
            ),
        }
