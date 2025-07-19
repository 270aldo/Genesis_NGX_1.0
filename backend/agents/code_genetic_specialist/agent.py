"""
CODE Genetic Specialist Agent (Refactored)
==========================================

This is a refactored version of the CODE agent using the modular architecture.
Original: ~1,909 lines → Refactored: ~400 lines (target)

The functionality is now split into:
- Core agent logic (this file)
- Skills modules (skills/)
- Services (services/)
- Configuration (config.py)
- Prompts (prompts.py)
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
from .config import CodeConfig
from .prompts import CodePrompts
from .skills import (
    GeneticAnalysisSkill,
    NutrigenomicsSkill,
    SportGeneticsSkill,
    EpigeneticOptimizationSkill,
    RiskAssessmentSkill
)
from .services import (
    GeneticSecurityService,
    ConsentManagementService
)

logger = get_logger(__name__)


class CodeGeneticSpecialist(BaseNGXAgent, ADKAgent):
    """
    CODE - Genetic Specialist Agent (Refactored).
    
    Specializes in genetic analysis, personalized medicine, and performance
    optimization based on each user's unique genetic profile.
    """
    
    def __init__(self, config: Optional[CodeConfig] = None, **kwargs):
        """Initialize CODE agent with modular architecture."""
        config = config or CodeConfig()
        
        # Store config and initialize prompts first
        self.config = config
        self.prompts = CodePrompts(personality_type=config.personality_type)
        
        # Get description for initialization
        description = (
            "CODE is your genetic performance specialist, decoding your unique "
            "genetic blueprint to unlock personalized optimization strategies. "
            "With advanced genomics, epigenetics, and nutrigenomics expertise, "
            "CODE transforms your DNA data into actionable health and performance insights."
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
        
        # Initialize CODE-specific services
        self._initialize_services()
        
        # Register skills
        self._register_code_skills()
        
        # Define ADK skills for external protocols
        self.adk_skills = [
            Skill(
                name="analyze_genetic_profile",
                description="Analyze genetic variants and provide insights",
                handler=self._adk_analyze_genetic_profile
            ),
            Skill(
                name="generate_nutrigenomics_plan",
                description="Generate personalized nutrition based on genetics",
                handler=self._adk_generate_nutrigenomics_plan
            )
        ]
        
        logger.info("CODE Genetic Specialist initialized (refactored version)")
    
    # ==================== Required Abstract Methods ====================
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of CODE capabilities."""
        return self.config.capabilities
    
    def get_agent_description(self) -> str:
        """Get CODE agent description."""
        return (
            "CODE is your genetic performance specialist, decoding your unique "
            "genetic blueprint to unlock personalized optimization strategies. "
            "With advanced genomics, epigenetics, and nutrigenomics expertise, "
            "CODE transforms your DNA data into actionable health and performance insights."
        )
    
    async def process_user_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request with genetic expertise.
        
        Args:
            request: User's input
            context: Request context including genetic data
            
        Returns:
            Genetic analysis response
        """
        try:
            start_time = datetime.now()
            
            # Update state
            self._state["total_interactions"] = self._state.get("total_interactions", 0) + 1
            self._state["last_interaction"] = start_time.isoformat()
            
            # Check consent if needed
            if self.config.enforce_consent:
                user_id = context.get("user_id")
                if user_id and not await self._check_genetic_consent(user_id):
                    return await self._handle_consent_required(request, context)
            
            # Check cache
            cache_key = f"code:{context.get('user_id', 'anonymous')}:{hash(request)}"
            cached_response = await self.get_cached_response(cache_key)
            if cached_response and self.config.enable_response_cache:
                logger.info("Returning cached genetic analysis")
                return cached_response
            
            # Detect request type
            request_type = self._detect_genetic_request_type(request, context)
            
            # Route to appropriate skill
            skill_response = await self._route_to_genetic_skill(
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
            self.record_metric("genetic_analysis_time", final_response["metadata"]["execution_time"])
            
            return final_response
            
        except Exception as e:
            return await self.handle_error(e, {"request": request, "context": context})
    
    # ==================== Service Initialization ====================
    
    def _initialize_services(self) -> None:
        """Initialize CODE-specific services."""
        # Import config class from core
        from .core.config import CodeGeneticConfig
        
        # Create config for security service
        genetic_config = CodeGeneticConfig()
        
        # Security service for genetic data protection
        self.security_service = GeneticSecurityService(config=genetic_config)
        
        # Consent management for genetic data
        # In production, this would use real Supabase client
        self.consent_service = ConsentManagementService(supabase_client=None)
    
    # ==================== Skill Registration ====================
    
    def _register_code_skills(self) -> None:
        """Register CODE-specific skills."""
        # Genetic analysis
        self.register_skill(
            "genetic_analysis",
            GeneticAnalysisSkill(self),
            metadata={"category": "analysis", "requires_consent": True}
        )
        
        # Nutrigenomics
        if self.config.enable_nutrigenomics:
            self.register_skill(
                "nutrigenomics",
                NutrigenomicsSkill(self),
                metadata={"category": "nutrition", "requires_consent": True}
            )
        
        # Sport genetics
        if self.config.enable_sport_genetics:
            self.register_skill(
                "sport_genetics",
                SportGeneticsSkill(self),
                metadata={"category": "performance", "requires_consent": True}
            )
        
        # Epigenetic optimization
        if self.config.enable_epigenetics:
            self.register_skill(
                "epigenetic_optimization",
                EpigeneticOptimizationSkill(self),
                metadata={"category": "optimization", "requires_consent": True}
            )
        
        # Risk assessment
        if self.config.enable_risk_assessment:
            self.register_skill(
                "risk_assessment",
                RiskAssessmentSkill(self),
                metadata={"category": "prevention", "requires_consent": True}
            )
    
    # ==================== Request Routing ====================
    
    def _detect_genetic_request_type(self, request: str, context: Dict[str, Any]) -> str:
        """Detect the type of genetic request."""
        request_lower = request.lower()
        
        if any(term in request_lower for term in ["nutrient", "diet", "nutrition", "food"]):
            return "nutrigenomics"
        elif any(term in request_lower for term in ["sport", "athletic", "performance", "training"]):
            return "sport_genetics"
        elif any(term in request_lower for term in ["epigenetic", "expression", "lifestyle"]):
            return "epigenetic"
        elif any(term in request_lower for term in ["risk", "predisposition", "disease"]):
            return "risk_assessment"
        elif any(term in request_lower for term in ["gene", "variant", "snp", "mutation"]):
            return "genetic_analysis"
        else:
            return "general_genetic"
    
    async def _route_to_genetic_skill(
        self,
        request_type: str,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route request to appropriate genetic skill."""
        skill_mapping = {
            "genetic_analysis": "genetic_analysis",
            "nutrigenomics": "nutrigenomics",
            "sport_genetics": "sport_genetics",
            "epigenetic": "epigenetic_optimization",
            "risk_assessment": "risk_assessment",
            "general_genetic": "genetic_analysis"  # Default
        }
        
        skill_name = skill_mapping.get(request_type, "genetic_analysis")
        
        # Check if skill is available
        if skill_name not in self._skills:
            # Fallback to genetic analysis
            skill_name = "genetic_analysis"
        
        return await self.execute_skill(
            skill_name,
            request={
                "query": request,
                "context": context,
                "genetic_data": context.get("genetic_data", {}),
                "user_profile": context.get("user_profile", {})
            }
        )
    
    # ==================== Consent Management ====================
    
    async def _check_genetic_consent(self, user_id: str) -> bool:
        """Check if user has consented to genetic data processing."""
        try:
            # Check if user has valid consent for genetic analysis
            has_consent = await self.consent_service.has_valid_consent(
                user_id, 
                "genetic_analysis"
            )
            return has_consent
        except Exception as e:
            logger.error(f"Error checking consent: {str(e)}")
            return False
    
    async def _handle_consent_required(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case where genetic consent is required."""
        return {
            "success": False,
            "agent": self.agent_id,
            "response": (
                "Para analizar tu información genética, necesito tu consentimiento explícito. "
                "La privacidad de tus datos genéticos es fundamental. "
                "¿Me autorizas a procesar tu información genética para proporcionarte "
                "recomendaciones personalizadas? Puedes revocar este consentimiento en cualquier momento."
            ),
            "metadata": {
                "consent_required": True,
                "consent_type": "genetic_data",
                "privacy_notice": "Tu información genética será encriptada y procesada según GINA y GDPR."
            }
        }
    
    # ==================== ADK Protocol Methods ====================
    
    async def _adk_analyze_genetic_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for genetic analysis."""
        return await self.execute_skill(
            "genetic_analysis",
            request={
                "genetic_data": params.get("genetic_data", {}),
                "analysis_type": params.get("analysis_type", "comprehensive"),
                "user_profile": params.get("user_profile", {})
            }
        )
    
    async def _adk_generate_nutrigenomics_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for nutrigenomics planning."""
        return await self.execute_skill(
            "nutrigenomics",
            request={
                "genetic_data": params.get("genetic_data", {}),
                "dietary_preferences": params.get("dietary_preferences", {}),
                "health_goals": params.get("health_goals", [])
            }
        )
    
    # ==================== Lifecycle Hooks ====================
    
    async def _agent_startup(self) -> None:
        """CODE-specific startup tasks."""
        # Initialize genetic databases if needed
        logger.info("CODE agent starting up - genetic services ready")
    
    async def _agent_shutdown(self) -> None:
        """CODE-specific shutdown tasks."""
        # Ensure all genetic data is properly secured
        logger.info("CODE agent shutting down - securing genetic data")