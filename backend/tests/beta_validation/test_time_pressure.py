#!/usr/bin/env python3
"""
Debug time pressure scenario
"""

import asyncio
import sys
sys.path.append('/Users/aldoolivas/Desktop/NGX_Ecosystem/GENESIS_oficial_BETA/backend')

from tests.beta_validation.intelligent_mock_client import IntelligentMockOrchestratorClient
from app.schemas.chat import ChatRequest


async def test_time_pressure():
    """Test time pressure scenario"""
    client = IntelligentMockOrchestratorClient()
    
    messages = [
        "No tengo tiempo para nada de esto",
        "Trabajo 12 horas al día, es imposible",
        "Estos planes son para gente que no tiene vida"
    ]
    
    print("=== Testing Time Pressure ===\n")
    
    for msg in messages:
        request = ChatRequest(
            text=msg,
            session_id="test-time",
            context={"available_time": "minimal", "stress_level": "high"}
        )
        
        response = await client.process_message(request)
        print(f"Message: {msg}")
        print(f"Response length: {len(response.response)}")
        print(f"Response preview: {response.response[:200]}...")
        print(f"\nBehaviors: {response.metadata.get('behaviors_included', [])}\n")
        
        # Check keywords
        response_lower = response.response.lower()
        print("Checking keywords:")
        print(f"  flexible_scheduling: {'flexible' in response_lower or 'cuando puedas' in response_lower}")
        print(f"  prioritize_essentials: {'esencial' in response_lower or 'priorizar' in response_lower or 'enfoquémonos' in response_lower}")
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_time_pressure())