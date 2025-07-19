"""
SPARK Motivation & Behavior Coach Agent (Refactored)
====================================================

This is a refactored version of the SPARK agent using the modular architecture.
Original: ~2,871 lines → Refactored: ~400 lines (target)

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
from .config import SparkConfig
from .prompts import SparkPrompts
from .skills import (
    MotivationBoostSkill,
    HabitFormationSkill,
    MindsetCoachingSkill,
    AccountabilityCheckSkill,
    CelebrationSystemSkill
)

logger = get_logger(__name__)


class MotivationBehaviorCoach(BaseNGXAgent, ADKAgent):
    """
    SPARK - Motivation & Behavior Coach Agent (Refactored).
    
    IMPORTANT: Inherits from BOTH BaseNGXAgent AND ADKAgent for full ADK/A2A compliance.
    
    Specializes in transformational motivation, habit formation, mindset coaching,
    and creating lasting behavioral change through personalized support.
    """
    
    def __init__(self, config: Optional[SparkConfig] = None, **kwargs):
        """Initialize SPARK agent with modular architecture."""
        config = config or SparkConfig()
        
        # Store config and initialize prompts first
        self.config = config
        self.prompts = SparkPrompts(personality_type=config.personality_type)
        
        # Get description for initialization
        description = (
            "SPARK is your transformational motivation coach, igniting lasting change "
            "through powerful inspiration and behavioral science. With expertise in "
            "habit formation, mindset transformation, and accountability, SPARK helps "
            "you break through barriers and achieve your full potential."
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
        self._register_spark_skills()
        
        # Define ADK skills for external protocols (A2A compliance)
        self.adk_skills = [
            Skill(
                name="provide_motivation",
                description="Deliver powerful personalized motivation",
                handler=self._adk_provide_motivation
            ),
            Skill(
                name="guide_habit_formation",
                description="Guide sustainable habit formation",
                handler=self._adk_guide_habit_formation
            ),
            Skill(
                name="coach_mindset",
                description="Transform limiting beliefs and mindsets",
                handler=self._adk_coach_mindset
            )
        ]
        
        logger.info("SPARK Motivation Coach initialized (refactored version)")
    
    # ==================== Required Abstract Methods ====================
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of SPARK capabilities."""
        return self.config.capabilities
    
    def get_agent_description(self) -> str:
        """Get SPARK agent description."""
        return (
            "SPARK is your transformational motivation coach, igniting lasting change "
            "through powerful inspiration and behavioral science. With expertise in "
            "habit formation, mindset transformation, and accountability, SPARK helps "
            "you break through barriers and achieve your full potential."
        )
    
    async def process_user_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request with motivational coaching expertise.
        
        Args:
            request: User's input
            context: Request context including emotional state
            
        Returns:
            Motivational coaching response
        """
        try:
            start_time = datetime.now()
            
            # Update state
            self._state["total_interactions"] = self._state.get("total_interactions", 0) + 1
            self._state["last_interaction"] = start_time.isoformat()
            
            # Detect emotional state for adaptive response
            emotional_state = self._detect_emotional_state(request, context)
            context["emotional_state"] = emotional_state
            
            # Check cache
            cache_key = f"spark:{context.get('user_id', 'anonymous')}:{hash(request)}"
            cached_response = await self.get_cached_response(cache_key)
            if cached_response and self.config.enable_response_cache:
                logger.info("Returning cached motivational response")
                return cached_response
            
            # Detect request type
            request_type = self._detect_coaching_request_type(request, context)
            
            # Route to appropriate skill
            skill_response = await self._route_to_coaching_skill(
                request_type,
                request,
                context
            )
            
            # Build final response
            final_response = {
                "success": True,
                "agent": self.agent_id,
                "response": skill_response.get("coaching", ""),
                "data": skill_response.get("data", {}),
                "metadata": {
                    "request_type": request_type,
                    "skill_used": skill_response.get("skill_used"),
                    "execution_time": (datetime.now() - start_time).total_seconds(),
                    "model_used": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "emotional_state": emotional_state,
                    "motivation_style": self.config.motivation_style
                }
            }
            
            # Cache response if enabled
            if self.config.enable_response_cache:
                await self.cache_response(cache_key, final_response, ttl=self.config.cache_ttl)
            
            # Record metrics
            self._metrics["success_count"] = self._metrics.get("success_count", 0) + 1
            self.record_metric("coaching_response_time", final_response["metadata"]["execution_time"])
            
            return final_response
            
        except Exception as e:
            return await self.handle_error(e, {"request": request, "context": context})
    
    # ==================== Skill Registration ====================
    
    def _register_spark_skills(self) -> None:
        """Register SPARK-specific skills."""
        # Motivation boost
        if self.config.enable_motivation_boost:
            self.register_skill(
                "motivation_boost",
                MotivationBoostSkill(self),
                metadata={"category": "motivation", "priority": "high"}
            )
        
        # Habit formation
        if self.config.enable_habit_formation:
            self.register_skill(
                "habit_formation",
                HabitFormationSkill(self),
                metadata={"category": "behavior", "priority": "high"}
            )
        
        # Mindset coaching
        if self.config.enable_mindset_coaching:
            self.register_skill(
                "mindset_coaching",
                MindsetCoachingSkill(self),
                metadata={"category": "mindset", "priority": "high"}
            )
        
        # Accountability check
        if self.config.enable_accountability_check:
            self.register_skill(
                "accountability_check",
                AccountabilityCheckSkill(self),
                metadata={"category": "support", "priority": "medium"}
            )
        
        # Celebration system
        if self.config.enable_celebration_system:
            self.register_skill(
                "celebration_system",
                CelebrationSystemSkill(self),
                metadata={"category": "recognition", "priority": "medium"}
            )
    
    # ==================== Request Routing ====================
    
    def _detect_coaching_request_type(self, request: str, context: Dict[str, Any]) -> str:
        """Detect the type of coaching request."""
        request_lower = request.lower()
        
        # Check for celebration triggers first
        if context.get("achievement_unlocked") or any(term in request_lower for term in ["achieved", "completed", "reached", "success"]):
            return "celebration"
        elif any(term in request_lower for term in ["motivation", "inspire", "energy", "boost", "help me"]):
            return "motivation"
        elif any(term in request_lower for term in ["habit", "routine", "consistency", "daily", "stick to"]):
            return "habit"
        elif any(term in request_lower for term in ["mindset", "believe", "confidence", "fear", "doubt"]):
            return "mindset"
        elif any(term in request_lower for term in ["accountability", "check in", "progress", "committed"]):
            return "accountability"
        else:
            # Default based on emotional state
            if context.get("emotional_state") == "low":
                return "motivation"
            else:
                return "accountability"
    
    async def _route_to_coaching_skill(
        self,
        request_type: str,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route request to appropriate coaching skill."""
        skill_mapping = {
            "motivation": "motivation_boost",
            "habit": "habit_formation",
            "mindset": "mindset_coaching",
            "accountability": "accountability_check",
            "celebration": "celebration_system"
        }
        
        skill_name = skill_mapping.get(request_type, "motivation_boost")
        
        # Check if skill is available
        if skill_name not in self._skills:
            # Fallback to motivation boost
            skill_name = "motivation_boost"
        
        return await self.execute_skill(
            skill_name,
            request={
                "query": request,
                "context": context,
                "user_profile": context.get("user_profile", {}),
                "recent_activity": context.get("recent_activity", {}),
                "emotional_state": context.get("emotional_state", "neutral")
            }
        )
    
    # ==================== Emotional Intelligence ====================
    
    def _detect_emotional_state(self, request: str, context: Dict[str, Any]) -> str:
        """Detect user's emotional state from request."""
        request_lower = request.lower()
        
        # Negative indicators
        negative_words = ["tired", "exhausted", "unmotivated", "struggling", "failed", "can't", "hard", "difficult", "frustrated"]
        positive_words = ["excited", "ready", "pumped", "motivated", "accomplished", "strong", "great", "amazing"]
        
        negative_count = sum(1 for word in negative_words if word in request_lower)
        positive_count = sum(1 for word in positive_words if word in request_lower)
        
        if negative_count > positive_count:
            return "low"
        elif positive_count > negative_count:
            return "high"
        else:
            return "neutral"
    
    # ==================== ADK Protocol Methods (A2A Compliance) ====================
    
    async def _adk_provide_motivation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for motivation delivery."""
        return await self.execute_skill(
            "motivation_boost",
            request={
                "situation": params.get("situation", "general"),
                "intensity": params.get("intensity", "medium"),
                "focus_area": params.get("focus_area", "fitness"),
                "user_state": params.get("emotional_state", "neutral")
            }
        )
    
    async def _adk_guide_habit_formation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for habit formation."""
        return await self.execute_skill(
            "habit_formation",
            request={
                "habit_goal": params.get("habit_goal", ""),
                "current_habits": params.get("current_habits", []),
                "obstacles": params.get("obstacles", []),
                "environment": params.get("environment", {})
            }
        )
    
    async def _adk_coach_mindset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for mindset coaching."""
        return await self.execute_skill(
            "mindset_coaching",
            request={
                "limiting_beliefs": params.get("limiting_beliefs", []),
                "desired_mindset": params.get("desired_mindset", "growth"),
                "current_challenges": params.get("challenges", [])
            }
        )
    
    # ==================== Lifecycle Hooks ====================
    
    async def _agent_startup(self) -> None:
        """SPARK-specific startup tasks."""
        # Initialize motivation systems
        logger.info("SPARK agent starting up - motivation systems ready")
    
    async def _agent_shutdown(self) -> None:
        """SPARK-specific shutdown tasks."""
        # Save coaching insights
        logger.info("SPARK agent shutting down - saving coaching state")