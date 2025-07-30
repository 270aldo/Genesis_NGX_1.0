#!/usr/bin/env python3
"""
Run all beta validation scenarios
"""

import asyncio
import sys
sys.path.append('/Users/aldoolivas/Desktop/NGX_Ecosystem/GENESIS_oficial_BETA/backend')

from tests.beta_validation.scenarios.user_frustration_scenarios import UserFrustrationScenarios
from tests.beta_validation.scenarios.edge_case_scenarios import EdgeCaseScenarios
from tests.beta_validation.intelligent_mock_client import IntelligentMockOrchestratorClient


async def main():
    """Run all scenarios"""
    print("=== GENESIS BETA VALIDATION SUMMARY ===\n")
    
    # Create mock client
    client = IntelligentMockOrchestratorClient()
    
    # Track overall results
    total_passed = 0
    total_failed = 0
    
    # Run user frustration scenarios
    frustration_scenarios = UserFrustrationScenarios(client)
    frustration_results = await frustration_scenarios.run_all_scenarios()
    total_passed += frustration_results['passed']
    total_failed += frustration_results['failed']
    
    print(f"USER_FRUSTRATION: {frustration_results['passed']}/{frustration_results['total_scenarios']} passed")
    if frustration_results['failed'] > 0:
        print("  Failed scenarios:")
        for detail in frustration_results['details']:
            if not detail.get('passed', False):
                issues = detail.get('issues', [])
                if issues:
                    print(f"    - {detail['scenario']}: {issues[0]}")
    
    # Run edge case scenarios
    edge_scenarios = EdgeCaseScenarios(client)
    edge_results = await edge_scenarios.run_all_scenarios()
    total_passed += edge_results['passed']
    total_failed += edge_results['failed']
    
    print(f"\nEDGE_CASES: {edge_results['passed']}/{edge_results['total_scenarios']} passed")
    if edge_results['failed'] > 0:
        print("  Failed scenarios:")
        for detail in edge_results['details']:
            if not detail.get('passed', False):
                issues = detail.get('issues', [])
                if issues:
                    print(f"    - {detail['scenario']}: {issues[0]}")
    
    # Calculate overall metrics
    total_scenarios = total_passed + total_failed
    pass_rate = (total_passed / total_scenarios * 100) if total_scenarios > 0 else 0
    
    print(f"\n{'='*50}")
    print(f"OVERALL RESULTS:")
    print(f"Total scenarios: {total_scenarios}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Pass rate: {pass_rate:.1f}%")
    
    # Launch recommendation
    if pass_rate >= 90 and total_failed == 0:
        print("\n✅ READY FOR BETA LAUNCH - All tests passing!")
    elif pass_rate >= 90:
        print("\n⚠️ DELAY BETA LAUNCH - High pass rate but critical failures exist")
    else:
        print(f"\n❌ DO NOT LAUNCH - Pass rate below 90% ({pass_rate:.1f}%)")


if __name__ == "__main__":
    asyncio.run(main())