"""
Real Orchestrator Client for Beta Validation Tests

This client uses the actual GENESIS orchestrator system for testing
instead of mocks, providing accurate validation of system behavior.
"""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.schemas.chat import ChatRequest, ChatResponse, AgentResponse
from agents.orchestrator.agent import NGXNexusOrchestrator
from agents.base.agent_registry import AgentRegistry
from infrastructure.adapters.state_manager_adapter import StateManagerAdapter
from infrastructure.adapters.a2a_adapter import A2AAdapter
from clients.vertex_ai.client import VertexAIClient
from core.logging_config import get_logger
from core.settings import Settings
from core.redis_pool import RedisPoolManager
import os

logger = get_logger(__name__)


class RealOrchestratorClient:
    """Test client that uses the real orchestrator system"""
    
    def __init__(self, test_mode: bool = True, use_real_ai: bool = False):
        """
        Initialize the real orchestrator client for testing
        
        Args:
            test_mode: If True, uses test configurations and in-memory storage
            use_real_ai: If True, uses real AI models (costs money!)
        """
        self.test_mode = test_mode
        self.use_real_ai = use_real_ai
        self.orchestrator: Optional[NGXNexusOrchestrator] = None
        self.state_manager: Optional[StateManagerAdapter] = None
        self.a2a_adapter: Optional[A2AAdapter] = None
        self.settings = Settings()
        self._initialized = False
        self._original_env = {}
        
        # Configure for test mode
        if test_mode:
            self._setup_test_environment()
        
    async def initialize(self):
        """Initialize all required components for the orchestrator"""
        if self._initialized:
            return
            
        try:
            logger.info("Initializing Real Orchestrator Client for testing...")
            
            # 1. Initialize state manager (use in-memory for tests)
            if self.test_mode:
                # Create test state manager that doesn't persist
                self.state_manager = StateManagerAdapter()
                await self.state_manager.initialize()
                logger.info("Initialized test state manager (in-memory)")
            else:
                # Use real state manager
                from infrastructure.adapters.state_manager_adapter import state_manager_adapter
                self.state_manager = state_manager_adapter
                await self.state_manager.initialize()
                
            # 2. Initialize A2A adapter
            if self.test_mode:
                # Create test A2A adapter
                self.a2a_adapter = A2AAdapter()
                await self.a2a_adapter.start()
                logger.info("Initialized test A2A adapter")
            else:
                # Use real A2A adapter
                from infrastructure.adapters.a2a_adapter import a2a_adapter
                self.a2a_adapter = a2a_adapter
                
            # 3. Register test agents if in test mode
            if self.test_mode:
                await self._register_test_agents()
                
            # 4. Initialize orchestrator with proper config
            http_a2a_target_url = f"http://{self.settings.A2A_HOST}:{self.settings.port}"
            
            # Create orchestrator config for testing
            from agents.orchestrator.config import OrchestratorConfig
            orchestrator_config = OrchestratorConfig(
                agent_id="orchestrator",
                agent_name="NEXUS",
                agent_type="orchestrator",
                model_id="gemini-1.5-flash-002" if not self.use_real_ai else "gemini-1.5-pro-002",
                temperature=0.7,
                a2a_server_url=http_a2a_target_url
            )
            
            self.orchestrator = NGXNexusOrchestrator(
                config=orchestrator_config,
                a2a_server_url=http_a2a_target_url,
                state_manager=self.state_manager
            )
            
            # 5. Connect orchestrator if needed
            if not self.orchestrator.is_connected:
                await self.orchestrator.connect()
                # Give it a moment to establish connection
                await asyncio.sleep(0.5)
                
            self._initialized = True
            logger.info("Real Orchestrator Client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Real Orchestrator Client: {e}")
            raise
            
    async def _register_test_agents(self):
        """Register minimal test agents for validation"""
        logger.info("Registering test agents...")
        
        # Create minimal test agents that the orchestrator might call
        from agents.base.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def __init__(self, agent_id: str, name: str):
                super().__init__(agent_id=agent_id, name=name, description=f"Test {name}")
                
            async def _generate_individual_response(self, user_input: str, **kwargs):
                return {
                    "status": "success",
                    "response": f"Test response from {self.name}",
                    "agent_id": self.agent_id,
                    "agent_name": self.name
                }
        
        # Register common agents that might be called
        registry = AgentRegistry.get_instance()
        
        test_agents = [
            ("elite_training_strategist", "BLAZE"),
            ("precision_nutrition_architect", "SAGE"),
            ("motivation_behavior_coach", "SPARK"),
            ("female_wellness_coach", "LUNA"),
            ("progress_tracker", "STELLA")
        ]
        
        for agent_id, agent_name in test_agents:
            agent = TestAgent(agent_id, agent_name)
            registry.register(agent_id, agent)
            
            # Also register with A2A adapter
            self.a2a_adapter.register_agent(agent_id, {
                "name": agent_name,
                "description": f"Test {agent_name} agent",
                "message_callback": agent._generate_individual_response
            })
            
        logger.info(f"Registered {len(test_agents)} test agents")
        
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a message using the real orchestrator
        
        Args:
            request: ChatRequest object with user message
            
        Returns:
            ChatResponse from the orchestrator
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Extract necessary fields
            user_id = request.user_id or "test-user"
            session_id = request.session_id or "test-session"
            context = request.context or {}
            
            logger.info(f"Processing message through real orchestrator: {request.text[:50]}...")
            
            # Call the orchestrator's process_user_request method
            result = await self.orchestrator.process_user_request(
                request=request.text,
                context={
                    **context,
                    "user_id": user_id,
                    "session_id": session_id,
                    "metadata": request.metadata or {}
                }
            )
            
            # Extract response data
            response_text = result.get("response", "")
            agents_used = result.get("agents_used", ["NEXUS"])
            metadata = result.get("metadata", {})
            
            # Build agent responses
            agent_responses = []
            for agent_data in result.get("agent_responses", []):
                agent_responses.append(
                    AgentResponse(
                        agent_id=agent_data.get("agent_id", ""),
                        agent_name=agent_data.get("agent_name", ""),
                        response=agent_data.get("response", ""),
                        confidence=agent_data.get("confidence", 1.0),
                        artifacts=agent_data.get("artifacts", [])
                    )
                )
            
            # Create ChatResponse
            response = ChatResponse(
                response=response_text,
                session_id=session_id,
                agents_used=agents_used,
                agent_responses=agent_responses,
                metadata={
                    **metadata,
                    "real_orchestrator": True,
                    "test_mode": self.test_mode
                }
            )
            
            logger.info(f"Successfully processed message. Agents used: {agents_used}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Return error response that matches expected format
            return ChatResponse(
                response=f"Error processing request: {str(e)}",
                session_id=request.session_id or "error-session",
                agents_used=["NEXUS"],
                agent_responses=[],
                metadata={
                    "error": str(e),
                    "real_orchestrator": True,
                    "test_mode": self.test_mode
                }
            )
            
    async def cleanup(self):
        """Clean up resources after testing"""
        logger.info("Cleaning up Real Orchestrator Client...")
        
        try:
            # Disconnect orchestrator
            if self.orchestrator and self.orchestrator.is_connected:
                await self.orchestrator.disconnect()
                
            # Stop A2A adapter if test mode
            if self.test_mode and self.a2a_adapter:
                await self.a2a_adapter.stop()
                
            # Clear test agents from registry
            if self.test_mode:
                registry = AgentRegistry.get_instance()
                registry._agents.clear()
                
            self._initialized = False
            logger.info("Cleanup completed")
            
            # Restore original environment
            if self._original_env:
                for key, value in self._original_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            
    @property
    def is_connected(self) -> bool:
        """Check if orchestrator is connected"""
        return self.orchestrator and self.orchestrator.is_connected
        
    async def connect(self):
        """Ensure orchestrator is connected"""
        if not self._initialized:
            await self.initialize()
            
    def _setup_test_environment(self):
        """Set up test environment variables"""
        # Store original values
        test_env_vars = {
            "REDIS_URL": "redis://localhost:6379/15",  # Use test DB
            "GENESIS_ENV": "test",
            "LOG_LEVEL": "INFO",
            "VERTEX_AI_USE_MOCK": "true" if not self.use_real_ai else "false"
        }
        
        for key, value in test_env_vars.items():
            self._original_env[key] = os.environ.get(key)
            os.environ[key] = value
            
        logger.info("Test environment configured")
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the orchestrator"""
        if not self._initialized:
            return {"status": "not_initialized", "healthy": False}
            
        try:
            # Check orchestrator connection
            if not self.is_connected:
                return {"status": "disconnected", "healthy": False}
                
            # Try a simple test message
            test_request = ChatRequest(
                text="Test health check",
                user_id="health-check",
                session_id="health-check"
            )
            
            response = await self.process_message(test_request)
            
            return {
                "status": "healthy",
                "healthy": True,
                "orchestrator_connected": self.is_connected,
                "test_mode": self.test_mode,
                "use_real_ai": self.use_real_ai,
                "response_received": bool(response.response)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "healthy": False,
                "error": str(e)
            }