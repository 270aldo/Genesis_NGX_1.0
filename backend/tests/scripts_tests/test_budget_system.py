#!/usr/bin/env python3
"""
Budget System Testing Script
Comprehensive testing of the NGX Agents budget management system
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.budget import budget_manager, AgentBudget, BudgetPeriod, BudgetAction
from tasks.budget import check_budget_alerts, reset_period_budgets
from core.settings import setup_logging

# Setup logging
setup_logging()


class BudgetSystemTester:
    """Comprehensive budget system tester."""

    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name} {message}")

        self.test_results.append(
            {
                "test": test_name,
                "passed": passed,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }
        )

        if passed:
            self.passed += 1
        else:
            self.failed += 1

    async def test_budget_configuration(self):
        """Test budget configuration loading."""
        print("\n🧪 Testing Budget Configuration...")

        try:
            # Test default budget exists
            budgets_count = len(budget_manager.budgets)
            self.log_test(
                "Budget Configuration Loading",
                budgets_count > 0,
                f"Loaded {budgets_count} agent budgets",
            )

            # Test specific agent budgets
            test_agents = ["sage", "blaze", "nexus", "guardian"]
            for agent_id in test_agents:
                budget = budget_manager.get_budget(agent_id)
                self.log_test(
                    f"Agent Budget ({agent_id})",
                    budget is not None,
                    f"Max tokens: {budget.max_tokens if budget else 'N/A'}",
                )

            # Test budget validation
            valid_actions = all(
                budget.action_on_limit
                in [
                    BudgetAction.WARN,
                    BudgetAction.BLOCK,
                    BudgetAction.DEGRADE,
                    BudgetAction.QUEUE,
                ]
                for budget in budget_manager.budgets.values()
            )
            self.log_test("Budget Action Validation", valid_actions)

        except Exception as e:
            self.log_test("Budget Configuration", False, f"Error: {e}")

    async def test_usage_recording(self):
        """Test token usage recording."""
        print("\n🧪 Testing Usage Recording...")

        try:
            test_agent = "sage"

            # Record some usage
            allowed, fallback = await budget_manager.record_usage(
                agent_id=test_agent,
                prompt_tokens=1000,
                completion_tokens=500,
                model="gemini-1.5-pro",
            )

            self.log_test(
                "Usage Recording",
                allowed is not None,
                f"Allowed: {allowed}, Fallback: {fallback}",
            )

            # Check usage was recorded
            usage = budget_manager.get_usage(test_agent)
            self.log_test(
                "Usage Retrieval",
                usage is not None and usage.total_tokens >= 1500,
                f"Total tokens: {usage.total_tokens if usage else 0}",
            )

            # Test budget status
            status = budget_manager.get_budget_status(test_agent)
            self.log_test(
                "Budget Status",
                "percentage" in status,
                f"Usage: {status.get('percentage', 0):.2f}%",
            )

        except Exception as e:
            self.log_test("Usage Recording", False, f"Error: {e}")

    async def test_budget_limits(self):
        """Test budget limit enforcement."""
        print("\n🧪 Testing Budget Limits...")

        try:
            # Create test budget with low limit
            test_budget = AgentBudget(
                agent_id="test_agent",
                max_tokens=5000,
                period=BudgetPeriod.MONTHLY,
                action_on_limit=BudgetAction.WARN,
            )
            budget_manager.set_budget(test_budget)

            # Use up most of the budget
            allowed1, _ = await budget_manager.record_usage(
                agent_id="test_agent",
                prompt_tokens=2000,
                completion_tokens=2000,
                model="gemini-1.5-pro",
            )

            self.log_test("Normal Usage", allowed1 == True, "4000 tokens recorded")

            # Try to exceed budget
            allowed2, _ = await budget_manager.record_usage(
                agent_id="test_agent",
                prompt_tokens=1500,
                completion_tokens=1500,
                model="gemini-1.5-pro",
            )

            # Should trigger warning but still allow
            self.log_test(
                "Budget Limit (WARN)",
                allowed2 == True,
                "Budget exceeded but allowed with warning",
            )

            # Test BLOCK action
            test_budget.action_on_limit = BudgetAction.BLOCK
            budget_manager.set_budget(test_budget)

            allowed3, _ = await budget_manager.record_usage(
                agent_id="test_agent",
                prompt_tokens=1000,
                completion_tokens=1000,
                model="gemini-1.5-pro",
            )

            self.log_test(
                "Budget Limit (BLOCK)",
                allowed3 == False,
                "Request blocked due to budget limit",
            )

        except Exception as e:
            self.log_test("Budget Limits", False, f"Error: {e}")

    async def test_queue_functionality(self):
        """Test queue functionality."""
        print("\n🧪 Testing Queue Functionality...")

        try:
            # Create budget with queue action
            queue_budget = AgentBudget(
                agent_id="queue_test_agent",
                max_tokens=1000,
                period=BudgetPeriod.MONTHLY,
                action_on_limit=BudgetAction.QUEUE,
            )
            budget_manager.set_budget(queue_budget)

            # Exceed budget to trigger queue
            await budget_manager.record_usage(
                agent_id="queue_test_agent",
                prompt_tokens=800,
                completion_tokens=400,
                model="gemini-1.5-pro",
            )

            # This should trigger queue
            allowed, _ = await budget_manager.record_usage(
                agent_id="queue_test_agent",
                prompt_tokens=500,
                completion_tokens=500,
                model="gemini-1.5-pro",
            )

            self.log_test(
                "Queue Trigger", allowed == False, "Request queued due to budget limit"
            )

        except Exception as e:
            self.log_test("Queue Functionality", False, f"Error: {e}")

    async def test_degradation(self):
        """Test model degradation."""
        print("\n🧪 Testing Model Degradation...")

        try:
            # Create budget with degrade action
            degrade_budget = AgentBudget(
                agent_id="degrade_test_agent",
                max_tokens=2000,
                period=BudgetPeriod.MONTHLY,
                action_on_limit=BudgetAction.DEGRADE,
                fallback_model="gemini-1.5-flash",
            )
            budget_manager.set_budget(degrade_budget)

            # Use up budget
            await budget_manager.record_usage(
                agent_id="degrade_test_agent",
                prompt_tokens=1500,
                completion_tokens=800,
                model="gemini-1.5-pro",
            )

            # This should trigger degradation
            allowed, fallback = await budget_manager.record_usage(
                agent_id="degrade_test_agent",
                prompt_tokens=500,
                completion_tokens=500,
                model="gemini-1.5-pro",
            )

            self.log_test(
                "Model Degradation",
                allowed and fallback == "gemini-1.5-flash",
                f"Degraded to: {fallback}",
            )

        except Exception as e:
            self.log_test("Model Degradation", False, f"Error: {e}")

    async def test_celery_tasks(self):
        """Test Celery budget tasks."""
        print("\n🧪 Testing Celery Tasks...")

        try:
            # Test alert checking
            result = check_budget_alerts.delay()
            time.sleep(2)  # Wait for task

            self.log_test(
                "Budget Alerts Task",
                result.state in ["SUCCESS", "PENDING"],
                f"Task state: {result.state}",
            )

            # Test budget reset
            result = reset_period_budgets.delay()
            time.sleep(2)  # Wait for task

            self.log_test(
                "Budget Reset Task",
                result.state in ["SUCCESS", "PENDING"],
                f"Task state: {result.state}",
            )

        except Exception as e:
            self.log_test("Celery Tasks", False, f"Error: {e}")

    async def test_cost_estimation(self):
        """Test cost estimation."""
        print("\n🧪 Testing Cost Estimation...")

        try:
            # Test cost calculation
            cost = budget_manager._estimate_cost(
                prompt_tokens=1000, completion_tokens=500, model="gemini-1.5-pro"
            )

            self.log_test("Cost Estimation", cost > 0, f"Estimated cost: ${cost:.6f}")

            # Test different models
            models_to_test = [
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gpt-4",
                "claude-3-opus",
            ]

            for model in models_to_test:
                model_cost = budget_manager._estimate_cost(1000, 500, model)
                self.log_test(
                    f"Cost Estimation ({model})", model_cost > 0, f"${model_cost:.6f}"
                )

        except Exception as e:
            self.log_test("Cost Estimation", False, f"Error: {e}")

    async def test_period_calculations(self):
        """Test period calculations."""
        print("\n🧪 Testing Period Calculations...")

        try:
            test_agents = ["sage", "blaze", "nexus"]

            for agent_id in test_agents:
                # Test period key generation
                period_key = budget_manager._get_period_key(agent_id)
                self.log_test(
                    f"Period Key ({agent_id})",
                    period_key is not None and len(period_key) > 0,
                    f"Period: {period_key}",
                )

                # Test next reset calculation
                next_reset = budget_manager._get_next_reset_date(agent_id)
                self.log_test(
                    f"Next Reset ({agent_id})",
                    next_reset is None or isinstance(next_reset, datetime),
                    f"Next reset: {next_reset}",
                )

        except Exception as e:
            self.log_test("Period Calculations", False, f"Error: {e}")

    def print_summary(self):
        """Print test summary."""
        print(f"\n📊 TEST SUMMARY")
        print(f"================")
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")

        if self.failed > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}: {result['message']}")

        # Save results to file
        results_file = project_root / "test_results_budget.json"
        with open(results_file, "w") as f:
            json.dump(
                {
                    "summary": {
                        "total": self.passed + self.failed,
                        "passed": self.passed,
                        "failed": self.failed,
                        "success_rate": self.passed / (self.passed + self.failed) * 100,
                        "timestamp": datetime.now().isoformat(),
                    },
                    "results": self.test_results,
                },
                f,
                indent=2,
            )

        print(f"\n💾 Results saved to: {results_file}")

    async def run_all_tests(self):
        """Run all budget system tests."""
        print("🚀 Starting NGX Agents Budget System Tests")
        print("=" * 50)

        await self.test_budget_configuration()
        await self.test_usage_recording()
        await self.test_budget_limits()
        await self.test_queue_functionality()
        await self.test_degradation()
        await self.test_celery_tasks()
        await self.test_cost_estimation()
        await self.test_period_calculations()

        self.print_summary()

        return self.failed == 0


async def main():
    """Main test runner."""
    tester = BudgetSystemTester()
    success = await tester.run_all_tests()

    if success:
        print("\n🎉 All tests passed! Budget system is ready for production.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review and fix issues before production.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
