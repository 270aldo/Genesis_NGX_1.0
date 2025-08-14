"""
A2A (Agent-to-Agent) Contract Testing for GENESIS Platform

Tests the communication contracts between AI agents to ensure:
- Message format consistency
- Agent coordination protocols
- Streaming response handling
- Error propagation
- Agent discovery and registration
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from agents.elite_training_strategist.agent import EliteTrainingStrategist
from agents.orchestrator.agent import Orchestrator
from agents.precision_nutrition_architect.agent import PrecisionNutritionArchitect
from infrastructure.a2a_server import A2AServer
from tests.contract.base_contract_test import A2AMessage, BaseContractTest


class TestA2AContracts(BaseContractTest):
    """Test suite for A2A communication contract validation"""

    def setup_method(self):
        super().setup_method()

        # Initialize A2A server for testing
        self.a2a_server = A2AServer()

        # Mock agents for testing
        self.orchestrator = MagicMock(spec=Orchestrator)
        self.blaze_agent = MagicMock(spec=EliteTrainingStrategist)
        self.sage_agent = MagicMock(spec=PrecisionNutritionArchitect)

        # Register mock agents
        self.registered_agents = {
            "orchestrator": self.orchestrator,
            "elite-training-strategist": self.blaze_agent,
            "precision-nutrition-architect": self.sage_agent,
        }

    # Agent Registration Contract Tests

    async def test_agent_registration_contract(self):
        """Test agent registration message contract"""
        registration_message = {
            "agent_id": "test-agent",
            "agent_name": "Test Agent",
            "capabilities": ["training", "analysis"],
            "version": "1.0.0",
            "status": "active",
            "endpoints": {"process": "/process", "health": "/health"},
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Validate registration message structure
        required_fields = [
            "agent_id",
            "agent_name",
            "capabilities",
            "version",
            "status",
        ]
        for field in required_fields:
            assert field in registration_message, f"Missing required field: {field}"

        # Test agent registration via A2A
        with patch.object(self.a2a_server, "register_agent") as mock_register:
            mock_register.return_value = {
                "status": "registered",
                "agent_id": "test-agent",
            }

            result = await self.a2a_server.register_agent(registration_message)
            assert result["status"] == "registered"
            mock_register.assert_called_once()

    async def test_agent_discovery_contract(self):
        """Test agent discovery message contract"""
        discovery_request = {
            "requester": "orchestrator",
            "capabilities_needed": ["training"],
            "filters": {"status": "active", "version": ">=1.0.0"},
            "timestamp": datetime.utcnow().isoformat(),
        }

        expected_response = {
            "available_agents": [
                {
                    "agent_id": "elite-training-strategist",
                    "agent_name": "BLAZE",
                    "capabilities": ["training", "exercise_planning"],
                    "status": "active",
                    "load": 0.25,
                }
            ],
            "total_count": 1,
            "timestamp": datetime.utcnow().isoformat(),
        }

        with patch.object(self.a2a_server, "discover_agents") as mock_discover:
            mock_discover.return_value = expected_response

            result = await self.a2a_server.discover_agents(discovery_request)

            # Validate response structure
            assert "available_agents" in result
            assert "total_count" in result
            assert isinstance(result["available_agents"], list)

            for agent in result["available_agents"]:
                required_agent_fields = [
                    "agent_id",
                    "agent_name",
                    "capabilities",
                    "status",
                ]
                for field in required_agent_fields:
                    assert field in agent, f"Missing agent field: {field}"

    # Message Routing Contract Tests

    async def test_message_routing_contract(self):
        """Test A2A message routing contract"""
        test_message = A2AMessage(
            agent_from="orchestrator",
            agent_to="elite-training-strategist",
            message_type="training_request",
            payload={
                "user_id": "test-user-123",
                "request": "Create a muscle building plan",
                "user_profile": {
                    "fitness_level": "beginner",
                    "goals": ["muscle_gain"],
                    "limitations": [],
                },
            },
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().timestamp(),
        )

        # Mock target agent response
        expected_response = {
            "agent_from": "elite-training-strategist",
            "message_type": "training_response",
            "payload": {
                "training_plan": {
                    "title": "Beginner Muscle Building Program",
                    "duration_weeks": 12,
                    "workouts": [],
                },
                "confidence": 0.95,
            },
            "correlation_id": test_message.correlation_id,
            "timestamp": datetime.utcnow().timestamp(),
        }

        with patch.object(self.a2a_server, "route_message") as mock_route:
            mock_route.return_value = expected_response

            # Send message
            response = await self.send_a2a_message(test_message)

            # Validate response contract
            is_valid, errors = await self.validate_a2a_response(
                response, "training_response"
            )

            assert is_valid, f"Invalid A2A response: {errors}"
            assert response["correlation_id"] == test_message.correlation_id

    # Streaming Response Contract Tests

    async def test_streaming_response_contract(self):
        """Test A2A streaming response contract"""
        streaming_request = A2AMessage(
            agent_from="orchestrator",
            agent_to="precision-nutrition-architect",
            message_type="nutrition_analysis_stream",
            payload={
                "user_id": "test-user-123",
                "analysis_type": "comprehensive",
                "data": {
                    "dietary_preferences": ["vegetarian"],
                    "health_goals": ["weight_loss"],
                },
            },
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().timestamp(),
        )

        # Expected streaming response chunks
        expected_chunks = [
            {
                "chunk_type": "analysis_start",
                "chunk_data": {"status": "initializing"},
                "chunk_index": 0,
                "is_final": False,
            },
            {
                "chunk_type": "analysis_progress",
                "chunk_data": {"progress": 0.5, "current_step": "macro_calculation"},
                "chunk_index": 1,
                "is_final": False,
            },
            {
                "chunk_type": "analysis_complete",
                "chunk_data": {
                    "nutrition_plan": {
                        "daily_calories": 1800,
                        "macros": {"protein": 135, "carbs": 180, "fat": 60},
                    }
                },
                "chunk_index": 2,
                "is_final": True,
            },
        ]

        with patch.object(self.a2a_server, "stream_response") as mock_stream:
            # Mock streaming response
            async def mock_stream_generator():
                for chunk in expected_chunks:
                    yield {
                        "agent_from": "precision-nutrition-architect",
                        "message_type": "nutrition_analysis_chunk",
                        "payload": chunk,
                        "correlation_id": streaming_request.correlation_id,
                        "timestamp": datetime.utcnow().timestamp(),
                    }

            mock_stream.return_value = mock_stream_generator()

            # Test streaming response
            chunks_received = []
            async for chunk in self.a2a_server.stream_response(streaming_request):
                chunks_received.append(chunk)

                # Validate each chunk contract
                required_chunk_fields = ["chunk_type", "chunk_index", "is_final"]
                for field in required_chunk_fields:
                    assert field in chunk["payload"], f"Missing chunk field: {field}"

            # Validate complete streaming sequence
            assert len(chunks_received) == len(expected_chunks)
            assert chunks_received[-1]["payload"]["is_final"] is True

    # Error Handling Contract Tests

    async def test_error_propagation_contract(self):
        """Test A2A error propagation contract"""
        error_triggering_message = A2AMessage(
            agent_from="orchestrator",
            agent_to="nonexistent-agent",
            message_type="test_request",
            payload={"test": "data"},
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().timestamp(),
        )

        expected_error_response = {
            "agent_from": "a2a-server",
            "message_type": "error",
            "payload": {
                "error_type": "agent_not_found",
                "error_code": "A2A_001",
                "error_message": "Target agent not found: nonexistent-agent",
                "original_message": {
                    "agent_to": "nonexistent-agent",
                    "message_type": "test_request",
                    "correlation_id": error_triggering_message.correlation_id,
                },
            },
            "correlation_id": error_triggering_message.correlation_id,
            "timestamp": datetime.utcnow().timestamp(),
        }

        with patch.object(self.a2a_server, "route_message") as mock_route:
            mock_route.return_value = expected_error_response

            # Send message that should trigger error
            response = await self.send_a2a_message(error_triggering_message)

            # Validate error response contract
            assert response["message_type"] == "error"
            assert "error_type" in response["payload"]
            assert "error_code" in response["payload"]
            assert "error_message" in response["payload"]
            assert response["correlation_id"] == error_triggering_message.correlation_id

    # Agent Coordination Contract Tests

    async def test_multi_agent_coordination_contract(self):
        """Test multi-agent coordination message contract"""
        coordination_request = A2AMessage(
            agent_from="orchestrator",
            agent_to="coordination-group",
            message_type="multi_agent_request",
            payload={
                "user_id": "test-user-123",
                "task": "comprehensive_health_plan",
                "required_agents": [
                    "elite-training-strategist",
                    "precision-nutrition-architect",
                ],
                "coordination_strategy": "sequential",
                "context": {
                    "user_goals": ["weight_loss", "muscle_gain"],
                    "timeline": "12_weeks",
                },
            },
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().timestamp(),
        )

        expected_coordination_response = {
            "agent_from": "orchestrator",
            "message_type": "coordination_complete",
            "payload": {
                "coordination_id": str(uuid.uuid4()),
                "participating_agents": [
                    "elite-training-strategist",
                    "precision-nutrition-architect",
                ],
                "execution_plan": [
                    {
                        "step": 1,
                        "agent": "elite-training-strategist",
                        "task": "create_training_plan",
                        "dependencies": [],
                    },
                    {
                        "step": 2,
                        "agent": "precision-nutrition-architect",
                        "task": "create_nutrition_plan",
                        "dependencies": ["step_1_complete"],
                    },
                ],
                "estimated_completion": "2024-01-15T10:00:00Z",
            },
            "correlation_id": coordination_request.correlation_id,
            "timestamp": datetime.utcnow().timestamp(),
        }

        with patch.object(self.a2a_server, "coordinate_agents") as mock_coordinate:
            mock_coordinate.return_value = expected_coordination_response

            response = await self.send_a2a_message(coordination_request)

            # Validate coordination response contract
            assert response["message_type"] == "coordination_complete"
            assert "coordination_id" in response["payload"]
            assert "participating_agents" in response["payload"]
            assert "execution_plan" in response["payload"]

            # Validate execution plan structure
            for step in response["payload"]["execution_plan"]:
                required_step_fields = ["step", "agent", "task"]
                for field in required_step_fields:
                    assert field in step, f"Missing execution step field: {field}"

    # Load Balancing Contract Tests

    async def test_load_balancing_contract(self):
        """Test A2A load balancing message contract"""
        load_query = {
            "requester": "orchestrator",
            "agent_type": "training",
            "current_load": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

        expected_load_response = {
            "agents": [
                {
                    "agent_id": "elite-training-strategist-1",
                    "current_load": 0.25,
                    "max_capacity": 100,
                    "active_sessions": 25,
                    "avg_response_time_ms": 1200,
                    "status": "healthy",
                },
                {
                    "agent_id": "elite-training-strategist-2",
                    "current_load": 0.80,
                    "max_capacity": 100,
                    "active_sessions": 80,
                    "avg_response_time_ms": 2500,
                    "status": "busy",
                },
            ],
            "recommendation": {
                "agent_id": "elite-training-strategist-1",
                "reason": "lowest_load",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        with patch.object(self.a2a_server, "get_agent_loads") as mock_loads:
            mock_loads.return_value = expected_load_response

            response = await self.a2a_server.get_agent_loads(load_query)

            # Validate load response contract
            assert "agents" in response
            assert "recommendation" in response

            for agent in response["agents"]:
                required_load_fields = [
                    "agent_id",
                    "current_load",
                    "max_capacity",
                    "active_sessions",
                    "status",
                ]
                for field in required_load_fields:
                    assert field in agent, f"Missing load field: {field}"

    # Health Check Contract Tests

    async def test_agent_health_check_contract(self):
        """Test A2A agent health check contract"""
        health_request = A2AMessage(
            agent_from="a2a-server",
            agent_to="elite-training-strategist",
            message_type="health_check",
            payload={"check_type": "full", "include_metrics": True},
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().timestamp(),
        )

        expected_health_response = {
            "agent_from": "elite-training-strategist",
            "message_type": "health_status",
            "payload": {
                "status": "healthy",
                "uptime_seconds": 86400,
                "last_activity": datetime.utcnow().isoformat(),
                "active_sessions": 15,
                "processed_messages_total": 1250,
                "error_rate": 0.02,
                "avg_response_time_ms": 1100,
                "memory_usage_mb": 256,
                "cpu_usage_percent": 25.5,
                "version": "1.2.0",
            },
            "correlation_id": health_request.correlation_id,
            "timestamp": datetime.utcnow().timestamp(),
        }

        with patch.object(self.blaze_agent, "health_check") as mock_health:
            mock_health.return_value = expected_health_response

            response = await self.send_a2a_message(health_request)

            # Validate health response contract
            assert response["message_type"] == "health_status"

            health_payload = response["payload"]
            required_health_fields = [
                "status",
                "uptime_seconds",
                "active_sessions",
                "processed_messages_total",
                "error_rate",
                "version",
            ]

            for field in required_health_fields:
                assert field in health_payload, f"Missing health field: {field}"

    # Performance Contract Tests

    async def test_a2a_performance_contracts(self):
        """Test A2A performance requirements"""
        # Agent discovery should be fast
        discovery_start = datetime.utcnow().timestamp()

        with patch.object(self.a2a_server, "discover_agents") as mock_discover:
            mock_discover.return_value = {"available_agents": [], "total_count": 0}
            await self.a2a_server.discover_agents({"requester": "test"})

        discovery_time = (datetime.utcnow().timestamp() - discovery_start) * 1000
        assert discovery_time < 100, f"Agent discovery too slow: {discovery_time}ms"

        # Message routing should be efficient
        routing_start = datetime.utcnow().timestamp()

        test_message = A2AMessage(
            agent_from="test",
            agent_to="test",
            message_type="test",
            payload={},
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().timestamp(),
        )

        with patch.object(self.a2a_server, "route_message") as mock_route:
            mock_route.return_value = {"status": "routed"}
            await self.send_a2a_message(test_message)

        routing_time = (datetime.utcnow().timestamp() - routing_start) * 1000
        assert routing_time < 50, f"Message routing too slow: {routing_time}ms"

    # Comprehensive Contract Validation

    async def test_all_a2a_message_types(self):
        """Test all defined A2A message types have valid contracts"""
        message_types = [
            "training_request",
            "training_response",
            "nutrition_request",
            "nutrition_response",
            "progress_request",
            "progress_response",
            "coordination_request",
            "coordination_response",
            "health_check",
            "health_status",
            "error",
            "acknowledgment",
        ]

        contract_violations = []

        for message_type in message_types:
            # Create test message for each type
            test_message = A2AMessage(
                agent_from="test-agent",
                agent_to="target-agent",
                message_type=message_type,
                payload=self._get_sample_payload_for_message_type(message_type),
                correlation_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().timestamp(),
            )

            # Validate message structure
            is_valid, errors = await self.validate_a2a_response(
                test_message.__dict__, message_type
            )

            if not is_valid:
                contract_violations.append(
                    {"message_type": message_type, "errors": errors}
                )

        assert (
            len(contract_violations) == 0
        ), f"A2A contract violations: {json.dumps(contract_violations, indent=2)}"

    def _get_sample_payload_for_message_type(self, message_type: str) -> Dict[str, Any]:
        """Get sample payload for testing different message types"""
        payloads = {
            "training_request": {
                "user_id": "test-user",
                "request": "Create workout plan",
                "parameters": {},
            },
            "training_response": {
                "training_plan": {"title": "Test Plan"},
                "confidence": 0.9,
            },
            "nutrition_request": {
                "user_id": "test-user",
                "request": "Create meal plan",
            },
            "nutrition_response": {
                "meal_plan": {"title": "Test Meal Plan"},
                "confidence": 0.9,
            },
            "health_check": {"check_type": "basic"},
            "health_status": {"status": "healthy", "uptime_seconds": 3600},
            "error": {"error_type": "processing_error", "error_message": "Test error"},
        }

        return payloads.get(message_type, {})

    def teardown_method(self):
        """Cleanup after each test"""
        super().teardown_method()

        # Generate A2A contract test report
        if self.test_results:
            self._generate_a2a_report()

    def _generate_a2a_report(self):
        """Generate A2A-specific test report"""
        report_path = self.test_data_dir / "a2a_contract_report.json"

        report_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": len(self.test_results),
            "successful_tests": len([r for r in self.test_results if r.success]),
            "test_results": [
                {
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "success": r.success,
                    "performance_ms": r.performance_ms,
                    "errors": r.schema_errors,
                }
                for r in self.test_results
            ],
        }

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"A2A contract test report generated: {report_path}")
