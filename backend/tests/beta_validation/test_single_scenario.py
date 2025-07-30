#!/usr/bin/env python3
"""
Debug single scenario
"""

import asyncio
import sys
sys.path.append('/Users/aldoolivas/Desktop/NGX_Ecosystem/GENESIS_oficial_BETA/backend')

from tests.beta_validation.intelligent_mock_client import IntelligentMockOrchestratorClient
from app.schemas.chat import ChatRequest


async def test_plan_not_working():
    """Test plan not working scenario"""
    client = IntelligentMockOrchestratorClient()
    
    messages = [
        "Llevo 3 semanas y no veo ningún resultado",
        "Estoy haciendo todo lo que dicen y no bajo ni un gramo",
        "Esto es una pérdida de tiempo, nada funciona"
    ]
    
    print("=== Testing Plan Not Working ===\n")
    
    for msg in messages:
        request = ChatRequest(
            text=msg,
            session_id="test-plan",
            context={"weeks_on_plan": 3, "results": "minimal"}
        )
        
        response = await client.process_message(request)
        print(f"Message: {msg}")
        print(f"Response: {response.response}\n")
        print(f"Behaviors: {response.metadata.get('behaviors_included', [])}\n")
        print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_plan_not_working())