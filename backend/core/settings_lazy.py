"""
Lazy-initialized settings for GENESIS.

This module provides lazy initialization for settings to prevent
blocking during imports.
"""

from core.settings import Settings
from core.lazy_init import LazyInstance

# Create a lazy-initialized settings instance
settings = LazyInstance(
    factory=lambda: Settings(),
    name="Settings"
)