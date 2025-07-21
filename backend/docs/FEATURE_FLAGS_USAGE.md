# Feature Flags Usage Guide

## Overview

The GENESIS Feature Flags system enables:
- **Gradual Feature Rollout**: Deploy features to a percentage of users
- **A/B Testing**: Test different variants with user segments
- **Kill Switches**: Instantly disable problematic features
- **Scheduled Releases**: Automatically enable/disable features by date
- **User Targeting**: Enable features for specific users or segments

## Quick Start

### 1. Basic Boolean Flag

```python
from core.feature_flags import get_feature_flags

# Check if feature is enabled
manager = await get_feature_flags()
if await manager.is_enabled("new_workout_algorithm", context={"user_id": user_id}):
    result = await new_algorithm()
else:
    result = await legacy_algorithm()
```

### 2. Using Decorators

```python
from core.feature_flags import feature_flag

@feature_flag("premium_features", default=False)
async def premium_workout_analysis(user_id: str, data: dict):
    # This function only executes if flag is enabled
    return await advanced_analysis(data)

# The decorator automatically checks the flag
result = await premium_workout_analysis(user_id="123", data={...})
```

### 3. A/B Testing with Variants

```python
from core.feature_flags import variant_flag

@variant_flag("checkout_flow", default_variant="control")
async def process_checkout(variant: str, user_id: str, cart: dict):
    if variant == "streamlined":
        return await new_checkout_flow(cart)
    elif variant == "one_click":
        return await one_click_checkout(cart)
    else:
        return await standard_checkout(cart)
```

## Configuration Examples

### 1. Percentage Rollout

```python
# Create a flag that's enabled for 20% of users
flag = FeatureFlag(
    name="new_onboarding_flow",
    description="Gradual rollout of new onboarding",
    type=FlagType.PERCENTAGE,
    target_percentage=20,  # 20% of users
    default_value=False
)
```

### 2. User List Targeting

```python
# Enable for specific beta testers
flag = FeatureFlag(
    name="beta_features",
    description="Features for beta testers",
    type=FlagType.USER_LIST,
    target_users=["user123", "user456", "user789"],
    default_value=False
)
```

### 3. Scheduled Feature

```python
# Enable feature during specific time window
flag = FeatureFlag(
    name="black_friday_sale",
    description="Black Friday special features",
    type=FlagType.SCHEDULE,
    start_date=datetime(2025, 11, 29),
    end_date=datetime(2025, 11, 30, 23, 59, 59),
    default_value=False
)
```

### 4. A/B Test Configuration

```python
# Configure variants for A/B testing
flag = FeatureFlag(
    name="recommendation_algorithm",
    description="Test different recommendation algorithms",
    type=FlagType.VARIANT,
    variants={
        "control": {"algorithm": "collaborative_filtering"},
        "treatment_a": {"algorithm": "neural_network"},
        "treatment_b": {"algorithm": "hybrid_approach"}
    },
    default_value="control"
)
```

## Integration with Agents

### 1. Agent with Feature Flags

```python
from adk.core import BaseADKAgent
from core.feature_flags import get_feature_flags

class EnhancedTrainingAgent(BaseADKAgent):
    async def _execute_core(self, request):
        manager = await get_feature_flags()
        
        # Check multiple features
        context = {"user_id": request.user_id}
        
        use_ai_coaching = await manager.is_enabled("ai_coaching", context)
        use_voice_feedback = await manager.is_enabled("voice_feedback", context)
        
        # Get A/B test variant
        workout_style = await manager.get_variant("workout_style", context)
        
        # Build response based on flags
        response = await self.generate_base_workout(request)
        
        if use_ai_coaching:
            response = await self.add_ai_coaching(response)
        
        if use_voice_feedback:
            response = await self.add_voice_instructions(response)
        
        if workout_style == "gamified":
            response = await self.gamify_workout(response)
        
        return response
```

### 2. Graceful Degradation

```python
class ResilientAgent(BaseADKAgent):
    async def _execute_core(self, request):
        manager = await get_feature_flags()
        
        # Check if advanced features are available
        if await manager.is_enabled("advanced_llm_features"):
            try:
                return await self.advanced_processing(request)
            except Exception as e:
                logger.error(f"Advanced processing failed: {e}")
                # Fall back to basic processing
        
        # Always available basic processing
        return await self.basic_processing(request)
```

## API Usage

### 1. List All Flags

```bash
GET /api/v1/feature-flags/
Authorization: Bearer <token>

Response:
[
    {
        "name": "new_workout_algorithm",
        "description": "Test new AI workout generation",
        "type": "percentage",
        "status": "active",
        "target_percentage": 50,
        "default_value": false
    }
]
```

### 2. Evaluate Single Flag

```bash
POST /api/v1/feature-flags/new_workout_algorithm/evaluate
Authorization: Bearer <token>
Content-Type: application/json

{
    "user_id": "user123",
    "user_segment": "premium",
    "metadata": {
        "device": "ios",
        "version": "3.2.1"
    }
}

Response:
{
    "flag_name": "new_workout_algorithm",
    "enabled": true,
    "variant": null,
    "metadata": {
        "evaluated_at": "2025-07-21T10:30:00Z"
    }
}
```

### 3. Bulk Evaluation

```bash
POST /api/v1/feature-flags/evaluate/bulk
Authorization: Bearer <token>
Content-Type: application/json

{
    "flag_names": [
        "ai_coaching",
        "voice_feedback",
        "premium_analytics"
    ],
    "context": {
        "user_id": "user123",
        "user_segment": "premium"
    }
}

Response:
{
    "ai_coaching": {
        "flag_name": "ai_coaching",
        "enabled": true,
        "variant": null
    },
    "voice_feedback": {
        "flag_name": "voice_feedback",
        "enabled": false,
        "variant": null
    },
    "premium_analytics": {
        "flag_name": "premium_analytics",
        "enabled": true,
        "variant": "detailed"
    }
}
```

### 4. Create Flag (Admin Only)

```bash
POST /api/v1/feature-flags/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
    "name": "experimental_feature",
    "description": "Test experimental workout features",
    "type": "percentage",
    "default_value": false,
    "target_percentage": 10,
    "target_segments": ["early_adopters"],
    "start_date": "2025-08-01T00:00:00Z"
}
```

## Best Practices

### 1. Naming Conventions

```python
# Good flag names
"enable_ai_coaching"           # Clear feature toggle
"workout_algorithm_variant"    # Clear A/B test
"premium_analytics_enabled"    # Clear feature gate

# Bad flag names
"test1"                       # Not descriptive
"new_feature"                 # Too vague
"temporary"                   # No context
```

### 2. Context Building

```python
def build_flag_context(user, request):
    """Build comprehensive context for flag evaluation."""
    return {
        "user_id": user.id,
        "user_segment": user.segment,
        "subscription_tier": user.subscription_tier,
        "account_age_days": (datetime.now() - user.created_at).days,
        "device_type": request.headers.get("User-Agent"),
        "app_version": request.headers.get("X-App-Version"),
        "country": user.country,
        "language": user.language
    }
```

### 3. Caching Critical Flags

```python
# Cache flags that are checked frequently
async def initialize_critical_flags():
    manager = await get_feature_flags()
    
    # Cache in memory for 1 minute
    critical_flags = [
        "rate_limiting_enabled",
        "maintenance_mode",
        "emergency_degradation"
    ]
    
    for flag_name in critical_flags:
        flag = await manager.get_flag(flag_name)
        if flag:
            manager.cache_in_memory(flag, ttl_seconds=60)
```

### 4. Monitoring Flag Usage

```python
from prometheus_client import Counter

flag_evaluations = Counter(
    'feature_flag_evaluations_total',
    'Feature flag evaluations',
    ['flag_name', 'result']
)

async def evaluate_with_metrics(flag_name: str, context: dict):
    manager = await get_feature_flags()
    result = await manager.is_enabled(flag_name, context)
    
    # Record metric
    flag_evaluations.labels(
        flag_name=flag_name,
        result="enabled" if result else "disabled"
    ).inc()
    
    return result
```

## Testing with Feature Flags

### 1. Unit Tests

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_with_feature_enabled():
    # Mock feature flag manager
    mock_manager = AsyncMock()
    mock_manager.is_enabled.return_value = True
    
    with patch('core.feature_flags.get_feature_flags', return_value=mock_manager):
        result = await function_with_feature_flag()
        assert result == "new_behavior"

@pytest.mark.asyncio
async def test_with_feature_disabled():
    mock_manager = AsyncMock()
    mock_manager.is_enabled.return_value = False
    
    with patch('core.feature_flags.get_feature_flags', return_value=mock_manager):
        result = await function_with_feature_flag()
        assert result == "legacy_behavior"
```

### 2. Integration Tests

```python
@pytest.mark.integration
async def test_percentage_rollout():
    """Test that percentage rollout is consistent for users."""
    manager = await get_feature_flags()
    
    # Create test flag
    flag = FeatureFlag(
        name="test_rollout",
        type=FlagType.PERCENTAGE,
        target_percentage=50
    )
    await manager.create_flag(flag)
    
    # Test consistency - same user always gets same result
    user_id = "test_user_123"
    results = []
    for _ in range(10):
        enabled = await manager.is_enabled("test_rollout", {"user_id": user_id})
        results.append(enabled)
    
    # All results should be the same
    assert all(r == results[0] for r in results)
```

## Migration Strategy

### 1. Gradual Feature Migration

```python
# Step 1: Create flag at 0%
await create_flag("new_payment_system", percentage=0)

# Step 2: Test with internal users
await update_flag("new_payment_system", target_users=["qa_team"])

# Step 3: Gradual rollout
for percentage in [5, 10, 25, 50, 100]:
    await update_flag("new_payment_system", target_percentage=percentage)
    await monitor_metrics(hours=24)
    if not await check_health_metrics():
        await rollback_flag("new_payment_system")
        break
```

### 2. Emergency Rollback

```python
async def emergency_disable_feature(flag_name: str, reason: str):
    """Emergency procedure to disable a feature."""
    manager = await get_feature_flags()
    
    # Get current flag state for audit
    flag = await manager.get_flag(flag_name)
    
    # Disable immediately
    flag.status = FlagStatus.DISABLED
    flag.metadata["emergency_disabled"] = {
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
        "previous_state": flag.dict()
    }
    
    await manager.update_flag(flag)
    
    # Clear all caches
    await manager.refresh_cache()
    
    # Alert team
    await alert_team(f"Emergency disabled: {flag_name} - {reason}")
```

## Debugging

### 1. Check Flag Evaluation

```python
# Enable debug logging for flag evaluation
import logging
logging.getLogger("core.feature_flags").setLevel(logging.DEBUG)

# Logs will show:
# - Flag name and context
# - Evaluation result
# - Which rule matched (if any)
```

### 2. Export Flag State

```python
async def export_flag_state():
    """Export all flags for debugging."""
    manager = await get_feature_flags()
    flags = await manager.get_all_flags()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "flags": [flag.dict() for flag in flags],
        "cache_status": {
            "redis_connected": manager.cache is not None,
            "memory_cache_size": len(manager._memory_cache)
        }
    }
```

## Summary

Feature flags provide powerful control over your application's behavior:

1. **Start Simple**: Use boolean flags for basic feature toggles
2. **Graduate to Targeting**: Add user segments and percentages
3. **Experiment Safely**: Use A/B testing with variants
4. **Monitor Everything**: Track flag evaluations and impacts
5. **Plan for Failure**: Have rollback procedures ready

Remember: Feature flags are technical debt - remove them once features are fully rolled out!