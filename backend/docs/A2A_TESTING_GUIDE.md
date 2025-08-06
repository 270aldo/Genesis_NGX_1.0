# A2A Integration Testing Guide

## Overview

The Agent-to-Agent (A2A) communication system is the backbone of GENESIS, enabling all 11 specialized agents to collaborate seamlessly. This guide documents the comprehensive A2A testing infrastructure.

## Test Suite Structure

```
tests/integration/a2a/
├── __init__.py
├── conftest.py                          # Shared fixtures and configuration
├── test_a2a_core_communication.py       # Core messaging tests
├── test_e2e_workflows.py                # End-to-end agent workflows
├── test_failure_recovery.py             # Error handling and recovery
├── test_multi_agent_coordination.py     # Multi-agent collaboration
├── test_performance_load.py             # Performance and load testing
└── utils/
    ├── __init__.py
    ├── agent_simulator.py                # Simulated agent behaviors
    ├── network_simulator.py              # Network condition simulation
    └── test_server.py                    # Isolated test A2A server
```

## Key Components

### 1. Test A2A Server (`test_server.py`)

- **Purpose**: Provides an isolated A2A server for testing
- **Features**:
  - Dynamic port allocation to avoid conflicts
  - Built-in monitoring and metrics
  - Graceful startup/shutdown
  - Agent registration tracking

### 2. Agent Simulator (`agent_simulator.py`)

- **Purpose**: Simulates all 11 GENESIS agents for testing
- **Agents Simulated**:
  - NEXUS (Orchestrator)
  - BLAZE (Elite Training)
  - SAGE (Nutrition)
  - CODE (Genetic)
  - WAVE (Analytics)
  - LUNA (Female Wellness)
  - STELLA (Progress)
  - SPARK (Motivation)
  - NOVA (Biohacking)
  - GUARDIAN (Security)
  - NODE (Integration)

### 3. Network Simulator (`network_simulator.py`)

- **Purpose**: Simulates various network conditions
- **Conditions**:
  - Normal operation
  - High latency
  - Packet loss
  - Connection drops
  - Bandwidth limitations

## Test Categories

### Core Communication Tests

Tests fundamental A2A messaging capabilities:

- Agent registration and discovery
- Message routing and delivery
- Response handling
- Connection management

### End-to-End Workflow Tests

Validates complete user workflows:

- Training plan generation (BLAZE → SAGE → STELLA)
- Health monitoring (WAVE → NOVA → GUARDIAN)
- Progress tracking (STELLA → SPARK → NEXUS)
- Security workflows (GUARDIAN → NODE → NEXUS)

### Failure Recovery Tests

Ensures system resilience:

- Agent crashes and restarts
- Network interruptions
- Message timeouts
- Retry mechanisms
- Circuit breaker patterns

### Multi-Agent Coordination Tests

Tests complex agent interactions:

- Parallel agent activation
- Sequential workflows
- Resource conflict resolution
- Priority-based routing
- Load balancing

### Performance Tests

Validates system performance:

- 200+ concurrent messages
- Latency under load
- Throughput benchmarks
- Memory usage
- Connection pooling

## Running the Tests

### Run All A2A Tests

```bash
pytest tests/integration/a2a/ -v
```

### Run Specific Test Categories

```bash
# Core communication only
pytest tests/integration/a2a/test_a2a_core_communication.py -v

# Performance tests
pytest tests/integration/a2a/test_performance_load.py -v

# With markers
pytest -m a2a -v
```

### Run with Coverage

```bash
pytest tests/integration/a2a/ --cov=infrastructure.a2a --cov-report=html
```

## Key Fixtures

### `test_a2a_server`

Provides an isolated A2A server instance for testing.

### `agent_simulator`

Provides simulated agents with realistic behaviors.

### `registered_agents`

Pre-registers all agents with the test server.

### `orchestrator_agent`

Provides the NEXUS orchestrator for coordination tests.

### `sample_messages`

Common test messages for various scenarios.

## Performance Benchmarks

Current performance metrics (as of August 2025):

- **Message Latency**: < 50ms (p95)
- **Throughput**: 500+ messages/second
- **Concurrent Connections**: 200+
- **Recovery Time**: < 2 seconds
- **Memory Usage**: < 500MB under load

## Best Practices

1. **Use Fixtures**: Always use provided fixtures for consistency
2. **Async/Await**: All tests should be async for realistic simulation
3. **Timeouts**: Set appropriate timeouts (default 10s, max 30s)
4. **Cleanup**: Ensure proper cleanup in test teardown
5. **Isolation**: Each test should be independent

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Test server automatically finds free ports
2. **Timeout Errors**: Increase timeout in fixture configuration
3. **Import Errors**: Ensure backend is in PYTHONPATH
4. **Async Warnings**: Use pytest-asyncio mode="auto"

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG pytest tests/integration/a2a/ -v -s
```

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] gRPC implementation for better performance
- [ ] Distributed testing across multiple nodes
- [ ] Chaos engineering tests
- [ ] Security penetration testing

## Contributing

When adding new A2A tests:

1. Follow existing patterns in test files
2. Add appropriate fixtures in conftest.py
3. Document new test scenarios
4. Ensure tests are deterministic
5. Add performance benchmarks if relevant

## Related Documentation

- [A+ Agent Standardization](./A+_AGENT_STANDARDIZATION.md)
- [Beta Validation Guide](./BETA_VALIDATION_GUIDE.md)
- [Agent Architecture](./AGENT_ARCHITECTURE.md)
