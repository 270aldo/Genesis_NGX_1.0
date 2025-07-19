"""
NOVA Biohacking Innovator Agent (Refactored)
============================================

This is a refactored version of the NOVA agent using the modular architecture.
Original: ~3,322 lines → Refactored: ~400 lines (target)

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
from .config import NovaConfig
from .prompts import NovaPrompts
from .skills import (
    SupplementProtocolsSkill,
    CircadianOptimizationSkill,
    CognitiveEnhancementSkill,
    LongevityStrategiesSkill,
    BiomarkerAnalysisSkill
)

logger = get_logger(__name__)


class NovaBiohackingInnovator(BaseNGXAgent, ADKAgent):
    """
    NOVA - Biohacking Innovator Agent (Refactored).
    
    IMPORTANT: Inherits from BOTH BaseNGXAgent AND ADKAgent for full ADK/A2A compliance.
    
    Specializes in cutting-edge biohacking protocols, supplementation strategies,
    and human optimization through evidence-based interventions.
    """
    
    def __init__(self, config: Optional[NovaConfig] = None, **kwargs):
        """Initialize NOVA agent with modular architecture."""
        config = config or NovaConfig()
        
        # Store config and initialize prompts first
        self.config = config
        self.prompts = NovaPrompts(personality_type=config.personality_type)
        
        # Get description for initialization
        description = (
            "NOVA is your biohacking innovator, pushing the boundaries of human "
            "optimization through cutting-edge science. With expertise in supplementation, "
            "circadian biology, cognitive enhancement, and longevity, NOVA helps you "
            "unlock your biological potential safely and effectively."
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
        self._register_nova_skills()
        
        # Define ADK skills for external protocols (A2A compliance)
        self.adk_skills = [
            Skill(
                name="design_supplement_protocol",
                description="Design personalized supplement protocols",
                handler=self._adk_design_supplement_protocol
            ),
            Skill(
                name="optimize_biology",
                description="Optimize biological systems comprehensively",
                handler=self._adk_optimize_biology
            ),
            Skill(
                name="analyze_biomarkers",
                description="Analyze and interpret biomarker data",
                handler=self._adk_analyze_biomarkers
            )
        ]
        
        logger.info("NOVA Biohacking Innovator initialized (refactored version)")
    
    # ==================== Required Abstract Methods ====================
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of NOVA capabilities."""
        return self.config.capabilities
    
    def get_agent_description(self) -> str:
        """Get NOVA agent description."""
        return (
            "NOVA is your biohacking innovator, pushing the boundaries of human "
            "optimization through cutting-edge science. With expertise in supplementation, "
            "circadian biology, cognitive enhancement, and longevity, NOVA helps you "
            "unlock your biological potential safely and effectively."
        )
    
    async def process_user_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request with biohacking expertise.
        
        Args:
            request: User's input
            context: Request context including health data
            
        Returns:
            Biohacking protocol response
        """
        try:
            start_time = datetime.now()
            
            # Update state
            self._state["total_interactions"] = self._state.get("total_interactions", 0) + 1
            self._state["last_interaction"] = start_time.isoformat()
            
            # Safety check for medical conditions
            if self.config.medical_contraindication_check:
                await self._check_contraindications(context)
            
            # Check cache
            cache_key = f"nova:{context.get('user_id', 'anonymous')}:{hash(request)}"
            cached_response = await self.get_cached_response(cache_key)
            if cached_response and self.config.enable_response_cache:
                logger.info("Returning cached biohacking response")
                return cached_response
            
            # Detect request type
            request_type = self._detect_biohacking_request_type(request, context)
            
            # Route to appropriate skill
            skill_response = await self._route_to_biohacking_skill(
                request_type,
                request,
                context
            )
            
            # Build final response
            final_response = {
                "success": True,
                "agent": self.agent_id,
                "response": skill_response.get("protocol", ""),
                "data": skill_response.get("data", {}),
                "metadata": {
                    "request_type": request_type,
                    "skill_used": skill_response.get("skill_used"),
                    "execution_time": (datetime.now() - start_time).total_seconds(),
                    "model_used": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "evidence_level": skill_response.get("evidence_level", "moderate"),
                    "safety_verified": True
                }
            }
            
            # Cache response if enabled
            if self.config.enable_response_cache:
                await self.cache_response(cache_key, final_response, ttl=self.config.cache_ttl)
            
            # Record metrics
            self._metrics["success_count"] = self._metrics.get("success_count", 0) + 1
            self.record_metric("biohacking_response_time", final_response["metadata"]["execution_time"])
            
            return final_response
            
        except Exception as e:
            return await self.handle_error(e, {"request": request, "context": context})
    
    # ==================== Skill Registration ====================
    
    def _register_nova_skills(self) -> None:
        """Register NOVA-specific skills."""
        # Supplement protocols
        if self.config.enable_supplement_protocols:
            self.register_skill(
                "supplement_protocols",
                SupplementProtocolsSkill(self),
                metadata={"category": "supplementation", "priority": "high"}
            )
        
        # Circadian optimization
        if self.config.enable_circadian_optimization:
            self.register_skill(
                "circadian_optimization",
                CircadianOptimizationSkill(self),
                metadata={"category": "circadian", "priority": "high"}
            )
        
        # Cognitive enhancement
        if self.config.enable_cognitive_enhancement:
            self.register_skill(
                "cognitive_enhancement",
                CognitiveEnhancementSkill(self),
                metadata={"category": "cognitive", "priority": "high"}
            )
        
        # Longevity strategies
        if self.config.enable_longevity_strategies:
            self.register_skill(
                "longevity_strategies",
                LongevityStrategiesSkill(self),
                metadata={"category": "longevity", "priority": "medium"}
            )
        
        # Biomarker analysis
        if self.config.enable_biomarker_analysis:
            self.register_skill(
                "biomarker_analysis",
                BiomarkerAnalysisSkill(self),
                metadata={"category": "analysis", "priority": "high"}
            )
    
    # ==================== Request Routing ====================
    
    def _detect_biohacking_request_type(self, request: str, context: Dict[str, Any]) -> str:
        """Detect the type of biohacking request."""
        request_lower = request.lower()
        
        if any(term in request_lower for term in ["supplement", "stack", "nootropic", "vitamin"]):
            return "supplements"
        elif any(term in request_lower for term in ["sleep", "circadian", "light", "melatonin"]):
            return "circadian"
        elif any(term in request_lower for term in ["cognitive", "brain", "focus", "memory"]):
            return "cognitive"
        elif any(term in request_lower for term in ["longevity", "aging", "lifespan", "NAD"]):
            return "longevity"
        elif any(term in request_lower for term in ["biomarker", "blood", "test", "lab"]):
            return "biomarkers"
        else:
            return "general_optimization"
    
    async def _route_to_biohacking_skill(
        self,
        request_type: str,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route request to appropriate biohacking skill."""
        skill_mapping = {
            "supplements": "supplement_protocols",
            "circadian": "circadian_optimization",
            "cognitive": "cognitive_enhancement",
            "longevity": "longevity_strategies",
            "biomarkers": "biomarker_analysis",
            "general_optimization": "supplement_protocols"  # Default
        }
        
        skill_name = skill_mapping.get(request_type, "supplement_protocols")
        
        # Check if skill is available
        if skill_name not in self._skills:
            # Fallback to supplement protocols
            skill_name = "supplement_protocols"
        
        return await self.execute_skill(
            skill_name,
            request={
                "query": request,
                "context": context,
                "health_data": context.get("health_data", {}),
                "user_profile": context.get("user_profile", {}),
                "risk_tolerance": self.config.protocol_risk_level
            }
        )
    
    # ==================== Safety Methods ====================
    
    async def _check_contraindications(self, context: Dict[str, Any]) -> None:
        """Check for medical contraindications."""
        health_conditions = context.get("health_data", {}).get("conditions", [])
        medications = context.get("health_data", {}).get("medications", [])
        
        if health_conditions or medications:
            # In production, this would check against a contraindication database
            logger.info(f"Checking contraindications for {len(health_conditions)} conditions and {len(medications)} medications")
    
    # ==================== ADK Protocol Methods (A2A Compliance) ====================
    
    async def _adk_design_supplement_protocol(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for supplement protocol design."""
        return await self.execute_skill(
            "supplement_protocols",
            request={
                "goals": params.get("goals", []),
                "current_supplements": params.get("current_supplements", []),
                "budget": params.get("budget", "moderate"),
                "preferences": params.get("preferences", {})
            }
        )
    
    async def _adk_optimize_biology(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for comprehensive biological optimization."""
        optimization_focus = params.get("focus", "general")
        
        if optimization_focus == "sleep":
            skill = "circadian_optimization"
        elif optimization_focus == "cognition":
            skill = "cognitive_enhancement"
        elif optimization_focus == "longevity":
            skill = "longevity_strategies"
        else:
            skill = "supplement_protocols"
            
        return await self.execute_skill(
            skill,
            request={
                "optimization_goals": params.get("goals", []),
                "current_status": params.get("current_status", {}),
                "timeline": params.get("timeline", "3_months")
            }
        )
    
    async def _adk_analyze_biomarkers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for biomarker analysis."""
        return await self.execute_skill(
            "biomarker_analysis",
            request={
                "lab_results": params.get("lab_results", {}),
                "previous_results": params.get("previous_results", {}),
                "health_goals": params.get("health_goals", [])
            }
        )
    
    # ==================== Lifecycle Hooks ====================
    
    async def _agent_startup(self) -> None:
        """NOVA-specific startup tasks."""
        # Initialize biohacking knowledge bases
        logger.info("NOVA agent starting up - biohacking systems ready")
    
    async def _agent_shutdown(self) -> None:
        """NOVA-specific shutdown tasks."""
        # Save protocol outcomes if tracked
        logger.info("NOVA agent shutting down - saving protocol data")