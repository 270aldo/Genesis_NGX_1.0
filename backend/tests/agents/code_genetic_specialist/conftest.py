"""
Test configuration and fixtures for CODE Genetic Specialist.
Provides comprehensive testing infrastructure for A+ level testing.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List
from datetime import datetime, timedelta

from agents.code_genetic_specialist.agent_refactored import CodeGeneticSpecialist
from agents.code_genetic_specialist.core.dependencies import AgentDependencies
from agents.code_genetic_specialist.core.config import CodeGeneticConfig
from core.personality.personality_adapter import PersonalityAdapter, PersonalityProfile


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for testing."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_personality_adapter():
    """Mock PersonalityAdapter with realistic genetic analysis responses."""
    adapter = AsyncMock(spec=PersonalityAdapter)

    # Configure realistic genetic communication responses
    adapter.adapt_response.return_value = {
        "adapted_message": "Your genetic analysis reveals strategic optimization opportunities for enhanced performance.",
        "confidence_score": 0.92,
        "adaptation_type": "PRIME",
        "metadata": {
            "program_type": "NGX_PRIME",
            "adaptation_applied": True,
            "genetic_sensitivity_maintained": True,
            "scientific_accuracy_preserved": True,
            "processing_time_ms": 180,
        },
    }

    adapter.initialize_profile.return_value = True
    return adapter


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client with realistic genetic analysis AI responses."""
    client = AsyncMock()

    # Standard genetic analysis response
    client.generate_content.return_value = {
        "content": "Based on your genetic profile, you have variants associated with enhanced athletic performance...",
        "confidence": 0.94,
        "model_version": "gemini-pro-1.5-genetics",
        "processing_time_ms": 450,
        "genetic_analysis_metadata": {
            "variants_analyzed": 23,
            "databases_consulted": ["ClinVar", "PharmGKB", "GWAS Catalog"],
            "scientific_references": 12,
        },
    }

    return client


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for genetic data storage."""
    client = AsyncMock()

    # Mock genetic data queries
    client.from_().select().eq().execute.return_value = {
        "data": [
            {
                "user_id": "test_user_123",
                "genetic_profile": {
                    "variants": ["rs1815739", "rs4680", "rs1042713"],
                    "ancestry": "European",
                    "quality_score": 0.95,
                },
                "consent_status": "active",
                "consent_date": datetime.utcnow().isoformat(),
                "data_encrypted": True,
            }
        ],
        "error": None,
    }

    return client


@pytest.fixture
def mock_genetic_security_service():
    """Mock genetic security service for testing."""
    service = AsyncMock()
    service.validate_encryption_status.return_value = True
    service.log_audit_event.return_value = True
    service.initialize.return_value = None
    return service


@pytest.fixture
def mock_consent_service():
    """Mock consent management service for testing."""
    service = AsyncMock()
    service.has_valid_consent.return_value = True
    service.initialize.return_value = None
    return service


@pytest.fixture
def test_dependencies(
    mock_personality_adapter, mock_gemini_client, mock_supabase_client
):
    """Create test dependencies with comprehensive mocks."""
    return AgentDependencies(
        personality_adapter=mock_personality_adapter,
        vertex_ai_client=mock_gemini_client,
        supabase_client=mock_supabase_client,
        program_classification_service=AsyncMock(),
        mcp_toolkit=MagicMock(),
        state_manager_adapter=AsyncMock(),
        intent_analyzer_adapter=AsyncMock(),
        a2a_adapter=AsyncMock(),
    )


@pytest.fixture
def test_config():
    """Create test configuration for CODE agent."""
    return CodeGeneticConfig(
        max_response_time=5.0,
        retry_attempts=1,
        cache_ttl=60,
        enable_personality_adaptation=True,
        enable_real_genetic_analysis=False,  # Use mock data for testing
        enable_audit_logging=True,
        enable_data_encryption=True,
        enable_gdpr_compliance=True,
        enable_hipaa_compliance=True,
        debug_mode=True,
        log_level="DEBUG",
    )


@pytest.fixture
async def agent(
    test_dependencies, test_config, mock_genetic_security_service, mock_consent_service
):
    """Create and initialize CODE agent for testing."""
    with patch(
        "agents.code_genetic_specialist.agent_refactored.GeneticSecurityService"
    ) as mock_security:
        with patch(
            "agents.code_genetic_specialist.agent_refactored.ConsentManagementService"
        ) as mock_consent:
            mock_security.return_value = mock_genetic_security_service
            mock_consent.return_value = mock_consent_service

            agent = CodeGeneticSpecialist(test_dependencies, test_config)
            await agent.initialize()
            return agent


@pytest.fixture
def sample_genetic_context():
    """Sample genetic analysis context for testing."""
    return {
        "user_id": "test_user_123",
        "program_type": "NGX_PRIME",
        "user_profile": {
            "age": 30,
            "sex": "male",
            "ancestry": "European",
            "genetic_consent": True,
            "analysis_preferences": {
                "focus_areas": ["performance", "nutrition", "recovery"],
                "detail_level": "comprehensive",
            },
        },
        "genetic_data": {
            "file_format": "23andme",
            "variants_count": 650000,
            "quality_score": 0.96,
            "processing_status": "completed",
        },
        "session_context": {
            "conversation_history": [],
            "current_analysis_type": "comprehensive_profile",
        },
    }


@pytest.fixture
def prime_genetic_profile():
    """PRIME user genetic profile for testing."""
    return PersonalityProfile(
        program_type="NGX_PRIME",
        user_traits={
            "communication_style": "scientific",
            "detail_preference": "comprehensive",
            "technical_depth": "high",
            "genetic_focus": "performance_optimization",
        },
        context_preferences={
            "language_complexity": "advanced",
            "risk_communication": "direct",
            "scientific_references": "detailed",
        },
    )


@pytest.fixture
def longevity_genetic_profile():
    """LONGEVITY user genetic profile for testing."""
    return PersonalityProfile(
        program_type="NGX_LONGEVITY",
        user_traits={
            "communication_style": "nurturing",
            "detail_preference": "accessible",
            "technical_depth": "moderate",
            "genetic_focus": "wellness_optimization",
        },
        context_preferences={
            "language_complexity": "accessible",
            "risk_communication": "supportive",
            "emotional_support": "enhanced",
        },
    )


@pytest.fixture
def sample_genetic_variants():
    """Sample genetic variants for testing."""
    return {
        "performance_variants": {
            "ACTN3": {
                "rs1815739": {
                    "genotype": "CC",
                    "phenotype": "Enhanced power performance",
                    "confidence": 0.95,
                    "population_frequency": 0.55,
                }
            },
            "ACE": {
                "rs4340": {
                    "genotype": "II",
                    "phenotype": "Enhanced endurance capacity",
                    "confidence": 0.92,
                    "population_frequency": 0.45,
                }
            },
        },
        "nutrition_variants": {
            "FTO": {
                "rs9939609": {
                    "genotype": "AT",
                    "phenotype": "Moderate obesity risk",
                    "confidence": 0.88,
                    "population_frequency": 0.42,
                }
            },
            "MTHFR": {
                "rs1801133": {
                    "genotype": "CT",
                    "phenotype": "Reduced folate processing",
                    "confidence": 0.94,
                    "population_frequency": 0.38,
                }
            },
        },
        "pharmacogenomics_variants": {
            "CYP2D6": {
                "activity_score": 1.5,
                "phenotype": "Normal metabolizer",
                "drugs_affected": ["codeine", "tramadol", "metoprolol"],
                "confidence": 0.96,
            }
        },
    }


@pytest.fixture
def sample_genetic_analysis_result():
    """Sample genetic analysis result for testing."""
    return {
        "success": True,
        "analysis_type": "comprehensive_profile",
        "user_id": "test_user_123",
        "analysis_id": "genetic_analysis_123456",
        "content": "Your genetic profile reveals strategic optimization opportunities...",
        "genetic_insights": {
            "performance_potential": {
                "power_sports": "high",
                "endurance_sports": "moderate",
                "recovery_rate": "above_average",
            },
            "nutrition_optimization": {
                "carbohydrate_sensitivity": "normal",
                "fat_metabolism": "efficient",
                "vitamin_requirements": ["B12", "folate", "vitamin_D"],
            },
            "health_predispositions": {
                "cardiovascular_risk": "low",
                "metabolic_efficiency": "high",
                "inflammation_response": "balanced",
            },
        },
        "recommendations": [
            "Focus on power-based training for optimal genetic expression",
            "Maintain balanced macronutrient intake with attention to folate",
            "Consider B-vitamin supplementation based on MTHFR variant",
        ],
        "confidence_score": 0.93,
        "processing_time_ms": 2450,
        "variants_analyzed": 45,
        "scientific_references": 23,
        "timestamp": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def mock_genetic_database_responses():
    """Mock responses from genetic databases."""
    return {
        "clinvar": {
            "rs1815739": {
                "clinical_significance": "benign",
                "condition": "Athletic performance",
                "review_status": "reviewed_by_expert_panel",
            }
        },
        "pharmgkb": {
            "CYP2D6": {
                "gene_function": "normal",
                "drug_interactions": ["codeine", "tramadol"],
                "guideline_annotations": 15,
            }
        },
        "gwas_catalog": {
            "rs9939609": {
                "trait": "body mass index",
                "p_value": 1.2e-15,
                "effect_size": 0.39,
                "study_size": 125000,
            }
        },
    }


# Performance testing fixtures
@pytest.fixture
def performance_test_data():
    """Data for performance testing scenarios."""
    return {
        "concurrent_requests": 50,
        "large_genetic_file": "genetic_data_1M_variants.vcf",
        "complex_analysis_request": "comprehensive_multi_domain_analysis",
        "target_response_time_ms": 500,
        "max_memory_usage_mb": 512,
    }


# Security testing fixtures
@pytest.fixture
def security_test_scenarios():
    """Security testing scenarios for genetic data."""
    return {
        "encryption_test": {
            "plaintext_genetic_data": "ATCG" * 1000,
            "expected_encrypted": True,
        },
        "consent_scenarios": [
            {"consent_status": "active", "should_allow": True},
            {"consent_status": "revoked", "should_allow": False},
            {"consent_status": "expired", "should_allow": False},
            {"consent_status": None, "should_allow": False},
        ],
        "audit_log_requirements": [
            "user_id",
            "timestamp",
            "action",
            "data_accessed",
            "consent_verified",
        ],
    }


# Property-based testing helpers
@pytest.fixture
def genetic_data_generators():
    """Generators for property-based testing."""
    return {
        "valid_genotypes": ["AA", "AT", "TT", "CC", "CG", "GG"],
        "valid_chromosomes": list(range(1, 23)) + ["X", "Y"],
        "valid_positions": range(1, 250000000),
        "valid_confidence_scores": [0.7, 0.8, 0.9, 0.95, 0.99],
        "valid_ancestries": [
            "European",
            "African",
            "Asian",
            "Hispanic",
            "Native American",
            "Mixed",
        ],
    }
