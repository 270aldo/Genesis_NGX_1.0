#!/usr/bin/env python3
"""
Test settings import to see if it's blocking.
"""

import time
import os

# Set minimal environment variables
os.environ['GEMINI_API_KEY'] = 'test-key'

print("Testing settings import...")
start_time = time.time()

try:
    from core.settings_lazy import settings
    elapsed = time.time() - start_time
    print(f"✅ Settings imported in {elapsed:.3f}s")
    print(f"Settings type: {type(settings)}")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"❌ Failed after {elapsed:.3f}s")
    print(f"Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()