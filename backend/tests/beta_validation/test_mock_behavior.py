#!/usr/bin/env python3
"""
Debug mock behavior detection
"""

import asyncio
import sys
sys.path.append('/Users/aldoolivas/Desktop/NGX_Ecosystem/GENESIS_oficial_BETA/backend')

from tests.beta_validation.intelligent_mock_client import IntelligentMockOrchestratorClient
from app.schemas.chat import ChatRequest


async def test_body_image():
    """Test body image scenario"""
    client = IntelligentMockOrchestratorClient()
    
    request = ChatRequest(
        text="Soy demasiado gorda, nada funciona para mí",
        session_id="test-body-image",
        context={"user_emotion": "depressed", "sensitive_topic": True}
    )
    
    response = await client.process_message(request)
    print("Body Image Response:")
    print(response.response)
    print("\nBehaviors included:", response.metadata.get('behaviors_included', []))
    
    # Check if expected behaviors are in response
    response_lower = response.response.lower()
    
    print("\n=== Checking Keywords ===")
    # validate_feelings
    validate_keywords = ["válidos", "válido", "es normal sentir", "normal sentir"]
    print(f"validate_feelings keywords: {[k for k in validate_keywords if k in response_lower]}")
    
    # focus_on_health_not_appearance
    health_keywords = ["salud", "cómo te sientes", "no solo en cómo te ves", "bienestar"]
    print(f"focus_on_health_not_appearance keywords: {[k for k in health_keywords if k in response_lower]}")


async def test_technology_confusion():
    """Test technology confusion scenario"""
    client = IntelligentMockOrchestratorClient()
    
    request = ChatRequest(
        text="No entiendo nada, esto es muy complicado",
        session_id="test-tech",
        context={"user_emotion": "frustrated", "tech_savvy": "low", "topic": "technology"}
    )
    
    response = await client.process_message(request)
    print("\n\nTechnology Confusion Response:")
    print(response.response)
    print("\nBehaviors included:", response.metadata.get('behaviors_included', []))


async def main():
    await test_body_image()
    await test_technology_confusion()


if __name__ == "__main__":
    asyncio.run(main())