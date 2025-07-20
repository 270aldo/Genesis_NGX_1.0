#!/usr/bin/env python3
"""
Test script for MCP adapters
Run this to verify all adapters are working correctly
"""

import asyncio
import json
from datetime import datetime

from mcp.adapters import (
    NexusCoreAdapter,
    NexusCRMAdapter,
    NGXPulseAdapter,
    NGXAgentsBlogAdapter,
    NexusConversationsAdapter
)


async def test_nexus_core():
    """Test Nexus Core adapter"""
    print("\n=== Testing Nexus Core Adapter ===")
    adapter = NexusCoreAdapter()
    await adapter.initialize()
    
    # Test get client analytics
    result = await adapter.execute_tool(
        "nexus_core.get_client_analytics",
        {"metric": "revenue", "period": "last_30_days"}
    )
    print(f"Client Analytics: {json.dumps(result, indent=2)}")
    
    # Test dashboard summary
    result = await adapter.execute_tool(
        "nexus_core.get_dashboard_summary",
        {"include_ai_usage": True}
    )
    print(f"Dashboard Summary: {json.dumps(result, indent=2)}")
    
    await adapter.close()


async def test_nexus_crm():
    """Test Nexus CRM adapter"""
    print("\n=== Testing Nexus CRM Adapter ===")
    adapter = NexusCRMAdapter()
    await adapter.initialize()
    
    # Test contact management
    result = await adapter.execute_tool(
        "nexus_crm.manage_contacts",
        {"action": "list", "filters": {"limit": 3}}
    )
    print(f"Contacts: {json.dumps(result, indent=2)}")
    
    # Test analytics
    result = await adapter.execute_tool(
        "nexus_crm.get_analytics",
        {"metric": "pipeline", "period": "month"}
    )
    print(f"CRM Analytics: {json.dumps(result, indent=2)}")
    
    await adapter.close()


async def test_ngx_pulse():
    """Test NGX Pulse adapter"""
    print("\n=== Testing NGX Pulse Adapter ===")
    adapter = NGXPulseAdapter()
    await adapter.initialize()
    
    # Test biometrics
    result = await adapter.execute_tool(
        "ngx_pulse.read_biometrics",
        {"user_id": "current", "metric": "hrv"}
    )
    print(f"Biometrics: {json.dumps(result, indent=2)}")
    
    # Test trends
    result = await adapter.execute_tool(
        "ngx_pulse.analyze_trends",
        {"user_id": "current", "metrics": ["fitness_level"], "period": "month"}
    )
    print(f"Health Trends: {json.dumps(result, indent=2)}")
    
    await adapter.close()


async def test_ngx_blog():
    """Test NGX Agents Blog adapter"""
    print("\n=== Testing NGX Agents Blog Adapter ===")
    adapter = NGXAgentsBlogAdapter()
    await adapter.initialize()
    
    # Test content generation
    result = await adapter.execute_tool(
        "ngx_blog.generate_content",
        {
            "topic": "HIIT Training",
            "keywords": ["high intensity", "fat loss"],
            "tone": "educational",
            "length": "short"
        }
    )
    print(f"Generated Content: {json.dumps(result, indent=2)}")
    
    # Test performance analytics
    result = await adapter.execute_tool(
        "ngx_blog.analyze_performance",
        {"metric": "engagement", "period": "week"}
    )
    print(f"Blog Performance: {json.dumps(result, indent=2)}")
    
    await adapter.close()


async def test_nexus_conversations():
    """Test Nexus Conversations adapter"""
    print("\n=== Testing Nexus Conversations Adapter ===")
    adapter = NexusConversationsAdapter()
    await adapter.initialize()
    
    # Test conversation management
    result = await adapter.execute_tool(
        "nexus_conversations.manage_conversation",
        {
            "action": "start",
            "user_id": "test_user",
            "agent_id": "BLAZE",
            "context": {"topic": "workout_planning"}
        }
    )
    print(f"Conversation Started: {json.dumps(result, indent=2)}")
    
    # Test engagement analysis
    result = await adapter.execute_tool(
        "nexus_conversations.analyze_engagement",
        {
            "analysis_type": "topic_trends",
            "scope": "global",
            "period": "week"
        }
    )
    print(f"Engagement Analysis: {json.dumps(result, indent=2)}")
    
    await adapter.close()


async def main():
    """Run all adapter tests"""
    print(f"Starting MCP Adapter Tests - {datetime.now()}")
    
    try:
        await test_nexus_core()
        await test_nexus_crm()
        await test_ngx_pulse()
        await test_ngx_blog()
        await test_nexus_conversations()
        
        print("\n✅ All adapter tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())