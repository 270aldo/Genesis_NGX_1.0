#!/usr/bin/env python3
"""
Simple test to debug Beta Validation issues.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.schemas.chat import ChatRequest, ChatResponse
from tests.beta_validation.scenarios.user_frustration_scenarios import UserFrustrationScenarios


async def test_simple():
    """Test a simple scenario"""
    print("Testing simple scenario...")
    
    # Create a mock client
    class MockClient:
        async def process_message(self, request):
            print(f"Received request: {request}")
            print(f"Request type: {type(request)}")
            print(f"Request text: {request.text}")
            
            return ChatResponse(
                response="Test response",
                session_id=request.session_id or "test-session",
                agents_used=["NEXUS"],
                agent_responses=[],
                metadata={}
            )
    
    # Create scenario
    client = MockClient()
    scenarios = UserFrustrationScenarios(client)
    
    # Run one scenario
    try:
        result = await scenarios.run_scenario("angry_wrong_plan")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_simple())