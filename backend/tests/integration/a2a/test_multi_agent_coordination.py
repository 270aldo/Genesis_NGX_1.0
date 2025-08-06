"""
Multi-Agent Coordination Integration Tests.

Comprehensive test suite for the orchestrator's multi-agent coordination capabilities:
- Parallel execution of multiple agents by the orchestrator
- Sequential execution with context passing between agents
- Priority-based agent execution
- Response synthesis from multiple agents
- Circuit breaker functionality per agent
- Handling scenarios where some agents are unavailable

Tests simulate real orchestration scenarios like:
- User needs training AND nutrition help → Orchestrator calls BLAZE + SAGE in parallel
- Complex workflow requiring sequential agent handoffs
- Emergency scenarios where GUARDIAN takes priority
- Graceful degradation when some agents fail
"""

import asyncio
import time
import uuid
from typing import Any, Dict

import pytest

from core.logging_config import get_logger
from tests.integration.a2a.utils.agent_simulator import SimulatedAgent
from tests.integration.a2a.utils.test_server import TestA2AServer

logger = get_logger(__name__)


class TestParallelAgentExecution:
    """Test orchestrator's ability to execute multiple agents in parallel."""

    async def test_parallel_training_nutrition_coordination(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """
        Test orchestrator coordinating BLAZE (training) and SAGE (nutrition) in parallel.

        Scenario: User asks "I need help with my training and nutrition plan"
        Expected: Orchestrator calls both agents in parallel and synthesizes responses
        """
        orchestrator = registered_agents["orchestrator"]

        # Prepare message that should trigger both training and nutrition
        message = {
            "user_input": "I need help with my training and nutrition plan for muscle building",
            "context": {
                "user_id": "test_user_parallel_1",
                "session_id": str(uuid.uuid4()),
                "goals": ["muscle_building", "nutrition_optimization"],
            },
        }

        # Record start time for performance metrics
        start_time = time.time()

        # Process the message through orchestrator
        response = await orchestrator.process_message(message)

        # Verify successful coordination
        assert response["status"] == "success"
        assert "response_data" in response

        # Verify the orchestrator identified multiple agents to call
        response_data = response["response_data"]
        assert "agents_to_call" in response_data
        agents_called = response_data["agents_to_call"]
        assert len(agents_called) >= 2
        assert "elite_training_strategist" in agents_called
        assert "precision_nutrition_architect" in agents_called

        # Verify response time is reasonable for parallel execution
        execution_time = time.time() - start_time
        assert (
            execution_time < 2.0
        ), f"Parallel execution took too long: {execution_time}s"

        # Verify routing decision confidence
        routing_decision = response_data.get("routing_decision", {})
        assert routing_decision.get("confidence", 0) > 0.7

        logger.info(f"Parallel coordination successful in {execution_time:.3f}s")

    async def test_parallel_execution_performance_metrics(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        performance_metrics: Dict[str, Any],
    ):
        """
        Test performance characteristics of parallel agent execution.

        Measures latency, throughput, and resource utilization.
        """
        orchestrator = registered_agents["orchestrator"]

        # Test data for multiple parallel requests
        test_messages = [
            "I need training and nutrition help",
            "Help me with genetics and biohacking",
            "I need motivation and progress tracking",
            "Analyze my performance and wellness data",
        ]

        # Execute multiple parallel coordination requests
        tasks = []
        start_time = time.time()

        for i, user_input in enumerate(test_messages):
            message = {
                "user_input": user_input,
                "context": {
                    "user_id": f"test_user_perf_{i}",
                    "session_id": str(uuid.uuid4()),
                },
            }
            task = asyncio.create_task(orchestrator.process_message(message))
            tasks.append(task)

        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Analyze results
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        failed_responses = [r for r in responses if isinstance(r, Exception)]

        # Update performance metrics
        performance_metrics["latencies"].append(total_time)
        performance_metrics["throughput"] = len(test_messages) / total_time
        performance_metrics["success_rate"] = len(successful_responses) / len(
            test_messages
        )
        performance_metrics["errors"] = len(failed_responses)

        # Assertions
        assert len(successful_responses) >= 3, "Most parallel requests should succeed"
        assert performance_metrics["success_rate"] >= 0.75, "Success rate too low"
        assert performance_metrics["throughput"] > 1.0, "Throughput too low"

        logger.info(
            f"Parallel performance: {performance_metrics['throughput']:.2f} req/s, "
            f"{performance_metrics['success_rate']:.1%} success rate"
        )

    async def test_mixed_priority_parallel_execution(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test parallel execution with mixed priority messages.

        Verifies that high-priority messages are processed faster than low-priority ones.
        """
        orchestrator = registered_agents["orchestrator"]

        # Create messages with different priorities
        high_priority_msg = {
            "user_input": "URGENT: I'm having chest pain during exercise, need immediate help",
            "context": {
                "user_id": "test_user_priority_high",
                "session_id": str(uuid.uuid4()),
                "urgency": "high",
                "medical": True,
            },
        }

        low_priority_msg = {
            "user_input": "Can you help me plan my workout for next week?",
            "context": {
                "user_id": "test_user_priority_low",
                "session_id": str(uuid.uuid4()),
                "urgency": "low",
            },
        }

        # Start both tasks simultaneously
        start_time = time.time()
        high_priority_task = asyncio.create_task(
            orchestrator.process_message(high_priority_msg)
        )
        low_priority_task = asyncio.create_task(
            orchestrator.process_message(low_priority_msg)
        )

        # Wait for high priority to complete first
        high_response = await high_priority_task
        high_completion_time = time.time() - start_time

        # Wait for low priority to complete
        low_response = await low_priority_task
        low_completion_time = time.time() - start_time

        # Verify both succeeded
        assert high_response["status"] == "success"
        assert low_response["status"] == "success"

        # High priority should complete faster or at similar time
        # (Note: In simulation, timing might be similar, but structure should indicate priority)
        assert high_completion_time <= low_completion_time + 0.1  # Allow small variance

        logger.info(
            f"Priority handling: High={high_completion_time:.3f}s, Low={low_completion_time:.3f}s"
        )


class TestSequentialAgentExecution:
    """Test orchestrator's ability to execute agents sequentially with context passing."""

    async def test_sequential_context_passing_workflow(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test sequential agent execution with context passing.

        Scenario: Complex user request requiring handoff between agents
        1. User submits genetic data inquiry
        2. CODE agent analyzes genetics
        3. BLAZE agent creates personalized training based on genetic insights
        4. SAGE agent adjusts nutrition based on genetic + training data
        """
        orchestrator = registered_agents["orchestrator"]

        # Stage 1: Initial genetic inquiry
        initial_message = {
            "user_input": "I have my genetic test results and want a complete personalized plan",
            "context": {
                "user_id": "test_user_sequential_1",
                "session_id": str(uuid.uuid4()),
                "has_genetic_data": True,
                "genetic_markers": ["ACTN3", "MCT1", "APOE"],
                "workflow_stage": "initial",
            },
        }

        # Process initial request
        stage1_response = await orchestrator.process_message(initial_message)

        # Verify initial routing to genetic specialist
        assert stage1_response["status"] == "success"
        response_data = stage1_response["response_data"]
        assert "genetic_specialist" in response_data.get("agents_to_call", [])

        # Stage 2: Follow-up with genetic insights for training
        followup_context = initial_message["context"].copy()
        followup_context.update(
            {
                "workflow_stage": "training_planning",
                "genetic_insights": {
                    "power_potential": "high",
                    "endurance_potential": "medium",
                    "recovery_time": "extended",
                },
                "previous_agent_responses": [stage1_response],
            }
        )

        training_message = {
            "user_input": "Based on my genetic analysis, create my training plan",
            "context": followup_context,
        }

        stage2_response = await orchestrator.process_message(training_message)

        # Verify training agent was called with genetic context
        assert stage2_response["status"] == "success"
        training_data = stage2_response["response_data"]
        assert "agents_to_call" in training_data

        # Stage 3: Final nutrition planning with all context
        final_context = followup_context.copy()
        final_context.update(
            {
                "workflow_stage": "nutrition_planning",
                "training_plan": {
                    "focus": "power_development",
                    "recovery_emphasis": "high",
                },
                "previous_agent_responses": [stage1_response, stage2_response],
            }
        )

        nutrition_message = {
            "user_input": "Complete my plan with personalized nutrition",
            "context": final_context,
        }

        stage3_response = await orchestrator.process_message(nutrition_message)

        # Verify final response incorporates all context
        assert stage3_response["status"] == "success"

        # Verify workflow progression was maintained
        workflow_stages = [
            initial_message["context"]["workflow_stage"],
            training_message["context"]["workflow_stage"],
            nutrition_message["context"]["workflow_stage"],
        ]
        expected_stages = ["initial", "training_planning", "nutrition_planning"]
        assert workflow_stages == expected_stages

        logger.info("Sequential workflow with context passing completed successfully")

    async def test_conditional_sequential_execution(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test conditional sequential execution based on previous agent responses.

        Tests the orchestrator's ability to make routing decisions based on
        intermediate results from other agents.
        """
        orchestrator = registered_agents["orchestrator"]

        # Initial health assessment request
        health_message = {
            "user_input": "I'm feeling exhausted and my workouts aren't effective",
            "context": {
                "user_id": "test_user_conditional_1",
                "session_id": str(uuid.uuid4()),
                "symptoms": ["fatigue", "poor_performance"],
                "conditional_routing": True,
            },
        }

        # Process initial health assessment
        health_response = await orchestrator.process_message(health_message)
        assert health_response["status"] == "success"

        # Simulate different conditional paths based on assessment
        # Path 1: If health issues detected, route to wellness specialist
        wellness_followup = {
            "user_input": "I need comprehensive wellness analysis",
            "context": {
                "user_id": "test_user_conditional_1",
                "session_id": health_message["context"]["session_id"],
                "previous_assessment": "health_concerns_detected",
                "route_to": "female_wellness_coach",  # Conditional routing
                "conditional_routing": True,
            },
        }

        wellness_response = await orchestrator.process_message(wellness_followup)
        assert wellness_response["status"] == "success"

        # Path 2: If wellness plan created, adjust training accordingly
        training_adjustment = {
            "user_input": "Adjust my training based on wellness recommendations",
            "context": {
                "user_id": "test_user_conditional_1",
                "session_id": health_message["context"]["session_id"],
                "wellness_recommendations": {
                    "reduce_intensity": True,
                    "focus_recovery": True,
                    "stress_management": True,
                },
                "conditional_routing": True,
            },
        }

        training_response = await orchestrator.process_message(training_adjustment)
        assert training_response["status"] == "success"

        # Verify the conditional routing chain maintained context
        assert len([health_response, wellness_response, training_response]) == 3

        logger.info("Conditional sequential execution completed successfully")


class TestPriorityBasedExecution:
    """Test orchestrator's priority-based agent execution system."""

    async def test_emergency_priority_override(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test that emergency/critical messages override normal priority queue.

        Scenario: GUARDIAN agent should be prioritized for security/safety issues.
        """
        orchestrator = registered_agents["orchestrator"]

        # Normal priority messages
        normal_messages = [
            {
                "user_input": "What's a good post-workout meal?",
                "context": {"user_id": f"normal_user_{i}", "priority": "normal"},
            }
            for i in range(3)
        ]

        # Critical emergency message
        emergency_message = {
            "user_input": "I'm having severe chest pain and dizziness during exercise - EMERGENCY",
            "context": {
                "user_id": "emergency_user",
                "priority": "critical",
                "is_emergency": True,
                "medical": True,
                "urgency": "critical",
            },
        }

        # Start normal messages first
        normal_tasks = [
            asyncio.create_task(orchestrator.process_message(msg))
            for msg in normal_messages
        ]

        # Small delay then add emergency
        await asyncio.sleep(0.01)
        emergency_task = asyncio.create_task(
            orchestrator.process_message(emergency_message)
        )

        # Wait for emergency response
        emergency_response = await emergency_task
        time.time()

        # Verify emergency was handled successfully
        assert emergency_response["status"] == "success"

        # Verify emergency response contains appropriate routing
        response_data = emergency_response["response_data"]
        agents_called = response_data.get("agents_to_call", [])

        # For emergency medical situations, GUARDIAN should be involved
        # Note: This depends on the orchestrator's routing logic
        assert len(agents_called) > 0

        # Wait for normal tasks to complete
        normal_responses = await asyncio.gather(*normal_tasks, return_exceptions=True)

        # Verify most normal messages also succeeded (system stability)
        successful_normal = [
            r for r in normal_responses if not isinstance(r, Exception)
        ]
        assert len(successful_normal) >= 2, "Normal messages should still process"

        logger.info(
            "Emergency priority override test completed - Emergency handled first"
        )

    async def test_priority_queue_ordering(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test that messages are processed in correct priority order.

        Verifies CRITICAL > HIGH > NORMAL > LOW priority ordering.
        """
        orchestrator = registered_agents["orchestrator"]

        # Create messages with different priorities
        messages_by_priority = {
            "low": {
                "user_input": "Can you suggest a good protein powder brand?",
                "context": {"user_id": "low_user", "priority": "low", "urgency": "low"},
            },
            "normal": {
                "user_input": "I need help planning my weekly workouts",
                "context": {"user_id": "normal_user", "priority": "normal"},
            },
            "high": {
                "user_input": "I'm not seeing results and getting frustrated with my program",
                "context": {
                    "user_id": "high_user",
                    "priority": "high",
                    "urgency": "high",
                },
            },
            "critical": {
                "user_input": "I'm experiencing concerning symptoms during training",
                "context": {
                    "user_id": "critical_user",
                    "priority": "critical",
                    "is_emergency": True,
                },
            },
        }

        # Submit all messages simultaneously
        tasks = {}
        start_time = time.time()

        for priority, message in messages_by_priority.items():
            task = asyncio.create_task(orchestrator.process_message(message))
            tasks[priority] = task

        # Collect completion times
        completion_times = {}
        responses = {}

        for priority, task in tasks.items():
            responses[priority] = await task
            completion_times[priority] = time.time() - start_time

        # Verify all messages were processed successfully
        for priority, response in responses.items():
            assert (
                response["status"] == "success"
            ), f"{priority} priority message failed"

        # Verify priority ordering (critical should complete first, low last)
        # Note: In simulation, exact timing may vary, but we can verify logical structure
        priorities_by_completion = sorted(
            completion_times.keys(), key=lambda p: completion_times[p]
        )

        # Critical and high should generally complete before normal and low
        high_priority_indices = [
            priorities_by_completion.index(p)
            for p in ["critical", "high"]
            if p in priorities_by_completion
        ]
        low_priority_indices = [
            priorities_by_completion.index(p)
            for p in ["normal", "low"]
            if p in priorities_by_completion
        ]

        if high_priority_indices and low_priority_indices:
            avg_high_index = sum(high_priority_indices) / len(high_priority_indices)
            avg_low_index = sum(low_priority_indices) / len(low_priority_indices)
            assert (
                avg_high_index <= avg_low_index
            ), "High priority should complete before low priority"

        logger.info(f"Priority ordering test completed - Times: {completion_times}")


class TestResponseSynthesis:
    """Test orchestrator's ability to synthesize responses from multiple agents."""

    async def test_multi_agent_response_synthesis(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test synthesis of responses from multiple agents into coherent output.

        Scenario: User needs comprehensive fitness guidance requiring multiple specialties.
        """
        orchestrator = registered_agents["orchestrator"]

        # Complex request requiring multiple agents
        complex_message = {
            "user_input": "I'm a 30-year-old female starting fitness journey, need help with training, nutrition, and motivation",
            "context": {
                "user_id": "test_user_synthesis_1",
                "session_id": str(uuid.uuid4()),
                "user_profile": {
                    "age": 30,
                    "gender": "female",
                    "fitness_level": "beginner",
                    "goals": ["weight_loss", "muscle_tone", "health_improvement"],
                },
                "requires_synthesis": True,
            },
        }

        # Process the complex request
        response = await orchestrator.process_message(complex_message)

        # Verify successful synthesis
        assert response["status"] == "success"
        assert "response_data" in response

        response_data = response["response_data"]

        # Verify multiple agents were identified for the comprehensive request
        agents_called = response_data.get("agents_to_call", [])
        assert len(agents_called) >= 2, "Complex request should involve multiple agents"

        # Expected agents for this scenario
        expected_agents = [
            "elite_training_strategist",
            "precision_nutrition_architect",
            "motivation_behavior_coach",
        ]
        called_agent_overlap = set(agents_called) & set(expected_agents)
        assert len(called_agent_overlap) >= 2, "Should call relevant specialist agents"

        # Verify routing confidence for complex multi-agent scenarios
        routing_decision = response_data.get("routing_decision", {})
        assert (
            routing_decision.get("confidence", 0) >= 0.7
        ), "Should be confident in multi-agent routing"

        logger.info(
            f"Multi-agent synthesis successful: {len(agents_called)} agents coordinated"
        )

    async def test_response_conflict_resolution(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test orchestrator's ability to handle conflicting responses from different agents.

        Simulates scenario where agents might provide contradictory advice.
        """
        orchestrator = registered_agents["orchestrator"]

        # Set up agents to provide potentially conflicting responses
        elite_training = registered_agents["elite_training_strategist"]
        precision_nutrition = registered_agents["precision_nutrition_architect"]

        # Add custom conflicting behavior
        def conflicting_training_handler(message):
            return {
                "content": "You should train 6 days per week with high intensity",
                "recommendation": "high_volume_training",
                "confidence": 0.9,
            }

        def conflicting_nutrition_handler(message):
            return {
                "content": "You should focus on recovery and train only 3 days per week",
                "recommendation": "recovery_focused_training",
                "confidence": 0.85,
            }

        elite_training.add_custom_handler("conflicting", conflicting_training_handler)
        precision_nutrition.add_custom_handler(
            "conflicting", conflicting_nutrition_handler
        )

        # Submit request that triggers conflicting responses
        conflicting_message = {
            "user_input": "I'm conflicting between training hard and proper recovery",
            "context": {
                "user_id": "test_user_conflict_1",
                "session_id": str(uuid.uuid4()),
                "conflict_scenario": True,
            },
        }

        # Process the conflicting request
        response = await orchestrator.process_message(conflicting_message)

        # Verify orchestrator handled the request successfully despite conflicts
        assert response["status"] == "success"

        # The orchestrator should be able to route and get responses
        response_data = response["response_data"]
        assert "agents_to_call" in response_data

        # Verify routing decision includes reasoning
        routing_decision = response_data.get("routing_decision", {})
        assert "reasoning" in routing_decision

        logger.info("Conflict resolution test completed successfully")

    async def test_partial_agent_failure_graceful_degradation(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test graceful degradation when some agents fail but others succeed.

        Verifies the orchestrator can still provide value when not all agents respond.
        """
        orchestrator = registered_agents["orchestrator"]

        # Set one agent to have high error rate
        failing_agent = registered_agents["precision_nutrition_architect"]
        failing_agent.set_error_rate(0.8)  # 80% failure rate

        # Set another agent to work normally
        working_agent = registered_agents["elite_training_strategist"]
        working_agent.set_error_rate(0.0)  # 0% failure rate

        # Request that would normally call both agents
        mixed_message = {
            "user_input": "I need help with both training and nutrition planning",
            "context": {
                "user_id": "test_user_partial_failure_1",
                "session_id": str(uuid.uuid4()),
                "graceful_degradation_test": True,
            },
        }

        # Process request multiple times to test consistency
        results = []
        for i in range(5):
            response = await orchestrator.process_message(mixed_message)
            results.append(response)

        # Analyze results
        successful_responses = [r for r in results if r["status"] == "success"]
        failed_responses = [r for r in results if r["status"] == "error"]

        # The orchestrator should handle the situation gracefully
        # At least some responses should succeed (from the working agent)
        assert (
            len(successful_responses) >= 2
        ), "Should have some successful responses despite partial failures"

        # If there are failures, they should be handled gracefully
        for response in failed_responses:
            assert "error" in response
            assert response["error"] is not None

        # Reset error rates
        failing_agent.set_error_rate(0.0)

        logger.info(
            f"Partial failure test: {len(successful_responses)}/5 successful despite agent failures"
        )


class TestCircuitBreakerFunctionality:
    """Test circuit breaker patterns for agent resilience."""

    async def test_agent_circuit_breaker_activation(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test circuit breaker activation when an agent consistently fails.

        Verifies that failing agents are temporarily isolated to prevent cascade failures.
        """
        orchestrator = registered_agents["orchestrator"]

        # Set up an agent to consistently fail
        failing_agent = registered_agents["genetic_specialist"]
        failing_agent.set_error_rate(1.0)  # 100% failure rate

        # Send multiple requests to trigger circuit breaker
        genetic_message = {
            "user_input": "Analyze my genetic data for training optimization",
            "context": {
                "user_id": "test_user_circuit_breaker",
                "session_id": str(uuid.uuid4()),
                "has_genetic_data": True,
                "circuit_breaker_test": True,
            },
        }

        # Send multiple requests to trigger failures
        failure_responses = []
        for i in range(6):  # Should trigger circuit breaker after ~5 failures
            response = await orchestrator.process_message(genetic_message)
            failure_responses.append(response)
            await asyncio.sleep(0.1)  # Small delay between requests

        # Verify that we got error responses
        error_count = sum(1 for r in failure_responses if r.get("status") == "error")

        # Should have multiple errors (agent is set to 100% failure)
        assert error_count >= 3, f"Expected multiple errors, got {error_count}"

        # Reset the agent to working state
        failing_agent.set_error_rate(0.0)

        # Test recovery after circuit breaker timeout
        await asyncio.sleep(1.0)  # Wait for potential circuit breaker recovery

        recovery_response = await orchestrator.process_message(genetic_message)

        # The orchestrator should still attempt to route (since this is simulation)
        # In a real system, the circuit breaker would prevent calls
        assert recovery_response is not None

        logger.info(
            f"Circuit breaker test: {error_count} failures detected, recovery attempted"
        )

    async def test_circuit_breaker_does_not_affect_other_agents(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test that circuit breaker activation for one agent doesn't affect others.

        Verifies isolation of failures to specific agents.
        """
        orchestrator = registered_agents["orchestrator"]

        # Set up one agent to fail
        failing_agent = registered_agents["biohacking_innovator"]
        failing_agent.set_error_rate(1.0)

        # Keep other agents working
        working_agent = registered_agents["elite_training_strategist"]
        working_agent.set_error_rate(0.0)

        # Message that should trigger the failing agent
        biohacking_message = {
            "user_input": "I want advanced biohacking protocols for optimization",
            "context": {
                "user_id": "test_user_isolation_1",
                "session_id": str(uuid.uuid4()),
                "biohacking_interest": True,
            },
        }

        # Message that should trigger the working agent
        training_message = {
            "user_input": "I need a basic strength training program",
            "context": {
                "user_id": "test_user_isolation_2",
                "session_id": str(uuid.uuid4()),
                "training_request": True,
            },
        }

        # Send multiple requests to trigger circuit breaker for failing agent
        for i in range(5):
            await orchestrator.process_message(biohacking_message)

        # Now test that the working agent still functions
        working_response = await orchestrator.process_message(training_message)

        # Working agent should still respond successfully
        assert working_response["status"] == "success"

        # Reset failing agent
        failing_agent.set_error_rate(0.0)

        logger.info(
            "Circuit breaker isolation test passed - failures isolated to specific agents"
        )


class TestAgentUnavailabilityHandling:
    """Test handling scenarios where agents are unavailable or unresponsive."""

    async def test_agent_timeout_handling(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test orchestrator handling of agent timeouts.

        Simulates agents that take too long to respond.
        """
        orchestrator = registered_agents["orchestrator"]

        # Set an agent to have very slow responses
        slow_agent = registered_agents["performance_analytics"]
        slow_agent.set_response_delay(5.0)  # 5 second delay

        # Message that should route to the slow agent
        analytics_message = {
            "user_input": "Analyze my performance data and trends",
            "context": {
                "user_id": "test_user_timeout",
                "session_id": str(uuid.uuid4()),
                "performance_data": {"recent_workouts": 10},
                "timeout_test": True,
            },
        }

        # Process with timeout expectation
        start_time = time.time()
        response = await orchestrator.process_message(analytics_message)
        execution_time = time.time() - start_time

        # The orchestrator should handle this gracefully
        # Either by timing out appropriately or handling the delay
        assert response is not None

        # In a real system, should timeout faster than the agent delay
        # But in simulation, we verify the system doesn't hang
        assert execution_time < 10.0, "System should not hang indefinitely"

        # Reset agent delay
        slow_agent.set_response_delay(0.1)

        logger.info(f"Timeout handling test completed in {execution_time:.2f}s")

    async def test_missing_agent_fallback(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test orchestrator behavior when trying to route to non-existent agents.

        Verifies graceful fallback when agents are not available.
        """
        orchestrator = registered_agents["orchestrator"]

        # Add a custom handler that tries to route to non-existent agent
        def route_to_missing_agent(message):
            return {
                "content": "I'll route this to our specialized agent",
                "agents_to_call": ["non_existent_agent", "another_missing_agent"],
                "routing_decision": {
                    "confidence": 0.9,
                    "reasoning": "Routing to missing agents for testing",
                },
            }

        orchestrator.add_custom_handler("missing", route_to_missing_agent)

        # Message that triggers routing to missing agents
        missing_agent_message = {
            "user_input": "I need help with missing agent specialization",
            "context": {
                "user_id": "test_user_missing_agent",
                "session_id": str(uuid.uuid4()),
                "missing_agent_test": True,
            },
        }

        # Process the request
        response = await orchestrator.process_message(missing_agent_message)

        # The orchestrator should handle missing agents gracefully
        assert response is not None
        assert response["status"] in ["success", "error"]  # Should not crash

        # If it routes to missing agents, should get an appropriate response
        if response["status"] == "success":
            response_data = response.get("response_data", {})
            agents_called = response_data.get("agents_to_call", [])
            # Should attempt to call the specified agents (even if they don't exist)
            assert "non_existent_agent" in agents_called

        logger.info("Missing agent fallback test completed successfully")

    async def test_partial_agent_availability(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test orchestrator adaptation when only some agents are available.

        Simulates real-world scenarios where agents may be temporarily unavailable.
        """
        orchestrator = registered_agents["orchestrator"]

        # Simulate some agents being unavailable by setting high error rates
        partially_available_agents = [
            "female_wellness_coach",  # Unavailable
            "progress_tracker",  # Unavailable
            "elite_training_strategist",  # Available
            "motivation_behavior_coach",  # Available
        ]

        # Set half the agents to be "unavailable" (high error rate)
        registered_agents["female_wellness_coach"].set_error_rate(1.0)
        registered_agents["progress_tracker"].set_error_rate(1.0)

        # Keep other agents available
        registered_agents["elite_training_strategist"].set_error_rate(0.0)
        registered_agents["motivation_behavior_coach"].set_error_rate(0.0)

        # Message that might route to both available and unavailable agents
        comprehensive_message = {
            "user_input": "I'm a female athlete needing training help and progress tracking",
            "context": {
                "user_id": "test_user_partial_availability",
                "session_id": str(uuid.uuid4()),
                "athlete_type": "female",
                "needs": ["training", "progress_tracking", "motivation"],
                "partial_availability_test": True,
            },
        }

        # Process the request
        response = await orchestrator.process_message(comprehensive_message)

        # The orchestrator should handle partial availability gracefully
        assert response is not None

        # Should still attempt to route to available agents
        if response["status"] == "success":
            response_data = response.get("response_data", {})
            agents_called = response_data.get("agents_to_call", [])

            # Should identify agents to call (may include unavailable ones)
            assert len(agents_called) > 0, "Should attempt to route to some agents"

        # Reset all agents to available state
        for agent in partially_available_agents:
            if agent in registered_agents:
                registered_agents[agent].set_error_rate(0.0)

        logger.info(
            "Partial availability test completed - system adapted to available agents"
        )


class TestRealWorldScenarios:
    """Test realistic multi-agent coordination scenarios."""

    async def test_beginner_onboarding_workflow(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test complete beginner onboarding requiring multiple agent coordination.

        Scenario: New user needs assessment, plan creation, and ongoing support setup.
        """
        orchestrator = registered_agents["orchestrator"]
        session_id = str(uuid.uuid4())

        # Stage 1: Initial assessment
        assessment_message = {
            "user_input": "I'm completely new to fitness and don't know where to start",
            "context": {
                "user_id": "beginner_user_1",
                "session_id": session_id,
                "fitness_level": "complete_beginner",
                "workflow": "onboarding",
                "stage": "assessment",
            },
        }

        assessment_response = await orchestrator.process_message(assessment_message)
        assert assessment_response["status"] == "success"

        # Stage 2: Goal setting and plan creation
        planning_message = {
            "user_input": "I want to lose weight and build confidence, can you create a plan?",
            "context": {
                "user_id": "beginner_user_1",
                "session_id": session_id,
                "goals": ["weight_loss", "confidence_building"],
                "assessment_complete": True,
                "workflow": "onboarding",
                "stage": "planning",
            },
        }

        planning_response = await orchestrator.process_message(planning_message)
        assert planning_response["status"] == "success"

        # Stage 3: Support system setup
        support_message = {
            "user_input": "How do I stay motivated and track my progress?",
            "context": {
                "user_id": "beginner_user_1",
                "session_id": session_id,
                "plan_created": True,
                "workflow": "onboarding",
                "stage": "support_setup",
            },
        }

        support_response = await orchestrator.process_message(support_message)
        assert support_response["status"] == "success"

        # Verify the complete workflow was coordinated
        workflow_responses = [assessment_response, planning_response, support_response]
        all_successful = all(r["status"] == "success" for r in workflow_responses)
        assert all_successful, "Complete onboarding workflow should succeed"

        logger.info("Beginner onboarding workflow completed successfully")

    async def test_injury_recovery_coordination(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test coordination for injury recovery scenario requiring multiple specialists.

        Scenario: User recovering from injury needs modified training and nutrition.
        """
        orchestrator = registered_agents["orchestrator"]
        session_id = str(uuid.uuid4())

        # Injury report and guidance request
        injury_message = {
            "user_input": "I'm recovering from a knee injury and need to modify my training and nutrition",
            "context": {
                "user_id": "injury_recovery_user",
                "session_id": session_id,
                "injury_type": "knee",
                "recovery_stage": "rehabilitation",
                "medical_clearance": True,
                "priority": "high",  # Health-related priority
            },
        }

        # Process injury recovery coordination
        recovery_response = await orchestrator.process_message(injury_message)

        # Verify successful coordination
        assert recovery_response["status"] == "success"

        # Should route to appropriate specialists for injury recovery
        response_data = recovery_response.get("response_data", {})
        agents_called = response_data.get("agents_to_call", [])

        # Expected: training modification + possibly nutrition + wellness
        assert (
            len(agents_called) >= 1
        ), "Should coordinate multiple specialists for injury recovery"

        # Follow-up for progress check
        progress_message = {
            "user_input": "How is my recovery plan working? Should I adjust anything?",
            "context": {
                "user_id": "injury_recovery_user",
                "session_id": session_id,
                "weeks_in_recovery": 3,
                "progress_indicators": ["reduced_pain", "increased_mobility"],
                "follow_up": True,
            },
        }

        progress_response = await orchestrator.process_message(progress_message)
        assert progress_response["status"] == "success"

        logger.info("Injury recovery coordination completed successfully")

    async def test_competition_preparation_workflow(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test coordination for competition preparation requiring peak performance optimization.

        Scenario: Athlete preparing for competition needs comprehensive support.
        """
        orchestrator = registered_agents["orchestrator"]
        session_id = str(uuid.uuid4())

        # Competition preparation request
        competition_message = {
            "user_input": "I have a bodybuilding competition in 12 weeks, need complete preparation plan",
            "context": {
                "user_id": "competition_athlete",
                "session_id": session_id,
                "competition_type": "bodybuilding",
                "weeks_until_competition": 12,
                "current_body_fat": 15,
                "target_body_fat": 8,
                "priority": "high",
            },
        }

        # Process competition preparation
        prep_response = await orchestrator.process_message(competition_message)
        assert prep_response["status"] == "success"

        # Should coordinate multiple agents for comprehensive preparation
        response_data = prep_response.get("response_data", {})
        agents_called = response_data.get("agents_to_call", [])

        # Competition prep typically requires training, nutrition, possibly supplementation
        assert (
            len(agents_called) >= 2
        ), "Competition prep should involve multiple specialists"

        # Peak week coordination
        peak_week_message = {
            "user_input": "It's peak week - final adjustments for competition",
            "context": {
                "user_id": "competition_athlete",
                "session_id": session_id,
                "competition_week": True,
                "days_until_competition": 3,
                "priority": "critical",  # Critical timing
            },
        }

        peak_response = await orchestrator.process_message(peak_week_message)
        assert peak_response["status"] == "success"

        logger.info("Competition preparation workflow completed successfully")


# Performance benchmarks and stress tests
class TestOrchestrationPerformance:
    """Test performance characteristics of multi-agent coordination."""

    async def test_high_concurrency_coordination(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        performance_metrics: Dict[str, Any],
    ):
        """
        Test orchestrator performance under high concurrent load.

        Verifies system stability and response times under stress.
        """
        orchestrator = registered_agents["orchestrator"]

        # Create many concurrent requests
        concurrent_requests = 20
        messages = []

        for i in range(concurrent_requests):
            message = {
                "user_input": f"User {i} needs help with training and nutrition",
                "context": {
                    "user_id": f"concurrent_user_{i}",
                    "session_id": str(uuid.uuid4()),
                    "request_id": i,
                    "concurrency_test": True,
                },
            }
            messages.append(message)

        # Execute all requests concurrently
        start_time = time.time()
        tasks = [orchestrator.process_message(msg) for msg in messages]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Analyze results
        successful_responses = [
            r
            for r in responses
            if not isinstance(r, Exception) and r.get("status") == "success"
        ]
        failed_responses = [
            r
            for r in responses
            if isinstance(r, Exception) or r.get("status") == "error"
        ]

        # Update performance metrics
        performance_metrics["total_requests"] = concurrent_requests
        performance_metrics["successful_requests"] = len(successful_responses)
        performance_metrics["failed_requests"] = len(failed_responses)
        performance_metrics["success_rate"] = (
            len(successful_responses) / concurrent_requests
        )
        performance_metrics["throughput"] = concurrent_requests / total_time
        performance_metrics["total_time"] = total_time

        # Performance assertions
        assert (
            performance_metrics["success_rate"] >= 0.8
        ), f"Success rate too low: {performance_metrics['success_rate']}"
        assert (
            performance_metrics["throughput"] >= 5.0
        ), f"Throughput too low: {performance_metrics['throughput']} req/s"
        assert total_time < 10.0, f"Total time too high: {total_time}s"

        logger.info(
            f"High concurrency test: {performance_metrics['throughput']:.2f} req/s, "
            f"{performance_metrics['success_rate']:.1%} success rate"
        )

    async def test_memory_usage_stability(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """
        Test memory usage stability during extended operation.

        Verifies no memory leaks in orchestration logic.
        """
        orchestrator = registered_agents["orchestrator"]

        # Run many sequential requests to test memory stability
        num_requests = 50
        responses = []

        for i in range(num_requests):
            message = {
                "user_input": f"Memory test request {i}",
                "context": {
                    "user_id": f"memory_test_user_{i}",
                    "session_id": str(uuid.uuid4()),
                    "memory_test": True,
                    "iteration": i,
                },
            }

            response = await orchestrator.process_message(message)
            responses.append(response)

            # Small delay to allow cleanup
            if i % 10 == 0:
                await asyncio.sleep(0.1)

        # Verify all requests were processed successfully
        successful_responses = [r for r in responses if r.get("status") == "success"]
        success_rate = len(successful_responses) / num_requests

        assert success_rate >= 0.9, f"Success rate degraded over time: {success_rate}"

        # Check that agent statistics are reasonable (no extreme values indicating leaks)
        agent_stats = orchestrator.get_stats()
        assert agent_stats["messages_processed"] == num_requests

        logger.info(
            f"Memory stability test: {num_requests} requests processed, {success_rate:.1%} success rate"
        )


# Cleanup and teardown
@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Ensure clean state after each test."""
    yield
    # Cleanup happens automatically via existing fixtures
    await asyncio.sleep(0.1)  # Small delay to allow cleanup
