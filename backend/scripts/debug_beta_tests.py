#!/usr/bin/env python3
"""
Debug Beta Validation tests to find the issue.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.beta_validation.run_beta_validation import BetaValidationRunner


async def debug_tests():
    """Debug the tests"""
    print("Starting debug...")
    
    # Create runner
    runner = BetaValidationRunner()
    
    # Run with debug
    try:
        await runner.run_all_tests(categories=["user_frustration"])
        
        # Print detailed results
        print("\n=== DETAILED RESULTS ===")
        print(f"Results: {runner.results}")
        
        # Print category details
        if "user_frustration" in runner.results["categories"]:
            cat_results = runner.results["categories"]["user_frustration"]
            print(f"\nUser Frustration Results:")
            print(f"Total: {cat_results.get('total_scenarios', 0)}")
            print(f"Passed: {cat_results.get('passed', 0)}")
            print(f"Failed: {cat_results.get('failed', 0)}")
            
            # Print scenario details
            print("\nScenario Details:")
            for detail in cat_results.get("details", []):
                print(f"\n- {detail.get('scenario', 'unknown')}: {'PASS' if detail.get('passed') else 'FAIL'}")
                if "error" in detail:
                    print(f"  Error: {detail['error']}")
                if "issues" in detail:
                    print(f"  Issues: {detail['issues']}")
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_tests())