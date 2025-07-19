"""
Integration tests for WAVE Performance Analytics Agent full workflows.
A+ testing framework with end-to-end scenario validation.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from agents.wave_performance_analytics.agent_optimized import (
    WavePerformanceAnalyticsAgent,
)
from agents.wave_performance_analytics.core.exceptions import (
    WaveAnalyticsError,
    RecoveryError,
    AnalyticsError,
    FusionError,
)


class TestRecoveryWorkflows:
    """Test complete recovery analysis workflows."""

    @pytest.mark.asyncio
    async def test_injury_risk_assessment_workflow(
        self, wave_agent, sample_user_data, sample_biometric_data
    ):
        """Test complete injury risk assessment workflow."""
        # Prepare comprehensive context
        context = {
            **sample_user_data,
            "biometric_data": sample_biometric_data,
            "program_type": "PRIME",
            "session_id": "integration_test_001",
        }

        message = "I want a complete injury risk assessment based on my current data"

        # Mock skills manager for injury prevention
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "injury_prevention",
                "assessment": {
                    "risk_score": 0.25,
                    "risk_level": "low",
                    "primary_risk_factors": ["training_load_increase"],
                    "prevention_recommendations": [
                        "Maintain current training progression",
                        "Monitor sleep consistency",
                        "Continue mobility routine",
                    ],
                },
                "risk_level": "low",
                "recommendations": [
                    "Maintain current training progression",
                    "Monitor sleep consistency",
                ],
                "generated_at": datetime.now().isoformat(),
            }
        )

        # Execute workflow
        result = await wave_agent._run_async_impl(message, context)

        # Verify complete workflow
        assert result["success"] is True
        assert result["agent"] == "wave_performance_analytics"
        assert result["agent_type"] == "recovery_analytics_fusion"

        # Verify fusion capabilities metadata
        assert "fusion_capabilities" in result
        fusion_caps = result["fusion_capabilities"]
        assert fusion_caps["recovery_enabled"] is True
        assert fusion_caps["analytics_enabled"] is True

        # Verify personality adaptation for PRIME program
        assert "personality_fusion" in result
        personality = result["personality_fusion"]
        assert personality["program_adaptation"] == "PRIME"
        assert "ISFP_holistic_wisdom" in personality["primary"]
        assert "INTP_analytical_precision" in personality["secondary"]

        # Verify usage statistics
        assert "usage_stats" in result
        stats = result["usage_stats"]
        assert stats["total_requests"] == 1
        assert "response_time_ms" in stats
        assert "fusion_skills_available" in stats

    @pytest.mark.asyncio
    async def test_rehabilitation_planning_workflow(self, wave_agent, sample_user_data):
        """Test complete rehabilitation planning workflow."""
        context = {
            **sample_user_data,
            "injury_details": {
                "type": "lower_back",
                "severity": "mild",
                "date_of_injury": "2024-05-15",
                "current_pain_level": 3,
            },
            "program_type": "LONGEVITY",
            "session_id": "integration_test_002",
        }

        message = "Create a comprehensive rehabilitation plan for my lower back issue"

        # Mock skills manager for rehabilitation
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "rehabilitation",
                "plan": {
                    "injury_type": "lower_back",
                    "severity": "mild",
                    "plan_id": "rehab_lower_back_20240607_120000",
                    "phases": [
                        {
                            "phase": 1,
                            "name": "Acute/Pain Management",
                            "duration_weeks": 1,
                            "goals": ["reduce_pain", "reduce_inflammation"],
                        },
                        {
                            "phase": 2,
                            "name": "Early Mobilization",
                            "duration_weeks": 2,
                            "goals": [
                                "restore_range_of_motion",
                                "gentle_strengthening",
                            ],
                        },
                    ],
                    "exercises": [
                        {"name": "Pelvic Tilts", "sets": 2, "reps": 10, "phase": 1},
                        {"name": "Cat-Cow Stretch", "sets": 2, "reps": 10, "phase": 1},
                    ],
                    "duration_weeks": 6,
                    "session_frequency": "3x/week",
                },
                "timeline": "6 weeks",
                "next_review": (datetime.now() + timedelta(days=14)).isoformat(),
            }
        )

        result = await wave_agent._run_async_impl(message, context)

        # Verify rehabilitation workflow
        assert result["success"] is True

        # Verify personality adaptation for LONGEVITY program
        personality = result["personality_fusion"]
        assert personality["program_adaptation"] == "LONGEVITY"

        # Verify skills manager was called with correct parameters
        wave_agent.skills_manager.process_message.assert_called_once_with(
            message, context
        )

    @pytest.mark.asyncio
    async def test_sleep_optimization_workflow(self, wave_agent, sample_user_data):
        """Test complete sleep optimization workflow."""
        context = {
            **sample_user_data,
            "sleep_data": {
                "avg_total_sleep": 7.2,
                "avg_deep_sleep": 1.1,
                "avg_rem_sleep": 1.6,
                "sleep_efficiency": 82.5,
                "recent_trends": "declining_quality",
            },
            "recovery_goals": [
                "improve_deep_sleep",
                "increase_efficiency",
                "better_recovery",
            ],
            "program_type": "PRIME",
            "session_id": "integration_test_003",
        }

        message = "Optimize my sleep protocol for better recovery and performance"

        # Mock skills manager for sleep optimization
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "sleep_optimization",
                "protocol": {
                    "current_metrics": {
                        "total_sleep_hours": 7.2,
                        "deep_sleep_percentage": 15.3,
                        "sleep_efficiency": 82.5,
                    },
                    "optimization_opportunities": [
                        "Increase deep sleep percentage",
                        "Improve sleep onset time",
                        "Enhance sleep consistency",
                    ],
                    "recommendations": [
                        "Maintain consistent bedtime (±30 minutes)",
                        "Reduce blue light exposure 2h before bed",
                        "Optimize bedroom temperature (65-68°F)",
                        "Implement evening routine for wind-down",
                    ],
                    "target_metrics": {
                        "total_sleep_hours": 8.0,
                        "deep_sleep_percentage": 20.0,
                        "sleep_efficiency": 90.0,
                    },
                    "monitoring_schedule": "daily_tracking",
                    "review_frequency": "weekly",
                },
                "implementation_timeline": "2-4 weeks",
                "expected_improvements": [
                    "Better recovery scores",
                    "Improved HRV",
                    "Enhanced performance",
                ],
            }
        )

        result = await wave_agent._run_async_impl(message, context)

        # Verify sleep optimization workflow
        assert result["success"] is True
        assert result["agent_type"] == "recovery_analytics_fusion"

        # Verify PRIME program adaptation (executive focus)
        personality = result["personality_fusion"]
        assert personality["program_adaptation"] == "PRIME"


class TestAnalyticsWorkflows:
    """Test complete analytics analysis workflows."""

    @pytest.mark.asyncio
    async def test_biometric_analysis_workflow(
        self, wave_agent, sample_user_data, sample_biometric_data
    ):
        """Test complete biometric analysis workflow."""
        context = {
            **sample_user_data,
            "biometric_data": sample_biometric_data,
            "analysis_request": {
                "focus_areas": [
                    "hrv_trends",
                    "recovery_patterns",
                    "training_readiness",
                ],
                "time_period": "last_30_days",
                "detail_level": "comprehensive",
            },
            "program_type": "PRIME",
            "session_id": "integration_test_004",
        }

        message = "Provide a comprehensive analysis of my biometric data and recovery patterns"

        # Mock skills manager for biometric analysis
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "biometric_analysis",
                "analysis": {
                    "recovery_status": "good",
                    "readiness_score": 82,
                    "key_trends": [
                        "HRV showing consistent improvement (+8% over 30 days)",
                        "RHR trending downward (optimal adaptation)",
                        "Sleep quality stable with room for optimization",
                    ],
                    "performance_indicators": {
                        "training_readiness": "high",
                        "recovery_capacity": "good",
                        "stress_resilience": "improving",
                    },
                    "recommendations": [
                        "Continue current training intensity",
                        "Focus on sleep consistency for next phase",
                        "Monitor stress levels during high-demand periods",
                    ],
                    "data_quality_score": 0.94,
                    "confidence_level": 0.89,
                },
                "recovery_status": "good",
                "readiness_score": 82,
                "recommendations": [
                    "Continue current training intensity",
                    "Focus on sleep consistency",
                ],
                "analyzed_at": datetime.now().isoformat(),
            }
        )

        result = await wave_agent._run_async_impl(message, context)

        # Verify biometric analysis workflow
        assert result["success"] is True
        assert result["agent"] == "wave_performance_analytics"

        # Verify context preservation
        assert result["request_id"] == "integration_test_004"

        # Verify personality adaptation
        personality = result["personality_fusion"]
        assert personality["program_adaptation"] == "PRIME"

    @pytest.mark.asyncio
    async def test_pattern_recognition_workflow(
        self, wave_agent, sample_user_data, sample_analytics_data
    ):
        """Test pattern recognition analysis workflow."""
        context = {
            **sample_user_data,
            "historical_data": sample_analytics_data,
            "analysis_window": "90_days",
            "pattern_types": ["circadian", "training_response", "stress_patterns"],
            "program_type": "LONGEVITY",
            "session_id": "integration_test_005",
        }

        message = "Identify patterns in my health data over the last 90 days"

        # Mock skills manager for pattern recognition
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "pattern_recognition",
                "patterns": {
                    "identified_patterns": [
                        {
                            "type": "circadian_rhythm",
                            "confidence": 0.91,
                            "description": "Highly consistent sleep-wake cycle with 7.5-8h optimal window",
                            "impact": "Positive correlation with next-day performance",
                        },
                        {
                            "type": "weekly_training_response",
                            "confidence": 0.84,
                            "description": "Peak performance on Tuesday-Thursday, recovery needs on weekends",
                            "impact": "Training adaptation pattern suggests optimal periodization",
                        },
                        {
                            "type": "stress_recovery_cycle",
                            "confidence": 0.78,
                            "description": "24-48h stress response pattern with consistent recovery",
                            "impact": "Strong resilience indicators for sustained wellness",
                        },
                    ],
                    "correlations": [
                        {
                            "metrics": ["sleep_quality", "next_day_hrv"],
                            "strength": 0.82,
                            "significance": "high",
                        }
                    ],
                    "recommendations": [
                        "Maintain current sleep consistency",
                        "Optimize training intensity on identified peak days",
                        "Use stress patterns to guide recovery protocols",
                    ],
                },
                "confidence_overall": 0.85,
                "data_quality": "excellent",
            }
        )

        result = await wave_agent._run_async_impl(message, context)

        # Verify pattern recognition workflow
        assert result["success"] is True

        # Verify LONGEVITY program adaptation
        personality = result["personality_fusion"]
        assert personality["program_adaptation"] == "LONGEVITY"


class TestFusionWorkflows:
    """Test complete fusion analysis workflows."""

    @pytest.mark.asyncio
    async def test_recovery_analytics_fusion_workflow(
        self, wave_agent, sample_user_data, sample_recovery_data, sample_analytics_data
    ):
        """Test complete recovery-analytics fusion workflow."""
        context = {
            **sample_user_data,
            "recovery_data": sample_recovery_data,
            "analytics_data": sample_analytics_data,
            "fusion_request": {
                "analysis_type": "comprehensive",
                "focus": "performance_optimization",
                "time_horizon": "next_4_weeks",
            },
            "program_type": "PRIME",
            "session_id": "integration_test_006",
        }

        message = "Give me a fusion analysis combining my recovery status with biometric analytics for optimal performance"

        # Mock skills manager for fusion analysis
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "recovery_analytics_fusion",
                "fusion_analysis": {
                    "holistic_insights": [
                        "Body is responding positively to current recovery protocols",
                        "Energy patterns align with natural circadian rhythms",
                        "Stress resilience is building steadily",
                    ],
                    "analytical_insights": [
                        "HRV trending upward +12% indicating improved autonomic function",
                        "Training load progression optimal at current 1.15 acute:chronic ratio",
                        "Sleep efficiency at 89% supports recovery demands",
                    ],
                    "integrated_recommendations": [
                        "Continue current recovery protocols with 15% intensity increase in 2 weeks",
                        "Leverage identified performance windows (Tue-Thu) for key sessions",
                        "Implement targeted sleep optimization for final performance gains",
                    ],
                    "fusion_confidence": 0.89,
                    "optimization_opportunities": [
                        {
                            "area": "sleep_optimization",
                            "potential_gain": "8-12% performance improvement",
                            "timeline": "2-3 weeks",
                        },
                        {
                            "area": "training_periodization",
                            "potential_gain": "5-8% efficiency gain",
                            "timeline": "4-6 weeks",
                        },
                    ],
                },
                "fusion_confidence": 0.89,
                "holistic_insights": [
                    "Body responding positively to protocols",
                    "Energy patterns optimized",
                ],
                "analytical_insights": [
                    "HRV trending upward +12%",
                    "Training load progression optimal",
                ],
                "integrated_recommendations": [
                    "Continue protocols with intensity increase",
                    "Leverage performance windows",
                ],
                "generated_at": datetime.now().isoformat(),
            }
        )

        result = await wave_agent._run_async_impl(message, context)

        # Verify fusion workflow
        assert result["success"] is True
        assert result["agent_type"] == "recovery_analytics_fusion"

        # Verify fusion capabilities are enabled
        fusion_caps = result["fusion_capabilities"]
        assert fusion_caps["fusion_ready"] is True
        assert fusion_caps["recovery_enabled"] is True
        assert fusion_caps["analytics_enabled"] is True

        # Verify PRIME program optimization focus
        personality = result["personality_fusion"]
        assert personality["program_adaptation"] == "PRIME"
        assert "ISFP_holistic_wisdom" in personality["primary"]
        assert "INTP_analytical_precision" in personality["secondary"]

    @pytest.mark.asyncio
    async def test_injury_prediction_analytics_workflow(
        self, wave_agent, sample_user_data
    ):
        """Test injury prediction analytics workflow."""
        context = {
            **sample_user_data,
            "historical_biometrics": {
                "hrv_trend": "declining_last_week",
                "training_load": "increasing_rapidly",
                "sleep_quality": "variable",
                "stress_markers": "elevated",
            },
            "risk_assessment_request": {
                "prediction_horizon": "14_days",
                "risk_categories": ["overuse", "acute", "metabolic"],
                "confidence_threshold": 0.75,
            },
            "program_type": "PRIME",
            "session_id": "integration_test_007",
        }

        message = "Predict my injury risk for the next 2 weeks based on current trends"

        # Mock skills manager for injury prediction
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "injury_prediction_analytics",
                "prediction": {
                    "risk_probabilities": {
                        "lower_back": 0.28,
                        "knee": 0.15,
                        "shoulder": 0.12,
                        "overall_risk": 0.32,
                    },
                    "risk_factors_identified": [
                        "Training load increase >20% in last 2 weeks",
                        "HRV declining 8% indicating recovery stress",
                        "Sleep quality variability affecting adaptation",
                    ],
                    "prevention_protocol": [
                        "Reduce training volume by 15% for next week",
                        "Implement daily mobility routine focusing on lower back",
                        "Prioritize sleep consistency (8h ±30min)",
                        "Monitor daily HRV for recovery guidance",
                    ],
                    "monitoring_parameters": [
                        "Daily pain levels (0-10 scale)",
                        "Morning movement quality assessment",
                        "Training session RPE tracking",
                        "Sleep quality and duration",
                    ],
                    "reassessment_timeline": "7 days",
                    "confidence_level": 0.79,
                },
                "prediction_horizon_days": 14,
                "risk_probabilities": {
                    "lower_back": 0.28,
                    "knee": 0.15,
                    "overall": 0.32,
                },
                "prevention_protocol": [
                    "Reduce training volume by 15%",
                    "Daily mobility routine",
                ],
                "monitoring_parameters": ["Daily pain levels", "Movement quality"],
                "generated_at": datetime.now().isoformat(),
            }
        )

        result = await wave_agent._run_async_impl(message, context)

        # Verify injury prediction workflow
        assert result["success"] is True
        assert result["agent"] == "wave_performance_analytics"

        # Verify prediction-specific metadata
        assert result["request_id"] == "integration_test_007"

        # Verify fusion capabilities
        fusion_caps = result["fusion_capabilities"]
        assert fusion_caps["fusion_ready"] is True

    @pytest.mark.asyncio
    async def test_holistic_wellness_dashboard_workflow(
        self, wave_agent, sample_user_data, sample_biometric_data
    ):
        """Test holistic wellness dashboard creation workflow."""
        context = {
            **sample_user_data,
            "dashboard_request": {
                "timeframe": "last_30_days",
                "metrics": ["recovery", "performance", "wellness", "predictions"],
                "format": "comprehensive_summary",
                "update_frequency": "weekly",
            },
            "current_biometrics": sample_biometric_data,
            "program_type": "LONGEVITY",
            "session_id": "integration_test_008",
        }

        message = "Create a holistic wellness dashboard with my recovery and performance insights"

        # Mock skills manager for holistic dashboard
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "holistic_wellness_dashboard",
                "dashboard": {
                    "wellness_score": 82,
                    "key_metrics": {
                        "recovery_status": "good",
                        "training_readiness": "high",
                        "stress_resilience": "improving",
                        "sleep_quality": "good",
                    },
                    "trend_analysis": {
                        "30_day_trends": {
                            "recovery": "improving",
                            "performance": "stable_high",
                            "wellness": "positive_trajectory",
                        },
                        "week_over_week": {
                            "recovery_score": "+5%",
                            "hrv": "+3%",
                            "sleep_quality": "stable",
                        },
                    },
                    "insights": [
                        "Consistent improvement in recovery metrics",
                        "Training adaptation proceeding optimally",
                        "Stress management strategies working effectively",
                    ],
                    "recommendations": [
                        "Maintain current wellness protocols",
                        "Consider gradual progression in challenging areas",
                        "Continue focus on sleep consistency",
                    ],
                    "next_focus_areas": [
                        "Fine-tune nutrition timing",
                        "Optimize recovery modalities",
                        "Enhance stress resilience practices",
                    ],
                },
                "wellness_score": 82,
                "key_insights": [
                    "Recovery metrics improving consistently",
                    "Training adaptation optimal",
                ],
                "recommendations": [
                    "Maintain current protocols",
                    "Consider gradual progression",
                ],
            }
        )

        result = await wave_agent._run_async_impl(message, context)

        # Verify holistic dashboard workflow
        assert result["success"] is True

        # Verify LONGEVITY program adaptation (wellness-focused)
        personality = result["personality_fusion"]
        assert personality["program_adaptation"] == "LONGEVITY"


class TestErrorHandlingWorkflows:
    """Test error handling in complete workflows."""

    @pytest.mark.asyncio
    async def test_workflow_with_recovery_service_error(
        self, wave_agent, sample_context
    ):
        """Test workflow handling when recovery service fails."""
        message = "Assess my injury risk"

        # Mock skills manager to raise RecoveryError
        wave_agent.skills_manager.process_message = AsyncMock(
            side_effect=RecoveryError(
                "Recovery service unavailable", {"service": "injury_assessment"}
            )
        )

        result = await wave_agent._run_async_impl(message, sample_context)

        # Verify error handling
        assert result["success"] is False
        assert result["error"] == "Recovery service unavailable"
        assert result["error_type"] == "RecoveryError"
        assert result["error_details"]["service"] == "injury_assessment"
        assert result["agent"] == "wave_performance_analytics"

    @pytest.mark.asyncio
    async def test_workflow_with_analytics_error(self, wave_agent, sample_context):
        """Test workflow handling when analytics processing fails."""
        message = "Analyze my biometric patterns"

        # Mock skills manager to raise AnalyticsError
        wave_agent.skills_manager.process_message = AsyncMock(
            side_effect=AnalyticsError(
                "Pattern recognition failed", {"component": "trend_analysis"}
            )
        )

        result = await wave_agent._run_async_impl(message, sample_context)

        # Verify error handling
        assert result["success"] is False
        assert result["error"] == "Pattern recognition failed"
        assert result["error_type"] == "AnalyticsError"
        assert result["error_details"]["component"] == "trend_analysis"

    @pytest.mark.asyncio
    async def test_workflow_with_fusion_error(self, wave_agent, sample_context):
        """Test workflow handling when fusion analysis fails."""
        message = "Give me integrated recovery and analytics insights"

        # Mock skills manager to raise FusionError
        wave_agent.skills_manager.process_message = AsyncMock(
            side_effect=FusionError(
                "Fusion processing failed", {"fusion_type": "recovery_analytics"}
            )
        )

        result = await wave_agent._run_async_impl(message, sample_context)

        # Verify error handling
        assert result["success"] is False
        assert result["error"] == "Fusion processing failed"
        assert result["error_type"] == "FusionError"
        assert result["error_details"]["fusion_type"] == "recovery_analytics"


class TestConcurrentWorkflows:
    """Test concurrent workflow execution."""

    @pytest.mark.asyncio
    async def test_concurrent_analysis_requests(self, wave_agent, sample_user_data):
        """Test handling multiple concurrent analysis requests."""
        contexts = [
            {
                **sample_user_data,
                "session_id": f"concurrent_test_{i}",
                "program_type": "PRIME",
            }
            for i in range(3)
        ]

        messages = [
            "Assess my injury risk",
            "Analyze my biometric data",
            "Create recovery recommendations",
        ]

        # Mock skills manager responses
        responses = [
            {"success": True, "skill": "injury_prevention", "assessment": "low_risk"},
            {"success": True, "skill": "biometric_analysis", "analysis": "good_status"},
            {
                "success": True,
                "skill": "general_recovery",
                "recommendations": ["rest", "hydrate"],
            },
        ]

        wave_agent.skills_manager.process_message = AsyncMock(side_effect=responses)

        # Execute concurrent requests
        tasks = [
            wave_agent._run_async_impl(message, context)
            for message, context in zip(messages, contexts)
        ]

        results = await asyncio.gather(*tasks)

        # Verify all requests completed successfully
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["success"] is True
            assert result["request_id"] == f"concurrent_test_{i}"

        # Verify request count tracking
        assert wave_agent.request_count == 3


class TestWorkflowPerformance:
    """Test workflow performance characteristics."""

    @pytest.mark.asyncio
    async def test_workflow_response_times(
        self, wave_agent, sample_context, performance_benchmarks
    ):
        """Test workflow response times meet benchmarks."""
        message = "Quick health check"

        # Mock fast skills manager response
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "general_recovery",
                "status": "healthy",
            }
        )

        start_time = datetime.now()
        result = await wave_agent._run_async_impl(message, sample_context)
        end_time = datetime.now()

        response_time = (end_time - start_time).total_seconds()

        # Verify response time meets benchmark
        assert response_time < performance_benchmarks["response_times"]["simple_query"]
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_complex_workflow_performance(
        self,
        wave_agent,
        sample_user_data,
        sample_biometric_data,
        performance_benchmarks,
    ):
        """Test complex fusion workflow performance."""
        context = {
            **sample_user_data,
            "biometric_data": sample_biometric_data,
            "program_type": "PRIME",
            "session_id": "performance_test",
        }

        message = (
            "Provide comprehensive fusion analysis with predictions and recommendations"
        )

        # Mock complex analysis response
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "recovery_analytics_fusion",
                "fusion_analysis": {"comprehensive": "analysis"},
                "predictions": {"injury_risk": 0.15},
                "recommendations": ["optimize", "monitor", "adjust"],
            }
        )

        start_time = datetime.now()
        result = await wave_agent._run_async_impl(message, context)
        end_time = datetime.now()

        response_time = (end_time - start_time).total_seconds()

        # Verify response time meets complex analysis benchmark
        assert (
            response_time < performance_benchmarks["response_times"]["fusion_analysis"]
        )
        assert result["success"] is True
        assert "fusion_analysis" in result or "fusion_capabilities" in result


class TestWorkflowSecurity:
    """Test security aspects of workflows."""

    @pytest.mark.asyncio
    async def test_health_data_consent_workflow(self, wave_agent, security_test_data):
        """Test health data consent checking in workflows."""
        context = {
            "user_id": "test_user",
            "program_type": "PRIME",
            "biometric_data": security_test_data["health_data"]["biometric_data"],
            "session_id": "security_test_001",
        }

        message = "Analyze my health data"

        # Mock skills manager response
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "biometric_analysis",
                "analysis": "health_data_processed",
            }
        )

        # Execute workflow with health data
        result = await wave_agent._run_async_impl(message, context)

        # Verify workflow completed (consent check is currently informational)
        assert result["success"] is True

        # Verify no sensitive data leaked in response
        result_str = json.dumps(result)
        assert security_test_data["pii_data"]["email"] not in result_str
        assert security_test_data["pii_data"]["phone"] not in result_str

    @pytest.mark.asyncio
    async def test_sensitive_query_handling(self, wave_agent, security_test_data):
        """Test handling of sensitive health queries."""
        for sensitive_query in security_test_data["sensitive_queries"]:
            context = {
                "user_id": "test_user",
                "program_type": "LONGEVITY",
                "session_id": f"sensitive_test_{hash(sensitive_query)}",
            }

            # Mock skills manager response for sensitive query
            wave_agent.skills_manager.process_message = AsyncMock(
                return_value={
                    "success": True,
                    "skill": "general_recovery",
                    "guidance": "consult_healthcare_provider",
                    "disclaimer": "not_medical_advice",
                }
            )

            result = await wave_agent._run_async_impl(sensitive_query, context)

            # Verify appropriate handling
            assert result["success"] is True
            # In production, would verify appropriate disclaimers and referrals


class TestWorkflowIntegrations:
    """Test workflow integrations with external services."""

    @pytest.mark.asyncio
    async def test_device_data_integration_workflow(
        self, wave_agent, integration_test_data
    ):
        """Test workflow with device data integration."""
        device_integration = integration_test_data["device_integrations"][0]  # WHOOP

        context = {
            "user_id": "test_user",
            "program_type": "PRIME",
            "device_data": {
                "source": device_integration["device_type"],
                "data_types": device_integration["data_types"],
                "last_sync": datetime.now().isoformat(),
                "data": {
                    "hrv": 45.2,
                    "recovery": 78,
                    "strain": 12.5,
                    "sleep": {"duration": 7.8, "efficiency": 89},
                },
            },
            "session_id": "device_integration_test",
        }

        message = "Analyze my latest device data for recovery insights"

        # Mock skills manager with device data processing
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "biometric_analysis",
                "analysis": {
                    "device_source": "whoop",
                    "data_quality": "excellent",
                    "recovery_insights": "optimal_status",
                },
                "device_integration_status": "successful",
            }
        )

        result = await wave_agent._run_async_impl(message, context)

        # Verify device integration workflow
        assert result["success"] is True
        assert result["agent"] == "wave_performance_analytics"

    @pytest.mark.asyncio
    async def test_ai_service_integration_workflow(self, wave_agent, sample_context):
        """Test workflow with AI service integration."""
        message = "Provide AI-enhanced recovery analysis"

        # Verify Gemini client integration in skills manager
        assert wave_agent.skills_manager.vertex_ai_client is not None

        # Mock successful AI service call
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "recovery_analytics_fusion",
                "ai_enhanced": True,
                "analysis": "comprehensive_ai_insights",
                "confidence": 0.91,
            }
        )

        result = await wave_agent._run_async_impl(message, sample_context)

        # Verify AI service integration
        assert result["success"] is True
        # In production, would verify AI service usage metrics
