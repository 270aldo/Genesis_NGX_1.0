"""
Genetic Analysis Skill
======================

Core genetic analysis functionality for CODE agent.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class GeneticAnalysisSkill:
    """Skill for analyzing genetic profiles."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "genetic_analysis"
        self.description = "Analyze genetic variants and provide insights"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze genetic profile.
        
        Args:
            request: Contains genetic_data, analysis_type, user_profile
            
        Returns:
            Genetic analysis results
        """
        try:
            genetic_data = request.get("genetic_data", {})
            analysis_type = request.get("analysis_type", "comprehensive")
            user_profile = request.get("user_profile", {})
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_genetic_analysis_prompt({
                "genetic_data": genetic_data,
                "analysis_type": analysis_type,
                "user_profile": user_profile
            })
            
            # Generate analysis using agent's Vertex AI client
            response = await self.agent.generate_response(prompt)
            
            # Structure the response
            return {
                "success": True,
                "analysis": response,
                "skill_used": "genetic_analysis",
                "metadata": {
                    "variants_analyzed": len(genetic_data.get("variants", [])),
                    "analysis_type": analysis_type,
                    "confidence": 0.92
                }
            }
            
        except Exception as e:
            logger.error(f"Error in genetic analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "genetic_analysis"
            }