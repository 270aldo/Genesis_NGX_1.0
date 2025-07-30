#!/usr/bin/env python3
"""
Compare Mock vs Real Orchestrator Clients

This script runs the same test scenarios through both the mock and real
orchestrator clients to compare their behavior and identify discrepancies.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.logging_config import get_logger
from tests.beta_validation.real_orchestrator_client import RealOrchestratorClient
from tests.beta_validation.intelligent_mock_client import IntelligentMockOrchestratorClient
from app.schemas.chat import ChatRequest

logger = get_logger(__name__)


class ClientComparator:
    """Compare responses from different orchestrator clients"""
    
    def __init__(self):
        self.test_scenarios = [
            {
                "name": "Simple greeting",
                "request": ChatRequest(
                    text="Hola, soy nuevo aquí",
                    user_id="test-user",
                    session_id="test-session"
                )
            },
            {
                "name": "Workout plan request",
                "request": ChatRequest(
                    text="Necesito un plan de entrenamiento para perder peso",
                    user_id="test-user",
                    session_id="test-session"
                )
            },
            {
                "name": "Frustration handling",
                "request": ChatRequest(
                    text="Este plan no funciona, es muy complicado!",
                    user_id="test-user",
                    session_id="test-session",
                    context={"user_emotion": "frustrated"}
                )
            },
            {
                "name": "Body image concern",
                "request": ChatRequest(
                    text="Me siento gorda y horrible",
                    user_id="test-user",
                    session_id="test-session"
                )
            },
            {
                "name": "Technical issue",
                "request": ChatRequest(
                    text="No puedo conectar mi dispositivo a la app",
                    user_id="test-user",
                    session_id="test-session",
                    context={"topic": "technology"}
                )
            },
            {
                "name": "Aggressive language",
                "request": ChatRequest(
                    text="Esta mierda no funciona, son unos estafadores!",
                    user_id="test-user",
                    session_id="test-session"
                )
            },
            {
                "name": "Progress plateau",
                "request": ChatRequest(
                    text="Llevo 3 semanas sin perder peso a pesar de seguir el plan",
                    user_id="test-user",
                    session_id="test-session"
                )
            },
            {
                "name": "Cost concern",
                "request": ChatRequest(
                    text="Es muy caro, no puedo pagar tanto",
                    user_id="test-user",
                    session_id="test-session"
                )
            }
        ]
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "scenarios": [],
            "summary": {
                "total_scenarios": len(self.test_scenarios),
                "behavior_matches": 0,
                "discrepancies": []
            }
        }
    
    async def compare_clients(self):
        """Run comparison between mock and real clients"""
        logger.info("Starting client comparison...")
        
        # Initialize clients
        mock_client = IntelligentMockOrchestratorClient()
        real_client = RealOrchestratorClient(test_mode=True, use_real_ai=False)
        
        try:
            # Initialize real client
            logger.info("Initializing real orchestrator client...")
            await real_client.initialize()
            
            # Run each scenario
            for scenario in self.test_scenarios:
                logger.info(f"\nTesting scenario: {scenario['name']}")
                
                # Get responses from both clients
                mock_response = await mock_client.process_message(scenario["request"])
                real_response = await real_client.process_message(scenario["request"])
                
                # Compare responses
                comparison = self._compare_responses(
                    scenario["name"],
                    mock_response,
                    real_response
                )
                
                self.results["scenarios"].append(comparison)
                
                # Log brief comparison
                if comparison["behavior_match"]:
                    logger.info(f"✅ Behavior match for: {scenario['name']}")
                else:
                    logger.warning(f"⚠️  Behavior mismatch for: {scenario['name']}")
                    for issue in comparison["discrepancies"]:
                        logger.warning(f"   - {issue}")
            
            # Calculate summary
            self._calculate_summary()
            
            # Save results
            self._save_results()
            
            logger.info("\nComparison completed!")
            self._print_summary()
            
        finally:
            # Clean up
            await real_client.cleanup()
    
    def _compare_responses(self, scenario_name: str, mock_response, real_response) -> Dict:
        """Compare two responses and identify discrepancies"""
        comparison = {
            "scenario": scenario_name,
            "mock_response": {
                "text": mock_response.response[:200] + "..." if len(mock_response.response) > 200 else mock_response.response,
                "agents_used": mock_response.agents_used,
                "metadata": mock_response.metadata
            },
            "real_response": {
                "text": real_response.response[:200] + "..." if len(real_response.response) > 200 else real_response.response,
                "agents_used": real_response.agents_used,
                "metadata": real_response.metadata
            },
            "behavior_match": True,
            "discrepancies": []
        }
        
        # Check expected behaviors from mock metadata
        expected_behaviors = mock_response.metadata.get("behaviors_included", [])
        real_response_lower = real_response.response.lower()
        
        # Check if real response includes expected behaviors
        behavior_checks = {
            "acknowledge_frustration": ["entiendo", "comprendo", "frustración"],
            "offer_to_adjust_plan": ["ajustar", "modificar", "cambiar", "adaptar"],
            "empathetic_response": ["siento", "entiendo cómo", "lamento"],
            "validate_feelings": ["válidos", "normal", "comprensible"],
            "suggest_mental_health_resources": ["profesional", "salud mental", "apoyo"],
            "patient_guidance": ["paso a paso", "tu ritmo", "despacio"],
            "provide_alternatives": ["alternativas", "opciones", "otra forma"]
        }
        
        for behavior in expected_behaviors:
            if behavior in behavior_checks:
                keywords = behavior_checks[behavior]
                if not any(keyword in real_response_lower for keyword in keywords):
                    comparison["behavior_match"] = False
                    comparison["discrepancies"].append(
                        f"Expected behavior '{behavior}' not found in real response"
                    )
        
        # Check agent usage differences
        mock_agents = set(mock_response.agents_used)
        real_agents = set(real_response.agents_used)
        
        if mock_agents != real_agents:
            comparison["discrepancies"].append(
                f"Different agents used - Mock: {mock_agents}, Real: {real_agents}"
            )
        
        # Check response length (should be reasonable)
        if len(real_response.response) < 50:
            comparison["behavior_match"] = False
            comparison["discrepancies"].append("Real response too short")
        
        # Check for error responses
        if "error" in real_response.response.lower() and "error" not in mock_response.response.lower():
            comparison["behavior_match"] = False
            comparison["discrepancies"].append("Real response contains unexpected error")
        
        return comparison
    
    def _calculate_summary(self):
        """Calculate summary statistics"""
        behavior_matches = sum(1 for s in self.results["scenarios"] if s["behavior_match"])
        self.results["summary"]["behavior_matches"] = behavior_matches
        
        # Collect all unique discrepancies
        all_discrepancies = []
        for scenario in self.results["scenarios"]:
            all_discrepancies.extend(scenario["discrepancies"])
        
        # Count discrepancy types
        discrepancy_counts = {}
        for disc in all_discrepancies:
            disc_type = disc.split(" - ")[0]
            discrepancy_counts[disc_type] = discrepancy_counts.get(disc_type, 0) + 1
        
        self.results["summary"]["discrepancy_types"] = discrepancy_counts
        self.results["summary"]["match_rate"] = (behavior_matches / len(self.test_scenarios)) * 100
    
    def _save_results(self):
        """Save comparison results to file"""
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_dir / f"client_comparison_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {filename}")
    
    def _print_summary(self):
        """Print summary to console"""
        print("\n" + "=" * 80)
        print("CLIENT COMPARISON SUMMARY")
        print("=" * 80)
        
        print(f"\nTotal scenarios tested: {self.results['summary']['total_scenarios']}")
        print(f"Behavior matches: {self.results['summary']['behavior_matches']}")
        print(f"Match rate: {self.results['summary']['match_rate']:.1f}%")
        
        if self.results['summary']['discrepancy_types']:
            print("\nDiscrepancy types:")
            for disc_type, count in self.results['summary']['discrepancy_types'].items():
                print(f"  - {disc_type}: {count}")
        
        print("\nScenario results:")
        for scenario in self.results["scenarios"]:
            status = "✅" if scenario["behavior_match"] else "❌"
            print(f"  {status} {scenario['scenario']}")
            if scenario["discrepancies"]:
                for disc in scenario["discrepancies"][:2]:  # Show first 2
                    print(f"     - {disc}")


async def main():
    """Main entry point"""
    comparator = ClientComparator()
    await comparator.compare_clients()


if __name__ == "__main__":
    asyncio.run(main())