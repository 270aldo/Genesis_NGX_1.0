"""
SAGE Precision Nutrition Architect Agent (Refactored)
=====================================================

This is a refactored version of the SAGE agent using the modular architecture.
Original: ~3,833 lines → Refactored: ~400 lines (90% reduction target)

The functionality is now split into:
- Core agent logic (this file)
- Skills modules (skills/)
- Services (services/)
- Configuration (config.py)
- Prompts (prompts/)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base.base_ngx_agent import BaseNGXAgent
from agents.base.adk_agent import ADKAgent
from adk.agent import Skill
from core.logging_config import get_logger
from infrastructure.adapters.a2a_adapter import a2a_adapter

# Import agent-specific components
from .config import SageConfig
from .prompts import SagePrompts
from .skills import (
    MealPlanGenerationSkill,
    SupplementRecommendationSkill,
    BiomarkerAnalysisSkill,
    ChrononutritionSkill,
    FoodImageAnalysisSkill
)
from .services import (
    NutritionDataService,
    NutritionSecurityService,
    NutritionIntegrationService
)

logger = get_logger(__name__)


class PrecisionNutritionArchitect(BaseNGXAgent, ADKAgent):
    """
    SAGE - Precision Nutrition Architect Agent (Refactored).
    
    Specializes in creating personalized nutrition plans, supplement recommendations,
    and chrononutrition strategies based on biomarkers and user profile.
    """
    
    def __init__(self, config: Optional[SageConfig] = None, **kwargs):
        """Initialize SAGE agent with modular architecture."""
        config = config or SageConfig()
        
        # Store config and initialize prompts first
        self.config = config
        self.prompts = SagePrompts()
        
        # Get description for initialization
        description = (
            "SAGE is your precision nutrition architect, creating scientifically-backed, "
            "personalized nutrition plans. With expertise in nutrigenomics, chrononutrition, "
            "and metabolic optimization, SAGE helps you achieve optimal health through "
            "precision nutrition strategies."
        )
        
        # Initialize with all required parameters for BaseNGXAgent
        super().__init__(
            agent_id=config.agent_id,
            agent_name=config.agent_name,
            agent_type="nutrition_specialist",
            personality_type=config.personality_type,
            model_id=config.model_id,
            temperature=config.temperature,
            name=config.agent_name,  # Required by ADKAgent
            description=description,  # Required by ADKAgent
            instruction=self.prompts.get_base_instruction(),  # Required by ADKAgent
            **kwargs
        )
        
        # Initialize SAGE-specific services
        self._initialize_services()
        
        # Register skills
        self._register_sage_skills()
        
        # Define ADK skills for external protocols
        self.adk_skills = [
            Skill(
                name="create_meal_plan",
                description="Create personalized meal plans",
                handler=self._adk_create_meal_plan
            ),
            Skill(
                name="recommend_supplements",
                description="Recommend supplements based on biomarkers",
                handler=self._adk_recommend_supplements
            )
        ]
        
        logger.info("SAGE Precision Nutrition Architect initialized (refactored version)")
    
    def _initialize_services(self):
        """Initialize SAGE services."""
        # Los servicios heredan de las clases base y necesitan parámetros
        self.nutrition_service = NutritionDataService(
            supabase_client=self.supabase_client,
            cache=self.cache if hasattr(self, 'cache') else None,
            config=self.config
        )
        self.security_service = NutritionSecurityService(config=self.config)
        self.integration_service = NutritionIntegrationService(config=self.config)
        logger.info("SAGE services initialized")
    
    def _register_sage_skills(self) -> None:
        """Register SAGE-specific skills."""
        # Meal plan generation
        self.register_skill(
            "meal_plan_generation",
            MealPlanGenerationSkill(self),
            metadata={"priority": "critical", "category": "planning"}
        )
        
        # Supplement recommendation
        self.register_skill(
            "supplement_recommendation",
            SupplementRecommendationSkill(self),
            metadata={"priority": "high", "category": "optimization"}
        )
        
        # Biomarker analysis
        self.register_skill(
            "biomarker_analysis",
            BiomarkerAnalysisSkill(self),
            metadata={"priority": "high", "category": "analysis"}
        )
        
        # Chrononutrition planning
        self.register_skill(
            "chrononutrition",
            ChrononutritionSkill(self),
            metadata={"priority": "medium", "category": "timing"}
        )
        
        # Food image analysis
        self.register_skill(
            "food_image_analysis",
            FoodImageAnalysisSkill(self),
            metadata={"priority": "medium", "category": "analysis"}
        )
    
    # ==================== Required Abstract Methods ====================
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of SAGE capabilities."""
        return self.config.capabilities
    
    def get_agent_description(self) -> str:
        """Get SAGE agent description."""
        return (
            "SAGE is your precision nutrition architect, creating scientifically-backed, "
            "personalized nutrition plans. With expertise in nutrigenomics, chrononutrition, "
            "and metabolic optimization, SAGE helps you achieve optimal health through "
            "precision nutrition strategies."
        )
    
    async def process_user_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request for nutrition-related queries.
        
        Args:
            request: User's input
            context: Request context including user data
            
        Returns:
            Nutrition response
        """
        try:
            # Determine the type of nutrition request
            request_lower = request.lower()
            
            if any(word in request_lower for word in ["meal", "plan", "diet", "comida", "dieta"]):
                # Generate meal plan
                result = await self.execute_skill(
                    "meal_plan_generation",
                    message=request,
                    user_profile=context.get("user_profile", {})
                )
            elif any(word in request_lower for word in ["supplement", "vitamin", "suplemento", "vitamina"]):
                # Recommend supplements
                result = await self.execute_skill(
                    "supplement_recommendation",
                    biomarkers=context.get("biomarkers", {}),
                    goals=context.get("goals", [])
                )
            elif any(word in request_lower for word in ["biomarker", "blood", "lab", "análisis", "sangre"]):
                # Analyze biomarkers
                result = await self.execute_skill(
                    "biomarker_analysis",
                    biomarkers=context.get("biomarkers", {})
                )
            elif any(word in request_lower for word in ["timing", "when", "chrono", "cuándo", "horario"]):
                # Chrononutrition planning
                result = await self.execute_skill(
                    "chrononutrition",
                    meal_times=context.get("meal_times", {}),
                    circadian_type=context.get("circadian_type", "balanced")
                )
            elif context.get("image_data"):
                # Food image analysis
                result = await self.execute_skill(
                    "food_image_analysis",
                    image_data=context.get("image_data")
                )
            else:
                # Default to meal plan generation
                result = await self.execute_skill(
                    "meal_plan_generation",
                    message=request,
                    user_profile=context.get("user_profile", {})
                )
            
            return {
                "success": result.get("success", True),
                "agent": self.agent_id,
                "response": result.get("meal_plan") or result.get("supplements") or 
                           result.get("analysis") or result.get("chrono_plan") or
                           result.get("food_analysis", "I'll help you with your nutrition needs."),
                "metadata": {
                    "skill_used": result.get("skill_used", "unknown"),
                    "confidence": result.get("confidence", 0.85)
                }
            }
            
        except Exception as e:
            return await self.handle_error(e, {"request": request, "context": context})
    
    # ==================== ADK Skill Handlers ====================
    
    async def _adk_create_meal_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for creating meal plans."""
        return await self.execute_skill(
            "meal_plan_generation",
            message=params.get("message", ""),
            user_profile=params.get("user_profile", {})
        )
    
    async def _adk_recommend_supplements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK handler for recommending supplements."""
        return await self.execute_skill(
            "supplement_recommendation",
            biomarkers=params.get("biomarkers", {}),
            goals=params.get("goals", [])
        )
    
    # ==================== Main Entry Point ====================
    
    async def run(self, *args, **kwargs):
        """
        Main entry point for SAGE agent using ADK framework.
        
        This method is called when the agent receives a request through A2A protocol.
        """
        # ADKAgent's run method will handle the request and route to appropriate skills
        return await super().run(*args, **kwargs)
    
    async def generate_response(self, prompt: str, temperature: float = None) -> str:
        """
        Generate response using the agent's LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Optional temperature override
            
        Returns:
            Generated response text
        """
        try:
            # Use ADK's generation method if available
            if hasattr(self, 'generate'):
                return await self.generate(prompt, temperature=temperature or self.config.temperature)
            else:
                # Fallback to vertex client
                response = await self.vertex_client.generate_content(
                    prompt, 
                    temperature=temperature or self.config.temperature
                )
                return response.get("text", "")
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}"
    
    # ==================== A2A Communication ====================
    
    async def communicate_with_agent(self, agent_id: str, message: str, context: Dict[str, Any] = None):
        """
        Communicate with another agent using A2A protocol.
        
        Args:
            agent_id: Target agent ID
            message: Message to send
            context: Additional context
            
        Returns:
            Response from the target agent
        """
        try:
            response = await a2a_adapter.send_message(
                from_agent_id=self.agent_id,
                to_agent_id=agent_id,
                message=message,
                context=context or {}
            )
            return response
        except Exception as e:
            logger.error(f"Error communicating with agent {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to communicate with {agent_id}"
            }