#!/usr/bin/env python3
"""
Test only frustration scenarios
"""

import asyncio
import sys
sys.path.append('/Users/aldoolivas/Desktop/NGX_Ecosystem/GENESIS_oficial_BETA/backend')

from tests.beta_validation.scenarios.user_frustration_scenarios import UserFrustrationScenarios
from tests.beta_validation.intelligent_mock_client import IntelligentMockOrchestratorClient


async def main():
    """Run frustration tests"""
    print("=== Testing User Frustration Scenarios ===\n")
    
    # Create mock client
    client = IntelligentMockOrchestratorClient()
    
    # Create scenarios
    scenarios = UserFrustrationScenarios(client)
    
    # Run all scenarios
    results = await scenarios.run_all_scenarios()
    
    # Print results
    print(f"\nTotal scenarios: {results['total_scenarios']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Pass rate: {results['passed'] / results['total_scenarios'] * 100:.1f}%")
    
    # Print failed scenarios
    if results['failed'] > 0:
        print("\n=== Failed Scenarios ===")
        for detail in results['details']:
            if not detail.get('passed', False):
                print(f"\n{detail['scenario']}:")
                if 'issues' in detail:
                    for issue in detail['issues']:
                        print(f"  - {issue}")
                if 'error' in detail:
                    print(f"  ERROR: {detail['error']}")


if __name__ == "__main__":
    asyncio.run(main())