# Contract Testing for GENESIS API

This directory contains contract tests to ensure API stability and prevent breaking changes between frontend and backend components.

## Testing Strategy

### 1. OpenAPI Schema Validation

- Validates all API endpoints against OpenAPI specification
- Ensures request/response schemas match documentation
- Catches schema drift and breaking changes

### 2. A2A Agent Contract Testing

- Custom framework for agent-to-agent communication validation
- Tests message schemas between agents
- Validates streaming response contracts

### 3. WebSocket Contract Testing

- Real-time communication contract validation
- Message format and protocol compliance
- Connection lifecycle testing

## Running Contract Tests

```bash
# Run all contract tests
make test-contract

# Run only OpenAPI tests
pytest tests/contract/openapi/ -v

# Run only A2A contract tests
pytest tests/contract/a2a/ -v

# Run WebSocket contract tests
pytest tests/contract/websocket/ -v

# Generate contract test report
pytest tests/contract/ --html=contract-report.html
```

## Test Categories

### API Contract Tests

- `/health` - Health check endpoint
- `/auth/*` - Authentication endpoints
- `/agents/*` - Agent management endpoints
- `/chat/*` - Chat and conversation endpoints
- `/voice/*` - Voice interaction endpoints
- `/wearables/*` - Wearable device integration

### A2A Contract Tests

- Agent registration and discovery
- Message routing and delivery
- Streaming response handling
- Error propagation and handling
- Agent coordination protocols

### WebSocket Contract Tests

- Connection establishment
- Message broadcasting
- Real-time updates
- Connection cleanup

## Adding New Contract Tests

1. Create test file in appropriate subdirectory
2. Use `BaseContractTest` class for common functionality
3. Follow naming convention: `test_contract_[endpoint/feature].py`
4. Include both positive and negative test cases
5. Add schema validation for all request/response pairs

## Contract Test Failure Handling

When contract tests fail:

1. **Schema Mismatch**: Update either implementation or documentation
2. **Breaking Changes**: Implement API versioning
3. **A2A Protocol Changes**: Update all affected agents
4. **WebSocket Changes**: Update both client and server implementations

## Maintenance

Contract tests should be updated when:

- New API endpoints are added
- Existing endpoints are modified
- New agents are introduced
- WebSocket protocols change
- Response formats are updated
