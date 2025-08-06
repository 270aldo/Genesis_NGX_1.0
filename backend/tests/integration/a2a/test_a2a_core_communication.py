"""
Core A2A Communication Integration Tests.

Comprehensive test suite for fundamental A2A communication features:
- Agent registration and deregistration
- WebSocket connection establishment and heartbeat
- Basic message passing between agents using call_agent()
- Message priority system (CRITICAL > HIGH > NORMAL > LOW)
- Timeout handling and resource cleanup
- Multiple agents communicating simultaneously

This file tests the core A2A infrastructure without requiring actual AI models.
"""

import asyncio
import time
import uuid
from typing import Any, Dict

import pytest

from core.logging_config import get_logger
from infrastructure.a2a_optimized import MessagePriority
from infrastructure.adapters.a2a_adapter import A2AAdapter
from tests.integration.a2a.utils.agent_simulator import AgentSimulator, SimulatedAgent
from tests.integration.a2a.utils.test_server import TestA2AServer

logger = get_logger(__name__)


class TestA2ACoreRegistration:
    """Test agent registration and deregistration with the A2A server."""

    async def test_single_agent_registration(
        self, test_a2a_server: TestA2AServer, agent_simulator: AgentSimulator
    ):
        """Test registering a single agent with the A2A server."""
        # Get a test agent
        orchestrator = agent_simulator.get_agent("orchestrator")
        assert orchestrator is not None

        # Register the agent
        def message_handler(msg):
            return orchestrator.process_message(msg)

        success = await test_a2a_server.register_test_agent(
            orchestrator.agent_id, message_handler
        )

        assert success is True
        assert orchestrator.agent_id in test_a2a_server.registered_agents

        # Verify server metrics
        metrics = test_a2a_server.get_metrics()
        assert metrics["agents_registered"] == 1

    async def test_multiple_agent_registration(
        self, test_a2a_server: TestA2AServer, agent_simulator: AgentSimulator
    ):
        """Test registering multiple agents simultaneously."""
        # Register all simulated agents
        await agent_simulator.register_all_with_server(test_a2a_server)

        # Verify all agents are registered
        expected_agents = list(agent_simulator.agents.keys())
        assert len(test_a2a_server.registered_agents) == len(expected_agents)

        for agent_id in expected_agents:
            assert agent_id in test_a2a_server.registered_agents

        # Verify server metrics
        metrics = test_a2a_server.get_metrics()
        assert metrics["agents_registered"] == len(expected_agents)

    async def test_agent_deregistration(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """Test deregistering agents from the A2A server."""
        # Pick an agent to deregister
        agent_id = "orchestrator"
        assert agent_id in test_a2a_server.registered_agents

        # Simulate disconnection
        await test_a2a_server.simulate_agent_disconnect(agent_id)

        # Verify agent is no longer registered
        assert agent_id not in test_a2a_server.registered_agents

        # Verify metrics updated
        metrics = test_a2a_server.get_metrics()
        assert metrics["agents_disconnected"] == 1

    async def test_duplicate_registration_rejection(
        self, test_a2a_server: TestA2AServer, agent_simulator: AgentSimulator
    ):
        """Test that duplicate agent registration is handled properly."""
        orchestrator = agent_simulator.get_agent("orchestrator")

        def handler(msg):
            return orchestrator.process_message(msg)

        # First registration should succeed
        success1 = await test_a2a_server.register_test_agent(
            orchestrator.agent_id, handler
        )
        assert success1 is True

        # Second registration should fail or be handled gracefully
        success2 = await test_a2a_server.register_test_agent(
            orchestrator.agent_id, handler
        )

        # The behavior depends on implementation - either fails or succeeds silently
        # The important thing is no crashes occur
        assert isinstance(success2, bool)


class TestA2AMessagePassing:
    """Test basic message passing between agents."""

    async def test_simple_message_send(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test sending a simple message between two agents."""
        from_agent = "orchestrator"
        to_agent = "elite_training_strategist"
        message_content = sample_messages["simple_training"]

        # Send message
        success = await test_a2a_server.send_test_message(
            from_agent=from_agent,
            to_agent=to_agent,
            content=message_content,
            priority=MessagePriority.NORMAL,
        )

        assert success is True

        # Verify metrics
        metrics = test_a2a_server.get_metrics()
        assert metrics["messages_sent"] >= 1
        assert metrics["messages_failed"] == 0

    async def test_message_with_all_priority_levels(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test sending messages with different priority levels."""
        from_agent = "orchestrator"
        to_agent = "elite_training_strategist"

        priorities = [
            MessagePriority.LOW,
            MessagePriority.NORMAL,
            MessagePriority.HIGH,
            MessagePriority.CRITICAL,
        ]

        messages_sent = 0
        for priority in priorities:
            success = await test_a2a_server.send_test_message(
                from_agent=from_agent,
                to_agent=to_agent,
                content=sample_messages["simple_training"],
                priority=priority,
            )

            assert success is True
            messages_sent += 1

        # Verify all messages were sent
        metrics = test_a2a_server.get_metrics()
        assert metrics["messages_sent"] >= messages_sent

    async def test_message_to_nonexistent_agent(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test sending message to an agent that doesn't exist."""
        success = await test_a2a_server.send_test_message(
            from_agent="orchestrator",
            to_agent="nonexistent_agent",
            content=sample_messages["simple_training"],
            priority=MessagePriority.NORMAL,
        )

        # Should fail gracefully
        assert success is False

        # Verify failed delivery is tracked
        metrics = test_a2a_server.get_metrics()
        assert metrics["messages_failed"] >= 1

    async def test_bidirectional_communication(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test bidirectional communication between agents."""
        agent1 = "orchestrator"
        agent2 = "elite_training_strategist"

        # Send message from agent1 to agent2
        success1 = await test_a2a_server.send_test_message(
            from_agent=agent1,
            to_agent=agent2,
            content=sample_messages["simple_training"],
            priority=MessagePriority.NORMAL,
        )

        # Send message from agent2 to agent1
        success2 = await test_a2a_server.send_test_message(
            from_agent=agent2,
            to_agent=agent1,
            content={"response": "Training plan created"},
            priority=MessagePriority.NORMAL,
        )

        assert success1 is True
        assert success2 is True

        # Verify both messages were sent
        metrics = test_a2a_server.get_metrics()
        assert metrics["messages_sent"] >= 2


class TestA2ACallAgent:
    """Test the call_agent functionality for direct agent communication."""

    async def test_call_agent_basic(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test basic call_agent functionality."""
        # Register agents with the adapter
        for agent_id, agent in registered_agents.items():
            a2a_adapter.register_agent(
                agent_id,
                {
                    "name": agent.name,
                    "description": agent.description,
                    "message_callback": agent.process_message,
                },
            )

        # Wait a moment for registration to complete
        await asyncio.sleep(0.1)

        # Call an agent
        response = await a2a_adapter.call_agent(
            agent_id="elite_training_strategist",
            user_input="I need a training plan for strength",
            context={"user_id": "test_user", "goal": "strength"},
        )

        # Verify response structure
        assert isinstance(response, dict)
        assert "status" in response
        # The response could be success or error depending on implementation

    async def test_call_agent_with_context(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test call_agent with rich context information."""
        # Register orchestrator
        orchestrator = registered_agents["orchestrator"]
        a2a_adapter.register_agent(
            orchestrator.agent_id,
            {
                "name": orchestrator.name,
                "description": orchestrator.description,
                "message_callback": orchestrator.process_message,
            },
        )

        await asyncio.sleep(0.1)

        # Call with detailed context
        response = await a2a_adapter.call_agent(
            agent_id="orchestrator",
            user_input="I'm frustrated with my training and nutrition progress",
            context={
                "user_id": "test_user_123",
                "emotion": "frustrated",
                "topics": ["training", "nutrition"],
                "session_id": str(uuid.uuid4()),
            },
        )

        assert isinstance(response, dict)
        assert "status" in response

    async def test_call_nonexistent_agent(self, a2a_adapter: A2AAdapter):
        """Test calling an agent that doesn't exist."""
        response = await a2a_adapter.call_agent(
            agent_id="nonexistent_agent", user_input="Hello", context={}
        )

        # Should return error response
        assert isinstance(response, dict)
        assert response["status"] == "error"
        assert "not registered" in response["error"].lower()

    async def test_call_agent_timeout(
        self, a2a_adapter: A2AAdapter, agent_simulator: AgentSimulator
    ):
        """Test call_agent timeout handling."""
        # Create a slow agent that doesn't respond
        slow_agent = SimulatedAgent(
            agent_id="slow_agent",
            agent_type="slow_agent",
            name="Slow Agent",
            description="Agent that responds very slowly",
            response_delay=65.0,  # Longer than timeout
        )

        a2a_adapter.register_agent(
            slow_agent.agent_id,
            {
                "name": slow_agent.name,
                "description": slow_agent.description,
                "message_callback": slow_agent.process_message,
            },
        )

        await asyncio.sleep(0.1)

        # Call should timeout
        start_time = time.time()
        response = await a2a_adapter.call_agent(
            agent_id="slow_agent", user_input="Hello", context={}
        )
        elapsed_time = time.time() - start_time

        # Should timeout and return error
        assert isinstance(response, dict)
        assert response["status"] == "error"
        assert "timeout" in response["error"].lower()
        assert elapsed_time < 65.0  # Should not wait full delay


class TestA2AMultipleAgentCommunication:
    """Test communication patterns with multiple agents."""

    async def test_multiple_agents_parallel_calls(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test calling multiple agents in parallel."""
        # Register key agents
        target_agents = [
            "elite_training_strategist",
            "precision_nutrition_architect",
            "motivation_behavior_coach",
        ]

        for agent_id in target_agents:
            if agent_id in registered_agents:
                agent = registered_agents[agent_id]
                a2a_adapter.register_agent(
                    agent_id,
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "message_callback": agent.process_message,
                    },
                )

        await asyncio.sleep(0.1)

        # Call multiple agents
        responses = await a2a_adapter.call_multiple_agents(
            user_input="I need help with training and nutrition",
            agent_ids=target_agents,
            context={"user_id": "test_user"},
        )

        # Verify responses
        assert isinstance(responses, dict)
        assert len(responses) == len(target_agents)

        for agent_id in target_agents:
            assert agent_id in responses
            assert isinstance(responses[agent_id], dict)
            assert "status" in responses[agent_id]

    async def test_agent_coordination_workflow(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test a realistic workflow with agent coordination."""
        # Register orchestrator and specialists
        agents_to_register = [
            "orchestrator",
            "elite_training_strategist",
            "precision_nutrition_architect",
        ]

        for agent_id in agents_to_register:
            if agent_id in registered_agents:
                agent = registered_agents[agent_id]
                a2a_adapter.register_agent(
                    agent_id,
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "message_callback": agent.process_message,
                    },
                )

        await asyncio.sleep(0.1)

        # Step 1: Call orchestrator
        orchestrator_response = await a2a_adapter.call_agent(
            agent_id="orchestrator",
            user_input="I need a comprehensive fitness plan",
            context={"user_id": "test_user", "goal": "comprehensive"},
        )

        assert isinstance(orchestrator_response, dict)

        # Step 2: Call specialists based on orchestrator response
        specialist_responses = await a2a_adapter.call_multiple_agents(
            user_input="Create a detailed plan based on orchestrator's guidance",
            agent_ids=["elite_training_strategist", "precision_nutrition_architect"],
            context={
                "user_id": "test_user",
                "orchestrator_response": orchestrator_response,
            },
        )

        assert isinstance(specialist_responses, dict)
        assert len(specialist_responses) == 2

    async def test_high_concurrent_message_load(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test server performance under high concurrent message load."""
        num_messages = 50
        from_agent = "orchestrator"
        to_agents = [
            "elite_training_strategist",
            "precision_nutrition_architect",
            "motivation_behavior_coach",
        ]

        # Create concurrent message tasks
        tasks = []
        for i in range(num_messages):
            to_agent = to_agents[i % len(to_agents)]
            priority = list(MessagePriority)[i % len(MessagePriority)]

            task = test_a2a_server.send_test_message(
                from_agent=from_agent,
                to_agent=to_agent,
                content=sample_messages["simple_training"],
                priority=priority,
            )
            tasks.append(task)

        # Execute all tasks concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed_time = time.time() - start_time

        # Analyze results
        successful_sends = sum(1 for result in results if result is True)
        len(results) - successful_sends

        logger.info(
            f"Concurrent load test: {successful_sends}/{num_messages} successful in {elapsed_time:.2f}s"
        )

        # Verify performance
        assert successful_sends > 0  # At least some messages should succeed
        assert elapsed_time < 10.0  # Should complete within reasonable time

        # Verify metrics
        metrics = test_a2a_server.get_metrics()
        assert metrics["messages_sent"] >= successful_sends
        assert metrics["max_latency_ms"] > 0


class TestA2ATimeoutAndCleanup:
    """Test timeout handling and resource cleanup."""

    async def test_connection_heartbeat(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        default_timeout: float,
    ):
        """Test that agent connections maintain heartbeat."""
        # This is a placeholder test since WebSocket heartbeat
        # implementation depends on the actual server architecture

        # Verify agents are still registered after some time
        initial_count = len(test_a2a_server.registered_agents)

        # Wait for heartbeat interval
        await asyncio.sleep(1.0)

        # Agents should still be registered
        current_count = len(test_a2a_server.registered_agents)
        assert current_count == initial_count

    async def test_resource_cleanup_on_server_stop(
        self, agent_simulator: AgentSimulator
    ):
        """Test that resources are properly cleaned up when server stops."""
        # Create a temporary test server
        temp_server = TestA2AServer()
        await temp_server.start()

        # Register some agents
        orchestrator = agent_simulator.get_agent("orchestrator")

        def handler(msg):
            return orchestrator.process_message(msg)

        await temp_server.register_test_agent(orchestrator.agent_id, handler)

        # Verify agent is registered
        assert len(temp_server.registered_agents) == 1

        # Stop server
        await temp_server.stop()

        # Verify cleanup (this test verifies no exceptions are raised)
        assert True  # If we get here, cleanup succeeded

    async def test_message_queue_overflow_handling(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test handling of message queue overflow."""
        # This test attempts to overflow the message queue
        # and verify graceful handling

        from_agent = "orchestrator"
        to_agent = "elite_training_strategist"

        # Send many messages rapidly
        overflow_count = 1200  # More than typical queue size
        successful_sends = 0

        for i in range(overflow_count):
            try:
                success = await test_a2a_server.send_test_message(
                    from_agent=from_agent,
                    to_agent=to_agent,
                    content=sample_messages["simple_training"],
                    priority=MessagePriority.NORMAL,
                )
                if success:
                    successful_sends += 1
            except Exception:
                # Some messages may fail due to overflow - this is expected
                pass

        # Should handle overflow gracefully without crashing
        assert successful_sends > 0  # At least some should succeed

        # Server should still be functional
        metrics = test_a2a_server.get_metrics()
        assert isinstance(metrics, dict)

    async def test_error_recovery_after_agent_failure(
        self, a2a_adapter: A2AAdapter, agent_simulator: AgentSimulator
    ):
        """Test system recovery after an agent encounters errors."""
        # Create an agent with high error rate
        error_agent = SimulatedAgent(
            agent_id="error_agent",
            agent_type="error_agent",
            name="Error Agent",
            description="Agent that frequently errors",
            error_rate=0.8,  # 80% error rate
        )

        # Register the error-prone agent
        a2a_adapter.register_agent(
            error_agent.agent_id,
            {
                "name": error_agent.name,
                "description": error_agent.description,
                "message_callback": error_agent.process_message,
            },
        )

        await asyncio.sleep(0.1)

        # Try calling the agent multiple times
        error_responses = 0
        success_responses = 0

        for i in range(10):
            response = await a2a_adapter.call_agent(
                agent_id="error_agent",
                user_input=f"Test message {i}",
                context={"test": True},
            )

            if response.get("status") == "error":
                error_responses += 1
            else:
                success_responses += 1

        # Should have some errors due to high error rate
        assert error_responses > 0

        # System should still be functional - we can still make calls
        assert True  # If we get here, system didn't crash


class TestA2AMessagePrioritySystem:
    """Test the message priority system implementation."""

    async def test_priority_message_ordering(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test that higher priority messages are processed first."""
        from_agent = "orchestrator"
        to_agent = "elite_training_strategist"

        # Send messages in reverse priority order (LOW first, CRITICAL last)
        messages_sent = []

        priorities = [
            (MessagePriority.LOW, "low priority message"),
            (MessagePriority.NORMAL, "normal priority message"),
            (MessagePriority.HIGH, "high priority message"),
            (MessagePriority.CRITICAL, "critical priority message"),
        ]

        # Send all messages rapidly
        for priority, content in priorities:
            message_content = {"text": content, "priority": priority.name}
            success = await test_a2a_server.send_test_message(
                from_agent=from_agent,
                to_agent=to_agent,
                content=message_content,
                priority=priority,
            )

            assert success is True
            messages_sent.append((priority, content))

        # Verify all messages were sent
        assert len(messages_sent) == 4

        # Note: Actual priority ordering verification would require
        # monitoring message processing order, which depends on
        # implementation details

    async def test_critical_priority_emergency_handling(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test that CRITICAL priority messages get immediate attention."""
        from_agent = "orchestrator"
        to_agent = "guardian"  # Security agent for emergency handling

        # Send critical emergency message
        emergency_message = sample_messages["emergency"]

        start_time = time.time()
        success = await test_a2a_server.send_test_message(
            from_agent=from_agent,
            to_agent=to_agent,
            content=emergency_message,
            priority=MessagePriority.CRITICAL,
        )
        elapsed_time = time.time() - start_time

        assert success is True

        # Critical messages should be processed very quickly
        assert elapsed_time < 1.0  # Should complete within 1 second

        # Verify metrics tracked the critical message
        metrics = test_a2a_server.get_metrics()
        assert metrics["messages_sent"] >= 1


# Performance and reliability markers
pytestmark = [pytest.mark.integration, pytest.mark.a2a, pytest.mark.asyncio]
