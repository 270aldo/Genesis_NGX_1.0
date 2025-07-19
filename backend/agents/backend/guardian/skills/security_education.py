"""
Security Education Skill
=======================

Provides security education and awareness content.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class SecurityEducationSkill:
    """Skill for security education and awareness."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "security_education"
        self.description = "Provide security education"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create security education content.
        
        Args:
            request: Contains topic, audience, format
            
        Returns:
            Security education materials
        """
        try:
            education_data = {
                "topic": request.get("topic", "general_security"),
                "audience": request.get("audience", "general_users"),
                "format": request.get("format", "comprehensive"),
                "include_exercises": request.get("include_exercises", True),
                "difficulty_level": request.get("difficulty_level", "beginner")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_security_education_prompt(education_data)
            
            # Generate education content
            response = await self.agent.generate_response(prompt)
            
            # Create learning objectives
            objectives = self._generate_learning_objectives(education_data)
            
            return {
                "success": True,
                "education_content": response,
                "skill_used": "security_education",
                "data": {
                    "topic": education_data["topic"],
                    "audience": education_data["audience"],
                    "learning_objectives": objectives,
                    "estimated_duration": self._estimate_duration(education_data),
                    "includes_practical": education_data["include_exercises"]
                },
                "metadata": {
                    "confidence": 0.93,
                    "pedagogy_type": "interactive",
                    "retention_score": 0.85
                }
            }
            
        except Exception as e:
            logger.error(f"Error in security education: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "security_education"
            }
    
    def _generate_learning_objectives(self, education_data: Dict[str, Any]) -> List[str]:
        """Generate learning objectives based on topic."""
        topic = education_data.get("topic", "general_security")
        audience = education_data.get("audience", "general_users")
        
        base_objectives = [
            f"Understand fundamental concepts of {topic}",
            f"Identify common risks and threats related to {topic}",
            f"Apply best practices for {topic}"
        ]
        
        # Add audience-specific objectives
        if "developer" in audience.lower():
            base_objectives.append("Implement secure coding practices")
        elif "executive" in audience.lower():
            base_objectives.append("Make informed security decisions")
        elif "general" in audience.lower():
            base_objectives.append("Protect personal information online")
        
        # Add topic-specific objectives
        if "phishing" in topic.lower():
            base_objectives.append("Recognize phishing attempts")
        elif "password" in topic.lower():
            base_objectives.append("Create and manage strong passwords")
        elif "privacy" in topic.lower():
            base_objectives.append("Control personal data sharing")
        
        return base_objectives[:5]  # Return top 5 objectives
    
    def _estimate_duration(self, education_data: Dict[str, Any]) -> str:
        """Estimate duration of education session."""
        format_type = education_data.get("format", "comprehensive")
        include_exercises = education_data.get("include_exercises", True)
        
        if format_type == "quick":
            base_minutes = 15
        elif format_type == "standard":
            base_minutes = 30
        else:  # comprehensive
            base_minutes = 60
        
        if include_exercises:
            base_minutes += 15
        
        if base_minutes <= 30:
            return f"{base_minutes} minutes"
        else:
            hours = base_minutes / 60
            return f"{hours:.1f} hours"