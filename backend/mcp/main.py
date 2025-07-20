#!/usr/bin/env python3
"""
MCP Gateway Main Entry Point

Run the GENESIS MCP Gateway server that connects
all NGX ecosystem tools.

Usage:
    python -m mcp.main
    or
    python mcp/main.py
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from mcp.server import gateway
from core.logging_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


def main():
    """Main entry point for MCP Gateway"""
    logger.info("=" * 60)
    logger.info("GENESIS MCP Gateway - NGX Ecosystem Integration")
    logger.info("=" * 60)
    
    # Check environment
    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        logger.warning("GOOGLE_CLOUD_PROJECT not set - some features may not work")
    
    if not os.getenv("SUPABASE_URL"):
        logger.warning("SUPABASE_URL not set - database features disabled")
    
    # Start gateway
    try:
        gateway.run()
    except KeyboardInterrupt:
        logger.info("Shutting down MCP Gateway...")
    except Exception as e:
        logger.error(f"Failed to start MCP Gateway: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()