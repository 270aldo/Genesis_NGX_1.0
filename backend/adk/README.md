# NGX Agent Development Kit (ADK)

## Overview

The NGX ADK is an internal framework that standardizes agent development across the GENESIS platform. It provides a robust foundation for creating, testing, and deploying AI agents with consistent patterns and best practices.

## Architecture

```
adk/
├── core/               # Core ADK components
│   ├── base_agent.py   # Base agent class with all common functionality
│   ├── exceptions.py   # ADK-specific exceptions
│   └── types.py        # Type definitions and protocols
├── toolkit/            # Common tools and utilities
│   ├── __init__.py
│   ├── caching.py      # Caching utilities
│   ├── monitoring.py   # Telemetry and monitoring
│   └── validation.py   # Input/output validation
├── patterns/           # Design patterns and mixins
│   ├── __init__.py
│   ├── circuit_breaker.py
│   ├── retry.py
│   └── streaming.py
└── testing/            # Testing utilities
    ├── __init__.py
    ├── fixtures.py     # Common test fixtures
    └── mocks.py        # Mock implementations
```

## Quick Start

### Creating a New Agent

```python
from adk.core import BaseADKAgent
from adk.patterns import CircuitBreaker, StreamingMixin
from adk.toolkit import cache_result

class MyAgent(BaseADKAgent, StreamingMixin):
    """Example agent implementation."""
    
    agent_id = "my_agent"
    agent_name = "My Agent"
    agent_type = "specialist"
    
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Main execution method."""
        # Validation is automatic via BaseADKAgent
        
        # Use caching decorator
        result = await self._process_with_cache(request)
        
        # Response formatting is automatic
        return self.create_response(result)
    
    @cache_result(ttl=3600)
    @CircuitBreaker(failure_threshold=3, timeout=30)
    async def _process_with_cache(self, request: AgentRequest):
        """Process with caching and circuit breaker."""
        return await self.llm_client.generate(request.prompt)
```

## Core Features

### 1. Standardized Lifecycle

Every ADK agent follows this lifecycle:

```
Initialize → Validate → Pre-process → Execute → Post-process → Format Response
```

### 2. Built-in Services

- **LLM Client**: Pre-configured Vertex AI client
- **Cache Manager**: Redis-based caching with TTL
- **Logger**: Structured logging with correlation IDs
- **Metrics**: OpenTelemetry integration
- **State Manager**: Conversation and session state

### 3. Error Handling

```python
from adk.core.exceptions import (
    AgentValidationError,
    AgentExecutionError,
    AgentTimeoutError,
    AgentRateLimitError
)

# Automatic retry with exponential backoff
@retry(max_attempts=3, backoff_factor=2)
async def risky_operation():
    # Your code here
    pass
```

### 4. Streaming Support

```python
class StreamingAgent(BaseADKAgent, StreamingMixin):
    async def stream_execute(self, request: AgentRequest):
        async for chunk in self.llm_client.stream_generate(request.prompt):
            yield self.format_stream_chunk(chunk)
```

## Testing

### Unit Tests

```python
from adk.testing import AgentTestCase, create_mock_request

class TestMyAgent(AgentTestCase):
    agent_class = MyAgent
    
    async def test_basic_execution(self):
        request = create_mock_request(
            prompt="Test prompt",
            user_id="test_user"
        )
        
        response = await self.agent.execute(request)
        
        self.assert_valid_response(response)
        self.assert_response_contains(response, "expected_content")
```

### Integration Tests

```python
from adk.testing import AgentIntegrationTest

class TestMyAgentIntegration(AgentIntegrationTest):
    async def test_with_real_llm(self):
        # Tests with actual LLM calls
        response = await self.agent.execute_with_llm(
            "Generate a workout plan"
        )
        self.assertTrue(response.success)
```

## Configuration

Agents can be configured via:

1. **Environment Variables**
2. **Pydantic Settings Classes**
3. **Runtime Configuration**

```python
class MyAgentConfig(BaseADKConfig):
    max_tokens: int = 1000
    temperature: float = 0.7
    custom_setting: str = "default"
    
    class Config:
        env_prefix = "MY_AGENT_"
```

## Best Practices

1. **Always inherit from BaseADKAgent**: This ensures consistency
2. **Use provided decorators**: For caching, retry, circuit breaking
3. **Implement proper validation**: Use Pydantic models
4. **Follow naming conventions**: agent_id should be snake_case
5. **Write comprehensive tests**: Aim for 90%+ coverage
6. **Use structured logging**: Never use print statements
7. **Handle errors gracefully**: Use ADK exceptions

## Advanced Features

### Multi-Agent Coordination

```python
from adk.patterns import MultiAgentCoordinator

coordinator = MultiAgentCoordinator()
results = await coordinator.execute_parallel(
    [agent1, agent2, agent3],
    request
)
```

### Conversation Memory

```python
from adk.toolkit import ConversationMemory

memory = ConversationMemory(redis_client)
await memory.add_message(user_id, message)
context = await memory.get_context(user_id, last_n=10)
```

### Feature Flags

```python
from adk.toolkit import feature_flag

@feature_flag("new_workout_algorithm")
async def generate_workout(self, request):
    # New algorithm implementation
    pass
```

## Migration Guide

For existing agents not using ADK:

1. Change inheritance from `BaseAgent` to `BaseADKAgent`
2. Update imports to use ADK modules
3. Replace custom implementations with ADK utilities
4. Run migration validator: `python -m adk.migrate validate`

## Performance Considerations

- ADK adds ~5ms overhead per request
- Caching can reduce LLM calls by 60-80%
- Circuit breakers prevent cascade failures
- Connection pooling improves throughput by 3x

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `adk` is in your Python path
2. **Configuration Not Loading**: Check environment variable prefix
3. **Cache Misses**: Verify Redis connection and key format
4. **Circuit Breaker Opening**: Check failure threshold settings

### Debug Mode

```python
# Enable debug mode for detailed logging
agent = MyAgent(debug=True)

# Or via environment variable
export ADK_DEBUG=true
```

## Contributing

To contribute to the ADK:

1. Follow the established patterns
2. Add tests for new features
3. Update documentation
4. Submit PR with clear description

## Changelog

### v2.0.0 (2025-07-21)
- Initial formal release
- Extracted from existing agent implementations
- Added circuit breaker and retry patterns
- Comprehensive testing utilities

### v1.0.0 (Legacy)
- Informal patterns used across agents
- No centralized toolkit

## Support

For ADK-related questions:
- Check this documentation first
- Review example implementations in `/examples`
- Contact the platform team

---

**Note**: The ADK is an internal framework specific to NGX GENESIS. It's designed to work seamlessly with our infrastructure and should not be used outside the GENESIS ecosystem.