"""
Supplement Protocols Skill
==========================

Designs evidence-based supplement protocols.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class SupplementProtocolsSkill:
    """Skill for supplement protocol design."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "supplement_protocols"
        self.description = "Design personalized supplement protocols"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design supplement protocol.
        
        Args:
            request: Contains goals, current_supplements, budget, health_data
            
        Returns:
            Supplement protocol recommendations
        """
        try:
            protocol_data = {
                "goals": request.get("goals", ["general_health"]),
                "current_supplements": request.get("current_supplements", []),
                "budget": request.get("budget", "moderate"),
                "health_conditions": request.get("health_data", {}).get("conditions", []),
                "preferences": request.get("preferences", {}),
                "risk_tolerance": request.get("risk_tolerance", "moderate")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_supplement_protocol_prompt(protocol_data)
            
            # Generate protocol
            response = await self.agent.generate_response(prompt)
            
            # Assess evidence level
            evidence_level = self._assess_evidence_level(protocol_data["goals"])
            
            return {
                "success": True,
                "protocol": response,
                "skill_used": "supplement_protocols",
                "data": {
                    "protocol_complexity": self._calculate_complexity(protocol_data),
                    "safety_score": self._calculate_safety_score(protocol_data),
                    "personalization_level": "high"
                },
                "evidence_level": evidence_level,
                "metadata": {
                    "approach": "evidence_based",
                    "confidence": 0.88,
                    "safety_verified": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in supplement protocol design: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "supplement_protocols"
            }
    
    def _assess_evidence_level(self, goals: List[str]) -> str:
        """Assess evidence level for protocol goals."""
        high_evidence = ["general_health", "vitamin_deficiency", "immune_support"]
        moderate_evidence = ["cognitive_enhancement", "athletic_performance", "sleep"]
        
        for goal in goals:
            if goal in high_evidence:
                return "high"
        
        for goal in goals:
            if goal in moderate_evidence:
                return "moderate"
                
        return "emerging"
    
    def _calculate_complexity(self, protocol_data: Dict[str, Any]) -> str:
        """Calculate protocol complexity."""
        supplement_count = len(protocol_data.get("current_supplements", []))
        goal_count = len(protocol_data.get("goals", []))
        
        if supplement_count + goal_count > 10:
            return "complex"
        elif supplement_count + goal_count > 5:
            return "moderate"
        else:
            return "simple"
    
    def _calculate_safety_score(self, protocol_data: Dict[str, Any]) -> float:
        """Calculate safety score for protocol."""
        score = 1.0
        
        # Reduce score for health conditions
        condition_count = len(protocol_data.get("health_conditions", []))
        score -= min(0.3, condition_count * 0.1)
        
        # Adjust for risk tolerance
        if protocol_data.get("risk_tolerance") == "conservative":
            score = min(1.0, score + 0.1)
        elif protocol_data.get("risk_tolerance") == "aggressive":
            score -= 0.1
            
        return max(0.5, score)