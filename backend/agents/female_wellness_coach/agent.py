"""
LUNA Female Wellness Coach Agent (Refactored)
=============================================

This is a refactored version of the LUNA agent using the modular architecture.
Original: ~2,030 lines → Refactored: ~400 lines (target)

The functionality is now split into:
- Core agent logic (this file)
- Skills modules (skills/)
- Services (services/)
- Configuration (config.py)
- Prompts (prompts.py)

IMPORTANT: Following ADK and A2A protocols - inherits from BOTH BaseNGXAgent AND ADKAgent
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base.base_ngx_agent import BaseNGXAgent
from agents.base.adk_agent import ADKAgent
from adk.agent import Skill
from adk.toolkit import Toolkit
from core.logging_config import get_logger
from infrastructure.adapters.a2a_adapter import a2a_adapter

# Import agent-specific components
from .config import LunaConfig
from .prompts import LunaPrompts
from .skills import (
    HormonalHealthSkill,
    PrenatalWellnessSkill,
    PostpartumRecoverySkill,
    MenopauseSupportSkill,
    StressManagementSkill
)

logger = get_logger(__name__)


class FemaleWellnessCoach(BaseNGXAgent, ADKAgent):
    """
    LUNA - Female Wellness Coach Agent (Refactored).
    
    IMPORTANT: Inherits from BOTH BaseNGXAgent AND ADKAgent for full ADK/A2A compliance.
    
    Specializes in women's health across all life stages, providing personalized
    wellness guidance with empathy and scientific backing.
    """
    
    def __init__(self, config: Optional[LunaConfig] = None, **kwargs):
        """Initialize LUNA agent with modular architecture."""
        config = config or LunaConfig()
        
        # Store config and initialize prompts first
        self.config = config
        self.prompts = LunaPrompts(personality_type=config.personality_type)
        
        # Get description for initialization
        description = (
            "LUNA is your dedicated female wellness coach, specializing in women's "
            "health across all life stages. With expertise in hormonal health, "
            "prenatal/postpartum care, and menopause support, LUNA provides "
            "compassionate, evidence-based guidance tailored to each woman's unique journey."
        )
        
        # Initialize with all required parameters
        super().__init__(
            agent_id=config.agent_id,
            agent_name=config.agent_name,
            agent_type=config.agent_type,
            personality_type=config.personality_type,
            model_id=config.model_id,
            temperature=config.temperature,
            name=config.agent_name,  # Required by ADKAgent
            description=description,  # Required by ADKAgent
            instruction=self.prompts.get_base_instruction(),  # Required by ADKAgent
            **kwargs
        )
        
        # Register skills
        self._register_luna_skills()
        
        # Define ADK skills for external protocols (A2A compliance)
        self.adk_skills = [
            Skill(
                name="optimize_hormonal_health",
                description="Provide hormonal health optimization guidance",
                handler=self._adk_optimize_hormonal_health
            ),
            Skill(
                name="create_prenatal_plan",
                description="Create personalized prenatal wellness plans",
                handler=self._adk_create_prenatal_plan
            ),
            Skill(
                name="support_life_transitions",
                description="Support women through life transitions",
                handler=self._adk_support_life_transitions
            )
        ]
        
        logger.info("LUNA Female Wellness Coach initialized (refactored version)")
    
    # ==================== Required Abstract Methods ====================
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of LUNA capabilities."""
        return self.config.capabilities
    
    def get_agent_description(self) -> str:
        """Get LUNA agent description."""
        return (
            "LUNA is your dedicated female wellness coach, specializing in women's "
            "health across all life stages. With expertise in hormonal health, "
            "prenatal/postpartum care, and menopause support, LUNA provides "
            "compassionate, evidence-based guidance tailored to each woman's unique journey."
        )
    
    async def process_user_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request with female wellness expertise.
        
        Args:
            request: User's input
            context: Request context including health data
            
        Returns:
            Wellness guidance response
        """
        try:
            start_time = datetime.now()
            
            # Update state
            self._state["total_interactions"] = self._state.get("total_interactions", 0) + 1
            self._state["last_interaction"] = start_time.isoformat()
            
            # Safety check for medical conditions
            if self.config.medical_disclaimer_required:
                await self._ensure_medical_disclaimer(context)
            
            # Check cache
            cache_key = f"luna:{context.get('user_id', 'anonymous')}:{hash(request)}"
            cached_response = await self.get_cached_response(cache_key)
            if cached_response and self.config.enable_response_cache:
                logger.info("Returning cached wellness response")
                return cached_response
            
            # Detect request type
            request_type = self._detect_wellness_request_type(request, context)
            
            # Route to appropriate skill
            skill_response = await self._route_to_wellness_skill(
                request_type,
                request,
                context
            )
            
            # Build final response
            final_response = {
                "success": True,
                "agent": self.agent_id,
                "response": skill_response.get("guidance", ""),
                "data": skill_response.get("data", {}),
                "metadata": {
                    "request_type": request_type,
                    "skill_used": skill_response.get("skill_used"),
                    "execution_time": (datetime.now() - start_time).total_seconds(),
                    "model_used": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "disclaimer_shown": context.get("disclaimer_acknowledged", False)
                }
            }
            
            # Cache response if enabled
            if self.config.enable_response_cache:
                await self.cache_response(cache_key, final_response, ttl=self.config.cache_ttl)
            
            # Record metrics
            self._metrics["success_count"] = self._metrics.get("success_count", 0) + 1
            self.record_metric("wellness_guidance_time", final_response["metadata"]["execution_time"])
            
            return final_response
            
        except Exception as e:
            return await self.handle_error(e, {"request": request, "context": context})
    
    # ==================== Skill Registration ====================
    
    def _register_luna_skills(self) -> None:
        """Register LUNA-specific skills."""
        # Hormonal health
        if self.config.enable_hormonal_health:
            self.register_skill(
                "hormonal_health",
                HormonalHealthSkill(self),
                metadata={"category": "health", "priority": "high"}
            )
        
        # Prenatal support
        if self.config.enable_prenatal_support:
            self.register_skill(
                "prenatal_wellness",
                PrenatalWellnessSkill(self),
                metadata={"category": "pregnancy", "priority": "high", "requires_disclaimer": True}
            )
        
        # Postpartum recovery
        if self.config.enable_postpartum_recovery:
            self.register_skill(
                "postpartum_recovery",
                PostpartumRecoverySkill(self),
                metadata={"category": "recovery", "priority": "high"}
            )
        
        # Menopause guidance
        if self.config.enable_menopause_guidance:
            self.register_skill(
                "menopause_support",
                MenopauseSupportSkill(self),
                metadata={"category": "transition", "priority": "medium"}
            )
        
        # Stress management
        if self.config.enable_stress_management:
            self.register_skill(
                "stress_management",
                StressManagementSkill(self),
                metadata={"category": "wellness", "priority": "medium"}
            )
    
    # ==================== Request Routing ====================
    
    def _detect_wellness_request_type(self, request: str, context: Dict[str, Any]) -> str:
        """Detect the type of wellness request."""
        request_lower = request.lower()
        
        # Check life stage context first
        life_stage = context.get("user_profile", {}).get("life_stage", "")
        
        if any(term in request_lower for term in ["pregnant", "prenatal", "pregnancy", "expecting"]):
            return "prenatal"
        elif any(term in request_lower for term in ["postpartum", "after birth", "new mom", "breastfeeding"]):
            return "postpartum"
        elif any(term in request_lower for term in ["menopause", "hot flash", "perimenopause"]):
            return "menopause"
        elif any(term in request_lower for term in ["hormone", "cycle", "period", "pms", "pcos"]):
            return "hormonal"
        elif any(term in request_lower for term in ["stress", "anxiety", "mood", "emotional"]):
            return "stress"
        else:
            # Default based on life stage
            if life_stage == "pregnant":
                return "prenatal"
            elif life_stage == "postpartum":
                return "postpartum"
            else:
                return "hormonal"  # Default to hormonal health
    
    async def _route_to_wellness_skill(
        self,
        request_type: str,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route request to appropriate wellness skill."""
        skill_mapping = {
            "hormonal": "hormonal_health",
            "prenatal": "prenatal_wellness",
            "postpartum": "postpartum_recovery",
            "menopause": "menopause_support",
            "stress": "stress_management"
        }
        
        skill_name = skill_mapping.get(request_type, "hormonal_health")
        
        # Check if skill is available
        if skill_name not in self._skills:
            # Fallback to hormonal health
            skill_name = "hormonal_health"
        
        return await self.execute_skill(
            skill_name,
            request={
                "query": request,
                "context": context,
                "health_data": context.get("health_data", {}),
                "user_profile": context.get("user_profile", {})
            }
        )
    
    # ==================== Safety Methods ====================
    
    async def _ensure_medical_disclaimer(self, context: Dict[str, Any]) -> None:
        """Ensure medical disclaimer is acknowledged."""
        if not context.get("disclaimer_acknowledged", False):
            # In production, this would trigger a disclaimer flow
            logger.info("Medical disclaimer required for user")
    
    # ==================== ADK Protocol Methods (A2A Compliance) ====================
    
    async def _adk_optimize_hormonal_health(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for hormonal health optimization."""
        return await self.execute_skill(
            "hormonal_health",
            request={
                "health_data": params.get("health_data", {}),
                "symptoms": params.get("symptoms", []),
                "goals": params.get("goals", [])
            }
        )
    
    async def _adk_create_prenatal_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for prenatal planning."""
        return await self.execute_skill(
            "prenatal_wellness",
            request={
                "trimester": params.get("trimester", 1),
                "health_status": params.get("health_status", {}),
                "concerns": params.get("concerns", [])
            }
        )
    
    async def _adk_support_life_transitions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for life transition support."""
        transition_type = params.get("transition_type", "menopause")
        
        if transition_type == "postpartum":
            skill = "postpartum_recovery"
        elif transition_type == "menopause":
            skill = "menopause_support"
        else:
            skill = "hormonal_health"
            
        return await self.execute_skill(
            skill,
            request={
                "transition_data": params.get("transition_data", {}),
                "support_needed": params.get("support_needed", [])
            }
        )
    
    # ==================== Lifecycle Hooks ====================
    
    async def _agent_startup(self) -> None:
        """LUNA-specific startup tasks."""
        # Initialize health tracking systems if needed
        logger.info("LUNA agent starting up - wellness services ready")
    
    async def _agent_shutdown(self) -> None:
        """LUNA-specific shutdown tasks."""
        # Save any pending health insights
        logger.info("LUNA agent shutting down - saving wellness state")