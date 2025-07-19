#!/usr/bin/env python3
"""
Validate Supabase Setup
=======================
Script para validar que la configuración de Supabase esté completa y funcional.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import asyncpg

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment
env_path = project_root / '.env'
load_dotenv(env_path)

async def validate_database_schema():
    """Validate that all required tables exist"""
    print("\n=== Validating Database Schema ===")
    
    required_tables = [
        'users', 'user_profiles', 'user_preferences', 'agents', 'chat_sessions',
        'chat_messages', 'weight_logs', 'body_composition_logs', 'performance_logs',
        'nutrition_logs', 'meal_plans', 'training_plans', 'feedback', 'biomarker_records',
        'user_device_connections', 'daily_summaries', 'migration_log', 'tasks',
        'agent_partnerships', 'collaboration_requests', 'conversation_memory',
        'personality_profiles', 'user_sessions', 'query_performance_metrics',
        'insight_fusion_results', 'async_task_queue'
    ]
    
    # Try different connection strings
    connection_strings = [
        os.getenv('SUPABASE_DB_URL'),
        os.getenv('DATABASE_URL'),
        os.getenv('DATABASE_URL_SESSION')
    ]
    
    conn = None
    for conn_str in connection_strings:
        if not conn_str:
            continue
        try:
            conn = await asyncpg.connect(conn_str)
            break
        except Exception:
            continue
    
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        # Get existing tables
        existing_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        
        existing_table_names = {row['table_name'] for row in existing_tables}
        
        print(f"Found {len(existing_table_names)} tables in database")
        
        missing_tables = []
        for table in required_tables:
            if table in existing_table_names:
                print(f"✅ {table}")
            else:
                print(f"❌ {table} - MISSING")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n⚠️ Missing {len(missing_tables)} required tables")
            return False
        else:
            print(f"\n✅ All {len(required_tables)} required tables exist")
            return True
            
    finally:
        await conn.close()

def validate_supabase_client():
    """Validate Supabase client connection and basic operations"""
    print("\n=== Validating Supabase Client ===")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_ANON_KEY not found in .env")
        return False
    
    try:
        client = create_client(url, key)
        print("✅ Supabase client created successfully")
        
        # Test reading agents table (should work with RLS)
        try:
            response = client.table('agents').select("*").limit(1).execute()
            print("✅ Successfully queried agents table")
            if response.data:
                print(f"✅ Found {len(response.data)} agent(s) in database")
            else:
                print("⚠️ No agents found - you may need to run migrations")
        except Exception as e:
            print(f"❌ Could not query agents table: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return False

async def validate_rls_policies():
    """Validate that RLS policies are properly configured"""
    print("\n=== Validating RLS Policies ===")
    
    connection_strings = [
        os.getenv('SUPABASE_DB_URL'),
        os.getenv('DATABASE_URL'),
        os.getenv('DATABASE_URL_SESSION')
    ]
    
    conn = None
    for conn_str in connection_strings:
        if not conn_str:
            continue
        try:
            conn = await asyncpg.connect(conn_str)
            break
        except Exception:
            continue
    
    if not conn:
        print("❌ No se pudo conectar a la base de datos para validar RLS")
        return False
    
    try:
        # Check which tables have RLS enabled
        rls_tables = await conn.fetch("""
            SELECT schemaname, tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND rowsecurity = true
        """)
        
        print(f"Found {len(rls_tables)} tables with RLS enabled:")
        for table in rls_tables:
            print(f"✅ {table['tablename']}")
        
        # Check policies
        policies = await conn.fetch("""
            SELECT schemaname, tablename, policyname 
            FROM pg_policies 
            WHERE schemaname = 'public'
        """)
        
        print(f"\nFound {len(policies)} RLS policies:")
        for policy in policies:
            print(f"✅ {policy['tablename']}: {policy['policyname']}")
        
        if len(rls_tables) >= 10 and len(policies) >= 10:
            print("\n✅ RLS configuration looks good")
            return True
        else:
            print(f"\n⚠️ Expected more RLS tables/policies. Found {len(rls_tables)} tables, {len(policies)} policies")
            return False
            
    finally:
        await conn.close()

async def validate_agents_data():
    """Validate that agents seed data was inserted"""
    print("\n=== Validating Agents Seed Data ===")
    
    expected_agents = [
        'nexus_central_command', 'blaze_elite_performance', 'sage_nutritional_wisdom',
        'code_genetic_optimization', 'wave_quantum_analytics', 'luna_female_specialist',
        'stella_progress_tracker', 'spark_motivation_coach', 'nova_biohacking_expert',
        'guardian_security', 'node_integration'
    ]
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    try:
        client = create_client(url, key)
        response = client.table('agents').select("agent_id, name, status").execute()
        
        if response.data:
            existing_agents = {agent['agent_id'] for agent in response.data}
            print(f"Found {len(response.data)} agents in database:")
            
            for agent in response.data:
                print(f"✅ {agent['agent_id']} ({agent['name']}) - {agent['status']}")
            
            missing_agents = set(expected_agents) - existing_agents
            if missing_agents:
                print(f"\n⚠️ Missing agents: {', '.join(missing_agents)}")
                return False
            else:
                print(f"\n✅ All {len(expected_agents)} expected agents are present")
                return True
        else:
            print("❌ No agents found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error validating agents: {e}")
        return False

async def main():
    """Main validation function"""
    print("GENESIS - Supabase Setup Validation")
    print("=" * 50)
    
    # Run all validations
    validations = [
        ("Database Schema", await validate_database_schema()),
        ("Supabase Client", validate_supabase_client()),
        ("RLS Policies", await validate_rls_policies()),
        ("Agents Seed Data", await validate_agents_data())
    ]
    
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, passed in validations:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:<20} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED! Supabase is 100% ready for production!")
    else:
        print("⚠️ Some validations failed. Please check the issues above.")
        print("\nNext steps:")
        print("1. Run migrations if schema/data is missing")
        print("2. Check RLS policies if access issues persist")
        print("3. Verify network connectivity for connection issues")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())