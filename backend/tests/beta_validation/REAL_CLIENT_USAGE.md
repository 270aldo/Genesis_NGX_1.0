# Real Orchestrator Client Usage Guide

This guide explains how to use the Real Orchestrator Client for Beta Validation testing.

## Overview

The `RealOrchestratorClient` allows you to test against the actual GENESIS orchestrator system instead of mocks, providing accurate validation of system behavior.

## Key Features

- **Test Mode**: Isolates tests using in-memory storage and test database
- **Health Checks**: Verifies orchestrator is functioning before tests
- **Error Handling**: Robust error handling and recovery
- **Test Agents**: Automatically registers minimal test agents
- **Environment Isolation**: Preserves original environment variables

## Usage

### 1. Basic Test

Test the real client in isolation:

```bash
python tests/beta_validation/test_real_client.py
```

### 2. Compare Mock vs Real

Compare behavior between mock and real clients:

```bash
python tests/beta_validation/compare_clients.py
```

### 3. Run Beta Validation with Real Orchestrator

Run the full beta validation suite with the real orchestrator:

```bash
# Test mode with mock AI (no costs)
python -m tests.beta_validation.run_beta_validation --use-real-orchestrator

# Test mode with real AI (WARNING: costs money!)
python -m tests.beta_validation.run_beta_validation --use-real-orchestrator --use-real-ai

# Run specific category
python -m tests.beta_validation.run_beta_validation --use-real-orchestrator --category user_frustration

# Verbose output
python -m tests.beta_validation.run_beta_validation --use-real-orchestrator --verbose
```

## Configuration

The Real Orchestrator Client supports these configuration options:

```python
client = RealOrchestratorClient(
    test_mode=True,      # Use test database and in-memory storage
    use_real_ai=False    # Use mock AI models (no costs)
)
```

## Test Environment

When `test_mode=True`, the client:

1. Uses Redis database 15 (test database)
2. Sets `GENESIS_ENV=test`
3. Enables mock AI models by default
4. Creates isolated state manager
5. Registers minimal test agents

## Test Agents

The following test agents are automatically registered:

- **BLAZE**: Elite Training Strategist
- **SAGE**: Precision Nutrition Architect
- **SPARK**: Motivation & Behavior Coach
- **LUNA**: Female Wellness Coach
- **STELLA**: Progress Tracker

These agents provide minimal responses for testing orchestration logic.

## Health Check

The client includes a health check method:

```python
health = await client.health_check()
# Returns:
# {
#     "status": "healthy",
#     "healthy": True,
#     "orchestrator_connected": True,
#     "test_mode": True,
#     "use_real_ai": False,
#     "response_received": True
# }
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis is running: `redis-cli ping`
   - Check Redis URL configuration

2. **Orchestrator Not Connected**
   - Check A2A adapter is properly initialized
   - Verify network connectivity

3. **Missing Dependencies**
   - Run: `pip install -r requirements.txt`
   - Ensure all NGX components are installed

4. **Test Failures**
   - Check logs in `logs/` directory
   - Run health check first
   - Try with `--verbose` flag

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python tests/beta_validation/test_real_client.py
```

## Best Practices

1. **Always use test mode** for validation tests
2. **Run health check** before full test suite
3. **Use mock AI** unless testing AI responses specifically
4. **Clean up resources** with `await client.cleanup()`
5. **Monitor logs** for detailed error information

## Example Test

```python
import asyncio
from tests.beta_validation.real_orchestrator_client import RealOrchestratorClient
from app.schemas.chat import ChatRequest

async def test_orchestrator():
    client = RealOrchestratorClient(test_mode=True)
    
    try:
        await client.initialize()
        
        request = ChatRequest(
            text="Necesito ayuda con mi plan de entrenamiento",
            user_id="test-user",
            session_id="test-session"
        )
        
        response = await client.process_message(request)
        print(f"Response: {response.response}")
        print(f"Agents used: {response.agents_used}")
        
    finally:
        await client.cleanup()

asyncio.run(test_orchestrator())
```

## Next Steps

1. Run `test_real_client.py` to verify setup
2. Run `compare_clients.py` to check behavior consistency
3. Run full beta validation with `--use-real-orchestrator`
4. Review reports in `reports/` directory