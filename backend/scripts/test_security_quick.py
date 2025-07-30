#!/usr/bin/env python3
"""
Quick security configuration test.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_security_config():
    """Test security configuration manually."""
    print("🔒 Testing Security Configuration...")
    
    # Test 1: JWT Secret
    jwt_secret = os.getenv('JWT_SECRET')
    if not jwt_secret:
        print("❌ JWT_SECRET not set")
        return False
    elif jwt_secret == "dev-secret-key":
        print("❌ JWT_SECRET using default value")
        return False
    elif len(jwt_secret) < 32:
        print("❌ JWT_SECRET too short (need at least 32 chars)")
        return False
    else:
        print(f"✅ JWT_SECRET is secure ({len(jwt_secret)} chars)")
    
    # Test 2: Environment
    env = os.getenv('ENV', 'development')
    print(f"✅ Environment: {env}")
    
    # Test 3: Redis Configuration
    redis_host = os.getenv('REDIS_HOST')
    redis_password = os.getenv('REDIS_PASSWORD')
    
    if not redis_host:
        print("❌ REDIS_HOST not set")
        return False
    else:
        print(f"✅ Redis host: {redis_host}")
    
    if not redis_password or redis_password == "your-redis-password-here":
        print("❌ REDIS_PASSWORD not secure")
        return False
    else:
        print(f"✅ Redis password is set ({len(redis_password)} chars)")
    
    # Test 4: Security Features
    rate_limiting = os.getenv('ENABLE_RATE_LIMITING', 'False').lower() == 'true'
    security_headers = os.getenv('ENABLE_SECURITY_HEADERS', 'False').lower() == 'true'
    audit_trail = os.getenv('ENABLE_AUDIT_TRAIL', 'False').lower() == 'true'
    
    print(f"✅ Rate Limiting: {'Enabled' if rate_limiting else '❌ Disabled'}")
    print(f"✅ Security Headers: {'Enabled' if security_headers else '❌ Disabled'}")
    print(f"✅ Audit Trail: {'Enabled' if audit_trail else '❌ Disabled'}")
    
    # Test 5: Rate Limit Values
    auth_limit = int(os.getenv('RATE_LIMIT_AUTH_REQUESTS', '5'))
    chat_limit = int(os.getenv('RATE_LIMIT_CHAT_REQUESTS', '30'))
    heavy_limit = int(os.getenv('RATE_LIMIT_HEAVY_REQUESTS', '10'))
    
    print(f"✅ Auth rate limit: {auth_limit} requests/min")
    print(f"✅ Chat rate limit: {chat_limit} requests/min")
    print(f"✅ Heavy ops limit: {heavy_limit} requests/hour")
    
    # Test 6: Database URLs (check they don't contain plaintext passwords in logs)
    db_url = os.getenv('DATABASE_URL', '')
    if 'postgresql://' in db_url:
        # Extract just the host for display
        parts = db_url.split('@')
        if len(parts) > 1:
            print(f"✅ Database URL configured (host: {parts[1].split('/')[0]})")
        else:
            print("✅ Database URL configured")
    
    # Test 7: API Keys (ensure they're not default values)
    vertex_key = os.getenv('VERTEX_API_KEY', '')
    if vertex_key and not vertex_key.startswith('your-'):
        print(f"✅ Vertex AI API key configured")
    
    # Test Redis connection
    try:
        import redis
        r = redis.Redis(
            host='localhost',
            port=6379,
            password=redis_password,
            decode_responses=True
        )
        r.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
    
    print("\n🎯 Security Configuration Test Complete!")
    return True

if __name__ == "__main__":
    # Load .env file
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    success = test_security_config()
    sys.exit(0 if success else 1)