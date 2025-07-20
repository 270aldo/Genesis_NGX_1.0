# Beta Validation Testing Suite

## Overview

This comprehensive testing suite is designed to validate GENESIS before BETA launch. It covers all possible user scenarios, edge cases, and system stress points to ensure a robust and reliable experience.

## Test Categories

### 1. User Frustration Scenarios (`user_frustration`)
Tests how GENESIS agents handle frustrated, angry, confused, or discouraged users.

**Scenarios:**
- Angry about wrong plan
- Body image issues
- Technology confusion
- Plan not working after weeks
- Injury frustration
- Financial concerns
- Time pressure
- Comparison depression
- Plateau frustration
- Aggressive language

### 2. Edge Case Scenarios (`edge_cases`)
Tests how GENESIS handles extreme conditions and unusual requests.

**Scenarios:**
- Multiple health conditions
- Extreme time constraints (5 min/day)
- Contradictory requirements
- Impossible goals
- Very long messages
- Multiple languages mixed
- Severe dietary restrictions
- Budget constraints
- Accessibility needs
- Data conflicts
- Rapid context switching
- Excessive personalization
- Missing critical data
- Extreme age cases
- Cultural sensitivity

### 3. Multi-Agent Coordination (`multi_agent`)
Tests agent collaboration and consistency across complex interactions.

**Scenarios:**
- Training & nutrition coordination
- Injury recovery flow
- Female wellness journey
- Biohacking optimization
- Complete transformation
- Agent handoff quality
- Data consistency
- Personality changes (PRIME/LONGEVITY)
- Conflicting agent advice
- Emergency escalation
- Progress tracking flow
- Motivation crisis handling
- Genetic integration
- Full ecosystem flow

### 4. Ecosystem Integration (`ecosystem_integration`)
Tests integration with NGX Pulse, Blog, CRM, and Conversations.

**Scenarios:**
- Pulse data integration
- Blog content generation
- CRM sync flow
- Conversations history
- Cross-platform analytics
- Unified user profile
- Real-time sync
- Failover resilience
- Data privacy across platforms
- Notification orchestration
- Subscription management
- Multi-device experience
- API rate limiting
- Ecosystem onboarding
- Complete user journey

### 5. Stress Testing (`stress_tests`)
Tests system performance under extreme conditions.

**Scenarios:**
- 100+ concurrent users
- Marathon sessions (2+ hours)
- Rapid fire messages
- Large context accumulation
- Memory pressure
- API rate limits
- Database connection pool
- Cache saturation
- WebSocket limits
- Error recovery
- Cascade failure prevention
- Resource exhaustion
- Network latency
- Data consistency under load
- Graceful degradation

## Running Tests

### Quick Start
```bash
# Run all beta validation tests
python -m tests.beta_validation.run_beta_validation

# Run specific test category
python -m tests.beta_validation.run_beta_validation --category user_frustration

# Run quick validation (subset of tests)
python -m tests.beta_validation.run_beta_validation --quick

# Run tests in parallel (faster)
python -m tests.beta_validation.run_beta_validation --parallel

# Run with detailed reporting
python -m tests.beta_validation.run_beta_validation --verbose --report
```

### Command Line Options
- `--category CATEGORY`: Run only specific category
- `--verbose`: Enable detailed logging
- `--report`: Generate HTML report
- `--quick`: Run quick subset (user_frustration + edge_cases)
- `--parallel`: Run tests in parallel
- `--output-dir DIR`: Specify report directory (default: reports/)

## Response Quality Validation

The suite includes a comprehensive `ResponseQualityValidator` that evaluates:

### Quality Metrics (Weighted)
- **Safety (25%)**: No harmful advice, proper disclaimers
- **Relevance (20%)**: Addresses user's actual query
- **Actionability (15%)**: Provides concrete steps
- **Clarity (15%)**: Well-structured, understandable
- **Consistency (10%)**: Aligns with conversation history
- **Empathy (10%)**: Appropriate emotional response
- **Personalization (3%)**: Tailored to user
- **Cultural Sensitivity (2%)**: Inclusive language

### Pass Criteria
- Overall quality score ≥ 70%
- No critical safety issues
- All critical scenarios must pass

## Reports

Test results are saved in `reports/` with:

### JSON Report (`beta_validation_results_YYYYMMDD_HHMMSS.json`)
- Complete test results
- Detailed metrics per scenario
- All issues and warnings
- Performance data

### Summary Report (`beta_validation_summary_YYYYMMDD_HHMMSS.txt`)
- Human-readable summary
- Pass/fail rates by category
- Critical issues highlighted
- Launch recommendations

### Report Contents
- Overall pass rate
- Category breakdowns
- Critical issues (must fix)
- Warnings (should fix)
- Performance metrics
- Recommendations

## Critical Scenarios

These MUST pass before BETA launch:

1. **Medical Emergency Detection**
   - Chest pain during exercise
   - Severe symptoms recognition
   - Proper escalation to medical help

2. **Safety Compliance**
   - No dangerous advice
   - Proper disclaimers
   - Injury prevention

3. **Data Privacy**
   - GDPR compliance
   - Selective data sharing
   - Privacy controls

4. **System Resilience**
   - Graceful degradation
   - Error recovery
   - Cascade failure prevention

5. **Emergency Protocols**
   - Guardian agent activation
   - Crisis intervention
   - Appropriate escalation

## Launch Criteria

### 🚀 Ready for BETA
- All critical scenarios pass
- Overall pass rate ≥ 90%
- No critical issues
- Response quality score ≥ 70%

### ⚠️ Delay Launch
- Pass rate < 90%
- Critical issues present
- Major performance problems
- Safety compliance failures

### ❌ Block Launch
- Critical safety failures
- Data privacy violations
- System instability
- Emergency protocol failures

## Adding New Tests

1. **Create Scenario Class**
   ```python
   class NewScenarios:
       def __init__(self, orchestrator_client):
           self.orchestrator = orchestrator_client
       
       async def test_new_scenario(self):
           # Implementation
   ```

2. **Define Expected Behaviors**
   ```python
   expected_behaviors = [
       "specific_behavior_1",
       "specific_behavior_2"
   ]
   ```

3. **Add to Runner**
   - Add to test_categories in run_beta_validation.py
   - Update documentation

4. **Document Thoroughly**
   - Add to this README
   - Include pass criteria
   - Specify critical vs non-critical

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure running from project root
   - Check Python path includes backend/

2. **Async Errors**
   - Use Python 3.8+
   - Run with asyncio.run()

3. **Mock Client Issues**
   - Real orchestrator integration pending
   - Mock provides basic responses

4. **Performance Issues**
   - Use --parallel for faster runs
   - Consider --quick for rapid validation