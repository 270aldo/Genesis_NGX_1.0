"""
STELLA Progress Data Service.
Comprehensive data management for progress tracking with analytics and caching.
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics

from ..core.constants import (
    ProgressMetricType,
    AchievementCategory,
    TrendDirection,
    PROGRESS_THRESHOLDS,
    MILESTONE_CRITERIA,
)
from ..core.exceptions import (
    ProgressDataStorageError,
    DataValidationError,
    ProgressAnalysisError,
)


@dataclass
class ProgressDataEntry:
    """Data structure for progress tracking entries."""

    user_id: str
    data_type: str
    content: Dict[str, Any]
    timestamp: datetime
    entry_id: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Generate entry ID if not provided."""
        if not self.entry_id:
            timestamp_str = self.timestamp.isoformat()
            content_str = json.dumps(self.content, sort_keys=True, default=str)
            hash_input = (
                f"{self.user_id}_{self.data_type}_{timestamp_str}_{content_str}"
            )
            self.entry_id = hashlib.md5(hash_input.encode()).hexdigest()


class ProgressDataService:
    """
    Comprehensive data service for STELLA Progress Tracker.
    Handles data storage, retrieval, analytics, and caching.
    """

    def __init__(self, cache_ttl_seconds: int = 3600, max_cache_size: int = 1000):
        """
        Initialize progress data service.

        Args:
            cache_ttl_seconds: Cache time-to-live in seconds
            max_cache_size: Maximum number of cached entries
        """
        self.progress_data = defaultdict(list)  # user_id -> List[ProgressDataEntry]
        self.user_profiles = {}  # user_id -> profile_data
        self.achievements = defaultdict(list)  # user_id -> List[achievement]
        self.milestones = defaultdict(list)  # user_id -> List[milestone]

        # Caching
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_ttl = cache_ttl_seconds
        self.max_cache_size = max_cache_size
        self.cache_access_order = deque()

        # Performance metrics
        self.operation_stats = defaultdict(int)
        self.analysis_cache = {}

    def store_progress_data(
        self,
        user_id: str,
        data_type: str,
        content: Dict[str, Any],
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store progress data entry.

        Args:
            user_id: User identifier
            data_type: Type of progress data
            content: Progress data content
            tags: Optional tags for categorization
            metadata: Optional metadata

        Returns:
            Entry ID of stored data

        Raises:
            DataValidationError: If data validation fails
            ProgressDataStorageError: If storage fails
        """
        try:
            # Validate inputs
            if not user_id or not user_id.strip():
                raise DataValidationError("User ID cannot be empty")

            if not data_type or not data_type.strip():
                raise DataValidationError("Data type cannot be empty")

            if not content:
                raise DataValidationError("Content cannot be empty")

            # Create entry
            entry = ProgressDataEntry(
                user_id=user_id.strip(),
                data_type=data_type.strip(),
                content=content,
                timestamp=datetime.utcnow(),
                tags=tags or [],
                metadata=metadata or {},
            )

            # Validate content based on data type
            self._validate_content_by_type(entry.data_type, entry.content)

            # Store entry
            self.progress_data[user_id].append(entry)

            # Sort by timestamp to maintain chronological order
            self.progress_data[user_id].sort(key=lambda x: x.timestamp)

            # Clear related caches
            self._clear_user_cache(user_id)

            # Update stats
            self.operation_stats["store"] += 1

            return entry.entry_id

        except (DataValidationError, ProgressDataStorageError):
            raise
        except Exception as e:
            raise ProgressDataStorageError(f"Failed to store progress data: {str(e)}")

    def retrieve_progress_data(
        self,
        user_id: str,
        data_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> List[ProgressDataEntry]:
        """
        Retrieve progress data with filtering options.

        Args:
            user_id: User identifier
            data_type: Filter by data type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of entries to return
            tags: Filter by tags

        Returns:
            List of progress data entries
        """
        # Check cache first
        cache_key = self._generate_cache_key(
            "retrieve", user_id, data_type, start_date, end_date, limit, tags
        )

        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            self.operation_stats["cache_hit"] += 1
            return cached_result

        # Retrieve from storage
        user_data = self.progress_data.get(user_id, [])
        filtered_data = []

        for entry in user_data:
            # Filter by data type
            if data_type and entry.data_type != data_type:
                continue

            # Filter by date range
            if start_date and entry.timestamp < start_date:
                continue
            if end_date and entry.timestamp > end_date:
                continue

            # Filter by tags
            if tags and not any(tag in (entry.tags or []) for tag in tags):
                continue

            filtered_data.append(entry)

        # Sort by timestamp (newest first)
        filtered_data.sort(key=lambda x: x.timestamp, reverse=True)

        # Apply limit
        if limit:
            filtered_data = filtered_data[:limit]

        # Cache result
        self._store_in_cache(cache_key, filtered_data)

        # Update stats
        self.operation_stats["retrieve"] += 1

        return filtered_data

    def analyze_progress_patterns(
        self, user_id: str, analysis_type: str
    ) -> Dict[str, Any]:
        """
        Analyze progress patterns for a user.

        Args:
            user_id: User identifier
            analysis_type: Type of analysis to perform

        Returns:
            Analysis results

        Raises:
            ProgressAnalysisError: If analysis fails
        """
        try:
            # Check analysis cache
            cache_key = f"analysis_{user_id}_{analysis_type}"
            cached_analysis = self.analysis_cache.get(cache_key)

            if cached_analysis and self._is_cache_valid(cache_key):
                return cached_analysis

            # Perform analysis based on type
            if analysis_type == "weight_trends":
                result = self._analyze_weight_trends(user_id)
            elif analysis_type == "strength_progress":
                result = self._analyze_strength_progress(user_id)
            elif analysis_type == "consistency_analysis":
                result = self._analyze_consistency(user_id)
            elif analysis_type == "achievement_summary":
                result = self._analyze_achievements(user_id)
            elif analysis_type == "milestone_progress":
                result = self._analyze_milestone_progress(user_id)
            elif analysis_type == "overall_progress":
                result = self._analyze_overall_progress(user_id)
            else:
                raise ProgressAnalysisError(f"Unknown analysis type: {analysis_type}")

            # Cache analysis result
            self.analysis_cache[cache_key] = result
            self.cache_timestamps[cache_key] = datetime.utcnow()

            return result

        except Exception as e:
            raise ProgressAnalysisError(f"Progress analysis failed: {str(e)}")

    def _analyze_weight_trends(self, user_id: str) -> Dict[str, Any]:
        """Analyze weight loss/gain trends."""
        weight_data = self.retrieve_progress_data(
            user_id,
            data_type="weight",
            start_date=datetime.utcnow() - timedelta(days=90),
        )

        if len(weight_data) < 2:
            return {
                "analysis_type": "weight_trends",
                "status": "insufficient_data",
                "message": "Need at least 2 weight entries for trend analysis",
            }

        weights = [
            (entry.timestamp, entry.content.get("weight", 0)) for entry in weight_data
        ]
        weights.sort(key=lambda x: x[0])

        # Calculate trend
        weight_values = [w[1] for w in weights]
        start_weight = weight_values[0]
        current_weight = weight_values[-1]
        weight_change = current_weight - start_weight
        percent_change = (weight_change / start_weight) * 100 if start_weight > 0 else 0

        # Determine trend direction
        if abs(percent_change) < PROGRESS_THRESHOLDS["plateau_threshold"] * 100:
            trend = TrendDirection.STABLE
        elif weight_change < 0:
            trend = (
                TrendDirection.IMPROVING
                if weight_change
                <= -PROGRESS_THRESHOLDS["significant_improvement"] * start_weight
                else TrendDirection.DECLINING
            )
        else:
            trend = (
                TrendDirection.DECLINING
                if weight_change
                >= PROGRESS_THRESHOLDS["significant_decline"] * start_weight
                else TrendDirection.IMPROVING
            )

        # Calculate average weekly change
        total_days = (weights[-1][0] - weights[0][0]).days
        weekly_change = (weight_change / total_days * 7) if total_days > 0 else 0

        return {
            "analysis_type": "weight_trends",
            "status": "completed",
            "start_weight": start_weight,
            "current_weight": current_weight,
            "total_change": weight_change,
            "percent_change": round(percent_change, 2),
            "weekly_average_change": round(weekly_change, 2),
            "trend_direction": trend.value,
            "data_points": len(weight_data),
            "analysis_period_days": total_days,
            "recommendations": self._generate_weight_recommendations(
                trend, percent_change
            ),
        }

    def _analyze_strength_progress(self, user_id: str) -> Dict[str, Any]:
        """Analyze strength training progress."""
        strength_data = self.retrieve_progress_data(
            user_id,
            data_type="strength",
            start_date=datetime.utcnow() - timedelta(days=60),
        )

        if not strength_data:
            return {
                "analysis_type": "strength_progress",
                "status": "no_data",
                "message": "No strength training data found",
            }

        # Group by exercise
        exercises = defaultdict(list)
        for entry in strength_data:
            exercise = entry.content.get("exercise", "unknown")
            weight = entry.content.get("weight", 0)
            reps = entry.content.get("reps", 0)
            sets = entry.content.get("sets", 0)

            exercises[exercise].append(
                {
                    "timestamp": entry.timestamp,
                    "weight": weight,
                    "reps": reps,
                    "sets": sets,
                    "volume": weight * reps * sets,
                }
            )

        # Analyze each exercise
        exercise_analysis = {}
        overall_improvement = 0

        for exercise, sessions in exercises.items():
            if len(sessions) < 2:
                continue

            sessions.sort(key=lambda x: x["timestamp"])
            start_volume = sessions[0]["volume"]
            current_volume = sessions[-1]["volume"]

            improvement = (
                ((current_volume - start_volume) / start_volume * 100)
                if start_volume > 0
                else 0
            )
            overall_improvement += improvement

            exercise_analysis[exercise] = {
                "sessions": len(sessions),
                "start_volume": start_volume,
                "current_volume": current_volume,
                "improvement_percent": round(improvement, 2),
                "trend": (
                    TrendDirection.IMPROVING.value
                    if improvement > 5
                    else TrendDirection.STABLE.value
                ),
            }

        avg_improvement = (
            overall_improvement / len(exercise_analysis) if exercise_analysis else 0
        )

        return {
            "analysis_type": "strength_progress",
            "status": "completed",
            "exercises_tracked": len(exercise_analysis),
            "average_improvement": round(avg_improvement, 2),
            "exercise_breakdown": exercise_analysis,
            "total_sessions": len(strength_data),
            "recommendations": self._generate_strength_recommendations(avg_improvement),
        }

    def _analyze_consistency(self, user_id: str) -> Dict[str, Any]:
        """Analyze workout consistency."""
        all_data = self.retrieve_progress_data(
            user_id, start_date=datetime.utcnow() - timedelta(days=30)
        )

        if not all_data:
            return {
                "analysis_type": "consistency_analysis",
                "status": "no_data",
                "message": "No workout data found for consistency analysis",
            }

        # Group by day
        daily_activity = defaultdict(list)
        for entry in all_data:
            day = entry.timestamp.date()
            daily_activity[day].append(entry)

        # Calculate consistency metrics
        total_days = 30
        active_days = len(daily_activity)
        consistency_rate = (active_days / total_days) * 100

        # Calculate streaks
        sorted_days = sorted(daily_activity.keys())
        current_streak = 0
        longest_streak = 0
        temp_streak = 0

        # Calculate current streak (from today backwards)
        today = datetime.utcnow().date()
        for i in range(total_days):
            check_date = today - timedelta(days=i)
            if check_date in daily_activity:
                current_streak += 1
            else:
                break

        # Calculate longest streak
        prev_date = None
        for day in sorted_days:
            if prev_date and (day - prev_date).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
            prev_date = day

        # Determine consistency level
        if consistency_rate >= 80:
            level = "excellent"
        elif consistency_rate >= 60:
            level = "good"
        elif consistency_rate >= 40:
            level = "fair"
        else:
            level = "needs_improvement"

        return {
            "analysis_type": "consistency_analysis",
            "status": "completed",
            "consistency_rate": round(consistency_rate, 1),
            "active_days": active_days,
            "total_days": total_days,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "consistency_level": level,
            "weekly_breakdown": self._calculate_weekly_breakdown(daily_activity),
            "recommendations": self._generate_consistency_recommendations(
                consistency_rate, current_streak
            ),
        }

    def _analyze_achievements(self, user_id: str) -> Dict[str, Any]:
        """Analyze user achievements."""
        achievements = self.achievements.get(user_id, [])

        # Group by category
        category_counts = defaultdict(int)
        recent_achievements = []

        for achievement in achievements:
            category = achievement.get("category", "unknown")
            category_counts[category] += 1

            # Check if recent (last 30 days)
            earned_date = datetime.fromisoformat(achievement.get("earned_date", ""))
            if earned_date > datetime.utcnow() - timedelta(days=30):
                recent_achievements.append(achievement)

        total_achievements = len(achievements)
        total_points = sum(a.get("points", 0) for a in achievements)

        return {
            "analysis_type": "achievement_summary",
            "status": "completed",
            "total_achievements": total_achievements,
            "total_points": total_points,
            "recent_achievements": len(recent_achievements),
            "category_breakdown": dict(category_counts),
            "latest_achievements": recent_achievements[:5],
            "achievement_rate": (
                len(recent_achievements) / 30 if recent_achievements else 0
            ),
        }

    def _analyze_milestone_progress(self, user_id: str) -> Dict[str, Any]:
        """Analyze milestone progress."""
        milestones = self.milestones.get(user_id, [])

        if not milestones:
            return {
                "analysis_type": "milestone_progress",
                "status": "no_milestones",
                "message": "No milestones set",
            }

        completed = [m for m in milestones if m.get("status") == "completed"]
        in_progress = [m for m in milestones if m.get("status") == "in_progress"]
        pending = [m for m in milestones if m.get("status") == "pending"]

        completion_rate = (len(completed) / len(milestones)) * 100 if milestones else 0

        return {
            "analysis_type": "milestone_progress",
            "status": "completed",
            "total_milestones": len(milestones),
            "completed": len(completed),
            "in_progress": len(in_progress),
            "pending": len(pending),
            "completion_rate": round(completion_rate, 1),
            "recent_completions": [
                m
                for m in completed
                if datetime.fromisoformat(m.get("completed_date", ""))
                > datetime.utcnow() - timedelta(days=30)
            ],
        }

    def _analyze_overall_progress(self, user_id: str) -> Dict[str, Any]:
        """Comprehensive overall progress analysis."""
        # Get individual analyses
        weight_analysis = self._analyze_weight_trends(user_id)
        strength_analysis = self._analyze_strength_progress(user_id)
        consistency_analysis = self._analyze_consistency(user_id)
        achievement_analysis = self._analyze_achievements(user_id)

        # Calculate overall score
        scores = []

        # Weight score (0-25 points)
        if weight_analysis["status"] == "completed":
            weight_score = min(25, max(0, 15 + weight_analysis["percent_change"] * -2))
            scores.append(weight_score)

        # Strength score (0-25 points)
        if strength_analysis["status"] == "completed":
            strength_score = min(
                25, max(0, strength_analysis["average_improvement"] / 2)
            )
            scores.append(strength_score)

        # Consistency score (0-30 points)
        if consistency_analysis["status"] == "completed":
            consistency_score = consistency_analysis["consistency_rate"] * 0.3
            scores.append(consistency_score)

        # Achievement score (0-20 points)
        achievement_score = min(20, achievement_analysis["total_achievements"] * 2)
        scores.append(achievement_score)

        overall_score = sum(scores)

        # Determine overall grade
        if overall_score >= 80:
            grade = "A"
        elif overall_score >= 70:
            grade = "B"
        elif overall_score >= 60:
            grade = "C"
        elif overall_score >= 50:
            grade = "D"
        else:
            grade = "F"

        return {
            "analysis_type": "overall_progress",
            "status": "completed",
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "component_scores": {
                "weight": scores[0] if len(scores) > 0 else 0,
                "strength": scores[1] if len(scores) > 1 else 0,
                "consistency": scores[2] if len(scores) > 2 else 0,
                "achievements": scores[3] if len(scores) > 3 else 0,
            },
            "summary": self._generate_overall_summary(grade, overall_score),
            "top_strengths": self._identify_strengths(
                weight_analysis, strength_analysis, consistency_analysis
            ),
            "improvement_areas": self._identify_improvement_areas(
                weight_analysis, strength_analysis, consistency_analysis
            ),
        }

    def _validate_content_by_type(self, data_type: str, content: Dict[str, Any]):
        """Validate content based on data type."""
        if data_type == "weight":
            if "weight" not in content:
                raise DataValidationError("Weight data must include 'weight' field")
            if (
                not isinstance(content["weight"], (int, float))
                or content["weight"] <= 0
            ):
                raise DataValidationError("Weight must be a positive number")

        elif data_type == "strength":
            required_fields = ["exercise", "weight", "reps", "sets"]
            for field in required_fields:
                if field not in content:
                    raise DataValidationError(
                        f"Strength data must include '{field}' field"
                    )

        elif data_type == "measurements":
            if not any(
                key in content for key in ["chest", "waist", "hips", "arms", "thighs"]
            ):
                raise DataValidationError(
                    "Measurements must include at least one body measurement"
                )

    def _generate_cache_key(self, operation: str, *args) -> str:
        """Generate cache key from operation and arguments."""
        key_parts = [operation] + [str(arg) for arg in args if arg is not None]
        return hashlib.md5("_".join(key_parts).encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get value from cache if valid."""
        if cache_key not in self.cache:
            return None

        if not self._is_cache_valid(cache_key):
            del self.cache[cache_key]
            del self.cache_timestamps[cache_key]
            return None

        # Update access order for LRU
        if cache_key in self.cache_access_order:
            self.cache_access_order.remove(cache_key)
        self.cache_access_order.append(cache_key)

        return self.cache[cache_key]

    def _store_in_cache(self, cache_key: str, value: Any):
        """Store value in cache with LRU eviction."""
        # Remove oldest entries if cache is full
        while len(self.cache) >= self.max_cache_size:
            oldest_key = self.cache_access_order.popleft()
            del self.cache[oldest_key]
            del self.cache_timestamps[oldest_key]

        self.cache[cache_key] = value
        self.cache_timestamps[cache_key] = datetime.utcnow()
        self.cache_access_order.append(cache_key)

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self.cache_timestamps:
            return False

        timestamp = self.cache_timestamps[cache_key]
        return (datetime.utcnow() - timestamp).total_seconds() < self.cache_ttl

    def _clear_user_cache(self, user_id: str):
        """Clear cache entries for a specific user."""
        keys_to_remove = []
        for key in self.cache.keys():
            if user_id in key:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            if key in self.cache:
                del self.cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
            if key in self.cache_access_order:
                self.cache_access_order.remove(key)

    def get_service_stats(self) -> Dict[str, Any]:
        """Get service performance statistics."""
        return {
            "total_users": len(self.progress_data),
            "total_entries": sum(
                len(entries) for entries in self.progress_data.values()
            ),
            "cache_size": len(self.cache),
            "cache_hit_rate": self.operation_stats.get("cache_hit", 0)
            / max(1, self.operation_stats.get("retrieve", 1)),
            "operations": dict(self.operation_stats),
            "analysis_cache_size": len(self.analysis_cache),
        }

    # Helper methods for generating recommendations and summaries
    def _generate_weight_recommendations(
        self, trend: TrendDirection, percent_change: float
    ) -> List[str]:
        """Generate weight-specific recommendations."""
        recommendations = []

        if trend == TrendDirection.STABLE:
            recommendations.append(
                "Your weight is stable. Consider adjusting your nutrition or exercise routine if you have specific goals."
            )
        elif trend == TrendDirection.IMPROVING and percent_change < -5:
            recommendations.append(
                "Great progress on weight loss! Maintain your current routine."
            )
        elif trend == TrendDirection.DECLINING and percent_change > 5:
            recommendations.append(
                "Consider reviewing your nutrition and exercise plan to support your goals."
            )

        return recommendations

    def _generate_strength_recommendations(self, avg_improvement: float) -> List[str]:
        """Generate strength-specific recommendations."""
        recommendations = []

        if avg_improvement > 10:
            recommendations.append(
                "Excellent strength gains! Keep pushing yourself with progressive overload."
            )
        elif avg_improvement > 0:
            recommendations.append(
                "Good progress on strength. Consider increasing weights or volume gradually."
            )
        else:
            recommendations.append(
                "Focus on proper form and consistent training to see strength improvements."
            )

        return recommendations

    def _generate_consistency_recommendations(
        self, consistency_rate: float, current_streak: int
    ) -> List[str]:
        """Generate consistency-specific recommendations."""
        recommendations = []

        if consistency_rate >= 80:
            recommendations.append(
                "Outstanding consistency! You're building excellent habits."
            )
        elif consistency_rate >= 60:
            recommendations.append(
                "Good consistency. Try to increase your workout frequency slightly."
            )
        else:
            recommendations.append(
                "Focus on building a sustainable routine. Start with shorter, more frequent workouts."
            )

        if current_streak == 0:
            recommendations.append(
                "Start a new streak today! Even a short workout counts."
            )

        return recommendations

    def _calculate_weekly_breakdown(self, daily_activity: Dict) -> List[int]:
        """Calculate weekly activity breakdown."""
        # Implementation for weekly breakdown calculation
        return [0, 0, 0, 0]  # Placeholder

    def _generate_overall_summary(self, grade: str, score: float) -> str:
        """Generate overall progress summary."""
        if grade == "A":
            return (
                "Outstanding progress across all areas! You're exceeding expectations."
            )
        elif grade == "B":
            return "Great progress! You're on track with your fitness goals."
        elif grade == "C":
            return "Good progress with room for improvement in some areas."
        else:
            return "Keep working! Focus on consistency and gradual improvements."

    def _identify_strengths(
        self, weight_analysis: Dict, strength_analysis: Dict, consistency_analysis: Dict
    ) -> List[str]:
        """Identify user's top strengths."""
        strengths = []

        if consistency_analysis.get("consistency_rate", 0) >= 70:
            strengths.append("Excellent workout consistency")

        if strength_analysis.get("average_improvement", 0) > 5:
            strengths.append("Strong strength progression")

        if weight_analysis.get("trend_direction") == "improving":
            strengths.append("Positive weight trends")

        return strengths[:3]  # Return top 3 strengths

    def _identify_improvement_areas(
        self, weight_analysis: Dict, strength_analysis: Dict, consistency_analysis: Dict
    ) -> List[str]:
        """Identify areas needing improvement."""
        areas = []

        if consistency_analysis.get("consistency_rate", 100) < 60:
            areas.append("Workout consistency")

        if strength_analysis.get("average_improvement", 100) <= 0:
            areas.append("Strength progression")

        if weight_analysis.get("trend_direction") == "declining":
            areas.append("Weight management")

        return areas[:3]  # Return top 3 improvement areas
