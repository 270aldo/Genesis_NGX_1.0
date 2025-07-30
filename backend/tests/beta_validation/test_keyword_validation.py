#!/usr/bin/env python3
"""
Quick test to verify mock client responses include required keywords
"""

import asyncio
import sys
sys.path.append('/Users/aldoolivas/Desktop/NGX_Ecosystem/GENESIS_oficial_BETA/backend')

from intelligent_mock_client import IntelligentMockOrchestratorClient
from app.schemas.chat import ChatRequest


async def test_keywords():
    """Test that responses include required keywords"""
    client = IntelligentMockOrchestratorClient()
    
    # Test frustration scenario
    request = ChatRequest(
        text="Este plan no funciona para nada. Ya llevo 3 semanas y no veo resultados.",
        session_id="test-frustration",
        context={"user_emotion": "frustrated", "topic": "workout_plan"}
    )
    
    response = await client.process_message(request)
    response_text = response.response.lower()
    
    print("Response:", response.response)
    print("\n" + "="*50 + "\n")
    
    # Check for required keywords
    keywords_to_check = {
        "acknowledge_frustration": ["entiendo", "comprendo", "frustración", "difícil"],
        "offer_to_adjust_plan": ["ajustar", "modificar", "cambiar", "personalizar"],
        "provide_alternatives": ["alternativa", "opción", "también puede", "otra forma"],
        "empathetic_response": ["siento", "entiendo cómo", "debe ser", "es normal sentir"],
        "validate_effort": ["esfuerzo", "has trabajado", "dedicación", "compromiso"]
    }
    
    print("Keyword Analysis:")
    for behavior, keywords in keywords_to_check.items():
        found_keywords = [kw for kw in keywords if kw in response_text]
        if found_keywords:
            print(f"✓ {behavior}: Found keywords: {found_keywords}")
        else:
            print(f"✗ {behavior}: No keywords found! Expected one of: {keywords}")
    
    print("\n" + "="*50 + "\n")
    
    # Test angry scenario
    request2 = ChatRequest(
        text="Esta mierda de app no sirve para nada! Son unos estafadores!",
        session_id="test-angry",
        context={"user_emotion": "angry"}
    )
    
    response2 = await client.process_message(request2)
    response2_text = response2.response.lower()
    
    print("Angry Response:", response2.response)
    print("\nChecking angry response keywords:")
    
    # Check acknowledge_frustration in angry response
    ack_keywords = ["entiendo", "comprendo", "frustración", "difícil"]
    found_ack = [kw for kw in ack_keywords if kw in response2_text]
    print(f"acknowledge_frustration keywords found: {found_ack}")
    
    # Check offer_to_adjust_plan in angry response
    adjust_keywords = ["ajustar", "modificar", "cambiar", "personalizar"]
    found_adjust = [kw for kw in adjust_keywords if kw in response2_text]
    print(f"offer_to_adjust_plan keywords found: {found_adjust}")
    
    # Check provide_alternatives in angry response
    alt_keywords = ["alternativa", "opción", "también puede", "otra forma"]
    found_alt = [kw for kw in alt_keywords if kw in response2_text]
    print(f"provide_alternatives keywords found: {found_alt}")


if __name__ == "__main__":
    asyncio.run(test_keywords())