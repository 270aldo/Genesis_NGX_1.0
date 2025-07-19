#!/usr/bin/env python3
"""
NGX Agents System Health Check

This script verifies that all components of the NGX Agents system are properly configured
and ready for frontend development.
"""

import os
import sys
import importlib
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class SystemHealthChecker:
    """Comprehensive system health checker for NGX Agents"""

    def __init__(self):
        self.results = {
            "agents": {},
            "integrations": {},
            "infrastructure": {},
            "configuration": {},
            "api_endpoints": {},
            "database": {},
            "external_services": {},
        }
        self.errors = []
        self.warnings = []

    async def run_all_checks(self):
        """Run all system health checks"""
        print("🏥 NGX Agents System Health Check")
        print("=" * 50)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 1. Check agents
        await self.check_agents()

        # 2. Check integrations
        await self.check_integrations()

        # 3. Check infrastructure
        await self.check_infrastructure()

        # 4. Check configuration
        await self.check_configuration()

        # 5. Check API endpoints
        await self.check_api_endpoints()

        # 6. Generate report
        self.generate_report()

    async def check_agents(self):
        """Check all agents are properly configured"""
        print("🤖 Checking Agents...")

        agents_to_check = [
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

        for agent_name in agents_to_check:
            try:
                # Try to import agent module
                module = importlib.import_module(f"agents.{agent_name}.agent")

                # Check if agent class exists
                agent_class_name = (
                    "".join(word.capitalize() for word in agent_name.split("_"))
                    + "Agent"
                )
                if hasattr(module, agent_class_name):
                    self.results["agents"][agent_name] = {
                        "status": "✅ OK",
                        "class": agent_class_name,
                        "module": f"agents.{agent_name}.agent",
                    }
                    print(f"  ✅ {agent_name}: Found {agent_class_name}")
                else:
                    self.results["agents"][agent_name] = {
                        "status": "❌ ERROR",
                        "error": f"Class {agent_class_name} not found",
                    }
                    self.errors.append(f"Agent {agent_name}: Class not found")
                    print(f"  ❌ {agent_name}: Class {agent_class_name} not found")

            except ImportError as e:
                self.results["agents"][agent_name] = {
                    "status": "❌ ERROR",
                    "error": str(e),
                }
                self.errors.append(f"Agent {agent_name}: Import error - {str(e)}")
                print(f"  ❌ {agent_name}: Import error - {str(e)}")

        # Check adapters
        print("\n  Checking Agent Adapters...")
        adapters_path = Path("infrastructure/adapters")
        if adapters_path.exists():
            adapter_files = list(adapters_path.glob("*_adapter.py"))
            print(f"  Found {len(adapter_files)} adapter files")
            for adapter_file in adapter_files[:5]:  # Show first 5
                print(f"    • {adapter_file.name}")
            if len(adapter_files) > 5:
                print(f"    ... and {len(adapter_files) - 5} more")
        else:
            self.errors.append("Adapters directory not found")

    async def check_integrations(self):
        """Check all integrations are properly configured"""
        print("\n📡 Checking Integrations...")

        integrations_to_check = {
            "wearables": ["whoop", "apple_health", "oura", "garmin"],
            "nutrition": ["myfitnesspal"],
            "notifications": ["firebase_service", "scheduler"],
            "whatsapp": ["whatsapp_service", "webhook_handler", "whatsapp_agent"],
        }

        for integration_type, modules in integrations_to_check.items():
            print(f"\n  {integration_type.capitalize()}:")
            self.results["integrations"][integration_type] = {}

            for module_name in modules:
                try:
                    if integration_type == "wearables":
                        module_path = f"integrations.wearables.adapters.{module_name}"
                    else:
                        module_path = f"integrations.{integration_type}.{module_name}"

                    module = importlib.import_module(module_path)
                    self.results["integrations"][integration_type][
                        module_name
                    ] = "✅ OK"
                    print(f"    ✅ {module_name}")

                except ImportError as e:
                    self.results["integrations"][integration_type][
                        module_name
                    ] = f"❌ ERROR: {str(e)}"
                    self.warnings.append(
                        f"Integration {integration_type}/{module_name}: {str(e)}"
                    )
                    print(f"    ❌ {module_name}: {str(e)}")

    async def check_infrastructure(self):
        """Check infrastructure components"""
        print("\n🏗️ Checking Infrastructure...")

        critical_files = [
            "infrastructure/a2a_optimized.py",
            "core/state_manager_optimized.py",
            "core/intent_analyzer_optimized.py",
            "clients/vertex_ai/client.py",
            "clients/supabase_client.py",
        ]

        for file_path in critical_files:
            if Path(file_path).exists():
                self.results["infrastructure"][file_path] = "✅ EXISTS"
                print(f"  ✅ {file_path}")
            else:
                self.results["infrastructure"][file_path] = "❌ MISSING"
                self.errors.append(f"Critical file missing: {file_path}")
                print(f"  ❌ {file_path} - MISSING")

    async def check_configuration(self):
        """Check configuration and environment variables"""
        print("\n⚙️ Checking Configuration...")

        try:
            from core.settings import settings

            # Check critical settings
            critical_settings = {
                "Supabase": ["supabase_url", "supabase_anon_key"],
                "WhatsApp": ["whatsapp_phone_number_id", "whatsapp_access_token"],
                "Gemini": ["gemini_api_key"],
                "Server": ["host", "port"],
                "A2A": ["a2a_server_url"],
            }

            for category, configs in critical_settings.items():
                print(f"\n  {category}:")
                for config in configs:
                    value = getattr(settings, config, None)
                    if value:
                        # Hide sensitive values
                        if "key" in config or "token" in config:
                            display_value = (
                                f"{str(value)[:8]}..." if len(str(value)) > 8 else "***"
                            )
                        else:
                            display_value = str(value)
                        print(f"    ✅ {config}: {display_value}")
                        self.results["configuration"][config] = "✅ SET"
                    else:
                        print(f"    ⚠️ {config}: NOT SET")
                        self.results["configuration"][config] = "⚠️ NOT SET"
                        self.warnings.append(f"Configuration {config} not set")

        except ImportError as e:
            self.errors.append(f"Cannot import settings: {str(e)}")
            print(f"  ❌ Cannot import settings: {str(e)}")

    async def check_api_endpoints(self):
        """Check API endpoints are properly configured"""
        print("\n🌐 Checking API Endpoints...")

        routers_to_check = [
            "auth",
            "agents",
            "chat",
            "stream",
            "feedback",
            "wearables",
            "notifications",
            "whatsapp",
            "visualization",
            "audio",
            "cdn",
        ]

        for router_name in routers_to_check:
            try:
                module = importlib.import_module(f"app.routers.{router_name}")
                if hasattr(module, "router"):
                    # Count routes
                    routes = [route for route in module.router.routes]
                    self.results["api_endpoints"][router_name] = {
                        "status": "✅ OK",
                        "routes": len(routes),
                    }
                    print(f"  ✅ {router_name}: {len(routes)} routes")
                else:
                    self.results["api_endpoints"][router_name] = {
                        "status": "⚠️ WARNING",
                        "error": "No router found",
                    }
                    self.warnings.append(
                        f"Router {router_name}: No router object found"
                    )
                    print(f"  ⚠️ {router_name}: No router found")

            except ImportError as e:
                self.results["api_endpoints"][router_name] = {
                    "status": "❌ ERROR",
                    "error": str(e),
                }
                self.errors.append(f"Router {router_name}: Import error - {str(e)}")
                print(f"  ❌ {router_name}: Import error")

    def generate_report(self):
        """Generate final health check report"""
        print("\n" + "=" * 50)
        print("📊 HEALTH CHECK SUMMARY")
        print("=" * 50)

        # Count totals
        total_agents = len(self.results["agents"])
        ok_agents = sum(
            1
            for a in self.results["agents"].values()
            if "✅" in str(a.get("status", ""))
        )

        total_integrations = sum(
            len(modules) for modules in self.results["integrations"].values()
        )
        ok_integrations = sum(
            1
            for category in self.results["integrations"].values()
            for status in category.values()
            if "✅" in str(status)
        )

        total_infrastructure = len(self.results["infrastructure"])
        ok_infrastructure = sum(
            1 for status in self.results["infrastructure"].values() if "✅" in status
        )

        total_configs = len(self.results["configuration"])
        ok_configs = sum(
            1 for status in self.results["configuration"].values() if "✅" in status
        )

        total_endpoints = len(self.results["api_endpoints"])
        ok_endpoints = sum(
            1
            for e in self.results["api_endpoints"].values()
            if e.get("status", "").startswith("✅")
        )

        # Print summary
        print(f"\n✅ Agents: {ok_agents}/{total_agents}")
        print(f"✅ Integrations: {ok_integrations}/{total_integrations}")
        print(f"✅ Infrastructure: {ok_infrastructure}/{total_infrastructure}")
        print(f"✅ Configuration: {ok_configs}/{total_configs}")
        print(f"✅ API Endpoints: {ok_endpoints}/{total_endpoints}")

        # Overall health score
        total_checks = (
            total_agents
            + total_integrations
            + total_infrastructure
            + total_configs
            + total_endpoints
        )
        ok_checks = (
            ok_agents + ok_integrations + ok_infrastructure + ok_configs + ok_endpoints
        )
        health_score = (ok_checks / total_checks * 100) if total_checks > 0 else 0

        print(f"\n🏥 Overall Health Score: {health_score:.1f}%")

        # Print errors and warnings
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors[:5]:
                print(f"  • {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more")

        if self.warnings:
            print(f"\n⚠️ Warnings ({len(self.warnings)}):")
            for warning in self.warnings[:5]:
                print(f"  • {warning}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more")

        # Recommendations
        print("\n💡 Recommendations:")
        if health_score >= 90:
            print(
                "  ✅ System is in excellent condition! Ready for frontend development."
            )
        elif health_score >= 75:
            print(
                "  ✅ System is in good condition. Address warnings before production."
            )
        elif health_score >= 60:
            print("  ⚠️ System needs attention. Fix errors before proceeding.")
        else:
            print("  ❌ System has critical issues. Address all errors immediately.")

        # Save detailed report
        report_path = Path("health_check_report.json")
        import json

        with open(report_path, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "health_score": health_score,
                    "results": self.results,
                    "errors": self.errors,
                    "warnings": self.warnings,
                },
                f,
                indent=2,
            )
        print(f"\n📄 Detailed report saved to: {report_path}")

        print("\n" + "=" * 50)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


async def main():
    """Run the health check"""
    checker = SystemHealthChecker()
    await checker.run_all_checks()


if __name__ == "__main__":
    asyncio.run(main())
