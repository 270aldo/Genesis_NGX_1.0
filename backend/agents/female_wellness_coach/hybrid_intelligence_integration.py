"""
GENESIS NGX Agents - LUNA Hybrid Intelligence Integration
========================================================

Integration module for the LUNA agent (Female Wellness Coach) with the
Hybrid Intelligence Engine. This module provides specialized personalization
for female health, hormonal cycles, and reproductive wellness.

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-10
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import logging
from enum import Enum

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
    UserBiometrics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MenstrualPhase(Enum):
    """Menstrual cycle phases for personalization"""
    MENSTRUAL = "menstrual"
    FOLLICULAR = "follicular"
    OVULATORY = "ovulatory"
    LUTEAL = "luteal"
    UNKNOWN = "unknown"


class LifeStage(Enum):
    """Female life stages for personalization"""
    REPRODUCTIVE = "reproductive"
    PERIMENOPAUSE = "perimenopause"
    MENOPAUSE = "menopause"
    POSTMENOPAUSE = "postmenopause"
    PREGNANCY = "pregnancy"
    POSTPARTUM = "postpartum"


class LUNAHybridIntelligenceIntegration:
    """
    Integration layer between LUNA agent and Hybrid Intelligence Engine
    
    Specialized for female health with advanced personalization considering:
    - Menstrual cycle phases and hormonal fluctuations
    - Life stage transitions (pregnancy, menopause, etc.)
    - Female-specific biometrics and wellness patterns
    - Archetype adaptation for female health goals
    """
    
    def __init__(self):
        """Initialize LUNA Hybrid Intelligence Integration"""
        self.engine = HybridIntelligenceEngine()
        self.integration_name = "LUNA_FEMALE_WELLNESS_HYBRID_INTELLIGENCE"
        self.version = "1.0.0"
        
        logger.info(f"Initialized {self.integration_name} v{self.version}")
    
    async def personalize_hormonal_guidance(
        self,
        user_query: str,
        user_profile: Dict[str, Any],
        cycle_data: Optional[Dict[str, Any]] = None
    ) -> PersonalizationResult:
        """
        Personalize guidance based on hormonal cycle and archetype
        
        Args:
            user_query: User's health query
            user_profile: Complete user profile
            cycle_data: Menstrual cycle tracking data
            
        Returns:
            PersonalizationResult with cycle-aware guidance
        """
        try:
            # Determine current menstrual phase
            current_phase = self._determine_cycle_phase(cycle_data or {})
            life_stage = self._determine_life_stage(user_profile)
            
            # Create hormonal personalization context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="female_wellness_coach",
                request_type="hormonal_guidance",
                session_data={
                    "user_query": user_query,
                    "menstrual_phase": current_phase.value,
                    "life_stage": life_stage.value,
                    "cycle_data": cycle_data or {},
                    "guidance_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute hybrid intelligence personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply female-specific modulation
            enhanced_result = self._apply_hormonal_modulation(result, current_phase, life_stage)
            
            logger.info(f"Hormonal guidance personalized for {current_phase.value} phase, {life_stage.value} stage")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in personalized hormonal guidance: {e}")
            return self._create_fallback_result(user_query, "hormonal_guidance")
    
    async def personalize_training_adaptation(
        self,
        training_request: Dict[str, Any],
        user_profile: Dict[str, Any],
        hormonal_state: Dict[str, Any]
    ) -> PersonalizationResult:
        """
        Personalize training recommendations based on hormonal fluctuations
        
        Args:
            training_request: Requested training parameters
            user_profile: Complete user profile
            hormonal_state: Current hormonal indicators
            
        Returns:
            PersonalizationResult with cycle-adapted training
        """
        try:
            current_phase = self._determine_cycle_phase(hormonal_state)
            
            # Create training personalization context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="female_wellness_coach",
                request_type="training_adaptation",
                session_data={
                    "training_request": training_request,
                    "hormonal_state": hormonal_state,
                    "cycle_phase": current_phase.value,
                    "adaptation_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply cycle-specific training adaptations
            adapted_result = self._apply_training_cycle_adaptations(result, current_phase)
            
            logger.info(f"Training adaptation personalized for {current_phase.value} phase")
            return adapted_result
            
        except Exception as e:
            logger.error(f"Error in personalized training adaptation: {e}")
            return self._create_fallback_result(training_request, "training_adaptation")
    
    async def personalize_nutritional_support(
        self,
        nutrition_query: str,
        user_profile: Dict[str, Any],
        symptoms: Optional[List[str]] = None
    ) -> PersonalizationResult:
        """
        Personalize nutritional guidance for female-specific needs
        
        Args:
            nutrition_query: Nutrition-related query
            user_profile: Complete user profile
            symptoms: Current symptoms or concerns
            
        Returns:
            PersonalizationResult with female-optimized nutrition
        """
        try:
            life_stage = self._determine_life_stage(user_profile)
            
            # Create nutrition personalization context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="female_wellness_coach",
                request_type="nutritional_support",
                session_data={
                    "nutrition_query": nutrition_query,
                    "symptoms": symptoms or [],
                    "life_stage": life_stage.value,
                    "nutrition_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply female-specific nutritional considerations
            enhanced_result = self._apply_nutritional_adaptations(result, life_stage, symptoms)
            
            logger.info(f"Nutritional support personalized for {life_stage.value} stage")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in personalized nutritional support: {e}")
            return self._create_fallback_result(nutrition_query, "nutritional_support")
    
    def _determine_cycle_phase(self, cycle_data: Dict[str, Any]) -> MenstrualPhase:
        """Determine current menstrual cycle phase from tracking data"""
        try:
            if not cycle_data:
                return MenstrualPhase.UNKNOWN
            
            last_period = cycle_data.get('last_period_date')
            cycle_length = cycle_data.get('average_cycle_length', 28)
            
            if not last_period:
                return MenstrualPhase.UNKNOWN
            
            # Calculate days since last period
            if isinstance(last_period, str):
                last_period_date = datetime.fromisoformat(last_period.replace('Z', '+00:00'))
            else:
                last_period_date = last_period
            
            days_since = (datetime.now() - last_period_date).days
            
            # Determine phase based on cycle day
            if days_since <= 5:
                return MenstrualPhase.MENSTRUAL
            elif days_since <= 13:
                return MenstrualPhase.FOLLICULAR
            elif days_since <= 16:
                return MenstrualPhase.OVULATORY
            elif days_since <= cycle_length:
                return MenstrualPhase.LUTEAL
            else:
                return MenstrualPhase.FOLLICULAR  # New cycle started
                
        except Exception as e:
            logger.warning(f"Could not determine cycle phase: {e}")
            return MenstrualPhase.UNKNOWN
    
    def _determine_life_stage(self, user_profile: Dict[str, Any]) -> LifeStage:
        """Determine current life stage from user profile"""
        try:
            age = user_profile.get('age', 30)
            pregnancy_status = user_profile.get('pregnancy_status', 'not_pregnant')
            menopause_status = user_profile.get('menopause_status', 'premenopausal')
            
            if pregnancy_status == 'pregnant':
                return LifeStage.PREGNANCY
            elif pregnancy_status == 'postpartum':
                return LifeStage.POSTPARTUM
            elif menopause_status == 'postmenopausal':
                return LifeStage.POSTMENOPAUSE
            elif menopause_status == 'menopausal':
                return LifeStage.MENOPAUSE
            elif menopause_status == 'perimenopausal' or age >= 45:
                return LifeStage.PERIMENOPAUSE
            else:
                return LifeStage.REPRODUCTIVE
                
        except Exception as e:
            logger.warning(f"Could not determine life stage: {e}")
            return LifeStage.REPRODUCTIVE
    
    def _apply_hormonal_modulation(
        self,
        result: PersonalizationResult,
        cycle_phase: MenstrualPhase,
        life_stage: LifeStage
    ) -> PersonalizationResult:
        """Apply hormonal-specific modulations to personalization result"""
        
        # Get cycle-specific adaptations
        cycle_adaptations = self._get_cycle_adaptations(cycle_phase)
        life_stage_adaptations = self._get_life_stage_adaptations(life_stage)
        
        # Enhance the result with hormonal context
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'cycle_adaptations': cycle_adaptations,
            'life_stage_adaptations': life_stage_adaptations,
            'hormonal_considerations': {
                'current_phase': cycle_phase.value,
                'life_stage': life_stage.value,
                'modulation_applied': True
            }
        })
        
        # Update physiological modulation
        enhanced_physio = result.physiological_modulation.copy()
        enhanced_physio.update({
            'hormonal_phase': cycle_phase.value,
            'life_stage_factor': life_stage.value,
            'female_specific_modulation': True
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=enhanced_physio,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'luna_hormonal_modulation': True,
                'cycle_phase': cycle_phase.value,
                'life_stage': life_stage.value
            }
        )
    
    def _apply_training_cycle_adaptations(
        self,
        result: PersonalizationResult,
        cycle_phase: MenstrualPhase
    ) -> PersonalizationResult:
        """Apply cycle-specific training adaptations"""
        
        training_adaptations = {
            MenstrualPhase.MENSTRUAL: {
                'intensity_modifier': 0.7,
                'recommended_types': ['gentle_yoga', 'walking', 'light_strength'],
                'avoid': ['high_intensity', 'heavy_lifting'],
                'focus': 'rest_and_restoration'
            },
            MenstrualPhase.FOLLICULAR: {
                'intensity_modifier': 0.9,
                'recommended_types': ['cardio', 'strength_training', 'skill_development'],
                'energy_level': 'building',
                'focus': 'progressive_loading'
            },
            MenstrualPhase.OVULATORY: {
                'intensity_modifier': 1.1,
                'recommended_types': ['hiit', 'competitive_sports', 'pr_attempts'],
                'energy_level': 'peak',
                'focus': 'maximum_performance'
            },
            MenstrualPhase.LUTEAL: {
                'intensity_modifier': 0.8,
                'recommended_types': ['strength_training', 'pilates', 'moderate_cardio'],
                'considerations': ['increased_recovery_needs', 'nutrition_support'],
                'focus': 'consistency_over_intensity'
            }
        }
        
        adaptations = training_adaptations.get(cycle_phase, {})
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content['training_cycle_adaptations'] = adaptations
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=result.physiological_modulation,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'training_cycle_adapted': True
            }
        )
    
    def _apply_nutritional_adaptations(
        self,
        result: PersonalizationResult,
        life_stage: LifeStage,
        symptoms: Optional[List[str]]
    ) -> PersonalizationResult:
        """Apply life-stage and symptom-specific nutritional adaptations"""
        
        nutritional_focus = {
            LifeStage.REPRODUCTIVE: {
                'key_nutrients': ['iron', 'folate', 'vitamin_d', 'omega3'],
                'considerations': ['cycle_support', 'energy_stability']
            },
            LifeStage.PREGNANCY: {
                'key_nutrients': ['folate', 'iron', 'calcium', 'dha'],
                'considerations': ['fetal_development', 'maternal_health']
            },
            LifeStage.PERIMENOPAUSE: {
                'key_nutrients': ['calcium', 'vitamin_d', 'magnesium', 'phytoestrogens'],
                'considerations': ['bone_health', 'hormonal_balance']
            },
            LifeStage.MENOPAUSE: {
                'key_nutrients': ['calcium', 'vitamin_d', 'vitamin_e', 'omega3'],
                'considerations': ['cardiovascular_health', 'cognitive_support']
            }
        }
        
        focus = nutritional_focus.get(life_stage, {})
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'nutritional_focus': focus,
            'symptom_considerations': symptoms or [],
            'life_stage_nutrition': life_stage.value
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=result.physiological_modulation,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'nutritional_adaptation_applied': True
            }
        )
    
    def _get_cycle_adaptations(self, phase: MenstrualPhase) -> Dict[str, Any]:
        """Get cycle-specific adaptations for guidance"""
        adaptations = {
            MenstrualPhase.MENSTRUAL: {
                'energy_pattern': 'low_conserve',
                'emotional_support': 'nurturing_comfort',
                'physical_focus': 'pain_relief_rest',
                'nutrition_emphasis': 'iron_support_hydration'
            },
            MenstrualPhase.FOLLICULAR: {
                'energy_pattern': 'building_momentum',
                'emotional_support': 'motivation_encouragement',
                'physical_focus': 'strength_building',
                'nutrition_emphasis': 'protein_complex_carbs'
            },
            MenstrualPhase.OVULATORY: {
                'energy_pattern': 'peak_performance',
                'emotional_support': 'confidence_empowerment',
                'physical_focus': 'maximum_output',
                'nutrition_emphasis': 'sustained_energy'
            },
            MenstrualPhase.LUTEAL: {
                'energy_pattern': 'stable_consistent',
                'emotional_support': 'balance_grounding',
                'physical_focus': 'strength_maintenance',
                'nutrition_emphasis': 'mood_support_magnesium'
            }
        }
        return adaptations.get(phase, {})
    
    def _get_life_stage_adaptations(self, stage: LifeStage) -> Dict[str, Any]:
        """Get life-stage-specific adaptations"""
        adaptations = {
            LifeStage.REPRODUCTIVE: {
                'health_priorities': ['fertility', 'energy', 'prevention'],
                'common_concerns': ['cycle_irregularities', 'pms', 'energy_fluctuations']
            },
            LifeStage.PREGNANCY: {
                'health_priorities': ['fetal_health', 'maternal_wellbeing', 'safe_exercise'],
                'common_concerns': ['morning_sickness', 'fatigue', 'body_changes']
            },
            LifeStage.PERIMENOPAUSE: {
                'health_priorities': ['hormonal_balance', 'bone_health', 'sleep_quality'],
                'common_concerns': ['irregular_cycles', 'hot_flashes', 'mood_changes']
            },
            LifeStage.MENOPAUSE: {
                'health_priorities': ['cardiovascular_health', 'bone_density', 'cognitive_health'],
                'common_concerns': ['hot_flashes', 'sleep_disturbances', 'weight_changes']
            }
        }
        return adaptations.get(stage, {})
    
    def _create_fallback_result(self, data: Any, request_type: str) -> PersonalizationResult:
        """Create fallback result when personalization fails"""
        return PersonalizationResult(
            archetype_adaptation={
                'user_archetype': UserArchetype.LONGEVITY,  # Default for female wellness
                'adaptation_strategy': 'fallback_default',
                'request_type': request_type
            },
            physiological_modulation={
                'modulation_applied': False,
                'fallback_reason': 'personalization_error'
            },
            personalized_content={'original_data': str(data)},
            confidence_score=0.5,
            personalization_metadata={
                'fallback_mode': True,
                'timestamp': datetime.now().isoformat()
            }
        )


# Integration functions for easy usage
async def personalize_female_wellness(
    user_query: str,
    user_profile: Dict[str, Any],
    cycle_data: Optional[Dict[str, Any]] = None,
    request_type: str = "general_wellness"
) -> Dict[str, Any]:
    """
    Complete female wellness personalization workflow
    
    Args:
        user_query: User's wellness query
        user_profile: Complete user profile
        cycle_data: Menstrual cycle tracking data
        request_type: Type of wellness request
        
    Returns:
        Complete personalized wellness strategy
    """
    integration = LUNAHybridIntelligenceIntegration()
    
    try:
        if request_type == "hormonal_guidance":
            result = await integration.personalize_hormonal_guidance(
                user_query, user_profile, cycle_data
            )
        elif request_type == "training_adaptation":
            result = await integration.personalize_training_adaptation(
                {'query': user_query}, user_profile, cycle_data or {}
            )
        elif request_type == "nutritional_support":
            result = await integration.personalize_nutritional_support(
                user_query, user_profile
            )
        else:
            result = await integration.personalize_hormonal_guidance(
                user_query, user_profile, cycle_data
            )
        
        return {
            'personalized_guidance': result.personalized_content,
            'archetype_insights': result.archetype_adaptation,
            'hormonal_considerations': result.physiological_modulation,
            'confidence_score': result.confidence_score,
            'metadata': result.personalization_metadata
        }
        
    except Exception as e:
        logger.error(f"Error in female wellness personalization: {e}")
        return {
            'error': str(e),
            'fallback_mode': True,
            'timestamp': datetime.now().isoformat()
        }


# Export the integration class
__all__ = ['LUNAHybridIntelligenceIntegration', 'personalize_female_wellness']