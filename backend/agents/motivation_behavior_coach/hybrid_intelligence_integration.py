"""
GENESIS NGX Agents - SPARK Hybrid Intelligence Integration
=========================================================

Integration module for the SPARK agent (Motivation & Behavior Coach) with the
Hybrid Intelligence Engine. This module provides specialized personalization
for motivation, behavior change, and psychological coaching.

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


class MotivationType(Enum):
    """Types of motivation for personalization"""
    INTRINSIC = "intrinsic"
    EXTRINSIC = "extrinsic"
    AUTONOMOUS = "autonomous"
    CONTROLLED = "controlled"
    SOCIAL = "social"
    ACHIEVEMENT = "achievement"


class BehaviorStage(Enum):
    """Stages of behavior change (Transtheoretical Model)"""
    PRECONTEMPLATION = "precontemplation"
    CONTEMPLATION = "contemplation"
    PREPARATION = "preparation"
    ACTION = "action"
    MAINTENANCE = "maintenance"
    RELAPSE = "relapse"


class PersonalityType(Enum):
    """Simplified personality types for motivation coaching"""
    COMPETITIVE = "competitive"
    COLLABORATIVE = "collaborative"
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    STRUCTURED = "structured"
    FLEXIBLE = "flexible"


class SPARKHybridIntelligenceIntegration:
    """
    Integration layer between SPARK agent and Hybrid Intelligence Engine
    
    Specialized for motivation and behavior change with advanced personalization:
    - Motivation type identification and adaptation
    - Behavior change stage assessment and guidance
    - Personality-based coaching approaches
    - Archetype-specific motivational strategies
    - Psychological state-aware interventions
    """
    
    def __init__(self):
        """Initialize SPARK Hybrid Intelligence Integration"""
        self.engine = HybridIntelligenceEngine()
        self.integration_name = "SPARK_MOTIVATION_BEHAVIOR_HYBRID_INTELLIGENCE"
        self.version = "1.0.0"
        
        logger.info(f"Initialized {self.integration_name} v{self.version}")
    
    async def personalize_motivational_strategy(
        self,
        user_goal: str,
        user_profile: Dict[str, Any],
        current_challenges: Optional[List[str]] = None
    ) -> PersonalizationResult:
        """
        Personalize motivational approach based on user archetype and psychology
        
        Args:
            user_goal: User's stated goal or objective
            user_profile: Complete user profile
            current_challenges: List of current motivational challenges
            
        Returns:
            PersonalizationResult with personalized motivational strategy
        """
        try:
            # Assess motivation type and behavior stage
            motivation_type = self._assess_motivation_type(user_profile)
            behavior_stage = self._assess_behavior_stage(user_profile, current_challenges)
            personality_type = self._assess_personality_type(user_profile)
            
            # Create motivational personalization context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="motivation_behavior_coach",
                request_type="motivational_strategy",
                session_data={
                    "user_goal": user_goal,
                    "current_challenges": current_challenges or [],
                    "motivation_type": motivation_type.value,
                    "behavior_stage": behavior_stage.value,
                    "personality_type": personality_type.value,
                    "strategy_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute hybrid intelligence personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply motivation-specific enhancements
            enhanced_result = self._apply_motivational_enhancements(
                result, motivation_type, behavior_stage, personality_type
            )
            
            logger.info(f"Motivational strategy personalized: {motivation_type.value}, {behavior_stage.value}, {personality_type.value}")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in personalized motivational strategy: {e}")
            return self._create_fallback_result(user_goal, "motivational_strategy")
    
    async def personalize_habit_formation(
        self,
        target_habit: str,
        user_profile: Dict[str, Any],
        existing_habits: Optional[Dict[str, Any]] = None
    ) -> PersonalizationResult:
        """
        Personalize habit formation approach based on user patterns and archetype
        
        Args:
            target_habit: Habit user wants to develop
            user_profile: Complete user profile
            existing_habits: Current habit patterns and success rates
            
        Returns:
            PersonalizationResult with personalized habit formation plan
        """
        try:
            # Analyze existing habit patterns
            habit_success_patterns = self._analyze_habit_patterns(existing_habits or {})
            optimal_timing = self._determine_optimal_habit_timing(user_profile)
            
            # Create habit formation context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="motivation_behavior_coach",
                request_type="habit_formation",
                session_data={
                    "target_habit": target_habit,
                    "existing_habits": existing_habits or {},
                    "success_patterns": habit_success_patterns,
                    "optimal_timing": optimal_timing,
                    "formation_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply habit-specific adaptations
            adapted_result = self._apply_habit_formation_adaptations(
                result, habit_success_patterns, optimal_timing
            )
            
            logger.info(f"Habit formation personalized for: {target_habit}")
            return adapted_result
            
        except Exception as e:
            logger.error(f"Error in personalized habit formation: {e}")
            return self._create_fallback_result(target_habit, "habit_formation")
    
    async def personalize_behavior_intervention(
        self,
        problematic_behavior: str,
        user_profile: Dict[str, Any],
        intervention_history: Optional[List[Dict[str, Any]]] = None
    ) -> PersonalizationResult:
        """
        Personalize behavior change intervention based on psychology and past attempts
        
        Args:
            problematic_behavior: Behavior that needs to change
            user_profile: Complete user profile
            intervention_history: Previous intervention attempts and outcomes
            
        Returns:
            PersonalizationResult with personalized intervention strategy
        """
        try:
            # Analyze intervention history for patterns
            intervention_insights = self._analyze_intervention_history(intervention_history or [])
            psychological_barriers = self._identify_psychological_barriers(user_profile)
            
            # Create intervention context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="motivation_behavior_coach",
                request_type="behavior_intervention",
                session_data={
                    "problematic_behavior": problematic_behavior,
                    "intervention_history": intervention_history or [],
                    "intervention_insights": intervention_insights,
                    "psychological_barriers": psychological_barriers,
                    "intervention_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply intervention-specific adaptations
            adapted_result = self._apply_intervention_adaptations(
                result, intervention_insights, psychological_barriers
            )
            
            logger.info(f"Behavior intervention personalized for: {problematic_behavior}")
            return adapted_result
            
        except Exception as e:
            logger.error(f"Error in personalized behavior intervention: {e}")
            return self._create_fallback_result(problematic_behavior, "behavior_intervention")
    
    def _assess_motivation_type(self, user_profile: Dict[str, Any]) -> MotivationType:
        """Assess user's primary motivation type from profile"""
        try:
            # Analyze user's goals and past behaviors
            goals = user_profile.get('goals', [])
            past_successes = user_profile.get('past_successes', [])
            preferences = user_profile.get('preferences', {})
            
            # Look for intrinsic vs extrinsic motivation indicators
            intrinsic_indicators = ['personal_growth', 'health', 'wellbeing', 'self_improvement']
            extrinsic_indicators = ['competition', 'recognition', 'rewards', 'social_status']
            
            intrinsic_score = sum(1 for goal in goals if any(ind in str(goal).lower() for ind in intrinsic_indicators))
            extrinsic_score = sum(1 for goal in goals if any(ind in str(goal).lower() for ind in extrinsic_indicators))
            
            if intrinsic_score > extrinsic_score:
                return MotivationType.INTRINSIC
            elif extrinsic_score > intrinsic_score:
                return MotivationType.EXTRINSIC
            else:
                # Check for social vs achievement orientation
                social_indicators = ['team', 'group', 'community', 'friends']
                if any(ind in str(preferences).lower() for ind in social_indicators):
                    return MotivationType.SOCIAL
                else:
                    return MotivationType.ACHIEVEMENT
                    
        except Exception as e:
            logger.warning(f"Could not assess motivation type: {e}")
            return MotivationType.INTRINSIC  # Default to intrinsic
    
    def _assess_behavior_stage(self, user_profile: Dict[str, Any], challenges: Optional[List[str]]) -> BehaviorStage:
        """Assess current stage of behavior change"""
        try:
            # Look for stage indicators in profile and challenges
            current_habits = user_profile.get('current_habits', {})
            habit_consistency = user_profile.get('habit_consistency', 0)
            recent_attempts = user_profile.get('recent_behavior_attempts', [])
            
            # Analyze challenge patterns
            if challenges:
                challenge_text = ' '.join(challenges).lower()
                if 'not sure' in challenge_text or 'don\'t know' in challenge_text:
                    return BehaviorStage.PRECONTEMPLATION
                elif 'thinking about' in challenge_text or 'considering' in challenge_text:
                    return BehaviorStage.CONTEMPLATION
                elif 'planning' in challenge_text or 'ready to start' in challenge_text:
                    return BehaviorStage.PREPARATION
                elif 'struggling' in challenge_text or 'went back' in challenge_text:
                    return BehaviorStage.RELAPSE
            
            # Assess based on habit consistency
            if habit_consistency < 0.3:
                return BehaviorStage.CONTEMPLATION
            elif habit_consistency < 0.6:
                return BehaviorStage.PREPARATION
            elif habit_consistency < 0.8:
                return BehaviorStage.ACTION
            else:
                return BehaviorStage.MAINTENANCE
                
        except Exception as e:
            logger.warning(f"Could not assess behavior stage: {e}")
            return BehaviorStage.PREPARATION  # Default to preparation
    
    def _assess_personality_type(self, user_profile: Dict[str, Any]) -> PersonalityType:
        """Assess personality type for coaching approach"""
        try:
            preferences = user_profile.get('preferences', {})
            communication_style = user_profile.get('communication_style', '')
            work_style = user_profile.get('work_style', '')
            
            # Simple personality assessment based on preferences
            if 'competitive' in str(preferences).lower() or 'challenge' in str(preferences).lower():
                return PersonalityType.COMPETITIVE
            elif 'team' in str(preferences).lower() or 'group' in str(preferences).lower():
                return PersonalityType.COLLABORATIVE
            elif 'data' in str(preferences).lower() or 'analysis' in str(preferences).lower():
                return PersonalityType.ANALYTICAL
            elif 'creative' in str(preferences).lower() or 'intuitive' in str(preferences).lower():
                return PersonalityType.INTUITIVE
            elif 'structured' in str(preferences).lower() or 'organized' in str(preferences).lower():
                return PersonalityType.STRUCTURED
            else:
                return PersonalityType.FLEXIBLE
                
        except Exception as e:
            logger.warning(f"Could not assess personality type: {e}")
            return PersonalityType.FLEXIBLE  # Default to flexible
    
    def _apply_motivational_enhancements(
        self,
        result: PersonalizationResult,
        motivation_type: MotivationType,
        behavior_stage: BehaviorStage,
        personality_type: PersonalityType
    ) -> PersonalizationResult:
        """Apply motivation-specific enhancements to result"""
        
        # Get motivation-specific strategies
        motivation_strategies = self._get_motivation_strategies(motivation_type)
        stage_interventions = self._get_stage_interventions(behavior_stage)
        personality_adaptations = self._get_personality_adaptations(personality_type)
        
        # Enhance content with psychological insights
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'motivation_strategies': motivation_strategies,
            'stage_interventions': stage_interventions,
            'personality_adaptations': personality_adaptations,
            'psychological_profile': {
                'motivation_type': motivation_type.value,
                'behavior_stage': behavior_stage.value,
                'personality_type': personality_type.value
            }
        })
        
        # Enhance physiological modulation with psychological factors
        enhanced_physio = result.physiological_modulation.copy()
        enhanced_physio.update({
            'psychological_state_factor': True,
            'motivation_readiness': behavior_stage.value,
            'personality_alignment': personality_type.value
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=enhanced_physio,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'spark_psychological_enhancement': True,
                'motivation_type': motivation_type.value,
                'behavior_stage': behavior_stage.value,
                'personality_type': personality_type.value
            }
        )
    
    def _analyze_habit_patterns(self, existing_habits: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze existing habit patterns for insights"""
        return {
            'success_rate': existing_habits.get('overall_success_rate', 0.5),
            'best_time_of_day': existing_habits.get('most_successful_time', 'morning'),
            'successful_categories': existing_habits.get('successful_types', ['simple', 'routine']),
            'failure_patterns': existing_habits.get('common_failure_reasons', ['inconsistency']),
            'average_formation_time': existing_habits.get('average_formation_days', 21)
        }
    
    def _determine_optimal_habit_timing(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Determine optimal timing for new habits"""
        schedule = user_profile.get('daily_schedule', {})
        energy_patterns = user_profile.get('energy_patterns', {})
        
        return {
            'recommended_time': energy_patterns.get('peak_time', 'morning'),
            'backup_times': ['evening', 'lunch_break'],
            'frequency_recommendation': 'daily',
            'duration_recommendation': '10-15 minutes'
        }
    
    def _analyze_intervention_history(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze past intervention attempts for patterns"""
        if not history:
            return {'no_history': True}
        
        successful_approaches = [item for item in history if item.get('success', False)]
        failed_approaches = [item for item in history if not item.get('success', True)]
        
        return {
            'successful_methods': [item.get('method') for item in successful_approaches],
            'failed_methods': [item.get('method') for item in failed_approaches],
            'success_rate': len(successful_approaches) / len(history) if history else 0,
            'common_failure_points': [item.get('failure_reason') for item in failed_approaches],
            'optimal_duration': 'varies'  # Could be calculated from successful attempts
        }
    
    def _identify_psychological_barriers(self, user_profile: Dict[str, Any]) -> List[str]:
        """Identify psychological barriers from user profile"""
        barriers = []
        
        # Look for common barrier indicators
        if user_profile.get('stress_level', 'normal') == 'high':
            barriers.append('high_stress')
        if user_profile.get('perfectionism_tendency', False):
            barriers.append('perfectionism')
        if user_profile.get('social_anxiety', False):
            barriers.append('social_anxiety')
        if user_profile.get('past_trauma_related_to_goals', False):
            barriers.append('past_negative_experiences')
        
        return barriers or ['none_identified']
    
    def _apply_habit_formation_adaptations(
        self,
        result: PersonalizationResult,
        patterns: Dict[str, Any],
        timing: Dict[str, Any]
    ) -> PersonalizationResult:
        """Apply habit formation specific adaptations"""
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'habit_formation_plan': {
                'success_patterns': patterns,
                'optimal_timing': timing,
                'personalized_approach': 'archetype_and_pattern_based',
                'formation_strategy': 'progressive_micro_habits'
            }
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=result.physiological_modulation,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'habit_formation_adapted': True
            }
        )
    
    def _apply_intervention_adaptations(
        self,
        result: PersonalizationResult,
        insights: Dict[str, Any],
        barriers: List[str]
    ) -> PersonalizationResult:
        """Apply intervention specific adaptations"""
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'intervention_plan': {
                'historical_insights': insights,
                'psychological_barriers': barriers,
                'adapted_approach': 'barrier_aware_intervention',
                'success_probability': insights.get('success_rate', 0.5)
            }
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=result.physiological_modulation,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'intervention_adapted': True
            }
        )
    
    def _get_motivation_strategies(self, motivation_type: MotivationType) -> Dict[str, Any]:
        """Get strategies based on motivation type"""
        strategies = {
            MotivationType.INTRINSIC: {
                'approach': 'autonomy_mastery_purpose',
                'key_elements': ['personal_growth', 'skill_development', 'meaningful_goals'],
                'communication_style': 'empowering_supportive'
            },
            MotivationType.EXTRINSIC: {
                'approach': 'rewards_recognition_competition',
                'key_elements': ['achievement_badges', 'leaderboards', 'external_validation'],
                'communication_style': 'achievement_focused'
            },
            MotivationType.SOCIAL: {
                'approach': 'community_accountability_support',
                'key_elements': ['group_challenges', 'peer_support', 'social_sharing'],
                'communication_style': 'collaborative_encouraging'
            },
            MotivationType.ACHIEVEMENT: {
                'approach': 'goal_setting_progress_tracking',
                'key_elements': ['clear_milestones', 'progress_metrics', 'personal_records'],
                'communication_style': 'results_oriented'
            }
        }
        return strategies.get(motivation_type, strategies[MotivationType.INTRINSIC])
    
    def _get_stage_interventions(self, stage: BehaviorStage) -> Dict[str, Any]:
        """Get interventions based on behavior change stage"""
        interventions = {
            BehaviorStage.PRECONTEMPLATION: {
                'focus': 'awareness_building',
                'techniques': ['education', 'consciousness_raising', 'self_reevaluation'],
                'timeline': 'weeks_to_months'
            },
            BehaviorStage.CONTEMPLATION: {
                'focus': 'motivation_enhancement',
                'techniques': ['pros_cons_analysis', 'motivational_interviewing', 'goal_clarification'],
                'timeline': 'days_to_weeks'
            },
            BehaviorStage.PREPARATION: {
                'focus': 'action_planning',
                'techniques': ['specific_goal_setting', 'barrier_identification', 'resource_mobilization'],
                'timeline': 'days'
            },
            BehaviorStage.ACTION: {
                'focus': 'behavior_implementation',
                'techniques': ['stimulus_control', 'reinforcement', 'self_monitoring'],
                'timeline': 'daily_weekly'
            },
            BehaviorStage.MAINTENANCE: {
                'focus': 'relapse_prevention',
                'techniques': ['coping_strategies', 'social_support', 'lifestyle_integration'],
                'timeline': 'ongoing'
            },
            BehaviorStage.RELAPSE: {
                'focus': 'recovery_and_learning',
                'techniques': ['relapse_analysis', 'motivation_rebuilding', 'strategy_adjustment'],
                'timeline': 'immediate'
            }
        }
        return interventions.get(stage, interventions[BehaviorStage.PREPARATION])
    
    def _get_personality_adaptations(self, personality_type: PersonalityType) -> Dict[str, Any]:
        """Get adaptations based on personality type"""
        adaptations = {
            PersonalityType.COMPETITIVE: {
                'communication_style': 'challenge_based',
                'motivation_triggers': ['competition', 'achievement', 'winning'],
                'preferred_format': 'gamified_leaderboards'
            },
            PersonalityType.COLLABORATIVE: {
                'communication_style': 'team_oriented',
                'motivation_triggers': ['group_success', 'helping_others', 'belonging'],
                'preferred_format': 'group_activities'
            },
            PersonalityType.ANALYTICAL: {
                'communication_style': 'data_driven',
                'motivation_triggers': ['progress_metrics', 'efficiency', 'optimization'],
                'preferred_format': 'detailed_tracking'
            },
            PersonalityType.INTUITIVE: {
                'communication_style': 'inspirational',
                'motivation_triggers': ['creativity', 'exploration', 'possibility'],
                'preferred_format': 'flexible_approach'
            },
            PersonalityType.STRUCTURED: {
                'communication_style': 'organized_systematic',
                'motivation_triggers': ['routine', 'predictability', 'planning'],
                'preferred_format': 'detailed_schedules'
            },
            PersonalityType.FLEXIBLE: {
                'communication_style': 'adaptive_varied',
                'motivation_triggers': ['variety', 'spontaneity', 'freedom'],
                'preferred_format': 'multiple_options'
            }
        }
        return adaptations.get(personality_type, adaptations[PersonalityType.FLEXIBLE])
    
    def _create_fallback_result(self, data: Any, request_type: str) -> PersonalizationResult:
        """Create fallback result when personalization fails"""
        return PersonalizationResult(
            archetype_adaptation={
                'user_archetype': UserArchetype.PRIME,  # Default
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
async def personalize_motivation_coaching(
    user_goal: str,
    user_profile: Dict[str, Any],
    coaching_type: str = "motivational_strategy",
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Complete motivation coaching personalization workflow
    
    Args:
        user_goal: User's goal or target behavior
        user_profile: Complete user profile
        coaching_type: Type of coaching needed
        additional_data: Additional context data
        
    Returns:
        Complete personalized coaching strategy
    """
    integration = SPARKHybridIntelligenceIntegration()
    
    try:
        if coaching_type == "motivational_strategy":
            result = await integration.personalize_motivational_strategy(
                user_goal, user_profile, additional_data.get('challenges', []) if additional_data else None
            )
        elif coaching_type == "habit_formation":
            result = await integration.personalize_habit_formation(
                user_goal, user_profile, additional_data.get('existing_habits') if additional_data else None
            )
        elif coaching_type == "behavior_intervention":
            result = await integration.personalize_behavior_intervention(
                user_goal, user_profile, additional_data.get('intervention_history') if additional_data else None
            )
        else:
            result = await integration.personalize_motivational_strategy(user_goal, user_profile)
        
        return {
            'personalized_coaching': result.personalized_content,
            'psychological_insights': result.archetype_adaptation,
            'behavioral_considerations': result.physiological_modulation,
            'confidence_score': result.confidence_score,
            'metadata': result.personalization_metadata
        }
        
    except Exception as e:
        logger.error(f"Error in motivation coaching personalization: {e}")
        return {
            'error': str(e),
            'fallback_mode': True,
            'timestamp': datetime.now().isoformat()
        }


# Export the integration class
__all__ = ['SPARKHybridIntelligenceIntegration', 'personalize_motivation_coaching']