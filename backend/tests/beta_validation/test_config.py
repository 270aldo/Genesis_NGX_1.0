"""
Test Configuration for Beta Validation

Provides test-specific configurations and utilities for running
beta validation tests with the real orchestrator.
"""

import os
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock
import asyncio

from core.settings_lazy import settings as _
from core.settings import Settings
from clients.vertex_ai.client import VertexAIClient
from core.logging_config import get_logger

logger = get_logger(__name__)


class TestVertexAIClient(VertexAIClient):
    """Test version of VertexAI client that returns predictable responses"""
    
    def __init__(self, use_real: bool = False):
        """
        Initialize test Vertex AI client
        
        Args:
            use_real: If True, uses real Vertex AI (costs money!)
        """
        self.use_real = use_real
        if use_real:
            super().__init__()
        else:
            # Don't initialize parent to avoid real API calls
            self.model = None
            self._mock_responses = self._create_mock_responses()
            
    def _create_mock_responses(self) -> Dict[str, str]:
        """Create mock responses for common patterns"""
        return {
            "intent_analysis": """
            {
                "primary_intent": "fitness_guidance",
                "confidence": 0.85,
                "recommended_agents": ["BLAZE", "SAGE"],
                "urgency": "normal",
                "reasoning": "User is asking about fitness guidance"
            }
            """,
            "response_synthesis": """
            Based on the analysis from our specialized agents, here's a comprehensive 
            response to your query. Our fitness expert BLAZE and nutrition specialist 
            SAGE have provided tailored guidance for your needs.
            """,
            "general": "This is a test response from the mock Vertex AI client."
        }
    
    async def generate_text_async(self, prompt: str, **kwargs) -> str:
        """Generate text response (mock or real)"""
        if self.use_real:
            return await super().generate_text_async(prompt, **kwargs)
            
        # Analyze prompt to return appropriate mock response
        prompt_lower = prompt.lower()
        
        if "intent" in prompt_lower and "analysis" in prompt_lower:
            return self._mock_responses["intent_analysis"]
        elif "synthesis" in prompt_lower or "combine" in prompt_lower:
            return self._mock_responses["response_synthesis"]
        else:
            return self._mock_responses["general"]
            
    async def generate_structured_output_async(self, prompt: str, schema: Any, **kwargs) -> Dict[str, Any]:
        """Generate structured output (mock or real)"""
        if self.use_real:
            return await super().generate_structured_output_async(prompt, schema, **kwargs)
            
        # Return mock structured data based on prompt
        if "intent" in prompt.lower():
            return {
                "primary_intent": "general_query",
                "confidence": 0.75,
                "recommended_agents": ["NEXUS"],
                "urgency": "normal"
            }
        else:
            return {"response": "Mock structured output"}


class TestSettings:
    """Test-specific settings for beta validation"""
    
    def __init__(self):
        # Basic settings
        self.env = "test"
        self.debug = True
        self.telemetry_enabled = False
        self.enable_budgets = False
        
        # Database settings
        self.use_test_database = True
        self.test_database_url = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
        
        # Service settings
        self.disable_external_services = True
        
        # Timeout settings
        self.a2a_timeout = 5
        self.orchestrator_timeout = 10
        
        # Add any other settings needed by tests
        self.gcp_project_id = "your-gcp-project-id"
        self.gcp_region = "us-central1"


class TestEnvironment:
    """Manages test environment setup and teardown"""
    
    def __init__(self, use_real_ai: bool = False):
        """
        Initialize test environment
        
        Args:
            use_real_ai: If True, uses real AI services (costs money!)
        """
        self.use_real_ai = use_real_ai
        self.original_settings = None
        self.test_settings = None
        self.vertex_client = None
        
    async def setup(self):
        """Set up test environment"""
        logger.info("Setting up test environment...")
        
        # 1. Replace settings with test settings
        self.test_settings = TestSettings()
        
        # 2. Create test Vertex AI client
        self.vertex_client = TestVertexAIClient(use_real=self.use_real_ai)
        
        # 3. Set up test directories if needed
        test_dirs = ["./test_logs", "./test_cache", "./test_reports"]
        for dir_path in test_dirs:
            os.makedirs(dir_path, exist_ok=True)
            
        logger.info("Test environment setup complete")
        
    async def teardown(self):
        """Clean up test environment"""
        logger.info("Tearing down test environment...")
        
        # Clean up test directories
        import shutil
        test_dirs = ["./test_logs", "./test_cache", "./test_reports"]
        for dir_path in test_dirs:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                
        logger.info("Test environment teardown complete")
        
    def get_test_context(self, scenario: str = "default") -> Dict[str, Any]:
        """Get test context for a specific scenario"""
        base_context = {
            "test_mode": True,
            "scenario": scenario,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Add scenario-specific context
        scenario_contexts = {
            "frustrated_user": {
                "user_emotion": "frustrated",
                "interaction_count": 5,
                "previous_issues": ["plan_not_working", "too_complicated"]
            },
            "angry_user": {
                "user_emotion": "angry", 
                "interaction_count": 10,
                "escalation_level": "high"
            },
            "confused_user": {
                "user_emotion": "confused",
                "interaction_count": 3,
                "topic": "technology"
            },
            "depressed_user": {
                "user_emotion": "depressed",
                "interaction_count": 7,
                "sensitive_topic": True
            }
        }
        
        if scenario in scenario_contexts:
            base_context.update(scenario_contexts[scenario])
            
        return base_context


def create_mock_agent_registry() -> Dict[str, Any]:
    """Create a mock agent registry for testing"""
    mock_agents = {}
    
    agent_configs = [
        ("elite_training_strategist", "BLAZE", "Elite Training Strategist"),
        ("precision_nutrition_architect", "SAGE", "Precision Nutrition Architect"),
        ("motivation_behavior_coach", "SPARK", "Motivation & Behavior Coach"),
        ("female_wellness_coach", "LUNA", "Female Wellness Coach"),
        ("progress_tracker", "STELLA", "Progress Tracker"),
        ("nova_biohacking_innovator", "NOVA", "Biohacking Innovator"),
        ("wave_performance_analytics", "WAVE", "Performance Analytics"),
        ("code_genetic_specialist", "CODE", "Genetic Specialist")
    ]
    
    for agent_id, name, description in agent_configs:
        mock_agent = Mock()
        mock_agent.agent_id = agent_id
        mock_agent.name = name
        mock_agent.description = description
        mock_agent.process_user_request = AsyncMock(return_value={
            "success": True,
            "agent": agent_id,
            "response": f"Test response from {name}",
            "metadata": {"test": True}
        })
        mock_agents[agent_id] = mock_agent
        
    return mock_agents