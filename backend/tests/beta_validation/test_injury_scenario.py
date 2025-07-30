#!/usr/bin/env python3
"""
Debug injury frustration scenario
"""

import asyncio
import sys
sys.path.append('/Users/aldoolivas/Desktop/NGX_Ecosystem/GENESIS_oficial_BETA/backend')

from tests.beta_validation.intelligent_mock_client import IntelligentMockOrchestratorClient
from app.schemas.chat import ChatRequest


async def test_injury():
    """Test injury scenario"""
    client = IntelligentMockOrchestratorClient()
    
    messages = [
        "Me lesioné y ahora no puedo hacer nada",
        "Justo cuando estaba progresando, maldita sea",
        "¿Para qué sigo pagando si no puedo entrenar?"
    ]
    
    print("=== Testing Injury Frustration ===\n")
    
    for msg in messages:
        request = ChatRequest(
            text=msg,
            session_id="test-injury",
            context={"injury_type": "knee", "severity": "moderate"}
        )
        
        response = await client.process_message(request)
        print(f"Message: {msg}")
        print(f"Response: {response.response}\n")
        print(f"Behaviors: {response.metadata.get('behaviors_included', [])}\n")
        print("="*80 + "\n")
        
        # Check keywords
        response_lower = response.response.lower()
        print("Checking keywords:")
        print(f"  express_empathy: {'lamento' in response_lower or 'siento' in response_lower}")
        print(f"  adapt_plan_for_injury: {'adaptar' in response_lower or 'modificaré' in response_lower}")
        print(f"  suggest_alternative_exercises: {'alternativas' in response_lower or 'mientras' in response_lower}")
        print(f"  focus_on_recovery: {'recuperación' in response_lower or 'prioridad' in response_lower}")
        print(f"  maintain_motivation: {'temporal' in response_lower or 'volverás' in response_lower}")
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_injury())