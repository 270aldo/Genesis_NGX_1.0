"""
Recovery service for WAVE Performance Analytics Agent.
Handles injury prevention, rehabilitation, sleep optimization, and mobility assessment.
Consolidates recovery capabilities from the original WAVE agent.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import json

from ..core.exceptions import (
    InjuryPreventionError,
    RehabilitationError,
    SleepOptimizationError,
    MobilityAssessmentError,
    RecoveryValidationError,
)

logger = logging.getLogger(__name__)


class RecoveryService:
    """
    Manages all recovery-related operations for the WAVE fusion agent.
    Combines injury prevention, rehabilitation, sleep, and mobility capabilities.
    """

    def __init__(self, config: Any, cache: Any = None):
        """Initialize recovery service with configuration."""
        self.config = config
        self.cache = cache
        self.recovery_protocols = config.recovery_protocols

    async def assess_injury_risk(
        self, user_data: Dict[str, Any], biometric_trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess injury risk based on user data and biometric trends.

        Args:
            user_data: User profile and recent activity
            biometric_trends: Recent biometric data trends

        Returns:
            Injury risk assessment with recommendations
        """
        try:
            # Extract risk factors
            risk_factors = self._extract_risk_factors(user_data, biometric_trends)

            # Calculate risk score
            risk_score = self._calculate_injury_risk_score(risk_factors)

            # Generate prevention recommendations
            recommendations = self._generate_prevention_recommendations(
                risk_score, risk_factors
            )

            # Create assessment result
            assessment = {
                "risk_score": risk_score,
                "risk_level": self._categorize_risk_level(risk_score),
                "primary_risk_factors": risk_factors["high_risk"],
                "secondary_risk_factors": risk_factors["medium_risk"],
                "prevention_recommendations": recommendations,
                "assessment_date": datetime.now().isoformat(),
                "reassessment_due": (datetime.now() + timedelta(days=7)).isoformat(),
            }

            # Cache assessment
            if self.cache:
                cache_key = f"injury_risk:{user_data.get('user_id', 'anonymous')}"
                await self.cache.set(cache_key, assessment, ttl=604800)  # 1 week

            return assessment

        except Exception as e:
            logger.error(f"Injury risk assessment failed: {e}")
            raise InjuryPreventionError(
                f"Failed to assess injury risk: {e}",
                injury_type="general",
                risk_level=None,
            )

    async def create_rehabilitation_plan(
        self, injury_type: str, severity: str, user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create personalized rehabilitation plan.

        Args:
            injury_type: Type of injury (e.g., "lower_back", "knee", "shoulder")
            severity: Injury severity ("mild", "moderate", "severe")
            user_profile: User fitness level and constraints

        Returns:
            Comprehensive rehabilitation plan
        """
        try:
            # Validate inputs
            self._validate_injury_inputs(injury_type, severity)

            # Get base protocol for injury type
            base_protocol = self._get_base_rehab_protocol(injury_type, severity)

            # Customize for user
            customized_plan = self._customize_rehab_plan(base_protocol, user_profile)

            # Add progression milestones
            milestones = self._create_rehab_milestones(injury_type, severity)

            # Create comprehensive plan
            plan = {
                "injury_type": injury_type,
                "severity": severity,
                "plan_id": f"rehab_{injury_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "phases": customized_plan["phases"],
                "exercises": customized_plan["exercises"],
                "progressions": milestones,
                "duration_weeks": customized_plan.get("duration_weeks", 8),
                "session_frequency": customized_plan.get("frequency", "3x/week"),
                "pain_monitoring": {
                    "pain_scale": "0-10",
                    "acceptable_level": 3,
                    "escalation_threshold": 6,
                },
                "created_date": datetime.now().isoformat(),
                "next_review": (datetime.now() + timedelta(days=14)).isoformat(),
            }

            return plan

        except Exception as e:
            logger.error(f"Rehabilitation plan creation failed: {e}")
            raise RehabilitationError(
                f"Failed to create rehabilitation plan: {e}", exercise_type=injury_type
            )

    async def optimize_sleep_protocol(
        self, sleep_data: Dict[str, Any], recovery_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Create sleep optimization protocol based on data and goals.

        Args:
            sleep_data: Recent sleep metrics and patterns
            recovery_goals: Recovery-focused goals

        Returns:
            Sleep optimization recommendations
        """
        try:
            # Analyze current sleep patterns
            sleep_analysis = self._analyze_sleep_patterns(sleep_data)

            # Identify optimization opportunities
            opportunities = self._identify_sleep_opportunities(
                sleep_analysis, recovery_goals
            )

            # Generate recommendations
            recommendations = self._generate_sleep_recommendations(opportunities)

            # Create implementation plan
            implementation = self._create_sleep_implementation_plan(recommendations)

            protocol = {
                "current_metrics": sleep_analysis["summary"],
                "optimization_opportunities": opportunities,
                "recommendations": recommendations,
                "implementation_plan": implementation,
                "target_metrics": {
                    "total_sleep_hours": self.recovery_protocols["sleep_optimization"][
                        "target_sleep_hours"
                    ],
                    "deep_sleep_percentage": self.recovery_protocols[
                        "sleep_optimization"
                    ]["deep_sleep_percentage"],
                    "rem_sleep_percentage": self.recovery_protocols[
                        "sleep_optimization"
                    ]["rem_sleep_percentage"],
                    "sleep_efficiency": 85,  # Target percentage
                },
                "monitoring_schedule": "daily_tracking",
                "review_frequency": "weekly",
                "created_date": datetime.now().isoformat(),
            }

            return protocol

        except Exception as e:
            logger.error(f"Sleep optimization failed: {e}")
            raise SleepOptimizationError(
                f"Failed to optimize sleep protocol: {e}", sleep_metric="general"
            )

    async def assess_mobility(
        self, assessment_type: str, user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform mobility assessment.

        Args:
            assessment_type: Type of assessment ("full", "targeted", "follow_up")
            user_profile: User information and constraints

        Returns:
            Mobility assessment results and recommendations
        """
        try:
            # Get assessment protocol
            protocol = self._get_mobility_protocol(assessment_type)

            # Simulate assessment execution (in real implementation, would guide user)
            assessment_results = self._execute_mobility_assessment(
                protocol, user_profile
            )

            # Analyze results
            analysis = self._analyze_mobility_results(assessment_results)

            # Generate improvement recommendations
            recommendations = self._generate_mobility_recommendations(analysis)

            assessment = {
                "assessment_type": assessment_type,
                "assessment_date": datetime.now().isoformat(),
                "results": assessment_results,
                "analysis": analysis,
                "overall_score": analysis.get("overall_score", 0),
                "limitations_identified": analysis.get("limitations", []),
                "improvement_recommendations": recommendations,
                "follow_up_schedule": self._determine_follow_up_schedule(analysis),
                "next_assessment": (datetime.now() + timedelta(days=14)).isoformat(),
            }

            return assessment

        except Exception as e:
            logger.error(f"Mobility assessment failed: {e}")
            raise MobilityAssessmentError(
                f"Failed to perform mobility assessment: {e}",
                joint_type=assessment_type,
            )

    # Helper methods
    def _extract_risk_factors(
        self, user_data: Dict[str, Any], biometric_trends: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Extract and categorize risk factors."""
        high_risk = []
        medium_risk = []
        low_risk = []

        # Analyze training load
        if biometric_trends.get("training_load_trend") == "increasing":
            high_risk.append("increased_training_load")

        # Analyze HRV trends
        hrv_trend = biometric_trends.get("hrv_trend")
        if hrv_trend == "declining":
            high_risk.append("declining_hrv")
        elif hrv_trend == "variable":
            medium_risk.append("variable_hrv")

        # Analyze sleep quality
        sleep_score = biometric_trends.get("sleep_quality_avg", 100)
        if sleep_score < 70:
            high_risk.append("poor_sleep_quality")
        elif sleep_score < 85:
            medium_risk.append("suboptimal_sleep")

        # Previous injury history
        if user_data.get("injury_history"):
            medium_risk.append("previous_injuries")

        return {
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
        }

    def _calculate_injury_risk_score(self, risk_factors: Dict[str, List[str]]) -> float:
        """Calculate overall injury risk score (0-1)."""
        high_weight = 0.6
        medium_weight = 0.3
        low_weight = 0.1

        high_count = len(risk_factors["high_risk"])
        medium_count = len(risk_factors["medium_risk"])
        low_count = len(risk_factors["low_risk"])

        # Calculate weighted score
        score = (
            (high_count * high_weight)
            + (medium_count * medium_weight)
            + (low_count * low_weight)
        ) / 10  # Normalize to 0-1 scale

        return min(score, 1.0)

    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk score into level."""
        if risk_score >= 0.8:
            return "high"
        elif risk_score >= 0.5:
            return "moderate"
        elif risk_score >= 0.3:
            return "low"
        else:
            return "minimal"

    def _validate_injury_inputs(self, injury_type: str, severity: str) -> None:
        """Validate injury type and severity inputs."""
        valid_injuries = [
            "lower_back",
            "knee",
            "shoulder",
            "ankle",
            "hip",
            "hamstring",
            "calf",
            "achilles",
            "plantar_fascia",
        ]
        valid_severities = ["mild", "moderate", "severe"]

        if injury_type not in valid_injuries:
            raise RecoveryValidationError(
                "Invalid injury type",
                field_name="injury_type",
                invalid_value=injury_type,
                validation_rule=f"Must be one of: {valid_injuries}",
            )

        if severity not in valid_severities:
            raise RecoveryValidationError(
                "Invalid severity level",
                field_name="severity",
                invalid_value=severity,
                validation_rule=f"Must be one of: {valid_severities}",
            )

    def _get_base_rehab_protocol(
        self, injury_type: str, severity: str
    ) -> Dict[str, Any]:
        """Get base rehabilitation protocol for injury type and severity."""
        # This would normally load from a comprehensive database
        # For now, return a structured template
        return {
            "phases": [
                {
                    "phase": 1,
                    "name": "Acute/Pain Management",
                    "duration_weeks": 1 if severity == "mild" else 2,
                    "goals": ["reduce_pain", "reduce_inflammation", "protect_injury"],
                },
                {
                    "phase": 2,
                    "name": "Early Mobilization",
                    "duration_weeks": 2,
                    "goals": ["restore_range_of_motion", "gentle_strengthening"],
                },
                {
                    "phase": 3,
                    "name": "Progressive Loading",
                    "duration_weeks": 3,
                    "goals": ["build_strength", "improve_function"],
                },
                {
                    "phase": 4,
                    "name": "Return to Activity",
                    "duration_weeks": 2,
                    "goals": ["sport_specific_training", "prevent_reinjury"],
                },
            ],
            "exercises": self._get_injury_specific_exercises(injury_type),
            "frequency": "3x/week" if severity != "severe" else "daily",
        }

    def _get_injury_specific_exercises(self, injury_type: str) -> List[Dict[str, Any]]:
        """Get exercises specific to injury type."""
        # Simplified exercise database
        exercise_db = {
            "lower_back": [
                {"name": "Pelvic Tilts", "sets": 2, "reps": 10, "phase": 1},
                {"name": "Cat-Cow Stretch", "sets": 2, "reps": 10, "phase": 1},
                {"name": "Dead Bug", "sets": 2, "reps": 8, "phase": 2},
                {"name": "Bird Dog", "sets": 2, "reps": 6, "phase": 2},
            ],
            "knee": [
                {"name": "Quad Sets", "sets": 3, "reps": 10, "phase": 1},
                {"name": "Straight Leg Raises", "sets": 2, "reps": 10, "phase": 2},
                {"name": "Wall Sits", "sets": 2, "reps": "30s", "phase": 3},
            ],
        }

        return exercise_db.get(injury_type, [])

    # Additional helper methods for sleep and mobility would be implemented here
    def _analyze_sleep_patterns(self, sleep_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sleep patterns and return insights."""
        return {
            "summary": {
                "avg_total_sleep": sleep_data.get("avg_total_sleep", 7.5),
                "avg_deep_sleep": sleep_data.get("avg_deep_sleep", 1.5),
                "avg_rem_sleep": sleep_data.get("avg_rem_sleep", 1.8),
                "sleep_efficiency": sleep_data.get("sleep_efficiency", 82),
            },
            "trends": "stable",  # Would calculate from historical data
            "issues_identified": [],
        }

    def _get_mobility_protocol(self, assessment_type: str) -> Dict[str, Any]:
        """Get mobility assessment protocol."""
        return {
            "tests": [
                {"name": "Overhead Squat", "target_score": 3},
                {"name": "Single Leg Balance", "target_time": 30},
                {"name": "Shoulder Mobility", "target_range": 180},
            ],
            "duration_minutes": 20 if assessment_type == "full" else 10,
        }
