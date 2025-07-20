"""
Tool Registry System for MCP Gateway

Dynamic registration system that allows NGX tools to:
- Register themselves with the gateway
- Update their capabilities
- Provide health status
- Handle versioning
"""

import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from mcp.schemas import ToolDefinition, HealthStatus
from mcp.config import ToolConfig
from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RegisteredTool:
    """Represents a tool registered with the MCP Gateway"""
    config: ToolConfig
    definitions: List[ToolDefinition] = field(default_factory=list)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    health_status: Optional[HealthStatus] = None
    metadata: Dict = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Check if tool is considered active (seen in last 5 minutes)"""
        return (datetime.utcnow() - self.last_seen) < timedelta(minutes=5)


class ToolRegistry:
    """
    Dynamic tool registry for the MCP Gateway
    
    Manages tool registration, discovery, and lifecycle
    """
    
    def __init__(self):
        self._tools: Dict[str, RegisteredTool] = {}
        self._tool_definitions: Dict[str, ToolDefinition] = {}
        self._capabilities: Dict[str, Set[str]] = {}  # capability -> set of tool names
        self._lock = asyncio.Lock()
        
    async def register_tool(
        self,
        name: str,
        config: ToolConfig,
        definitions: List[ToolDefinition],
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Register a new tool or update existing registration
        
        Args:
            name: Unique tool name
            config: Tool configuration
            definitions: List of tool definitions (capabilities)
            metadata: Optional metadata about the tool
            
        Returns:
            bool: Success status
        """
        async with self._lock:
            try:
                # Create or update tool registration
                tool = RegisteredTool(
                    config=config,
                    definitions=definitions,
                    metadata=metadata or {}
                )
                
                # Update definitions index
                for definition in definitions:
                    self._tool_definitions[definition.name] = definition
                    
                    # Update capability index
                    for capability in config.capabilities:
                        if capability not in self._capabilities:
                            self._capabilities[capability] = set()
                        self._capabilities[capability].add(name)
                
                # Store tool
                self._tools[name] = tool
                
                logger.info(
                    f"Registered tool '{name}' with {len(definitions)} definitions "
                    f"and {len(config.capabilities)} capabilities"
                )
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to register tool '{name}': {e}")
                return False
    
    async def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool from the gateway
        
        Args:
            name: Tool name to unregister
            
        Returns:
            bool: Success status
        """
        async with self._lock:
            if name not in self._tools:
                return False
            
            tool = self._tools[name]
            
            # Remove from definitions
            for definition in tool.definitions:
                self._tool_definitions.pop(definition.name, None)
            
            # Remove from capabilities
            for capability in tool.config.capabilities:
                if capability in self._capabilities:
                    self._capabilities[capability].discard(name)
                    if not self._capabilities[capability]:
                        del self._capabilities[capability]
            
            # Remove tool
            del self._tools[name]
            
            logger.info(f"Unregistered tool '{name}'")
            return True
    
    async def update_health(self, name: str, health_status: HealthStatus) -> bool:
        """
        Update health status for a tool
        
        Args:
            name: Tool name
            health_status: New health status
            
        Returns:
            bool: Success status
        """
        async with self._lock:
            if name not in self._tools:
                return False
            
            self._tools[name].health_status = health_status
            self._tools[name].last_seen = datetime.utcnow()
            return True
    
    async def heartbeat(self, name: str) -> bool:
        """
        Update last seen time for a tool (keepalive)
        
        Args:
            name: Tool name
            
        Returns:
            bool: Success status
        """
        async with self._lock:
            if name not in self._tools:
                return False
            
            self._tools[name].last_seen = datetime.utcnow()
            return True
    
    def get_tool(self, name: str) -> Optional[RegisteredTool]:
        """Get a registered tool by name"""
        return self._tools.get(name)
    
    def get_tool_definition(self, definition_name: str) -> Optional[ToolDefinition]:
        """Get a tool definition by name"""
        return self._tool_definitions.get(definition_name)
    
    def list_tools(self, active_only: bool = False) -> List[str]:
        """
        List all registered tools
        
        Args:
            active_only: Only return active tools
            
        Returns:
            List of tool names
        """
        if active_only:
            return [name for name, tool in self._tools.items() if tool.is_active]
        return list(self._tools.keys())
    
    def list_capabilities(self) -> List[str]:
        """List all available capabilities across all tools"""
        return list(self._capabilities.keys())
    
    def get_tools_by_capability(self, capability: str) -> List[str]:
        """Get all tools that provide a specific capability"""
        return list(self._capabilities.get(capability, set()))
    
    def get_all_definitions(self) -> List[ToolDefinition]:
        """Get all tool definitions from all registered tools"""
        return list(self._tool_definitions.values())
    
    def get_registry_stats(self) -> Dict:
        """Get statistics about the registry"""
        active_tools = sum(1 for tool in self._tools.values() if tool.is_active)
        
        return {
            "total_tools": len(self._tools),
            "active_tools": active_tools,
            "inactive_tools": len(self._tools) - active_tools,
            "total_definitions": len(self._tool_definitions),
            "total_capabilities": len(self._capabilities),
            "tools_by_status": self._get_tools_by_status()
        }
    
    def _get_tools_by_status(self) -> Dict[str, int]:
        """Get count of tools by health status"""
        status_counts = {"healthy": 0, "degraded": 0, "unhealthy": 0, "unknown": 0}
        
        for tool in self._tools.values():
            if tool.health_status:
                status_counts[tool.health_status.status] += 1
            else:
                status_counts["unknown"] += 1
        
        return status_counts
    
    def export_registry(self) -> Dict:
        """Export the registry state for persistence or debugging"""
        return {
            "tools": {
                name: {
                    "config": {
                        "name": tool.config.name,
                        "endpoint": tool.config.endpoint,
                        "version": tool.config.version,
                        "capabilities": tool.config.capabilities
                    },
                    "definitions": [d.dict() for d in tool.definitions],
                    "registered_at": tool.registered_at.isoformat(),
                    "last_seen": tool.last_seen.isoformat(),
                    "is_active": tool.is_active,
                    "health_status": tool.health_status.dict() if tool.health_status else None,
                    "metadata": tool.metadata
                }
                for name, tool in self._tools.items()
            },
            "exported_at": datetime.utcnow().isoformat()
        }
    
    async def import_registry(self, data: Dict) -> bool:
        """Import registry state from exported data"""
        try:
            async with self._lock:
                # Clear existing
                self._tools.clear()
                self._tool_definitions.clear()
                self._capabilities.clear()
                
                # Import tools
                for name, tool_data in data.get("tools", {}).items():
                    config = ToolConfig(
                        name=tool_data["config"]["name"],
                        endpoint=tool_data["config"]["endpoint"],
                        version=tool_data["config"]["version"]
                    )
                    config.capabilities = tool_data["config"]["capabilities"]
                    
                    definitions = [
                        ToolDefinition(**d) for d in tool_data["definitions"]
                    ]
                    
                    await self.register_tool(
                        name=name,
                        config=config,
                        definitions=definitions,
                        metadata=tool_data.get("metadata", {})
                    )
                
                logger.info(f"Imported registry with {len(self._tools)} tools")
                return True
                
        except Exception as e:
            logger.error(f"Failed to import registry: {e}")
            return False


# Global registry instance
tool_registry = ToolRegistry()