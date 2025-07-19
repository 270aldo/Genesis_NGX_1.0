"""
WAVE Performance Analytics Agent Testing Module.
A+ testing framework with comprehensive coverage.
"""

__version__ = "1.0.0"
__description__ = "Comprehensive testing suite for WAVE Performance Analytics Agent"

# Test configuration constants
TEST_CONFIG = {
    "coverage_target": 90,  # 90%+ coverage target
    "performance_benchmarks": {
        "simple_query_ms": 500,
        "complex_analysis_ms": 2000,
        "fusion_analysis_ms": 3000,
        "health_check_ms": 100,
    },
    "security_requirements": {
        "encryption_enabled": True,
        "gdpr_compliant": True,
        "hipaa_compliant": True,
        "audit_logging": True,
    },
    "load_testing": {
        "concurrent_users": 50,
        "requests_per_second": 10,
        "max_memory_mb": 100,
    },
}

# Test categories
TEST_CATEGORIES = [
    "unit",  # Unit tests for individual components
    "integration",  # Integration tests for full workflows
    "performance",  # Performance and load testing
    "security",  # Security and compliance testing
]

# A+ Testing Quality Standards
QUALITY_STANDARDS = {
    "code_coverage": {"minimum": 85, "target": 90, "excellent": 95},
    "test_performance": {
        "max_test_runtime_seconds": 300,  # 5 minutes max
        "max_single_test_seconds": 30,
        "parallel_execution": True,
    },
    "test_reliability": {
        "flaky_test_tolerance": 0,  # Zero tolerance for flaky tests
        "test_isolation": True,
        "deterministic_results": True,
    },
    "security_testing": {
        "vulnerability_scanning": True,
        "penetration_testing": True,
        "compliance_validation": True,
    },
}


def get_test_config():
    """Get test configuration."""
    return TEST_CONFIG


def get_quality_standards():
    """Get A+ quality standards."""
    return QUALITY_STANDARDS
