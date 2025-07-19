"""
GENESIS NGX Agents - STELLA Hybrid Intelligence Integration
=========================================================

Integration module for the STELLA agent (Progress Tracker) with the
Hybrid Intelligence Engine. This module provides specialized personalization
for progress tracking, analytics, and goal achievement monitoring.

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
import statistics

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


class ProgressMetricType(Enum):
    """Types of progress metrics for personalization"""
    PHYSIOLOGICAL = "physiological"
    PERFORMANCE = "performance"
    BEHAVIORAL = "behavioral"
    PSYCHOLOGICAL = "psychological"
    LIFESTYLE = "lifestyle"
    COMPOSITE = "composite"


class ProgressTrend(Enum):
    """Progress trend classifications"""
    ACCELERATING = "accelerating"
    STEADY = "steady"
    PLATEAUING = "plateauing"
    DECLINING = "declining"
    FLUCTUATING = "fluctuating"
    INSUFFICIENT_DATA = "insufficient_data"


class GoalTimeframe(Enum):
    """Goal timeframe categories"""
    SHORT_TERM = "short_term"      # 1-4 weeks
    MEDIUM_TERM = "medium_term"    # 1-3 months
    LONG_TERM = "long_term"        # 3+ months
    ONGOING = "ongoing"            # Lifestyle goals


class STELLAHybridIntelligenceIntegration:
    """
    Integration layer between STELLA agent and Hybrid Intelligence Engine
    
    Specialized for progress tracking and analytics with advanced personalization:
    - Archetype-specific progress visualization and reporting
    - Physiological state-aware progress interpretation
    - Personalized goal setting and milestone creation
    - Adaptive feedback based on progress patterns
    - Motivation-aligned progress communication
    """
    
    def __init__(self):
        """Initialize STELLA Hybrid Intelligence Integration"""
        self.engine = HybridIntelligenceEngine()
        self.integration_name = "STELLA_PROGRESS_TRACKER_HYBRID_INTELLIGENCE"
        self.version = "1.0.0"
        
        logger.info(f"Initialized {self.integration_name} v{self.version}")
    
    async def personalize_progress_analysis(
        self,
        progress_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        analysis_period: Optional[str] = "30_days"
    ) -> PersonalizationResult:
        """
        Personalize progress analysis based on user archetype and preferences
        
        Args:
            progress_data: Raw progress data across multiple metrics
            user_profile: Complete user profile
            analysis_period: Time period for analysis
            
        Returns:
            PersonalizationResult with personalized progress insights
        """
        try:
            # Analyze progress patterns
            progress_trends = self._analyze_progress_trends(progress_data)
            key_metrics = self._identify_key_metrics(progress_data, user_profile)
            achievement_rate = self._calculate_achievement_rate(progress_data)
            
            # Create progress analysis context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="progress_tracker",
                request_type="progress_analysis",
                session_data={
                    "progress_data": progress_data,
                    "analysis_period": analysis_period,
                    "progress_trends": progress_trends,
                    "key_metrics": key_metrics,
                    "achievement_rate": achievement_rate,
                    "analysis_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute hybrid intelligence personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply progress-specific enhancements
            enhanced_result = self._apply_progress_analysis_enhancements(
                result, progress_trends, key_metrics, achievement_rate
            )
            
            logger.info(f"Progress analysis personalized for {len(key_metrics)} key metrics")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in personalized progress analysis: {e}")
            return self._create_fallback_result(progress_data, "progress_analysis")
    
    async def personalize_goal_setting(
        self,
        goal_request: Dict[str, Any],
        user_profile: Dict[str, Any],
        historical_performance: Optional[Dict[str, Any]] = None
    ) -> PersonalizationResult:
        """
        Personalize goal setting based on archetype and historical performance
        
        Args:
            goal_request: User's goal setting request
            user_profile: Complete user profile
            historical_performance: Past goal achievement data
            
        Returns:
            PersonalizationResult with personalized goal recommendations
        """
        try:
            # Analyze historical performance patterns
            performance_insights = self._analyze_historical_performance(historical_performance or {})
            optimal_challenge_level = self._determine_optimal_challenge_level(user_profile, performance_insights)
            timeframe_recommendations = self._recommend_goal_timeframes(user_profile)
            
            # Create goal setting context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="progress_tracker",
                request_type="goal_setting",
                session_data={
                    "goal_request": goal_request,
                    "historical_performance": historical_performance or {},
                    "performance_insights": performance_insights,
                    "optimal_challenge_level": optimal_challenge_level,
                    "timeframe_recommendations": timeframe_recommendations,
                    "goal_setting_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            # Apply goal-specific adaptations
            adapted_result = self._apply_goal_setting_adaptations(
                result, optimal_challenge_level, timeframe_recommendations
            )
            
            logger.info(f"Goal setting personalized with {optimal_challenge_level} challenge level")
            return adapted_result
            
        except Exception as e:
            logger.error(f"Error in personalized goal setting: {e}")
            return self._create_fallback_result(goal_request, "goal_setting")
    
    async def personalize_progress_visualization(
        self,
        data_visualization_request: Dict[str, Any],
        user_profile: Dict[str, Any],
        preferred_formats: Optional[List[str]] = None
    ) -> PersonalizationResult:
        """
        Personalize progress visualization based on archetype and preferences
        
        Args:
            data_visualization_request: Request for specific visualizations
            user_profile: Complete user profile
            preferred_formats: User's preferred visualization formats
            
        Returns:
            PersonalizationResult with personalized visualization strategy
        """
        try:
            # Determine optimal visualization approaches
            archetype_viz_preferences = self._get_archetype_visualization_preferences(user_profile)
            data_complexity_level = self._assess_data_complexity_preference(user_profile)
            motivational_elements = self._identify_motivational_visualization_elements(user_profile)
            
            # Create visualization context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="progress_tracker",
                request_type="progress_visualization",
                session_data={
                    "visualization_request": data_visualization_request,
                    "preferred_formats": preferred_formats or [],
                    "archetype_preferences": archetype_viz_preferences,
                    "complexity_level": data_complexity_level,
                    "motivational_elements": motivational_elements,
                    "visualization_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.STANDARD
            )
            
            # Apply visualization-specific adaptations
            adapted_result = self._apply_visualization_adaptations(
                result, archetype_viz_preferences, data_complexity_level, motivational_elements
            )
            
            logger.info(f"Progress visualization personalized for {data_complexity_level} complexity")
            return adapted_result
            
        except Exception as e:
            logger.error(f"Error in personalized progress visualization: {e}")
            return self._create_fallback_result(data_visualization_request, "progress_visualization")
    
    def _analyze_progress_trends(self, progress_data: Dict[str, Any]) -> Dict[str, ProgressTrend]:
        """Analyze trends in progress data across different metrics"""
        trends = {}
        
        try:
            for metric_name, metric_data in progress_data.items():
                if isinstance(metric_data, list) and len(metric_data) >= 3:
                    # Calculate trend for time series data
                    values = [float(point.get('value', 0)) for point in metric_data if 'value' in point]
                    if len(values) >= 3:
                        trend = self._calculate_trend(values)
                        trends[metric_name] = trend
                    else:
                        trends[metric_name] = ProgressTrend.INSUFFICIENT_DATA
                else:
                    trends[metric_name] = ProgressTrend.INSUFFICIENT_DATA
        except Exception as e:
            logger.warning(f"Error analyzing progress trends: {e}")
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> ProgressTrend:
        """Calculate trend from a series of values"""
        if len(values) < 3:
            return ProgressTrend.INSUFFICIENT_DATA
        
        try:
            # Calculate moving averages to smooth out noise
            if len(values) >= 5:
                recent_avg = statistics.mean(values[-3:])
                earlier_avg = statistics.mean(values[:3])
                middle_avg = statistics.mean(values[len(values)//2-1:len(values)//2+2])
                
                # Determine trend pattern
                if recent_avg > earlier_avg * 1.1 and middle_avg > earlier_avg * 1.05:
                    return ProgressTrend.ACCELERATING
                elif recent_avg < earlier_avg * 0.9 and middle_avg < earlier_avg * 0.95:
                    return ProgressTrend.DECLINING
                elif abs(recent_avg - earlier_avg) / earlier_avg < 0.05:
                    return ProgressTrend.PLATEAUING
                else:
                    # Check for fluctuation
                    variance = statistics.variance(values)
                    mean_val = statistics.mean(values)
                    cv = variance / (mean_val ** 2) if mean_val != 0 else 0
                    
                    if cv > 0.2:  # High coefficient of variation
                        return ProgressTrend.FLUCTUATING
                    else:
                        return ProgressTrend.STEADY
            else:
                # Simple comparison for shorter series
                if values[-1] > values[0] * 1.1:
                    return ProgressTrend.ACCELERATING
                elif values[-1] < values[0] * 0.9:
                    return ProgressTrend.DECLINING
                else:
                    return ProgressTrend.STEADY
                    
        except Exception as e:
            logger.warning(f"Error calculating trend: {e}")
            return ProgressTrend.INSUFFICIENT_DATA
    
    def _identify_key_metrics(self, progress_data: Dict[str, Any], user_profile: Dict[str, Any]) -> List[str]:
        """Identify the most important metrics based on user goals and archetype"""
        user_goals = user_profile.get('goals', [])
        archetype = user_profile.get('archetype', 'PRIME')
        
        # Priority metrics by archetype
        archetype_priorities = {
            'PRIME': ['performance', 'efficiency', 'strength', 'power', 'speed'],
            'LONGEVITY': ['health', 'wellness', 'sustainability', 'recovery', 'consistency']
        }
        
        priority_keywords = archetype_priorities.get(archetype, archetype_priorities['PRIME'])
        
        # Score metrics based on relevance
        metric_scores = {}
        for metric_name in progress_data.keys():
            score = 0
            metric_lower = metric_name.lower()
            
            # Score based on archetype priorities
            for keyword in priority_keywords:
                if keyword in metric_lower:
                    score += 3
            
            # Score based on user goals
            for goal in user_goals:
                goal_lower = str(goal).lower()
                if any(word in metric_lower for word in goal_lower.split()):
                    score += 2
            
            # Score based on data quality
            if isinstance(progress_data[metric_name], list) and len(progress_data[metric_name]) > 5:
                score += 1
            
            metric_scores[metric_name] = score
        
        # Return top scoring metrics
        sorted_metrics = sorted(metric_scores.items(), key=lambda x: x[1], reverse=True)
        return [metric for metric, score in sorted_metrics[:5] if score > 0]
    
    def _calculate_achievement_rate(self, progress_data: Dict[str, Any]) -> float:
        """Calculate overall achievement rate from progress data"""
        try:
            total_goals = 0
            achieved_goals = 0
            
            for metric_name, metric_data in progress_data.items():
                if isinstance(metric_data, dict) and 'target' in metric_data and 'current' in metric_data:
                    total_goals += 1
                    target = float(metric_data['target'])
                    current = float(metric_data['current'])
                    
                    # Consider achieved if within 90% of target
                    if current >= target * 0.9:
                        achieved_goals += 1
            
            return achieved_goals / total_goals if total_goals > 0 else 0.5
            
        except Exception as e:
            logger.warning(f"Error calculating achievement rate: {e}")
            return 0.5
    
    def _analyze_historical_performance(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze historical performance patterns"""
        if not historical_data:
            return {'no_history': True}
        
        try:
            insights = {
                'average_goal_completion_time': historical_data.get('avg_completion_days', 30),
                'success_rate': historical_data.get('success_rate', 0.7),
                'preferred_goal_types': historical_data.get('successful_goal_types', []),
                'challenging_areas': historical_data.get('challenging_areas', []),
                'optimal_goal_difficulty': historical_data.get('optimal_difficulty', 'moderate')
            }
            
            # Calculate consistency score
            completion_times = historical_data.get('completion_times', [])
            if completion_times:
                cv = statistics.stdev(completion_times) / statistics.mean(completion_times)
                insights['consistency_score'] = max(0, 1 - cv)
            else:
                insights['consistency_score'] = 0.5
            
            return insights
            
        except Exception as e:
            logger.warning(f"Error analyzing historical performance: {e}")
            return {'analysis_error': True}
    
    def _determine_optimal_challenge_level(self, user_profile: Dict[str, Any], performance_insights: Dict[str, Any]) -> str:
        """Determine optimal challenge level for new goals"""
        try:
            archetype = user_profile.get('archetype', 'PRIME')
            success_rate = performance_insights.get('success_rate', 0.7)
            consistency_score = performance_insights.get('consistency_score', 0.5)
            
            # PRIME users generally prefer higher challenge
            if archetype == 'PRIME':
                if success_rate > 0.8 and consistency_score > 0.7:
                    return 'high'
                elif success_rate > 0.6:
                    return 'moderate_high'
                else:
                    return 'moderate'
            else:  # LONGEVITY
                if success_rate > 0.8 and consistency_score > 0.7:
                    return 'moderate_high'
                elif success_rate > 0.6:
                    return 'moderate'
                else:
                    return 'moderate_low'
                    
        except Exception as e:
            logger.warning(f"Error determining challenge level: {e}")
            return 'moderate'
    
    def _recommend_goal_timeframes(self, user_profile: Dict[str, Any]) -> Dict[str, str]:
        """Recommend optimal timeframes for different types of goals"""
        archetype = user_profile.get('archetype', 'PRIME')
        lifestyle = user_profile.get('lifestyle', {})
        
        if archetype == 'PRIME':
            return {
                'fitness_goals': 'medium_term',
                'skill_goals': 'short_term',
                'habit_goals': 'short_term',
                'health_goals': 'medium_term'
            }
        else:  # LONGEVITY
            return {
                'fitness_goals': 'long_term',
                'skill_goals': 'medium_term', 
                'habit_goals': 'medium_term',
                'health_goals': 'long_term'
            }
    
    def _get_archetype_visualization_preferences(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get visualization preferences based on user archetype"""
        archetype = user_profile.get('archetype', 'PRIME')
        
        if archetype == 'PRIME':
            return {
                'preferred_charts': ['line_charts', 'bar_charts', 'performance_dashboards'],
                'data_density': 'high',
                'focus_areas': ['performance_metrics', 'efficiency_gains', 'competitive_comparisons'],
                'color_scheme': 'high_contrast',
                'update_frequency': 'real_time'
            }
        else:  # LONGEVITY
            return {
                'preferred_charts': ['trend_lines', 'progress_circles', 'wellness_summaries'],
                'data_density': 'moderate',
                'focus_areas': ['wellness_trends', 'consistency_patterns', 'holistic_progress'],
                'color_scheme': 'calming',
                'update_frequency': 'daily_weekly'
            }
    
    def _assess_data_complexity_preference(self, user_profile: Dict[str, Any]) -> str:
        """Assess user's preference for data complexity in visualizations"""
        technical_background = user_profile.get('technical_background', False)
        data_comfort_level = user_profile.get('data_comfort_level', 'moderate')
        archetype = user_profile.get('archetype', 'PRIME')
        
        if technical_background and data_comfort_level == 'high':
            return 'high'
        elif archetype == 'PRIME' and data_comfort_level != 'low':
            return 'moderate_high'
        elif data_comfort_level == 'low':
            return 'low'
        else:
            return 'moderate'
    
    def _identify_motivational_visualization_elements(self, user_profile: Dict[str, Any]) -> List[str]:
        """Identify motivational elements to include in visualizations"""
        motivation_style = user_profile.get('motivation_style', 'achievement')
        archetype = user_profile.get('archetype', 'PRIME')
        
        elements = []
        
        if motivation_style == 'achievement' or archetype == 'PRIME':
            elements.extend(['progress_badges', 'milestone_markers', 'performance_comparisons'])
        
        if motivation_style == 'social':
            elements.extend(['social_comparisons', 'group_challenges', 'shared_achievements'])
        
        if archetype == 'LONGEVITY':
            elements.extend(['consistency_streaks', 'wellness_celebrations', 'sustainable_progress'])
        
        # Always include basic motivational elements
        elements.extend(['goal_proximity', 'positive_reinforcement'])
        
        return list(set(elements))  # Remove duplicates
    
    def _apply_progress_analysis_enhancements(
        self,
        result: PersonalizationResult,
        trends: Dict[str, ProgressTrend],
        key_metrics: List[str],
        achievement_rate: float
    ) -> PersonalizationResult:
        """Apply progress analysis specific enhancements"""
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'progress_analysis': {
                'trends': {metric: trend.value for metric, trend in trends.items()},
                'key_metrics': key_metrics,
                'achievement_rate': achievement_rate,
                'analysis_quality': 'high' if len(key_metrics) > 3 else 'moderate'
            },
            'actionable_insights': self._generate_actionable_insights(trends, achievement_rate),
            'next_focus_areas': key_metrics[:3]
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=result.physiological_modulation,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'stella_progress_analysis_applied': True,
                'key_metrics_count': len(key_metrics)
            }
        )
    
    def _apply_goal_setting_adaptations(
        self,
        result: PersonalizationResult,
        challenge_level: str,
        timeframe_recommendations: Dict[str, str]
    ) -> PersonalizationResult:
        """Apply goal setting specific adaptations"""
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'goal_setting_strategy': {
                'optimal_challenge_level': challenge_level,
                'timeframe_recommendations': timeframe_recommendations,
                'goal_structuring_approach': 'smart_goals_plus',
                'milestone_frequency': 'weekly' if challenge_level in ['high', 'moderate_high'] else 'bi_weekly'
            }
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=result.physiological_modulation,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'stella_goal_setting_adapted': True,
                'challenge_level': challenge_level
            }
        )
    
    def _apply_visualization_adaptations(
        self,
        result: PersonalizationResult,
        viz_preferences: Dict[str, Any],
        complexity_level: str,
        motivational_elements: List[str]
    ) -> PersonalizationResult:
        """Apply visualization specific adaptations"""
        
        enhanced_content = result.personalized_content.copy()
        enhanced_content.update({
            'visualization_strategy': {
                'preferences': viz_preferences,
                'complexity_level': complexity_level,
                'motivational_elements': motivational_elements,
                'adaptive_design': True
            }
        })
        
        return PersonalizationResult(
            archetype_adaptation=result.archetype_adaptation,
            physiological_modulation=result.physiological_modulation,
            personalized_content=enhanced_content,
            confidence_score=result.confidence_score,
            personalization_metadata={
                **result.personalization_metadata,
                'stella_visualization_adapted': True,
                'complexity_level': complexity_level
            }
        )
    
    def _generate_actionable_insights(self, trends: Dict[str, ProgressTrend], achievement_rate: float) -> List[str]:
        """Generate actionable insights from progress analysis"""
        insights = []
        
        # Analyze overall achievement rate
        if achievement_rate > 0.8:
            insights.append("Excellent goal achievement rate - consider increasing challenge level")
        elif achievement_rate < 0.5:
            insights.append("Consider adjusting goal difficulty or implementation strategy")
        
        # Analyze trends
        declining_metrics = [metric for metric, trend in trends.items() if trend == ProgressTrend.DECLINING]
        if declining_metrics:
            insights.append(f"Focus needed on improving: {', '.join(declining_metrics[:3])}")
        
        accelerating_metrics = [metric for metric, trend in trends.items() if trend == ProgressTrend.ACCELERATING]
        if accelerating_metrics:
            insights.append(f"Great momentum in: {', '.join(accelerating_metrics[:3])}")
        
        plateauing_metrics = [metric for metric, trend in trends.items() if trend == ProgressTrend.PLATEAUING]
        if plateauing_metrics:
            insights.append(f"Consider strategy change for: {', '.join(plateauing_metrics[:2])}")
        
        return insights[:5]  # Limit to top 5 insights
    
    def _create_fallback_result(self, data: Any, request_type: str) -> PersonalizationResult:
        """Create fallback result when personalization fails"""
        return PersonalizationResult(
            archetype_adaptation={
                'user_archetype': UserArchetype.PRIME,
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
async def personalize_progress_tracking(
    tracking_request: Dict[str, Any],
    user_profile: Dict[str, Any],
    tracking_type: str = "progress_analysis",
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Complete progress tracking personalization workflow
    
    Args:
        tracking_request: Progress tracking request data
        user_profile: Complete user profile
        tracking_type: Type of tracking personalization needed
        additional_data: Additional context data
        
    Returns:
        Complete personalized tracking strategy
    """
    integration = STELLAHybridIntelligenceIntegration()
    
    try:
        if tracking_type == "progress_analysis":
            result = await integration.personalize_progress_analysis(
                tracking_request, user_profile, additional_data.get('analysis_period') if additional_data else None
            )
        elif tracking_type == "goal_setting":
            result = await integration.personalize_goal_setting(
                tracking_request, user_profile, additional_data.get('historical_performance') if additional_data else None
            )
        elif tracking_type == "progress_visualization":
            result = await integration.personalize_progress_visualization(
                tracking_request, user_profile, additional_data.get('preferred_formats') if additional_data else None
            )
        else:
            result = await integration.personalize_progress_analysis(tracking_request, user_profile)
        
        return {
            'personalized_tracking': result.personalized_content,
            'archetype_considerations': result.archetype_adaptation,
            'progress_modulation': result.physiological_modulation,
            'confidence_score': result.confidence_score,
            'metadata': result.personalization_metadata
        }
        
    except Exception as e:
        logger.error(f"Error in progress tracking personalization: {e}")
        return {
            'error': str(e),
            'fallback_mode': True,
            'timestamp': datetime.now().isoformat()
        }


# Export the integration class
__all__ = ['STELLAHybridIntelligenceIntegration', 'personalize_progress_tracking']