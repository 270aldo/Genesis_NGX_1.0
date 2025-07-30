#!/usr/bin/env python3
"""
Test script for Real Orchestrator Client

This script tests the RealOrchestratorClient to ensure it's working properly
before running the full beta validation suite.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.logging_config import get_logger
from tests.beta_validation.real_orchestrator_client import RealOrchestratorClient
from app.schemas.chat import ChatRequest

logger = get_logger(__name__)


async def test_real_client():
    """Test the real orchestrator client"""
    logger.info("Starting Real Orchestrator Client test...")
    
    # Create client in test mode
    client = RealOrchestratorClient(test_mode=True, use_real_ai=False)
    
    try:
        # Initialize client
        logger.info("Initializing client...")
        await client.initialize()
        
        # Perform health check
        logger.info("Performing health check...")
        health = await client.health_check()
        logger.info(f"Health check result: {health}")
        
        if not health.get("healthy", False):
            logger.error("Client is not healthy!")
            return False
        
        # Test simple message
        logger.info("Testing simple message processing...")
        test_request = ChatRequest(
            text="Hola, necesito ayuda para crear un plan de entrenamiento",
            user_id="test-user-001",
            session_id="test-session-001"
        )
        
        response = await client.process_message(test_request)
        
        logger.info(f"Response received:")
        logger.info(f"  Text: {response.response[:100]}...")
        logger.info(f"  Agents used: {response.agents_used}")
        logger.info(f"  Session ID: {response.session_id}")
        logger.info(f"  Metadata: {response.metadata}")
        
        # Test frustration handling
        logger.info("\nTesting frustration handling...")
        frustration_request = ChatRequest(
            text="Este plan no funciona, es muy complicado y no tengo tiempo!",
            user_id="test-user-001",
            session_id="test-session-001",
            context={"user_emotion": "frustrated"}
        )
        
        frustration_response = await client.process_message(frustration_request)
        
        logger.info(f"Frustration response:")
        logger.info(f"  Text: {frustration_response.response[:100]}...")
        logger.info(f"  Agents used: {frustration_response.agents_used}")
        
        # Test error handling
        logger.info("\nTesting error handling...")
        error_request = ChatRequest(
            text="",  # Empty message
            user_id="test-user-001",
            session_id="test-session-001"
        )
        
        error_response = await client.process_message(error_request)
        logger.info(f"Error response: {error_response.response[:100]}...")
        
        logger.info("\nAll tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
        
    finally:
        # Clean up
        logger.info("Cleaning up...")
        await client.cleanup()
        logger.info("Cleanup completed")


async def main():
    """Main entry point"""
    success = await test_real_client()
    
    if success:
        logger.info("\n✅ Real Orchestrator Client is working properly!")
        logger.info("You can now run the full beta validation suite with --use-real-orchestrator")
    else:
        logger.error("\n❌ Real Orchestrator Client tests failed!")
        logger.error("Please fix the issues before running beta validation")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())