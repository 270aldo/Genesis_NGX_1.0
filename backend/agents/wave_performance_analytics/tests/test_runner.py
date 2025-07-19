"""
Test runner for WAVE Performance Analytics Agent.
A+ testing framework with comprehensive coverage reporting.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from typing import Dict, Any, List
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class WaveTestRunner:
    """A+ Test runner for WAVE Performance Analytics Agent."""

    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.coverage_target = 90
        self.results = {}

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories and generate comprehensive report."""
        print("🧪 Starting WAVE Performance Analytics Agent A+ Test Suite")
        print("=" * 70)

        start_time = time.time()

        # Test categories to run
        test_categories = [
            ("Unit Tests", "unit/"),
            ("Integration Tests", "integration/"),
            ("Performance Tests", "performance/"),
            ("Security Tests", "security/"),
        ]

        results = {
            "overall_status": "PASS",
            "total_duration": 0,
            "categories": {},
            "coverage": {},
            "summary": {},
        }

        for category_name, category_path in test_categories:
            print(f"\n🔍 Running {category_name}...")
            category_result = self._run_test_category(category_path)
            results["categories"][category_name] = category_result

            if not category_result["passed"]:
                results["overall_status"] = "FAIL"

        # Generate coverage report
        print(f"\n📊 Generating Coverage Report...")
        coverage_result = self._generate_coverage_report()
        results["coverage"] = coverage_result

        end_time = time.time()
        results["total_duration"] = end_time - start_time

        # Generate summary
        results["summary"] = self._generate_summary(results)

        # Print final report
        self._print_final_report(results)

        return results

    def _run_test_category(self, category_path: str) -> Dict[str, Any]:
        """Run tests for a specific category."""
        test_path = self.test_dir / category_path

        if not test_path.exists():
            return {
                "passed": False,
                "error": f"Test directory {test_path} does not exist",
                "duration": 0,
                "test_count": 0,
            }

        # Pytest arguments for this category
        pytest_args = [
            str(test_path),
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "--strict-markers",  # Strict marker enforcement
            "--strict-config",  # Strict config enforcement
        ]

        start_time = time.time()

        try:
            # Run pytest and capture results
            exit_code = pytest.main(pytest_args)
            duration = time.time() - start_time

            return {
                "passed": exit_code == 0,
                "exit_code": exit_code,
                "duration": duration,
                "test_path": str(test_path),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "passed": False,
                "error": str(e),
                "duration": duration,
                "test_path": str(test_path),
            }

    def _generate_coverage_report(self) -> Dict[str, Any]:
        """Generate code coverage report."""
        # Run pytest with coverage
        coverage_args = [
            str(self.test_dir),
            "--cov=agents.wave_performance_analytics",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=json:coverage.json",
            f"--cov-fail-under={self.coverage_target}",
            "-q",  # Quiet mode for coverage
        ]

        try:
            exit_code = pytest.main(coverage_args)

            # Try to read coverage data
            coverage_data = self._read_coverage_data()

            return {
                "passed": exit_code == 0,
                "target": self.coverage_target,
                "actual": coverage_data.get("totals", {}).get("percent_covered", 0),
                "details": coverage_data,
                "html_report": "htmlcov/index.html",
            }

        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "target": self.coverage_target,
                "actual": 0,
            }

    def _read_coverage_data(self) -> Dict[str, Any]:
        """Read coverage data from JSON report."""
        try:
            coverage_file = Path("coverage.json")
            if coverage_file.exists():
                with open(coverage_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass

        return {}

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary."""
        total_categories = len(results["categories"])
        passed_categories = sum(
            1 for cat in results["categories"].values() if cat["passed"]
        )

        coverage_passed = results["coverage"]["passed"]
        coverage_actual = results["coverage"]["actual"]

        return {
            "categories_passed": f"{passed_categories}/{total_categories}",
            "coverage_status": "PASS" if coverage_passed else "FAIL",
            "coverage_percentage": f"{coverage_actual:.1f}%",
            "overall_grade": self._calculate_grade(results),
            "recommendations": self._generate_recommendations(results),
        }

    def _calculate_grade(self, results: Dict[str, Any]) -> str:
        """Calculate overall test grade."""
        # Calculate score based on multiple factors
        score = 0
        max_score = 100

        # Category success (40 points)
        passed_categories = sum(
            1 for cat in results["categories"].values() if cat["passed"]
        )
        total_categories = len(results["categories"])
        category_score = (passed_categories / total_categories) * 40
        score += category_score

        # Coverage score (30 points)
        coverage_actual = results["coverage"]["actual"]
        if coverage_actual >= 95:
            coverage_score = 30
        elif coverage_actual >= 90:
            coverage_score = 25
        elif coverage_actual >= 85:
            coverage_score = 20
        elif coverage_actual >= 80:
            coverage_score = 15
        else:
            coverage_score = 0
        score += coverage_score

        # Performance score (20 points)
        total_duration = results["total_duration"]
        if total_duration <= 60:  # Under 1 minute
            performance_score = 20
        elif total_duration <= 120:  # Under 2 minutes
            performance_score = 15
        elif total_duration <= 300:  # Under 5 minutes
            performance_score = 10
        else:
            performance_score = 5
        score += performance_score

        # Security tests bonus (10 points)
        security_passed = (
            results["categories"].get("Security Tests", {}).get("passed", False)
        )
        if security_passed:
            score += 10

        # Determine grade
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        else:
            return "F"

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improvement."""
        recommendations = []

        # Check coverage
        coverage_actual = results["coverage"]["actual"]
        if coverage_actual < 90:
            recommendations.append(
                f"Increase test coverage from {coverage_actual:.1f}% to 90%+ for A+ grade"
            )

        # Check failed categories
        for category_name, category_result in results["categories"].items():
            if not category_result["passed"]:
                recommendations.append(f"Fix failing tests in {category_name}")

        # Check performance
        total_duration = results["total_duration"]
        if total_duration > 300:  # 5 minutes
            recommendations.append(
                "Optimize test performance - tests should complete in under 5 minutes"
            )

        # Security recommendations
        security_passed = (
            results["categories"].get("Security Tests", {}).get("passed", False)
        )
        if not security_passed:
            recommendations.append(
                "Ensure all security tests pass for enterprise compliance"
            )

        if not recommendations:
            recommendations.append(
                "Excellent! All tests passing with A+ quality standards."
            )

        return recommendations

    def _print_final_report(self, results: Dict[str, Any]) -> None:
        """Print final test report."""
        print("\n" + "=" * 70)
        print("📋 WAVE PERFORMANCE ANALYTICS AGENT - TEST REPORT")
        print("=" * 70)

        # Overall status
        status_emoji = "✅" if results["overall_status"] == "PASS" else "❌"
        print(f"\n🎯 Overall Status: {status_emoji} {results['overall_status']}")
        print(f"⏱️  Total Duration: {results['total_duration']:.2f}s")
        print(f"🏆 Overall Grade: {results['summary']['overall_grade']}")

        # Category results
        print(f"\n📊 Test Categories:")
        for category_name, category_result in results["categories"].items():
            status = "✅ PASS" if category_result["passed"] else "❌ FAIL"
            duration = category_result.get("duration", 0)
            print(f"  {category_name:20} {status:10} ({duration:.2f}s)")

        # Coverage results
        print(f"\n📈 Code Coverage:")
        coverage_status = "✅ PASS" if results["coverage"]["passed"] else "❌ FAIL"
        coverage_pct = results["coverage"]["actual"]
        coverage_target = results["coverage"]["target"]
        print(
            f"  Coverage:              {coverage_status} {coverage_pct:.1f}% (target: {coverage_target}%)"
        )

        if results["coverage"].get("html_report"):
            print(f"  HTML Report:           {results['coverage']['html_report']}")

        # Summary
        print(f"\n📋 Summary:")
        summary = results["summary"]
        print(f"  Categories Passed:     {summary['categories_passed']}")
        print(f"  Coverage Status:       {summary['coverage_status']}")
        print(f"  Coverage Percentage:   {summary['coverage_percentage']}")

        # Recommendations
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(summary["recommendations"], 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 70)


def run_unit_tests():
    """Run only unit tests."""
    runner = WaveTestRunner()
    return runner._run_test_category("unit/")


def run_integration_tests():
    """Run only integration tests."""
    runner = WaveTestRunner()
    return runner._run_test_category("integration/")


def run_performance_tests():
    """Run only performance tests."""
    runner = WaveTestRunner()
    return runner._run_test_category("performance/")


def run_security_tests():
    """Run only security tests."""
    runner = WaveTestRunner()
    return runner._run_test_category("security/")


def main():
    """Main test runner entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="WAVE Performance Analytics Agent Test Runner"
    )
    parser.add_argument(
        "--category",
        choices=["unit", "integration", "performance", "security", "all"],
        default="all",
        help="Test category to run",
    )
    parser.add_argument(
        "--coverage-target",
        type=int,
        default=90,
        help="Code coverage target percentage",
    )

    args = parser.parse_args()

    runner = WaveTestRunner()
    runner.coverage_target = args.coverage_target

    if args.category == "all":
        results = runner.run_all_tests()
        exit_code = 0 if results["overall_status"] == "PASS" else 1
    elif args.category == "unit":
        result = run_unit_tests()
        exit_code = 0 if result["passed"] else 1
    elif args.category == "integration":
        result = run_integration_tests()
        exit_code = 0 if result["passed"] else 1
    elif args.category == "performance":
        result = run_performance_tests()
        exit_code = 0 if result["passed"] else 1
    elif args.category == "security":
        result = run_security_tests()
        exit_code = 0 if result["passed"] else 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
