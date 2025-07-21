"""
Base ADK Agent Implementation
============================

This module provides the base class for all NGX agents, enforcing
consistent patterns and providing common functionality.
"""

from typing import Dict, Any, List, Optional, Set, Union, AsyncGenerator
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import time
import uuid
from functools import wraps

from pydantic import BaseModel, Field, validator
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from core.logging_config import get_logger
from core.personality.personality_adapter import PersonalityAdapter
from clients.vertex_ai.client import VertexAIClient
from core.exceptions import AgentError
from core.redis_pool import RedisPoolManager
from .exceptions import (
    AgentValidationError,
    AgentExecutionError,
    AgentTimeoutError,
    AgentConfigurationError
)
from .types import AgentType, AgentStatus, ResponseFormat, ConversationContext

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)


class AgentRequest(BaseModel):
    """Standard request format for all agents."""
    
    prompt: str = Field(..., description="The user's request or query")
    user_id: str = Field(..., description="Unique user identifier")
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    context: Optional[ConversationContext] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    streaming: bool = Field(default=False)
    timeout: Optional[int] = Field(default=30, ge=1, le=300)
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty")
        if len(v) > 10000:
            raise ValueError("Prompt exceeds maximum length of 10000 characters")
        return v.strip()


class AgentResponse(BaseModel):
    """Standard response format for all agents."""
    
    success: bool
    agent_id: str
    agent_name: str
    content: Union[str, Dict[str, Any]]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    processing_time: float
    tokens_used: Optional[int] = None
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BaseADKConfig(BaseModel):
    """Base configuration for ADK agents."""
    
    max_tokens: int = Field(default=2000, ge=1, le=8000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    timeout: int = Field(default=30, ge=1, le=300)
    cache_ttl: int = Field(default=3600, ge=0)
    enable_streaming: bool = True
    enable_caching: bool = True
    enable_monitoring: bool = True
    retry_attempts: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, ge=0.1, le=60.0)
    
    class Config:
        extra = "allow"


class BaseADKAgent(ABC):
    """
    Base class for all ADK agents.
    
    This class provides:
    - Standardized initialization
    - Common service injection
    - Consistent error handling
    - Automatic monitoring and logging
    - Request/response validation
    - Caching capabilities
    - State management
    """
    
    # Agent metadata (must be overridden by subclasses)
    agent_id: str = None
    agent_name: str = None
    agent_type: AgentType = AgentType.SPECIALIST
    agent_version: str = "1.0.0"
    agent_description: str = ""
    
    # Configuration class (can be overridden)
    config_class = BaseADKConfig
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        personality_type: str = "prime",
        debug: bool = False,
        **kwargs
    ):
        """Initialize the ADK agent with common services."""
        
        # Validate agent metadata
        if not self.agent_id or not self.agent_name:
            raise AgentConfigurationError(
                "Agent must define agent_id and agent_name class attributes"
            )
        
        # Initialize configuration
        config_data = config or {}
        config_data.update(kwargs)
        self.config = self.config_class(**config_data)
        
        # Debug mode
        self.debug = debug
        
        # Initialize services
        self._initialize_services(personality_type)
        
        # Agent state
        self._status = AgentStatus.READY
        self._initialized_at = datetime.utcnow()
        self._request_count = 0
        self._error_count = 0
        
        # Skills registry
        self._skills: Dict[str, Any] = {}
        self._initialize_skills()
        
        logger.info(
            f"Initialized {self.agent_name} (v{self.agent_version})",
            extra={
                "agent_id": self.agent_id,
                "config": self.config.dict(),
                "debug": self.debug
            }
        )
    
    def _initialize_services(self, personality_type: str):
        """Initialize common services."""
        try:
            # LLM Client
            self.llm_client = VertexAIClient()
            
            # Personality Adapter
            self.personality = PersonalityAdapter(personality_type)
            
            # Redis for caching and state
            self.redis_manager = RedisPoolManager()
            self.redis_client = self.redis_manager.get_connection()
            
            # Logger with agent context
            self.logger = get_logger(f"agent.{self.agent_id}")
            
        except Exception as e:
            raise AgentConfigurationError(f"Failed to initialize services: {str(e)}")
    
    def _initialize_skills(self):
        """Initialize agent-specific skills. Override in subclasses."""
        pass
    
    @abstractmethod
    async def _execute_core(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Core execution logic. Must be implemented by subclasses.
        
        This method should contain the main agent logic and return
        a dictionary with the results.
        """
        pass
    
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Main execution method with full lifecycle management.
        
        Handles validation, monitoring, error handling, and response formatting.
        """
        start_time = time.time()
        self._request_count += 1
        
        # Create span for monitoring
        with tracer.start_as_current_span(
            f"{self.agent_id}.execute",
            attributes={
                "agent.id": self.agent_id,
                "agent.name": self.agent_name,
                "user.id": request.user_id,
                "session.id": request.session_id
            }
        ) as span:
            try:
                # Validate request
                self._validate_request(request)
                
                # Pre-process
                request = await self._pre_process(request)
                
                # Check cache if enabled
                if self.config.enable_caching:
                    cached_result = await self._get_cached_result(request)
                    if cached_result:
                        span.set_attribute("cache.hit", True)
                        return self._create_response(
                            cached_result,
                            request,
                            time.time() - start_time
                        )
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    self._execute_core(request),
                    timeout=request.timeout or self.config.timeout
                )
                
                # Post-process
                result = await self._post_process(result, request)
                
                # Cache result if enabled
                if self.config.enable_caching:
                    await self._cache_result(request, result)
                
                # Create response
                response = self._create_response(
                    result,
                    request,
                    time.time() - start_time
                )
                
                span.set_status(Status(StatusCode.OK))
                return response
                
            except asyncio.TimeoutError:
                self._error_count += 1
                span.set_status(
                    Status(StatusCode.ERROR, "Execution timeout")
                )
                raise AgentTimeoutError(
                    f"Agent execution timed out after {request.timeout}s"
                )
                
            except AgentValidationError:
                self._error_count += 1
                span.set_status(
                    Status(StatusCode.ERROR, "Validation failed")
                )
                raise
                
            except Exception as e:
                self._error_count += 1
                span.record_exception(e)
                span.set_status(
                    Status(StatusCode.ERROR, str(e))
                )
                
                self.logger.error(
                    f"Agent execution error: {str(e)}",
                    extra={
                        "agent_id": self.agent_id,
                        "request_id": request.session_id,
                        "error_type": type(e).__name__
                    },
                    exc_info=True
                )
                
                raise AgentExecutionError(
                    f"Agent execution failed: {str(e)}"
                )
    
    async def stream_execute(
        self,
        request: AgentRequest
    ) -> AsyncGenerator[str, None]:
        """
        Streaming execution method for real-time responses.
        
        Override this method in subclasses to provide streaming support.
        """
        if not self.config.enable_streaming:
            raise AgentExecutionError("Streaming is not enabled for this agent")
        
        # Default implementation converts regular response to stream
        response = await self.execute(request)
        yield response.content if isinstance(response.content, str) else str(response.content)
    
    def _validate_request(self, request: AgentRequest):
        """Validate incoming request."""
        # Pydantic validation is automatic
        # Add custom validation here if needed
        
        if self._status != AgentStatus.READY:
            raise AgentValidationError(
                f"Agent is not ready. Current status: {self._status}"
            )
    
    async def _pre_process(self, request: AgentRequest) -> AgentRequest:
        """Pre-process request. Override for custom preprocessing."""
        # Add personality context
        if hasattr(self, 'personality'):
            personality_context = self.personality.get_context()
            request.metadata['personality_context'] = personality_context
        
        return request
    
    async def _post_process(
        self,
        result: Dict[str, Any],
        request: AgentRequest
    ) -> Dict[str, Any]:
        """Post-process result. Override for custom postprocessing."""
        return result
    
    def _create_response(
        self,
        result: Dict[str, Any],
        request: AgentRequest,
        processing_time: float
    ) -> AgentResponse:
        """Create standardized response."""
        return AgentResponse(
            success=True,
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            content=result.get('content', result),
            metadata={
                **result.get('metadata', {}),
                'request_count': self._request_count,
                'agent_version': self.agent_version
            },
            processing_time=processing_time,
            tokens_used=result.get('tokens_used'),
            session_id=request.session_id
        )
    
    async def _get_cached_result(
        self,
        request: AgentRequest
    ) -> Optional[Dict[str, Any]]:
        """Get cached result if available."""
        if not self.redis_client:
            return None
        
        cache_key = self._generate_cache_key(request)
        try:
            cached = await self.redis_client.get(cache_key)
            if cached:
                self.logger.debug(f"Cache hit for key: {cache_key}")
                return cached
        except Exception as e:
            self.logger.warning(f"Cache retrieval error: {str(e)}")
        
        return None
    
    async def _cache_result(
        self,
        request: AgentRequest,
        result: Dict[str, Any]
    ):
        """Cache result with TTL."""
        if not self.redis_client:
            return
        
        cache_key = self._generate_cache_key(request)
        try:
            await self.redis_client.setex(
                cache_key,
                self.config.cache_ttl,
                result
            )
            self.logger.debug(f"Cached result for key: {cache_key}")
        except Exception as e:
            self.logger.warning(f"Cache storage error: {str(e)}")
    
    def _generate_cache_key(self, request: AgentRequest) -> str:
        """Generate cache key for request."""
        # Simple implementation - override for custom logic
        import hashlib
        
        key_data = f"{self.agent_id}:{request.prompt}:{request.user_id}"
        return f"adk:cache:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def register_skill(self, name: str, skill_instance: Any):
        """Register a skill with the agent."""
        self._skills[name] = skill_instance
        self.logger.info(f"Registered skill: {name}")
    
    def get_skill(self, name: str) -> Any:
        """Get a registered skill by name."""
        if name not in self._skills:
            raise AgentExecutionError(f"Skill '{name}' not found")
        return self._skills[name]
    
    @property
    def status(self) -> AgentStatus:
        """Get current agent status."""
        return self._status
    
    @status.setter
    def status(self, value: AgentStatus):
        """Set agent status."""
        old_status = self._status
        self._status = value
        self.logger.info(
            f"Agent status changed: {old_status} -> {value}",
            extra={"agent_id": self.agent_id}
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        uptime = (datetime.utcnow() - self._initialized_at).total_seconds()
        error_rate = (
            self._error_count / self._request_count 
            if self._request_count > 0 
            else 0
        )
        
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self._status.value,
            "uptime_seconds": uptime,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": error_rate,
            "version": self.agent_version
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        checks = {
            "agent": True,
            "llm_client": False,
            "redis": False
        }
        
        # Check LLM client
        try:
            if hasattr(self.llm_client, 'health_check'):
                await self.llm_client.health_check()
            checks["llm_client"] = True
        except Exception as e:
            self.logger.warning(f"LLM client health check failed: {str(e)}")
        
        # Check Redis
        try:
            if self.redis_client:
                await self.redis_client.ping()
                checks["redis"] = True
        except Exception as e:
            self.logger.warning(f"Redis health check failed: {str(e)}")
        
        return {
            "healthy": all(checks.values()),
            "checks": checks,
            "metrics": self.get_metrics()
        }
    
    async def shutdown(self):
        """Graceful shutdown."""
        self.status = AgentStatus.SHUTTING_DOWN
        
        # Close connections
        if hasattr(self, 'redis_client') and self.redis_client:
            await self.redis_client.close()
        
        self.status = AgentStatus.STOPPED
        self.logger.info(f"Agent {self.agent_name} shutdown complete")