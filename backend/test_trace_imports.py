#!/usr/bin/env python3
"""
Trace imports to find where the blocking occurs.
"""

import sys
import time
import importlib.util

# Store original import
original_import = __builtins__.__import__

# Track import times
import_times = {}
import_stack = []

def traced_import(name, *args, **kwargs):
    """Traced import function."""
    # Track nested imports
    indent = "  " * len(import_stack)
    
    # Skip already imported modules
    if name in sys.modules:
        return original_import(name, *args, **kwargs)
    
    print(f"{indent}→ Importing: {name}", flush=True)
    start_time = time.time()
    import_stack.append(name)
    
    try:
        module = original_import(name, *args, **kwargs)
        elapsed = time.time() - start_time
        import_times[name] = elapsed
        
        if elapsed > 0.5:  # Flag slow imports
            print(f"{indent}⚠️  SLOW: {name} took {elapsed:.3f}s", flush=True)
        
        return module
    finally:
        import_stack.pop()

# Install the traced import
__builtins__.__import__ = traced_import

print("Starting traced import of NGXNexusOrchestrator...")
print("=" * 60)

try:
    start_time = time.time()
    from agents.orchestrator.agent import NGXNexusOrchestrator
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"✅ Import successful in {total_time:.3f}s")
    
    # Show slowest imports
    print("\nSlowest imports:")
    sorted_imports = sorted(import_times.items(), key=lambda x: x[1], reverse=True)
    for module, elapsed in sorted_imports[:10]:
        if elapsed > 0.1:
            print(f"  {module}: {elapsed:.3f}s")
            
except Exception as e:
    print(f"\n❌ Import failed: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    # Restore original import
    __builtins__.__import__ = original_import