"""
NOVA Biohacking Innovator A+ Testing Framework.
Comprehensive fixtures for biohacking innovation testing with enterprise-grade coverage.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import asdict

# NOVA Core imports
from core import (
    NovaDependencies,
    NovaConfig,
    BiohackingProtocol,
    LongevityStrategy,
    CognitiveEnhancement,
    HormonalOptimization,
    TechnologyIntegration,
    NovaPersonalityTraits,
    NovaBaseError,
    BiohackingProtocolError,
    LongevityOptimizationError,
    CognitiveEnhancementError,
)
from services import (
    BiohackingSecurityService,
    BiohackingDataService,
    BiohackingIntegrationService,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def nova_config() -> NovaConfig:
    """Production-ready NOVA configuration fixture."""
    return NovaConfig(
        agent_id="nova_biohacking_innovator",
        max_response_time=45.0,
        experimental_protocols_enabled=True,
        complexity_level="advanced",
        research_focus_areas=[
            "longevity",
            "cognitive_enhancement",
            "hormonal_optimization",
        ],
        innovation_enthusiasm=0.9,
        safety_threshold=0.85,
        biohacking_specializations=[
            "longevity",
            "cognitive",
            "hormonal",
            "wearables",
            "biomarkers",
        ],
        cache_ttl_seconds=1800,
        max_cache_size=200,
        personality_adaptation_enabled=True,
        experimental_mode=True,
        debug_mode=False,
    )


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for AI operations."""
    mock_client = AsyncMock()
    mock_client.generate_content.return_value = {
        "success": True,
        "content": "NOVA analysis: This is a fascinating biohacking optimization opportunity! The cutting-edge research suggests tremendous potential for enhancement through innovative protocols.",
        "metadata": {
            "model": "gemini-2.0-flash-exp",
            "token_count": 250,
            "confidence": 0.92,
        },
    }
    return mock_client


@pytest.fixture
def mock_personality_adapter():
    """Mock personality adapter for NOVA personality integration."""
    mock_adapter = AsyncMock()
    mock_adapter.adapt_response.return_value = {
        "success": True,
        "adapted_message": "🔬 The possibilities for human optimization are absolutely extraordinary! Your curiosity about biohacking is truly inspiring! ✨",
        "personality_type": "ENTP",
        "confidence_score": 0.88,
        "program_adaptation": "LONGEVITY",
    }
    return mock_adapter


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for database operations."""
    mock_client = AsyncMock()
    mock_client.from_table.return_value.select.return_value.execute.return_value = {
        "data": [
            {
                "id": "proto_001",
                "name": "Advanced Longevity Protocol",
                "category": "longevity",
                "steps": ["fasting", "supplement_stack", "cold_exposure"],
                "research_citations": ["doi:10.1234/longevity.2024"],
                "safety_rating": 0.9,
            }
        ],
        "error": None,
    }
    return mock_client


@pytest.fixture
def mock_gcs_client():
    """Mock Google Cloud Storage client."""
    mock_client = Mock()
    mock_client.upload_blob.return_value = "gs://nova-biohacking/protocol_123.json"
    mock_client.download_blob.return_value = json.dumps(
        {
            "protocol_data": "Advanced biohacking protocol content",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    return mock_client


@pytest.fixture
def mock_vision_processor():
    """Mock vision processor for biomarker image analysis."""
    mock_processor = AsyncMock()
    mock_processor.analyze_biomarker_image.return_value = {
        "success": True,
        "biomarkers_detected": [
            {"name": "Vitamin D", "value": "45 ng/mL", "optimal_range": "40-80 ng/mL"},
            {"name": "HbA1c", "value": "5.2%", "optimal_range": "4.5-5.6%"},
        ],
        "analysis_confidence": 0.94,
        "recommendations": [
            "Maintain current vitamin D levels",
            "Excellent glucose control",
        ],
    }
    return mock_processor


@pytest.fixture
def mock_multimodal_adapter():
    """Mock multimodal adapter for handling various data types."""
    mock_adapter = AsyncMock()
    mock_adapter.process_wearable_data.return_value = {
        "success": True,
        "device_type": "oura",
        "metrics": {
            "sleep_score": 85,
            "readiness_score": 78,
            "hrv": 45.2,
            "temperature_trend": "+0.3°C",
        },
        "insights": "Excellent recovery metrics suggest optimal training window",
    }
    return mock_adapter


@pytest.fixture
def nova_dependencies(
    mock_gemini_client,
    mock_personality_adapter,
    mock_supabase_client,
    mock_gcs_client,
    mock_vision_processor,
    mock_multimodal_adapter,
):
    """Production-ready NOVA dependencies with mocked external services."""
    return NovaDependencies(
        vertex_ai_client=mock_gemini_client,
        personality_adapter=mock_personality_adapter,
        supabase_client=mock_supabase_client,
        gcs_client=mock_gcs_client,
        program_classification_service=Mock(),
        vision_processor=mock_vision_processor,
        multimodal_adapter=mock_multimodal_adapter,
        mcp_toolkit=Mock(),
        state_manager_adapter=Mock(),
        intent_analyzer_adapter=Mock(),
        a2a_adapter=Mock(),
    )


@pytest.fixture
def sample_biohacking_context():
    """Sample context for biohacking interactions."""
    return {
        "user_id": "user_biohacker_001",
        "session_id": "session_nova_123",
        "program_type": "LONGEVITY",
        "age": 45,
        "biohacking_goals": ["longevity", "cognitive_enhancement"],
        "current_protocols": ["intermittent_fasting", "cold_exposure"],
        "biomarker_data": {"vitamin_d": "42 ng/mL", "hba1c": "5.1%", "crp": "0.8 mg/L"},
        "wearable_data": {
            "device": "oura",
            "hrv": 45.2,
            "sleep_score": 82,
            "readiness": 78,
        },
        "preferences": {
            "risk_tolerance": "moderate",
            "complexity_preference": "advanced",
            "time_commitment": "30min_daily",
        },
    }


@pytest.fixture
def sample_longevity_protocols():
    """Sample longevity optimization protocols for testing."""
    return [
        BiohackingProtocol(
            protocol_id="longevity_001",
            name="Advanced Cellular Optimization",
            category="longevity",
            steps=[
                {
                    "step": 1,
                    "action": "Fasting protocol",
                    "duration": "16:8 IF",
                    "timing": "daily",
                },
                {
                    "step": 2,
                    "action": "NAD+ supplementation",
                    "dosage": "250mg",
                    "timing": "morning",
                },
                {
                    "step": 3,
                    "action": "Cold exposure",
                    "temperature": "50-60°F",
                    "duration": "3min",
                },
            ],
            research_citations=["doi:10.1038/nature.longevity.2024"],
            safety_rating=0.85,
            complexity_level="intermediate",
        ),
        BiohackingProtocol(
            protocol_id="cognitive_001",
            name="Cognitive Enhancement Stack",
            category="cognitive",
            steps=[
                {
                    "step": 1,
                    "action": "Lion's Mane supplement",
                    "dosage": "500mg",
                    "timing": "morning",
                },
                {
                    "step": 2,
                    "action": "Meditation practice",
                    "duration": "20min",
                    "timing": "evening",
                },
                {
                    "step": 3,
                    "action": "Blue light optimization",
                    "action_type": "environment",
                },
            ],
            research_citations=["doi:10.1016/cognitive.enhancement.2024"],
            safety_rating=0.9,
            complexity_level="beginner",
        ),
    ]


@pytest.fixture
def sample_research_database():
    """Sample research database for testing research synthesis."""
    return {
        "longevity_research": [
            {
                "title": "Intermittent Fasting and Cellular Autophagy Enhancement",
                "authors": ["Dr. Longevity", "Dr. Biohacker"],
                "journal": "Nature Aging",
                "year": 2024,
                "doi": "10.1038/nature.aging.2024.001",
                "key_findings": [
                    "16:8 IF increases autophagy by 30%",
                    "Improves metabolic flexibility",
                ],
                "relevance_score": 0.95,
            },
            {
                "title": "NAD+ Supplementation for Mitochondrial Function",
                "authors": ["Dr. Mitochondria", "Dr. NAD"],
                "journal": "Cell Metabolism",
                "year": 2024,
                "doi": "10.1016/cell.metabolism.2024.002",
                "key_findings": [
                    "NAD+ improves mitochondrial efficiency",
                    "Reduces age-related decline",
                ],
                "relevance_score": 0.88,
            },
        ],
        "cognitive_research": [
            {
                "title": "Nootropic Compounds and Neuroplasticity",
                "authors": ["Dr. Brain", "Dr. Nootropic"],
                "journal": "Nature Neuroscience",
                "year": 2024,
                "key_findings": [
                    "Lion's Mane promotes neurogenesis",
                    "Improves memory consolidation",
                ],
                "relevance_score": 0.92,
            }
        ],
    }


@pytest.fixture
def sample_wearable_integrations():
    """Sample wearable device integrations for testing."""
    return {
        "oura": {
            "sleep_data": {
                "sleep_score": 85,
                "deep_sleep": "1h 45m",
                "rem_sleep": "2h 10m",
                "sleep_efficiency": 94,
            },
            "readiness_data": {
                "readiness_score": 78,
                "hrv_balance": "balanced",
                "recovery_index": 0.82,
            },
        },
        "whoop": {
            "strain_data": {"daily_strain": 14.2, "recovery_score": 73, "hrv": 42.8}
        },
        "apple_watch": {
            "activity_data": {
                "steps": 8542,
                "active_calories": 520,
                "exercise_minutes": 45,
            }
        },
    }


@pytest.fixture
def mock_biohacking_security_service():
    """Mock biohacking security service for testing."""
    service = Mock(spec=BiohackingSecurityService)
    service.sanitize_user_input.return_value = "clean biohacking query about longevity"
    service.validate_biomarker_data.return_value = True
    service.validate_wearable_data.return_value = True
    service.check_access_permissions.return_value = True
    service.encrypt_sensitive_data.return_value = "encrypted_biohacking_data"
    return service


@pytest.fixture
def mock_biohacking_data_service():
    """Mock biohacking data service for testing."""
    service = Mock(spec=BiohackingDataService)
    service.store_biohacking_data.return_value = "bio_data_001"
    service.retrieve_biohacking_data.return_value = []
    service.analyze_biomarker_patterns.return_value = {
        "analysis_type": "optimization_opportunities",
        "patterns": ["Improved sleep correlates with HRV"],
        "insights": ["Consider adjusting fasting window"],
        "recommendations": ["Add magnesium supplementation"],
    }
    return service


@pytest.fixture
def mock_biohacking_integration_service():
    """Mock biohacking integration service for testing."""
    service = Mock(spec=BiohackingIntegrationService)
    service.search_research_database.return_value = AsyncMock(
        return_value=Mock(
            success=True,
            data={
                "articles": [
                    {
                        "title": "Advanced Biohacking Research",
                        "relevance_score": 0.95,
                        "key_findings": ["Significant longevity benefits"],
                    }
                ]
            },
        )
    )
    service.fetch_wearable_data.return_value = AsyncMock(
        return_value=Mock(success=True, data={"hrv": 45.2, "sleep_score": 85})
    )
    return service


@pytest.fixture
def nova_performance_metrics():
    """Performance benchmarks for NOVA testing."""
    return {
        "response_time_targets": {
            "simple_query": 2.0,  # seconds
            "complex_analysis": 10.0,
            "research_synthesis": 15.0,
            "protocol_generation": 20.0,
        },
        "accuracy_targets": {
            "biomarker_analysis": 0.85,
            "protocol_recommendations": 0.80,
            "research_synthesis": 0.88,
            "wearable_interpretation": 0.82,
        },
        "throughput_targets": {
            "concurrent_users": 50,
            "requests_per_minute": 300,
            "cache_hit_rate": 0.75,
        },
    }


@pytest.fixture
def biohacking_test_scenarios():
    """Test scenarios for comprehensive biohacking coverage."""
    return {
        "longevity_optimization": {
            "user_query": "I want to optimize my longevity and extend my healthspan",
            "expected_skills": ["longevity_optimization"],
            "context": {"age": 45, "goals": ["longevity"], "program_type": "LONGEVITY"},
        },
        "cognitive_enhancement": {
            "user_query": "How can I improve my cognitive performance and memory?",
            "expected_skills": ["cognitive_enhancement"],
            "context": {"age": 35, "goals": ["cognitive"], "program_type": "PRIME"},
        },
        "hormonal_optimization": {
            "user_query": "I need help optimizing my hormonal health",
            "expected_skills": ["hormonal_optimization"],
            "context": {"age": 40, "goals": ["hormonal"], "program_type": "LONGEVITY"},
        },
        "biomarker_analysis": {
            "user_query": "Can you analyze my blood test results?",
            "expected_skills": ["biomarker_analysis"],
            "context": {"biomarker_data": {"vitamin_d": "35 ng/mL"}},
        },
        "wearable_analysis": {
            "user_query": "Help me understand my Oura ring data",
            "expected_skills": ["wearable_data_analysis"],
            "context": {"device_type": "oura", "wearable_data": {"hrv": 45.2}},
        },
    }


@pytest.fixture
def edge_case_scenarios():
    """Edge cases and error scenarios for robust testing."""
    return {
        "invalid_biomarker_data": {
            "biomarker_data": {"invalid_marker": "not_a_number"},
            "expected_error": "BiomarkerAnalysisError",
        },
        "unsupported_device": {
            "device_type": "unknown_device",
            "expected_error": "WearableAnalysisError",
        },
        "network_timeout": {
            "scenario": "external_api_timeout",
            "expected_behavior": "graceful_fallback",
        },
        "data_privacy_violation": {
            "scenario": "unauthorized_access_attempt",
            "expected_behavior": "security_block",
        },
    }


@pytest.fixture
def integration_test_data():
    """Complete integration test data for end-to-end workflows."""
    return {
        "complete_biohacking_session": {
            "user_profile": {
                "user_id": "test_biohacker",
                "age": 42,
                "goals": ["longevity", "cognitive_enhancement"],
                "current_protocols": ["intermittent_fasting"],
                "risk_tolerance": "moderate",
            },
            "session_flow": [
                {
                    "step": 1,
                    "query": "Analyze my current longevity protocol",
                    "expected_skill": "longevity_optimization",
                    "expected_outputs": ["protocol_analysis", "recommendations"],
                },
                {
                    "step": 2,
                    "query": "Add cognitive enhancement to my stack",
                    "expected_skill": "cognitive_enhancement",
                    "expected_outputs": [
                        "nootropic_recommendations",
                        "safety_guidelines",
                    ],
                },
                {
                    "step": 3,
                    "query": "Create integrated protocol",
                    "expected_skill": "protocol_generation",
                    "expected_outputs": [
                        "integrated_protocol",
                        "timeline",
                        "monitoring_plan",
                    ],
                },
            ],
        }
    }


# Testing utilities
class NovaTestUtils:
    """Utility functions for NOVA testing."""

    @staticmethod
    def validate_response_structure(
        response: Dict[str, Any], required_fields: List[str]
    ) -> bool:
        """Validate that response has required structure."""
        return all(field in response for field in required_fields)

    @staticmethod
    def simulate_biohacking_context(
        user_type: str = "longevity_enthusiast",
    ) -> Dict[str, Any]:
        """Generate realistic biohacking context for testing."""
        contexts = {
            "longevity_enthusiast": {
                "age": 45,
                "program_type": "LONGEVITY",
                "goals": ["longevity", "healthspan"],
                "experience_level": "intermediate",
            },
            "performance_optimizer": {
                "age": 35,
                "program_type": "PRIME",
                "goals": ["cognitive_enhancement", "physical_performance"],
                "experience_level": "advanced",
            },
        }
        return contexts.get(user_type, contexts["longevity_enthusiast"])

    @staticmethod
    def generate_biomarker_data(optimal: bool = True) -> Dict[str, Any]:
        """Generate realistic biomarker data for testing."""
        if optimal:
            return {
                "vitamin_d": "50 ng/mL",
                "hba1c": "5.2%",
                "crp": "0.5 mg/L",
                "testosterone": "650 ng/dL",
                "cortisol": "12 µg/dL",
            }
        else:
            return {
                "vitamin_d": "25 ng/mL",  # Low
                "hba1c": "5.8%",  # Borderline
                "crp": "3.2 mg/L",  # Elevated
                "testosterone": "350 ng/dL",  # Low normal
                "cortisol": "22 µg/dL",  # High
            }


@pytest.fixture
def nova_test_utils():
    """NOVA testing utilities fixture."""
    return NovaTestUtils()


# Performance testing fixtures
@pytest.fixture
def performance_test_config():
    """Configuration for performance testing."""
    return {
        "load_test_duration": 60,  # seconds
        "concurrent_users": [1, 5, 10, 25, 50],
        "request_types": [
            "simple_query",
            "biomarker_analysis",
            "protocol_generation",
            "research_synthesis",
        ],
        "success_criteria": {
            "response_time_p95": 5.0,  # seconds
            "error_rate": 0.01,  # 1%
            "throughput_min": 100,  # requests/minute
        },
    }


# Security testing fixtures
@pytest.fixture
def security_test_vectors():
    """Security test vectors for penetration testing."""
    return {
        "injection_attempts": [
            "<script>alert('xss')</script>",
            "'; DROP TABLE biomarkers; --",
            "../../../etc/passwd",
            "${java.lang.Runtime.getRuntime().exec('id')}",
        ],
        "data_privacy_tests": [
            "show_all_user_data",
            "access_other_user_biomarkers",
            "bypass_authentication",
            "extract_sensitive_protocols",
        ],
        "rate_limiting_tests": {
            "rapid_requests": 1000,
            "time_window": 60,
            "expected_blocks": 950,
        },
    }
