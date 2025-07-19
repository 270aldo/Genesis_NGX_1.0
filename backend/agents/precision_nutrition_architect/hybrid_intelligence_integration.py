"""
GENESIS NGX Agents - SAGE Hybrid Intelligence Integration
=========================================================

Integration module for the SAGE agent (Precision Nutrition Architect) with the
Hybrid Intelligence Engine. This module provides nutrition-specific personalization
using the two-layer system.

SAGE specializes in:
- Precision nutrition planning
- Nutrigenomics integration
- Meal timing optimization
- Supplement protocols
- Dietary restriction management

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-09
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Import base mixin
from agents.base.hybrid_intelligence_mixin import HybridIntelligenceMixin

# Import hybrid intelligence components
from core.hybrid_intelligence import (
    UserProfile,
    PersonalizationContext,
    PersonalizationResult
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SAGEHybridIntelligenceIntegration(HybridIntelligenceMixin):
    """
    Hybrid Intelligence integration for SAGE (Precision Nutrition Architect)
    
    Provides nutrition-specific adaptations based on:
    - User archetype (PRIME vs LONGEVITY)
    - Physiological state and biomarkers
    - Dietary restrictions and preferences
    - Activity levels and recovery needs
    """
    
    def __init__(self):
        super().__init__()
        self.AGENT_ID = "precision_nutrition_architect"
        logger.info("SAGE Hybrid Intelligence Integration initialized")
    
    def _get_agent_adaptations(self) -> Dict[str, Any]:
        """Get SAGE-specific adaptation configurations"""
        
        return {
            "communication_styles": {
                "direct_performance": "scientific_precise",
                "supportive_educational": "nurturing_educational",
                "analytical": "evidence_based"
            },
            "nutrition_focus": {
                "prime": {
                    "priorities": ["performance_optimization", "muscle_synthesis", "energy_maximization"],
                    "meal_timing": "strategic_performance",
                    "supplement_approach": "aggressive_stacking",
                    "macro_distribution": "performance_oriented"
                },
                "longevity": {
                    "priorities": ["anti_inflammatory", "gut_health", "metabolic_flexibility"],
                    "meal_timing": "circadian_aligned",
                    "supplement_approach": "essential_support",
                    "macro_distribution": "balanced_sustainable"
                }
            },
            "content_delivery": {
                "prime": ["quick_protocols", "performance_metrics", "optimization_tips"],
                "longevity": ["educational_content", "long_term_benefits", "gentle_transitions"]
            },
            "biomarker_interpretations": {
                "inflammation_markers": {
                    "high": "anti_inflammatory_protocol",
                    "moderate": "balanced_approach",
                    "low": "performance_focus"
                },
                "metabolic_markers": {
                    "insulin_sensitivity": "carb_timing_optimization",
                    "lipid_profile": "fat_quality_focus",
                    "glucose_control": "glycemic_management"
                }
            }
        }
    
    async def _get_agent_specific_adaptations(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Get SAGE-specific nutritional adaptations"""
        
        archetype = combined_recs["personalization_metadata"]["archetype"]
        readiness_score = combined_recs["personalization_metadata"]["readiness_score"]
        
        # Get nutrition focus based on archetype
        nutrition_focus = self._agent_adaptations["nutrition_focus"][archetype]
        
        # Adjust based on physiological state
        if readiness_score < 0.5:
            # Low readiness - focus on recovery nutrition
            nutrition_adaptations = {
                "primary_focus": "recovery_nutrition",
                "macro_emphasis": "anti_inflammatory",
                "hydration_priority": "high",
                "supplement_focus": ["adaptogens", "anti_inflammatory", "sleep_support"],
                "meal_complexity": "simplified"
            }
        elif archetype == "prime":
            # PRIME with good readiness
            nutrition_adaptations = {
                "primary_focus": "performance_nutrition",
                "macro_emphasis": "muscle_synthesis",
                "hydration_priority": "performance_hydration",
                "supplement_focus": ["performance_enhancers", "recovery_accelerators", "nootropics"],
                "meal_complexity": "strategic"
            }
        else:  # LONGEVITY
            nutrition_adaptations = {
                "primary_focus": "longevity_nutrition",
                "macro_emphasis": "balanced_sustainable",
                "hydration_priority": "cellular_hydration",
                "supplement_focus": ["antioxidants", "gut_health", "joint_support"],
                "meal_complexity": "moderate"
            }
        
        # Add timing recommendations
        timing_adaptations = self._get_nutrition_timing(combined_recs)
        
        # Add restriction handling
        restriction_adaptations = self._get_restriction_adaptations(combined_recs)
        
        return {
            "nutrition_focus": nutrition_adaptations,
            "timing_strategies": timing_adaptations,
            "restriction_handling": restriction_adaptations,
            "personalization_level": self._determine_personalization_level(readiness_score),
            "communication_approach": self._get_nutrition_communication_style(archetype, readiness_score)
        }
    
    def _get_nutrition_timing(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Get personalized nutrition timing recommendations"""
        
        timing_recs = combined_recs.get("timing_adaptations", {})
        archetype = combined_recs["personalization_metadata"]["archetype"]
        
        if archetype == "prime":
            return {
                "pre_workout": "30-45_minutes_strategic_fuel",
                "post_workout": "immediate_anabolic_window",
                "meal_frequency": "5-6_optimized_doses",
                "fasting_approach": "strategic_performance_fasting",
                "nutrient_timing": "performance_synchronized"
            }
        else:  # longevity
            return {
                "pre_workout": "60-90_minutes_gentle_fuel",
                "post_workout": "within_2_hours_recovery",
                "meal_frequency": "3-4_satisfying_meals",
                "fasting_approach": "circadian_rhythm_fasting",
                "nutrient_timing": "intuitive_sustainable"
            }
    
    def _get_restriction_adaptations(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dietary restrictions with personalization"""
        
        archetype = combined_recs["personalization_metadata"]["archetype"]
        
        if archetype == "prime":
            return {
                "approach": "performance_within_constraints",
                "substitution_strategy": "optimal_alternatives",
                "flexibility": "minimal_compromise",
                "education_level": "quick_swaps"
            }
        else:
            return {
                "approach": "enjoyable_compliance",
                "substitution_strategy": "satisfying_alternatives",
                "flexibility": "gentle_adaptation",
                "education_level": "comprehensive_understanding"
            }
    
    def _determine_personalization_level(self, readiness_score: float) -> str:
        """Determine appropriate personalization level"""
        
        if readiness_score > 0.8:
            return "advanced_precision"
        elif readiness_score > 0.6:
            return "moderate_guidance"
        elif readiness_score > 0.4:
            return "supportive_basics"
        else:
            return "gentle_recovery"
    
    def _get_nutrition_communication_style(self, archetype: str, readiness_score: float) -> Dict[str, Any]:
        """Get nutrition-specific communication style"""
        
        if archetype == "prime":
            return {
                "tone": "scientific_authoritative",
                "detail_level": "precise_metrics",
                "motivation": "performance_gains",
                "examples": "athlete_focused",
                "urgency": "time_efficient"
            }
        else:  # longevity
            return {
                "tone": "supportive_educational",
                "detail_level": "comprehensive_context",
                "motivation": "health_benefits",
                "examples": "lifestyle_focused",
                "urgency": "sustainable_pace"
            }
    
    async def personalize_meal_plan(self, 
                                  user_data: Dict[str, Any],
                                  meal_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Specialized method for meal plan personalization
        
        Args:
            user_data: User profile data
            meal_preferences: Specific meal preferences and requirements
            
        Returns:
            Personalized meal plan with adaptations
        """
        
        # Get base personalization
        personalization = await self.personalize_response(
            user_data=user_data,
            request_type="meal_plan",
            request_content=f"Create meal plan with preferences: {meal_preferences}"
        )
        
        # Add meal-specific adaptations
        if personalization["personalization_applied"]:
            nutrition_focus = personalization["agent_adaptations"]["nutrition_focus"]
            
            meal_adaptations = {
                "meal_structure": self._get_meal_structure(nutrition_focus["primary_focus"]),
                "portion_guidance": self._get_portion_guidance(user_data["archetype"]),
                "recipe_complexity": nutrition_focus["meal_complexity"],
                "shopping_approach": self._get_shopping_approach(user_data["archetype"]),
                "prep_strategies": self._get_prep_strategies(nutrition_focus["meal_complexity"])
            }
            
            personalization["meal_specific_adaptations"] = meal_adaptations
        
        return personalization
    
    def _get_meal_structure(self, primary_focus: str) -> Dict[str, Any]:
        """Get meal structure based on nutrition focus"""
        
        structures = {
            "performance_nutrition": {
                "pattern": "pre_post_workout_centric",
                "macro_timing": "strategic",
                "meal_sizes": "varied_by_activity"
            },
            "recovery_nutrition": {
                "pattern": "anti_inflammatory_focus",
                "macro_timing": "gentle",
                "meal_sizes": "consistent_moderate"
            },
            "longevity_nutrition": {
                "pattern": "circadian_aligned",
                "macro_timing": "balanced",
                "meal_sizes": "satisfying_portions"
            }
        }
        
        return structures.get(primary_focus, structures["longevity_nutrition"])
    
    def _get_portion_guidance(self, archetype: str) -> str:
        """Get portion guidance style based on archetype"""
        
        if archetype == "prime":
            return "precise_macro_tracking"
        else:
            return "intuitive_visual_guides"
    
    def _get_shopping_approach(self, archetype: str) -> str:
        """Get shopping approach based on archetype"""
        
        if archetype == "prime":
            return "efficiency_bulk_prep"
        else:
            return "variety_fresh_focus"
    
    def _get_prep_strategies(self, meal_complexity: str) -> List[str]:
        """Get meal prep strategies based on complexity"""
        
        strategies = {
            "simplified": ["batch_cooking", "minimal_ingredients", "quick_assembly"],
            "moderate": ["weekend_prep", "versatile_components", "frozen_helpers"],
            "strategic": ["precise_portioning", "timed_preparation", "performance_optimization"]
        }
        
        return strategies.get(meal_complexity, strategies["moderate"])
    
    async def personalize_supplement_protocol(self,
                                            user_data: Dict[str, Any],
                                            health_goals: List[str]) -> Dict[str, Any]:
        """
        Specialized method for supplement protocol personalization
        
        Args:
            user_data: User profile data
            health_goals: Specific health and performance goals
            
        Returns:
            Personalized supplement protocol
        """
        
        # Get base personalization
        personalization = await self.personalize_response(
            user_data=user_data,
            request_type="supplement_protocol",
            request_content=f"Create supplement protocol for goals: {health_goals}"
        )
        
        if personalization["personalization_applied"]:
            archetype = user_data.get("archetype", "prime")
            
            supplement_adaptations = {
                "timing_protocol": self._get_supplement_timing(archetype),
                "stacking_approach": self._get_stacking_approach(archetype),
                "quality_standards": self._get_quality_standards(archetype),
                "budget_optimization": self._get_budget_approach(archetype),
                "cycling_strategy": self._get_cycling_strategy(archetype)
            }
            
            personalization["supplement_specific_adaptations"] = supplement_adaptations
        
        return personalization
    
    def _get_supplement_timing(self, archetype: str) -> Dict[str, Any]:
        """Get supplement timing based on archetype"""
        
        if archetype == "prime":
            return {
                "morning": "nootropic_stack",
                "pre_workout": "performance_enhancers",
                "post_workout": "recovery_accelerators",
                "evening": "sleep_optimization"
            }
        else:
            return {
                "morning": "foundational_nutrients",
                "with_meals": "absorption_enhancers",
                "evening": "calming_support"
            }
    
    def _get_stacking_approach(self, archetype: str) -> str:
        """Get supplement stacking approach"""
        
        return "aggressive_synergistic" if archetype == "prime" else "gentle_foundational"
    
    def _get_quality_standards(self, archetype: str) -> str:
        """Get quality standards preference"""
        
        return "performance_grade_premium" if archetype == "prime" else "clean_label_trusted"
    
    def _get_budget_approach(self, archetype: str) -> str:
        """Get budget optimization approach"""
        
        return "roi_performance_focused" if archetype == "prime" else "essential_value_focused"
    
    def _get_cycling_strategy(self, archetype: str) -> str:
        """Get supplement cycling strategy"""
        
        return "strategic_periodization" if archetype == "prime" else "consistent_support"


# Export the integration class
__all__ = ["SAGEHybridIntelligenceIntegration"]