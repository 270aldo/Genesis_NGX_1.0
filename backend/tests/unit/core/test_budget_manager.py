"""
Unit tests for BudgetManager in core.budget module.

Tests cover budget configuration, usage tracking, reset logic,
and budget enforcement actions.
"""

import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import mock_open, patch

import pytest

from core.budget import (
    AgentBudget,
    BudgetAction,
    BudgetManager,
    BudgetPeriod,
    TokenUsage,
)


class TestBudgetManager:
    """Test suite for BudgetManager functionality."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        BudgetManager._instance = None
        yield
        BudgetManager._instance = None

    @pytest.fixture
    def budget_manager(self):
        """Create a BudgetManager instance for testing."""
        with patch("core.budget.settings") as mock_settings:
            mock_settings.enable_budgets = False  # Disable budget loading
            manager = BudgetManager()
            return manager

    @pytest.fixture
    def sample_budget(self):
        """Create a sample budget configuration."""
        return AgentBudget(
            agent_id="test_agent",
            max_tokens=10000,
            period=BudgetPeriod.MONTHLY,
            action_on_limit=BudgetAction.WARN,
            fallback_model="gpt-3.5-turbo",
            reset_day=1,
        )


class TestBudgetConfiguration(TestBudgetManager):
    """Tests for budget configuration management."""

    def test_singleton_pattern(self):
        """Test that BudgetManager follows singleton pattern."""
        manager1 = BudgetManager()
        manager2 = BudgetManager()
        assert manager1 is manager2

    def test_set_and_get_budget(self, budget_manager, sample_budget):
        """Test setting and retrieving budget configurations."""
        # Set budget
        budget_manager.set_budget(sample_budget)

        # Get budget
        retrieved = budget_manager.get_budget("test_agent")
        assert retrieved is not None
        assert retrieved.agent_id == "test_agent"
        assert retrieved.max_tokens == 10000
        assert retrieved.period == BudgetPeriod.MONTHLY

    def test_get_nonexistent_budget(self, budget_manager):
        """Test getting budget for non-configured agent."""
        result = budget_manager.get_budget("nonexistent")
        assert result is None

    def test_multiple_agent_budgets(self, budget_manager):
        """Test managing budgets for multiple agents."""
        # Create budgets for different agents
        budgets = [
            AgentBudget(agent_id="agent1", max_tokens=5000, period=BudgetPeriod.DAILY),
            AgentBudget(
                agent_id="agent2", max_tokens=10000, period=BudgetPeriod.WEEKLY
            ),
            AgentBudget(
                agent_id="agent3", max_tokens=50000, period=BudgetPeriod.MONTHLY
            ),
        ]

        # Set all budgets
        for budget in budgets:
            budget_manager.set_budget(budget)

        # Verify all can be retrieved
        for budget in budgets:
            retrieved = budget_manager.get_budget(budget.agent_id)
            assert retrieved is not None
            assert retrieved.agent_id == budget.agent_id
            assert retrieved.max_tokens == budget.max_tokens


class TestPeriodCalculation(TestBudgetManager):
    """Tests for period key calculation."""

    def test_period_key_daily(self, budget_manager):
        """Test daily period key calculation."""
        budget = AgentBudget(
            agent_id="daily_agent", max_tokens=1000, period=BudgetPeriod.DAILY
        )
        budget_manager.set_budget(budget)

        with patch("core.budget.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 31, 12, 0, 0)
            key = budget_manager._get_period_key("daily_agent")
            assert key == "2025-07-31"

    def test_period_key_weekly(self, budget_manager):
        """Test weekly period key calculation."""
        budget = AgentBudget(
            agent_id="weekly_agent", max_tokens=5000, period=BudgetPeriod.WEEKLY
        )
        budget_manager.set_budget(budget)

        with patch("core.budget.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 31)  # Thursday
            key = budget_manager._get_period_key("weekly_agent")
            # Week 31 of 2025
            assert key == "2025-W31"

    def test_period_key_monthly(self, budget_manager):
        """Test monthly period key calculation."""
        budget = AgentBudget(
            agent_id="monthly_agent", max_tokens=10000, period=BudgetPeriod.MONTHLY
        )
        budget_manager.set_budget(budget)

        with patch("core.budget.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 31)
            key = budget_manager._get_period_key("monthly_agent")
            assert key == "2025-07"

    def test_period_key_yearly(self, budget_manager):
        """Test yearly period key calculation."""
        budget = AgentBudget(
            agent_id="yearly_agent", max_tokens=100000, period=BudgetPeriod.YEARLY
        )
        budget_manager.set_budget(budget)

        with patch("core.budget.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 31)
            key = budget_manager._get_period_key("yearly_agent")
            assert key == "2025"

    def test_period_key_infinite(self, budget_manager):
        """Test infinite period key calculation."""
        budget = AgentBudget(
            agent_id="infinite_agent", max_tokens=1000000, period=BudgetPeriod.INFINITE
        )
        budget_manager.set_budget(budget)

        key = budget_manager._get_period_key("infinite_agent")
        assert key == "infinite"


class TestResetLogic(TestBudgetManager):
    """Tests for usage reset logic."""

    def test_should_reset_daily(self, budget_manager):
        """Test daily reset logic."""
        budget = AgentBudget(
            agent_id="daily_agent", max_tokens=1000, period=BudgetPeriod.DAILY
        )
        budget_manager.set_budget(budget)

        # Set last reset to yesterday
        budget_manager.last_reset["daily_agent"] = datetime.now() - timedelta(days=1)

        assert budget_manager._should_reset("daily_agent") is True

        # Set last reset to today
        budget_manager.last_reset["daily_agent"] = datetime.now()
        assert budget_manager._should_reset("daily_agent") is False

    def test_should_reset_monthly(self, budget_manager):
        """Test monthly reset logic."""
        budget = AgentBudget(
            agent_id="monthly_agent",
            max_tokens=10000,
            period=BudgetPeriod.MONTHLY,
            reset_day=1,
        )
        budget_manager.set_budget(budget)

        with patch("core.budget.datetime") as mock_datetime:
            # Test on reset day
            mock_datetime.now.return_value = datetime(2025, 8, 1)
            budget_manager.last_reset["monthly_agent"] = datetime(2025, 7, 1)
            assert budget_manager._should_reset("monthly_agent") is True

            # Test not on reset day
            mock_datetime.now.return_value = datetime(2025, 7, 15)
            assert budget_manager._should_reset("monthly_agent") is False

    def test_no_reset_for_infinite(self, budget_manager):
        """Test that infinite budgets never reset."""
        budget = AgentBudget(
            agent_id="infinite_agent", max_tokens=1000000, period=BudgetPeriod.INFINITE
        )
        budget_manager.set_budget(budget)

        # Even with old last reset, should not reset
        budget_manager.last_reset["infinite_agent"] = datetime(2020, 1, 1)
        assert budget_manager._should_reset("infinite_agent") is False


class TestUsageTracking(TestBudgetManager):
    """Tests for token usage tracking."""

    @pytest.mark.asyncio
    async def test_record_usage_success(self, budget_manager, sample_budget):
        """Test successful usage recording."""
        budget_manager.set_budget(sample_budget)

        # Record usage
        allowed, fallback = await budget_manager.record_usage(
            agent_id="test_agent",
            prompt_tokens=100,
            completion_tokens=50,
            model="gpt-4",
        )

        assert allowed is True
        assert fallback is None

        # Check usage was recorded
        usage = budget_manager.get_usage("test_agent")
        assert usage is not None
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150

    @pytest.mark.asyncio
    async def test_record_usage_exceeds_budget(self, budget_manager):
        """Test behavior when usage exceeds budget."""
        # Set small budget
        budget = AgentBudget(
            agent_id="limited_agent",
            max_tokens=100,
            period=BudgetPeriod.DAILY,
            action_on_limit=BudgetAction.BLOCK,
        )
        budget_manager.set_budget(budget)

        # Record usage that exceeds budget
        allowed, fallback = await budget_manager.record_usage(
            agent_id="limited_agent",
            prompt_tokens=80,
            completion_tokens=30,  # Total: 110 > 100
            model="gpt-4",
        )

        # Should be blocked
        assert allowed is False
        assert fallback is None

    @pytest.mark.asyncio
    async def test_record_usage_degrade_action(self, budget_manager):
        """Test degradation action when budget exceeded."""
        budget = AgentBudget(
            agent_id="degrade_agent",
            max_tokens=100,
            period=BudgetPeriod.DAILY,
            action_on_limit=BudgetAction.DEGRADE,
            fallback_model="gpt-3.5-turbo",
        )
        budget_manager.set_budget(budget)

        # Record usage that exceeds budget
        allowed, fallback = await budget_manager.record_usage(
            agent_id="degrade_agent",
            prompt_tokens=80,
            completion_tokens=30,
            model="gpt-4",
        )

        # Should be allowed with fallback model
        assert allowed is True
        assert fallback == "gpt-3.5-turbo"

    @pytest.mark.asyncio
    async def test_record_usage_warn_action(self, budget_manager):
        """Test warning action when budget exceeded."""
        budget = AgentBudget(
            agent_id="warn_agent",
            max_tokens=100,
            period=BudgetPeriod.DAILY,
            action_on_limit=BudgetAction.WARN,
        )
        budget_manager.set_budget(budget)

        # Record usage that exceeds budget
        with patch("core.budget.logger") as mock_logger:
            allowed, fallback = await budget_manager.record_usage(
                agent_id="warn_agent",
                prompt_tokens=80,
                completion_tokens=30,
                model="gpt-4",
            )

            # Should be allowed with warning
            assert allowed is True
            assert fallback is None
            # Check that warning was logged
            assert mock_logger.warning.called

    @pytest.mark.asyncio
    async def test_cumulative_usage_tracking(self, budget_manager, sample_budget):
        """Test that usage accumulates correctly."""
        budget_manager.set_budget(sample_budget)

        # Record multiple usages
        await budget_manager.record_usage("test_agent", 100, 50, "gpt-4")
        await budget_manager.record_usage("test_agent", 200, 100, "gpt-4")
        await budget_manager.record_usage("test_agent", 150, 75, "gpt-4")

        # Check cumulative usage
        usage = budget_manager.get_usage("test_agent")
        assert usage.prompt_tokens == 450
        assert usage.completion_tokens == 225
        assert usage.total_tokens == 675


class TestBudgetStatus(TestBudgetManager):
    """Tests for budget status reporting."""

    def test_get_budget_status(self, budget_manager, sample_budget):
        """Test getting comprehensive budget status."""
        budget_manager.set_budget(sample_budget)

        # Add some usage
        period_key = budget_manager._get_period_key("test_agent")
        budget_manager.usage["test_agent"] = {
            period_key: TokenUsage(
                prompt_tokens=2000,
                completion_tokens=1000,
                total_tokens=3000,
                estimated_cost_usd=0.15,
            )
        }

        status = budget_manager.get_budget_status("test_agent")

        assert status["agent_id"] == "test_agent"
        assert status["budget"]["max_tokens"] == 10000
        assert status["usage"]["total_tokens"] == 3000
        assert status["usage_percentage"] == 30.0
        assert status["remaining_tokens"] == 7000
        assert status["is_exceeded"] is False

    def test_get_budget_status_exceeded(self, budget_manager):
        """Test budget status when exceeded."""
        budget = AgentBudget(
            agent_id="exceeded_agent",
            max_tokens=1000,
            period=BudgetPeriod.DAILY,
            action_on_limit=BudgetAction.BLOCK,
        )
        budget_manager.set_budget(budget)

        # Add usage that exceeds budget
        period_key = budget_manager._get_period_key("exceeded_agent")
        budget_manager.usage["exceeded_agent"] = {
            period_key: TokenUsage(
                prompt_tokens=800,
                completion_tokens=300,
                total_tokens=1100,
                estimated_cost_usd=0.055,
            )
        }

        status = budget_manager.get_budget_status("exceeded_agent")

        assert status["is_exceeded"] is True
        assert status["usage_percentage"] == 110.0
        assert status["remaining_tokens"] == -100
        assert status["action"] == "block"

    def test_get_all_usage(self, budget_manager):
        """Test getting usage for all agents."""
        # Set up multiple agents
        agents = ["agent1", "agent2", "agent3"]
        for agent_id in agents:
            budget = AgentBudget(
                agent_id=agent_id, max_tokens=10000, period=BudgetPeriod.MONTHLY
            )
            budget_manager.set_budget(budget)

            # Add usage
            period_key = budget_manager._get_period_key(agent_id)
            budget_manager.usage[agent_id] = {
                period_key: TokenUsage(
                    prompt_tokens=100 * (agents.index(agent_id) + 1),
                    completion_tokens=50 * (agents.index(agent_id) + 1),
                    total_tokens=150 * (agents.index(agent_id) + 1),
                )
            }

        all_usage = budget_manager.get_all_usage()

        assert len(all_usage) == 3
        assert "agent1" in all_usage
        assert "agent2" in all_usage
        assert "agent3" in all_usage


class TestBudgetLoading(TestBudgetManager):
    """Tests for loading budget configuration from file."""

    def test_load_budgets_from_file(self):
        """Test loading budget configuration from JSON file."""
        config_data = {
            "default": {
                "max_tokens": 5000,
                "period": "monthly",
                "action_on_limit": "warn",
            },
            "agents": {
                "agent1": {
                    "max_tokens": 10000,
                    "period": "daily",
                    "action_on_limit": "block",
                },
                "agent2": {
                    "max_tokens": 50000,
                    "period": "weekly",
                    "action_on_limit": "degrade",
                    "fallback_model": "gpt-3.5-turbo",
                },
            },
        }

        with (
            patch("core.budget.settings") as mock_settings,
            patch("builtins.open", mock_open(read_data=json.dumps(config_data))),
            patch("os.path.exists", return_value=True),
        ):

            mock_settings.enable_budgets = True
            mock_settings.budget_config_path = "/path/to/config.json"

            manager = BudgetManager()

            # Check budgets were loaded
            assert len(manager.budgets) == 2

            budget1 = manager.get_budget("agent1")
            assert budget1 is not None
            assert budget1.max_tokens == 10000
            assert budget1.period == BudgetPeriod.DAILY

            budget2 = manager.get_budget("agent2")
            assert budget2 is not None
            assert budget2.max_tokens == 50000
            assert budget2.period == BudgetPeriod.WEEKLY
            assert budget2.fallback_model == "gpt-3.5-turbo"


class TestConcurrency(TestBudgetManager):
    """Tests for concurrent operations."""

    @pytest.mark.asyncio
    async def test_concurrent_usage_recording(self, budget_manager, sample_budget):
        """Test concurrent usage recording from multiple agents."""
        budget_manager.set_budget(sample_budget)

        # Create multiple concurrent tasks
        tasks = []
        for i in range(10):
            task = budget_manager.record_usage(
                agent_id="test_agent",
                prompt_tokens=10,
                completion_tokens=5,
                model="gpt-4",
            )
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(allowed for allowed, _ in results)

        # Check final usage
        usage = budget_manager.get_usage("test_agent")
        assert usage.prompt_tokens == 100  # 10 * 10
        assert usage.completion_tokens == 50  # 5 * 10
        assert usage.total_tokens == 150
