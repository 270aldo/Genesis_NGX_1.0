"""
Mindset Coaching Skill
======================

Transforms limiting beliefs and builds empowering mindsets.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class MindsetCoachingSkill:
    """Skill for mindset transformation coaching."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "mindset_coaching"
        self.description = "Transform limiting beliefs and mindsets"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide mindset coaching.
        
        Args:
            request: Contains limiting_beliefs, desired_mindset, challenges
            
        Returns:
            Mindset transformation guidance
        """
        try:
            mindset_data = {
                "limiting_beliefs": request.get("limiting_beliefs", []),
                "desired_mindset": request.get("desired_mindset", "growth"),
                "current_challenges": request.get("challenges", []),
                "strengths": request.get("user_profile", {}).get("strengths", []),
                "query": request.get("query", "")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_mindset_coaching_prompt(mindset_data)
            
            # Generate mindset coaching
            response = await self.agent.generate_response(prompt)
            
            return {
                "success": True,
                "coaching": response,
                "skill_used": "mindset_coaching",
                "data": {
                    "beliefs_addressed": len(mindset_data["limiting_beliefs"]),
                    "transformation_focus": self._identify_transformation_focus(mindset_data),
                    "techniques": ["reframing", "evidence_gathering", "visualization"]
                },
                "metadata": {
                    "approach": "cognitive_behavioral",
                    "confidence": 0.91,
                    "transformative": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in mindset coaching: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "mindset_coaching"
            }
    
    def _identify_transformation_focus(self, mindset_data: Dict[str, Any]) -> str:
        """Identify the primary focus for mindset transformation."""
        limiting_beliefs = mindset_data.get("limiting_beliefs", [])
        
        if not limiting_beliefs:
            return "growth_reinforcement"
        
        # Analyze belief patterns
        belief_text = " ".join(limiting_beliefs).lower()
        
        if any(word in belief_text for word in ["can't", "unable", "impossible"]):
            return "capability_expansion"
        elif any(word in belief_text for word in ["worth", "deserve", "enough"]):
            return "self_worth_elevation"
        elif any(word in belief_text for word in ["fail", "mistake", "wrong"]):
            return "resilience_building"
        else:
            return "perspective_shift"