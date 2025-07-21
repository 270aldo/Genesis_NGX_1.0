"""
Type Definitions for NGX ADK
============================

This module defines common types, enums, and protocols used
throughout the ADK framework.
"""

from typing import Dict, Any, List, Optional, Protocol, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Types of agents in the system."""
    ORCHESTRATOR = "orchestrator"
    SPECIALIST = "specialist"
    BACKEND = "backend"
    FRONTEND = "frontend"
    HYBRID = "hybrid"


class AgentStatus(str, Enum):
    """Agent operational status."""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"


class ResponseFormat(str, Enum):
    """Supported response formats."""
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    STRUCTURED = "structured"


class Priority(str, Enum):
    """Request priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ConversationContext(BaseModel):
    """Context for maintaining conversation state."""
    
    conversation_id: str = Field(..., description="Unique conversation identifier")
    messages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Previous messages in the conversation"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        default=None,
        description="User profile information"
    )
    session_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Session-specific data"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def get_recent_messages(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get the n most recent messages."""
        return self.messages[-n:] if self.messages else []
    
    def clear_old_messages(self, keep_last: int = 50):
        """Remove old messages keeping only the most recent ones."""
        if len(self.messages) > keep_last:
            self.messages = self.messages[-keep_last:]


class AgentMetadata(BaseModel):
    """Metadata about an agent."""
    
    agent_id: str
    agent_name: str
    agent_type: AgentType
    version: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    supported_languages: List[str] = Field(default=["en"])
    max_tokens: int = 2000
    temperature_range: tuple[float, float] = (0.0, 2.0)
    streaming_enabled: bool = True
    caching_enabled: bool = True
    rate_limit: Optional[int] = None  # requests per minute
    
    class Config:
        use_enum_values = True


class SkillMetadata(BaseModel):
    """Metadata about an agent skill."""
    
    skill_id: str
    skill_name: str
    description: str
    category: str
    required_permissions: List[str] = Field(default_factory=list)
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        extra = "allow"


class ExecutionContext(BaseModel):
    """Context for agent execution."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    correlation_id: Optional[str] = None
    priority: Priority = Priority.NORMAL
    timeout: int = 30
    max_retries: int = 3
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentProtocol(Protocol):
    """Protocol defining the interface all agents must implement."""
    
    agent_id: str
    agent_name: str
    agent_type: AgentType
    
    async def execute(self, request: "AgentRequest") -> "AgentResponse":
        """Execute the agent's main logic."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health status."""
        ...
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        ...


class SkillProtocol(Protocol):
    """Protocol defining the interface all skills must implement."""
    
    skill_id: str
    skill_name: str
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the skill logic."""
        ...
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate skill input."""
        ...


class CacheableResult(BaseModel):
    """Result that can be cached."""
    
    key: str
    value: Any
    ttl: int = 3600  # seconds
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if the cached result has expired."""
        age = (datetime.utcnow() - self.created_at).total_seconds()
        return age > self.ttl


class ErrorInfo(BaseModel):
    """Structured error information."""
    
    error_type: str
    error_message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    traceback: Optional[str] = None
    
    @classmethod
    def from_exception(cls, exc: Exception, include_traceback: bool = False) -> "ErrorInfo":
        """Create ErrorInfo from an exception."""
        import traceback as tb
        
        return cls(
            error_type=type(exc).__name__,
            error_message=str(exc),
            error_code=getattr(exc, 'error_code', None),
            details=getattr(exc, 'details', None),
            traceback=tb.format_exc() if include_traceback else None
        )


# Type aliases for common use cases
MessageHistory = List[Dict[str, Any]]
SkillResult = Dict[str, Any]
AgentConfig = Dict[str, Any]
ValidationResult = tuple[bool, Optional[str]]  # (is_valid, error_message)


# Import uuid for type definitions
import uuid