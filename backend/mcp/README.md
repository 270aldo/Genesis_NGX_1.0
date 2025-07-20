# GENESIS MCP Gateway - NGX Ecosystem Integration

## Overview

The GENESIS MCP (Model Context Protocol) Gateway is a unified server that connects all NGX ecosystem tools, allowing them to communicate with the GENESIS AI brain and be accessible through Claude Desktop.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Claude Desktop │────▶│  MCP Gateway     │────▶│  NGX Tools      │
└─────────────────┘     │  (Port 3000)     │     ├─────────────────┤
                        │                  │     │ • nexus_core    │
┌─────────────────┐     │  - Auth         │     │ • nexus-crm     │
│  GENESIS AI     │────▶│  - Routing      │────▶│ • ngx_pulse     │
│  Backend        │     │  - Caching      │     │ • ngx_blog      │
└─────────────────┘     │  - Monitoring   │     │ • nexus_conv    │
                        └──────────────────┘     └─────────────────┘
```

## Key Features

1. **Unified Entry Point**: Single MCP server for all tools (no need for 5+ separate servers)
2. **Dynamic Tool Registry**: Tools can register/unregister dynamically
3. **Intelligent Routing**: Automatically routes requests to appropriate services
4. **Built-in Caching**: Reduces API calls and improves performance
5. **Health Monitoring**: Continuous health checks of all registered tools
6. **Authentication**: Unified auth for all tools
7. **WebSocket Support**: Real-time streaming responses

## Quick Start

### 1. Configure Environment

```bash
# MCP Gateway Configuration
export MCP_HOST=0.0.0.0
export MCP_PORT=3000
export MCP_API_KEY=your-secure-api-key

# Tool Endpoints
export NEXUS_CORE_URL=http://localhost:8001
export NEXUS_CRM_URL=http://localhost:8002
export NGX_PULSE_URL=http://localhost:8003
export NGX_BLOG_URL=http://localhost:8004
export NEXUS_CONV_URL=http://localhost:8005
```

### 2. Start the Gateway

```bash
# From backend directory
python -m mcp.main

# Or with uvicorn directly
uvicorn mcp.server:app --host 0.0.0.0 --port 3000 --reload
```

### 3. Configure Claude Desktop

Create or update `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "genesis-ngx": {
      "command": "node",
      "args": ["/path/to/mcp-client.js"],
      "env": {
        "MCP_GATEWAY_URL": "http://localhost:3000",
        "MCP_API_KEY": "your-secure-api-key"
      }
    }
  }
}
```

## API Endpoints

### Server Information
```http
GET /
```
Returns server info, protocol version, and capabilities.

### Health Check
```http
GET /health
```
Returns health status of gateway and all registered tools.

### List Tools
```http
GET /tools
```
Returns all available tool definitions.

### Execute Tool
```http
POST /v1/messages
Content-Type: application/json

{
  "id": "req_123",
  "method": "completion",
  "params": {
    "messages": [
      {
        "role": "user",
        "content": "What's the revenue for last month?"
      }
    ],
    "tools": ["nexus_core", "nexus_crm"]
  }
}
```

### WebSocket (Streaming)
```
ws://localhost:3000/ws
```
For real-time streaming responses.

## Tool Adapters

Each NGX tool has an adapter that translates MCP requests into tool-specific API calls.

### Creating a New Adapter

1. Create adapter file in `mcp/adapters/`:

```python
from mcp.schemas import ToolDefinition
from mcp.config import ToolConfig

class YourToolAdapter:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="your_tool.operation",
                description="What this operation does",
                input_schema={...}
            )
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        # Implement tool execution
        pass
```

2. Register in gateway startup.

## Tool Examples

### Nexus Core - Analytics
```python
# Get client analytics
{
  "tool": "nexus_core.get_client_analytics",
  "arguments": {
    "metric": "revenue",
    "period": "last_30_days"
  }
}
```

### Nexus CRM - Contact Management
```python
# List contacts
{
  "tool": "nexus_crm.contacts_manage",
  "arguments": {
    "action": "list",
    "filters": {"status": "active"}
  }
}
```

### NGX Pulse - Health Data
```python
# Get biometrics
{
  "tool": "ngx_pulse.biometrics_read",
  "arguments": {
    "user_id": "current",
    "metric": "heart_rate_variability"
  }
}
```

## Monitoring

### Metrics Available
- Total requests processed
- Active connections
- Tool health status
- Cache hit rates
- Response latencies

### Health Status Levels
- **healthy**: All systems operational
- **degraded**: Some tools unavailable
- **unhealthy**: Major issues detected

## Security

1. **API Key Authentication**: Required for all requests
2. **CORS Configuration**: Configurable allowed origins
3. **Rate Limiting**: Configurable per tool
4. **Request Validation**: Input schema validation

## Advanced Features

### Caching Strategy
- TTL-based caching (default: 5 minutes)
- Cache key includes tool name and arguments
- Automatic cache invalidation on errors

### Tool Priority
- Tools can have priority levels (1-10)
- Higher priority tools get preference during high load

### Graceful Degradation
- Gateway continues operating even if some tools fail
- Automatic retry with exponential backoff
- Circuit breaker pattern for failing tools

## Troubleshooting

### Gateway Won't Start
1. Check port 3000 is not in use
2. Verify environment variables are set
3. Check logs for specific errors

### Tools Not Registering
1. Verify tool endpoints are accessible
2. Check health endpoint returns 200
3. Review adapter implementation

### Claude Desktop Can't Connect
1. Verify gateway is running
2. Check API key matches
3. Ensure claude_desktop_config.json is valid

## Development

### Running Tests
```bash
pytest tests/mcp/
```

### Adding New Tools
1. Create adapter in `mcp/adapters/`
2. Add configuration to `mcp/config/settings.py`
3. Register in gateway startup
4. Add tests

### Contributing
- Follow existing patterns
- Add comprehensive tests
- Update documentation
- Submit PR with clear description

## Future Enhancements

1. **GraphQL Support**: Alternative to REST API
2. **Metrics Dashboard**: Real-time monitoring UI
3. **Tool Marketplace**: Dynamic tool discovery
4. **Multi-tenancy**: Support for multiple organizations
5. **Edge Deployment**: CDN-based distribution

---

For more information, see the main GENESIS documentation or contact the development team.