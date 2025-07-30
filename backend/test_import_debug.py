#!/usr/bin/env python3
"""
Debug script to isolate import issues with the orchestrator agent.
"""

import sys
import time
import traceback

def test_import(module_path, description):
    """Test importing a module and measure time."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Module: {module_path}")
    print('-'*60)
    
    start_time = time.time()
    try:
        if '.' in module_path:
            # Handle submodule imports
            parts = module_path.split('.')
            module = __import__(module_path, fromlist=[parts[-1]])
        else:
            module = __import__(module_path)
        
        elapsed = time.time() - start_time
        print(f"✓ SUCCESS - Import took {elapsed:.3f} seconds")
        
        # Print any global instances created
        if hasattr(module, '__dict__'):
            globals_created = []
            for name, value in module.__dict__.items():
                if not name.startswith('_') and not callable(value) and not isinstance(value, type):
                    globals_created.append(f"  - {name}: {type(value).__name__}")
            
            if globals_created:
                print("\nGlobal instances created:")
                for item in globals_created[:10]:  # Limit output
                    print(item)
                if len(globals_created) > 10:
                    print(f"  ... and {len(globals_created) - 10} more")
                    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ FAILED - After {elapsed:.3f} seconds")
        print(f"Error: {type(e).__name__}: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        
    return elapsed

def main():
    """Run import tests in isolation."""
    print("Import Debug Script")
    print("==================")
    print(f"Python: {sys.version}")
    print(f"Path: {sys.executable}")
    
    # Test imports in order of dependency
    tests = [
        ("core.settings", "Core settings module"),
        ("core.logging_config", "Logging configuration"),
        ("core.telemetry", "Telemetry module"),
        ("infrastructure.a2a_optimized", "A2A optimized server"),
        ("infrastructure.adapters.a2a_adapter", "A2A adapter"),
        ("agents.base.adk_agent", "ADK Agent base class"),
        ("agents.base.base_ngx_agent", "Base NGX Agent class"),
        ("agents.orchestrator.config", "Orchestrator config"),
        ("agents.orchestrator.skills", "Orchestrator skills"),
        ("agents.orchestrator.agent", "Orchestrator agent (full import)"),
    ]
    
    total_time = 0
    failed = []
    
    for module_path, description in tests:
        elapsed = test_import(module_path, description)
        total_time += elapsed
        
        if elapsed > 1.0:
            print(f"\n⚠️  WARNING: This import took {elapsed:.3f} seconds!")
            
    print(f"\n{'='*60}")
    print(f"Total import time: {total_time:.3f} seconds")
    
    # Try direct import to reproduce the exact issue
    print(f"\n{'='*60}")
    print("Attempting direct import as in test:")
    print("from agents.orchestrator.agent import NGXNexusOrchestrator")
    print('-'*60)
    
    start_time = time.time()
    try:
        from agents.orchestrator.agent import NGXNexusOrchestrator
        elapsed = time.time() - start_time
        print(f"✓ SUCCESS - Direct import took {elapsed:.3f} seconds")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ FAILED - After {elapsed:.3f} seconds")
        print(f"Error: {type(e).__name__}: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()