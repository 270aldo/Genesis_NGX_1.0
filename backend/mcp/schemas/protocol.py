"""
MCP Protocol Schemas

Defines the standard schemas for MCP communication
following the Model Context Protocol specification.
"""

from typing import Any, Dict, List, Optional, Union, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class MessageRole(str, Enum):
    """Message roles in MCP protocol"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ToolCall(BaseModel):
    """Represents a tool call in the MCP protocol"""
    id: str = Field(..., description="Unique identifier for the tool call")
    name: str = Field(..., description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "call_123",
                "name": "nexus_core.get_client_analytics",
                "arguments": {"client_id": "client_456", "period": "last_30_days"}
            }
        }


class ToolResult(BaseModel):
    """Result from a tool execution"""
    tool_call_id: str = Field(..., description="ID of the tool call this result belongs to")
    content: Any = Field(..., description="Result content")
    is_error: bool = Field(default=False, description="Whether this is an error result")
    
    class Config:
        schema_extra = {
            "example": {
                "tool_call_id": "call_123",
                "content": {"analytics": {"sessions": 45, "engagement": 0.78}},
                "is_error": False
            }
        }


class Message(BaseModel):
    """Standard MCP message format"""
    role: MessageRole = Field(..., description="Role of the message sender")
    content: Optional[str] = Field(None, description="Text content of the message")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="Tool calls to make")
    tool_call_id: Optional[str] = Field(None, description="ID when responding to a tool call")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('tool_calls')
    def validate_tool_calls(cls, v, values):
        if v and values.get('role') != MessageRole.ASSISTANT:
            raise ValueError("Only assistant messages can have tool_calls")
        return v


class MCPRequest(BaseModel):
    """Standard MCP request format"""
    id: str = Field(..., description="Unique request ID")
    method: str = Field(..., description="Method to call")
    params: Dict[str, Any] = Field(default_factory=dict, description="Method parameters")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Request metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "req_789",
                "method": "completion",
                "params": {
                    "messages": [
                        {"role": "user", "content": "What's the revenue for last month?"}
                    ],
                    "tools": ["nexus_core", "nexus_crm"],
                    "temperature": 0.7
                }
            }
        }


class MCPResponse(BaseModel):
    """Standard MCP response format"""
    id: str = Field(..., description="Request ID this response belongs to")
    result: Optional[Any] = Field(None, description="Result of the method call")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information if failed")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    
    @validator('error')
    def validate_error_result(cls, v, values):
        if v and values.get('result') is not None:
            raise ValueError("Response cannot have both result and error")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "req_789",
                "result": {
                    "message": {
                        "role": "assistant",
                        "content": "Based on the data from nexus_core, last month's revenue was $125,430."
                    }
                }
            }
        }


class ToolDefinition(BaseModel):
    """Definition of a tool available in the MCP gateway"""
    name: str = Field(..., description="Unique name of the tool")
    description: str = Field(..., description="What this tool does")
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema for tool input")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for output")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "nexus_core.get_analytics",
                "description": "Retrieve analytics data for clients",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "metric": {"type": "string", "enum": ["revenue", "engagement", "retention"]},
                        "period": {"type": "string"}
                    },
                    "required": ["client_id", "metric"]
                }
            }
        }


class ToolRegistry(BaseModel):
    """Registry of all available tools"""
    tools: List[ToolDefinition] = Field(..., description="List of available tools")
    version: str = Field(default="1.0.0", description="Registry version")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ServerInfo(BaseModel):
    """MCP server information"""
    name: str = Field(default="GENESIS MCP Gateway", description="Server name")
    version: str = Field(..., description="Server version")
    protocol_version: str = Field(default="1.0", description="MCP protocol version")
    capabilities: List[str] = Field(..., description="Server capabilities")
    tools_available: int = Field(..., description="Number of tools available")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "GENESIS MCP Gateway",
                "version": "1.0.0",
                "protocol_version": "1.0",
                "capabilities": ["tools", "streaming", "function_calling"],
                "tools_available": 47
            }
        }


class HealthStatus(BaseModel):
    """Health status of a service or tool"""
    service: str = Field(..., description="Service name")
    status: Literal["healthy", "degraded", "unhealthy"] = Field(..., description="Health status")
    latency_ms: Optional[float] = Field(None, description="Response latency in milliseconds")
    last_check: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = Field(None, description="Error message if unhealthy")
    
    class Config:
        schema_extra = {
            "example": {
                "service": "nexus_core",
                "status": "healthy",
                "latency_ms": 45.2,
                "last_check": "2025-07-19T10:30:00Z"
            }
        }


class GatewayHealth(BaseModel):
    """Overall gateway health status"""
    status: Literal["healthy", "degraded", "unhealthy"] = Field(..., description="Overall status")
    services: List[HealthStatus] = Field(..., description="Individual service statuses")
    uptime_seconds: float = Field(..., description="Gateway uptime in seconds")
    total_requests: int = Field(default=0, description="Total requests processed")
    active_connections: int = Field(default=0, description="Current active connections")