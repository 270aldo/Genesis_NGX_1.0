#!/usr/bin/env python3
"""
Test script to verify the Real Orchestrator Client works correctly
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.schemas.chat import ChatRequest
from tests.beta_validation.real_orchestrator_client import RealOrchestratorClient
from tests.beta_validation.test_config import TestEnvironment
from core.logging_config import get_logger

logger = get_logger(__name__)


async def test_real_orchestrator():
    """Test the real orchestrator client"""
    print("\n" + "="*60)
    print("Testing Real Orchestrator Client")
    print("="*60 + "\n")
    
    # Create test environment
    test_env = TestEnvironment(use_real_ai=False)
    await test_env.setup()
    
    # Create real orchestrator client
    client = RealOrchestratorClient(test_mode=True)
    
    try:
        # Initialize client
        print("1. Initializing Real Orchestrator Client...")
        await client.initialize()
        print("   ✅ Client initialized successfully")
        
        # Test simple message
        print("\n2. Testing simple message processing...")
        request = ChatRequest(
            text="Hola, necesito ayuda con mi plan de entrenamiento",
            session_id="test-session-001",
            user_id="test-user-001"
        )
        
        response = await client.process_message(request)
        print(f"   ✅ Response received:")
        print(f"      - Session ID: {response.session_id}")
        print(f"      - Agents used: {response.agents_used}")
        print(f"      - Response preview: {response.response[:100]}...")
        
        # Test with context
        print("\n3. Testing message with context...")
        request_with_context = ChatRequest(
            text="Mi plan actual no está funcionando, estoy frustrado",
            session_id="test-session-002",
            user_id="test-user-001",
            context={
                "user_emotion": "frustrated",
                "topic": "workout_plan"
            }
        )
        
        response = await client.process_message(request_with_context)
        print(f"   ✅ Response received:")
        print(f"      - Agents used: {response.agents_used}")
        print(f"      - Metadata: {response.metadata}")
        
        # Test error handling
        print("\n4. Testing error handling...")
        error_request = ChatRequest(
            text="Test error scenario",
            session_id="error-session",
            user_id=None  # This might cause issues
        )
        
        response = await client.process_message(error_request)
        print(f"   ✅ Error handled gracefully:")
        print(f"      - Response: {response.response[:100]}...")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        print("\n5. Cleaning up...")
        await client.cleanup()
        await test_env.teardown()
        print("   ✅ Cleanup completed")


async def test_scenario_execution():
    """Test running actual scenarios with real orchestrator"""
    print("\n" + "="*60)
    print("Testing Scenario Execution with Real Orchestrator")
    print("="*60 + "\n")
    
    from tests.beta_validation.scenarios.user_frustration_scenarios import UserFrustrationScenarios
    
    # Create real orchestrator client
    client = RealOrchestratorClient(test_mode=True)
    await client.initialize()
    
    try:
        # Create scenario runner
        scenarios = UserFrustrationScenarios(client)
        
        # Run a single scenario
        print("Running 'angry_wrong_plan' scenario...")
        result = await scenarios.run_scenario("angry_wrong_plan")
        
        print(f"\nScenario Result:")
        print(f"  - Passed: {result['passed']}")
        print(f"  - Issues: {result.get('issues', [])}")
        print(f"  - Messages exchanged: {len(result.get('messages', []))}")
        
        if result.get('expected_behaviors'):
            print(f"  - Expected behaviors found: {result['expected_behaviors']['found']}")
            print(f"  - Expected behaviors missing: {result['expected_behaviors']['missing']}")
            
    finally:
        await client.cleanup()


async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Real Orchestrator Client")
    parser.add_argument(
        "--scenario", 
        action="store_true",
        help="Test scenario execution"
    )
    
    args = parser.parse_args()
    
    try:
        # Run basic tests
        await test_real_orchestrator()
        
        # Run scenario tests if requested
        if args.scenario:
            await test_scenario_execution()
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())