"""
Base NGX Agent Class
====================

This module provides a base class for all NGX agents, consolidating
common functionality and reducing code duplication across agents.

Features:
- Automatic initialization of common services
- Standardized configuration management
- Built-in telemetry and monitoring
- Consistent error handling
- Modular skill system
"""

import asyncio
import json
from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.base.adk_agent import ADKAgent
from clients.vertex_ai.client import VertexAIClient
from core.exceptions import AgentError
from core.logging_config import get_logger
from core.personality.personality_adapter import PersonalityAdapter
from tools.mcp_toolkit import MCPToolkit

logger = get_logger(__name__)


class BaseNGXAgent(ADKAgent):
    """
    Base class for all NGX agents.

    Provides common functionality including:
    - Service initialization
    - Configuration management
    - Skill registration and execution
    - Caching and state management
    - Error handling and recovery
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        personality_type: str = "prime",
        model_id: Optional[str] = None,
        temperature: float = 0.7,
        mcp_toolkit: Optional[MCPToolkit] = None,
        **kwargs,
    ):
        """
        Initialize base NGX agent.

        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            agent_type: Type of agent (training, nutrition, wellness, etc.)
            personality_type: Personality profile (prime, longevity)
            model_id: AI model to use
            temperature: Model temperature for generation
            mcp_toolkit: MCP toolkit instance
            **kwargs: Additional agent-specific parameters
        """
        # Initialize parent ADKAgent with all required parameters
        # Extract ADK-specific parameters from kwargs or use defaults
        name = kwargs.pop("name", agent_name)
        description = kwargs.pop("description", f"{agent_name} - {agent_type} agent")
        instruction = kwargs.pop(
            "instruction", f"You are {agent_name}, a specialized {agent_type} agent."
        )

        super().__init__(
            agent_id=agent_id,
            name=name,
            description=description,
            model=model_id or "gemini-1.5-flash",
            instruction=instruction,
            **kwargs,
        )

        # Core agent properties
        self.agent_id = agent_id
        self.name = agent_name
        self.agent_type = agent_type
        self.personality = personality_type
        self.temperature = temperature

        # Initialize services
        self._initialize_core_services(mcp_toolkit)

        # Skills registry
        self._skills: Dict[str, Any] = {}
        self._skill_metadata: Dict[str, Dict[str, Any]] = {}

        # State management
        self._state: Dict[str, Any] = {
            "initialized_at": datetime.now().isoformat(),
            "total_interactions": 0,
            "last_interaction": None,
            "active_sessions": {},
        }

        # Performance metrics
        self._metrics = {
            "response_times": [],
            "error_count": 0,
            "success_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        logger.info(
            f"Initialized {agent_name} ({agent_id}) with personality {personality_type}"
        )

    # ==================== Abstract Methods ====================

    @abstractmethod
    def get_agent_capabilities(self) -> List[str]:
        """Get list of agent capabilities. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_agent_description(self) -> str:
        """Get agent description. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def process_user_request(
        self, request: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process user request. Must be implemented by subclasses."""
        pass

    # ==================== Core Services Initialization ====================

    def _initialize_core_services(self, mcp_toolkit: Optional[MCPToolkit]) -> None:
        """Initialize core services used by all agents."""
        try:
            # MCP Toolkit
            self.mcp_toolkit = mcp_toolkit or MCPToolkit()

            # Vertex AI Client
            self.vertex_client = VertexAIClient()

            # Personality Adapter
            self.personality_adapter = PersonalityAdapter()

            # Redis for caching
            from core.redis_pool import redis_pool_manager

            self.redis_manager = redis_pool_manager

            # Initialize agent-specific services
            self._initialize_agent_services()

            logger.info(f"Core services initialized for {self.agent_id}")

        except Exception as e:
            logger.error(f"Error initializing core services: {e}")
            raise AgentError(f"Failed to initialize agent services: {str(e)}")

    def _initialize_agent_services(self) -> None:
        """Initialize agent-specific services. Override in subclasses if needed."""
        pass

    # ==================== Skill Management ====================

    def register_skill(
        self,
        skill_name: str,
        skill_instance: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a skill with the agent.

        Args:
            skill_name: Unique skill identifier
            skill_instance: Skill instance
            metadata: Optional skill metadata
        """
        self._skills[skill_name] = skill_instance

        # Merge provided metadata with defaults
        default_metadata = {
            "registered_at": datetime.now().isoformat(),
            "execution_count": 0,
            "last_executed": None,
        }

        if metadata:
            default_metadata.update(metadata)

        self._skill_metadata[skill_name] = default_metadata

        logger.info(f"Registered skill '{skill_name}' for agent {self.agent_id}")

    async def execute_skill(self, skill_name: str, **kwargs) -> Any:
        """
        Execute a registered skill.

        Args:
            skill_name: Name of skill to execute
            **kwargs: Arguments to pass to skill

        Returns:
            Skill execution result
        """
        if skill_name not in self._skills:
            raise AgentError(f"Skill '{skill_name}' not found")

        try:
            # Update metadata
            self._skill_metadata[skill_name]["execution_count"] += 1
            self._skill_metadata[skill_name][
                "last_executed"
            ] = datetime.now().isoformat()

            # Execute skill
            skill = self._skills[skill_name]

            # Handle both sync and async skills
            if asyncio.iscoroutinefunction(skill.execute):
                result = await skill.execute(**kwargs)
            else:
                result = skill.execute(**kwargs)

            return result

        except Exception as e:
            logger.error(f"Error executing skill '{skill_name}': {e}")
            raise AgentError(f"Skill execution failed: {str(e)}")

    def get_available_skills(self) -> List[Dict[str, Any]]:
        """Get list of available skills with metadata."""
        return [
            {
                "name": name,
                "metadata": metadata,
                "has_execute": hasattr(self._skills[name], "execute"),
            }
            for name, metadata in self._skill_metadata.items()
        ]

    # ==================== Caching ====================

    async def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available.

        Args:
            cache_key: Cache key

        Returns:
            Cached response or None
        """
        if not self.redis_manager or not await self.redis_manager.is_connected():
            self._metrics["cache_misses"] += 1
            return None

        try:
            cached = await self.redis_manager.get(f"{self.agent_id}:{cache_key}")
            if cached:
                self._metrics["cache_hits"] += 1
                # Use json.loads for safe deserialization instead of eval()
                return json.loads(cached)
            else:
                self._metrics["cache_misses"] += 1
                return None

        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
            self._metrics["cache_misses"] += 1
            return None

    async def cache_response(
        self, cache_key: str, response: Dict[str, Any], ttl: int = 3600
    ) -> None:
        """
        Cache a response.

        Args:
            cache_key: Cache key
            response: Response to cache
            ttl: Time to live in seconds
        """
        if not self.redis_manager or not await self.redis_manager.is_connected():
            return

        try:
            await self.redis_manager.set(
                f"{self.agent_id}:{cache_key}", json.dumps(response), ex=ttl
            )
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")

    # ==================== State Management ====================

    def update_state(self, key: str, value: Any) -> None:
        """Update agent state."""
        self._state[key] = value
        self._state["last_updated"] = datetime.now().isoformat()

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get agent state value."""
        return self._state.get(key, default)

    async def persist_state(self) -> None:
        """Persist agent state to storage."""
        if self.redis_manager and await self.redis_manager.is_connected():
            try:
                await self.redis_manager.set(
                    f"{self.agent_id}:state", str(self._state), ex=86400  # 24 hours
                )
            except Exception as e:
                logger.error(f"Error persisting state: {e}")

    async def restore_state(self) -> None:
        """Restore agent state from storage."""
        if self.redis_manager and await self.redis_manager.is_connected():
            try:
                stored_state = await self.redis_manager.get(f"{self.agent_id}:state")
                if stored_state:
                    self._state.update(
                        eval(stored_state)
                    )  # Safe in controlled environment
            except Exception as e:
                logger.error(f"Error restoring state: {e}")

    # ==================== Performance Metrics ====================

    def record_metric(self, metric_name: str, value: Any) -> None:
        """Record a performance metric."""
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []

        if isinstance(self._metrics[metric_name], list):
            self._metrics[metric_name].append(value)
            # Keep only last 1000 entries
            if len(self._metrics[metric_name]) > 1000:
                self._metrics[metric_name] = self._metrics[metric_name][-1000:]
        elif isinstance(self._metrics[metric_name], (int, float)):
            self._metrics[metric_name] += value

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics."""
        summary = {
            "agent_id": self.agent_id,
            "uptime_hours": (
                datetime.now() - datetime.fromisoformat(self._state["initialized_at"])
            ).total_seconds()
            / 3600,
            "total_interactions": self._state["total_interactions"],
            "error_rate": (
                self._metrics["error_count"]
                / max(self._metrics["error_count"] + self._metrics["success_count"], 1)
            ),
            "cache_hit_rate": (
                self._metrics["cache_hits"]
                / max(self._metrics["cache_hits"] + self._metrics["cache_misses"], 1)
            ),
        }

        # Calculate average response time
        if self._metrics["response_times"]:
            summary["avg_response_time"] = sum(self._metrics["response_times"]) / len(
                self._metrics["response_times"]
            )

        return summary

    # ==================== Error Handling ====================

    async def handle_error(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle errors with graceful fallback.

        Args:
            error: The exception that occurred
            context: Error context

        Returns:
            Error response
        """
        self._metrics["error_count"] += 1

        logger.error(
            f"Error in {self.agent_id}: {str(error)}", extra={"context": context}
        )

        # Get personalized error message
        error_personality = self.personality_adapter.get_error_response(
            self.personality, str(error)
        )

        return {
            "success": False,
            "error": {
                "message": error_personality,
                "type": error.__class__.__name__,
                "agent": self.agent_id,
            },
            "fallback": await self.get_fallback_response(context),
        }

    async def get_fallback_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get fallback response when primary processing fails.
        Override in subclasses for agent-specific fallbacks.
        """
        return {
            "message": "I encountered an issue processing your request. Please try again or contact support.",
            "suggestions": [
                "Try rephrasing your request",
                "Check your input data",
                "Contact support if the issue persists",
            ],
        }

    # ==================== Lifecycle Management ====================

    async def startup(self) -> None:
        """Perform startup tasks."""
        logger.info(f"Starting up agent {self.agent_id}")

        # Restore state
        await self.restore_state()

        # Initialize agent-specific resources
        await self._agent_startup()

        # Update state
        self.update_state("status", "active")
        self.update_state("started_at", datetime.now().isoformat())

    async def shutdown(self) -> None:
        """Perform shutdown tasks."""
        logger.info(f"Shutting down agent {self.agent_id}")

        # Persist state
        await self.persist_state()

        # Clean up agent-specific resources
        await self._agent_shutdown()

        # Update state
        self.update_state("status", "shutdown")
        self.update_state("stopped_at", datetime.now().isoformat())

    async def _agent_startup(self) -> None:
        """Agent-specific startup tasks. Override in subclasses."""
        pass

    async def _agent_shutdown(self) -> None:
        """Agent-specific shutdown tasks. Override in subclasses."""
        pass

    # ==================== Health Check ====================

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        health_status = {
            "agent_id": self.agent_id,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {},
        }

        # Check core services
        try:
            # Vertex AI
            health_status["checks"]["vertex_ai"] = self.vertex_client is not None

            # Redis
            if self.redis_manager:
                health_status["checks"][
                    "redis"
                ] = await self.redis_manager.is_connected()
            else:
                health_status["checks"]["redis"] = False

            # Skills
            health_status["checks"]["skills_loaded"] = len(self._skills)

            # Determine overall health
            if not all(health_status["checks"].values()):
                health_status["status"] = "degraded"

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)

        return health_status
