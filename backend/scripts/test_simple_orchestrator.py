#!/usr/bin/env python3
"""
Simple test to debug orchestrator initialization issues.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_simple():
    """Test basic orchestrator setup"""
    print("=== Testing Basic Orchestrator Setup ===")
    
    try:
        # Step 1: Import basic modules
        print("\n1. Importing modules...")
        from core.logging_config import get_logger
        from agents.orchestrator.agent import NGXNexusOrchestrator
        from core.settings_lazy import settings
        print("✓ Imports successful")
        
        # Step 2: Check environment
        print("\n2. Checking environment...")
        print(f"   ENV: {settings.env}")
        print(f"   A2A URL: {getattr(settings, 'a2a_server_url', 'Not set')}")
        print(f"   Vertex Project: {getattr(settings, 'vertex_project_id', 'Not set')}")
        
        # Step 3: Test simple instantiation
        print("\n3. Creating orchestrator instance...")
        orchestrator = NGXNexusOrchestrator(
            a2a_server_url="http://localhost:8001",
            state_manager=None,  # Simple test without state
            use_streaming=False
        )
        print("✓ Orchestrator created")
        
        # Step 4: Check orchestrator properties
        print("\n4. Checking orchestrator properties...")
        print(f"   Name: {orchestrator.name}")
        print(f"   ID: {orchestrator.id}")
        print(f"   Skills: {len(orchestrator.skills)}")
        
        print("\n✅ Basic setup successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_simple())
    sys.exit(0 if success else 1)