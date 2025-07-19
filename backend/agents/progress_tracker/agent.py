"""
STELLA Progress Tracker Agent (Refactored)
==========================================

This is a refactored version of the STELLA agent using the modular architecture.
Original: ~2,881 lines → Refactored: ~400 lines (target)

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
from .config import StellaConfig
from .prompts import StellaPrompts
from .skills import (
    FitnessProgressSkill,
    BodyCompositionSkill,
    GoalTrackingSkill,
    NutritionComplianceSkill,
    StreakTrackingSkill
)

logger = get_logger(__name__)


class ProgressTracker(BaseNGXAgent, ADKAgent):
    """
    STELLA - Progress Tracker Agent (Refactored).
    
    IMPORTANT: Inherits from BOTH BaseNGXAgent AND ADKAgent for full ADK/A2A compliance.
    
    Specializes in tracking, analyzing, and visualizing user progress across
    fitness, nutrition, and body composition goals.
    """
    
    def __init__(self, config: Optional[StellaConfig] = None, **kwargs):
        """Initialize STELLA agent with modular architecture."""
        config = config or StellaConfig()
        
        # Store config and initialize prompts first
        self.config = config
        self.prompts = StellaPrompts(personality_type=config.personality_type)
        
        # Get description for initialization
        description = (
            "STELLA is your dedicated progress tracker, transforming your fitness "
            "journey into measurable achievements. With expertise in data analysis, "
            "goal tracking, and motivational insights, STELLA helps you stay on "
            "track and celebrate every milestone along your transformation."
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
        self._register_stella_skills()
        
        # Define ADK skills for external protocols (A2A compliance)
        self.adk_skills = [
            Skill(
                name="analyze_progress",
                description="Analyze comprehensive fitness progress",
                handler=self._adk_analyze_progress
            ),
            Skill(
                name="track_goals",
                description="Track and analyze goal achievement",
                handler=self._adk_track_goals
            ),
            Skill(
                name="generate_insights",
                description="Generate motivational progress insights",
                handler=self._adk_generate_insights
            )
        ]
        
        logger.info("STELLA Progress Tracker initialized (refactored version)")
    
    # ==================== Required Abstract Methods ====================
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of STELLA capabilities."""
        return self.config.capabilities
    
    def get_agent_description(self) -> str:
        """Get STELLA agent description."""
        return (
            "STELLA is your dedicated progress tracker, transforming your fitness "
            "journey into measurable achievements. With expertise in data analysis, "
            "goal tracking, and motivational insights, STELLA helps you stay on "
            "track and celebrate every milestone along your transformation."
        )
    
    async def process_user_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request with progress tracking expertise.
        
        Args:
            request: User's input
            context: Request context including progress data
            
        Returns:
            Progress analysis response
        """
        try:
            start_time = datetime.now()
            
            # Update state
            self._state["total_interactions"] = self._state.get("total_interactions", 0) + 1
            self._state["last_interaction"] = start_time.isoformat()
            
            # Check cache
            cache_key = f"stella:{context.get('user_id', 'anonymous')}:{hash(request)}"
            cached_response = await self.get_cached_response(cache_key)
            if cached_response and self.config.enable_response_cache:
                logger.info("Returning cached progress analysis")
                return cached_response
            
            # Detect request type
            request_type = self._detect_progress_request_type(request, context)
            
            # Route to appropriate skill
            skill_response = await self._route_to_progress_skill(
                request_type,
                request,
                context
            )
            
            # Build final response
            final_response = {
                "success": True,
                "agent": self.agent_id,
                "response": skill_response.get("analysis", ""),
                "data": skill_response.get("data", {}),
                "metadata": {
                    "request_type": request_type,
                    "skill_used": skill_response.get("skill_used"),
                    "execution_time": (datetime.now() - start_time).total_seconds(),
                    "model_used": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "progress_period": context.get("period", "30d")
                }
            }
            
            # Cache response if enabled
            if self.config.enable_response_cache:
                await self.cache_response(cache_key, final_response, ttl=self.config.cache_ttl)
            
            # Record metrics
            self._metrics["success_count"] = self._metrics.get("success_count", 0) + 1
            self.record_metric("progress_analysis_time", final_response["metadata"]["execution_time"])
            
            return final_response
            
        except Exception as e:
            return await self.handle_error(e, {"request": request, "context": context})
    
    # ==================== Skill Registration ====================
    
    def _register_stella_skills(self) -> None:
        """Register STELLA-specific skills."""
        # Fitness progress tracking
        if self.config.enable_fitness_tracking:
            self.register_skill(
                "fitness_progress",
                FitnessProgressSkill(self),
                metadata={"category": "tracking", "priority": "high"}
            )
        
        # Body composition analysis
        if self.config.enable_body_composition:
            self.register_skill(
                "body_composition",
                BodyCompositionSkill(self),
                metadata={"category": "analysis", "priority": "high"}
            )
        
        # Goal tracking
        if self.config.enable_goal_management:
            self.register_skill(
                "goal_tracking",
                GoalTrackingSkill(self),
                metadata={"category": "goals", "priority": "high"}
            )
        
        # Nutrition compliance
        if self.config.enable_nutrition_monitoring:
            self.register_skill(
                "nutrition_compliance",
                NutritionComplianceSkill(self),
                metadata={"category": "nutrition", "priority": "medium"}
            )
        
        # Streak tracking
        if self.config.enable_streak_tracking:
            self.register_skill(
                "streak_tracking",
                StreakTrackingSkill(self),
                metadata={"category": "consistency", "priority": "medium"}
            )
    
    # ==================== Request Routing ====================
    
    def _detect_progress_request_type(self, request: str, context: Dict[str, Any]) -> str:
        """Detect the type of progress request."""
        request_lower = request.lower()
        
        if any(term in request_lower for term in ["fitness", "workout", "strength", "performance"]):
            return "fitness"
        elif any(term in request_lower for term in ["body", "weight", "composition", "measurements"]):
            return "body_composition"
        elif any(term in request_lower for term in ["goal", "target", "achievement", "milestone"]):
            return "goals"
        elif any(term in request_lower for term in ["nutrition", "diet", "calories", "macros"]):
            return "nutrition"
        elif any(term in request_lower for term in ["streak", "consistency", "adherence", "routine"]):
            return "streaks"
        else:
            return "general_progress"
    
    async def _route_to_progress_skill(
        self,
        request_type: str,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route request to appropriate progress skill."""
        skill_mapping = {
            "fitness": "fitness_progress",
            "body_composition": "body_composition",
            "goals": "goal_tracking",
            "nutrition": "nutrition_compliance",
            "streaks": "streak_tracking",
            "general_progress": "fitness_progress"  # Default
        }
        
        skill_name = skill_mapping.get(request_type, "fitness_progress")
        
        # Check if skill is available
        if skill_name not in self._skills:
            # Fallback to fitness progress
            skill_name = "fitness_progress"
        
        return await self.execute_skill(
            skill_name,
            request={
                "query": request,
                "context": context,
                "progress_data": context.get("progress_data", {}),
                "user_profile": context.get("user_profile", {}),
                "time_period": context.get("period", "30d")
            }
        )
    
    # ==================== Progress Analysis Methods ====================
    
    def _calculate_progress_percentage(self, current: float, start: float, goal: float) -> float:
        """Calculate progress percentage towards goal."""
        if goal == start:
            return 100.0 if current == goal else 0.0
        
        progress = ((current - start) / (goal - start)) * 100
        return max(0.0, min(100.0, progress))
    
    def _identify_trends(self, data_points: List[Dict[str, Any]]) -> str:
        """Identify trends in progress data."""
        if len(data_points) < 2:
            return "insufficient_data"
        
        # Simple trend analysis
        recent = data_points[-5:] if len(data_points) >= 5 else data_points
        values = [p.get("value", 0) for p in recent]
        
        if all(values[i] >= values[i-1] for i in range(1, len(values))):
            return "improving"
        elif all(values[i] <= values[i-1] for i in range(1, len(values))):
            return "declining"
        else:
            return "variable"
    
    # ==================== ADK Protocol Methods (A2A Compliance) ====================
    
    async def _adk_analyze_progress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for progress analysis."""
        return await self.execute_skill(
            "fitness_progress",
            request={
                "progress_data": params.get("progress_data", {}),
                "time_period": params.get("time_period", "30d"),
                "metrics": params.get("metrics", ["all"])
            }
        )
    
    async def _adk_track_goals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for goal tracking."""
        return await self.execute_skill(
            "goal_tracking",
            request={
                "goals": params.get("goals", []),
                "current_values": params.get("current_values", {}),
                "start_values": params.get("start_values", {})
            }
        )
    
    async def _adk_generate_insights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for insight generation."""
        # Combine multiple skills for comprehensive insights
        progress_type = params.get("insight_type", "comprehensive")
        
        if progress_type == "fitness":
            skill = "fitness_progress"
        elif progress_type == "body":
            skill = "body_composition"
        else:
            skill = "fitness_progress"
            
        return await self.execute_skill(
            skill,
            request={
                "data": params.get("data", {}),
                "focus": "insights",
                "motivational": True
            }
        )
    
    # ==================== Lifecycle Hooks ====================
    
    async def _agent_startup(self) -> None:
        """STELLA-specific startup tasks."""
        # Initialize progress tracking systems
        logger.info("STELLA agent starting up - progress tracking ready")
    
    async def _agent_shutdown(self) -> None:
        """STELLA-specific shutdown tasks."""
        # Save any pending progress data
        logger.info("STELLA agent shutting down - saving progress state")