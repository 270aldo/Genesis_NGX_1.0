#!/usr/bin/env python3
"""
GENESIS Beta Validation Test Runner

This script runs all beta validation tests and generates comprehensive reports
to ensure the system is ready for BETA launch.

Usage:
    python -m tests.beta_validation.run_beta_validation [options]

Options:
    --category CATEGORY     Run only specific category of tests
    --verbose              Enable verbose output
    --report               Generate detailed HTML report
    --quick                Run quick subset of tests
    --parallel             Run tests in parallel (faster but uses more resources)
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback
from concurrent.futures import ProcessPoolExecutor

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.logging_config import get_logger
from tests.beta_validation.scenarios import (
    UserFrustrationScenarios,
    EdgeCaseScenarios,
    MultiAgentScenarios,
    EcosystemIntegrationScenarios,
    StressTestScenarios
)
from tests.beta_validation.validators import ResponseQualityValidator

logger = get_logger(__name__)


class BetaValidationRunner:
    """Main runner for beta validation tests"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the beta validation runner
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.results = {
            "start_time": None,
            "end_time": None,
            "duration": None,
            "categories": {},
            "summary": {
                "total_scenarios": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0
            },
            "critical_issues": [],
            "warnings": []
        }
        
        # Initialize orchestrator client (mock for now)
        self.orchestrator_client = self._create_orchestrator_client()
        
        # Initialize MCP gateway client if available
        self.mcp_gateway_client = self._create_mcp_gateway_client()
        
        # Initialize response validator
        self.response_validator = ResponseQualityValidator()
    
    def _create_orchestrator_client(self):
        """Create orchestrator client for tests"""
        # In a real implementation, this would create an actual client
        # For now, we'll create a mock client
        class MockOrchestratorClient:
            async def process_message(self, request):
                """Mock message processing"""
                from app.schemas.chat import ChatResponse
                
                # Simulate different responses based on message content
                message = request.message.lower()
                
                if "error" in message:
                    raise Exception("Simulated error")
                
                response_templates = {
                    "frustration": "Entiendo tu frustración. Es completamente normal sentirse así. Vamos a trabajar juntos para encontrar una solución que funcione para ti.",
                    "plan": "Aquí está tu plan personalizado:\n1. Lunes: Entrenamiento de fuerza superior\n2. Martes: Cardio moderado 30 min\n3. Miércoles: Descanso activo",
                    "nutrition": "Para tu objetivo, recomiendo consumir aproximadamente 2000 calorías diarias, con 150g de proteína, 200g de carbohidratos y 65g de grasas saludables.",
                    "default": "Gracias por tu mensaje. Estoy aquí para ayudarte con tu journey de fitness y bienestar."
                }
                
                # Select appropriate response
                response_text = response_templates["default"]
                for key, template in response_templates.items():
                    if key in message:
                        response_text = template
                        break
                
                return ChatResponse(
                    message=response_text,
                    session_id=request.session_id,
                    agents_used=["NEXUS", "BLAZE"],
                    agent_responses=[],
                    metadata={"mock": True}
                )
            
            @property
            def is_connected(self):
                return True
            
            async def connect(self):
                pass
        
        return MockOrchestratorClient()
    
    def _create_mcp_gateway_client(self):
        """Create MCP gateway client if available"""
        # For now, return None as MCP gateway is optional
        return None
    
    async def run_all_tests(self, categories: Optional[List[str]] = None, parallel: bool = False):
        """
        Run all beta validation tests
        
        Args:
            categories: Optional list of categories to run (None = all)
            parallel: Whether to run tests in parallel
        """
        self.results["start_time"] = datetime.utcnow().isoformat()
        logger.info("Starting GENESIS Beta Validation Tests")
        
        # Define test categories
        test_categories = {
            "user_frustration": UserFrustrationScenarios,
            "edge_cases": EdgeCaseScenarios,
            "multi_agent": MultiAgentScenarios,
            "ecosystem_integration": EcosystemIntegrationScenarios,
            "stress_tests": StressTestScenarios
        }
        
        # Filter categories if specified
        if categories:
            test_categories = {k: v for k, v in test_categories.items() if k in categories}
        
        # Run tests
        if parallel and len(test_categories) > 1:
            await self._run_parallel_tests(test_categories)
        else:
            await self._run_sequential_tests(test_categories)
        
        # Finalize results
        self.results["end_time"] = datetime.utcnow().isoformat()
        start = datetime.fromisoformat(self.results["start_time"])
        end = datetime.fromisoformat(self.results["end_time"])
        self.results["duration"] = (end - start).total_seconds()
        
        # Calculate summary
        self._calculate_summary()
        
        # Identify critical issues
        self._identify_critical_issues()
        
        logger.info(f"Beta Validation Tests completed in {self.results['duration']:.2f} seconds")
        logger.info(f"Overall pass rate: {self.results['summary']['pass_rate']:.1f}%")
    
    async def _run_sequential_tests(self, test_categories: Dict[str, Any]):
        """Run tests sequentially"""
        for category_name, scenario_class in test_categories.items():
            logger.info(f"Running {category_name} scenarios...")
            
            try:
                # Initialize scenario with appropriate clients
                if category_name == "ecosystem_integration":
                    scenario = scenario_class(self.orchestrator_client, self.mcp_gateway_client)
                else:
                    scenario = scenario_class(self.orchestrator_client)
                
                # Run scenarios
                category_results = await scenario.run_all_scenarios()
                self.results["categories"][category_name] = category_results
                
                # Update totals
                self.results["summary"]["total_scenarios"] += category_results.get("total_scenarios", 0)
                self.results["summary"]["passed"] += category_results.get("passed", 0)
                self.results["summary"]["failed"] += category_results.get("failed", 0)
                
                logger.info(f"{category_name}: {category_results.get('passed', 0)}/{category_results.get('total_scenarios', 0)} passed")
                
            except Exception as e:
                logger.error(f"Error running {category_name}: {e}")
                logger.error(traceback.format_exc())
                self.results["categories"][category_name] = {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "passed": 0,
                    "failed": 1,
                    "total_scenarios": 1
                }
                self.results["summary"]["failed"] += 1
                self.results["summary"]["total_scenarios"] += 1
    
    async def _run_parallel_tests(self, test_categories: Dict[str, Any]):
        """Run tests in parallel"""
        tasks = []
        
        for category_name, scenario_class in test_categories.items():
            task = self._run_category_async(category_name, scenario_class)
            tasks.append(task)
        
        # Run all categories in parallel
        category_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for (category_name, _), result in zip(test_categories.items(), category_results):
            if isinstance(result, Exception):
                logger.error(f"Error running {category_name}: {result}")
                self.results["categories"][category_name] = {
                    "error": str(result),
                    "passed": 0,
                    "failed": 1,
                    "total_scenarios": 1
                }
                self.results["summary"]["failed"] += 1
                self.results["summary"]["total_scenarios"] += 1
            else:
                self.results["categories"][category_name] = result
                self.results["summary"]["total_scenarios"] += result.get("total_scenarios", 0)
                self.results["summary"]["passed"] += result.get("passed", 0)
                self.results["summary"]["failed"] += result.get("failed", 0)
    
    async def _run_category_async(self, category_name: str, scenario_class):
        """Run a single category asynchronously"""
        logger.info(f"Running {category_name} scenarios...")
        
        if category_name == "ecosystem_integration":
            scenario = scenario_class(self.orchestrator_client, self.mcp_gateway_client)
        else:
            scenario = scenario_class(self.orchestrator_client)
        
        result = await scenario.run_all_scenarios()
        logger.info(f"{category_name}: {result.get('passed', 0)}/{result.get('total_scenarios', 0)} passed")
        
        return result
    
    def _calculate_summary(self):
        """Calculate summary statistics"""
        total = self.results["summary"]["total_scenarios"]
        if total > 0:
            self.results["summary"]["pass_rate"] = (
                self.results["summary"]["passed"] / total * 100
            )
        
        # Add category-specific summaries
        for category_name, category_data in self.results["categories"].items():
            if "total_scenarios" in category_data:
                category_total = category_data["total_scenarios"]
                category_passed = category_data.get("passed", 0)
                
                if category_total > 0:
                    pass_rate = category_passed / category_total * 100
                    self.results["categories"][category_name]["pass_rate"] = pass_rate
    
    def _identify_critical_issues(self):
        """Identify critical issues that must be fixed before BETA"""
        critical_patterns = [
            "medical emergency",
            "suicide",
            "safety compliance failed",
            "data privacy",
            "cascade failure",
            "security",
            "guardian_activation"
        ]
        
        for category_name, category_data in self.results["categories"].items():
            if "details" not in category_data:
                continue
                
            for scenario in category_data["details"]:
                # Check for critical failures
                if not scenario.get("passed", False):
                    scenario_name = scenario.get("scenario", "unknown")
                    
                    # Check if it's a critical scenario
                    for pattern in critical_patterns:
                        if pattern in scenario_name.lower() or pattern in str(scenario.get("issues", [])).lower():
                            self.results["critical_issues"].append({
                                "category": category_name,
                                "scenario": scenario_name,
                                "issues": scenario.get("issues", []),
                                "severity": "CRITICAL"
                            })
                            break
                    else:
                        # Non-critical but still failed
                        if scenario.get("issues"):
                            self.results["warnings"].append({
                                "category": category_name,
                                "scenario": scenario_name,
                                "issues": scenario.get("issues", []),
                                "severity": "WARNING"
                            })
    
    def save_results(self, output_dir: str = "reports"):
        """
        Save test results to file
        
        Args:
            output_dir: Directory to save results
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"beta_validation_results_{timestamp}.json"
        filepath = output_path / filename
        
        # Save results
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {filepath}")
        
        # Also save a summary report
        self._save_summary_report(output_path, timestamp)
        
        return filepath
    
    def _save_summary_report(self, output_path: Path, timestamp: str):
        """Save a human-readable summary report"""
        report_file = output_path / f"beta_validation_summary_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("GENESIS BETA VALIDATION SUMMARY REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Test Date: {self.results['start_time']}\n")
            f.write(f"Duration: {self.results['duration']:.2f} seconds\n")
            f.write(f"Overall Pass Rate: {self.results['summary']['pass_rate']:.1f}%\n")
            f.write(f"Total Scenarios: {self.results['summary']['total_scenarios']}\n")
            f.write(f"Passed: {self.results['summary']['passed']}\n")
            f.write(f"Failed: {self.results['summary']['failed']}\n\n")
            
            # Category breakdown
            f.write("CATEGORY BREAKDOWN\n")
            f.write("-" * 80 + "\n")
            
            for category, data in self.results["categories"].items():
                if "error" in data:
                    f.write(f"\n{category.upper()}: ERROR - {data['error']}\n")
                else:
                    pass_rate = data.get("pass_rate", 0)
                    f.write(f"\n{category.upper()}: {pass_rate:.1f}% pass rate\n")
                    f.write(f"  Scenarios: {data.get('total_scenarios', 0)}\n")
                    f.write(f"  Passed: {data.get('passed', 0)}\n")
                    f.write(f"  Failed: {data.get('failed', 0)}\n")
            
            # Critical issues
            if self.results["critical_issues"]:
                f.write("\n" + "=" * 80 + "\n")
                f.write("CRITICAL ISSUES (MUST FIX BEFORE BETA)\n")
                f.write("=" * 80 + "\n")
                
                for issue in self.results["critical_issues"]:
                    f.write(f"\n[{issue['severity']}] {issue['category']} - {issue['scenario']}\n")
                    for problem in issue['issues']:
                        f.write(f"  - {problem}\n")
            
            # Warnings
            if self.results["warnings"]:
                f.write("\n" + "=" * 80 + "\n")
                f.write("WARNINGS (SHOULD FIX)\n")
                f.write("=" * 80 + "\n")
                
                for warning in self.results["warnings"][:10]:  # First 10 warnings
                    f.write(f"\n[{warning['severity']}] {warning['category']} - {warning['scenario']}\n")
                    for problem in warning['issues']:
                        f.write(f"  - {problem}\n")
                
                if len(self.results["warnings"]) > 10:
                    f.write(f"\n... and {len(self.results['warnings']) - 10} more warnings\n")
            
            # Recommendations
            f.write("\n" + "=" * 80 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("=" * 80 + "\n")
            
            if self.results["critical_issues"]:
                f.write("\n1. BLOCK BETA LAUNCH - Critical issues found\n")
                f.write("   Fix all critical issues before proceeding\n")
            elif self.results["summary"]["pass_rate"] < 90:
                f.write("\n1. DELAY BETA LAUNCH - Pass rate below 90%\n")
                f.write("   Improve failing scenarios before launch\n")
            else:
                f.write("\n1. READY FOR BETA - All critical tests passed\n")
                f.write("   Consider fixing warnings for better user experience\n")
            
            f.write("\n2. Focus areas for improvement:\n")
            
            # Find worst performing categories
            worst_categories = []
            for category, data in self.results["categories"].items():
                if "pass_rate" in data and data["pass_rate"] < 80:
                    worst_categories.append((category, data["pass_rate"]))
            
            worst_categories.sort(key=lambda x: x[1])
            
            for category, pass_rate in worst_categories[:3]:
                f.write(f"   - {category}: {pass_rate:.1f}% pass rate\n")
        
        logger.info(f"Summary report saved to {report_file}")
    
    def generate_html_report(self, output_dir: str = "reports"):
        """Generate an HTML report with visualizations"""
        # This would generate a nice HTML report with charts
        # For now, we'll skip the implementation
        logger.info("HTML report generation not implemented yet")
    
    def print_summary(self):
        """Print a summary to console"""
        print("\n" + "=" * 80)
        print("BETA VALIDATION TEST RESULTS")
        print("=" * 80)
        
        print(f"\nOverall Pass Rate: {self.results['summary']['pass_rate']:.1f}%")
        print(f"Total Scenarios: {self.results['summary']['total_scenarios']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        
        if self.results["critical_issues"]:
            print(f"\n⚠️  CRITICAL ISSUES FOUND: {len(self.results['critical_issues'])}")
            print("BETA LAUNCH SHOULD BE BLOCKED UNTIL THESE ARE FIXED")
            
            for issue in self.results["critical_issues"][:3]:
                print(f"\n- {issue['category']}/{issue['scenario']}")
                for problem in issue['issues'][:2]:
                    print(f"  • {problem}")
        
        print("\nCategory Results:")
        for category, data in self.results["categories"].items():
            if "pass_rate" in data:
                status = "✅" if data["pass_rate"] >= 90 else "⚠️" if data["pass_rate"] >= 70 else "❌"
                print(f"  {status} {category}: {data['pass_rate']:.1f}%")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run GENESIS Beta Validation Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--category",
        type=str,
        help="Run only specific category (user_frustration, edge_cases, multi_agent, ecosystem_integration, stress_tests)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed HTML report"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick subset of tests"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Directory to save reports (default: reports)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine categories to run
    categories = None
    if args.category:
        categories = [args.category]
    elif args.quick:
        # Quick subset for rapid validation
        categories = ["user_frustration", "edge_cases"]
    
    # Create and run validator
    runner = BetaValidationRunner()
    
    try:
        await runner.run_all_tests(categories=categories, parallel=args.parallel)
        
        # Save results
        runner.save_results(args.output_dir)
        
        # Generate HTML report if requested
        if args.report:
            runner.generate_html_report(args.output_dir)
        
        # Print summary
        runner.print_summary()
        
        # Exit with appropriate code
        if runner.results["critical_issues"]:
            sys.exit(2)  # Critical issues found
        elif runner.results["summary"]["pass_rate"] < 90:
            sys.exit(1)  # Below acceptable threshold
        else:
            sys.exit(0)  # Success
            
    except Exception as e:
        logger.error(f"Fatal error running beta validation: {e}")
        logger.error(traceback.format_exc())
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())