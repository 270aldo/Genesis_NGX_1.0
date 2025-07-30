#!/usr/bin/env python3
"""
Debug import issues step by step.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=== Debug Import Process ===")
print(f"Python: {sys.executable}")
print(f"Path: {project_root}")

try:
    print("\n1. Testing basic imports...")
    import os
    print("✓ os")
    
    from core.settings_lazy import settings
    print("✓ core.settings")
    
    print("\n2. Testing telemetry import...")
    from core.telemetry import get_tracer
    print("✓ core.telemetry")
    
    print("\n3. Testing agent base imports...")
    from agents.base.base_agent import BaseAgent
    print("✓ agents.base.base_agent")
    
    print("\n4. Testing ADK imports...")
    from adk.core.base_agent import BaseADKAgent
    print("✓ adk.core.base_agent")
    
    print("\n5. Testing NGX agent imports...")
    from agents.base.base_ngx_agent import BaseNGXAgent
    print("✓ agents.base.base_ngx_agent")
    
    print("\n6. Testing orchestrator import...")
    print("   This might take a while if it's initializing connections...")
    from agents.orchestrator.agent import NGXNexusOrchestrator
    print("✓ agents.orchestrator.agent")
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    
    # Try to identify the specific module causing issues
    print("\n--- Checking module initialization ---")
    if 'telemetry' in str(e):
        print("Issue seems to be in telemetry module")
        print("Checking OpenTelemetry installation...")
        try:
            import opentelemetry
            print(f"OpenTelemetry version: {opentelemetry.__version__}")
        except:
            print("OpenTelemetry not properly installed")