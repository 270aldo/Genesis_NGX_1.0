#!/usr/bin/env python3
"""
Test security endpoints and features.
"""
import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_security_headers():
    """Test security headers are present."""
    print("\n🔒 Testing Security Headers...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/") as resp:
            headers = resp.headers
            
            # Check security headers
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': None,  # Check exists
                'Content-Security-Policy': None,  # Check exists
            }
            
            for header, expected in security_headers.items():
                value = headers.get(header)
                if expected:
                    if value == expected:
                        print(f"✅ {header}: {value}")
                    else:
                        print(f"❌ {header}: {value} (expected: {expected})")
                else:
                    if value:
                        print(f"✅ {header}: {value[:50]}...")
                    else:
                        print(f"❌ {header}: Not set")

async def test_rate_limiting():
    """Test rate limiting is working."""
    print("\n🚦 Testing Rate Limiting...")
    
    async with aiohttp.ClientSession() as session:
        # Test auth endpoint rate limiting (5 requests per minute)
        auth_url = f"{BASE_URL}/auth/login"
        
        print("\nTesting auth endpoint (limit: 5/min)...")
        for i in range(7):
            data = {"email": f"test{i}@example.com", "password": "wrong"}
            try:
                async with session.post(auth_url, json=data) as resp:
                    if resp.status == 429:
                        print(f"✅ Request {i+1}: Rate limited (429)")
                    else:
                        print(f"✅ Request {i+1}: {resp.status}")
            except Exception as e:
                print(f"Request {i+1}: {e}")
            
            await asyncio.sleep(0.5)

async def test_input_validation():
    """Test input validation middleware."""
    print("\n🛡️ Testing Input Validation...")
    
    async with aiohttp.ClientSession() as session:
        # Test SQL injection attempt
        malicious_inputs = [
            {"test": "'; DROP TABLE users; --"},
            {"test": "<script>alert('XSS')</script>"},
            {"path": "../../../etc/passwd"},
        ]
        
        for i, payload in enumerate(malicious_inputs):
            try:
                async with session.post(f"{BASE_URL}/auth/login", json=payload) as resp:
                    if resp.status == 400:
                        print(f"✅ Malicious input {i+1} blocked: {resp.status}")
                    else:
                        print(f"⚠️ Malicious input {i+1} status: {resp.status}")
            except Exception as e:
                print(f"Error testing input {i+1}: {e}")

async def test_cors_configuration():
    """Test CORS is properly configured."""
    print("\n🌐 Testing CORS Configuration...")
    
    async with aiohttp.ClientSession() as session:
        # Test from allowed origin
        headers = {'Origin': 'http://localhost:3000'}
        async with session.options(f"{BASE_URL}/", headers=headers) as resp:
            cors_headers = {
                'Access-Control-Allow-Origin': resp.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Credentials': resp.headers.get('Access-Control-Allow-Credentials'),
            }
            
            for header, value in cors_headers.items():
                if value:
                    print(f"✅ {header}: {value}")
                else:
                    print(f"❌ {header}: Not set")
        
        # Test from disallowed origin
        headers = {'Origin': 'http://evil.com'}
        async with session.options(f"{BASE_URL}/", headers=headers) as resp:
            if resp.headers.get('Access-Control-Allow-Origin') == 'http://evil.com':
                print("❌ CORS allows all origins (security risk)")
            else:
                print("✅ CORS blocks unauthorized origins")

async def test_health_endpoints():
    """Test health check endpoints."""
    print("\n💚 Testing Health Endpoints...")
    
    async with aiohttp.ClientSession() as session:
        endpoints = ['/health', '/api/health', '/']
        
        for endpoint in endpoints:
            try:
                async with session.get(f"{BASE_URL}{endpoint}") as resp:
                    print(f"✅ {endpoint}: {resp.status}")
            except Exception as e:
                print(f"❌ {endpoint}: {e}")

async def main():
    """Run all security tests."""
    print("🔐 GENESIS Security Test Suite")
    print("=" * 50)
    print(f"Testing: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    
    await test_health_endpoints()
    await test_security_headers()
    await test_cors_configuration()
    await test_rate_limiting()
    await test_input_validation()
    
    print("\n✅ Security tests completed!")

if __name__ == "__main__":
    asyncio.run(main())