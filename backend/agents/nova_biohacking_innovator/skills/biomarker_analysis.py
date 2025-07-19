"""
Biomarker Analysis Skill
========================

Analyzes and interprets biomarker data for optimization.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class BiomarkerAnalysisSkill:
    """Skill for biomarker analysis and interpretation."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "biomarker_analysis"
        self.description = "Analyze and interpret biomarker data"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze biomarker data.
        
        Args:
            request: Contains lab_results, previous_results, health_goals
            
        Returns:
            Biomarker analysis and optimization plan
        """
        try:
            biomarker_data = {
                "current_results": request.get("lab_results", {}),
                "previous_results": request.get("previous_results", {}),
                "reference_ranges": request.get("reference_ranges", {}),
                "health_goals": request.get("health_goals", []),
                "symptoms": request.get("symptoms", [])
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_biomarker_analysis_prompt(biomarker_data)
            
            # Generate analysis
            response = await self.agent.generate_response(prompt)
            
            # Analyze trends if previous results available
            trends = self._analyze_trends(biomarker_data)
            
            return {
                "success": True,
                "protocol": response,
                "skill_used": "biomarker_analysis",
                "data": {
                    "markers_analyzed": len(biomarker_data["current_results"]),
                    "optimization_priorities": self._identify_priorities(biomarker_data),
                    "trends": trends,
                    "actionable_insights": True
                },
                "metadata": {
                    "analysis_depth": "comprehensive",
                    "confidence": 0.90,
                    "clinical_relevance": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in biomarker analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "biomarker_analysis"
            }
    
    def _analyze_trends(self, biomarker_data: Dict[str, Any]) -> Dict[str, str]:
        """Analyze trends in biomarker data."""
        trends = {}
        current = biomarker_data.get("current_results", {})
        previous = biomarker_data.get("previous_results", {})
        
        if not previous:
            return {"status": "first_assessment"}
        
        for marker, value in current.items():
            if marker in previous:
                prev_value = previous[marker]
                if isinstance(value, (int, float)) and isinstance(prev_value, (int, float)):
                    change = ((value - prev_value) / prev_value) * 100
                    if abs(change) < 5:
                        trends[marker] = "stable"
                    elif change > 0:
                        trends[marker] = "increasing"
                    else:
                        trends[marker] = "decreasing"
        
        return trends
    
    def _identify_priorities(self, biomarker_data: Dict[str, Any]) -> List[str]:
        """Identify optimization priorities from biomarkers."""
        priorities = []
        current = biomarker_data.get("current_results", {})
        
        # Simple heuristic for demonstration
        if current.get("inflammation_markers"):
            priorities.append("inflammation_reduction")
            
        if current.get("metabolic_markers"):
            priorities.append("metabolic_optimization")
            
        if current.get("hormone_panel"):
            priorities.append("hormonal_balance")
            
        if not priorities:
            priorities = ["general_optimization"]
            
        return priorities[:3]  # Top 3 priorities