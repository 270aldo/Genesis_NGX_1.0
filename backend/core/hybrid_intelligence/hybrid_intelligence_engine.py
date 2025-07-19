"""
GENESIS NGX Agents - Hybrid Intelligence Engine
==============================================

Revolutionary two-layer personalization system combining:
- Layer 1: Archetype Adaptation (PRIME vs LONGEVITY strategic alignment)
- Layer 2: Physiological Modulation (real-time bio-data personalization)

This engine transforms the binary PersonalityAdapter into a sophisticated
system that understands users at both strategic and physiological levels.

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-09
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from datetime import datetime, timedelta

# Import base dependencies
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserArchetype(Enum):
    """NGX User Archetypes for strategic personalization"""
    PRIME = "prime"        # Optimizers seeking performance and efficiency
    LONGEVITY = "longevity"  # Life architects focused on prevention and sustainability


class PersonalizationMode(Enum):
    """Personalization intensity modes"""
    BASIC = "basic"        # Simple archetype-based adaptation
    ADVANCED = "advanced"  # Full hybrid intelligence with bio-data
    EXPERT = "expert"      # Maximum personalization with ML predictions


@dataclass
class UserProfile:
    """Complete user profile for hybrid intelligence processing"""
    user_id: str
    archetype: UserArchetype
    
    # Basic demographics
    age: int
    gender: str
    
    # Physiological data
    fitness_level: str = "intermediate"
    injury_history: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    
    # Biomarkers (optional, for advanced users)
    biomarkers: Dict[str, Any] = field(default_factory=dict)
    
    # Real-time data
    recent_workouts: List[Dict] = field(default_factory=list)
    sleep_quality: Optional[float] = None
    stress_level: Optional[float] = None
    energy_level: Optional[float] = None
    
    # Preferences and constraints
    time_constraints: Dict[str, Any] = field(default_factory=dict)
    equipment_access: List[str] = field(default_factory=list)
    dietary_restrictions: List[str] = field(default_factory=list)
    
    # Learning data
    interaction_history: List[Dict] = field(default_factory=list)
    preference_scores: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class PersonalizationContext:
    """Context for a specific personalization request"""
    user_profile: UserProfile
    agent_type: str
    request_type: str
    request_content: str
    current_time: datetime = field(default_factory=datetime.now)
    session_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonalizationResult:
    """Result of hybrid intelligence processing"""
    archetype_adaptation: Dict[str, Any]
    physiological_modulation: Dict[str, Any]
    combined_recommendations: Dict[str, Any]
    confidence_score: float
    explanation: str
    learning_data: Dict[str, Any] = field(default_factory=dict)


class ArchetypeAdaptationLayer:
    """
    Layer 1: Strategic archetype-based personalization
    
    PRIME users get:
    - Performance-focused protocols
    - Efficiency optimization
    - Competitive elements
    - Advanced metrics
    
    LONGEVITY users get:
    - Prevention-focused protocols
    - Sustainability emphasis
    - Wellness integration
    - Long-term planning
    """
    
    def __init__(self):
        self.archetype_profiles = {
            UserArchetype.PRIME: {
                "communication_style": "direct_performance",
                "motivation_triggers": ["competition", "optimization", "efficiency"],
                "content_preferences": ["advanced_metrics", "performance_data", "benchmarks"],
                "protocol_intensity": "high_performance",
                "focus_areas": ["strength", "power", "performance_metrics"],
                "decision_style": "data_driven_fast",
                "goal_orientation": "achievement_focused"
            },
            UserArchetype.LONGEVITY: {
                "communication_style": "supportive_educational",
                "motivation_triggers": ["wellness", "prevention", "sustainability"],
                "content_preferences": ["educational", "wellness_tips", "long_term_benefits"],
                "protocol_intensity": "sustainable_moderate",
                "focus_areas": ["mobility", "balance", "preventive_care"],
                "decision_style": "thoughtful_holistic",
                "goal_orientation": "process_focused"
            }
        }
    
    async def adapt_for_archetype(self, context: PersonalizationContext) -> Dict[str, Any]:
        """Generate archetype-specific adaptations"""
        archetype = context.user_profile.archetype
        profile = self.archetype_profiles[archetype]
        
        # Age-based modulation for archetype
        age_factor = self._calculate_age_factor(context.user_profile.age, archetype)
        
        adaptation = {
            "communication_style": profile["communication_style"],
            "motivation_approach": self._adapt_motivation(profile["motivation_triggers"], age_factor),
            "content_delivery": self._adapt_content_style(profile["content_preferences"], context),
            "protocol_intensity": self._adapt_intensity(profile["protocol_intensity"], age_factor),
            "focus_prioritization": self._adapt_focus_areas(profile["focus_areas"], context),
            "decision_support": profile["decision_style"],
            "goal_framework": profile["goal_orientation"],
            "age_modulation": age_factor
        }
        
        return adaptation
    
    def _calculate_age_factor(self, age: int, archetype: UserArchetype) -> Dict[str, Any]:
        """Calculate age-based modulation factor"""
        if archetype == UserArchetype.PRIME:
            if age < 30:
                return {"intensity": 1.0, "recovery_emphasis": 0.7, "safety_factor": 0.8}
            elif age < 45:
                return {"intensity": 0.9, "recovery_emphasis": 0.8, "safety_factor": 0.9}
            else:
                return {"intensity": 0.8, "recovery_emphasis": 1.0, "safety_factor": 1.0}
        else:  # LONGEVITY
            if age < 40:
                return {"intensity": 0.8, "recovery_emphasis": 0.9, "safety_factor": 0.9}
            elif age < 60:
                return {"intensity": 0.7, "recovery_emphasis": 1.0, "safety_factor": 1.0}
            else:
                return {"intensity": 0.6, "recovery_emphasis": 1.2, "safety_factor": 1.2}
    
    def _adapt_motivation(self, base_triggers: List[str], age_factor: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt motivation triggers based on age"""
        return {
            "primary_triggers": base_triggers,
            "intensity_modifier": age_factor["intensity"],
            "safety_emphasis": age_factor["safety_factor"]
        }
    
    def _adapt_content_style(self, preferences: List[str], context: PersonalizationContext) -> Dict[str, Any]:
        """Adapt content delivery style"""
        return {
            "preferred_formats": preferences,
            "complexity_level": "advanced" if context.user_profile.archetype == UserArchetype.PRIME else "educational",
            "detail_level": "high" if context.user_profile.archetype == UserArchetype.PRIME else "comprehensive"
        }
    
    def _adapt_intensity(self, base_intensity: str, age_factor: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt protocol intensity"""
        return {
            "base_intensity": base_intensity,
            "age_adjusted_intensity": age_factor["intensity"],
            "recovery_emphasis": age_factor["recovery_emphasis"]
        }
    
    def _adapt_focus_areas(self, base_areas: List[str], context: PersonalizationContext) -> Dict[str, Any]:
        """Adapt focus areas based on context"""
        return {
            "primary_areas": base_areas,
            "injury_considerations": context.user_profile.injury_history,
            "equipment_constraints": context.user_profile.equipment_access
        }


class PhysiologicalModulationLayer:
    """
    Layer 2: Real-time physiological data modulation
    
    Adjusts archetype-based recommendations using:
    - Current biomarkers
    - Real-time biometric data
    - Recent performance data
    - Recovery status
    - Health constraints
    """
    
    def __init__(self):
        self.modulation_weights = {
            "sleep_quality": 0.3,
            "stress_level": 0.25,
            "energy_level": 0.2,
            "recovery_status": 0.15,
            "injury_status": 0.1
        }
    
    async def modulate_physiologically(self, 
                                    archetype_adaptation: Dict[str, Any],
                                    context: PersonalizationContext) -> Dict[str, Any]:
        """Apply physiological modulation to archetype adaptations"""
        
        # Calculate current physiological state
        physio_state = await self._assess_physiological_state(context.user_profile)
        
        # Apply modulations
        modulated_adaptation = {
            "intensity_adjustment": self._modulate_intensity(
                archetype_adaptation["protocol_intensity"], 
                physio_state
            ),
            "recovery_emphasis": self._modulate_recovery_focus(
                archetype_adaptation, 
                physio_state
            ),
            "safety_adjustments": self._apply_safety_modulations(
                archetype_adaptation,
                context.user_profile.injury_history,
                physio_state
            ),
            "timing_optimization": self._optimize_timing(
                archetype_adaptation,
                physio_state
            ),
            "biomarker_considerations": self._apply_biomarker_insights(
                archetype_adaptation,
                context.user_profile.biomarkers
            ),
            "real_time_adjustments": physio_state
        }
        
        return modulated_adaptation
    
    async def _assess_physiological_state(self, profile: UserProfile) -> Dict[str, Any]:
        """Assess current physiological state from available data"""
        state = {
            "sleep_quality": profile.sleep_quality or 0.7,  # Default moderate
            "stress_level": profile.stress_level or 0.5,
            "energy_level": profile.energy_level or 0.7,
            "recovery_status": self._calculate_recovery_status(profile),
            "injury_risk": self._assess_injury_risk(profile),
            "readiness_score": 0.0
        }
        
        # Calculate overall readiness score
        state["readiness_score"] = self._calculate_readiness_score(state)
        
        return state
    
    def _calculate_recovery_status(self, profile: UserProfile) -> float:
        """Calculate recovery status from recent workouts and biometrics"""
        if not profile.recent_workouts:
            return 0.8  # Well rested
        
        # Simple recovery calculation based on recent workout intensity
        recent_intensity = sum(w.get("intensity", 0.5) for w in profile.recent_workouts[-3:])
        recovery_factor = max(0.2, 1.0 - (recent_intensity / 3.0) * 0.6)
        
        return recovery_factor
    
    def _assess_injury_risk(self, profile: UserProfile) -> float:
        """Assess current injury risk based on history and state"""
        base_risk = 0.1  # Base risk for everyone
        
        # Increase risk based on injury history
        if profile.injury_history:
            base_risk += len(profile.injury_history) * 0.05
        
        # Adjust for current state
        if profile.stress_level and profile.stress_level > 0.7:
            base_risk += 0.1
        
        if profile.sleep_quality and profile.sleep_quality < 0.5:
            base_risk += 0.15
        
        return min(base_risk, 0.8)  # Cap at 80%
    
    def _calculate_readiness_score(self, state: Dict[str, Any]) -> float:
        """Calculate overall readiness score"""
        score = 0.0
        
        # Positive factors
        score += state["sleep_quality"] * 0.3
        score += state["energy_level"] * 0.25
        score += state["recovery_status"] * 0.2
        
        # Negative factors
        score -= state["stress_level"] * 0.15
        score -= state["injury_risk"] * 0.1
        
        return max(0.0, min(1.0, score))
    
    def _modulate_intensity(self, base_intensity: Dict[str, Any], physio_state: Dict[str, Any]) -> Dict[str, Any]:
        """Modulate training intensity based on physiological state"""
        readiness = physio_state["readiness_score"]
        
        if readiness > 0.8:
            intensity_factor = 1.0
            recommendation = "proceed_as_planned"
        elif readiness > 0.6:
            intensity_factor = 0.8
            recommendation = "moderate_reduction"
        elif readiness > 0.4:
            intensity_factor = 0.6
            recommendation = "significant_reduction"
        else:
            intensity_factor = 0.3
            recommendation = "recovery_focus"
        
        return {
            "base_intensity": base_intensity,
            "modulated_intensity": intensity_factor,
            "recommendation": recommendation,
            "reasoning": f"Readiness score: {readiness:.2f}"
        }
    
    def _modulate_recovery_focus(self, archetype_adaptation: Dict[str, Any], physio_state: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust recovery focus based on physiological state"""
        base_recovery = archetype_adaptation["protocol_intensity"]["recovery_emphasis"]
        
        if physio_state["readiness_score"] < 0.6:
            recovery_multiplier = 1.5
        elif physio_state["stress_level"] > 0.7:
            recovery_multiplier = 1.3
        else:
            recovery_multiplier = 1.0
        
        return {
            "base_recovery_focus": base_recovery,
            "adjusted_recovery_focus": base_recovery * recovery_multiplier,
            "recovery_recommendations": self._generate_recovery_recommendations(physio_state)
        }
    
    def _apply_safety_modulations(self, archetype_adaptation: Dict[str, Any], 
                                injury_history: List[str], 
                                physio_state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply safety modulations based on injury history and current state"""
        safety_factor = archetype_adaptation["protocol_intensity"]["recovery_emphasis"]
        
        # Increase safety for injury history
        if injury_history:
            safety_factor *= 1.2
        
        # Increase safety for high stress or poor recovery
        if physio_state["stress_level"] > 0.7 or physio_state["recovery_status"] < 0.4:
            safety_factor *= 1.3
        
        return {
            "safety_factor": safety_factor,
            "injury_considerations": injury_history,
            "current_risk_level": physio_state["injury_risk"],
            "safety_recommendations": self._generate_safety_recommendations(injury_history, physio_state)
        }
    
    def _optimize_timing(self, archetype_adaptation: Dict[str, Any], physio_state: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize timing recommendations based on physiological state"""
        return {
            "optimal_training_time": self._suggest_optimal_time(physio_state),
            "recovery_windows": self._suggest_recovery_windows(physio_state),
            "nutrition_timing": self._suggest_nutrition_timing(physio_state)
        }
    
    def _apply_biomarker_insights(self, archetype_adaptation: Dict[str, Any], biomarkers: Dict[str, Any]) -> Dict[str, Any]:
        """Apply insights from biomarker data"""
        if not biomarkers:
            return {"status": "no_biomarker_data"}
        
        insights = {
            "metabolic_insights": self._analyze_metabolic_biomarkers(biomarkers),
            "inflammation_status": self._analyze_inflammatory_markers(biomarkers),
            "hormonal_considerations": self._analyze_hormonal_markers(biomarkers),
            "nutrient_status": self._analyze_nutrient_markers(biomarkers)
        }
        
        return insights
    
    def _generate_recovery_recommendations(self, physio_state: Dict[str, Any]) -> List[str]:
        """Generate specific recovery recommendations"""
        recommendations = []
        
        if physio_state["sleep_quality"] < 0.6:
            recommendations.append("Prioritize sleep optimization")
        
        if physio_state["stress_level"] > 0.7:
            recommendations.append("Implement stress management techniques")
        
        if physio_state["recovery_status"] < 0.5:
            recommendations.append("Extend recovery periods between sessions")
        
        return recommendations
    
    def _generate_safety_recommendations(self, injury_history: List[str], physio_state: Dict[str, Any]) -> List[str]:
        """Generate safety-specific recommendations"""
        recommendations = []
        
        if injury_history:
            recommendations.append("Modified movement patterns for injury prevention")
        
        if physio_state["injury_risk"] > 0.4:
            recommendations.append("Enhanced warm-up and mobility work")
        
        if physio_state["readiness_score"] < 0.5:
            recommendations.append("Consider active recovery or rest day")
        
        return recommendations
    
    def _suggest_optimal_time(self, physio_state: Dict[str, Any]) -> str:
        """Suggest optimal training time based on physiological state"""
        if physio_state["energy_level"] > 0.7:
            return "morning_or_afternoon"
        elif physio_state["energy_level"] > 0.4:
            return "afternoon_preferred"
        else:
            return "light_activity_only"
    
    def _suggest_recovery_windows(self, physio_state: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest recovery windows based on current state"""
        if physio_state["recovery_status"] < 0.5:
            return {"between_sessions": "48-72_hours", "within_session": "extended_rest"}
        else:
            return {"between_sessions": "24-48_hours", "within_session": "standard_rest"}
    
    def _suggest_nutrition_timing(self, physio_state: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest nutrition timing based on physiological state"""
        return {
            "pre_workout": "2-3_hours_before" if physio_state["energy_level"] < 0.6 else "1-2_hours_before",
            "post_workout": "within_30_minutes" if physio_state["recovery_status"] < 0.6 else "within_60_minutes",
            "hydration_focus": "increased" if physio_state["stress_level"] > 0.6 else "standard"
        }
    
    def _analyze_metabolic_biomarkers(self, biomarkers: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze metabolic biomarkers for insights"""
        # This would integrate with actual biomarker analysis
        return {"status": "analysis_pending", "recommendations": []}
    
    def _analyze_inflammatory_markers(self, biomarkers: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze inflammatory markers"""
        return {"status": "analysis_pending", "recommendations": []}
    
    def _analyze_hormonal_markers(self, biomarkers: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze hormonal markers"""
        return {"status": "analysis_pending", "recommendations": []}
    
    def _analyze_nutrient_markers(self, biomarkers: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze nutrient markers"""
        return {"status": "analysis_pending", "recommendations": []}


class ContinuousLearningEngine:
    """
    Continuous learning system for hybrid intelligence optimization
    """
    
    def __init__(self):
        self.learning_data = {}
        self.adaptation_patterns = {}
        self.effectiveness_metrics = {}
    
    async def learn_from_interaction(self, 
                                   context: PersonalizationContext,
                                   result: PersonalizationResult,
                                   user_feedback: Optional[Dict[str, Any]] = None):
        """Learn from user interactions and outcomes"""
        
        learning_entry = {
            "timestamp": datetime.now(),
            "user_id": context.user_profile.user_id,
            "archetype": context.user_profile.archetype.value,
            "context": {
                "agent_type": context.agent_type,
                "request_type": context.request_type,
                "physiological_state": context.user_profile.sleep_quality  # Example
            },
            "personalization_result": {
                "confidence_score": result.confidence_score,
                "recommendations": result.combined_recommendations
            },
            "user_feedback": user_feedback or {},
            "effectiveness_score": self._calculate_effectiveness_score(result, user_feedback)
        }
        
        # Store learning data
        await self._store_learning_data(learning_entry)
        
        # Update adaptation patterns
        await self._update_adaptation_patterns(learning_entry)
    
    def _calculate_effectiveness_score(self, result: PersonalizationResult, feedback: Optional[Dict[str, Any]]) -> float:
        """Calculate effectiveness score for learning"""
        base_score = result.confidence_score
        
        if feedback:
            user_satisfaction = feedback.get("satisfaction", 0.5)
            outcome_success = feedback.get("outcome_success", 0.5)
            
            effectiveness = (base_score + user_satisfaction + outcome_success) / 3.0
        else:
            effectiveness = base_score
        
        return effectiveness
    
    async def _store_learning_data(self, learning_entry: Dict[str, Any]):
        """Store learning data for future analysis"""
        user_id = learning_entry["user_id"]
        
        if user_id not in self.learning_data:
            self.learning_data[user_id] = []
        
        self.learning_data[user_id].append(learning_entry)
    
    async def _update_adaptation_patterns(self, learning_entry: Dict[str, Any]):
        """Update adaptation patterns based on learning"""
        archetype = learning_entry["archetype"]
        effectiveness = learning_entry["effectiveness_score"]
        
        if archetype not in self.adaptation_patterns:
            self.adaptation_patterns[archetype] = {
                "total_interactions": 0,
                "average_effectiveness": 0.0,
                "successful_patterns": [],
                "improvement_areas": []
            }
        
        pattern = self.adaptation_patterns[archetype]
        pattern["total_interactions"] += 1
        
        # Update rolling average
        current_avg = pattern["average_effectiveness"]
        new_avg = (current_avg * (pattern["total_interactions"] - 1) + effectiveness) / pattern["total_interactions"]
        pattern["average_effectiveness"] = new_avg
        
        # Track successful patterns
        if effectiveness > 0.7:
            pattern["successful_patterns"].append(learning_entry["context"])


class HybridIntelligenceEngine:
    """
    Main Hybrid Intelligence Engine
    
    Orchestrates the two-layer personalization system to provide
    revolutionary user understanding and adaptation capabilities.
    """
    
    def __init__(self):
        self.archetype_layer = ArchetypeAdaptationLayer()
        self.physiological_layer = PhysiologicalModulationLayer()
        self.learning_engine = ContinuousLearningEngine()
        
        logger.info("Hybrid Intelligence Engine initialized")
    
    async def personalize_for_user(self, 
                                 context: PersonalizationContext,
                                 mode: PersonalizationMode = PersonalizationMode.ADVANCED) -> PersonalizationResult:
        """
        Main personalization method combining both layers
        
        Args:
            context: Personalization context with user profile and request
            mode: Personalization intensity mode
            
        Returns:
            PersonalizationResult with comprehensive adaptations
        """
        
        logger.info(f"Personalizing for user {context.user_profile.user_id}, archetype: {context.user_profile.archetype.value}")
        
        try:
            # Layer 1: Archetype Adaptation
            archetype_adaptation = await self.archetype_layer.adapt_for_archetype(context)
            
            # Layer 2: Physiological Modulation (if advanced mode)
            if mode in [PersonalizationMode.ADVANCED, PersonalizationMode.EXPERT]:
                physiological_modulation = await self.physiological_layer.modulate_physiologically(
                    archetype_adaptation, context
                )
            else:
                physiological_modulation = {"status": "basic_mode", "adaptations": {}}
            
            # Combine adaptations
            combined_recommendations = await self._combine_adaptations(
                archetype_adaptation, 
                physiological_modulation,
                context
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                archetype_adaptation, 
                physiological_modulation,
                context
            )
            
            # Generate explanation
            explanation = self._generate_explanation(
                archetype_adaptation,
                physiological_modulation,
                combined_recommendations,
                context
            )
            
            # Create result
            result = PersonalizationResult(
                archetype_adaptation=archetype_adaptation,
                physiological_modulation=physiological_modulation,
                combined_recommendations=combined_recommendations,
                confidence_score=confidence_score,
                explanation=explanation,
                learning_data={
                    "mode": mode.value,
                    "timestamp": datetime.now(),
                    "processing_time": "calculated_separately"
                }
            )
            
            # Learn from this interaction
            await self.learning_engine.learn_from_interaction(context, result)
            
            logger.info(f"Personalization complete. Confidence: {confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Personalization failed: {str(e)}")
            raise
    
    async def _combine_adaptations(self, 
                                 archetype_adaptation: Dict[str, Any],
                                 physiological_modulation: Dict[str, Any],
                                 context: PersonalizationContext) -> Dict[str, Any]:
        """Combine archetype and physiological adaptations"""
        
        combined = {
            "communication_adaptations": {
                "style": archetype_adaptation["communication_style"],
                "intensity": physiological_modulation.get("intensity_adjustment", {}).get("modulated_intensity", 1.0),
                "safety_emphasis": physiological_modulation.get("safety_adjustments", {}).get("safety_factor", 1.0)
            },
            "content_adaptations": {
                "delivery_style": archetype_adaptation["content_delivery"],
                "complexity_adjustment": self._adjust_complexity_for_state(
                    archetype_adaptation["content_delivery"], 
                    physiological_modulation
                ),
                "focus_prioritization": archetype_adaptation["focus_prioritization"]
            },
            "protocol_adaptations": {
                "base_intensity": archetype_adaptation["protocol_intensity"],
                "physiological_modulation": physiological_modulation.get("intensity_adjustment", {}),
                "recovery_focus": physiological_modulation.get("recovery_emphasis", {}),
                "safety_modifications": physiological_modulation.get("safety_adjustments", {})
            },
            "timing_adaptations": physiological_modulation.get("timing_optimization", {}),
            "personalization_metadata": {
                "archetype": context.user_profile.archetype.value,
                "age_factor": archetype_adaptation.get("age_modulation", {}),
                "readiness_score": physiological_modulation.get("real_time_adjustments", {}).get("readiness_score", 0.7),
                "confidence_factors": {
                    "archetype_confidence": 0.9,  # High confidence in archetype matching
                    "physiological_confidence": 0.8,  # Good confidence in bio-data
                    "combined_confidence": 0.85
                }
            }
        }
        
        return combined
    
    def _adjust_complexity_for_state(self, content_delivery: Dict[str, Any], 
                                   physiological_modulation: Dict[str, Any]) -> str:
        """Adjust content complexity based on physiological state"""
        base_complexity = content_delivery.get("complexity_level", "standard")
        
        readiness_score = physiological_modulation.get("real_time_adjustments", {}).get("readiness_score", 0.7)
        
        if readiness_score < 0.5:
            return "simplified"
        elif readiness_score > 0.8:
            return "enhanced"
        else:
            return base_complexity
    
    def _calculate_confidence_score(self, 
                                  archetype_adaptation: Dict[str, Any],
                                  physiological_modulation: Dict[str, Any],
                                  context: PersonalizationContext) -> float:
        """Calculate confidence score for personalization result"""
        
        # Base confidence from archetype matching
        archetype_confidence = 0.9  # High confidence in archetype system
        
        # Physiological data confidence
        physio_confidence = 0.8
        if physiological_modulation.get("status") == "basic_mode":
            physio_confidence = 0.6
        
        # Data completeness factor
        profile = context.user_profile
        data_completeness = 0.5  # Base
        
        if profile.sleep_quality is not None:
            data_completeness += 0.1
        if profile.stress_level is not None:
            data_completeness += 0.1
        if profile.recent_workouts:
            data_completeness += 0.1
        if profile.biomarkers:
            data_completeness += 0.2
        
        # Combine scores
        combined_confidence = (archetype_confidence * 0.4 + 
                             physio_confidence * 0.4 + 
                             data_completeness * 0.2)
        
        return min(combined_confidence, 1.0)
    
    def _generate_explanation(self, 
                            archetype_adaptation: Dict[str, Any],
                            physiological_modulation: Dict[str, Any],
                            combined_recommendations: Dict[str, Any],
                            context: PersonalizationContext) -> str:
        """Generate human-readable explanation of personalization"""
        
        archetype = context.user_profile.archetype.value.upper()
        age = context.user_profile.age
        
        explanation = f"Personalization for {archetype} archetype (age {age}):\n\n"
        
        # Archetype explanation
        if archetype == "PRIME":
            explanation += "🎯 PRIME Focus: Performance-driven protocols with efficiency optimization\n"
        else:
            explanation += "🌿 LONGEVITY Focus: Sustainable wellness with prevention emphasis\n"
        
        # Physiological adjustments
        if physiological_modulation.get("status") != "basic_mode":
            readiness = physiological_modulation.get("real_time_adjustments", {}).get("readiness_score", 0.7)
            explanation += f"📊 Current Readiness: {readiness:.1%} - "
            
            if readiness > 0.8:
                explanation += "Excellent condition for full intensity\n"
            elif readiness > 0.6:
                explanation += "Good condition with minor adjustments\n"
            elif readiness > 0.4:
                explanation += "Moderate condition requiring intensity reduction\n"
            else:
                explanation += "Low readiness - recovery focus recommended\n"
        
        # Key adaptations
        explanation += "\n🔧 Key Adaptations:\n"
        
        comm_style = combined_recommendations["communication_adaptations"]["style"]
        explanation += f"• Communication: {comm_style.replace('_', ' ').title()}\n"
        
        intensity_mod = combined_recommendations["protocol_adaptations"]["physiological_modulation"].get("modulated_intensity", 1.0)
        explanation += f"• Intensity Adjustment: {intensity_mod:.0%} of baseline\n"
        
        safety_factor = combined_recommendations["protocol_adaptations"]["safety_modifications"].get("safety_factor", 1.0)
        if safety_factor > 1.0:
            explanation += f"• Enhanced Safety: {safety_factor:.1f}x safety protocols\n"
        
        return explanation
    
    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive insights about a user's personalization patterns"""
        
        user_learning_data = self.learning_engine.learning_data.get(user_id, [])
        
        if not user_learning_data:
            return {"status": "no_data", "message": "No learning data available for user"}
        
        # Analyze patterns
        recent_interactions = user_learning_data[-10:]  # Last 10 interactions
        
        insights = {
            "total_interactions": len(user_learning_data),
            "average_effectiveness": sum(entry["effectiveness_score"] for entry in user_learning_data) / len(user_learning_data),
            "recent_performance": sum(entry["effectiveness_score"] for entry in recent_interactions) / len(recent_interactions),
            "most_effective_contexts": self._find_most_effective_contexts(user_learning_data),
            "improvement_trends": self._analyze_improvement_trends(user_learning_data),
            "personalization_preferences": self._extract_preferences(user_learning_data)
        }
        
        return insights
    
    def _find_most_effective_contexts(self, learning_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find contexts where personalization was most effective"""
        effective_contexts = [entry for entry in learning_data if entry["effectiveness_score"] > 0.7]
        
        # Group by context type
        context_groups = {}
        for entry in effective_contexts:
            context_key = f"{entry['context']['agent_type']}_{entry['context']['request_type']}"
            if context_key not in context_groups:
                context_groups[context_key] = []
            context_groups[context_key].append(entry)
        
        # Return top contexts
        return sorted(context_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    
    def _analyze_improvement_trends(self, learning_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze improvement trends over time"""
        if len(learning_data) < 5:
            return {"status": "insufficient_data"}
        
        # Calculate trend over last 10 vs previous 10
        recent_10 = learning_data[-10:]
        previous_10 = learning_data[-20:-10] if len(learning_data) >= 20 else learning_data[:-10]
        
        recent_avg = sum(entry["effectiveness_score"] for entry in recent_10) / len(recent_10)
        previous_avg = sum(entry["effectiveness_score"] for entry in previous_10) / len(previous_10)
        
        improvement = recent_avg - previous_avg
        
        return {
            "recent_average": recent_avg,
            "previous_average": previous_avg,
            "improvement": improvement,
            "trend": "improving" if improvement > 0.05 else "stable" if improvement > -0.05 else "declining"
        }
    
    def _extract_preferences(self, learning_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract user preferences from learning data"""
        # This would analyze patterns in successful interactions
        return {
            "preferred_communication_style": "analytical",  # Would be calculated
            "optimal_intensity_range": "moderate_to_high",
            "best_interaction_times": "morning",
            "most_effective_agents": ["BLAZE", "SAGE"]  # Would be calculated
        }


# Export main class
__all__ = ["HybridIntelligenceEngine", "UserProfile", "PersonalizationContext", "PersonalizationResult", "UserArchetype", "PersonalizationMode"]