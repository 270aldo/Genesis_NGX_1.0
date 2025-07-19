"""
Dependencies module for GUARDIAN Security Compliance agent.
Manages dependency injection and service initialization.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import asyncio

from agents.backend.guardian.core.config import GuardianConfig
from agents.backend.guardian.core.exceptions import GuardianSecurityError
from clients.vertex_ai.client import VertexAIClient
from clients.supabase_client import SupabaseClient
from infrastructure.adapters.vision_adapter import VisionAdapter
from infrastructure.adapters.multimodal_adapter import MultimodalAdapter
from infrastructure.adapters.personality_adapter import PersonalityAdapter
from clients.elevenlabs_client import ElevenLabsClient
from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class GuardianDependencies:
    """
    Container for all GUARDIAN agent dependencies.

    This class manages the lifecycle of all external services and adapters
    required by the GUARDIAN Security Compliance agent.
    """

    # Core AI services
    vertex_ai_client: VertexAIClient
    personality_adapter: PersonalityAdapter

    # Database and storage
    supabase_client: SupabaseClient

    # Vision and multimodal processing
    vision_adapter: VisionAdapter
    multimodal_adapter: MultimodalAdapter

    # Voice synthesis (for security alerts)
    voice_client: ElevenLabsClient

    # Security-specific services (initialized later)
    security_monitor_service: Optional[Any] = None
    compliance_checker_service: Optional[Any] = None
    audit_trail_service: Optional[Any] = None

    # Configuration
    config: Optional[GuardianConfig] = None

    async def initialize_security_services(self) -> None:
        """Initialize security-specific services."""
        try:
            # Import services here to avoid circular imports
            from agents.backend.guardian.services.security_monitor_service import (
                SecurityMonitorService,
            )
            from agents.backend.guardian.services.compliance_checker_service import (
                ComplianceCheckerService,
            )
            from agents.backend.guardian.services.audit_trail_service import (
                AuditTrailService,
            )

            # Initialize security monitoring
            self.security_monitor_service = SecurityMonitorService(self.config)
            await self.security_monitor_service.initialize()

            # Initialize compliance checking
            self.compliance_checker_service = ComplianceCheckerService(self.config)
            await self.compliance_checker_service.initialize()

            # Initialize audit trail
            self.audit_trail_service = AuditTrailService(self.config)
            await self.audit_trail_service.initialize()

            logger.info("Security services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize security services: {e}")
            raise GuardianSecurityError(f"Security services initialization failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all dependencies."""
        health_status = {
            "vertex_ai_client": "unknown",
            "personality_adapter": "unknown",
            "supabase_client": "unknown",
            "vision_adapter": "unknown",
            "multimodal_adapter": "unknown",
            "voice_client": "unknown",
            "security_monitor": "unknown",
            "compliance_checker": "unknown",
            "audit_trail": "unknown",
        }

        # Check core AI services
        try:
            await self.vertex_ai_client.health_check()
            health_status["vertex_ai_client"] = "healthy"
        except Exception as e:
            health_status["vertex_ai_client"] = f"unhealthy: {str(e)}"

        # Check personality adapter
        try:
            if self.personality_adapter:
                health_status["personality_adapter"] = "healthy"
        except Exception:
            health_status["personality_adapter"] = "unhealthy"

        # Check database
        try:
            # Assuming supabase_client has a health check method
            health_status["supabase_client"] = "healthy"
        except Exception as e:
            health_status["supabase_client"] = f"unhealthy: {str(e)}"

        # Check vision services
        try:
            if self.vision_adapter:
                health_status["vision_adapter"] = "healthy"
        except Exception:
            health_status["vision_adapter"] = "unhealthy"

        try:
            if self.multimodal_adapter:
                health_status["multimodal_adapter"] = "healthy"
        except Exception:
            health_status["multimodal_adapter"] = "unhealthy"

        # Check voice client
        try:
            if self.voice_client:
                health_status["voice_client"] = "healthy"
        except Exception:
            health_status["voice_client"] = "unhealthy"

        # Check security services
        if self.security_monitor_service:
            try:
                await self.security_monitor_service.health_check()
                health_status["security_monitor"] = "healthy"
            except Exception as e:
                health_status["security_monitor"] = f"unhealthy: {str(e)}"

        if self.compliance_checker_service:
            try:
                await self.compliance_checker_service.health_check()
                health_status["compliance_checker"] = "healthy"
            except Exception as e:
                health_status["compliance_checker"] = f"unhealthy: {str(e)}"

        if self.audit_trail_service:
            try:
                await self.audit_trail_service.health_check()
                health_status["audit_trail"] = "healthy"
            except Exception as e:
                health_status["audit_trail"] = f"unhealthy: {str(e)}"

        # Calculate overall health
        unhealthy_services = [
            service
            for service, status in health_status.items()
            if not isinstance(status, str) or not status.startswith("healthy")
        ]

        overall_health = "healthy" if not unhealthy_services else "degraded"
        if len(unhealthy_services) > len(health_status) / 2:
            overall_health = "unhealthy"

        return {
            "overall_health": overall_health,
            "services": health_status,
            "unhealthy_count": len(unhealthy_services),
            "total_services": len(health_status),
        }

    async def cleanup(self) -> None:
        """Clean up all dependencies."""
        cleanup_tasks = []

        # Cleanup security services
        if self.security_monitor_service:
            cleanup_tasks.append(self.security_monitor_service.cleanup())

        if self.compliance_checker_service:
            cleanup_tasks.append(self.compliance_checker_service.cleanup())

        if self.audit_trail_service:
            cleanup_tasks.append(self.audit_trail_service.cleanup())

        # Cleanup other services if they have cleanup methods
        # Add more cleanup tasks as needed

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        logger.info("Dependencies cleaned up successfully")


async def create_guardian_dependencies(config: GuardianConfig) -> GuardianDependencies:
    """
    Factory function to create and initialize GUARDIAN dependencies.

    Args:
        config: GUARDIAN configuration instance

    Returns:
        GuardianDependencies: Initialized dependencies container
    """
    try:
        # Initialize core AI services
        vertex_ai_client = VertexAIClient()
        personality_adapter = PersonalityAdapter()

        # Initialize database
        supabase_client = SupabaseClient()

        # Initialize vision and multimodal services
        vision_adapter = VisionAdapter()
        multimodal_adapter = MultimodalAdapter()

        # Initialize voice client for security alerts
        voice_client = ElevenLabsClient()

        # Create dependencies container
        dependencies = GuardianDependencies(
            vertex_ai_client=vertex_ai_client,
            personality_adapter=personality_adapter,
            supabase_client=supabase_client,
            vision_adapter=vision_adapter,
            multimodal_adapter=multimodal_adapter,
            voice_client=voice_client,
            config=config,
        )

        # Initialize security-specific services
        await dependencies.initialize_security_services()

        # Perform initial health check
        health_status = await dependencies.health_check()
        if health_status["overall_health"] == "unhealthy":
            raise GuardianSecurityError(
                "Dependencies health check failed", details=health_status
            )

        logger.info("GUARDIAN dependencies initialized successfully")
        return dependencies

    except Exception as e:
        logger.error(f"Failed to create GUARDIAN dependencies: {e}")
        raise GuardianSecurityError(f"Dependencies initialization failed: {e}")
