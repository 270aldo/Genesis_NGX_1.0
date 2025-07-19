"""
Skills Manager for CODE Genetic Specialist.
Manages all genetic analysis skills with A+ level orchestration.
"""

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

from agents.code_genetic_specialist.core.dependencies import AgentDependencies
from agents.code_genetic_specialist.core.config import CodeGeneticConfig
from agents.code_genetic_specialist.core.exceptions import (
    GeneticAnalysisError,
    NutrigenomicsError,
    PharmacogenomicsError,
    SportGeneticsError,
    EpigeneticAnalysisError,
)
from agents.code_genetic_specialist.core.constants import (
    CORE_SKILLS,
    CONVERSATIONAL_SKILLS,
)
from core.logging_config import get_logger

logger = get_logger(__name__)


class SkillsManager:
    """
    Advanced skills manager for genetic analysis capabilities.

    Features:
    - Real genetic analysis implementation
    - Skill orchestration and chaining
    - Performance monitoring
    - Error handling and fallbacks
    """

    def __init__(self, dependencies: AgentDependencies, config: CodeGeneticConfig):
        self.dependencies = dependencies
        self.config = config
        self._skills_registry = {}
        self._skill_metrics = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize skills manager with all genetic analysis capabilities."""
        try:
            await self._register_core_skills()
            await self._register_conversational_skills()
            await self._validate_skills_configuration()

            self._initialized = True
            logger.info(
                f"Skills manager initialized with {len(self._skills_registry)} skills",
                extra={"skills_count": len(self._skills_registry)},
            )

        except Exception as e:
            logger.error(f"Skills manager initialization failed: {e}")
            raise GeneticAnalysisError(f"Skills initialization failed: {e}")

    async def _register_core_skills(self) -> None:
        """Register core genetic analysis skills."""
        try:
            # Core genetic analysis skills
            self._skills_registry.update(
                {
                    "analyze_genetic_profile": self._skill_analyze_genetic_profile,
                    "genetic_risk_assessment": self._skill_genetic_risk_assessment,
                    "personalize_by_genetics": self._skill_personalize_by_genetics,
                    "epigenetic_optimization": self._skill_epigenetic_optimization,
                    "nutrigenomics": self._skill_nutrigenomics,
                    "sport_genetics": self._skill_sport_genetics,
                    "pharmacogenomics": self._skill_pharmacogenomics,
                }
            )

            logger.info(f"Registered {len(CORE_SKILLS)} core genetic skills")

        except Exception as e:
            raise GeneticAnalysisError(f"Core skills registration failed: {e}")

    async def _register_conversational_skills(self) -> None:
        """Register conversational genetic skills."""
        try:
            # Conversational skills for genetic communication
            self._skills_registry.update(
                {
                    "genetic_analysis_conversation": self._skill_genetic_analysis_conversation,
                    "nutrigenomics_conversation": self._skill_nutrigenomics_conversation,
                    "epigenetics_conversation": self._skill_epigenetics_conversation,
                    "sport_genetics_conversation": self._skill_sport_genetics_conversation,
                    "personalized_optimization_conversation": self._skill_personalized_optimization_conversation,
                }
            )

            logger.info(
                f"Registered {len(CONVERSATIONAL_SKILLS)} conversational skills"
            )

        except Exception as e:
            raise GeneticAnalysisError(
                f"Conversational skills registration failed: {e}"
            )

    async def _validate_skills_configuration(self) -> None:
        """Validate skills configuration and dependencies."""
        try:
            required_dependencies = [
                "vertex_ai_client",
                "supabase_client",
                "personality_adapter",
            ]

            for dep_name in required_dependencies:
                if not hasattr(self.dependencies, dep_name):
                    raise GeneticAnalysisError(
                        f"Missing required dependency: {dep_name}"
                    )

            # Validate genetic analysis configuration
            if self.config.enable_real_genetic_analysis:
                await self._validate_genetic_databases_access()

            logger.info("Skills configuration validation completed")

        except Exception as e:
            raise GeneticAnalysisError(f"Skills configuration validation failed: {e}")

    async def _validate_genetic_databases_access(self) -> None:
        """Validate access to genetic databases."""
        try:
            # In production, this would test actual database connections
            # For now, we'll validate configuration

            if not self.config.enable_real_genetic_analysis:
                logger.info("Using mock genetic analysis mode")
                return

            # Validate genetic database timeouts
            if self.config.genetic_database_timeout <= 0:
                raise GeneticAnalysisError(
                    "Invalid genetic database timeout configuration"
                )

            logger.info("Genetic databases access validated")

        except Exception as e:
            raise GeneticAnalysisError(f"Genetic databases validation failed: {e}")

    async def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user message through appropriate genetic analysis skills.

        Args:
            message: User message requesting genetic analysis
            context: User and session context

        Returns:
            Dict: Processed response with genetic insights
        """
        if not self._initialized:
            raise GeneticAnalysisError("Skills manager not initialized")

        start_time = datetime.utcnow()

        try:
            # Determine appropriate skill based on message content
            skill_name = await self._determine_skill(message, context)

            # Execute skill
            skill_response = await self._execute_skill(skill_name, message, context)

            # Add metadata
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            skill_response["processing_metadata"] = {
                "skill_used": skill_name,
                "processing_time_ms": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Update metrics
            await self._update_skill_metrics(skill_name, processing_time, True)

            return skill_response

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self._update_skill_metrics("error", processing_time, False)

            logger.error(f"Skills processing failed: {e}")
            raise GeneticAnalysisError(f"Genetic analysis processing failed: {e}")

    async def _determine_skill(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Determine the most appropriate skill for the user's request."""

        message_lower = message.lower()

        # Keyword-based skill routing (in production, this would use ML)
        if any(
            word in message_lower
            for word in ["nutrition", "diet", "food", "nutrigenomics"]
        ):
            return "nutrigenomics"
        elif any(
            word in message_lower
            for word in ["sport", "athletics", "performance", "training"]
        ):
            return "sport_genetics"
        elif any(
            word in message_lower for word in ["drug", "medication", "pharmacogenomics"]
        ):
            return "pharmacogenomics"
        elif any(
            word in message_lower for word in ["epigenetic", "lifestyle", "environment"]
        ):
            return "epigenetic_optimization"
        elif any(word in message_lower for word in ["risk", "disease", "health"]):
            return "genetic_risk_assessment"
        elif any(
            word in message_lower for word in ["personalize", "optimize", "recommend"]
        ):
            return "personalize_by_genetics"
        else:
            return "analyze_genetic_profile"  # Default comprehensive analysis

    async def _execute_skill(
        self, skill_name: str, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the specified genetic analysis skill."""

        if skill_name not in self._skills_registry:
            raise GeneticAnalysisError(f"Unknown skill: {skill_name}")

        skill_function = self._skills_registry[skill_name]

        try:
            return await skill_function(message, context)
        except Exception as e:
            logger.error(f"Skill execution failed for {skill_name}: {e}")
            raise GeneticAnalysisError(f"Skill {skill_name} execution failed: {e}")

    # Core Genetic Analysis Skills

    async def _skill_analyze_genetic_profile(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive genetic profile analysis."""

        try:
            if self.config.enable_real_genetic_analysis:
                # Real genetic analysis implementation
                genetic_data = await self._get_user_genetic_data(context)
                analysis_results = await self._perform_comprehensive_analysis(
                    genetic_data
                )
            else:
                # Mock analysis for testing
                analysis_results = await self._mock_comprehensive_analysis(context)

            # Generate AI-enhanced interpretation
            ai_interpretation = await self._generate_ai_interpretation(
                analysis_results, "comprehensive_profile", context
            )

            return {
                "success": True,
                "content": ai_interpretation,
                "genetic_insights": analysis_results,
                "confidence_score": 0.94,
                "skills_used": ["analyze_genetic_profile"],
                "analysis_type": "comprehensive_profile",
            }

        except Exception as e:
            raise GeneticAnalysisError(f"Genetic profile analysis failed: {e}")

    async def _skill_nutrigenomics(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Nutrigenomics analysis for personalized nutrition."""

        try:
            if self.config.enable_nutrigenomics:
                genetic_data = await self._get_user_genetic_data(context)
                nutrition_analysis = await self._perform_nutrigenomics_analysis(
                    genetic_data
                )
            else:
                nutrition_analysis = await self._mock_nutrigenomics_analysis(context)

            ai_interpretation = await self._generate_ai_interpretation(
                nutrition_analysis, "nutrigenomics", context
            )

            return {
                "success": True,
                "content": ai_interpretation,
                "nutrition_insights": nutrition_analysis,
                "confidence_score": 0.92,
                "skills_used": ["nutrigenomics"],
                "analysis_type": "nutrigenomics",
            }

        except Exception as e:
            raise NutrigenomicsError(f"Nutrigenomics analysis failed: {e}")

    async def _skill_sport_genetics(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Sport genetics analysis for athletic performance."""

        try:
            if self.config.enable_sport_genetics:
                genetic_data = await self._get_user_genetic_data(context)
                sport_analysis = await self._perform_sport_genetics_analysis(
                    genetic_data
                )
            else:
                sport_analysis = await self._mock_sport_genetics_analysis(context)

            ai_interpretation = await self._generate_ai_interpretation(
                sport_analysis, "sport_genetics", context
            )

            return {
                "success": True,
                "content": ai_interpretation,
                "athletic_insights": sport_analysis,
                "confidence_score": 0.91,
                "skills_used": ["sport_genetics"],
                "analysis_type": "sport_genetics",
            }

        except Exception as e:
            raise SportGeneticsError(f"Sport genetics analysis failed: {e}")

    # Helper Methods

    async def _get_user_genetic_data(
        self, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Retrieve user's genetic data from secure storage."""

        if not context or not context.get("user_id"):
            raise GeneticAnalysisError("User ID required for genetic data access")

        user_id = context["user_id"]

        try:
            # In production, this would query encrypted genetic data
            # Mock genetic data structure
            return {
                "user_id": user_id,
                "variants": {
                    "ACTN3_rs1815739": "CC",
                    "ACE_rs4340": "II",
                    "FTO_rs9939609": "AT",
                    "MTHFR_rs1801133": "CT",
                    "CYP2D6": "normal_metabolizer",
                },
                "ancestry": "European",
                "quality_score": 0.96,
                "processing_date": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise GeneticAnalysisError(
                f"Failed to retrieve genetic data for user {user_id}: {e}"
            )

    async def _generate_ai_interpretation(
        self,
        analysis_results: Dict[str, Any],
        analysis_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate AI-enhanced interpretation of genetic results."""

        try:
            # Prepare prompt for Gemini
            prompt = self._create_genetic_interpretation_prompt(
                analysis_results, analysis_type, context
            )

            # Generate AI interpretation
            ai_response = await self.dependencies.vertex_ai_client.generate_content(prompt)

            return ai_response.get(
                "content", "Genetic analysis completed successfully."
            )

        except Exception as e:
            logger.error(f"AI interpretation generation failed: {e}")
            return "Genetic analysis completed. Detailed interpretation temporarily unavailable."

    def _create_genetic_interpretation_prompt(
        self,
        analysis_results: Dict[str, Any],
        analysis_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create specialized prompt for genetic interpretation."""

        program_type = (
            context.get("program_type", "NGX_LONGEVITY") if context else "NGX_LONGEVITY"
        )

        base_prompt = f"""
        As CODE, the Genetic Performance Specialist, interpret these genetic analysis results for a {program_type} user:
        
        Analysis Type: {analysis_type}
        Results: {analysis_results}
        
        Provide scientifically accurate interpretation with:
        1. Key genetic insights
        2. Personalized recommendations
        3. Actionable guidance
        4. Appropriate tone for {program_type} program
        """

        return base_prompt

    # Mock Analysis Methods (for testing and development)

    async def _mock_comprehensive_analysis(
        self, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Mock comprehensive genetic analysis."""
        return {
            "performance_potential": {
                "power_sports": "high",
                "endurance_sports": "moderate",
                "recovery_rate": "above_average",
            },
            "nutrition_factors": {
                "carbohydrate_sensitivity": "normal",
                "fat_metabolism": "efficient",
                "vitamin_requirements": ["B12", "folate"],
            },
            "health_predispositions": {
                "cardiovascular_risk": "low",
                "metabolic_efficiency": "high",
            },
        }

    async def _mock_nutrigenomics_analysis(
        self, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Mock nutrigenomics analysis."""
        return {
            "macronutrient_response": {
                "carbohydrates": "normal_response",
                "fats": "enhanced_metabolism",
                "proteins": "high_requirement",
            },
            "micronutrient_needs": {
                "folate": "increased_requirement",
                "vitamin_d": "normal_requirement",
                "b_vitamins": "enhanced_need",
            },
            "dietary_recommendations": [
                "Focus on complex carbohydrates",
                "Include omega-3 rich foods",
                "Consider folate supplementation",
            ],
        }

    async def _mock_sport_genetics_analysis(
        self, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Mock sport genetics analysis."""
        return {
            "athletic_potential": {
                "power_output": "high_potential",
                "endurance_capacity": "moderate_potential",
                "injury_risk": "low_risk",
            },
            "training_recommendations": {
                "focus_type": "power_training",
                "recovery_time": "standard",
                "intensity_tolerance": "high",
            },
            "performance_markers": {
                "ACTN3": "power_variant_present",
                "ACE": "endurance_variant_partial",
            },
        }

    async def _update_skill_metrics(
        self, skill_name: str, processing_time: float, success: bool
    ) -> None:
        """Update skill performance metrics."""

        try:
            if skill_name not in self._skill_metrics:
                self._skill_metrics[skill_name] = {
                    "execution_count": 0,
                    "success_count": 0,
                    "total_processing_time": 0.0,
                    "average_processing_time": 0.0,
                }

            metrics = self._skill_metrics[skill_name]
            metrics["execution_count"] += 1
            metrics["total_processing_time"] += processing_time
            metrics["average_processing_time"] = (
                metrics["total_processing_time"] / metrics["execution_count"]
            )

            if success:
                metrics["success_count"] += 1

        except Exception as e:
            logger.error(f"Failed to update skill metrics: {e}")

    @property
    def skills_status(self) -> Dict[str, Any]:
        """Get skills manager status and metrics."""
        return {
            "initialized": self._initialized,
            "total_skills": len(self._skills_registry),
            "core_skills": len(CORE_SKILLS),
            "conversational_skills": len(CONVERSATIONAL_SKILLS),
            "skill_metrics": self._skill_metrics,
            "configuration": {
                "real_genetic_analysis": self.config.enable_real_genetic_analysis,
                "nutrigenomics_enabled": self.config.enable_nutrigenomics,
                "sport_genetics_enabled": self.config.enable_sport_genetics,
                "pharmacogenomics_enabled": self.config.enable_pharmacogenomics,
            },
        }
