"""
Female Wellness Data Service for LUNA Female Wellness Specialist.
Handles menstrual cycle data, hormonal patterns, and wellness metrics.
"""

import asyncio
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional, List, Tuple
import statistics
from dataclasses import dataclass

from agents.female_wellness_coach.core.config import LunaConfig
from agents.female_wellness_coach.core.exceptions import (
    WellnessDataNotFoundError,
    MenstrualCycleAnalysisError,
    LunaValidationError,
)
from agents.female_wellness_coach.core.constants import WELLNESS_ANALYSIS_CONFIG
from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CycleData:
    """Data structure for menstrual cycle information."""

    cycle_start: date
    cycle_length: int
    flow_duration: int
    flow_intensity: str  # light, medium, heavy
    symptoms: List[str]
    mood_patterns: List[str]
    energy_levels: List[int]  # 1-10 scale
    pain_levels: List[int]  # 1-10 scale


@dataclass
class HormonalProfile:
    """Data structure for hormonal information."""

    estrogen_levels: Optional[float] = None
    progesterone_levels: Optional[float] = None
    fsh_levels: Optional[float] = None
    lh_levels: Optional[float] = None
    testosterone_levels: Optional[float] = None
    cycle_phase: Optional[str] = None


@dataclass
class WellnessMetrics:
    """Data structure for overall wellness metrics."""

    sleep_quality: Optional[float] = None  # 1-10 scale
    stress_levels: Optional[float] = None  # 1-10 scale
    exercise_frequency: Optional[int] = None  # days per week
    nutrition_quality: Optional[float] = None  # 1-10 scale
    hydration_levels: Optional[float] = None  # liters per day


class FemaleWellnessDataService:
    """
    Comprehensive data service for female wellness analytics.

    Features:
    - Menstrual cycle tracking and analysis
    - Hormonal pattern recognition
    - Wellness metrics aggregation
    - Predictive cycle modeling
    - Data validation and cleansing
    """

    def __init__(self, config: LunaConfig):
        self.config = config
        self._cycle_data_cache = {}
        self._hormonal_cache = {}
        self._wellness_cache = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the wellness data service."""
        try:
            self._cycle_data_cache = {}
            self._hormonal_cache = {}
            self._wellness_cache = {}
            self._initialized = True

            logger.info("Female wellness data service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize wellness data service: {e}")
            raise WellnessDataNotFoundError(
                f"Data service initialization failed: {e}",
                data_type="initialization",
            )

    async def store_cycle_data(self, user_id: str, cycle_data: CycleData) -> None:
        """
        Store menstrual cycle data for a user.

        Args:
            user_id: User identifier
            cycle_data: Cycle data to store

        Raises:
            LunaValidationError: If cycle data is invalid
        """
        try:
            # Validate cycle data
            await self._validate_cycle_data(cycle_data)

            # Store in cache (in production, would use database)
            if user_id not in self._cycle_data_cache:
                self._cycle_data_cache[user_id] = []

            self._cycle_data_cache[user_id].append(cycle_data)

            # Keep only recent cycles (last 12 months)
            cutoff_date = datetime.now().date() - timedelta(days=365)
            self._cycle_data_cache[user_id] = [
                cycle
                for cycle in self._cycle_data_cache[user_id]
                if cycle.cycle_start >= cutoff_date
            ]

            logger.info(f"Stored cycle data for user {user_id[:8]}...")

        except Exception as e:
            logger.error(f"Failed to store cycle data: {e}")
            raise

    async def get_cycle_history(self, user_id: str, months: int = 6) -> List[CycleData]:
        """
        Retrieve menstrual cycle history for a user.

        Args:
            user_id: User identifier
            months: Number of months of history to retrieve

        Returns:
            List[CycleData]: User's cycle history

        Raises:
            WellnessDataNotFoundError: If no cycle data exists
        """
        try:
            if user_id not in self._cycle_data_cache:
                raise WellnessDataNotFoundError(
                    f"No cycle data found for user",
                    data_type="menstrual_cycle",
                )

            cutoff_date = datetime.now().date() - timedelta(days=months * 30)
            recent_cycles = [
                cycle
                for cycle in self._cycle_data_cache[user_id]
                if cycle.cycle_start >= cutoff_date
            ]

            # Sort by date (most recent first)
            recent_cycles.sort(key=lambda x: x.cycle_start, reverse=True)

            return recent_cycles

        except Exception as e:
            logger.error(f"Failed to retrieve cycle history: {e}")
            raise

    async def analyze_cycle_patterns(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze menstrual cycle patterns for insights.

        Args:
            user_id: User identifier

        Returns:
            Dict[str, Any]: Cycle pattern analysis

        Raises:
            MenstrualCycleAnalysisError: If analysis fails
        """
        try:
            cycles = await self.get_cycle_history(user_id, months=12)

            if len(cycles) < 3:
                raise MenstrualCycleAnalysisError(
                    "Insufficient cycle data for pattern analysis (minimum 3 cycles)",
                    cycle_phase="analysis",
                )

            # Calculate cycle statistics
            cycle_lengths = [cycle.cycle_length for cycle in cycles]
            flow_durations = [cycle.flow_duration for cycle in cycles]

            # Analyze symptoms frequency
            all_symptoms = []
            for cycle in cycles:
                all_symptoms.extend(cycle.symptoms)

            symptom_frequency = {}
            for symptom in set(all_symptoms):
                symptom_frequency[symptom] = all_symptoms.count(symptom) / len(cycles)

            # Analyze mood patterns
            mood_patterns = {}
            for cycle in cycles:
                for mood in cycle.mood_patterns:
                    if mood not in mood_patterns:
                        mood_patterns[mood] = 0
                    mood_patterns[mood] += 1

            # Calculate energy and pain averages
            avg_energy = []
            avg_pain = []
            for cycle in cycles:
                if cycle.energy_levels:
                    avg_energy.extend(cycle.energy_levels)
                if cycle.pain_levels:
                    avg_pain.extend(cycle.pain_levels)

            analysis = {
                "cycle_regularity": {
                    "average_length": statistics.mean(cycle_lengths),
                    "length_variation": (
                        statistics.stdev(cycle_lengths) if len(cycle_lengths) > 1 else 0
                    ),
                    "is_regular": (
                        statistics.stdev(cycle_lengths) < 3
                        if len(cycle_lengths) > 1
                        else True
                    ),
                },
                "flow_patterns": {
                    "average_duration": statistics.mean(flow_durations),
                    "duration_variation": (
                        statistics.stdev(flow_durations)
                        if len(flow_durations) > 1
                        else 0
                    ),
                },
                "symptom_analysis": {
                    "most_common_symptoms": sorted(
                        symptom_frequency.items(), key=lambda x: x[1], reverse=True
                    )[:5],
                    "symptom_frequency": symptom_frequency,
                },
                "mood_analysis": {
                    "mood_distribution": mood_patterns,
                    "dominant_moods": sorted(
                        mood_patterns.items(), key=lambda x: x[1], reverse=True
                    )[:3],
                },
                "wellness_metrics": {
                    "average_energy": (
                        statistics.mean(avg_energy) if avg_energy else None
                    ),
                    "average_pain": statistics.mean(avg_pain) if avg_pain else None,
                    "energy_consistency": (
                        statistics.stdev(avg_energy) if len(avg_energy) > 1 else None
                    ),
                },
                "cycles_analyzed": len(cycles),
                "analysis_date": datetime.utcnow().isoformat(),
            }

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze cycle patterns: {e}")
            raise MenstrualCycleAnalysisError(
                f"Cycle pattern analysis failed: {e}",
                cycle_phase="pattern_analysis",
            )

    async def predict_next_cycle(self, user_id: str) -> Dict[str, Any]:
        """
        Predict next menstrual cycle based on historical data.

        Args:
            user_id: User identifier

        Returns:
            Dict[str, Any]: Next cycle prediction
        """
        try:
            cycles = await self.get_cycle_history(user_id, months=6)

            if len(cycles) < 2:
                raise MenstrualCycleAnalysisError(
                    "Insufficient data for cycle prediction (minimum 2 cycles)",
                    cycle_phase="prediction",
                )

            # Calculate average cycle length
            cycle_lengths = [cycle.cycle_length for cycle in cycles]
            avg_cycle_length = statistics.mean(cycle_lengths)

            # Get last cycle start date
            last_cycle = max(cycles, key=lambda x: x.cycle_start)

            # Predict next cycle
            predicted_start = last_cycle.cycle_start + timedelta(
                days=int(avg_cycle_length)
            )

            # Calculate confidence based on cycle regularity
            length_variation = (
                statistics.stdev(cycle_lengths) if len(cycle_lengths) > 1 else 0
            )
            confidence = max(0.5, 1.0 - (length_variation / avg_cycle_length))

            prediction = {
                "predicted_start_date": predicted_start.isoformat(),
                "predicted_cycle_length": int(avg_cycle_length),
                "confidence_score": round(confidence, 2),
                "prediction_window": {
                    "earliest": (predicted_start - timedelta(days=2)).isoformat(),
                    "latest": (predicted_start + timedelta(days=2)).isoformat(),
                },
                "based_on_cycles": len(cycles),
                "prediction_date": datetime.utcnow().isoformat(),
            }

            return prediction

        except Exception as e:
            logger.error(f"Failed to predict next cycle: {e}")
            raise

    async def determine_current_phase(self, user_id: str) -> Dict[str, Any]:
        """
        Determine current menstrual cycle phase.

        Args:
            user_id: User identifier

        Returns:
            Dict[str, Any]: Current cycle phase information
        """
        try:
            cycles = await self.get_cycle_history(user_id, months=2)

            if not cycles:
                raise WellnessDataNotFoundError(
                    "No recent cycle data available for phase determination",
                    data_type="current_cycle",
                )

            last_cycle = max(cycles, key=lambda x: x.cycle_start)
            today = datetime.now().date()

            # Calculate days since last cycle start
            days_since_start = (today - last_cycle.cycle_start).days

            # Determine phase based on typical cycle
            if days_since_start <= 5:
                phase = "menstrual"
                description = "Menstrual phase - focus on rest and gentle movement"
            elif days_since_start <= 13:
                phase = "follicular"
                description = (
                    "Follicular phase - energy building, good for new activities"
                )
            elif days_since_start <= 16:
                phase = "ovulatory"
                description = (
                    "Ovulatory phase - peak energy, ideal for high-intensity activities"
                )
            else:
                phase = "luteal"
                description = "Luteal phase - energy stabilizing, focus on maintenance"

            phase_info = {
                "current_phase": phase,
                "phase_description": description,
                "days_since_cycle_start": days_since_start,
                "cycle_day": days_since_start + 1,
                "last_cycle_start": last_cycle.cycle_start.isoformat(),
                "phase_characteristics": self._get_phase_characteristics(phase),
                "determination_date": datetime.utcnow().isoformat(),
            }

            return phase_info

        except Exception as e:
            logger.error(f"Failed to determine current phase: {e}")
            raise

    def _get_phase_characteristics(self, phase: str) -> Dict[str, Any]:
        """Get characteristics for a specific cycle phase."""
        characteristics = {
            "menstrual": {
                "energy_level": "low",
                "recommended_activities": ["gentle yoga", "walking", "stretching"],
                "nutrition_focus": ["iron-rich foods", "anti-inflammatory foods"],
                "self_care": ["rest", "heat therapy", "gentle massage"],
            },
            "follicular": {
                "energy_level": "building",
                "recommended_activities": [
                    "strength training",
                    "new skills",
                    "planning",
                ],
                "nutrition_focus": ["protein", "healthy fats", "complex carbs"],
                "self_care": ["goal setting", "creative projects", "social activities"],
            },
            "ovulatory": {
                "energy_level": "peak",
                "recommended_activities": ["HIIT", "competitions", "presentations"],
                "nutrition_focus": ["antioxidants", "fiber", "healthy fats"],
                "self_care": [
                    "challenging workouts",
                    "social events",
                    "important meetings",
                ],
            },
            "luteal": {
                "energy_level": "declining",
                "recommended_activities": [
                    "moderate cardio",
                    "completion tasks",
                    "organization",
                ],
                "nutrition_focus": ["magnesium", "B vitamins", "complex carbs"],
                "self_care": ["stress management", "preparation", "reflection"],
            },
        }

        return characteristics.get(phase, {})

    async def _validate_cycle_data(self, cycle_data: CycleData) -> None:
        """Validate menstrual cycle data."""
        # Validate cycle length
        min_length, max_length = 21, 35
        if not (min_length <= cycle_data.cycle_length <= max_length):
            raise LunaValidationError(
                f"Cycle length must be between {min_length} and {max_length} days",
                field="cycle_length",
            )

        # Validate flow duration
        if not (1 <= cycle_data.flow_duration <= cycle_data.cycle_length):
            raise LunaValidationError(
                "Flow duration must be between 1 day and cycle length",
                field="flow_duration",
            )

        # Validate flow intensity
        valid_intensities = ["light", "medium", "heavy"]
        if cycle_data.flow_intensity not in valid_intensities:
            raise LunaValidationError(
                f"Flow intensity must be one of: {valid_intensities}",
                field="flow_intensity",
            )

        # Validate rating scales
        for level in cycle_data.energy_levels + cycle_data.pain_levels:
            if not (1 <= level <= 10):
                raise LunaValidationError(
                    "Energy and pain levels must be between 1 and 10",
                    field="rating_scales",
                )

    async def store_hormonal_profile(
        self, user_id: str, hormonal_data: HormonalProfile
    ) -> None:
        """Store hormonal profile data for a user."""
        try:
            if user_id not in self._hormonal_cache:
                self._hormonal_cache[user_id] = []

            # Add timestamp to hormonal data
            timestamped_data = {
                "profile": hormonal_data,
                "recorded_at": datetime.utcnow(),
            }

            self._hormonal_cache[user_id].append(timestamped_data)

            # Keep only recent data (last 6 months)
            cutoff_date = datetime.utcnow() - timedelta(days=180)
            self._hormonal_cache[user_id] = [
                data
                for data in self._hormonal_cache[user_id]
                if data["recorded_at"] >= cutoff_date
            ]

            logger.info(f"Stored hormonal profile for user {user_id[:8]}...")

        except Exception as e:
            logger.error(f"Failed to store hormonal profile: {e}")
            raise

    async def get_wellness_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive wellness insights for a user.

        Args:
            user_id: User identifier

        Returns:
            Dict[str, Any]: Comprehensive wellness insights
        """
        try:
            # Gather all available data
            cycle_analysis = await self.analyze_cycle_patterns(user_id)
            current_phase = await self.determine_current_phase(user_id)
            next_cycle_prediction = await self.predict_next_cycle(user_id)

            insights = {
                "cycle_health": {
                    "regularity_score": self._calculate_regularity_score(
                        cycle_analysis
                    ),
                    "symptom_severity": self._assess_symptom_severity(cycle_analysis),
                    "overall_wellness": self._calculate_wellness_score(cycle_analysis),
                },
                "current_status": current_phase,
                "future_planning": next_cycle_prediction,
                "recommendations": await self._generate_recommendations(
                    user_id, cycle_analysis, current_phase
                ),
                "insights_generated_at": datetime.utcnow().isoformat(),
            }

            return insights

        except Exception as e:
            logger.error(f"Failed to generate wellness insights: {e}")
            raise

    def _calculate_regularity_score(self, cycle_analysis: Dict[str, Any]) -> float:
        """Calculate cycle regularity score (0-100)."""
        variation = cycle_analysis["cycle_regularity"]["length_variation"]
        # Lower variation = higher score
        if variation <= 1:
            return 100.0
        elif variation <= 3:
            return 85.0
        elif variation <= 5:
            return 70.0
        else:
            return max(50.0, 100.0 - (variation * 10))

    def _assess_symptom_severity(self, cycle_analysis: Dict[str, Any]) -> str:
        """Assess overall symptom severity."""
        symptoms = cycle_analysis["symptom_analysis"]["symptom_frequency"]

        # Count high-impact symptoms
        severe_symptoms = ["severe_cramping", "heavy_bleeding", "severe_mood_swings"]
        severe_count = sum(1 for symptom in severe_symptoms if symptom in symptoms)

        total_symptom_frequency = sum(symptoms.values())

        if severe_count >= 2 or total_symptom_frequency > 10:
            return "high"
        elif severe_count == 1 or total_symptom_frequency > 5:
            return "moderate"
        else:
            return "low"

    def _calculate_wellness_score(self, cycle_analysis: Dict[str, Any]) -> float:
        """Calculate overall wellness score (0-100)."""
        regularity_score = self._calculate_regularity_score(cycle_analysis)

        # Factor in energy and pain levels
        wellness_metrics = cycle_analysis.get("wellness_metrics", {})
        avg_energy = wellness_metrics.get("average_energy", 5)
        avg_pain = wellness_metrics.get("average_pain", 5)

        # Higher energy and lower pain = better score
        energy_score = (avg_energy / 10) * 50 if avg_energy else 25
        pain_score = ((10 - avg_pain) / 10) * 30 if avg_pain else 15

        total_score = (regularity_score * 0.4) + energy_score + pain_score
        return min(100.0, max(0.0, total_score))

    async def _generate_recommendations(
        self,
        user_id: str,
        cycle_analysis: Dict[str, Any],
        current_phase: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Generate personalized recommendations based on cycle data."""
        recommendations = []

        # Regularity recommendations
        if not cycle_analysis["cycle_regularity"]["is_regular"]:
            recommendations.append(
                {
                    "category": "cycle_regularity",
                    "priority": "high",
                    "recommendation": "Consider tracking stress levels and sleep patterns to improve cycle regularity",
                    "action": "Start a stress management routine and maintain consistent sleep schedule",
                }
            )

        # Phase-specific recommendations
        current_phase_name = current_phase["current_phase"]
        phase_chars = current_phase.get("phase_characteristics", {})

        if phase_chars:
            recommendations.append(
                {
                    "category": "phase_optimization",
                    "priority": "medium",
                    "recommendation": f"Optimize your {current_phase_name} phase with appropriate activities and nutrition",
                    "action": f"Focus on: {', '.join(phase_chars.get('recommended_activities', []))}",
                }
            )

        # Symptom-specific recommendations
        top_symptoms = cycle_analysis["symptom_analysis"]["most_common_symptoms"][:3]
        for symptom, frequency in top_symptoms:
            if frequency > 0.5:  # Occurs in more than 50% of cycles
                recommendations.append(
                    {
                        "category": "symptom_management",
                        "priority": "medium",
                        "recommendation": f"Address recurring {symptom.replace('_', ' ')}",
                        "action": f"Consult healthcare provider about managing {symptom.replace('_', ' ')}",
                    }
                )

        return recommendations
