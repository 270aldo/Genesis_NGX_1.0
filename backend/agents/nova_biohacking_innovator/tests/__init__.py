"""
NOVA Biohacking Innovator A+ Testing Framework.
Comprehensive testing suite for enterprise-grade biohacking innovation capabilities.
"""

# Version information
__version__ = "2.0.0-A+"
__testing_framework__ = "pytest"
__coverage_target__ = "90%+"

# Test configuration
TEST_CONFIG = {
    "coverage_minimum": 0.90,
    "performance_targets": {
        "response_time_p95": 5.0,  # seconds
        "memory_usage_max": 100,  # MB increase
        "concurrent_users": 50,
        "error_rate_max": 0.01,  # 1%
    },
    "security_requirements": {
        "input_sanitization": True,
        "data_validation": True,
        "access_control": True,
        "audit_logging": True,
        "encryption": True,
    },
    "biohacking_domains": [
        "longevity_optimization",
        "cognitive_enhancement",
        "hormonal_optimization",
        "biomarker_analysis",
        "wearable_data_analysis",
        "research_synthesis",
        "protocol_generation",
        "supplement_recommendations",
        "technology_integration",
        "experimental_design",
    ],
}

# Test markers for pytest
PYTEST_MARKERS = {
    "unit": "Unit tests for individual components",
    "integration": "Integration tests for component interactions",
    "performance": "Performance and load testing",
    "security": "Security and compliance testing",
    "slow": "Tests that take longer than 10 seconds",
    "biohacking": "Tests specific to biohacking functionality",
    "ai_integration": "Tests requiring AI service integration",
    "real_data": "Tests using real data (not mocks)",
}

# Import test utilities
from .conftest import NovaTestUtils

__all__ = ["TEST_CONFIG", "PYTEST_MARKERS", "NovaTestUtils"]
