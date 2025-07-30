#!/usr/bin/env python3
"""
Test script to reproduce the import hanging issue.
"""

import sys
import time

print(f"Python: {sys.version}")
print(f"Starting import test at {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Test imports one by one to find where it hangs
print("\n1. Testing basic imports...")
try:
    import asyncio
    print("   ✓ asyncio imported")
except Exception as e:
    print(f"   ✗ asyncio failed: {e}")

print("\n2. Testing core.settings import...")
try:
    from core.settings import Settings
    print("   ✓ core.settings imported (class only)")
except Exception as e:
    print(f"   ✗ core.settings failed: {e}")

print("\n3. Testing settings instantiation...")
try:
    from core.settings_lazy import settings
    print("   ✓ settings instance imported")
except Exception as e:
    print(f"   ✗ settings instance failed: {e}")

print("\n4. Testing vertex_ai client import...")
try:
    from clients.vertex_ai.client import VertexAIClient
    print("   ✓ VertexAIClient class imported")
except Exception as e:
    print(f"   ✗ VertexAIClient class failed: {e}")

print("\n5. Testing vertex_ai_client instance import...")
try:
    from clients.vertex_ai.client import vertex_ai_client
    print("   ✓ vertex_ai_client instance imported")
except Exception as e:
    print(f"   ✗ vertex_ai_client instance failed: {e}")

print("\n6. Testing redis_pool_manager import...")
try:
    from core.redis_pool import redis_pool_manager
    print("   ✓ redis_pool_manager imported")
except Exception as e:
    print(f"   ✗ redis_pool_manager failed: {e}")

print("\n7. Testing a2a_server import...")
try:
    from infrastructure.a2a_optimized import a2a_server
    print("   ✓ a2a_server imported")
except Exception as e:
    print(f"   ✗ a2a_server failed: {e}")

print("\n8. Testing a2a_adapter import...")
try:
    from infrastructure.adapters.a2a_adapter import a2a_adapter
    print("   ✓ a2a_adapter imported")
except Exception as e:
    print(f"   ✗ a2a_adapter failed: {e}")

print("\n9. Testing orchestrator agent import...")
try:
    print("   Starting orchestrator import...")
    from agents.orchestrator.agent import NGXNexusOrchestrator
    print("   ✓ NGXNexusOrchestrator imported successfully!")
except Exception as e:
    print(f"   ✗ NGXNexusOrchestrator failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\nTest completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")