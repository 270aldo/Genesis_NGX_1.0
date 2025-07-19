"""
Fitness Progress Skill
======================

Tracks and analyzes fitness performance improvements.
"""

from typing import Dict, Any
from core.logging_config import get_logger

logger = get_logger(__name__)


class FitnessProgressSkill:
    """Skill for fitness progress tracking."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "fitness_progress"
        self.description = "Track and analyze fitness progress"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze fitness progress data.
        
        Args:
            request: Contains progress_data, time_period, metrics
            
        Returns:
            Fitness progress analysis
        """
        try:
            progress_data = request.get("progress_data", {})
            time_period = request.get("time_period", "30d")
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_fitness_progress_prompt({
                "progress_data": progress_data,
                "period": time_period,
                "user_context": request.get("context", {})
            })
            
            # Generate analysis
            response = await self.agent.generate_response(prompt)
            
            # Calculate some metrics
            improvements = self._calculate_improvements(progress_data)
            
            return {
                "success": True,
                "analysis": response,
                "skill_used": "fitness_progress",
                "data": {
                    "period_analyzed": time_period,
                    "improvements": improvements,
                    "trend": self.agent._identify_trends(progress_data.get("history", []))
                },
                "metadata": {
                    "analysis_type": "fitness_performance",
                    "confidence": 0.92,
                    "motivational": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in fitness progress analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "fitness_progress"
            }
    
    def _calculate_improvements(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate improvement percentages."""
        improvements = {}
        
        for metric, values in data.items():
            if isinstance(values, dict) and "start" in values and "current" in values:
                start = values["start"]
                current = values["current"]
                if start > 0:
                    improvement = ((current - start) / start) * 100
                    improvements[metric] = round(improvement, 1)
        
        return improvements