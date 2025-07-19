"""
Comprehensive tests for NODE Systems Integration Agent.
Tests the complete A+ optimized agent implementation.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from agents.backend.node.agent_optimized import (
    NodeSystemsIntegrationAgent,
    create_node_agent,
)
from agents.backend.node.core.config import NodeConfig
from agents.backend.node.core.exceptions import (
    NodeIntegrationError,
    NodeValidationError,
)


class TestNodeSystemsIntegrationAgent:
    """Test suite for NODE Systems Integration Agent."""

    @pytest.fixture
    async def mock_dependencies(self):
        """Create mock dependencies for testing."""
        dependencies = MagicMock()

        # Mock Gemini client
        dependencies.vertex_ai_client = AsyncMock()
        dependencies.vertex_ai_client.analyze_with_ai = AsyncMock(
            return_value={
                "analysis": "Mock AI analysis",
                "recommendations": ["recommendation 1", "recommendation 2"],
                "strategic_insights": ["insight 1", "insight 2"],
            }
        )
        dependencies.vertex_ai_client.health_check = AsyncMock()

        # Mock personality adapter
        dependencies.personality_adapter = AsyncMock()
        dependencies.personality_adapter.adapt_response = AsyncMock(
            return_value={
                "adapted_response": "INTJ-adapted response",
                "personality_traits": {"analytical": 0.9, "strategic": 0.95},
                "strategic_insights": ["strategic insight 1"],
                "optimizations": ["optimization 1"],
            }
        )

        # Mock services
        dependencies.systems_integration_service = AsyncMock()
        dependencies.infrastructure_automation_service = AsyncMock()
        dependencies.data_pipeline_service = AsyncMock()
        dependencies.vision_adapter = AsyncMock()
        dependencies.multimodal_adapter = AsyncMock()
        dependencies.voice_client = AsyncMock()
        dependencies.supabase_client = AsyncMock()

        return dependencies

    @pytest.fixture
    async def agent(self, mock_dependencies):
        """Create agent instance for testing."""
        agent = NodeSystemsIntegrationAgent()

        # Mock the dependency creation
        with patch(
            "agents.backend.node.agent_optimized.create_node_dependencies",
            return_value=mock_dependencies,
        ):
            await agent.initialize()

        return agent

    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_dependencies):
        """Test agent initialization process."""
        agent = NodeSystemsIntegrationAgent()

        with patch(
            "agents.backend.node.agent_optimized.create_node_dependencies",
            return_value=mock_dependencies,
        ):
            result = await agent.initialize()

        assert result["status"] == "success"
        assert result["agent_name"] == "NODE Systems Integration"
        assert result["personality"] == "INTJ - The Architect"
        assert result["ready_for_operations"] is True
        assert agent._initialized is True

    @pytest.mark.asyncio
    async def test_agent_initialization_with_config_override(self, mock_dependencies):
        """Test agent initialization with custom configuration."""
        config_override = {
            "environment": "testing",
            "max_concurrent_api_calls": 20,
            "api_timeout": 45,
        }

        agent = NodeSystemsIntegrationAgent(config_override)

        with patch(
            "agents.backend.node.agent_optimized.create_node_dependencies",
            return_value=mock_dependencies,
        ):
            result = await agent.initialize()

        assert result["status"] == "success"
        assert agent.config.environment == "testing"
        assert agent.config.max_concurrent_api_calls == 20

    @pytest.mark.asyncio
    async def test_process_integration_request_api_integration(self, agent):
        """Test processing API integration requests."""
        # Mock skills manager response
        agent.skills_manager.integrate_external_api = AsyncMock(
            return_value={
                "status": "success",
                "integration_type": "external_api",
                "execution_time": datetime.utcnow().isoformat(),
                "api_response": {"data": "test"},
            }
        )

        request_data = {
            "endpoint": "https://api.example.com/test",
            "method": "GET",
            "auth": {"type": "bearer", "token": "test_token"},
        }

        result = await agent.process_integration_request(
            request_type="api_integration", request_data=request_data, priority="high"
        )

        assert result["status"] == "success"
        assert result["request_type"] == "api_integration"
        assert result["priority"] == "high"
        assert "request_analysis" in result
        assert "agent_insights" in result

    @pytest.mark.asyncio
    async def test_process_integration_request_microservices(self, agent):
        """Test processing microservices orchestration requests."""
        agent.skills_manager.orchestrate_microservices = AsyncMock(
            return_value={
                "status": "success",
                "orchestration_pattern": "choreography",
                "services_orchestrated": 3,
                "execution_time": datetime.utcnow().isoformat(),
            }
        )

        request_data = {
            "services": [
                {"name": "user-service", "port": 3001},
                {"name": "auth-service", "port": 3002},
            ],
            "pattern": "choreography",
        }

        result = await agent.process_integration_request(
            request_type="microservices_orchestration",
            request_data=request_data,
            priority="medium",
        )

        assert result["status"] == "success"
        assert result["request_type"] == "microservices_orchestration"
        assert "strategic_recommendations" in result["agent_insights"]

    @pytest.mark.asyncio
    async def test_integrate_external_system(self, agent):
        """Test external system integration."""
        agent.skills_manager.integrate_external_api = AsyncMock(
            return_value={
                "status": "success",
                "integration_result": {"connection": "established"},
                "execution_time": datetime.utcnow().isoformat(),
            }
        )

        system_config = {
            "system_name": "CRM System",
            "endpoint": "https://crm.example.com/api",
            "auth": {"type": "api_key", "key": "test_key"},
        }

        result = await agent.integrate_external_system(
            system_config=system_config, integration_pattern="api_gateway"
        )

        assert result["status"] == "success"
        assert result["integration_type"] == "external_system"
        assert result["pattern"] == "api_gateway"
        assert result["connection_status"] == "established"

    @pytest.mark.asyncio
    async def test_orchestrate_infrastructure(self, agent):
        """Test infrastructure orchestration."""
        agent.skills_manager.automate_deployment_pipeline = AsyncMock(
            return_value={
                "status": "success",
                "deployment_result": {"deployed": True},
                "execution_time": datetime.utcnow().isoformat(),
            }
        )

        infrastructure_specs = {
            "environment": "production",
            "application_name": "test-app",
            "replicas": 3,
            "resources": {"cpu": "500m", "memory": "512Mi"},
        }

        result = await agent.orchestrate_infrastructure(
            infrastructure_specs=infrastructure_specs,
            orchestration_strategy="automated",
        )

        assert result["status"] == "success"
        assert result["orchestration_type"] == "infrastructure_automation"
        assert result["infrastructure_deployed"] is True

    @pytest.mark.asyncio
    async def test_manage_data_workflows(self, agent):
        """Test data workflow management."""
        agent.skills_manager.manage_data_pipelines = AsyncMock(
            return_value={
                "status": "success",
                "pipelines_created": 2,
                "execution_time": datetime.utcnow().isoformat(),
            }
        )

        workflow_config = {
            "transformations": [
                {"type": "filter", "expression": "value > 100"},
                {"type": "map", "expression": "value * 2"},
            ]
        }

        data_sources = [
            {"source_type": "database", "connection_string": "postgresql://..."},
            {"source_type": "api", "endpoint": "https://api.example.com/data"},
        ]

        data_targets = [{"target_type": "database", "table_name": "processed_data"}]

        result = await agent.manage_data_workflows(
            workflow_config=workflow_config,
            data_sources=data_sources,
            data_targets=data_targets,
        )

        assert result["status"] == "success"
        assert result["workflow_type"] == "data_pipeline_management"
        assert result["sources_configured"] == 2
        assert result["targets_configured"] == 1

    @pytest.mark.asyncio
    async def test_analyze_system_visually_architecture(self, agent):
        """Test visual system analysis for architecture."""
        agent.skills_manager.analyze_system_architecture_diagram = AsyncMock(
            return_value={
                "status": "success",
                "analysis_type": "system_architecture_visual_analysis",
                "execution_time": datetime.utcnow().isoformat(),
            }
        )

        visual_data = b"mock_image_data"

        result = await agent.analyze_system_visually(
            visual_data=visual_data, analysis_type="architecture"
        )

        assert result["status"] == "success"
        assert result["analysis_type"] == "visual_architecture_analysis"
        assert result["visual_processing"] == "completed"

    @pytest.mark.asyncio
    async def test_analyze_system_visually_network(self, agent):
        """Test visual system analysis for network topology."""
        agent.skills_manager.analyze_network_topology = AsyncMock(
            return_value={
                "status": "success",
                "analysis_type": "network_topology_analysis",
                "execution_time": datetime.utcnow().isoformat(),
            }
        )

        visual_data = b"mock_network_diagram_data"

        result = await agent.analyze_system_visually(
            visual_data=visual_data, analysis_type="network"
        )

        assert result["status"] == "success"
        assert result["analysis_type"] == "visual_network_analysis"

    @pytest.mark.asyncio
    async def test_analyze_system_visually_metrics(self, agent):
        """Test visual system analysis for metrics dashboard."""
        agent.skills_manager.monitor_dashboard_metrics = AsyncMock(
            return_value={
                "status": "success",
                "monitoring_type": "dashboard_visual_metrics",
                "execution_time": datetime.utcnow().isoformat(),
            }
        )

        visual_data = b"mock_dashboard_screenshot"

        result = await agent.analyze_system_visually(
            visual_data=visual_data, analysis_type="metrics"
        )

        assert result["status"] == "success"
        assert result["analysis_type"] == "visual_metrics_analysis"

    @pytest.mark.asyncio
    async def test_analyze_system_visually_invalid_type(self, agent):
        """Test visual analysis with invalid type."""
        visual_data = b"mock_data"

        with pytest.raises(NodeValidationError):
            await agent.analyze_system_visually(
                visual_data=visual_data, analysis_type="invalid_type"
            )

    @pytest.mark.asyncio
    async def test_provide_strategic_consultation(self, agent):
        """Test strategic consultation capability."""
        agent.skills_manager.provide_technical_consultation = AsyncMock(
            return_value={
                "status": "success",
                "consultation_type": "expert_technical_advisory",
                "execution_time": datetime.utcnow().isoformat(),
            }
        )

        consultation_request = {
            "topic": "microservices migration",
            "current_architecture": "monolithic",
            "constraints": {"timeline": "6 months", "budget": "500k"},
        }

        result = await agent.provide_strategic_consultation(
            consultation_request=consultation_request,
            expertise_area="systems_architecture",
        )

        assert result["status"] == "success"
        assert result["consultation_type"] == "strategic_technical_advisory"
        assert result["expertise_area"] == "systems_architecture"

    @pytest.mark.asyncio
    async def test_complexity_score_calculation(self, agent):
        """Test complexity score calculation logic."""
        # Low complexity
        low_complexity_data = {"simple": "request"}
        assert agent._calculate_complexity_score(low_complexity_data) == "low"

        # Medium complexity
        medium_complexity_data = {
            "integrations": ["api1", "api2"],
            "custom_config": True,
        }
        assert agent._calculate_complexity_score(medium_complexity_data) == "medium"

        # High complexity
        high_complexity_data = {
            "integrations": ["api1", "api2", "api3"],
            "custom_config": True,
            "real_time": True,
            "security_level": "high",
        }
        assert agent._calculate_complexity_score(high_complexity_data) == "high"

    @pytest.mark.asyncio
    async def test_risk_assessment(self, agent):
        """Test risk level assessment logic."""
        # Low risk
        assert agent._assess_risk_level("api_integration", {}) == "low-medium"

        # Medium-high risk (deployment)
        assert agent._assess_risk_level("deployment_automation", {}) == "medium-high"

        # Medium-high risk (production)
        assert (
            agent._assess_risk_level(
                "api_integration", {"production_environment": True}
            )
            == "medium-high"
        )

    @pytest.mark.asyncio
    async def test_health_check(self, agent):
        """Test agent health check functionality."""
        health_status = await agent._perform_health_check()

        assert "overall_status" in health_status
        assert "components" in health_status
        assert "last_check" in health_status
        assert agent._health_status in ["healthy", "degraded", "unhealthy", "error"]

    @pytest.mark.asyncio
    async def test_session_activity_recording(self, agent):
        """Test session activity recording."""
        initial_count = len(agent._session_history)

        # Record some activities
        for i in range(3):
            await agent._record_session_activity(
                f"test_request_{i}",
                {"status": "success", "execution_time": datetime.utcnow().isoformat()},
            )

        assert len(agent._session_history) == initial_count + 3

    @pytest.mark.asyncio
    async def test_get_agent_status(self, agent):
        """Test agent status retrieval."""
        status = await agent.get_agent_status()

        assert "agent_info" in status
        assert "operational_status" in status
        assert "capabilities" in status
        assert "performance_metrics" in status
        assert "session_activity" in status
        assert "configuration" in status

        assert status["agent_info"]["name"] == "NODE Systems Integration"
        assert status["agent_info"]["personality"] == "INTJ - The Architect"

    @pytest.mark.asyncio
    async def test_process_request_not_initialized(self):
        """Test processing request when agent is not initialized."""
        agent = NodeSystemsIntegrationAgent()

        with pytest.raises(NodeIntegrationError, match="Agent not initialized"):
            await agent.process_integration_request(
                request_type="api_integration", request_data={}, priority="medium"
            )

    @pytest.mark.asyncio
    async def test_unsupported_request_type(self, agent):
        """Test processing unsupported request type."""
        with pytest.raises(NodeValidationError, match="Unsupported request type"):
            await agent.process_integration_request(
                request_type="unsupported_type", request_data={}, priority="medium"
            )

    @pytest.mark.asyncio
    async def test_agent_cleanup(self, agent):
        """Test agent cleanup process."""
        assert agent._initialized is True

        await agent.cleanup()

        assert agent._initialized is False
        assert agent._health_status == "shutdown"

    @pytest.mark.asyncio
    async def test_create_node_agent_factory(self, mock_dependencies):
        """Test agent factory function."""
        with patch(
            "agents.backend.node.agent_optimized.create_node_dependencies",
            return_value=mock_dependencies,
        ):
            agent = await create_node_agent()

        assert isinstance(agent, NodeSystemsIntegrationAgent)
        assert agent._initialized is True

    @pytest.mark.asyncio
    async def test_create_node_agent_with_config(self, mock_dependencies):
        """Test agent factory with configuration override."""
        config_override = {"environment": "testing"}

        with patch(
            "agents.backend.node.agent_optimized.create_node_dependencies",
            return_value=mock_dependencies,
        ):
            agent = await create_node_agent(config_override)

        assert agent.config.environment == "testing"

    @pytest.mark.asyncio
    async def test_personality_enhancement_failure_handling(self, agent):
        """Test handling of personality enhancement failures."""
        # Mock personality adapter to fail
        agent.dependencies.personality_adapter.adapt_response = AsyncMock(
            side_effect=Exception("Mock error")
        )

        response = {"status": "success"}
        analysis = {"test": "data"}

        # Should handle the error gracefully and return original response
        enhanced_response = await agent._enhance_response_with_personality(
            response, analysis
        )

        assert enhanced_response["status"] == "success"
        # Should not have enhancement fields due to error
        assert "intj_enhancements" not in enhanced_response

    @pytest.mark.asyncio
    async def test_strategic_analysis_failure_handling(self, agent):
        """Test handling of strategic analysis failures."""
        # Mock Gemini client to fail
        agent.dependencies.vertex_ai_client.analyze_with_ai = AsyncMock(
            side_effect=Exception("Mock AI error")
        )

        analysis = await agent._analyze_request_strategically(
            "test_request", {"test": "data"}, "medium"
        )

        # Should return fallback analysis
        assert "error" in analysis
        assert analysis["fallback_analysis"] is True

    @pytest.mark.asyncio
    async def test_health_check_with_unhealthy_components(self, agent):
        """Test health check when components are unhealthy."""
        # Mock health check failure
        agent.dependencies.vertex_ai_client.health_check = AsyncMock(
            side_effect=Exception("Health check failed")
        )

        health_status = await agent._perform_health_check()

        # Should still return status with degraded/unhealthy state
        assert health_status["overall_status"] in ["degraded", "unhealthy", "error"]
