#!/usr/bin/env python3
"""
Quick Health Check for NGX Agents
A simpler version that handles configuration errors gracefully
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_agents():
    """Check agent files exist"""
    print("\n🤖 Checking Agents...")
    agents_dir = Path("agents")

    required_agents = [
        "orchestrator",
        "elite_training_strategist",
        "precision_nutrition_architect",
        "biometrics_insight_engine",
        "motivation_behavior_coach",
        "progress_tracker",
        "recovery_corrective",
        "security_compliance_guardian",
        "systems_integration_ops",
        "biohacking_innovator",
        "client_success_liaison",
    ]

    found = 0
    for agent in required_agents:
        agent_file = agents_dir / agent / "agent.py"
        if agent_file.exists():
            print(f"  ✅ {agent}")
            found += 1
        else:
            print(f"  ❌ {agent} - NOT FOUND")

    print(f"\n  Summary: {found}/{len(required_agents)} agents found")
    return found == len(required_agents)


def check_integrations():
    """Check integration files exist"""
    print("\n📡 Checking Integrations...")
    integrations_dir = Path("integrations")

    integrations = {
        "wearables": ["whoop.py", "apple_health.py", "oura.py", "garmin.py"],
        "nutrition": ["myfitnesspal_adapter.py"],
        "notifications": ["firebase_service.py", "scheduler.py"],
        "whatsapp": ["whatsapp_service.py", "webhook_handler.py", "whatsapp_agent.py"],
    }

    all_good = True
    for category, files in integrations.items():
        print(f"\n  {category.capitalize()}:")
        category_dir = integrations_dir / category

        if category == "wearables":
            category_dir = category_dir / "adapters"

        for file in files:
            file_path = category_dir / file
            if file_path.exists():
                print(f"    ✅ {file}")
            else:
                print(f"    ❌ {file} - NOT FOUND")
                all_good = False

    return all_good


def check_infrastructure():
    """Check critical infrastructure files"""
    print("\n🏗️ Checking Infrastructure...")

    critical_files = [
        "infrastructure/a2a_optimized.py",
        "infrastructure/adapters/orchestrator_adapter.py",
        "core/state_manager_optimized.py",
        "core/intent_analyzer_optimized.py",
        "clients/vertex_ai/client.py",
        "clients/supabase_client.py",
        "app/main.py",
    ]

    found = 0
    for file in critical_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
            found += 1
        else:
            print(f"  ❌ {file} - NOT FOUND")

    print(f"\n  Summary: {found}/{len(critical_files)} infrastructure files found")
    return found == len(critical_files)


def check_routers():
    """Check API routers exist"""
    print("\n🌐 Checking API Routers...")
    routers_dir = Path("app/routers")

    required_routers = [
        "auth.py",
        "agents.py",
        "chat.py",
        "stream.py",
        "feedback.py",
        "wearables.py",
        "notifications.py",
        "whatsapp.py",
        "visualization.py",
        "audio.py",
    ]

    found = 0
    for router in required_routers:
        if (routers_dir / router).exists():
            print(f"  ✅ {router}")
            found += 1
        else:
            print(f"  ❌ {router} - NOT FOUND")

    print(f"\n  Summary: {found}/{len(required_routers)} routers found")
    return found == len(required_routers)


def check_tests():
    """Check test files exist"""
    print("\n🧪 Checking Tests...")
    tests_dir = Path("tests")

    test_categories = {
        "unit": ["test_intent_analyzer.py", "test_state_manager.py"],
        "integration/wearables": [
            "test_whoop_integration.py",
            "test_oura_integration.py",
            "test_garmin_integration.py",
        ],
        "integration/whatsapp": ["test_whatsapp_integration.py"],
        "integration/notifications": ["test_notifications.py"],
    }

    total_found = 0
    total_expected = 0

    for category, files in test_categories.items():
        print(f"\n  {category}:")
        category_dir = tests_dir / category

        for file in files:
            total_expected += 1
            if (category_dir / file).exists():
                print(f"    ✅ {file}")
                total_found += 1
            else:
                print(f"    ⚠️ {file} - Not found")

    print(f"\n  Summary: {total_found}/{total_expected} test files found")
    return total_found > 0


def check_environment():
    """Check for .env file"""
    print("\n⚙️ Checking Environment...")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("  ✅ .env file exists")
        # Try to read and check for critical vars
        try:
            with open(env_file) as f:
                content = f.read()
                critical_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "GEMINI_API_KEY"]

                print("\n  Checking critical variables:")
                for var in critical_vars:
                    if f"{var}=" in content:
                        print(f"    ✅ {var} is set")
                    else:
                        print(f"    ⚠️ {var} not found")
        except Exception:
            print("  ⚠️ Could not read .env file")
    else:
        print("  ❌ .env file NOT FOUND")
        if env_example.exists():
            print("  💡 .env.example exists - copy it to .env and configure")

    return env_file.exists()


def main():
    """Run all checks"""
    print("🏥 NGX Agents Quick Health Check")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working directory: {os.getcwd()}")

    # Run all checks
    results = {
        "Agents": check_agents(),
        "Integrations": check_integrations(),
        "Infrastructure": check_infrastructure(),
        "Routers": check_routers(),
        "Tests": check_tests(),
        "Environment": check_environment(),
    }

    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for component, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {component}: {'PASS' if status else 'FAIL'}")

    # Overall score
    score = (passed / total) * 100
    print(f"\n🏥 Overall Health Score: {score:.0f}%")

    # Recommendations
    print("\n💡 Recommendations:")
    if score >= 80:
        print("  ✅ System is ready for frontend development!")
        print("  - Most components are in place")
        print("  - Address any missing tests or documentation as needed")
    elif score >= 60:
        print("  ⚠️ System is mostly ready but needs attention:")
        print("  - Fix any missing critical components")
        print("  - Ensure environment is properly configured")
    else:
        print("  ❌ System needs significant work:")
        print("  - Multiple critical components are missing")
        print("  - Review installation and setup procedures")

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create a simple report file
    with open("quick_health_report.txt", "w") as f:
        f.write(f"NGX Agents Health Check Report\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Score: {score:.0f}%\n\n")
        for component, status in results.items():
            f.write(f"{component}: {'PASS' if status else 'FAIL'}\n")

    print(f"\n📄 Report saved to: quick_health_report.txt")


if __name__ == "__main__":
    main()
