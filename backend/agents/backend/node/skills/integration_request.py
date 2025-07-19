"""
Integration Request Skill
========================

Handles system integration requests.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class IntegrationRequestSkill:
    """Skill for handling system integration requests."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "integration_request"
        self.description = "Handle system integration requests"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process integration request.
        
        Args:
            request: Contains query, systems, requirements
            
        Returns:
            Integration solution and plan
        """
        try:
            # Extract integration details
            query = request.get("query", "")
            context = request.get("context", {})
            
            # Identify systems to integrate
            systems = self._identify_systems(query, context)
            
            integration_data = {
                "query": query,
                "systems": systems,
                "requirements": request.get("requirements", {}),
                "auth_type": request.get("auth_type", "oauth2")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_integration_request_prompt(integration_data)
            
            # Generate integration solution
            response = await self.agent.generate_response(prompt)
            
            # Extract integration steps
            steps = self._extract_integration_steps(systems)
            
            return {
                "success": True,
                "integration_plan": response,
                "skill_used": "integration_request",
                "data": {
                    "systems_identified": systems,
                    "integration_steps": steps,
                    "estimated_effort": self._estimate_effort(systems),
                    "recommended_tools": self._recommend_tools(systems)
                },
                "metadata": {
                    "confidence": 0.88,
                    "complexity": self._assess_complexity(systems),
                    "best_practices_applied": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in integration request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "integration_request"
            }
    
    def _identify_systems(self, query: str, context: Dict[str, Any]) -> List[str]:
        """Identify systems mentioned in the query."""
        systems = []
        query_lower = query.lower()
        
        # Fitness and health systems
        fitness_systems = {
            "garmin": ["garmin", "connect", "garmin connect"],
            "fitbit": ["fitbit"],
            "apple_health": ["apple", "health", "healthkit"],
            "google_fit": ["google fit", "googlefit"],
            "strava": ["strava"],
            "oura": ["oura", "ring"],
            "whoop": ["whoop"],
            "myfitnesspal": ["myfitnesspal", "mfp"],
            "polar": ["polar"],
            "suunto": ["suunto"]
        }
        
        for system, keywords in fitness_systems.items():
            if any(keyword in query_lower for keyword in keywords):
                systems.append(system)
        
        # Add from context if provided
        if context.get("systems"):
            systems.extend(context["systems"])
        
        return list(set(systems)) if systems else ["general_system"]
    
    def _extract_integration_steps(self, systems: List[str]) -> List[Dict[str, str]]:
        """Extract integration steps based on systems."""
        steps = [
            {"step": "authentication", "description": "Set up OAuth2/API key authentication"},
            {"step": "data_mapping", "description": "Map data fields between systems"},
            {"step": "sync_setup", "description": "Configure sync frequency and direction"},
            {"step": "error_handling", "description": "Implement retry logic and error handling"},
            {"step": "testing", "description": "Test integration with sample data"}
        ]
        
        if len(systems) > 2:
            steps.insert(2, {
                "step": "conflict_resolution",
                "description": "Define rules for data conflicts"
            })
        
        return steps
    
    def _estimate_effort(self, systems: List[str]) -> str:
        """Estimate integration effort."""
        if len(systems) <= 2:
            return "low"
        elif len(systems) <= 4:
            return "medium"
        else:
            return "high"
    
    def _recommend_tools(self, systems: List[str]) -> List[str]:
        """Recommend integration tools."""
        tools = ["Zapier", "API Gateway"]
        
        if len(systems) > 3:
            tools.extend(["Apache Airflow", "n8n"])
        
        if any("health" in s.lower() for s in systems):
            tools.append("FHIR Standards")
        
        return tools
    
    def _assess_complexity(self, systems: List[str]) -> str:
        """Assess integration complexity."""
        if len(systems) <= 2:
            return "simple"
        elif len(systems) <= 4:
            return "moderate"
        else:
            return "complex"