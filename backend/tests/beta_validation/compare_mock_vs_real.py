#!/usr/bin/env python3
"""
Compare Mock vs Real Orchestrator Responses

This script runs the same scenarios with both mock and real orchestrators
to compare their behavior and identify gaps.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.schemas.chat import ChatRequest
from tests.beta_validation.intelligent_mock_client import IntelligentMockOrchestratorClient
from tests.beta_validation.real_orchestrator_client import RealOrchestratorClient
from core.logging_config import get_logger

logger = get_logger(__name__)


class MockVsRealComparator:
    """Compare responses between mock and real orchestrators"""
    
    def __init__(self):
        self.mock_client = None
        self.real_client = None
        self.comparison_results = []
        
    async def setup(self):
        """Set up both clients"""
        print("Setting up clients...")
        
        # Create mock client
        self.mock_client = IntelligentMockOrchestratorClient()
        print("  ✅ Mock client ready")
        
        # Create real client
        self.real_client = RealOrchestratorClient(test_mode=True)
        await self.real_client.initialize()
        print("  ✅ Real client initialized")
        
    async def cleanup(self):
        """Clean up resources"""
        if self.real_client:
            await self.real_client.cleanup()
            
    async def compare_single_message(self, request: ChatRequest) -> Dict[str, Any]:
        """Compare responses for a single message"""
        # Get mock response
        mock_response = await self.mock_client.process_message(request)
        
        # Get real response
        real_response = await self.real_client.process_message(request)
        
        # Compare responses
        comparison = {
            "request": request.text,
            "mock": {
                "response_preview": mock_response.response[:200] + "...",
                "agents_used": mock_response.agents_used,
                "metadata": mock_response.metadata
            },
            "real": {
                "response_preview": real_response.response[:200] + "...",
                "agents_used": real_response.agents_used,
                "metadata": real_response.metadata
            },
            "differences": self._analyze_differences(mock_response, real_response)
        }
        
        return comparison
        
    def _analyze_differences(self, mock_response, real_response) -> Dict[str, Any]:
        """Analyze differences between responses"""
        differences = {
            "agents_match": set(mock_response.agents_used) == set(real_response.agents_used),
            "response_length_diff": abs(len(mock_response.response) - len(real_response.response)),
            "both_handle_emotion": False,
            "behavioral_gaps": []
        }
        
        # Check if both handle emotional content
        emotion_keywords = ["entiendo", "comprendo", "frustración", "siento"]
        mock_has_emotion = any(kw in mock_response.response.lower() for kw in emotion_keywords)
        real_has_emotion = any(kw in real_response.response.lower() for kw in emotion_keywords)
        differences["both_handle_emotion"] = mock_has_emotion and real_has_emotion
        
        # Check for expected behaviors in mock that might be missing in real
        mock_behaviors = mock_response.metadata.get("behaviors_included", [])
        for behavior in mock_behaviors:
            if not self._check_behavior_in_response(behavior, real_response.response):
                differences["behavioral_gaps"].append(behavior)
                
        return differences
        
    def _check_behavior_in_response(self, behavior: str, response: str) -> bool:
        """Check if a behavior is present in response"""
        behavior_indicators = {
            "acknowledge_frustration": ["entiendo", "comprendo", "frustración"],
            "offer_to_adjust_plan": ["ajustar", "modificar", "cambiar el plan"],
            "empathetic_response": ["siento", "lamento", "entiendo cómo"],
            "provide_alternatives": ["alternativas", "opciones", "otra forma"],
            "patient_guidance": ["paso a paso", "tu ritmo", "no hay prisa"]
        }
        
        if behavior in behavior_indicators:
            return any(indicator in response.lower() for indicator in behavior_indicators[behavior])
        return False
        
    async def run_comparison_suite(self):
        """Run a suite of comparison tests"""
        print("\n" + "="*60)
        print("Running Mock vs Real Comparison Suite")
        print("="*60 + "\n")
        
        test_cases = [
            {
                "name": "Simple greeting",
                "request": ChatRequest(
                    text="Hola, ¿cómo estás?",
                    session_id="test-1"
                )
            },
            {
                "name": "Frustrated user",
                "request": ChatRequest(
                    text="Este plan no funciona, estoy muy frustrado",
                    session_id="test-2",
                    context={"user_emotion": "frustrated"}
                )
            },
            {
                "name": "Angry user with profanity",
                "request": ChatRequest(
                    text="Esta mierda de plan no sirve para nada",
                    session_id="test-3",
                    context={"user_emotion": "angry"}
                )
            },
            {
                "name": "Technical confusion",
                "request": ChatRequest(
                    text="No entiendo cómo conectar mi dispositivo, es muy complicado",
                    session_id="test-4",
                    context={"topic": "technology"}
                )
            },
            {
                "name": "Body image concerns",
                "request": ChatRequest(
                    text="Me veo gorda y odio mi cuerpo",
                    session_id="test-5",
                    context={"user_emotion": "depressed"}
                )
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {test_case['name']}")
            print(f"   Message: {test_case['request'].text}")
            
            try:
                comparison = await self.compare_single_message(test_case['request'])
                self.comparison_results.append(comparison)
                
                # Print summary
                print(f"   Mock agents: {comparison['mock']['agents_used']}")
                print(f"   Real agents: {comparison['real']['agents_used']}")
                print(f"   Agents match: {'✅' if comparison['differences']['agents_match'] else '❌'}")
                print(f"   Both handle emotion: {'✅' if comparison['differences']['both_handle_emotion'] else '❌'}")
                
                if comparison['differences']['behavioral_gaps']:
                    print(f"   ⚠️  Missing behaviors in real: {comparison['differences']['behavioral_gaps']}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    def generate_report(self):
        """Generate comparison report"""
        print("\n" + "="*60)
        print("COMPARISON REPORT")
        print("="*60 + "\n")
        
        total_tests = len(self.comparison_results)
        agent_matches = sum(1 for r in self.comparison_results if r['differences']['agents_match'])
        emotion_handling = sum(1 for r in self.comparison_results if r['differences']['both_handle_emotion'])
        
        print(f"Total test cases: {total_tests}")
        print(f"Agent selection matches: {agent_matches}/{total_tests} ({agent_matches/total_tests*100:.1f}%)")
        print(f"Emotion handling matches: {emotion_handling}/{total_tests} ({emotion_handling/total_tests*100:.1f}%)")
        
        # Identify common gaps
        all_gaps = []
        for result in self.comparison_results:
            all_gaps.extend(result['differences']['behavioral_gaps'])
            
        if all_gaps:
            print("\nMost common behavioral gaps in real orchestrator:")
            from collections import Counter
            gap_counts = Counter(all_gaps)
            for behavior, count in gap_counts.most_common(5):
                print(f"  - {behavior}: {count} occurrences")
                
        # Save detailed report
        report_path = Path("reports/mock_vs_real_comparison.json")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump({
                "timestamp": asyncio.get_event_loop().time(),
                "summary": {
                    "total_tests": total_tests,
                    "agent_matches": agent_matches,
                    "emotion_matches": emotion_handling
                },
                "results": self.comparison_results
            }, f, indent=2)
            
        print(f"\nDetailed report saved to: {report_path}")


async def main():
    """Main entry point"""
    comparator = MockVsRealComparator()
    
    try:
        await comparator.setup()
        await comparator.run_comparison_suite()
        comparator.generate_report()
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await comparator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())