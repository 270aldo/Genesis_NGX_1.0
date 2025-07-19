"""
Supplement Recommendation Skill
===============================

Recommends supplements based on biomarkers and health goals.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class SupplementRecommendationSkill:
    """Skill for recommending supplements."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend supplements based on biomarkers and goals.
        
        Args:
            request: Contains biomarkers and health goals
            
        Returns:
            Supplement recommendations
        """
        try:
            biomarkers = request.get("biomarkers", {})
            goals = request.get("goals", ["general_health"])
            
            # Use agent's prompt system
            prompt = self.agent.prompts.get_supplement_recommendation_prompt(biomarkers, goals)
            
            # Generate recommendations using agent's LLM
            recommendations = await self.agent.generate_response(prompt)
            
            # Add safety disclaimer
            if "supplement" in recommendations.lower():
                recommendations += "\n\n⚠️ IMPORTANT: Always consult with a healthcare provider before starting any supplement regimen."
            
            return {
                "success": True,
                "supplements": recommendations,
                "skill_used": "supplement_recommendation",
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"Error recommending supplements: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "supplement_recommendation"
            }