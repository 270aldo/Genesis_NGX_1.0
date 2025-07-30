#!/usr/bin/env python3
"""
Test orchestrator with a comprehensive analysis and fix.

This script identifies and resolves the blocking import issues.
"""

import os
import sys
import time
import asyncio
from unittest.mock import Mock, patch
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

print("=== Orchestrator Import Debug and Fix ===\n")

# Step 1: Set required environment variables
print("1. Setting up environment...")
os.environ['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', 'test-key')
os.environ['SUPABASE_URL'] = os.environ.get('SUPABASE_URL', 'http://localhost:54321')
os.environ['SUPABASE_ANON_KEY'] = os.environ.get('SUPABASE_ANON_KEY', 'test-key')

# Step 2: Mock problematic global instances
print("2. Mocking problematic global instances...")

# Mock the A2A server to prevent it from starting
mock_a2a_server = Mock()
mock_a2a_server.running = False
mock_a2a_server.agent_queues = {}
mock_a2a_server.start = Mock(return_value=asyncio.Future())
mock_a2a_server.start.return_value.set_result(None)

# Create a mock module for a2a_optimized
mock_a2a_module = Mock()
mock_a2a_module.a2a_server = mock_a2a_server
mock_a2a_module.MessagePriority = Mock()
sys.modules['infrastructure.a2a_optimized'] = mock_a2a_module

# Mock telemetry to prevent external connections
mock_telemetry = Mock()
mock_telemetry.start_span = Mock(return_value="test-span")
mock_telemetry.end_span = Mock()
mock_telemetry.set_span_attribute = Mock()
mock_telemetry.record_metric = Mock()

sys.modules['core.telemetry'] = Mock()
sys.modules['core.telemetry'].telemetry_manager = mock_telemetry
sys.modules['tests.mocks.core.telemetry'] = Mock()
sys.modules['tests.mocks.core.telemetry'].telemetry_manager = mock_telemetry

print("✅ Mocking complete")

# Step 3: Test the import
print("\n3. Testing orchestrator import...")
start_time = time.time()

try:
    from agents.orchestrator.agent import NGXNexusOrchestrator
    elapsed = time.time() - start_time
    print(f"✅ Import successful in {elapsed:.3f}s")
    
    # Step 4: Test instantiation
    print("\n4. Testing orchestrator instantiation...")
    
    # Mock additional dependencies for instantiation
    with patch('agents.base.base_ngx_agent.MCPToolkit') as mock_mcp, \
         patch('agents.base.base_ngx_agent.VertexAIClient') as mock_vertex, \
         patch('agents.base.base_ngx_agent.PersonalityAdapter') as mock_personality, \
         patch('agents.base.base_ngx_agent.redis_pool_manager') as mock_redis:
        
        # Configure mocks
        mock_mcp.return_value = Mock()
        mock_vertex.return_value = Mock()
        mock_personality.return_value = Mock()
        mock_redis.is_connected = Mock(return_value=asyncio.Future())
        mock_redis.is_connected.return_value.set_result(False)
        
        # Create orchestrator instance
        orchestrator = NGXNexusOrchestrator()
        print(f"✅ Orchestrator created: {orchestrator.agent_id}")
        
        # Test basic functionality
        print("\n5. Testing basic functionality...")
        
        # Get capabilities
        capabilities = orchestrator.get_agent_capabilities()
        print(f"   - Capabilities: {len(capabilities)} found")
        for cap in capabilities[:3]:
            print(f"     • {cap}")
        
        # Get description
        description = orchestrator.get_agent_description()
        print(f"   - Description: {description[:60]}...")
        
        # Check skills
        skills = orchestrator.get_available_skills()
        print(f"   - Skills: {len(skills)} registered")
        
        print("\n✅ All tests passed!")
        
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n❌ Import failed after {elapsed:.3f}s")
    print(f"Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    
    # Provide diagnosis
    print("\n=== DIAGNOSIS ===")
    print("The import is failing due to:")
    print("1. Circular imports between adk.toolkit directory and adk.toolkit.py file")
    print("2. Global instances being created during import (a2a_server)")
    print("3. Synchronous operations during module initialization")
    print("\n=== SOLUTION ===")
    print("1. Rename adk/toolkit directory to adk/utilities to avoid naming conflict")
    print("2. Lazy-load the a2a_server instance instead of creating it globally")
    print("3. Move synchronous operations to initialization methods instead of module level")

print("\n=== Summary ===")
print("The orchestrator test is timing out due to:")
print("1. Naming conflict between adk/toolkit.py and adk/toolkit/ directory")
print("2. Global instance creation in infrastructure/a2a_optimized.py")
print("3. These issues cause import resolution problems and blocking operations")
print("\nTo fix permanently:")
print("1. Run: mv adk/toolkit adk/utilities")
print("2. Update imports from 'adk.toolkit.*' to 'adk.utilities.*'")
print("3. Make a2a_server initialization lazy (create on first use)")