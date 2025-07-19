"""
WAVE Performance Analytics Agent (Refactored)
============================================

This is a refactored version of the WAVE agent using the modular architecture.
Original: ~788 lines → Refactored: ~400 lines (target)

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
from .config import WaveConfig
from .prompts import WavePrompts
from .skills import (
    BiometricsAnalysisSkill,
    RecoveryProtocolSkill,
    PerformanceTrackingSkill,
    InjuryPreventionSkill,
    SleepOptimizationSkill
)

logger = get_logger(__name__)


class WavePerformanceAnalytics(BaseNGXAgent, ADKAgent):
    """
    WAVE - Performance Analytics Agent (Refactored).
    
    IMPORTANT: Inherits from BOTH BaseNGXAgent AND ADKAgent for full ADK/A2A compliance.
    
    Specializes in biometrics analysis, recovery optimization, and performance
    tracking using data-driven insights from wearables and assessments.
    """
    
    def __init__(self, config: Optional[WaveConfig] = None, **kwargs):
        """Initialize WAVE agent with modular architecture."""
        config = config or WaveConfig()
        
        # Store config and initialize prompts first
        self.config = config
        self.prompts = WavePrompts(personality_type=config.personality_type)
        
        # Get description for initialization
        description = (
            "WAVE is your performance analytics specialist, transforming biometric "
            "data into actionable insights. With expertise in recovery science, "
            "performance optimization, and injury prevention, WAVE helps athletes "
            "achieve sustainable peak performance through data-driven strategies."
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
        self._register_wave_skills()
        
        # Define ADK skills for external protocols (A2A compliance)
        self.adk_skills = [
            Skill(
                name="analyze_biometrics",
                description="Analyze biometric data and provide insights",
                handler=self._adk_analyze_biometrics
            ),
            Skill(
                name="generate_recovery_protocol",
                description="Generate personalized recovery protocols",
                handler=self._adk_generate_recovery_protocol
            ),
            Skill(
                name="track_performance",
                description="Track and analyze performance trends",
                handler=self._adk_track_performance
            )
        ]
        
        logger.info("WAVE Performance Analytics initialized (refactored version)")
    
    # ==================== Required Abstract Methods ====================
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of WAVE capabilities."""
        return self.config.capabilities
    
    def get_agent_description(self) -> str:
        """Get WAVE agent description."""
        return (
            "WAVE is your performance analytics specialist, transforming biometric "
            "data into actionable insights. With expertise in recovery science, "
            "performance optimization, and injury prevention, WAVE helps athletes "
            "achieve sustainable peak performance through data-driven strategies."
        )
    
    async def process_user_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request with performance analytics expertise.
        
        Args:
            request: User's input
            context: Request context including biometric data
            
        Returns:
            Analytics response with insights
        """
        try:
            start_time = datetime.now()
            
            # Update state
            self._state["total_interactions"] = self._state.get("total_interactions", 0) + 1
            self._state["last_interaction"] = start_time.isoformat()
            
            # Check cache
            cache_key = f"wave:{context.get('user_id', 'anonymous')}:{hash(request)}"
            cached_response = await self.get_cached_response(cache_key)
            if cached_response and self.config.enable_response_cache:
                logger.info("Returning cached analytics response")
                return cached_response
            
            # Detect request type
            request_type = self._detect_analytics_request_type(request, context)
            
            # Route to appropriate skill
            skill_response = await self._route_to_analytics_skill(
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
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Cache response if enabled
            if self.config.enable_response_cache:
                await self.cache_response(cache_key, final_response, ttl=self.config.cache_ttl)
            
            # Record metrics
            self._metrics["success_count"] = self._metrics.get("success_count", 0) + 1
            self.record_metric("analytics_time", final_response["metadata"]["execution_time"])
            
            return final_response
            
        except Exception as e:
            return await self.handle_error(e, {"request": request, "context": context})
    
    # ==================== Skill Registration ====================
    
    def _register_wave_skills(self) -> None:
        """Register WAVE-specific skills."""
        # Biometrics analysis
        if self.config.enable_biometrics_analysis:
            self.register_skill(
                "biometrics_analysis",
                BiometricsAnalysisSkill(self),
                metadata={"category": "analytics", "priority": "high"}
            )
        
        # Recovery protocols
        if self.config.enable_recovery_protocols:
            self.register_skill(
                "recovery_protocol",
                RecoveryProtocolSkill(self),
                metadata={"category": "recovery", "priority": "high"}
            )
        
        # Performance tracking
        if self.config.enable_performance_tracking:
            self.register_skill(
                "performance_tracking",
                PerformanceTrackingSkill(self),
                metadata={"category": "tracking", "priority": "medium"}
            )
        
        # Injury prevention
        if self.config.enable_injury_prevention:
            self.register_skill(
                "injury_prevention",
                InjuryPreventionSkill(self),
                metadata={"category": "prevention", "priority": "high"}
            )
        
        # Sleep analysis
        if self.config.enable_sleep_analysis:
            self.register_skill(
                "sleep_optimization",
                SleepOptimizationSkill(self),
                metadata={"category": "recovery", "priority": "medium"}
            )
    
    # ==================== Request Routing ====================
    
    def _detect_analytics_request_type(self, request: str, context: Dict[str, Any]) -> str:
        """Detect the type of analytics request."""
        request_lower = request.lower()
        
        if any(term in request_lower for term in ["biometric", "hrv", "heart rate", "readiness"]):
            return "biometrics"
        elif any(term in request_lower for term in ["recovery", "rest", "recuperation", "fatigue"]):
            return "recovery"
        elif any(term in request_lower for term in ["performance", "trend", "progress", "improvement"]):
            return "performance"
        elif any(term in request_lower for term in ["injury", "pain", "prevention", "risk"]):
            return "injury_prevention"
        elif any(term in request_lower for term in ["sleep", "rest quality", "rem", "deep sleep"]):
            return "sleep"
        else:
            return "general_analytics"
    
    async def _route_to_analytics_skill(
        self,
        request_type: str,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route request to appropriate analytics skill."""
        skill_mapping = {
            "biometrics": "biometrics_analysis",
            "recovery": "recovery_protocol",
            "performance": "performance_tracking",
            "injury_prevention": "injury_prevention",
            "sleep": "sleep_optimization",
            "general_analytics": "biometrics_analysis"  # Default
        }
        
        skill_name = skill_mapping.get(request_type, "biometrics_analysis")
        
        # Check if skill is available
        if skill_name not in self._skills:
            # Fallback to biometrics analysis
            skill_name = "biometrics_analysis"
        
        return await self.execute_skill(
            skill_name,
            request={
                "query": request,
                "context": context,
                "biometric_data": context.get("biometric_data", {}),
                "user_profile": context.get("user_profile", {})
            }
        )
    
    # ==================== ADK Protocol Methods (A2A Compliance) ====================
    
    async def _adk_analyze_biometrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for biometrics analysis."""
        return await self.execute_skill(
            "biometrics_analysis",
            request={
                "biometric_data": params.get("biometric_data", {}),
                "analysis_type": params.get("analysis_type", "comprehensive"),
                "time_range": params.get("time_range", "7d")
            }
        )
    
    async def _adk_generate_recovery_protocol(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for recovery protocol generation."""
        return await self.execute_skill(
            "recovery_protocol",
            request={
                "fatigue_level": params.get("fatigue_level", "moderate"),
                "recent_training": params.get("recent_training", {}),
                "recovery_time": params.get("recovery_time", "24h")
            }
        )
    
    async def _adk_track_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for performance tracking."""
        return await self.execute_skill(
            "performance_tracking",
            request={
                "metrics": params.get("metrics", {}),
                "time_period": params.get("time_period", "30d"),
                "comparison_type": params.get("comparison_type", "trend")
            }
        )
    
    # ==================== Lifecycle Hooks ====================
    
    async def _agent_startup(self) -> None:
        """WAVE-specific startup tasks."""
        # Initialize wearable connections if needed
        logger.info("WAVE agent starting up - analytics services ready")
    
    async def _agent_shutdown(self) -> None:
        """WAVE-specific shutdown tasks."""
        # Close any open analytics connections
        logger.info("WAVE agent shutting down - saving analytics state")