"""
GENESIS NGX Agents - NOVA Hybrid Intelligence Integration
========================================================

Integration module for the NOVA agent (Biohacking Innovator) with the
Hybrid Intelligence Engine. This module provides biohacking-specific personalization
using the two-layer system.

NOVA specializes in:
- Advanced biohacking protocols
- Cutting-edge optimization techniques
- Experimental wellness approaches
- Technology-enhanced performance
- Innovative recovery methods

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


class NOVAHybridIntelligenceIntegration(HybridIntelligenceMixin):
    """
    Hybrid Intelligence integration for NOVA (Biohacking Innovator)
    
    Provides biohacking-specific adaptations based on:
    - User archetype (PRIME vs LONGEVITY)
    - Risk tolerance for experimental protocols
    - Technology adoption preferences
    - Optimization aggressiveness levels
    """
    
    def __init__(self):
        super().__init__()
        self.AGENT_ID = "nova_biohacking_innovator"
        logger.info("NOVA Hybrid Intelligence Integration initialized")
    
    def _get_agent_adaptations(self) -> Dict[str, Any]:
        """Get NOVA-specific adaptation configurations"""
        
        return {
            "communication_styles": {
                "direct_performance": "cutting_edge_technical",
                "supportive_educational": "innovative_explanatory",
                "analytical": "research_backed_detailed"
            },
            "biohacking_approach": {
                "prime": {
                    "priorities": ["performance_enhancement", "competitive_edge", "rapid_optimization"],
                    "risk_tolerance": "high_experimental",
                    "protocol_intensity": "aggressive_stacking",
                    "technology_adoption": "early_adopter",
                    "innovation_level": "cutting_edge"
                },
                "longevity": {
                    "priorities": ["health_optimization", "sustainable_enhancement", "preventive_care"],
                    "risk_tolerance": "conservative_proven",
                    "protocol_intensity": "gentle_progressive",
                    "technology_adoption": "validated_tools",
                    "innovation_level": "evidence_based"
                }
            },
            "protocol_categories": {
                "prime": {
                    "tier_1": ["cold_therapy", "heat_therapy", "light_therapy", "breathwork"],
                    "tier_2": ["nootropics", "peptides", "red_light", "compression"],
                    "tier_3": ["electromagnetic", "hyperbaric", "cryotherapy", "infrared_sauna"]
                },
                "longevity": {
                    "tier_1": ["meditation", "gentle_cold", "circadian_lighting", "basic_breathwork"],
                    "tier_2": ["natural_supplements", "grounding", "forest_bathing", "aromatherapy"],
                    "tier_3": ["gentle_heat", "sound_therapy", "color_therapy", "energy_work"]
                }
            },
            "technology_preferences": {
                "prime": ["wearable_optimization", "smart_recovery", "performance_tracking", "ai_coaching"],
                "longevity": ["wellness_monitoring", "gentle_feedback", "mindfulness_apps", "health_tracking"]
            },
            "safety_protocols": {
                "prime": "calculated_risks",
                "longevity": "maximum_safety"
            }
        }
    
    async def _get_agent_specific_adaptations(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Get NOVA-specific biohacking adaptations"""
        
        archetype = combined_recs["personalization_metadata"]["archetype"]
        readiness_score = combined_recs["personalization_metadata"]["readiness_score"]
        age_factor = combined_recs["personalization_metadata"]["age_factor"]
        
        # Get biohacking approach based on archetype
        biohacking_approach = self._agent_adaptations["biohacking_approach"][archetype]
        
        # Adapt protocol selection based on physiological state and age
        protocol_selection = self._determine_protocol_selection(archetype, readiness_score, age_factor)
        
        # Get risk management approach
        risk_management = self._get_risk_management_approach(archetype, readiness_score)
        
        # Get technology integration level
        tech_integration = self._get_technology_integration(archetype, readiness_score)
        
        return {
            "biohacking_strategy": {
                "approach": biohacking_approach["priorities"],
                "intensity_level": self._calculate_intensity_level(archetype, readiness_score),
                "risk_tolerance": biohacking_approach["risk_tolerance"],
                "innovation_readiness": biohacking_approach["innovation_level"]
            },
            "protocol_selection": protocol_selection,
            "risk_management": risk_management,
            "technology_integration": tech_integration,
            "education_approach": self._get_education_approach(archetype),
            "monitoring_requirements": self._get_monitoring_requirements(archetype, readiness_score),
            "progression_strategy": self._get_progression_strategy(archetype)
        }
    
    def _determine_protocol_selection(self, archetype: str, readiness_score: float, age_factor: Dict[str, Any]) -> Dict[str, Any]:
        """Determine appropriate biohacking protocol selection"""
        
        protocol_categories = self._agent_adaptations["protocol_categories"][archetype]
        
        # Adjust based on readiness and age
        if readiness_score > 0.8 and age_factor["intensity"] > 0.8:
            available_tiers = ["tier_1", "tier_2", "tier_3"]
        elif readiness_score > 0.6 and age_factor["intensity"] > 0.6:
            available_tiers = ["tier_1", "tier_2"]
        else:
            available_tiers = ["tier_1"]
        
        selected_protocols = []
        for tier in available_tiers:
            selected_protocols.extend(protocol_categories[tier])
        
        return {
            "available_protocols": selected_protocols,
            "recommended_start": protocol_categories["tier_1"],
            "progression_path": available_tiers,
            "safety_modifications": self._get_safety_modifications(archetype, readiness_score)
        }
    
    def _calculate_intensity_level(self, archetype: str, readiness_score: float) -> str:
        """Calculate appropriate biohacking intensity level"""
        
        if archetype == "prime":
            if readiness_score > 0.8:
                return "high_intensity_optimization"
            elif readiness_score > 0.6:
                return "moderate_enhancement"
            else:
                return "recovery_focused"
        else:  # longevity
            if readiness_score > 0.7:
                return "gentle_optimization"
            elif readiness_score > 0.4:
                return "maintenance_enhancement"
            else:
                return "restorative_support"
    
    def _get_risk_management_approach(self, archetype: str, readiness_score: float) -> Dict[str, Any]:
        """Get risk management approach for biohacking protocols"""
        
        if archetype == "prime":
            return {
                "risk_assessment": "calculated_experimental",
                "monitoring_level": "high_frequency",
                "safety_protocols": "performance_oriented",
                "adjustment_speed": "rapid_optimization",
                "emergency_protocols": "immediate_response"
            }
        else:  # longevity
            return {
                "risk_assessment": "conservative_proven",
                "monitoring_level": "gentle_tracking",
                "safety_protocols": "maximum_safety",
                "adjustment_speed": "gradual_adaptation",
                "emergency_protocols": "comprehensive_support"
            }
    
    def _get_technology_integration(self, archetype: str, readiness_score: float) -> Dict[str, Any]:
        """Get technology integration preferences"""
        
        tech_preferences = self._agent_adaptations["technology_preferences"][archetype]
        
        return {
            "preferred_technologies": tech_preferences,
            "adoption_speed": "early_adopter" if archetype == "prime" else "validated_follower",
            "complexity_tolerance": "high" if archetype == "prime" else "moderate",
            "integration_level": "deep_optimization" if archetype == "prime" else "gentle_enhancement",
            "data_granularity": "detailed_tracking" if archetype == "prime" else "trend_focused"
        }
    
    def _get_education_approach(self, archetype: str) -> Dict[str, Any]:
        """Get education and learning approach"""
        
        if archetype == "prime":
            return {
                "style": "technical_deep_dive",
                "pace": "rapid_learning",
                "focus": "optimization_science",
                "format": "research_papers_protocols",
                "depth": "mechanism_understanding"
            }
        else:  # longevity
            return {
                "style": "gentle_explanatory",
                "pace": "comfortable_learning",
                "focus": "wellness_benefits",
                "format": "stories_testimonials",
                "depth": "practical_application"
            }
    
    def _get_monitoring_requirements(self, archetype: str, readiness_score: float) -> Dict[str, Any]:
        """Get monitoring requirements for biohacking protocols"""
        
        if archetype == "prime":
            return {
                "frequency": "continuous_optimization",
                "metrics": ["performance_markers", "biomarkers", "recovery_metrics"],
                "tools": ["advanced_wearables", "lab_testing", "subjective_tracking"],
                "adjustments": "real_time_optimization"
            }
        else:  # longevity
            return {
                "frequency": "regular_check_ins",
                "metrics": ["wellness_indicators", "energy_levels", "mood_tracking"],
                "tools": ["simple_wearables", "periodic_testing", "journal_tracking"],
                "adjustments": "gradual_refinement"
            }
    
    def _get_progression_strategy(self, archetype: str) -> Dict[str, Any]:
        """Get progression strategy for biohacking journey"""
        
        if archetype == "prime":
            return {
                "approach": "aggressive_stacking",
                "timeline": "rapid_progression",
                "complexity_growth": "exponential",
                "goal_orientation": "performance_peaks",
                "adaptation_speed": "fast_iteration"
            }
        else:  # longevity
            return {
                "approach": "gentle_building",
                "timeline": "steady_progression",
                "complexity_growth": "linear",
                "goal_orientation": "sustainable_wellness",
                "adaptation_speed": "comfortable_pace"
            }
    
    def _get_safety_modifications(self, archetype: str, readiness_score: float) -> List[str]:
        """Get safety modifications based on archetype and state"""
        
        modifications = []
        
        if archetype == "longevity":
            modifications.extend(["gentle_introduction", "extended_adaptation", "conservative_dosing"])
        
        if readiness_score < 0.6:
            modifications.extend(["reduced_intensity", "increased_monitoring", "recovery_focus"])
        
        return modifications
    
    async def personalize_biohacking_protocol(self,
                                            user_data: Dict[str, Any],
                                            protocol_type: str,
                                            experience_level: str) -> Dict[str, Any]:
        """
        Specialized method for biohacking protocol personalization
        
        Args:
            user_data: User profile data
            protocol_type: Type of biohacking protocol (cold_therapy, nootropics, etc.)
            experience_level: User's experience level (beginner, intermediate, advanced)
            
        Returns:
            Personalized biohacking protocol
        """
        
        # Get base personalization
        personalization = await self.personalize_response(
            user_data=user_data,
            request_type="biohacking_protocol",
            request_content=f"Design {protocol_type} protocol for {experience_level} level"
        )
        
        if personalization["personalization_applied"]:
            archetype = user_data.get("archetype", "prime")
            
            protocol_config = {
                "protocol_design": self._design_protocol(protocol_type, archetype, experience_level),
                "implementation_strategy": self._get_implementation_strategy(archetype),
                "monitoring_plan": self._get_protocol_monitoring(protocol_type, archetype),
                "safety_guidelines": self._get_protocol_safety(protocol_type, archetype),
                "progression_plan": self._get_protocol_progression(protocol_type, archetype, experience_level)
            }
            
            personalization["protocol_specific_adaptations"] = protocol_config
        
        return personalization
    
    def _design_protocol(self, protocol_type: str, archetype: str, experience_level: str) -> Dict[str, Any]:
        """Design specific biohacking protocol"""
        
        # Protocol templates based on type and archetype
        protocol_designs = {
            "cold_therapy": {
                "prime": {
                    "beginner": {"duration": "2-3 min", "temp": "50-55°F", "frequency": "daily"},
                    "intermediate": {"duration": "5-8 min", "temp": "45-50°F", "frequency": "daily"},
                    "advanced": {"duration": "10-15 min", "temp": "39-45°F", "frequency": "twice_daily"}
                },
                "longevity": {
                    "beginner": {"duration": "30-60 sec", "temp": "55-60°F", "frequency": "3x_week"},
                    "intermediate": {"duration": "2-3 min", "temp": "50-55°F", "frequency": "daily"},
                    "advanced": {"duration": "5-8 min", "temp": "45-50°F", "frequency": "daily"}
                }
            },
            "breathwork": {
                "prime": {
                    "beginner": {"technique": "box_breathing", "duration": "10 min", "frequency": "daily"},
                    "intermediate": {"technique": "wim_hof", "duration": "20 min", "frequency": "daily"},
                    "advanced": {"technique": "advanced_pranayama", "duration": "30 min", "frequency": "twice_daily"}
                },
                "longevity": {
                    "beginner": {"technique": "gentle_breathing", "duration": "5 min", "frequency": "daily"},
                    "intermediate": {"technique": "coherent_breathing", "duration": "15 min", "frequency": "daily"},
                    "advanced": {"technique": "varied_techniques", "duration": "25 min", "frequency": "daily"}
                }
            }
        }
        
        return protocol_designs.get(protocol_type, {}).get(archetype, {}).get(experience_level, {})
    
    def _get_implementation_strategy(self, archetype: str) -> Dict[str, Any]:
        """Get implementation strategy for biohacking protocol"""
        
        if archetype == "prime":
            return {
                "introduction_pace": "rapid_integration",
                "schedule_approach": "optimized_timing",
                "consistency_strategy": "performance_driven",
                "adjustment_method": "data_guided_optimization"
            }
        else:  # longevity
            return {
                "introduction_pace": "gentle_integration",
                "schedule_approach": "lifestyle_compatible",
                "consistency_strategy": "habit_building",
                "adjustment_method": "comfort_guided_adaptation"
            }
    
    def _get_protocol_monitoring(self, protocol_type: str, archetype: str) -> Dict[str, Any]:
        """Get monitoring plan for specific protocol"""
        
        monitoring_templates = {
            "cold_therapy": {
                "metrics": ["core_temperature", "heart_rate_variability", "mood_energy"],
                "tools": ["thermometer", "hrv_monitor", "subjective_scale"],
                "frequency": "pre_post_session"
            },
            "breathwork": {
                "metrics": ["heart_rate", "stress_markers", "focus_clarity"],
                "tools": ["pulse_monitor", "stress_app", "journal"],
                "frequency": "daily_tracking"
            }
        }
        
        base_monitoring = monitoring_templates.get(protocol_type, {})
        
        if archetype == "prime":
            base_monitoring["detail_level"] = "comprehensive"
            base_monitoring["automation"] = "high"
        else:
            base_monitoring["detail_level"] = "essential"
            base_monitoring["automation"] = "minimal"
        
        return base_monitoring
    
    def _get_protocol_safety(self, protocol_type: str, archetype: str) -> List[str]:
        """Get safety guidelines for specific protocol"""
        
        safety_guidelines = {
            "cold_therapy": [
                "gradual_temperature_reduction",
                "monitor_extremities",
                "avoid_if_cardiovascular_issues",
                "warm_up_protocol_post"
            ],
            "breathwork": [
                "practice_seated_position",
                "stop_if_dizzy",
                "avoid_if_pregnant",
                "start_with_guidance"
            ]
        }
        
        base_safety = safety_guidelines.get(protocol_type, [])
        
        if archetype == "longevity":
            base_safety.extend(["extra_conservative_approach", "medical_clearance_recommended"])
        
        return base_safety
    
    def _get_protocol_progression(self, protocol_type: str, archetype: str, current_level: str) -> Dict[str, Any]:
        """Get progression plan for protocol"""
        
        progression_levels = ["beginner", "intermediate", "advanced", "expert"]
        current_index = progression_levels.index(current_level) if current_level in progression_levels else 0
        
        if archetype == "prime":
            progression_timeline = "4-6_weeks_per_level"
            progression_criteria = "performance_metrics_achievement"
        else:
            progression_timeline = "8-12_weeks_per_level"
            progression_criteria = "comfort_and_consistency"
        
        next_level = progression_levels[min(current_index + 1, len(progression_levels) - 1)]
        
        return {
            "current_level": current_level,
            "next_level": next_level,
            "progression_timeline": progression_timeline,
            "progression_criteria": progression_criteria,
            "milestone_markers": self._get_milestone_markers(protocol_type, next_level)
        }
    
    def _get_milestone_markers(self, protocol_type: str, target_level: str) -> List[str]:
        """Get milestone markers for progression"""
        
        milestones = {
            "cold_therapy": {
                "intermediate": ["comfortable_2min", "no_shivering", "controlled_breathing"],
                "advanced": ["comfortable_5min", "mental_clarity", "recovery_benefits"],
                "expert": ["comfortable_10min+", "performance_enhancement", "teaching_others"]
            },
            "breathwork": {
                "intermediate": ["20_rounds_comfortable", "breath_control", "stress_reduction"],
                "advanced": ["advanced_techniques", "emotional_regulation", "peak_states"],
                "expert": ["mastery_multiple_techniques", "teaching_capability", "integration_lifestyle"]
            }
        }
        
        return milestones.get(protocol_type, {}).get(target_level, [])


# Export the integration class
__all__ = ["NOVAHybridIntelligenceIntegration"]