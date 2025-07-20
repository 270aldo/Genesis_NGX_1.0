"""
MCP Gateway Server

The central MCP server that acts as a gateway between GENESIS
and all NGX ecosystem tools. This server provides:

- Unified entry point for all MCP requests
- Dynamic tool registration and discovery
- Request routing to appropriate services
- Authentication and authorization
- Health monitoring and metrics
- Caching and performance optimization
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
import aiohttp
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from mcp.config import settings, NGX_TOOLS
from mcp.schemas import (
    MCPRequest,
    MCPResponse,
    ServerInfo,
    ToolRegistry,
    ToolDefinition,
    GatewayHealth,
    HealthStatus,
    Message,
    MessageRole,
    ToolCall,
    ToolResult
)
from mcp.utils.auth import verify_api_key
from mcp.utils.cache import CacheManager
from mcp.server.registry import tool_registry
from mcp.adapters import (
    NexusCoreAdapter,
    NexusCRMAdapter,
    NGXPulseAdapter,
    NGXAgentsBlogAdapter,
    NexusConversationsAdapter
)
from core.logging_config import get_logger

logger = get_logger(__name__)


class MCPGateway:
    """Main MCP Gateway Server implementation"""
    
    def __init__(self):
        self.app = FastAPI(
            title="GENESIS MCP Gateway",
            description="Unified MCP server for NGX ecosystem integration",
            version="1.0.0"
        )
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_endpoints: Dict[str, str] = {}
        self.health_status: Dict[str, HealthStatus] = {}
        self.active_connections: Set[WebSocket] = set()
        self.start_time = datetime.utcnow()
        self.request_count = 0
        self.cache = CacheManager(ttl=settings.mcp_cache_ttl)
        self.session = None
        
        self._setup_middleware()
        self._setup_routes()
        self._register_tools()
    
    def _setup_middleware(self):
        """Configure middleware for the FastAPI app"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.mcp_allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @self.app.middleware("http")
        async def add_request_id(request: Request, call_next):
            """Add request ID to all requests"""
            request_id = request.headers.get("X-Request-ID", f"req_{datetime.utcnow().timestamp()}")
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
    
    def _setup_routes(self):
        """Set up API routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize async session on startup"""
            self.session = aiohttp.ClientSession()
            # Start health check loop
            asyncio.create_task(self._health_check_loop())
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Clean up on shutdown"""
            if self.session:
                await self.session.close()
        
        @self.app.get("/", response_model=ServerInfo)
        async def get_server_info():
            """Get MCP server information"""
            return ServerInfo(
                name="GENESIS MCP Gateway",
                version="1.0.0",
                protocol_version="1.0",
                capabilities=[
                    "tools",
                    "streaming",
                    "function_calling",
                    "multi_tool_use",
                    "caching",
                    "health_monitoring"
                ],
                tools_available=len(self.tools)
            )
        
        @self.app.get("/health", response_model=GatewayHealth)
        async def get_health():
            """Get gateway health status"""
            overall_status = "healthy"
            unhealthy_count = sum(1 for s in self.health_status.values() if s.status == "unhealthy")
            degraded_count = sum(1 for s in self.health_status.values() if s.status == "degraded")
            
            if unhealthy_count > 0:
                overall_status = "degraded" if unhealthy_count < len(self.health_status) // 2 else "unhealthy"
            elif degraded_count > 0:
                overall_status = "degraded"
            
            return GatewayHealth(
                status=overall_status,
                services=list(self.health_status.values()),
                uptime_seconds=(datetime.utcnow() - self.start_time).total_seconds(),
                total_requests=self.request_count,
                active_connections=len(self.active_connections)
            )
        
        @self.app.get("/tools", response_model=ToolRegistry)
        async def get_tools():
            """Get all available tools"""
            return ToolRegistry(
                tools=tool_registry.get_all_definitions(),
                version="1.0.0"
            )
        
        @self.app.post("/v1/messages", response_model=MCPResponse)
        async def process_message(request: MCPRequest):
            """Process an MCP message request"""
            self.request_count += 1
            
            try:
                # Verify authentication if enabled
                if settings.mcp_auth_enabled:
                    api_key = request.meta.get("api_key")
                    if not verify_api_key(api_key):
                        raise HTTPException(status_code=401, detail="Invalid API key")
                
                # Route based on method
                if request.method == "completion":
                    result = await self._handle_completion(request)
                elif request.method == "tool_call":
                    result = await self._handle_tool_call(request)
                else:
                    raise ValueError(f"Unknown method: {request.method}")
                
                return MCPResponse(
                    id=request.id,
                    result=result
                )
                
            except Exception as e:
                logger.error(f"Error processing request {request.id}: {e}")
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32603,
                        "message": str(e)
                    }
                )
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for streaming responses"""
            await websocket.accept()
            self.active_connections.add(websocket)
            
            try:
                while True:
                    data = await websocket.receive_text()
                    request = MCPRequest.parse_raw(data)
                    
                    # Process request and stream response
                    async for chunk in self._handle_streaming_request(request):
                        await websocket.send_text(json.dumps(chunk))
                        
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
    
    def _register_tools(self):
        """Register all NGX tools with the registry"""
        # Initialize adapters dictionary
        if not hasattr(self, "adapters"):
            self.adapters = {}
        
        # Register each tool with its adapter
        asyncio.create_task(self._register_nexus_core())
        asyncio.create_task(self._register_nexus_crm())
        asyncio.create_task(self._register_ngx_pulse())
        asyncio.create_task(self._register_ngx_blog())
        asyncio.create_task(self._register_nexus_conversations())
    
    async def _register_nexus_core(self):
        """Register Nexus Core with its full adapter"""
        adapter = NexusCoreAdapter(NGX_TOOLS["nexus_core"].endpoint)
        await adapter.initialize()
        
        definitions = adapter.get_tool_definitions()
        
        await tool_registry.register_tool(
            name="nexus_core",
            config=NGX_TOOLS["nexus_core"],
            definitions=definitions,
            metadata={"adapter": "NexusCoreAdapter"}
        )
        
        # Store adapter reference and endpoints
        self.adapters["nexus_core"] = adapter
        for definition in definitions:
            self.tool_endpoints[definition.name] = NGX_TOOLS["nexus_core"].endpoint
    
    async def _register_nexus_crm(self):
        """Register Nexus CRM with its adapter"""
        adapter = NexusCRMAdapter(NGX_TOOLS["nexus_crm"].endpoint)
        await adapter.initialize()
        
        definitions = adapter.get_tool_definitions()
        
        await tool_registry.register_tool(
            name="nexus_crm",
            config=NGX_TOOLS["nexus_crm"],
            definitions=definitions,
            metadata={"adapter": "NexusCRMAdapter"}
        )
        
        self.adapters["nexus_crm"] = adapter
        for definition in definitions:
            self.tool_endpoints[definition.name] = NGX_TOOLS["nexus_crm"].endpoint
    
    async def _register_ngx_pulse(self):
        """Register NGX Pulse with its adapter"""
        adapter = NGXPulseAdapter(NGX_TOOLS["ngx_pulse"].endpoint)
        await adapter.initialize()
        
        definitions = adapter.get_tool_definitions()
        
        await tool_registry.register_tool(
            name="ngx_pulse",
            config=NGX_TOOLS["ngx_pulse"],
            definitions=definitions,
            metadata={"adapter": "NGXPulseAdapter"}
        )
        
        self.adapters["ngx_pulse"] = adapter
        for definition in definitions:
            self.tool_endpoints[definition.name] = NGX_TOOLS["ngx_pulse"].endpoint
    
    async def _register_ngx_blog(self):
        """Register NGX Agents Blog with its adapter"""
        adapter = NGXAgentsBlogAdapter(NGX_TOOLS["ngx_agents_blog"].endpoint)
        await adapter.initialize()
        
        definitions = adapter.get_tool_definitions()
        
        await tool_registry.register_tool(
            name="ngx_agents_blog",
            config=NGX_TOOLS["ngx_agents_blog"],
            definitions=definitions,
            metadata={"adapter": "NGXAgentsBlogAdapter"}
        )
        
        self.adapters["ngx_agents_blog"] = adapter
        for definition in definitions:
            self.tool_endpoints[definition.name] = NGX_TOOLS["ngx_agents_blog"].endpoint
    
    async def _register_nexus_conversations(self):
        """Register Nexus Conversations with its adapter"""
        adapter = NexusConversationsAdapter(NGX_TOOLS["nexus_conversations"].endpoint)
        await adapter.initialize()
        
        definitions = adapter.get_tool_definitions()
        
        await tool_registry.register_tool(
            name="nexus_conversations",
            config=NGX_TOOLS["nexus_conversations"],
            definitions=definitions,
            metadata={"adapter": "NexusConversationsAdapter"}
        )
        
        self.adapters["nexus_conversations"] = adapter
        for definition in definitions:
            self.tool_endpoints[definition.name] = NGX_TOOLS["nexus_conversations"].endpoint
    
    async def _handle_completion(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle completion request with tool use"""
        messages = request.params.get("messages", [])
        available_tools = request.params.get("tools", list(self.tools.keys()))
        
        # Check if we need to use tools
        last_message = messages[-1] if messages else None
        if last_message and last_message.get("role") == "user":
            # Analyze user intent and determine which tools to use
            tool_calls = await self._analyze_intent_and_select_tools(
                last_message.get("content", ""),
                available_tools
            )
            
            if tool_calls:
                # Execute tool calls
                tool_results = []
                for tool_call in tool_calls:
                    result = await self._execute_tool(
                        tool_call["name"],
                        tool_call["arguments"]
                    )
                    tool_results.append(ToolResult(
                        tool_call_id=tool_call["id"],
                        content=result,
                        is_error=isinstance(result, dict) and "error" in result
                    ))
                
                # Return assistant message with tool results
                return {
                    "message": {
                        "role": "assistant",
                        "tool_calls": tool_calls,
                        "content": self._generate_response_from_tools(tool_results)
                    }
                }
        
        # Default response without tools
        return {
            "message": {
                "role": "assistant",
                "content": "I'm ready to help you with the NGX ecosystem. What would you like to know?"
            }
        }
    
    async def _handle_tool_call(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle direct tool call"""
        tool_name = request.params.get("tool")
        arguments = request.params.get("arguments", {})
        
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        result = await self._execute_tool(tool_name, arguments)
        return {"result": result}
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool call by routing to the appropriate service"""
        # Check cache first
        cache_key = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
        cached_result = await self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Try to use adapter if available
        adapter_name = tool_name.split(".")[0]  # Get base tool name
        if adapter_name in self.adapters:
            try:
                adapter = self.adapters[adapter_name]
                result = await adapter.execute_tool(tool_name, arguments)
                # Cache successful results
                if not isinstance(result, dict) or "error" not in result:
                    await self.cache.set(cache_key, result)
                return result
            except Exception as e:
                logger.error(f"Error executing tool {tool_name} via adapter: {e}")
                return {"error": str(e)}
        
        # Fallback to endpoint-based execution
        endpoint = self.tool_endpoints.get(tool_name)
        if not endpoint:
            return {"error": f"No endpoint configured for tool: {tool_name}"}
        
        try:
            # Make request to tool endpoint
            async with self.session.post(
                f"{endpoint}/mcp/execute",
                json={
                    "tool": tool_name,
                    "arguments": arguments
                },
                timeout=aiohttp.ClientTimeout(total=settings.mcp_tool_timeout)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    # Cache successful results
                    await self.cache.set(cache_key, result)
                    return result
                else:
                    error_text = await response.text()
                    return {"error": f"Tool execution failed: {error_text}"}
                    
        except asyncio.TimeoutError:
            return {"error": f"Tool execution timed out after {settings.mcp_tool_timeout}s"}
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def _analyze_intent_and_select_tools(
        self,
        user_message: str,
        available_tools: List[str]
    ) -> List[Dict[str, Any]]:
        """Analyze user intent and select appropriate tools to use"""
        # This is a simplified implementation
        # In production, this would use GENESIS AI to analyze intent
        
        tool_calls = []
        
        # Simple keyword matching for demo
        message_lower = user_message.lower()
        
        # Nexus Core - Analytics and Dashboard
        if any(word in message_lower for word in ["analytics", "revenue", "dashboard", "metrics", "report"]):
            if "nexus_core.get_client_analytics" in available_tools:
                tool_calls.append({
                    "id": f"call_{datetime.utcnow().timestamp()}",
                    "name": "nexus_core.get_client_analytics",
                    "arguments": {"metric": "revenue", "period": "last_30_days"}
                })
            elif "nexus_core.get_dashboard_summary" in available_tools:
                tool_calls.append({
                    "id": f"call_{datetime.utcnow().timestamp()}",
                    "name": "nexus_core.get_dashboard_summary",
                    "arguments": {"include_ai_usage": True, "include_financial": True}
                })
        
        # Nexus CRM - Contact and Deal Management
        if any(word in message_lower for word in ["client", "customer", "contact", "deal", "crm"]):
            if "nexus_crm.manage_contacts" in available_tools:
                tool_calls.append({
                    "id": f"call_{datetime.utcnow().timestamp()}",
                    "name": "nexus_crm.manage_contacts",
                    "arguments": {"action": "list", "filters": {"status": "active", "limit": 10}}
                })
            if "deal" in message_lower and "nexus_crm.manage_deals" in available_tools:
                tool_calls.append({
                    "id": f"call_{datetime.utcnow().timestamp()}",
                    "name": "nexus_crm.manage_deals",
                    "arguments": {"action": "list"}
                })
        
        # NGX Pulse - Health and Biometrics
        if any(word in message_lower for word in ["health", "biometric", "heart", "sleep", "workout", "fitness"]):
            if "ngx_pulse.read_biometrics" in available_tools:
                tool_calls.append({
                    "id": f"call_{datetime.utcnow().timestamp()}",
                    "name": "ngx_pulse.read_biometrics",
                    "arguments": {"user_id": "current", "metric": "all"}
                })
            if "workout" in message_lower and "ngx_pulse.track_workout" in available_tools:
                tool_calls.append({
                    "id": f"call_{datetime.utcnow().timestamp()}",
                    "name": "ngx_pulse.track_workout",
                    "arguments": {"action": "analyze", "workout_id": "latest"}
                })
        
        # NGX Blog - Content Management
        if any(word in message_lower for word in ["blog", "content", "post", "article", "seo"]):
            if "ngx_blog.manage_posts" in available_tools:
                tool_calls.append({
                    "id": f"call_{datetime.utcnow().timestamp()}",
                    "name": "ngx_blog.manage_posts",
                    "arguments": {"action": "list", "filters": {"status": "published", "limit": 5}}
                })
            if "performance" in message_lower and "ngx_blog.analyze_performance" in available_tools:
                tool_calls.append({
                    "id": f"call_{datetime.utcnow().timestamp()}",
                    "name": "ngx_blog.analyze_performance",
                    "arguments": {"metric": "all", "period": "month"}
                })
        
        # Nexus Conversations - Chat Analytics
        if any(word in message_lower for word in ["conversation", "chat", "message", "engagement"]):
            if "nexus_conversations.analyze_engagement" in available_tools:
                tool_calls.append({
                    "id": f"call_{datetime.utcnow().timestamp()}",
                    "name": "nexus_conversations.analyze_engagement",
                    "arguments": {"analysis_type": "user_satisfaction", "scope": "global", "period": "week"}
                })
            if "history" in message_lower and "nexus_conversations.get_history" in available_tools:
                tool_calls.append({
                    "id": f"call_{datetime.utcnow().timestamp()}",
                    "name": "nexus_conversations.get_history",
                    "arguments": {"time_range": "today", "limit": 10}
                })
        
        return tool_calls
    
    def _generate_response_from_tools(self, tool_results: List[ToolResult]) -> str:
        """Generate natural language response from tool results"""
        # This is simplified - in production would use GENESIS AI
        if not tool_results:
            return "I couldn't find any relevant information."
        
        response_parts = []
        for result in tool_results:
            if not result.is_error:
                response_parts.append(f"Based on the data: {json.dumps(result.content)}")
            else:
                response_parts.append(f"There was an error: {result.content.get('error', 'Unknown error')}")
        
        return " ".join(response_parts)
    
    async def _handle_streaming_request(self, request: MCPRequest):
        """Handle streaming request over WebSocket"""
        # Stream chunks of response
        yield {"type": "start", "request_id": request.id}
        
        # Process request
        if request.method == "completion":
            # Simulate streaming response
            response_text = "Processing your request through the NGX ecosystem..."
            for word in response_text.split():
                yield {
                    "type": "content",
                    "content": word + " ",
                    "request_id": request.id
                }
                await asyncio.sleep(0.1)  # Simulate processing
        
        yield {"type": "end", "request_id": request.id}
    
    async def _health_check_loop(self):
        """Continuously check health of registered services"""
        while True:
            for tool_name, tool_config in NGX_TOOLS.items():
                try:
                    start_time = datetime.utcnow()
                    async with self.session.get(
                        f"{tool_config.endpoint}{tool_config.health_check_path}",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                        
                        if response.status == 200:
                            self.health_status[tool_name] = HealthStatus(
                                service=tool_name,
                                status="healthy",
                                latency_ms=latency_ms
                            )
                        else:
                            self.health_status[tool_name] = HealthStatus(
                                service=tool_name,
                                status="degraded",
                                latency_ms=latency_ms,
                                error=f"HTTP {response.status}"
                            )
                            
                except Exception as e:
                    self.health_status[tool_name] = HealthStatus(
                        service=tool_name,
                        status="unhealthy",
                        error=str(e)
                    )
            
            await asyncio.sleep(settings.mcp_health_check_interval)
    
    def run(self):
        """Run the MCP Gateway server"""
        logger.info(f"Starting MCP Gateway on {settings.mcp_host}:{settings.mcp_port}")
        uvicorn.run(
            self.app,
            host=settings.mcp_host,
            port=settings.mcp_port,
            log_level="debug" if settings.mcp_debug else "info"
        )


# Create gateway instance
gateway = MCPGateway()

# Export app for direct usage
app = gateway.app