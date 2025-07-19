"""
Sleep Optimization Skill
========================

Optimizes sleep quality for performance and recovery.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class SleepOptimizationSkill:
    """Skill for sleep optimization analysis."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "sleep_optimization"
        self.description = "Optimize sleep quality and recovery"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize sleep based on data.
        
        Args:
            request: Contains sleep_data, lifestyle_factors, goals
            
        Returns:
            Sleep optimization recommendations
        """
        try:
            sleep_data = {
                "sleep_metrics": request.get("sleep_data", {}),
                "lifestyle_factors": request.get("lifestyle_factors", {}),
                "performance_goals": request.get("goals", []),
                "current_issues": request.get("sleep_issues", [])
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_sleep_optimization_prompt(sleep_data)
            
            # Generate recommendations
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "skill_used": "sleep_optimization",
                "data": {
                    "issues_addressed": len(sleep_data["current_issues"]),
                    "optimization_focus": "quality_and_recovery"
                },
                "metadata": {
                    "recommendation_type": "personalized",
                    "confidence": 0.90
                }
            }
            
        except Exception as e:
            logger.error(f"Error in sleep optimization: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "sleep_optimization"
            }