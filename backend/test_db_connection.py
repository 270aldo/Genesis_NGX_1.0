#!/usr/bin/env python3
"""Test database connection to Supabase - Enhanced version"""

import asyncio
import asyncpg
import os
import urllib.parse
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

async def test_url(url_name: str, database_url: str) -> bool:
    """Test a specific database URL"""
    if not database_url:
        print(f"  ❌ {url_name}: Not configured")
        return False
    
    # Parse URL to hide password
    parsed = urllib.parse.urlparse(database_url)
    safe_url = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}:{parsed.port}{parsed.path}"
    print(f"\n📡 Testing {url_name}:")
    print(f"   URL: {safe_url}")
    
    try:
        # Try to connect with a timeout
        conn = await asyncio.wait_for(
            asyncpg.connect(database_url),
            timeout=10.0
        )
        
        # Run a simple query
        version = await conn.fetchval("SELECT version()")
        print(f"   ✅ Connection successful!")
        print(f"   PostgreSQL: {version.split(',')[0]}")
        
        # Check if any tables exist
        table_count = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        print(f"   Tables: {table_count}")
        
        # List some tables if they exist
        if table_count > 0:
            tables = await conn.fetch("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                LIMIT 5
            """)
            print(f"   Sample tables: {', '.join([t['table_name'] for t in tables])}")
        
        await conn.close()
        return True
        
    except asyncio.TimeoutError:
        print(f"   ❌ Connection timeout (10s)")
        return False
    except asyncpg.InvalidPasswordError:
        print(f"   ❌ Invalid password")
        return False
    except asyncpg.InvalidCatalogNameError:
        print(f"   ❌ Database does not exist")
        return False
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {e}")
        return False

async def test_all_connections():
    """Test all configured database connections"""
    print("🔍 SUPABASE CONNECTION DIAGNOSTIC")
    print("=" * 50)
    
    # Test environment setup
    print("\n📋 Environment Check:")
    print(f"   .env file: {'✅ Found' if env_path.exists() else '❌ Not found'}")
    print(f"   SUPABASE_URL: {'✅ Set' if os.getenv('SUPABASE_URL') else '❌ Not set'}")
    print(f"   SUPABASE_ANON_KEY: {'✅ Set' if os.getenv('SUPABASE_ANON_KEY') else '❌ Not set'}")
    
    # Get all database URLs
    urls_to_test = {
        "Direct Connection": os.getenv('SUPABASE_DB_URL'),
        "Pooler Transaction Mode": os.getenv('DATABASE_URL'),
        "Pooler Session Mode": os.getenv('DATABASE_URL_SESSION'),
    }
    
    # Test each URL
    results = {}
    for name, url in urls_to_test.items():
        results[name] = await test_url(name, url)
    
    # Summary
    print("\n📊 SUMMARY:")
    print("=" * 50)
    successful = sum(1 for v in results.values() if v)
    print(f"Successful connections: {successful}/{len(results)}")
    
    if successful > 0:
        print("\n✅ At least one connection method works!")
        working = [k for k, v in results.items() if v]
        print(f"   Working: {', '.join(working)}")
        return True
    else:
        print("\n❌ No connections successful")
        print("\n🔧 TROUBLESHOOTING TIPS:")
        print("1. Check your Supabase dashboard for the correct connection string")
        print("2. Verify the password is correct (current: 270Aldo!ALAN)")
        print("3. Ensure your IP is allowed in Supabase (check Database Settings)")
        print("4. Try different regions (us-east-1, us-west-1, etc.)")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_all_connections())
    exit(0 if success else 1)