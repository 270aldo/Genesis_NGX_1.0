"""
NOVA Biohacking Innovator - Core Module.
A+ standardized implementation with modular architecture, real AI integration,
and comprehensive biohacking capabilities.
"""

from .dependencies import (
    NovaDependencies,
    create_production_dependencies,
    create_test_dependencies,
)
from .config import NovaConfig
from .exceptions import *
from .constants import (
    BiohackingProtocol,
    LongevityStrategy,
    CognitiveEnhancement,
    HormonalOptimization,
    TechnologyIntegration,
    NovaPersonalityTraits,
    NOVA_PERSONALITY_TRAITS,
    get_nova_personality_style,
    format_nova_response,
    handle_nova_exception,
)

__all__ = [
    # Dependencies
    "NovaDependencies",
    "create_production_dependencies",
    "create_test_dependencies",
    # Configuration
    "NovaConfig",
    # Constants and Types
    "BiohackingProtocol",
    "LongevityStrategy",
    "CognitiveEnhancement",
    "HormonalOptimization",
    "TechnologyIntegration",
    "NovaPersonalityTraits",
    "NOVA_PERSONALITY_TRAITS",
    "get_nova_personality_style",
    "format_nova_response",
    # Error Handling
    "handle_nova_exception",
]
