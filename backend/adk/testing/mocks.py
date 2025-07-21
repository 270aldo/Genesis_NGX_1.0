"""
Mock Implementations for ADK Testing
===================================

Mock implementations of common dependencies for testing.
"""

from typing import Dict, Any, List, Optional, AsyncGenerator
import asyncio
import json
from datetime import datetime

from ..core import BaseADKAgent, AgentRequest, AgentResponse
from ..core.types import AgentType


class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self, default_response: str = "Mock LLM response"):
        self.default_response = default_response
        self.call_count = 0
        self.last_prompt = None
        self.responses = []
        self._should_fail = False
        self._fail_after = None
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Mock generate method."""
        self.call_count += 1
        self.last_prompt = prompt
        
        # Simulate failure if configured
        if self._should_fail:
            raise Exception("Mock LLM failure")
        
        if self._fail_after and self.call_count > self._fail_after:
            raise Exception(f"Mock LLM failure after {self._fail_after} calls")
        
        # Return queued response or default
        if self.responses:
            response = self.responses.pop(0)
        else:
            response = self.default_response
        
        return {
            "content": response,
            "tokens_used": len(response.split()),
            "model": "mock-model",
            "finish_reason": "stop"
        }
    
    async def stream_generate(
        self,
        prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Mock streaming generation."""
        self.call_count += 1
        self.last_prompt = prompt
        
        # Stream response word by word
        words = self.default_response.split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.01)  # Simulate streaming delay
    
    def set_response(self, response: str):
        """Set the next response."""
        self.responses.append(response)
    
    def set_responses(self, responses: List[str]):
        """Set multiple responses."""
        self.responses.extend(responses)
    
    def fail_next(self):
        """Make the next call fail."""
        self._should_fail = True
    
    def fail_after(self, n: int):
        """Fail after n calls."""
        self._fail_after = n
    
    async def health_check(self) -> bool:
        """Mock health check."""
        return not self._should_fail


class MockRedisClient:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.call_count = 0
        self._should_fail = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Mock get method."""
        self.call_count += 1
        if self._should_fail:
            raise Exception("Mock Redis failure")
        return self.data.get(key)
    
    async def set(self, key: str, value: Any) -> bool:
        """Mock set method."""
        self.call_count += 1
        if self._should_fail:
            raise Exception("Mock Redis failure")
        self.data[key] = value
        return True
    
    async def setex(self, key: str, ttl: int, value: Any) -> bool:
        """Mock setex method."""
        self.call_count += 1
        if self._should_fail:
            raise Exception("Mock Redis failure")
        self.data[key] = value
        # TTL is ignored in mock
        return True
    
    async def delete(self, *keys: str) -> int:
        """Mock delete method."""
        self.call_count += 1
        if self._should_fail:
            raise Exception("Mock Redis failure")
        
        deleted = 0
        for key in keys:
            if key in self.data:
                del self.data[key]
                deleted += 1
        return deleted
    
    async def exists(self, key: str) -> bool:
        """Mock exists method."""
        self.call_count += 1
        return key in self.data
    
    async def ping(self) -> bool:
        """Mock ping method."""
        return not self._should_fail
    
    def fail_next(self):
        """Make the next call fail."""
        self._should_fail = True
    
    def clear(self):
        """Clear all data."""
        self.data.clear()


class MockAgent(BaseADKAgent):
    """Mock agent for testing multi-agent scenarios."""
    
    agent_id = "mock_agent"
    agent_name = "Mock Agent"
    agent_type = AgentType.SPECIALIST
    
    def __init__(self, response: str = "Mock agent response", **kwargs):
        super().__init__(**kwargs)
        self.mock_response = response
        self.execution_count = 0
    
    async def _execute_core(self, request: AgentRequest) -> Dict[str, Any]:
        """Mock execution."""
        self.execution_count += 1
        
        # Simulate some processing time
        await asyncio.sleep(0.01)
        
        return {
            "content": self.mock_response,
            "metadata": {
                "agent_id": self.agent_id,
                "execution_count": self.execution_count
            },
            "tokens_used": len(self.mock_response.split())
        }


class MockSkill:
    """Mock skill for testing."""
    
    def __init__(self, skill_id: str = "mock_skill", result: Any = "Mock skill result"):
        self.skill_id = skill_id
        self.skill_name = f"Mock {skill_id}"
        self.result = result
        self.execution_count = 0
        self._should_fail = False
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mock skill."""
        self.execution_count += 1
        
        if self._should_fail:
            raise Exception(f"Mock skill {self.skill_id} failure")
        
        # Simulate processing
        await asyncio.sleep(0.01)
        
        return {
            "result": self.result,
            "skill_id": self.skill_id,
            "execution_count": self.execution_count,
            "input_received": input_data
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Mock input validation."""
        return True
    
    def fail_next(self):
        """Make the next execution fail."""
        self._should_fail = True


class MockPersonalityAdapter:
    """Mock personality adapter for testing."""
    
    def __init__(self, personality_type: str = "prime"):
        self.personality_type = personality_type
    
    def get_context(self) -> Dict[str, Any]:
        """Get mock personality context."""
        contexts = {
            "prime": {
                "style": "professional",
                "tone": "executive",
                "detail_level": "concise"
            },
            "longevity": {
                "style": "supportive",
                "tone": "encouraging",
                "detail_level": "comprehensive"
            }
        }
        return contexts.get(self.personality_type, contexts["prime"])
    
    def adapt_response(self, response: str) -> str:
        """Mock response adaptation."""
        if self.personality_type == "prime":
            return f"Executive Summary: {response}"
        else:
            return f"Your Journey: {response}"


class MockMetricsCollector:
    """Mock metrics collector for testing."""
    
    def __init__(self):
        self.metrics = {
            "requests": 0,
            "errors": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_duration": 0.0
        }
    
    def record_request(self, duration: float, success: bool = True):
        """Record mock request."""
        self.metrics["requests"] += 1
        self.metrics["total_duration"] += duration
        if not success:
            self.metrics["errors"] += 1
    
    def record_error(self, error_type: str):
        """Record mock error."""
        self.metrics["errors"] += 1
    
    def record_cache_hit(self):
        """Record mock cache hit."""
        self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """Record mock cache miss."""
        self.metrics["cache_misses"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get mock metrics."""
        return self.metrics.copy()