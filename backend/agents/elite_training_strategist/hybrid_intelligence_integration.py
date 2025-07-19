"""
GENESIS NGX Agents - BLAZE Hybrid Intelligence Integration
=========================================================

Integration module for the BLAZE agent (Elite Training Strategist) with the
new Hybrid Intelligence Engine. This module replaces the PersonalityAdapter
integration with the revolutionary two-layer personalization system.

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-09
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging

# Import hybrid intelligence components
from core.hybrid_intelligence import (
    HybridIntelligenceEngine,
    UserProfile,
    PersonalizationContext,
    PersonalizationResult,
    UserArchetype,
    PersonalizationMode
)

# Import data models
from core.hybrid_intelligence.models import (
    UserProfileData,
    PersonalizationContextData,
    HybridIntelligenceRequest,
    HybridIntelligenceResponse,
    UserBiometrics,
    WorkoutData,
    WorkoutIntensity,
    FitnessLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BLAZEHybridIntelligenceIntegration:
    """
    Integration layer between BLAZE agent and Hybrid Intelligence Engine
    
    This class handles:
    - User profile data transformation
    - Context preparation for personalization
    - Personalization result application
    - Learning feedback integration
    """
    
    def __init__(self, hybrid_engine: Optional[HybridIntelligenceEngine] = None):
        self.hybrid_engine = hybrid_engine or HybridIntelligenceEngine()
        self.agent_type = "elite_training_strategist"
        
        # BLAZE-specific personalization mappings
        self.blaze_adaptations = {
            "communication_styles": {
                "direct_performance": "motivational_direct",
                "supportive_educational": "encouraging_educational",
                "analytical": "data_driven_coaching"
            },
            "training_intensities": {
                "high_performance": {"base": 0.85, "max": 1.0},
                "sustainable_moderate": {"base": 0.65, "max": 0.85},
                "recovery_focus": {"base": 0.3, "max": 0.6}
            },
            "content_delivery": {
                "advanced_metrics": "performance_data_rich",
                "educational": "educational_progressive",
                "simplified": "basic_motivational"
            }
        }
        
        logger.info("BLAZE Hybrid Intelligence Integration initialized")
    
    async def personalize_training_response(self, 
                                          user_data: Dict[str, Any],
                                          request_type: str,
                                          request_content: str,
                                          session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main method to personalize BLAZE training responses using Hybrid Intelligence
        
        Args:
            user_data: User profile and biometric data
            request_type: Type of training request (plan, analysis, adaptation, etc.)
            request_content: Specific content of the request
            session_context: Current session context
            
        Returns:
            Personalized training response with adaptations
        """
        try:
            # Transform user data to hybrid intelligence format
            user_profile = await self._transform_user_data(user_data)
            
            # Create personalization context
            context = PersonalizationContext(
                user_profile=user_profile,
                agent_type=self.agent_type,
                request_type=request_type,
                request_content=request_content,
                session_context=session_context or {}
            )
            
            # Get personalization from hybrid engine
            personalization_result = await self.hybrid_engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply personalization to BLAZE response
            personalized_response = await self._apply_blaze_personalization(
                personalization_result,
                request_type,
                request_content
            )
            
            logger.info(f"BLAZE personalization complete. Confidence: {personalization_result.confidence_score:.2f}")
            
            return personalized_response
            
        except Exception as e:
            logger.error(f"BLAZE personalization failed: {str(e)}")
            # Return fallback response
            return await self._generate_fallback_response(request_type, request_content)
    
    async def _transform_user_data(self, user_data: Dict[str, Any]) -> UserProfile:
        """Transform user data to UserProfile format"""
        
        # Extract basic profile data
        archetype = UserArchetype.PRIME if user_data.get("archetype", "prime") == "prime" else UserArchetype.LONGEVITY
        
        # Create UserProfile with BLAZE-specific data
        user_profile = UserProfile(
            user_id=user_data.get("user_id", "unknown"),
            archetype=archetype,
            age=user_data.get("age", 30),
            gender=user_data.get("gender", "unknown"),
            
            # Fitness-specific data
            fitness_level=user_data.get("fitness_level", "intermediate"),
            injury_history=user_data.get("injury_history", []),
            current_medications=user_data.get("medications", []),
            
            # Biometric data
            sleep_quality=user_data.get("sleep_quality"),
            stress_level=user_data.get("stress_level"),
            energy_level=user_data.get("energy_level"),
            
            # Training-specific data
            recent_workouts=user_data.get("recent_workouts", []),
            time_constraints=user_data.get("time_constraints", {}),
            equipment_access=user_data.get("equipment_access", []),
            
            # Preferences
            preference_scores=user_data.get("training_preferences", {}),
            interaction_history=user_data.get("interaction_history", [])
        )
        
        return user_profile
    
    async def _apply_blaze_personalization(self, 
                                         personalization_result: PersonalizationResult,
                                         request_type: str,
                                         request_content: str) -> Dict[str, Any]:
        """Apply personalization results to BLAZE-specific response"""
        
        # Extract personalization components
        combined_recs = personalization_result.combined_recommendations
        
        # Build personalized response
        personalized_response = {
            "personalization_applied": True,
            "confidence_score": personalization_result.confidence_score,
            "explanation": personalization_result.explanation,
            
            # Communication adaptations
            "communication_style": await self._adapt_communication_style(combined_recs),
            
            # Training adaptations
            "training_adaptations": await self._adapt_training_approach(combined_recs, request_type),
            
            # Content adaptations
            "content_adaptations": await self._adapt_content_delivery(combined_recs),
            
            # Motivation adaptations
            "motivation_approach": await self._adapt_motivation_approach(combined_recs),
            
            # Safety adaptations
            "safety_considerations": await self._adapt_safety_approach(combined_recs),
            
            # Timing adaptations
            "timing_recommendations": combined_recs.get("timing_adaptations", {}),
            
            # Metadata
            "personalization_metadata": {
                "archetype": combined_recs["personalization_metadata"]["archetype"],
                "readiness_score": combined_recs["personalization_metadata"]["readiness_score"],
                "age_considerations": combined_recs["personalization_metadata"]["age_factor"],
                "applied_at": datetime.now().isoformat()
            }
        }
        
        return personalized_response
    
    async def _adapt_communication_style(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt BLAZE communication style based on personalization"""
        
        base_style = combined_recs["communication_adaptations"]["style"]
        intensity = combined_recs["communication_adaptations"]["intensity"]
        
        # Map to BLAZE-specific communication styles
        blaze_style = self.blaze_adaptations["communication_styles"].get(
            base_style, "motivational_direct"
        )
        
        return {
            "style": blaze_style,
            "intensity_level": intensity,
            "motivational_elements": {
                "high_energy": intensity > 0.7,
                "technical_focus": base_style == "analytical",
                "supportive_tone": base_style == "supportive_educational"
            },
            "voice_adaptations": {
                "pace": "fast" if intensity > 0.7 else "moderate",
                "tone": "energetic" if intensity > 0.8 else "encouraging",
                "technical_depth": "high" if base_style == "analytical" else "moderate"
            }
        }
    
    async def _adapt_training_approach(self, combined_recs: Dict[str, Any], request_type: str) -> Dict[str, Any]:
        """Adapt training approach based on personalization"""
        
        protocol_adaptations = combined_recs["protocol_adaptations"]
        
        # Extract intensity information
        base_intensity = protocol_adaptations["base_intensity"]
        physio_mod = protocol_adaptations["physiological_modulation"]
        
        # Calculate adapted intensity
        adapted_intensity = physio_mod.get("modulated_intensity", 1.0)
        
        # Map to BLAZE training parameters
        training_adaptations = {
            "intensity_adjustment": adapted_intensity,
            "volume_adjustment": self._calculate_volume_adjustment(adapted_intensity),
            "recovery_emphasis": protocol_adaptations["recovery_focus"],
            "progression_rate": self._calculate_progression_rate(adapted_intensity, base_intensity),
            
            # Request-type specific adaptations
            "plan_generation": await self._adapt_plan_generation(protocol_adaptations, request_type),
            "exercise_selection": await self._adapt_exercise_selection(protocol_adaptations),
            "periodization": await self._adapt_periodization(protocol_adaptations),
            
            # Safety considerations
            "injury_prevention": protocol_adaptations["safety_modifications"],
            "movement_screening": self._should_emphasize_screening(protocol_adaptations),
            
            # Performance optimization
            "performance_focus": self._determine_performance_focus(protocol_adaptations)
        }
        
        return training_adaptations
    
    async def _adapt_content_delivery(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content delivery based on personalization"""
        
        content_adaptations = combined_recs["content_adaptations"]
        
        return {
            "complexity_level": content_adaptations.get("complexity_adjustment", "moderate"),
            "detail_level": content_adaptations["delivery_style"].get("detail_level", "comprehensive"),
            "visual_aids": self._should_include_visual_aids(content_adaptations),
            "scientific_backing": self._should_include_scientific_data(content_adaptations),
            "practical_examples": self._should_include_examples(content_adaptations),
            "progress_tracking": self._should_emphasize_tracking(content_adaptations)
        }
    
    async def _adapt_motivation_approach(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt motivation approach based on personalization"""
        
        archetype = combined_recs["personalization_metadata"]["archetype"]
        readiness_score = combined_recs["personalization_metadata"]["readiness_score"]
        
        if archetype == "prime":
            motivation_approach = {
                "type": "performance_driven",
                "elements": ["competition", "optimization", "efficiency"],
                "intensity": "high" if readiness_score > 0.7 else "moderate",
                "focus": "results_oriented"
            }
        else:  # longevity
            motivation_approach = {
                "type": "wellness_focused",
                "elements": ["sustainability", "health", "balance"],
                "intensity": "supportive",
                "focus": "process_oriented"
            }
        
        # Adjust based on readiness
        if readiness_score < 0.5:
            motivation_approach["elements"].append("encouragement")
            motivation_approach["intensity"] = "gentle"
        
        return motivation_approach
    
    async def _adapt_safety_approach(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt safety approach based on personalization"""
        
        safety_mods = combined_recs["protocol_adaptations"]["safety_modifications"]
        
        return {
            "safety_level": safety_mods.get("safety_factor", 1.0),
            "injury_considerations": safety_mods.get("injury_considerations", []),
            "risk_assessment": safety_mods.get("current_risk_level", 0.1),
            "recommendations": safety_mods.get("safety_recommendations", []),
            "movement_modifications": self._generate_movement_modifications(safety_mods),
            "monitoring_requirements": self._generate_monitoring_requirements(safety_mods)
        }
    
    def _calculate_volume_adjustment(self, intensity_adjustment: float) -> float:
        """Calculate volume adjustment based on intensity"""
        # Inverse relationship: if intensity is reduced, volume can be maintained or slightly increased
        if intensity_adjustment < 0.7:
            return min(1.2, 1.0 + (0.7 - intensity_adjustment) * 0.5)
        else:
            return 1.0
    
    def _calculate_progression_rate(self, adapted_intensity: float, base_intensity: Dict[str, Any]) -> str:
        """Calculate progression rate based on intensity adaptations"""
        if adapted_intensity > 0.8:
            return "aggressive"
        elif adapted_intensity > 0.6:
            return "moderate"
        else:
            return "conservative"
    
    async def _adapt_plan_generation(self, protocol_adaptations: Dict[str, Any], request_type: str) -> Dict[str, Any]:
        """Adapt plan generation based on request type and personalization"""
        
        if request_type == "training_plan":
            return {
                "plan_structure": self._determine_plan_structure(protocol_adaptations),
                "exercise_complexity": self._determine_exercise_complexity(protocol_adaptations),
                "progression_timeline": self._determine_progression_timeline(protocol_adaptations),
                "recovery_integration": self._determine_recovery_integration(protocol_adaptations)
            }
        
        return {"status": "not_applicable"}
    
    async def _adapt_exercise_selection(self, protocol_adaptations: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt exercise selection based on personalization"""
        
        safety_mods = protocol_adaptations["safety_modifications"]
        
        return {
            "exercise_filters": self._generate_exercise_filters(safety_mods),
            "movement_patterns": self._prioritize_movement_patterns(protocol_adaptations),
            "equipment_considerations": self._apply_equipment_constraints(protocol_adaptations),
            "injury_accommodations": safety_mods.get("injury_considerations", [])
        }
    
    async def _adapt_periodization(self, protocol_adaptations: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt periodization based on personalization"""
        
        return {
            "phase_duration": self._determine_phase_duration(protocol_adaptations),
            "intensity_distribution": self._determine_intensity_distribution(protocol_adaptations),
            "recovery_phases": self._determine_recovery_phases(protocol_adaptations),
            "adaptation_timeline": self._determine_adaptation_timeline(protocol_adaptations)
        }
    
    # Helper methods for personalization logic
    def _should_emphasize_screening(self, protocol_adaptations: Dict[str, Any]) -> bool:
        """Determine if movement screening should be emphasized"""
        safety_factor = protocol_adaptations["safety_modifications"].get("safety_factor", 1.0)
        return safety_factor > 1.1
    
    def _determine_performance_focus(self, protocol_adaptations: Dict[str, Any]) -> str:
        """Determine performance focus based on adaptations"""
        intensity_mod = protocol_adaptations["physiological_modulation"].get("modulated_intensity", 1.0)
        
        if intensity_mod > 0.8:
            return "performance_optimization"
        elif intensity_mod > 0.6:
            return "balanced_development"
        else:
            return "recovery_maintenance"
    
    def _should_include_visual_aids(self, content_adaptations: Dict[str, Any]) -> bool:
        """Determine if visual aids should be included"""
        complexity = content_adaptations.get("complexity_adjustment", "moderate")
        return complexity in ["simplified", "moderate"]
    
    def _should_include_scientific_data(self, content_adaptations: Dict[str, Any]) -> bool:
        """Determine if scientific data should be included"""
        complexity = content_adaptations.get("complexity_adjustment", "moderate")
        return complexity in ["enhanced", "advanced"]
    
    def _should_include_examples(self, content_adaptations: Dict[str, Any]) -> bool:
        """Determine if practical examples should be included"""
        return True  # Always beneficial for training content
    
    def _should_emphasize_tracking(self, content_adaptations: Dict[str, Any]) -> bool:
        """Determine if progress tracking should be emphasized"""
        delivery_style = content_adaptations["delivery_style"]
        return delivery_style.get("detail_level") == "comprehensive"
    
    def _generate_movement_modifications(self, safety_mods: Dict[str, Any]) -> List[str]:
        """Generate movement modifications based on safety considerations"""
        modifications = []
        
        injury_considerations = safety_mods.get("injury_considerations", [])
        
        for injury in injury_considerations:
            if "knee" in injury.lower():
                modifications.append("reduced_knee_stress")
            elif "shoulder" in injury.lower():
                modifications.append("shoulder_stability_focus")
            elif "back" in injury.lower():
                modifications.append("spine_neutral_emphasis")
        
        return modifications
    
    def _generate_monitoring_requirements(self, safety_mods: Dict[str, Any]) -> List[str]:
        """Generate monitoring requirements based on safety considerations"""
        requirements = []
        
        risk_level = safety_mods.get("current_risk_level", 0.1)
        
        if risk_level > 0.3:
            requirements.append("enhanced_form_monitoring")
        if risk_level > 0.5:
            requirements.append("frequent_fatigue_assessment")
        if risk_level > 0.7:
            requirements.append("real_time_movement_analysis")
        
        return requirements
    
    def _determine_plan_structure(self, protocol_adaptations: Dict[str, Any]) -> str:
        """Determine optimal plan structure"""
        intensity_mod = protocol_adaptations["physiological_modulation"].get("modulated_intensity", 1.0)
        
        if intensity_mod > 0.8:
            return "high_intensity_focused"
        elif intensity_mod > 0.6:
            return "balanced_approach"
        else:
            return "recovery_emphasized"
    
    def _determine_exercise_complexity(self, protocol_adaptations: Dict[str, Any]) -> str:
        """Determine exercise complexity level"""
        safety_factor = protocol_adaptations["safety_modifications"].get("safety_factor", 1.0)
        
        if safety_factor > 1.2:
            return "simplified"
        elif safety_factor > 1.0:
            return "moderate"
        else:
            return "advanced"
    
    def _determine_progression_timeline(self, protocol_adaptations: Dict[str, Any]) -> str:
        """Determine progression timeline"""
        recovery_emphasis = protocol_adaptations["recovery_focus"]
        
        if recovery_emphasis.get("adjusted_recovery_focus", 1.0) > 1.3:
            return "extended"
        else:
            return "standard"
    
    def _determine_recovery_integration(self, protocol_adaptations: Dict[str, Any]) -> str:
        """Determine recovery integration level"""
        recovery_emphasis = protocol_adaptations["recovery_focus"]
        
        if recovery_emphasis.get("adjusted_recovery_focus", 1.0) > 1.2:
            return "high_integration"
        else:
            return "standard_integration"
    
    def _generate_exercise_filters(self, safety_mods: Dict[str, Any]) -> List[str]:
        """Generate exercise filters based on safety modifications"""
        filters = []
        
        safety_factor = safety_mods.get("safety_factor", 1.0)
        
        if safety_factor > 1.2:
            filters.append("low_impact_preferred")
        if safety_factor > 1.1:
            filters.append("controlled_movement_focus")
        
        return filters
    
    def _prioritize_movement_patterns(self, protocol_adaptations: Dict[str, Any]) -> List[str]:
        """Prioritize movement patterns based on personalization"""
        patterns = ["fundamental_movements"]
        
        safety_factor = protocol_adaptations["safety_modifications"].get("safety_factor", 1.0)
        
        if safety_factor > 1.1:
            patterns.append("stability_emphasis")
        if safety_factor < 1.0:
            patterns.append("power_movements")
        
        return patterns
    
    def _apply_equipment_constraints(self, protocol_adaptations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply equipment constraints based on personalization"""
        return {
            "required_equipment": [],
            "preferred_equipment": [],
            "equipment_alternatives": True
        }
    
    def _determine_phase_duration(self, protocol_adaptations: Dict[str, Any]) -> str:
        """Determine phase duration for periodization"""
        recovery_emphasis = protocol_adaptations["recovery_focus"]
        
        if recovery_emphasis.get("adjusted_recovery_focus", 1.0) > 1.3:
            return "extended_phases"
        else:
            return "standard_phases"
    
    def _determine_intensity_distribution(self, protocol_adaptations: Dict[str, Any]) -> Dict[str, float]:
        """Determine intensity distribution"""
        intensity_mod = protocol_adaptations["physiological_modulation"].get("modulated_intensity", 1.0)
        
        if intensity_mod > 0.8:
            return {"high": 0.2, "moderate": 0.6, "low": 0.2}
        elif intensity_mod > 0.6:
            return {"high": 0.1, "moderate": 0.7, "low": 0.2}
        else:
            return {"high": 0.05, "moderate": 0.5, "low": 0.45}
    
    def _determine_recovery_phases(self, protocol_adaptations: Dict[str, Any]) -> Dict[str, Any]:
        """Determine recovery phase characteristics"""
        recovery_emphasis = protocol_adaptations["recovery_focus"]
        
        return {
            "frequency": "increased" if recovery_emphasis.get("adjusted_recovery_focus", 1.0) > 1.2 else "standard",
            "duration": "extended" if recovery_emphasis.get("adjusted_recovery_focus", 1.0) > 1.3 else "standard",
            "intensity": "active" if recovery_emphasis.get("adjusted_recovery_focus", 1.0) > 1.1 else "mixed"
        }
    
    def _determine_adaptation_timeline(self, protocol_adaptations: Dict[str, Any]) -> str:
        """Determine adaptation timeline"""
        intensity_mod = protocol_adaptations["physiological_modulation"].get("modulated_intensity", 1.0)
        
        if intensity_mod > 0.8:
            return "accelerated"
        elif intensity_mod > 0.6:
            return "standard"
        else:
            return "gradual"
    
    async def _generate_fallback_response(self, request_type: str, request_content: str) -> Dict[str, Any]:
        """Generate fallback response if personalization fails"""
        
        return {
            "personalization_applied": False,
            "fallback_mode": True,
            "communication_style": {
                "style": "motivational_direct",
                "intensity_level": 0.7,
                "voice_adaptations": {
                    "pace": "moderate",
                    "tone": "encouraging",
                    "technical_depth": "moderate"
                }
            },
            "training_adaptations": {
                "intensity_adjustment": 0.8,
                "volume_adjustment": 1.0,
                "progression_rate": "moderate"
            },
            "safety_considerations": {
                "safety_level": 1.1,
                "monitoring_requirements": ["standard_form_monitoring"]
            },
            "message": "Using standard BLAZE configuration due to personalization system unavailability"
        }
    
    async def provide_feedback(self, 
                             personalization_result: PersonalizationResult,
                             user_feedback: Dict[str, Any]):
        """Provide feedback to the hybrid intelligence engine for learning"""
        
        # This would be called after user interaction to improve personalization
        await self.hybrid_engine.learning_engine.learn_from_interaction(
            context=None,  # Would need to store context from previous call
            result=personalization_result,
            user_feedback=user_feedback
        )
    
    async def get_user_training_insights(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive training insights for a user"""
        
        # Get insights from hybrid engine
        general_insights = await self.hybrid_engine.get_user_insights(user_id)
        
        # Add BLAZE-specific insights
        training_insights = {
            "general_insights": general_insights,
            "training_specific": {
                "preferred_intensity_range": self._analyze_intensity_preferences(general_insights),
                "most_effective_training_types": self._analyze_training_effectiveness(general_insights),
                "optimal_communication_style": self._analyze_communication_effectiveness(general_insights),
                "injury_risk_patterns": self._analyze_injury_risk_patterns(general_insights)
            }
        }
        
        return training_insights
    
    def _analyze_intensity_preferences(self, general_insights: Dict[str, Any]) -> str:
        """Analyze intensity preferences from general insights"""
        # This would analyze patterns in user responses to different intensities
        return "moderate_to_high"  # Placeholder
    
    def _analyze_training_effectiveness(self, general_insights: Dict[str, Any]) -> List[str]:
        """Analyze most effective training types"""
        # This would analyze which training types had highest effectiveness scores
        return ["strength_training", "functional_movement"]  # Placeholder
    
    def _analyze_communication_effectiveness(self, general_insights: Dict[str, Any]) -> str:
        """Analyze most effective communication style"""
        # This would analyze communication patterns with highest effectiveness
        return "motivational_direct"  # Placeholder
    
    def _analyze_injury_risk_patterns(self, general_insights: Dict[str, Any]) -> List[str]:
        """Analyze injury risk patterns"""
        # This would analyze patterns that led to injury risk increases
        return ["overtraining_tendency", "insufficient_recovery"]  # Placeholder


# Export the integration class
__all__ = ["BLAZEHybridIntelligenceIntegration"]