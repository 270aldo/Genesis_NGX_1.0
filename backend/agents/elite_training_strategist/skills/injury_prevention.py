"""
Injury Prevention Skill
=======================

Assesses injury risks and provides prevention strategies.
"""

from typing import Dict, Any, Optional, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class InjuryPreventionSkill:
    """Skill for injury risk assessment and prevention strategies."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess injury risks and provide prevention strategies.
        
        Args:
            request: Contains risk factors and user context
            
        Returns:
            Injury prevention assessment and strategies
        """
        try:
            risk_factors = request.get("risk_factors", {
                "movement_issues": [],
                "injury_history": [],
                "weekly_volume": "moderate",
                "imbalances": [],
                "primary_activity": "general fitness"
            })
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(risk_factors)
            
            # Use agent's prompt system
            prompt = self.agent.prompts.get_injury_prevention_prompt(risk_factors)
            
            # Generate prevention strategies using agent's LLM
            strategies = await self.agent.generate_response(prompt)
            
            # Add risk-based warnings
            if risk_score > 0.7:
                strategies = "⚠️ HIGH INJURY RISK DETECTED\n\n" + strategies
                strategies += "\n\n🏥 IMPORTANT: Consider consulting a physical therapist or sports medicine professional before continuing intensive training."
            
            return {
                "success": True,
                "risk_score": risk_score,
                "risk_level": self._get_risk_level(risk_score),
                "prevention_strategies": strategies,
                "immediate_actions": self._get_immediate_actions(risk_score, risk_factors),
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"Error in injury prevention assessment: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_risk_score(self, risk_factors: Dict[str, Any]) -> float:
        """Calculate overall injury risk score (0-1)."""
        score = 0.0
        
        # Previous injuries (highest weight)
        injury_count = len(risk_factors.get("injury_history", []))
        score += min(injury_count * 0.15, 0.4)
        
        # Movement issues
        movement_issues = len(risk_factors.get("movement_issues", []))
        score += min(movement_issues * 0.1, 0.3)
        
        # Training volume
        volume = risk_factors.get("weekly_volume", "moderate")
        if volume == "high":
            score += 0.2
        elif volume == "very_high":
            score += 0.3
        
        # Muscle imbalances
        imbalances = len(risk_factors.get("imbalances", []))
        score += min(imbalances * 0.05, 0.15)
        
        return min(score, 1.0)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level."""
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "moderate"
        else:
            return "low"
    
    def _get_immediate_actions(self, risk_score: float, risk_factors: Dict[str, Any]) -> List[str]:
        """Get immediate actions based on risk assessment."""
        actions = []
        
        if risk_score >= 0.7:
            actions.append("Reduce training volume by 30-50% immediately")
            actions.append("Focus on mobility and corrective exercises")
            actions.append("Consider professional assessment")
        
        if risk_factors.get("injury_history"):
            actions.append("Warm up thoroughly before every session")
            actions.append("Avoid exercises that previously caused issues")
        
        if risk_factors.get("movement_issues"):
            actions.append("Prioritize movement quality over load")
            actions.append("Include daily mobility work")
        
        return actions