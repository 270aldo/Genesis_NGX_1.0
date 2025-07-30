#!/usr/bin/env python3
"""
Minimal test for orchestrator that mocks blocking imports.
"""

import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Mock the problematic imports before they're loaded
sys.modules['infrastructure.adapters.a2a_adapter'] = Mock()
sys.modules['infrastructure.adapters.a2a_adapter'].a2a_adapter = Mock()

# Mock the A2A optimized server to prevent blocking
mock_a2a_server = Mock()
mock_a2a_server.start = Mock(return_value=asyncio.Future())
mock_a2a_server.start.return_value.set_result(None)
sys.modules['infrastructure.a2a_optimized'] = Mock()
sys.modules['infrastructure.a2a_optimized'].a2a_server = mock_a2a_server

# Mock telemetry to prevent any external connections
sys.modules['core.telemetry'] = Mock()
sys.modules['core.telemetry'].telemetry_manager = Mock()

# Now we can import the orchestrator
print("Importing orchestrator with mocked dependencies...")
from agents.orchestrator.agent import NGXNexusOrchestrator

class TestOrchestratorImport(unittest.TestCase):
    """Test orchestrator import and basic functionality."""
    
    def test_orchestrator_import(self):
        """Test that orchestrator can be imported."""
        self.assertTrue(NGXNexusOrchestrator is not None)
        print("✅ Orchestrator imported successfully")
    
    def test_orchestrator_instantiation(self):
        """Test that orchestrator can be instantiated."""
        # Mock required dependencies
        with patch('agents.base.base_ngx_agent.MCPToolkit'), \
             patch('agents.base.base_ngx_agent.VertexAIClient'), \
             patch('agents.base.base_ngx_agent.PersonalityAdapter'), \
             patch('agents.base.base_ngx_agent.redis_pool_manager'):
            
            orchestrator = NGXNexusOrchestrator()
            self.assertIsNotNone(orchestrator)
            self.assertEqual(orchestrator.agent_id, "nexus_orchestrator")
            print("✅ Orchestrator instantiated successfully")
    
    def test_orchestrator_capabilities(self):
        """Test orchestrator capabilities."""
        with patch('agents.base.base_ngx_agent.MCPToolkit'), \
             patch('agents.base.base_ngx_agent.VertexAIClient'), \
             patch('agents.base.base_ngx_agent.PersonalityAdapter'), \
             patch('agents.base.base_ngx_agent.redis_pool_manager'):
            
            orchestrator = NGXNexusOrchestrator()
            capabilities = orchestrator.get_agent_capabilities()
            
            self.assertIsInstance(capabilities, list)
            self.assertIn("intent_analysis", capabilities)
            self.assertIn("multi_agent_coordination", capabilities)
            print(f"✅ Orchestrator has {len(capabilities)} capabilities")

if __name__ == "__main__":
    # Run tests
    print("\nRunning orchestrator tests...")
    print("=" * 60)
    unittest.main(verbosity=2)