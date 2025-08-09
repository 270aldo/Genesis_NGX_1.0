"""
NGX-Specific Feature Flags for Strategic Pivot
==============================================

This module defines the feature flags for NGX's strategic pivot where
users interact only with NEXUS (the orchestrator) instead of directly
with individual agents.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from core.feature_flags import FeatureFlag, FlagStatus, FlagType, get_feature_flags
from core.logging_config import get_logger

logger = get_logger(__name__)


# NGX Strategic Feature Flags
class NGXFeatureFlags:
    """NGX-specific feature flag definitions"""

    # Core Strategic Pivot Flags
    NEXUS_ONLY_MODE = "nexus_only_mode"  # Users interact only with NEXUS
    ENABLE_DIRECT_AGENT_ACCESS = (
        "enable_direct_agent_access"  # Legacy: direct agent chat
    )

    # UI Enhancement Flags
    SHOW_AGENT_COLLABORATION = (
        "show_agent_collaboration"  # Visual indicators when agents collaborate
    )
    SHOW_AGENT_ATTRIBUTION = "show_agent_attribution"  # Show which agent provided info
    SHOW_AGENT_ACTIVITY = "show_agent_activity"  # Real-time agent activity indicators

    # Cost Optimization Flags
    SINGLE_VOICE_CHANNEL = "single_voice_channel"  # Only NEXUS uses ElevenLabs
    OPTIMIZE_LLM_CALLS = "optimize_llm_calls"  # Batch and cache LLM calls

    # Monetization Flags
    ENABLE_COACHING_POWERUP = "enable_coaching_powerup"  # $499/mo coaching tier
    ENABLE_PIONEER_DISCOUNT = "enable_pioneer_discount"  # 50% lifetime discount

    # Beta Features
    ENABLE_BETA_FEATURES = "enable_beta_features"
    ENABLE_DEBUG_MODE = "enable_debug_mode"


async def initialize_ngx_flags():
    """Initialize NGX-specific feature flags with defaults"""

    manager = await get_feature_flags()

    # Define NGX strategic pivot flags
    flags = [
        FeatureFlag(
            name=NGXFeatureFlags.NEXUS_ONLY_MODE,
            description="Users interact only with NEXUS orchestrator",
            type=FlagType.BOOLEAN,
            status=FlagStatus.ACTIVE,
            default_value=True,  # Enabled by default for new strategy
            metadata={
                "category": "strategic",
                "impact": "high",
                "cost_savings": "93%",
                "rollout_date": datetime.utcnow().isoformat(),
            },
        ),
        FeatureFlag(
            name=NGXFeatureFlags.ENABLE_DIRECT_AGENT_ACCESS,
            description="Allow direct chat with individual agents (legacy)",
            type=FlagType.BOOLEAN,
            status=FlagStatus.ACTIVE,
            default_value=False,  # Disabled by default
            metadata={
                "category": "legacy",
                "deprecation_date": "2025-01-01",
                "migration_path": "nexus_only_mode",
            },
        ),
        FeatureFlag(
            name=NGXFeatureFlags.SHOW_AGENT_COLLABORATION,
            description="Show visual indicators when agents collaborate",
            type=FlagType.BOOLEAN,
            status=FlagStatus.ACTIVE,
            default_value=True,
            metadata={"category": "ui_enhancement", "user_experience": "transparency"},
        ),
        FeatureFlag(
            name=NGXFeatureFlags.SHOW_AGENT_ATTRIBUTION,
            description="Show which agent provided specific information",
            type=FlagType.BOOLEAN,
            status=FlagStatus.ACTIVE,
            default_value=True,
            metadata={"category": "ui_enhancement", "user_experience": "trust"},
        ),
        FeatureFlag(
            name=NGXFeatureFlags.SHOW_AGENT_ACTIVITY,
            description="Real-time indicators of agent activity",
            type=FlagType.BOOLEAN,
            status=FlagStatus.ACTIVE,
            default_value=True,
            metadata={"category": "ui_enhancement", "user_experience": "engagement"},
        ),
        FeatureFlag(
            name=NGXFeatureFlags.SINGLE_VOICE_CHANNEL,
            description="Only NEXUS uses ElevenLabs voice API",
            type=FlagType.BOOLEAN,
            status=FlagStatus.ACTIVE,
            default_value=True,
            metadata={
                "category": "cost_optimization",
                "savings": "93%",
                "api": "elevenlabs",
            },
        ),
        FeatureFlag(
            name=NGXFeatureFlags.OPTIMIZE_LLM_CALLS,
            description="Batch and cache LLM calls for efficiency",
            type=FlagType.BOOLEAN,
            status=FlagStatus.ACTIVE,
            default_value=True,
            metadata={"category": "cost_optimization", "performance": "2x"},
        ),
        FeatureFlag(
            name=NGXFeatureFlags.ENABLE_COACHING_POWERUP,
            description="Enable $499/mo coaching tier",
            type=FlagType.PERCENTAGE,
            status=FlagStatus.ACTIVE,
            default_value=False,
            target_percentage=100,  # Roll out to all users
            metadata={"category": "monetization", "price": 499, "includes_base": True},
        ),
        FeatureFlag(
            name=NGXFeatureFlags.ENABLE_PIONEER_DISCOUNT,
            description="50% lifetime discount after 6 months",
            type=FlagType.BOOLEAN,
            status=FlagStatus.ACTIVE,
            default_value=True,
            metadata={
                "category": "monetization",
                "discount": 0.5,
                "requirement_months": 6,
            },
        ),
    ]

    # Create or update flags
    for flag in flags:
        try:
            await manager.create_flag(flag)
            logger.info(f"Initialized NGX feature flag: {flag.name}")
        except Exception as e:
            # Flag might already exist, try to update
            try:
                await manager.update_flag(flag)
                logger.info(f"Updated NGX feature flag: {flag.name}")
            except Exception:
                logger.warning(f"Could not create/update flag {flag.name}: {e}")

    return True


# Convenience functions for NGX-specific checks
async def is_nexus_only_mode(context: Optional[Dict[str, Any]] = None) -> bool:
    """Check if system is in NEXUS-only mode"""
    manager = await get_feature_flags()
    return await manager.is_enabled(
        NGXFeatureFlags.NEXUS_ONLY_MODE,
        context or {},
        default=True,  # Default to new strategy
    )


async def is_direct_agent_access_enabled(
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """Check if direct agent access is enabled (legacy mode)"""
    manager = await get_feature_flags()
    return await manager.is_enabled(
        NGXFeatureFlags.ENABLE_DIRECT_AGENT_ACCESS,
        context or {},
        default=False,  # Default to disabled
    )


async def should_show_agent_collaboration(
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """Check if agent collaboration indicators should be shown"""
    manager = await get_feature_flags()
    return await manager.is_enabled(
        NGXFeatureFlags.SHOW_AGENT_COLLABORATION, context or {}, default=True
    )


async def should_show_agent_attribution(
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """Check if agent attribution should be shown"""
    manager = await get_feature_flags()
    return await manager.is_enabled(
        NGXFeatureFlags.SHOW_AGENT_ATTRIBUTION, context or {}, default=True
    )


async def is_single_voice_channel_enabled(
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """Check if only NEXUS should use voice API"""
    manager = await get_feature_flags()
    return await manager.is_enabled(
        NGXFeatureFlags.SINGLE_VOICE_CHANNEL, context or {}, default=True
    )


async def get_ngx_client_flags(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get NGX feature flags safe to send to client/frontend

    Args:
        user_id: Optional user ID for personalized flags

    Returns:
        Dictionary of client-safe feature flags
    """
    manager = await get_feature_flags()
    context = {"user_id": user_id} if user_id else {}

    # Client-safe flags
    client_flags = {
        "nexusOnlyMode": await is_nexus_only_mode(context),
        "directAgentAccess": await is_direct_agent_access_enabled(context),
        "showAgentCollaboration": await should_show_agent_collaboration(context),
        "showAgentAttribution": await should_show_agent_attribution(context),
        "showAgentActivity": await manager.is_enabled(
            NGXFeatureFlags.SHOW_AGENT_ACTIVITY, context, True
        ),
        "enableCoachingPowerup": await manager.is_enabled(
            NGXFeatureFlags.ENABLE_COACHING_POWERUP, context, False
        ),
        "enableBetaFeatures": await manager.is_enabled(
            NGXFeatureFlags.ENABLE_BETA_FEATURES, context, False
        ),
    }

    return client_flags
