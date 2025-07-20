"""
MCP (Model Context Protocol) Gateway for NGX Ecosystem

This module provides a unified MCP server that acts as a gateway
for all NGX tools to communicate with the GENESIS AI brain.

Architecture:
- Single MCP server for all tools (reduces complexity)
- Dynamic tool registration system
- Unified authentication and authorization
- Intelligent routing to appropriate services
- Built-in monitoring and health checks
"""

__version__ = "1.0.0"
__all__ = ["MCPGateway", "ToolRegistry", "MCPConfig"]