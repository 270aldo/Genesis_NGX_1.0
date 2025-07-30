#!/usr/bin/env python3
"""
Test the toolkit import issue.
"""

import sys
print("Python path:", sys.path[:3])

# Try different import approaches
print("\n1. Trying: from adk.toolkit import Toolkit")
try:
    from adk.toolkit import Toolkit
    print("   SUCCESS - Toolkit imported")
    print(f"   Toolkit type: {type(Toolkit)}")
    print(f"   Toolkit module: {Toolkit.__module__}")
except ImportError as e:
    print(f"   FAILED: {e}")

print("\n2. Trying: import adk.toolkit")
try:
    import adk.toolkit
    print("   SUCCESS - adk.toolkit imported")
    print(f"   adk.toolkit type: {type(adk.toolkit)}")
    print(f"   adk.toolkit.__file__: {getattr(adk.toolkit, '__file__', 'No __file__ attribute')}")
    print(f"   adk.toolkit dir: {[x for x in dir(adk.toolkit) if not x.startswith('_')][:5]}")
except ImportError as e:
    print(f"   FAILED: {e}")

print("\n3. Trying to import from the file directly")
try:
    # First, let's see what's in adk
    import adk
    print(f"   adk.__file__: {adk.__file__}")
    
    # Now try to access toolkit as a module attribute
    import importlib
    toolkit_module = importlib.import_module('adk.toolkit')
    print(f"   toolkit_module: {toolkit_module}")
    print(f"   Has Toolkit? {'Toolkit' in dir(toolkit_module)}")
    
except Exception as e:
    print(f"   Error: {type(e).__name__}: {e}")

print("\n4. Checking sys.modules")
for key in sys.modules:
    if 'toolkit' in key:
        print(f"   {key}: {sys.modules[key]}")