"""
Sport Genetics Skill
====================

Athletic performance optimization based on genetics.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class SportGeneticsSkill:
    """Skill for sport genetics analysis."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "sport_genetics"
        self.description = "Analyze athletic potential based on genetics"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sport genetics.
        
        Args:
            request: Contains genetic_data, sport_preferences, fitness_level
            
        Returns:
            Sport genetics analysis
        """
        try:
            profile = {
                "genetic_data": request.get("genetic_data", {}),
                "sport_preferences": request.get("sport_preferences", []),
                "fitness_level": request.get("fitness_level", "intermediate")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_sport_genetics_prompt(profile)
            
            # Generate analysis
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "skill_used": "sport_genetics",
                "metadata": {
                    "analysis_type": "athletic_potential",
                    "confidence": 0.90
                }
            }
            
        except Exception as e:
            logger.error(f"Error in sport genetics analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "sport_genetics"
            }