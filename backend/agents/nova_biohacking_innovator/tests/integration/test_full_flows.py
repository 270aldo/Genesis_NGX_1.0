"""
NOVA Biohacking Innovator - Integration Tests.
End-to-end workflow testing for complete biohacking scenarios.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

# NOVA Core imports
from core import (
    NovaDependencies,
    NovaConfig,
    BiohackingProtocol,
    NovaBaseError,
    BiohackingProtocolError,
    LongevityOptimizationError,
)
from services import (
    BiohackingSecurityService,
    BiohackingDataService,
    BiohackingIntegrationService,
)
from skills_manager import NovaSkillsManager


class TestCompleteUserJourneys:
    """Test complete user journeys through NOVA biohacking workflows."""

    @pytest.fixture
    async def nova_system(self, nova_dependencies, nova_config):
        """Complete NOVA system setup for integration testing."""
        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Setup mock responses for realistic integration flow
        nova_dependencies.vertex_ai_client.generate_content = AsyncMock(
            return_value={
                "success": True,
                "content": "NOVA analysis: This is a fascinating biohacking optimization opportunity! The cutting-edge research suggests tremendous potential for enhancement through innovative protocols.",
                "metadata": {"model": "gemini-2.0-flash-exp", "confidence": 0.92},
            }
        )

        return skills_manager

    @pytest.mark.asyncio
    async def test_longevity_optimization_complete_workflow(
        self, nova_system, sample_biohacking_context
    ):
        """Test complete longevity optimization workflow."""
        # Step 1: Initial longevity assessment
        initial_query = "I'm 45 years old and want to optimize my longevity and extend my healthspan using cutting-edge biohacking protocols"

        result_1 = await nova_system.process_message(
            initial_query, sample_biohacking_context
        )

        # Verify initial response
        assert result_1["success"] == True
        assert result_1["skill"] == "longevity_optimization"
        assert "longevity_strategies" in result_1
        assert "biomarker_recommendations" in result_1
        assert "implementation_timeline" in result_1
        assert "nova_excitement" in result_1

        # Verify NOVA personality in response
        excitement = result_1["nova_excitement"]
        assert (
            any(emoji in excitement for emoji in ["🔬", "✨", "🚀"])
            or "extraordinary" in excitement.lower()
        )

        # Step 2: Follow-up with biomarker analysis
        biomarker_context = sample_biohacking_context.copy()
        biomarker_context["biomarker_data"] = {
            "vitamin_d": "35 ng/mL",  # Suboptimal
            "hba1c": "5.4%",  # Good
            "crp": "2.1 mg/L",  # Slightly elevated
            "testosterone": "450 ng/dL",  # Normal but could be optimized
        }

        biomarker_query = "Based on these biomarker results, what specific optimizations do you recommend?"

        result_2 = await nova_system.process_message(biomarker_query, biomarker_context)

        # Verify biomarker analysis
        assert result_2["success"] == True
        assert result_2["skill"] == "biomarker_analysis"
        assert "biomarker_insights" in result_2
        assert "optimization_strategies" in result_2
        assert "supplement_recommendations" in result_2

        # Step 3: Protocol generation
        protocol_query = "Create a comprehensive longevity protocol integrating the biomarker findings"

        result_3 = await nova_system.process_message(protocol_query, biomarker_context)

        # Verify protocol generation
        assert result_3["success"] == True
        assert result_3["skill"] == "protocol_generation"

        # Verify workflow continuity
        assert all(result["success"] for result in [result_1, result_2, result_3])

    @pytest.mark.asyncio
    async def test_cognitive_enhancement_workflow(
        self, nova_system, sample_biohacking_context
    ):
        """Test cognitive enhancement workflow for executive performance."""
        # Setup PRIME context for executive user
        prime_context = sample_biohacking_context.copy()
        prime_context.update(
            {
                "program_type": "PRIME",
                "age": 38,
                "cognitive_goals": ["focus", "memory", "processing_speed"],
                "current_supplements": ["none"],
                "work_demands": "high_cognitive_load",
            }
        )

        # Step 1: Cognitive assessment and optimization request
        cognitive_query = "I need to optimize my cognitive performance for demanding executive work. Focus on memory, concentration, and mental energy."

        result_1 = await nova_system.process_message(cognitive_query, prime_context)

        # Verify cognitive enhancement response
        assert result_1["success"] == True
        assert result_1["skill"] == "cognitive_enhancement"
        assert "nootropic_protocols" in result_1
        assert "lifestyle_interventions" in result_1
        assert "technology_recommendations" in result_1
        assert "cognitive_testing" in result_1

        # Verify PRIME-specific adaptation
        if "personality_adaptation" in result_1:
            adaptation = result_1["personality_adaptation"]
            assert adaptation.get("program_type") == "PRIME"

        # Step 2: Research synthesis for cognitive compounds
        research_query = "What does the latest research say about Lion's Mane and Bacopa Monnieri for cognitive enhancement?"

        result_2 = await nova_system.process_message(research_query, prime_context)

        # Verify research synthesis
        assert result_2["success"] == True
        assert result_2["skill"] == "research_synthesis"
        assert "key_findings" in result_2
        assert "practical_applications" in result_2
        assert "safety_considerations" in result_2

        # Verify workflow continuity and knowledge building
        assert result_1["success"] and result_2["success"]

    @pytest.mark.asyncio
    async def test_wearable_data_integration_workflow(
        self, nova_system, sample_wearable_integrations
    ):
        """Test complete wearable data analysis and optimization workflow."""
        # Setup context with wearable data
        wearable_context = {
            "user_id": "wearable_user_001",
            "program_type": "LONGEVITY",
            "device_type": "oura",
            "wearable_data": sample_wearable_integrations["oura"],
            "optimization_goals": ["sleep", "recovery", "hrv"],
        }

        # Step 1: Wearable data analysis
        wearable_query = "Analyze my Oura ring data and provide insights for optimizing my recovery and sleep"

        result_1 = await nova_system.process_message(wearable_query, wearable_context)

        # Verify wearable analysis
        assert result_1["success"] == True
        assert result_1["skill"] == "wearable_data_analysis"
        assert "device_insights" in result_1
        assert "optimization_protocols" in result_1
        assert "trend_analysis" in result_1
        assert "biohacking_recommendations" in result_1

        # Step 2: Recovery protocol generation based on wearable insights
        recovery_query = (
            "Based on my wearable data, create a recovery optimization protocol"
        )

        result_2 = await nova_system.process_message(recovery_query, wearable_context)

        # Verify recovery protocol
        assert result_2["success"] == True
        # Should route to either protocol_generation or recovery-specific handling
        assert result_2["skill"] in ["protocol_generation", "longevity_optimization"]

        # Verify workflow integration
        assert result_1["success"] and result_2["success"]

    @pytest.mark.asyncio
    async def test_hormonal_optimization_workflow(self, nova_system):
        """Test hormonal optimization workflow with biomarker integration."""
        # Setup context for hormonal optimization
        hormonal_context = {
            "user_id": "hormonal_user_001",
            "program_type": "LONGEVITY",
            "age": 42,
            "gender": "male",
            "hormone_concerns": ["testosterone", "cortisol", "sleep_hormones"],
            "biomarker_data": {
                "testosterone": "380 ng/dL",  # Low normal
                "cortisol_am": "18 µg/dL",  # Slightly elevated
                "shbg": "45 nmol/L",  # Normal
                "free_t": "9.2 pg/mL",  # Low normal
            },
            "symptoms": ["low_energy", "poor_recovery", "mood_fluctuations"],
        }

        # Step 1: Hormonal assessment
        hormonal_query = "My testosterone is 380 ng/dL and I'm experiencing low energy and poor recovery. Help me optimize my hormones naturally."

        result_1 = await nova_system.process_message(hormonal_query, hormonal_context)

        # Verify hormonal optimization response
        assert result_1["success"] == True
        assert result_1["skill"] == "hormonal_optimization"
        assert "hormonal_protocols" in result_1
        assert "natural_optimization" in result_1
        assert "testing_recommendations" in result_1
        assert "lifestyle_modifications" in result_1

        # Step 2: Supplement recommendations for hormonal support
        supplement_query = "What supplements and protocols can help optimize testosterone and reduce cortisol?"

        result_2 = await nova_system.process_message(supplement_query, hormonal_context)

        # Verify supplement recommendations
        assert result_2["success"] == True
        assert result_2["skill"] == "supplement_recommendations"

        # Verify safety considerations are included
        assert "safety_considerations" in result_1
        safety_notes = result_1["safety_considerations"]
        assert any("medical supervision" in note.lower() for note in safety_notes)

        # Verify workflow continuity
        assert result_1["success"] and result_2["success"]


class TestCrossServiceIntegration:
    """Test integration between different NOVA services."""

    @pytest.mark.asyncio
    async def test_security_data_integration_flow(self, nova_dependencies, nova_config):
        """Test security service integration with data storage."""
        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Test input sanitization in workflow
        malicious_input = "<script>alert('xss')</script>I want longevity optimization"
        clean_context = {"user_id": "test_user", "program_type": "LONGEVITY"}

        # Mock security service to verify sanitization occurs
        skills_manager.security_service.sanitize_user_input = Mock(
            return_value="I want longevity optimization"
        )

        result = await skills_manager.process_message(malicious_input, clean_context)

        # Verify security service was called
        skills_manager.security_service.sanitize_user_input.assert_called_once()

        # Verify result is successful despite malicious input
        assert result["success"] == True

    @pytest.mark.asyncio
    async def test_data_service_biomarker_analysis_integration(
        self, nova_dependencies, nova_config
    ):
        """Test data service integration with biomarker analysis."""
        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Mock data service for biomarker pattern analysis
        skills_manager.data_service.analyze_biomarker_patterns = AsyncMock(
            return_value={
                "analysis_type": "optimization_opportunities",
                "patterns": [
                    "HRV correlates with sleep quality",
                    "Vitamin D affects mood",
                ],
                "insights": [
                    "Morning sunlight exposure may improve vitamin D",
                    "Sleep optimization priority",
                ],
                "recommendations": [
                    "Add vitamin D supplementation",
                    "Implement sleep hygiene protocol",
                ],
            }
        )

        biomarker_context = {
            "user_id": "integration_test",
            "biomarker_data": {"vitamin_d": "28 ng/mL", "hrv": 35.5},
        }

        result = await skills_manager.process_message(
            "Analyze my biomarker patterns for optimization opportunities",
            biomarker_context,
        )

        # Verify data service integration
        skills_manager.data_service.analyze_biomarker_patterns.assert_called_once()

        # Verify result includes quantitative analysis
        assert result["success"] == True
        assert "quantitative_analysis" in result

    @pytest.mark.asyncio
    async def test_integration_service_research_synthesis(
        self, nova_dependencies, nova_config
    ):
        """Test integration service research database functionality."""
        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Mock integration service research calls
        mock_research_response = Mock()
        mock_research_response.success = True
        mock_research_response.data = {
            "articles": [
                {
                    "title": "Longevity Research 2024",
                    "authors": ["Dr. Longevity"],
                    "journal": "Nature Aging",
                    "year": 2024,
                    "relevance_score": 0.95,
                }
            ]
        }

        skills_manager.integration_service.search_research_database = AsyncMock(
            return_value=mock_research_response
        )

        research_context = {"research_topic": "longevity optimization"}

        result = await skills_manager.process_message(
            "Find the latest research on longevity optimization", research_context
        )

        # Verify integration service was called
        skills_manager.integration_service.search_research_database.assert_called()

        # Verify research synthesis result
        assert result["success"] == True
        assert result["skill"] == "research_synthesis"
        assert "research_sources" in result


class TestPersonalityAdaptationIntegration:
    """Test personality adaptation across different biohacking workflows."""

    @pytest.mark.asyncio
    async def test_prime_vs_longevity_adaptation(self, nova_dependencies, nova_config):
        """Test personality adaptation differences between PRIME and LONGEVITY programs."""
        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Setup mock personality adapter
        async def mock_adapt_response(
            message, target_personality, program_type, context
        ):
            if program_type == "PRIME":
                return {
                    "success": True,
                    "adapted_message": "🚀 Strategic biohacking optimization for executive performance! Your analytical approach to longevity will yield competitive advantages in health ROI.",
                    "confidence_score": 0.9,
                    "program_adaptation": "PRIME",
                }
            else:  # LONGEVITY
                return {
                    "success": True,
                    "adapted_message": "🔬 The fascinating science of longevity optimization opens extraordinary possibilities for your wellness journey! Let's explore these gentle yet powerful interventions.",
                    "confidence_score": 0.88,
                    "program_adaptation": "LONGEVITY",
                }

        skills_manager.dependencies.personality_adapter.adapt_response = (
            mock_adapt_response
        )

        # Test PRIME context
        prime_context = {
            "user_id": "prime_executive",
            "program_type": "PRIME",
            "age": 40,
            "goals": ["performance_optimization", "competitive_advantage"],
        }

        prime_result = await skills_manager.process_message(
            "Optimize my longevity for executive performance", prime_context
        )

        # Test LONGEVITY context
        longevity_context = {
            "user_id": "longevity_enthusiast",
            "program_type": "LONGEVITY",
            "age": 55,
            "goals": ["healthspan", "wellness", "prevention"],
        }

        longevity_result = await skills_manager.process_message(
            "Help me with sustainable longevity practices", longevity_context
        )

        # Verify both responses are successful
        assert prime_result["success"] == True
        assert longevity_result["success"] == True

        # Verify personality adaptation was applied
        assert "personality_adaptation" in prime_result
        assert "personality_adaptation" in longevity_result

        # Verify different adaptations
        prime_adaptation = prime_result["personality_adaptation"]
        longevity_adaptation = longevity_result["personality_adaptation"]

        assert prime_adaptation["program_adaptation"] == "PRIME"
        assert longevity_adaptation["program_adaptation"] == "LONGEVITY"

        # Verify different messaging styles
        prime_message = prime_adaptation.get("adapted_message", "")
        longevity_message = longevity_adaptation.get("adapted_message", "")

        # PRIME should be more strategic/executive
        assert any(
            word in prime_message.lower()
            for word in ["strategic", "executive", "performance", "competitive", "roi"]
        )

        # LONGEVITY should be more gentle/exploratory
        assert any(
            word in longevity_message.lower()
            for word in ["fascinating", "gentle", "wellness", "journey", "explore"]
        )


class TestErrorRecoveryAndResilience:
    """Test error recovery and system resilience in integration scenarios."""

    @pytest.mark.asyncio
    async def test_gemini_api_failure_recovery(self, nova_dependencies, nova_config):
        """Test graceful handling of Gemini API failures."""
        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Mock Gemini API to fail initially, then succeed
        call_count = 0

        async def mock_gemini_with_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return {"success": False, "error": "API rate limit exceeded"}
            else:
                return {
                    "success": True,
                    "content": "NOVA fallback analysis: While external AI processing is temporarily limited, I can still provide foundational biohacking guidance based on established protocols.",
                    "metadata": {"fallback": True},
                }

        skills_manager.dependencies.vertex_ai_client.generate_content = (
            mock_gemini_with_failure
        )

        # Test that system handles failures gracefully
        result = await skills_manager.process_message(
            "What are the best longevity optimization strategies?",
            {"user_id": "resilience_test", "program_type": "LONGEVITY"},
        )

        # Should handle gracefully, not crash
        # Result might be error state or fallback content
        assert isinstance(result, dict)
        # Should not raise unhandled exceptions

    @pytest.mark.asyncio
    async def test_multiple_service_failures(self, nova_dependencies, nova_config):
        """Test handling when multiple services fail simultaneously."""
        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Mock multiple service failures
        skills_manager.dependencies.vertex_ai_client.generate_content = AsyncMock(
            return_value={"success": False, "error": "Service unavailable"}
        )

        skills_manager.integration_service.search_research_database = AsyncMock(
            return_value=Mock(success=False, error="Database connection failed")
        )

        skills_manager.dependencies.personality_adapter.adapt_response = AsyncMock(
            side_effect=Exception("Personality service down")
        )

        # System should still respond, even if with limited functionality
        result = await skills_manager.process_message(
            "Help with biohacking protocols", {"user_id": "multi_failure_test"}
        )

        # Should not crash the entire system
        assert isinstance(result, dict)
        # Should handle gracefully

    @pytest.mark.asyncio
    async def test_invalid_data_resilience(self, nova_dependencies, nova_config):
        """Test resilience to invalid or corrupted data inputs."""
        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Test with various invalid inputs
        invalid_contexts = [
            {"user_id": None, "program_type": "INVALID"},
            {"biomarker_data": "not_a_dict"},
            {"wearable_data": {"invalid": "structure"}},
            {},  # Empty context
            {"user_id": "<script>alert('xss')</script>"},  # Malicious content
        ]

        for invalid_context in invalid_contexts:
            try:
                result = await skills_manager.process_message(
                    "Test with invalid context", invalid_context
                )
                # Should either succeed with error handling or return error state
                assert isinstance(result, dict)
            except Exception as e:
                # If exceptions occur, they should be handled properly
                assert isinstance(e, (NovaBaseError, BiohackingProtocolError))


class TestPerformanceIntegration:
    """Test performance characteristics of integrated workflows."""

    @pytest.mark.asyncio
    async def test_concurrent_user_simulation(self, nova_dependencies, nova_config):
        """Test system performance with multiple concurrent users."""
        import time

        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Create multiple user contexts
        user_contexts = [
            {"user_id": f"user_{i}", "program_type": "PRIME" if i % 2 else "LONGEVITY"}
            for i in range(10)
        ]

        # Define queries for each user
        queries = [
            "Optimize my longevity protocols",
            "Analyze my cognitive performance",
            "Help with hormonal optimization",
            "Review my biomarker results",
            "Improve my wearable data insights",
        ]

        # Simulate concurrent requests
        start_time = time.time()

        tasks = []
        for i, context in enumerate(user_contexts):
            query = queries[i % len(queries)]
            task = skills_manager.process_message(query, context)
            tasks.append(task)

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = end_time - start_time

        # Verify results
        successful_results = [
            r for r in results if isinstance(r, dict) and r.get("success")
        ]

        # Should handle reasonable concurrent load
        assert len(successful_results) >= 7  # At least 70% success rate
        assert total_time < 30  # Should complete within 30 seconds

    @pytest.mark.asyncio
    async def test_memory_efficiency_in_workflows(self, nova_dependencies, nova_config):
        """Test memory efficiency during extended workflows."""
        import psutil
        import os

        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run extended workflow
        context = {"user_id": "memory_test", "program_type": "LONGEVITY"}

        # Simulate 20 interactions
        for i in range(20):
            query = f"Biohacking optimization query {i}"
            await skills_manager.process_message(query, context)

        # Check final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 100MB for this test)
        assert (
            memory_increase < 100
        ), f"Memory increased by {memory_increase}MB during workflow"

    def test_cache_performance_integration(self, nova_dependencies, nova_config):
        """Test caching performance across service integrations."""
        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Test data service caching
        data_service = skills_manager.data_service

        # Verify cache configuration
        assert data_service.cache_ttl == 1800  # 30 minutes
        assert data_service.max_cache_size == 200

        # Test integration service caching
        integration_service = skills_manager.integration_service

        # Verify circuit breaker states (part of caching strategy)
        assert integration_service.circuit_breakers is not None

        # All circuit breakers should be in closed state initially
        for service_name, breaker in integration_service.circuit_breakers.items():
            assert breaker.state == "closed"
            assert breaker.failure_count == 0
