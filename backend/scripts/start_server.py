#!/usr/bin/env python3
"""
Start the GENESIS server with security configuration.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Import and run
    import uvicorn
    from app.main import app
    
    print("🚀 Starting GENESIS Server with Security Configuration...")
    print(f"📌 Environment: {os.getenv('ENV', 'development')}")
    print(f"🔒 JWT Secret: {'✅ Set' if os.getenv('JWT_SECRET') else '❌ Not set'}")
    print(f"🚦 Rate Limiting: {os.getenv('ENABLE_RATE_LIMITING', 'False')}")
    print(f"🛡️ Security Headers: {os.getenv('ENABLE_SECURITY_HEADERS', 'False')}")
    print(f"📝 Audit Trail: {os.getenv('ENABLE_AUDIT_TRAIL', 'False')}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )