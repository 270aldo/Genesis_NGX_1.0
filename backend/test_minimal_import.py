#!/usr/bin/env python3
"""
Minimal test to isolate blocking operations during import.
"""

import time
import signal
import sys

def timeout_handler(signum, frame):
    print("\n⏰ TIMEOUT: Import is taking too long (>5 seconds)")
    print("The import is likely blocked on:")
    print("  - Loading environment variables")
    print("  - Connecting to external services")
    print("  - Circular imports")
    print("  - Synchronous I/O operations")
    sys.exit(1)

# Set a 5-second timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)

print("Testing import with 5-second timeout...")
start_time = time.time()

try:
    print("1. Importing NGXNexusOrchestrator...", flush=True)
    from agents.orchestrator.agent import NGXNexusOrchestrator
    
    # Cancel the alarm if import succeeds
    signal.alarm(0)
    
    elapsed = time.time() - start_time
    print(f"✅ SUCCESS: Import completed in {elapsed:.3f} seconds")
    
    # Test instantiation
    print("\n2. Testing instantiation...", flush=True)
    orchestrator = NGXNexusOrchestrator()
    print("✅ SUCCESS: Orchestrator instantiated")
    
except Exception as e:
    signal.alarm(0)  # Cancel the alarm
    elapsed = time.time() - start_time
    print(f"\n❌ FAILED after {elapsed:.3f} seconds")
    print(f"Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()