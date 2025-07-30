# Beta Validation with Real Orchestrator

This document explains how to run beta validation tests using the real GENESIS orchestrator instead of mocks.

## Overview

The beta validation tests can now run in three modes:

1. **Simple Mock Mode** - Basic mock responses (fast, limited)
2. **Intelligent Mock Mode** - Context-aware mock responses (default)
3. **Real Orchestrator Mode** - Uses actual GENESIS system (most accurate)

## Why Use Real Orchestrator Testing?

Using the real orchestrator provides:
- **Accurate system behavior** - Tests actual code paths and integrations
- **Real agent interactions** - Validates multi-agent coordination
- **True performance metrics** - Measures actual response times
- **Integration validation** - Ensures all components work together

## Prerequisites

Before running real orchestrator tests:

1. Ensure Redis is running (for caching and state management)
2. Set up test database or use in-memory storage
3. Configure test environment variables
4. (Optional) Set up Vertex AI credentials for real AI responses

## Running Tests with Real Orchestrator

### Basic Test Run

```bash
# Run with real orchestrator (uses mock AI)
python -m tests.beta_validation.run_beta_validation --use-real-orchestrator

# Run specific category
python -m tests.beta_validation.run_beta_validation --use-real-orchestrator --category user_frustration

# Run with verbose output
python -m tests.beta_validation.run_beta_validation --use-real-orchestrator --verbose
```

### Advanced Options

```bash
# Use real AI services (WARNING: costs money!)
python -m tests.beta_validation.run_beta_validation --use-real-orchestrator --use-real-ai

# Run tests in parallel (faster but uses more resources)
python -m tests.beta_validation.run_beta_validation --use-real-orchestrator --parallel

# Generate detailed report
python -m tests.beta_validation.run_beta_validation --use-real-orchestrator --report
```

## Test Scripts

### 1. Test Real Orchestrator Connection

```bash
# Basic connection test
python tests/beta_validation/test_real_orchestrator.py

# Test with scenario execution
python tests/beta_validation/test_real_orchestrator.py --scenario
```

### 2. Compare Mock vs Real Responses

```bash
# Run comparison suite
python tests/beta_validation/compare_mock_vs_real.py
```

This generates a report showing:
- Agent selection differences
- Response quality comparison
- Behavioral gaps between mock and real

## Configuration

### Test Environment Settings

The `TestSettings` class in `test_config.py` controls:
- `use_test_database`: Use in-memory or test database
- `disable_external_services`: Disable external API calls
- `a2a_timeout`: Timeout for agent-to-agent calls
- `telemetry_enabled`: Enable/disable telemetry

### Real AI vs Mock AI

When using `--use-real-orchestrator` without `--use-real-ai`:
- Orchestrator logic is real
- Agent routing is real
- AI responses are mocked (predictable, free)

When adding `--use-real-ai`:
- Everything uses production code
- Vertex AI generates real responses
- **WARNING**: This costs money!

## Understanding Results

### Real Orchestrator Response Structure

```json
{
  "response": "Actual orchestrator response text",
  "agents_used": ["NEXUS", "BLAZE", "SAGE"],
  "agent_responses": [
    {
      "agent_id": "elite_training_strategist",
      "agent_name": "BLAZE",
      "response": "Agent-specific response",
      "confidence": 0.85
    }
  ],
  "metadata": {
    "real_orchestrator": true,
    "test_mode": true,
    "orchestration": {
      "intent": "fitness_guidance",
      "routing_strategy": "parallel"
    }
  }
}
```

### Key Differences from Mocks

1. **Dynamic Agent Selection** - Real intent analysis determines agents
2. **Actual Processing Time** - Real latency measurements
3. **Error Handling** - Real error paths and recovery
4. **State Management** - Real session and context handling

## Troubleshooting

### Common Issues

1. **"Failed to initialize Real Orchestrator Client"**
   - Check Redis is running
   - Verify test database configuration
   - Check logs for specific errors

2. **"Agent not found" errors**
   - Test agents may not be fully registered
   - Check agent registry initialization

3. **Timeout errors**
   - Adjust `a2a_timeout` in test config
   - Check if agents are responding

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python -m tests.beta_validation.run_beta_validation --use-real-orchestrator --verbose
```

## Best Practices

1. **Start with mock testing** - Validate test scenarios work
2. **Move to real orchestrator** - Verify actual behavior
3. **Use real AI sparingly** - Only for final validation
4. **Monitor resource usage** - Real tests use more CPU/memory
5. **Clean up after tests** - Ensure test data is removed

## CI/CD Integration

For automated testing:

```yaml
# Example GitHub Actions workflow
- name: Run Beta Validation (Mock)
  run: python -m tests.beta_validation.run_beta_validation --quick

- name: Run Beta Validation (Real Orchestrator)
  run: python -m tests.beta_validation.run_beta_validation --use-real-orchestrator --category edge_cases
  if: github.event_name == 'pull_request'

- name: Run Full Validation (Real AI)
  run: python -m tests.beta_validation.run_beta_validation --use-real-orchestrator --use-real-ai
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

## Extending Real Tests

To add new real orchestrator tests:

1. Create test scenarios in `scenarios/`
2. Ensure they work with `ChatRequest`/`ChatResponse` schemas
3. Test with mock first, then real orchestrator
4. Document expected vs actual behavior differences