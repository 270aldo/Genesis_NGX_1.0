# NGX Agents Budget Management System

## 🎯 Overview

The NGX Agents Budget Management System provides comprehensive control over token usage and costs across all 13 specialized agents. This system ensures optimal resource utilization while preventing unexpected cost overruns.

## 🏗️ Architecture

### Core Components

1. **BudgetManager** (`core/budget.py`) - Central budget management
2. **Budget Tasks** (`tasks/budget.py`) - Celery-based queue processing
3. **Budget API** (`app/routers/budget_monitoring.py`) - REST API for monitoring
4. **Dashboard** (`monitoring/budget_dashboard.py`) - Real-time monitoring
5. **Configuration** (`config/budgets.json`) - Agent-specific budget rules

### System Flow

```
User Request → Agent → BudgetManager.record_usage() → Action Decision
                                    ↓
              WARN ←─────────────────┼─────────────────→ BLOCK
                                    ↓
              DEGRADE ←──────────────┼─────────────────→ QUEUE
                                    ↓
                            Celery Task (queue_over_budget_task)
                                    ↓
                            Retry when budget available
```

## ⚙️ Configuration

### Budget Configuration (`config/budgets.json`)

```json
{
  "default": {
    "max_tokens": 1000000,
    "period": "monthly",
    "action_on_limit": "warn",
    "reset_day": 1,
    "fallback_model": "gemini-1.5-flash"
  },
  "agents": {
    "sage": {
      "max_tokens": 3000000,
      "period": "monthly",
      "action_on_limit": "degrade",
      "fallback_model": "gemini-1.5-flash",
      "reset_day": 1,
      "description": "Nutrition Architect - Highest usage with vision processing"
    }
  }
}
```

### Budget Periods

- **daily**: Reset every day at midnight
- **weekly**: Reset on specified day of week (1=Monday, 7=Sunday)
- **monthly**: Reset on specified day of month (1-28)
- **yearly**: Reset on January 1st
- **infinite**: Never reset automatically

### Actions on Limit

- **warn**: Log warning but allow execution
- **block**: Immediately block the request
- **degrade**: Switch to fallback model (cheaper/faster)
- **queue**: Queue request for later processing

## 🚀 Usage Guide

### 1. Monitor Budget Status

```bash
# Get status for all agents
curl -X GET "http://localhost:8000/api/budget/status" \
     -H "Authorization: Bearer YOUR_TOKEN"

# Get status for specific agent
curl -X GET "http://localhost:8000/api/budget/status/sage" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Update Agent Budget

```bash
curl -X PUT "http://localhost:8000/api/budget/update/sage" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "max_tokens": 4000000,
       "action_on_limit": "degrade"
     }'
```

### 3. Reset Agent Budget

```bash
curl -X POST "http://localhost:8000/api/budget/reset/sage" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Get Budget Alerts

```bash
curl -X GET "http://localhost:8000/api/budget/alerts" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 Monitoring and Alerting

### Real-time Dashboard

Start the monitoring dashboard:

```bash
python scripts/start_budget_monitoring.py
```

Features:
- Real-time usage tracking
- Health status indicators
- Cost projections
- Alert notifications

### Alert Thresholds

- **75% Usage**: Warning alert
- **90% Usage**: Critical alert
- **100% Usage**: Action triggered based on configuration

### Celery Tasks

The system includes automatic Celery tasks:

- **Budget Alerts**: Check every 30 minutes
- **Budget Resets**: Daily reset check at midnight
- **Queue Processing**: Process queued requests when budget available

## 💰 Cost Management

### Agent Budget Allocation (Monthly)

| Agent | Budget (Tokens) | Action | Priority | Estimated Cost |
|-------|----------------|---------|----------|----------------|
| SAGE | 3,000,000 | Degrade | High | $15.00 |
| BLAZE | 2,500,000 | Degrade | High | $12.50 |
| VOLT | 2,200,000 | Degrade | High | $11.00 |
| LUNA | 2,000,000 | Degrade | High | $10.00 |
| NOVA | 1,800,000 | Degrade | Medium | $9.00 |
| SPARK | 1,500,000 | Queue | Medium | $7.50 |
| AURA | 1,300,000 | Queue | Medium | $6.50 |
| STELLA | 1,200,000 | Degrade | Medium | $6.00 |
| WAVE | 1,100,000 | Queue | Low | $5.50 |
| CODE | 1,600,000 | Warn | Medium | $8.00 |
| NEXUS | 800,000 | Queue | High | $4.00 |
| NODE | 500,000 | Warn | Low | $2.50 |
| GUARDIAN | 400,000 | Block | Critical | $2.00 |

**Total Monthly Budget**: ~$119.50 (23.9M tokens)

### Cost Optimization Strategies

1. **Fallback Models**: Automatic degradation to cheaper models
2. **Request Queueing**: Defer non-urgent requests
3. **Usage Analytics**: Identify optimization opportunities
4. **Smart Caching**: Reduce redundant API calls

## 🔧 Advanced Configuration

### Dynamic Budget Adjustment

```python
from core.budget import budget_manager, AgentBudget, BudgetPeriod, BudgetAction

# Create new budget
budget = AgentBudget(
    agent_id="custom_agent",
    max_tokens=1500000,
    period=BudgetPeriod.MONTHLY,
    action_on_limit=BudgetAction.DEGRADE,
    fallback_model="gemini-1.5-flash"
)

# Apply budget
budget_manager.set_budget(budget)
```

### Usage Recording

```python
from core.budget import budget_manager

# Record token usage
allowed, fallback_model = await budget_manager.record_usage(
    agent_id="sage",
    prompt_tokens=1000,
    completion_tokens=500,
    model="gemini-1.5-pro"
)

if not allowed:
    # Handle budget exceeded
    pass
elif fallback_model:
    # Use fallback model
    pass
```

## 📈 Analytics and Reporting

### Usage Metrics

- Token consumption by agent
- Cost breakdown by model
- Efficiency ratios
- Trend analysis

### Performance Indicators

- **Utilization Rate**: Percentage of budget used
- **Cost per Request**: Average cost per agent interaction
- **Efficiency Score**: Budget utilization vs. user satisfaction
- **Prediction Accuracy**: Forecast vs. actual usage

## 🚨 Troubleshooting

### Common Issues

#### 1. Budget Exceeded Unexpectedly

**Symptoms**: Agent suddenly blocked or degraded
**Causes**: Unusual spike in usage, misconfigured period
**Solutions**:
- Check recent usage patterns
- Verify period configuration
- Temporarily increase budget
- Review alert thresholds

#### 2. Queue Tasks Not Processing

**Symptoms**: Requests stuck in queue
**Causes**: Celery workers down, Redis connection issues
**Solutions**:
- Check Celery worker status
- Verify Redis connectivity
- Restart budget monitoring
- Review queue task logs

#### 3. Inaccurate Cost Estimates

**Symptoms**: Unexpected billing amounts
**Causes**: Outdated model pricing, untracked usage
**Solutions**:
- Update cost estimation in `_estimate_cost()`
- Verify all usage is being recorded
- Cross-reference with actual billing

### Debug Commands

```bash
# Check budget status for all agents
python -c "
from core.budget import budget_manager
for agent_id in budget_manager.budgets.keys():
    status = budget_manager.get_budget_status(agent_id)
    print(f'{agent_id}: {status[\"percentage\"]:.1f}%')
"

# View Celery task queue
celery -A core.celery_app inspect active

# Check Redis budget keys
redis-cli KEYS "budget:*"
```

## 🔮 Future Enhancements

### Planned Features

1. **Machine Learning Predictions**
   - Usage forecasting
   - Anomaly detection
   - Automatic budget adjustment

2. **Advanced Analytics**
   - ROI analysis by agent
   - User value correlation
   - Seasonal usage patterns

3. **Integration Enhancements**
   - Slack/Teams notifications
   - Grafana dashboards
   - Billing system integration

4. **Smart Optimization**
   - Dynamic model selection
   - Intelligent caching strategies
   - Performance-based budgeting

## 📞 Support

For budget system support:
- **Documentation**: `docs/BUDGET_SYSTEM_GUIDE.md`
- **API Reference**: `http://localhost:8000/docs#/Budget%20Monitoring`
- **Monitoring**: `python scripts/start_budget_monitoring.py`
- **Logs**: Check `logs/budget.log` for detailed information

---

**Last Updated**: June 5, 2025
**Version**: 1.0.0
**Author**: NGX Systems Engineering Team