#!/usr/bin/env python3
"""Debug script for beta validation issues"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.schemas.chat import ChatRequest, ChatResponse
from tests.beta_validation.intelligent_mock_client import IntelligentMockOrchestratorClient
from datetime import datetime


async def test_chat_request_format():
    """Test the ChatRequest format issue"""
    print("Testing ChatRequest format...")
    
    # Test valid request
    try:
        request = ChatRequest(
            text="Test message",
            session_id="test_session_123",
            user_id="test_user",
            context={"test": "context"}
        )
        print("✅ Valid ChatRequest created successfully")
        print(f"   Fields: text='{request.text}', session_id='{request.session_id}'")
    except Exception as e:
        print(f"❌ Error creating ChatRequest: {e}")
        
    # Test invalid session_id with dots
    try:
        request_bad = ChatRequest(
            text="Test message",
            session_id="test.session.123",  # This should fail
            user_id="test_user"
        )
        print("❌ Invalid session_id was accepted (should have failed)")
    except Exception as e:
        print(f"✅ Invalid session_id correctly rejected: {e}")


async def test_mock_client():
    """Test the intelligent mock client"""
    print("\nTesting IntelligentMockOrchestratorClient...")
    
    client = IntelligentMockOrchestratorClient()
    
    # Test simple request
    request = ChatRequest(
        text="Quiero perder 20kg en 2 semanas para mi boda",
        session_id="test_impossible_goals_123",
        context={"goal_feasibility": "impossible"}
    )
    
    try:
        response = await client.process_message(request)
        print("✅ Mock client processed message successfully")
        print(f"   Response type: {type(response)}")
        print(f"   Session ID: {response.session_id}")
        print(f"   Response length: {len(response.response)} chars")
        
        # Check for expected behaviors
        response_lower = response.response.lower()
        behaviors_found = []
        
        if "fisiológicamente" in response_lower or "cuerpo necesita" in response_lower:
            behaviors_found.append("educate_on_physiology")
        if "realista" in response_lower or "semanas" in response_lower:
            behaviors_found.append("explain_realistic_timelines")
            
        print(f"   Behaviors found: {behaviors_found}")
        
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        import traceback
        traceback.print_exc()


async def test_edge_case_scenario():
    """Test a specific edge case scenario"""
    print("\nTesting edge case scenario (impossible goals)...")
    
    from tests.beta_validation.scenarios.edge_case_scenarios import EdgeCaseScenarios
    
    client = IntelligentMockOrchestratorClient()
    scenarios = EdgeCaseScenarios(client)
    
    try:
        result = await scenarios.test_impossible_goals()
        print(f"✅ Scenario completed: passed={result['passed']}")
        if not result['passed']:
            print(f"   Issues: {result['issues']}")
            print(f"   Behaviors detected: {result['behaviors_detected']}")
            
            # Expected behaviors
            expected = [
                "explain_realistic_timelines",
                "health_risks_warning", 
                "offer_achievable_alternatives",
                "maintain_empathy",
                "educate_on_physiology"
            ]
            missing = set(expected) - set(result['behaviors_detected'])
            print(f"   Missing behaviors: {missing}")
            
    except Exception as e:
        print(f"❌ Error running scenario: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all debug tests"""
    print("=" * 60)
    print("NGX GENESIS Beta Validation Debug")
    print("=" * 60)
    
    await test_chat_request_format()
    await test_mock_client()
    await test_edge_case_scenario()
    
    print("\n" + "=" * 60)
    print("Debug session complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())