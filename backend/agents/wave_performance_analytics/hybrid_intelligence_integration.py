"""
GENESIS NGX Agents - WAVE Hybrid Intelligence Integration
========================================================

Integration module for the WAVE agent (Performance Analytics) with the
Hybrid Intelligence Engine. This module provides analytics-specific personalization
using the two-layer system.

WAVE specializes in:
- Performance data analysis
- Progress tracking algorithms
- Predictive performance modeling
- Competitive benchmarking
- Training load optimization

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


class WAVEHybridIntelligenceIntegration(HybridIntelligenceMixin):
    """
    Hybrid Intelligence integration for WAVE (Performance Analytics)
    
    Provides analytics-specific adaptations based on:
    - User archetype (PRIME vs LONGEVITY)
    - Performance data patterns
    - Goal-oriented analytics
    - Progress measurement preferences
    """
    
    def __init__(self):
        super().__init__()
        self.AGENT_ID = "wave_performance_analytics"
        logger.info("WAVE Hybrid Intelligence Integration initialized")
    
    def _get_agent_adaptations(self) -> Dict[str, Any]:
        """Get WAVE-specific adaptation configurations"""
        
        return {
            "communication_styles": {
                "direct_performance": "metrics_driven_insights",
                "supportive_educational": "progress_storytelling",
                "analytical": "deep_data_analysis"
            },
            "analytics_focus": {
                "prime": {
                    "priorities": ["performance_optimization", "competitive_analysis", "efficiency_metrics"],
                    "measurement_frequency": "high_frequency_tracking",
                    "analysis_depth": "granular_performance",
                    "comparison_benchmarks": "elite_standards",
                    "prediction_models": "performance_peaks"
                },
                "longevity": {
                    "priorities": ["consistency_tracking", "health_indicators", "sustainable_progress"],
                    "measurement_frequency": "trend_based_tracking",
                    "analysis_depth": "holistic_wellness",
                    "comparison_benchmarks": "personal_progress",
                    "prediction_models": "health_trajectories"
                }
            },
            "visualization_preferences": {
                "prime": ["performance_curves", "competitive_charts", "optimization_heatmaps"],
                "longevity": ["progress_journeys", "wellness_trends", "achievement_celebrations"]
            },
            "reporting_styles": {
                "prime": "performance_briefings",
                "longevity": "progress_stories"
            },
            "metric_priorities": {
                "prime": {
                    "primary": ["power_output", "vo2_max", "training_load", "recovery_efficiency"],
                    "secondary": ["technique_optimization", "competitive_positioning"],
                    "tertiary": ["equipment_optimization", "environmental_factors"]
                },
                "longevity": {
                    "primary": ["consistency_score", "energy_balance", "stress_management", "sleep_quality"],
                    "secondary": ["functional_movement", "cardiovascular_health"],
                    "tertiary": ["life_balance", "enjoyment_factors"]
                }
            }
        }
    
    async def _get_agent_specific_adaptations(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Get WAVE-specific analytics adaptations"""
        
        archetype = combined_recs["personalization_metadata"]["archetype"]
        readiness_score = combined_recs["personalization_metadata"]["readiness_score"]
        
        # Get analytics focus based on archetype
        analytics_focus = self._agent_adaptations["analytics_focus"][archetype]
        
        # Adapt analysis approach based on physiological state
        analysis_approach = self._determine_analysis_approach(readiness_score, archetype)
        
        # Get visualization and reporting preferences
        visualization_style = self._get_visualization_style(archetype, readiness_score)
        
        # Get measurement and tracking preferences
        tracking_preferences = self._get_tracking_preferences(archetype)
        
        return {
            "analytics_strategy": {
                "focus_areas": analytics_focus["priorities"],
                "measurement_approach": analytics_focus["measurement_frequency"],
                "analysis_depth": analysis_approach,
                "benchmark_standards": analytics_focus["comparison_benchmarks"]
            },
            "visualization_style": visualization_style,
            "tracking_preferences": tracking_preferences,
            "reporting_approach": self._get_reporting_approach(archetype, readiness_score),
            "prediction_focus": analytics_focus["prediction_models"],
            "metric_prioritization": self._agent_adaptations["metric_priorities"][archetype],
            "insight_delivery": self._get_insight_delivery_preferences(archetype)
        }
    
    def _determine_analysis_approach(self, readiness_score: float, archetype: str) -> str:
        """Determine appropriate analysis approach"""
        
        if archetype == "prime":
            if readiness_score > 0.8:
                return "peak_performance_analysis"
            elif readiness_score > 0.6:
                return "optimization_focused"
            else:
                return "recovery_analytics"
        else:  # longevity
            if readiness_score > 0.7:
                return "progress_celebration"
            elif readiness_score > 0.4:
                return "steady_improvement"
            else:
                return "supportive_tracking"
    
    def _get_visualization_style(self, archetype: str, readiness_score: float) -> Dict[str, Any]:
        """Get visualization style preferences"""
        
        if archetype == "prime":
            return {
                "chart_types": ["performance_curves", "competitive_radar", "optimization_heatmaps"],
                "color_scheme": "high_contrast_performance",
                "detail_level": "metric_rich",
                "interactivity": "drill_down_analysis",
                "time_horizons": ["session", "weekly", "monthly_peaks"]
            }
        else:  # longevity
            return {
                "chart_types": ["progress_lines", "wellness_areas", "achievement_badges"],
                "color_scheme": "calming_wellness",
                "detail_level": "story_focused",
                "interactivity": "exploratory_gentle",
                "time_horizons": ["weekly", "monthly", "quarterly_trends"]
            }
    
    def _get_tracking_preferences(self, archetype: str) -> Dict[str, Any]:
        """Get tracking and measurement preferences"""
        
        if archetype == "prime":
            return {
                "frequency": "continuous_monitoring",
                "granularity": "high_precision",
                "automation_level": "full_automation",
                "manual_inputs": "performance_context",
                "data_retention": "comprehensive_history"
            }
        else:  # longevity
            return {
                "frequency": "milestone_based",
                "granularity": "meaningful_changes",
                "automation_level": "assisted_tracking",
                "manual_inputs": "wellness_check_ins",
                "data_retention": "trend_focused"
            }
    
    def _get_reporting_approach(self, archetype: str, readiness_score: float) -> Dict[str, Any]:
        """Get reporting approach based on archetype and state"""
        
        if archetype == "prime":
            return {
                "format": "performance_briefing",
                "frequency": "real_time_updates",
                "content_focus": "actionable_insights",
                "tone": "coach_analysis",
                "detail_preference": "comprehensive_metrics"
            }
        else:  # longevity
            return {
                "format": "progress_story",
                "frequency": "weekly_summaries",
                "content_focus": "meaningful_progress",
                "tone": "encouraging_guide",
                "detail_preference": "contextual_insights"
            }
    
    def _get_insight_delivery_preferences(self, archetype: str) -> Dict[str, Any]:
        """Get insight delivery preferences"""
        
        if archetype == "prime":
            return {
                "timing": "performance_relevant",
                "depth": "technical_detail",
                "actionability": "immediate_implementation",
                "context": "competitive_advantage",
                "format": "bullet_point_insights"
            }
        else:  # longevity
            return {
                "timing": "reflection_moments",
                "depth": "educational_context",
                "actionability": "gradual_integration",
                "context": "wellness_journey",
                "format": "narrative_insights"
            }
    
    async def personalize_performance_dashboard(self,
                                              user_data: Dict[str, Any],
                                              performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Specialized method for performance dashboard personalization
        
        Args:
            user_data: User profile data
            performance_data: Current performance metrics
            
        Returns:
            Personalized dashboard configuration
        """
        
        # Get base personalization
        personalization = await self.personalize_response(
            user_data=user_data,
            request_type="performance_dashboard",
            request_content=f"Create dashboard for metrics: {performance_data.keys()}"
        )
        
        if personalization["personalization_applied"]:
            archetype = user_data.get("archetype", "prime")
            
            dashboard_config = {
                "layout": self._get_dashboard_layout(archetype),
                "metrics_selection": self._get_metrics_selection(archetype, performance_data),
                "visualization_config": self._get_visualization_config(archetype),
                "alert_setup": self._get_alert_setup(archetype),
                "export_capabilities": self._get_export_capabilities(archetype)
            }
            
            personalization["dashboard_specific_adaptations"] = dashboard_config
        
        return personalization
    
    def _get_dashboard_layout(self, archetype: str) -> Dict[str, Any]:
        """Get dashboard layout configuration"""
        
        if archetype == "prime":
            return {
                "structure": "performance_command_center",
                "widget_density": "information_rich",
                "primary_focus": "current_performance",
                "secondary_panels": ["optimization_opportunities", "competitive_benchmarks"],
                "navigation": "quick_drill_down"
            }
        else:
            return {
                "structure": "wellness_overview",
                "widget_density": "comfortable_spacing",
                "primary_focus": "progress_celebration",
                "secondary_panels": ["trend_insights", "achievement_gallery"],
                "navigation": "exploratory_journey"
            }
    
    def _get_metrics_selection(self, archetype: str, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get metrics selection based on archetype and available data"""
        
        metric_priorities = self._agent_adaptations["metric_priorities"][archetype]
        
        selected_metrics = []
        
        # Primary metrics (always show if available)
        for metric in metric_priorities["primary"]:
            if self._is_metric_available(metric, performance_data):
                selected_metrics.append({
                    "metric": metric,
                    "priority": "primary",
                    "display_style": "prominent",
                    "update_frequency": "real_time" if archetype == "prime" else "periodic"
                })
        
        # Secondary metrics (show if space available)
        for metric in metric_priorities["secondary"]:
            if self._is_metric_available(metric, performance_data):
                selected_metrics.append({
                    "metric": metric,
                    "priority": "secondary",
                    "display_style": "standard",
                    "update_frequency": "periodic"
                })
        
        return selected_metrics
    
    def _is_metric_available(self, metric: str, performance_data: Dict[str, Any]) -> bool:
        """Check if metric is available in performance data"""
        
        # Simplified availability check - in real implementation, this would be more sophisticated
        metric_keywords = {
            "power_output": ["power", "wattage", "strength"],
            "vo2_max": ["vo2", "cardio", "aerobic"],
            "training_load": ["load", "volume", "intensity"],
            "consistency_score": ["consistency", "adherence"],
            "energy_balance": ["energy", "calories", "balance"]
        }
        
        keywords = metric_keywords.get(metric, [metric])
        return any(keyword in str(performance_data.keys()).lower() for keyword in keywords)
    
    def _get_visualization_config(self, archetype: str) -> Dict[str, Any]:
        """Get visualization configuration"""
        
        if archetype == "prime":
            return {
                "chart_style": "technical_precision",
                "color_palette": "performance_focused",
                "animation_level": "minimal_distraction",
                "interactivity": "detailed_exploration",
                "responsive_breakpoints": ["desktop_primary"]
            }
        else:
            return {
                "chart_style": "friendly_accessible",
                "color_palette": "wellness_calming",
                "animation_level": "engaging_smooth",
                "interactivity": "guided_discovery",
                "responsive_breakpoints": ["mobile_friendly", "tablet_optimized"]
            }
    
    def _get_alert_setup(self, archetype: str) -> Dict[str, Any]:
        """Get alert and notification setup"""
        
        if archetype == "prime":
            return {
                "enabled": True,
                "triggers": ["performance_peaks", "optimization_opportunities", "goal_achievement"],
                "delivery_method": "immediate_notification",
                "frequency_limit": "unlimited",
                "customization_level": "granular_control"
            }
        else:
            return {
                "enabled": True,
                "triggers": ["milestone_achievement", "positive_trends", "encouragement_moments"],
                "delivery_method": "gentle_summary",
                "frequency_limit": "daily_digest",
                "customization_level": "simple_preferences"
            }
    
    def _get_export_capabilities(self, archetype: str) -> List[str]:
        """Get data export capabilities"""
        
        if archetype == "prime":
            return ["detailed_csv", "api_integration", "performance_reports", "coaching_summaries"]
        else:
            return ["progress_pdf", "wellness_summary", "achievement_gallery", "trend_stories"]
    
    async def personalize_progress_analysis(self,
                                          user_data: Dict[str, Any],
                                          time_period: str) -> Dict[str, Any]:
        """
        Specialized method for progress analysis personalization
        
        Args:
            user_data: User profile data
            time_period: Analysis time period (weekly, monthly, quarterly)
            
        Returns:
            Personalized progress analysis
        """
        
        # Get base personalization
        personalization = await self.personalize_response(
            user_data=user_data,
            request_type="progress_analysis",
            request_content=f"Analyze progress over {time_period}"
        )
        
        if personalization["personalization_applied"]:
            archetype = user_data.get("archetype", "prime")
            
            analysis_config = {
                "analysis_framework": self._get_analysis_framework(archetype, time_period),
                "comparison_methods": self._get_comparison_methods(archetype),
                "insight_generation": self._get_insight_generation_style(archetype),
                "recommendation_style": self._get_recommendation_style(archetype),
                "visualization_approach": self._get_progress_visualization(archetype)
            }
            
            personalization["progress_analysis_adaptations"] = analysis_config
        
        return personalization
    
    def _get_analysis_framework(self, archetype: str, time_period: str) -> Dict[str, Any]:
        """Get analysis framework based on archetype and time period"""
        
        if archetype == "prime":
            return {
                "focus": "performance_optimization",
                "metrics_emphasis": "peak_achievements",
                "trend_analysis": "performance_curves",
                "goal_alignment": "competitive_targets"
            }
        else:
            return {
                "focus": "wellness_journey",
                "metrics_emphasis": "consistent_progress",
                "trend_analysis": "wellness_patterns",
                "goal_alignment": "life_balance"
            }
    
    def _get_comparison_methods(self, archetype: str) -> List[str]:
        """Get comparison methods based on archetype"""
        
        if archetype == "prime":
            return ["personal_best", "peer_benchmarks", "elite_standards", "theoretical_potential"]
        else:
            return ["personal_progress", "wellness_milestones", "age_appropriate", "lifestyle_goals"]
    
    def _get_insight_generation_style(self, archetype: str) -> str:
        """Get insight generation style"""
        
        return "performance_optimization" if archetype == "prime" else "wellness_understanding"
    
    def _get_recommendation_style(self, archetype: str) -> str:
        """Get recommendation style"""
        
        return "aggressive_improvement" if archetype == "prime" else "sustainable_enhancement"
    
    def _get_progress_visualization(self, archetype: str) -> str:
        """Get progress visualization approach"""
        
        return "performance_analytics" if archetype == "prime" else "progress_storytelling"


# Export the integration class
__all__ = ["WAVEHybridIntelligenceIntegration"]