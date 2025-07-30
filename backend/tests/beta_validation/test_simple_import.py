#!/usr/bin/env python3
"""
Simple test to verify the circular import issues are fixed.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("Testing imports...")

# Test 1: Import settings
try:
    from core.settings_lazy import settings
    print("✅ Successfully imported lazy settings")
except Exception as e:
    print(f"❌ Failed to import lazy settings: {e}")
    sys.exit(1)

# Test 2: Access settings attributes
try:
    host = settings.host
    port = settings.port
    print(f"✅ Successfully accessed settings: host={host}, port={port}")
except Exception as e:
    print(f"❌ Failed to access settings attributes: {e}")
    sys.exit(1)

# Test 3: Import logging config
try:
    from core.logging_config import get_logger
    logger = get_logger(__name__)
    print("✅ Successfully imported logging config")
except Exception as e:
    print(f"❌ Failed to import logging config: {e}")
    sys.exit(1)

# Test 4: Import orchestrator dependencies
try:
    from agents.orchestrator.core.dependencies import NexusDependencies
    print("✅ Successfully imported orchestrator dependencies")
except Exception as e:
    print(f"❌ Failed to import orchestrator dependencies: {e}")
    sys.exit(1)

# Test 5: Import beta validation runner
try:
    from tests.beta_validation.run_beta_validation import BetaValidationRunner
    print("✅ Successfully imported beta validation runner")
except Exception as e:
    print(f"❌ Failed to import beta validation runner: {e}")
    sys.exit(1)

# Test 6: Create a validation runner instance
try:
    runner = BetaValidationRunner()
    print("✅ Successfully created validation runner instance")
except Exception as e:
    print(f"❌ Failed to create validation runner: {e}")
    sys.exit(1)

print("\n🎉 All import tests passed! The circular import issues are fixed.")