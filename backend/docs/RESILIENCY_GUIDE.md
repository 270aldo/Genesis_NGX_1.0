# 🛡️ GENESIS Resiliency Guide

## Table of Contents
1. [Overview](#overview)
2. [Resiliency Patterns](#resiliency-patterns)
3. [Circuit Breaker Pattern](#circuit-breaker-pattern)
4. [Retry Pattern](#retry-pattern)
5. [Timeout Pattern](#timeout-pattern)
6. [Bulkhead Pattern](#bulkhead-pattern)
7. [Graceful Degradation](#graceful-degradation)
8. [Health Checks](#health-checks)
9. [Monitoring & Alerts](#monitoring--alerts)
10. [Chaos Engineering](#chaos-engineering)
11. [Best Practices](#best-practices)
12. [Emergency Procedures](#emergency-procedures)

## Overview

GENESIS implements enterprise-grade resiliency patterns to ensure 99.9% uptime and graceful handling of failures. This guide documents all resiliency mechanisms and how to configure, test, and monitor them.

### Key Principles

1. **Fail Fast**: Detect failures quickly and respond appropriately
2. **Isolate Failures**: Prevent cascading failures across components
3. **Graceful Degradation**: Provide reduced functionality rather than complete failure
4. **Self-Healing**: Automatic recovery from transient failures
5. **Observability**: Comprehensive monitoring and alerting

## Resiliency Patterns

### Pattern Overview

| Pattern | Purpose | Implementation | Use Case |
|---------|---------|----------------|----------|
| Circuit Breaker | Prevent cascading failures | ADK `CircuitBreaker` class | External API calls |
| Retry | Handle transient failures | ADK `@retry` decorator | Network requests |
| Timeout | Prevent hanging operations | `asyncio.timeout` | All async operations |
| Bulkhead | Isolate resources | Connection pools | Database, Redis |
| Rate Limiting | Prevent overload | `slowapi` | API endpoints |
| Graceful Degradation | Partial service | Feature flags | Non-critical features |

## Circuit Breaker Pattern

### How It Works

The circuit breaker prevents cascading failures by monitoring the success rate of operations and "opening" the circuit when failures exceed a threshold.

```
CLOSED → [failures > threshold] → OPEN → [timeout] → HALF-OPEN → [success] → CLOSED
                                     ↓                     ↓
                                [requests blocked]    [test request]
```

### Implementation

```python
from adk.patterns import CircuitBreaker, CircuitBreakerError

# Create circuit breaker
llm_breaker = CircuitBreaker(
    failure_threshold=5,      # Open after 5 failures
    recovery_timeout=60,      # Try recovery after 60 seconds
    expected_exception=Exception,
    name="llm_service"
)

# Use with decorators
@circuit_breaker(failure_threshold=3, recovery_timeout=30)
async def call_external_api():
    response = await external_api.call()
    return response

# Use programmatically
try:
    result = await llm_breaker.async_call(risky_operation, arg1, arg2)
except CircuitBreakerError as e:
    # Circuit is open, use fallback
    result = get_cached_result() or default_response()
```

### Configuration

```python
# In agents using ADK
class MyAgent(BaseADKAgent, CircuitBreakerMixin):
    def __init__(self):
        super().__init__()
        self.init_circuit_breakers()
        
        # Add circuit breakers for different services
        self.add_circuit_breaker(
            "vertex_ai",
            failure_threshold=5,
            recovery_timeout=60
        )
        
        self.add_circuit_breaker(
            "database",
            failure_threshold=10,
            recovery_timeout=30
        )
```

### Monitoring Circuit Breakers

```python
# Get circuit breaker stats
stats = circuit_breaker.get_stats()
# Returns:
{
    "name": "llm_service",
    "state": "closed",  # closed, open, or half_open
    "failure_count": 2,
    "success_count": 198,
    "total_calls": 200,
    "success_rate": 0.99,
    "last_failure_time": "2025-07-21T10:30:00Z"
}

# Check all circuit breakers in an agent
all_stats = agent.get_circuit_stats()
```

## Retry Pattern

### Retry Policies

```python
from adk.patterns import retry, RetryPolicy, CommonRetryPolicies

# Simple retry with exponential backoff
@retry(max_attempts=3, initial_delay=1.0, backoff_factor=2.0)
async def unreliable_operation():
    return await external_service.call()

# Use predefined policies
@retry(policy=CommonRetryPolicies.api_calls())
async def call_api():
    # Retries 3 times with exponential backoff
    # Only on ConnectionError, TimeoutError
    pass

@retry(policy=CommonRetryPolicies.database())
async def query_database():
    # Retries 5 times with jitter
    # Very short initial delay (0.1s)
    pass

# Custom retry policy
custom_policy = RetryPolicy(
    max_attempts=5,
    initial_delay=0.5,
    max_delay=30.0,
    backoff_factor=1.5,
    jitter=True,
    retry_on=(HTTPError, TimeoutError),
    dont_retry_on=(ValueError, AuthenticationError),
    on_retry=lambda e, attempt: logger.warning(f"Retry {attempt}: {e}"),
    on_failure=lambda e, attempts: alert_team(f"Failed after {attempts} attempts")
)

@retry(policy=custom_policy)
async def critical_operation():
    pass
```

### Retry with Circuit Breaker

```python
# Combine patterns for maximum resilience
@circuit_breaker(failure_threshold=5)
@retry(max_attempts=3)
@timeout(30)
async def resilient_operation():
    # This operation will:
    # 1. Timeout after 30 seconds
    # 2. Retry up to 3 times on failure
    # 3. Open circuit breaker after 5 consecutive failures
    return await external_service.call()
```

## Timeout Pattern

### Implementation

```python
import asyncio
from adk.core.exceptions import AgentTimeoutError

# Using asyncio timeout
async def operation_with_timeout():
    try:
        async with asyncio.timeout(30):  # 30 second timeout
            result = await long_running_operation()
            return result
    except asyncio.TimeoutError:
        logger.error("Operation timed out after 30 seconds")
        raise AgentTimeoutError("Operation timeout")

# In ADK agents
class MyAgent(BaseADKAgent):
    async def _execute_core(self, request: AgentRequest):
        # Request timeout is automatically enforced
        # Use request.timeout or self.config.timeout
        
        # For specific operations
        try:
            result = await asyncio.wait_for(
                self.llm_client.generate(prompt),
                timeout=min(request.timeout, 60)  # Max 60 seconds
            )
        except asyncio.TimeoutError:
            # Use cached or degraded response
            return self.get_cached_response(request)
```

### Timeout Configuration

```yaml
# Environment variables
AGENT_DEFAULT_TIMEOUT=30
LLM_TIMEOUT=60
DATABASE_TIMEOUT=10
REDIS_TIMEOUT=5

# Per-request timeout
request = AgentRequest(
    prompt="...",
    timeout=45  # Override default
)
```

## Bulkhead Pattern

### Resource Isolation

```python
# Database connection pool
from core.database import DatabasePool

db_pool = DatabasePool(
    min_connections=5,
    max_connections=20,
    max_overflow=5,
    pool_timeout=30,
    recycle=3600  # Recycle connections after 1 hour
)

# Redis connection pool
from core.redis_pool import RedisPoolManager

redis_pool = RedisPoolManager(
    max_connections=50,
    max_connections_per_db=10,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True
)

# Separate thread pools for CPU-intensive operations
import concurrent.futures

cpu_executor = concurrent.futures.ProcessPoolExecutor(
    max_workers=4,
    mp_context=multiprocessing.get_context('spawn')
)

io_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=10,
    thread_name_prefix='io_worker'
)
```

### Agent Isolation

```python
# Isolate agent resources
class IsolatedAgent(BaseADKAgent):
    def __init__(self):
        super().__init__()
        
        # Dedicated connection pools
        self.db_pool = DatabasePool(max_connections=5)
        self.redis_pool = RedisPoolManager(max_connections=10)
        
        # Separate circuit breakers
        self.init_circuit_breakers()
        
        # Resource limits
        self.max_concurrent_requests = 10
        self.semaphore = asyncio.Semaphore(self.max_concurrent_requests)
    
    async def execute(self, request):
        async with self.semaphore:  # Limit concurrent requests
            return await super().execute(request)
```

## Graceful Degradation

### Feature Flags for Degradation

```python
from core.feature_flags import FeatureFlags

flags = FeatureFlags()

class ResilientAgent(BaseADKAgent):
    async def _execute_core(self, request):
        # Check if advanced features are enabled
        if flags.is_enabled("advanced_llm_features"):
            try:
                return await self.advanced_processing(request)
            except Exception as e:
                logger.warning(f"Advanced processing failed: {e}")
                # Fall back to basic processing
        
        # Basic processing (always available)
        return await self.basic_processing(request)
    
    async def get_recommendations(self, user_id):
        # Try real-time calculation
        if flags.is_enabled("realtime_recommendations"):
            try:
                return await self.calculate_realtime_recommendations(user_id)
            except Exception:
                pass
        
        # Fall back to cached recommendations
        cached = await self.redis_client.get(f"recommendations:{user_id}")
        if cached:
            return cached
        
        # Ultimate fallback: generic recommendations
        return self.get_generic_recommendations()
```

### Degraded Mode Router

```python
from app.routers.degraded_mode import degraded_mode_manager

@router.get("/status")
async def get_status():
    if degraded_mode_manager.is_degraded:
        return {
            "status": "degraded",
            "message": "Some features may be limited",
            "affected_services": degraded_mode_manager.affected_services,
            "estimated_recovery": degraded_mode_manager.estimated_recovery
        }
    
    return {"status": "healthy", "all_systems": "operational"}
```

## Health Checks

### Multi-Level Health Checks

```python
# Level 1: Basic liveness
@router.get("/health/live")
async def liveness():
    """Basic check - is the service running?"""
    return {"status": "alive"}

# Level 2: Readiness check
@router.get("/health/ready")
async def readiness():
    """Can the service handle requests?"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "llm": await check_llm_service()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "ready": all_healthy,
            "checks": checks
        }
    )

# Level 3: Detailed health
@router.get("/health/detailed")
async def detailed_health(
    current_user: Dict = Depends(get_current_user)
):
    """Detailed health information (requires auth)"""
    
    # Collect health from all components
    health_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "uptime": get_uptime(),
        "components": {}
    }
    
    # Check each agent
    for agent_id, agent in agent_registry.items():
        try:
            agent_health = await agent.health_check()
            health_data["components"][agent_id] = agent_health
        except Exception as e:
            health_data["components"][agent_id] = {
                "healthy": False,
                "error": str(e)
            }
    
    # Check infrastructure
    health_data["infrastructure"] = {
        "database": await check_database_detailed(),
        "redis": await check_redis_detailed(),
        "circuit_breakers": get_all_circuit_breaker_stats(),
        "resource_usage": get_resource_usage()
    }
    
    return health_data
```

### Automated Health Monitoring

```python
# Background health monitor
class HealthMonitor:
    def __init__(self):
        self.unhealthy_components = set()
        self.health_history = deque(maxlen=100)
    
    async def run(self):
        """Run continuous health monitoring"""
        while True:
            try:
                health = await self.check_system_health()
                self.health_history.append(health)
                
                # Detect state changes
                newly_unhealthy = health["unhealthy"] - self.unhealthy_components
                newly_healthy = self.unhealthy_components - health["unhealthy"]
                
                # Alert on changes
                for component in newly_unhealthy:
                    await self.alert_unhealthy(component)
                
                for component in newly_healthy:
                    await self.alert_recovered(component)
                
                self.unhealthy_components = health["unhealthy"]
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
            
            await asyncio.sleep(30)  # Check every 30 seconds
```

## Monitoring & Alerts

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
request_total = Counter(
    'genesis_requests_total',
    'Total requests',
    ['agent', 'method', 'status']
)

request_duration = Histogram(
    'genesis_request_duration_seconds',
    'Request duration',
    ['agent', 'method']
)

circuit_breaker_state = Gauge(
    'genesis_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half-open)',
    ['service']
)

error_rate = Gauge(
    'genesis_error_rate',
    'Current error rate',
    ['agent']
)

# Export circuit breaker metrics
def export_circuit_breaker_metrics():
    for name, cb in all_circuit_breakers.items():
        stats = cb.get_stats()
        state_value = {
            'closed': 0,
            'open': 1,
            'half_open': 2
        }[stats['state']]
        circuit_breaker_state.labels(service=name).set(state_value)
```

### Alert Rules

```yaml
# prometheus/alerts.yml
groups:
  - name: genesis_alerts
    rules:
      # Circuit breaker alerts
      - alert: CircuitBreakerOpen
        expr: genesis_circuit_breaker_state > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Circuit breaker {{ $labels.service }} is open"
          description: "Circuit breaker for {{ $labels.service }} has been open for more than 1 minute"
      
      # Error rate alerts
      - alert: HighErrorRate
        expr: genesis_error_rate > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate for {{ $labels.agent }}"
          description: "Error rate for {{ $labels.agent }} is {{ $value | humanizePercentage }}"
      
      # Performance alerts
      - alert: SlowResponse
        expr: histogram_quantile(0.95, genesis_request_duration_seconds) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow responses detected"
          description: "95th percentile response time is {{ $value }}s"
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "GENESIS Resiliency Dashboard",
    "panels": [
      {
        "title": "Circuit Breaker Status",
        "targets": [{
          "expr": "genesis_circuit_breaker_state",
          "legendFormat": "{{ service }}"
        }]
      },
      {
        "title": "Request Success Rate",
        "targets": [{
          "expr": "rate(genesis_requests_total{status='success'}[5m]) / rate(genesis_requests_total[5m])",
          "legendFormat": "{{ agent }}"
        }]
      },
      {
        "title": "Retry Attempts",
        "targets": [{
          "expr": "rate(genesis_retry_attempts_total[5m])",
          "legendFormat": "{{ operation }}"
        }]
      },
      {
        "title": "Timeout Errors",
        "targets": [{
          "expr": "rate(genesis_timeout_errors_total[5m])",
          "legendFormat": "{{ agent }}"
        }]
      }
    ]
  }
}
```

## Chaos Engineering

### Chaos Testing Framework

```python
from app.routers.chaos_testing import ChaosTestingManager

chaos_manager = ChaosTestingManager()

# Configure chaos scenarios
chaos_manager.add_scenario(
    "network_latency",
    probability=0.1,  # 10% of requests
    latency_ms=1000,  # Add 1 second latency
    affected_services=["llm_service"]
)

chaos_manager.add_scenario(
    "service_failure",
    probability=0.05,  # 5% of requests
    error_type=ConnectionError,
    affected_services=["database"]
)

chaos_manager.add_scenario(
    "cpu_spike",
    probability=0.02,  # 2% of requests
    cpu_load=0.8,  # 80% CPU usage
    duration_seconds=10
)

# Enable chaos testing in staging
if settings.ENVIRONMENT == "staging":
    chaos_manager.enable()
```

### Chaos Test Scenarios

```python
# Test circuit breaker behavior
async def test_circuit_breaker_opens_on_failures():
    # Force failures
    chaos_manager.force_scenario("service_failure", probability=1.0)
    
    # Make requests until circuit opens
    for i in range(10):
        try:
            await agent.execute(request)
        except Exception:
            pass
    
    # Verify circuit is open
    assert agent.llm_circuit_breaker.state == CircuitState.OPEN

# Test graceful degradation
async def test_graceful_degradation():
    # Disable primary service
    chaos_manager.disable_service("llm_service")
    
    # Should still get response (degraded)
    response = await agent.execute(request)
    assert response.success
    assert response.metadata.get("degraded") == True

# Test retry behavior
async def test_retry_recovers_from_transient_failure():
    # Fail first 2 attempts
    chaos_manager.add_scenario(
        "transient_failure",
        probability=1.0,
        max_occurrences=2
    )
    
    # Should succeed on 3rd attempt
    response = await agent.execute(request)
    assert response.success
    assert response.metadata.get("retry_count") == 2
```

## Best Practices

### 1. Design for Failure

```python
class ResilientService:
    def __init__(self):
        # Always have fallbacks
        self.primary_llm = VertexAIClient()
        self.fallback_llm = OpenAIClient()
        self.cache = RedisCache()
        
    async def generate(self, prompt):
        # Try primary
        try:
            return await self.primary_llm.generate(prompt)
        except Exception as e:
            logger.warning(f"Primary LLM failed: {e}")
        
        # Try fallback
        try:
            return await self.fallback_llm.generate(prompt)
        except Exception as e:
            logger.warning(f"Fallback LLM failed: {e}")
        
        # Use cache
        cached = await self.cache.get_similar(prompt)
        if cached:
            return cached
        
        # Ultimate fallback
        return self.get_static_response(prompt)
```

### 2. Set Appropriate Timeouts

```python
# Cascade timeouts
TOTAL_REQUEST_TIMEOUT = 60
LLM_TIMEOUT = 30
DATABASE_TIMEOUT = 10
REDIS_TIMEOUT = 5

async def handle_request(request):
    async with asyncio.timeout(TOTAL_REQUEST_TIMEOUT):
        # Each operation has its own timeout
        llm_task = asyncio.create_task(
            asyncio.wait_for(llm_generate(), LLM_TIMEOUT)
        )
        
        db_task = asyncio.create_task(
            asyncio.wait_for(db_query(), DATABASE_TIMEOUT)
        )
        
        # Can proceed with partial results
        results = await asyncio.gather(
            llm_task, db_task, 
            return_exceptions=True
        )
```

### 3. Monitor Everything

```python
# Comprehensive monitoring
class MonitoredOperation:
    def __init__(self, name: str):
        self.name = name
        self.metrics = {
            "requests": Counter(f"{name}_requests_total"),
            "errors": Counter(f"{name}_errors_total"),
            "duration": Histogram(f"{name}_duration_seconds"),
            "in_progress": Gauge(f"{name}_in_progress")
        }
    
    async def __aenter__(self):
        self.start_time = time.time()
        self.metrics["requests"].inc()
        self.metrics["in_progress"].inc()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.metrics["duration"].observe(duration)
        self.metrics["in_progress"].dec()
        
        if exc_type:
            self.metrics["errors"].inc()
            logger.error(
                f"Operation {self.name} failed",
                extra={
                    "duration": duration,
                    "error": str(exc_val)
                }
            )
```

### 4. Test Resiliency

```python
# Resiliency test suite
class ResiliencyTests:
    @pytest.mark.resiliency
    async def test_handles_database_outage(self):
        # Simulate database down
        with mock.patch('db.connect', side_effect=ConnectionError):
            response = await api_client.get("/health")
            assert response.status_code == 503
            assert response.json()["degraded"] == True
    
    @pytest.mark.resiliency
    async def test_recovers_from_redis_failure(self):
        # Simulate Redis failure then recovery
        redis_mock = AsyncMock()
        redis_mock.get.side_effect = [
            ConnectionError(), 
            ConnectionError(),
            "cached_value"  # Recovers on 3rd attempt
        ]
        
        with mock.patch('redis_client', redis_mock):
            result = await get_with_cache("key")
            assert result == "cached_value"
```

## Emergency Procedures

### 1. Circuit Breaker Stuck Open

```python
# Manual reset procedure
async def emergency_reset_circuit_breaker(service_name: str):
    """Emergency procedure to reset a stuck circuit breaker"""
    
    # 1. Log the emergency action
    logger.critical(
        f"EMERGENCY: Manually resetting circuit breaker for {service_name}",
        extra={"operator": current_user.id, "reason": reason}
    )
    
    # 2. Get the circuit breaker
    cb = circuit_breaker_registry.get(service_name)
    if not cb:
        raise ValueError(f"No circuit breaker found for {service_name}")
    
    # 3. Check current state
    stats = cb.get_stats()
    logger.info(f"Current state: {stats}")
    
    # 4. Reset the circuit breaker
    cb.reset()
    
    # 5. Test with a canary request
    try:
        await cb.async_call(health_check_operation)
        logger.info(f"Circuit breaker {service_name} successfully reset")
    except Exception as e:
        logger.error(f"Circuit breaker test failed: {e}")
        raise
    
    # 6. Alert team
    await alert_team(
        f"Circuit breaker {service_name} was manually reset",
        severity="warning"
    )
```

### 2. Complete Service Degradation

```python
# Emergency degraded mode
async def activate_emergency_mode():
    """Activate emergency degraded mode for all services"""
    
    logger.critical("ACTIVATING EMERGENCY DEGRADED MODE")
    
    # 1. Enable all feature flags for degraded mode
    await feature_flags.enable_all([
        "use_cached_responses",
        "disable_realtime_features",
        "use_static_recommendations",
        "minimal_processing_mode"
    ])
    
    # 2. Increase all cache TTLs
    await cache_manager.set_emergency_ttls({
        "default": 3600,  # 1 hour
        "user_data": 7200,  # 2 hours
        "recommendations": 86400  # 24 hours
    })
    
    # 3. Reduce resource limits
    for agent in agent_registry.values():
        agent.config.max_tokens = 500
        agent.config.timeout = 10
    
    # 4. Notify all users
    await broadcast_message({
        "type": "emergency",
        "message": "System operating in limited capacity",
        "estimated_recovery": "2 hours"
    })
```

### 3. Recovery Procedures

```python
# Gradual recovery from incident
class RecoveryManager:
    async def gradual_recovery(self):
        """Gradually restore services after incident"""
        
        stages = [
            {
                "name": "Stage 1: Core Services",
                "duration": 300,  # 5 minutes
                "actions": [
                    self.enable_core_agents,
                    self.restore_database_connections,
                    self.test_critical_paths
                ]
            },
            {
                "name": "Stage 2: Secondary Services",
                "duration": 600,  # 10 minutes
                "actions": [
                    self.enable_all_agents,
                    self.restore_normal_timeouts,
                    self.reduce_cache_ttls
                ]
            },
            {
                "name": "Stage 3: Full Service",
                "duration": 900,  # 15 minutes
                "actions": [
                    self.disable_degraded_mode,
                    self.restore_all_features,
                    self.clear_emergency_caches
                ]
            }
        ]
        
        for stage in stages:
            logger.info(f"Starting recovery {stage['name']}")
            
            # Execute stage actions
            for action in stage["actions"]:
                try:
                    await action()
                except Exception as e:
                    logger.error(f"Recovery action failed: {e}")
                    # Rollback to previous stage
                    return await self.rollback_recovery(stage)
            
            # Monitor for stability
            await self.monitor_stability(stage["duration"])
            
            # Check metrics before proceeding
            if not await self.check_health_metrics():
                logger.warning("Health metrics not stable, pausing recovery")
                return await self.pause_recovery(stage)
        
        logger.info("Full recovery completed successfully")
        await self.notify_recovery_complete()
```

## Summary

GENESIS implements comprehensive resiliency patterns to ensure reliable service even under adverse conditions. Key takeaways:

1. **Layer resiliency patterns**: Combine circuit breakers, retries, and timeouts
2. **Monitor proactively**: Track all metrics and set up alerts
3. **Test regularly**: Use chaos engineering to validate resiliency
4. **Plan for failure**: Have degradation strategies and emergency procedures
5. **Automate recovery**: Implement self-healing mechanisms where possible

Remember: **Failures are inevitable, but outages are preventable with proper resiliency patterns.**