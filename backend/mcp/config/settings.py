"""
MCP Configuration Settings

Central configuration for the MCP Gateway that connects
GENESIS with the NGX ecosystem tools.
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseSettings, Field


class MCPSettings(BaseSettings):
    """MCP Gateway configuration settings"""
    
    # Server Configuration
    mcp_host: str = Field(default="0.0.0.0", env="MCP_HOST")
    mcp_port: int = Field(default=3000, env="MCP_PORT")
    mcp_debug: bool = Field(default=False, env="MCP_DEBUG")
    
    # Security
    mcp_auth_enabled: bool = Field(default=True, env="MCP_AUTH_ENABLED")
    mcp_api_key: Optional[str] = Field(default=None, env="MCP_API_KEY")
    mcp_allowed_origins: List[str] = Field(
        default=["http://localhost:*", "https://*.ngx.com"],
        env="MCP_ALLOWED_ORIGINS"
    )
    
    # Tool Registry
    mcp_auto_discover: bool = Field(default=True, env="MCP_AUTO_DISCOVER")
    mcp_tool_timeout: int = Field(default=30, env="MCP_TOOL_TIMEOUT")
    
    # Performance
    mcp_max_concurrent_requests: int = Field(default=100, env="MCP_MAX_CONCURRENT_REQUESTS")
    mcp_request_timeout: int = Field(default=60, env="MCP_REQUEST_TIMEOUT")
    mcp_cache_ttl: int = Field(default=300, env="MCP_CACHE_TTL")
    
    # Monitoring
    mcp_metrics_enabled: bool = Field(default=True, env="MCP_METRICS_ENABLED")
    mcp_health_check_interval: int = Field(default=30, env="MCP_HEALTH_CHECK_INTERVAL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ToolConfig:
    """Configuration for individual NGX tools"""
    
    def __init__(self, name: str, endpoint: str, version: str = "1.0.0"):
        self.name = name
        self.endpoint = endpoint
        self.version = version
        self.health_check_path = "/health"
        self.capabilities: List[str] = []
        self.required_permissions: List[str] = []
        self.rate_limit: Optional[int] = None
        self.priority: int = 5  # 1-10, higher is more important


# Predefined tool configurations
NGX_TOOLS = {
    "nexus_core": ToolConfig(
        name="nexus_core",
        endpoint=os.getenv("NEXUS_CORE_URL", "http://localhost:8001"),
        version="1.0.0"
    ),
    "nexus_crm": ToolConfig(
        name="nexus_crm",
        endpoint=os.getenv("NEXUS_CRM_URL", "http://localhost:8002"),
        version="1.0.0"
    ),
    "ngx_pulse": ToolConfig(
        name="ngx_pulse",
        endpoint=os.getenv("NGX_PULSE_URL", "http://localhost:8003"),
        version="1.0.0"
    ),
    "ngx_agents_blog": ToolConfig(
        name="ngx_agents_blog",
        endpoint=os.getenv("NGX_BLOG_URL", "http://localhost:8004"),
        version="1.0.0"
    ),
    "nexus_conversations": ToolConfig(
        name="nexus_conversations",
        endpoint=os.getenv("NEXUS_CONV_URL", "http://localhost:8005"),
        version="1.0.0"
    )
}

# Tool capabilities mapping
TOOL_CAPABILITIES = {
    "nexus_core": [
        "analytics:read",
        "dashboard:read",
        "clients:manage",
        "reports:generate"
    ],
    "nexus_crm": [
        "contacts:manage",
        "deals:manage",
        "alerts:manage",
        "usage:track"
    ],
    "ngx_pulse": [
        "biometrics:read",
        "biometrics:write",
        "health:analyze",
        "wearables:sync"
    ],
    "ngx_agents_blog": [
        "content:read",
        "content:write",
        "chat:participate",
        "learning:track"
    ],
    "nexus_conversations": [
        "sessions:create",
        "sessions:manage",
        "agents:orchestrate",
        "recordings:access"
    ]
}

# Update tool capabilities
for tool_name, capabilities in TOOL_CAPABILITIES.items():
    if tool_name in NGX_TOOLS:
        NGX_TOOLS[tool_name].capabilities = capabilities

# Singleton settings instance
settings = MCPSettings()