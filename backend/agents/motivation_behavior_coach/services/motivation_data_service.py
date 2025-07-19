"""
Data management service for SPARK Motivation Behavior Coach.
Provides behavioral data operations, caching, and persistence.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class BehavioralDataEntry:
    """Structure for behavioral data entries."""

    user_id: str
    data_type: str
    content: Dict[str, Any]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "data_type": self.data_type,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BehavioralDataEntry":
        """Create from dictionary."""
        return cls(
            user_id=data["user_id"],
            data_type=data["data_type"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata"),
        )


class MotivationDataService:
    """
    Data management service for behavioral and motivational data.

    Provides operations for storing, retrieving, analyzing, and managing
    behavioral change data with caching and performance optimization.
    """

    def __init__(self, cache_ttl_seconds: int = 3600, max_cache_size: int = 1000):
        """
        Initialize data service.

        Args:
            cache_ttl_seconds: Cache time-to-live in seconds
            max_cache_size: Maximum number of cached entries
        """
        self.cache_ttl_seconds = cache_ttl_seconds
        self.max_cache_size = max_cache_size

        # In-memory storage (in production, this would be a database)
        self.behavioral_data: Dict[str, List[BehavioralDataEntry]] = defaultdict(list)
        self.user_profiles: Dict[str, Dict[str, Any]] = {}

        # Cache for frequently accessed data
        self.cache: Dict[str, Tuple[Any, float]] = {}  # key: (data, timestamp)

        logger.info("MotivationDataService initialized")

    def store_behavioral_data(
        self,
        user_id: str,
        data_type: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store behavioral data entry.

        Args:
            user_id: User identifier
            data_type: Type of behavioral data
            content: Data content
            metadata: Optional metadata

        Returns:
            str: Entry identifier

        Raises:
            ValueError: If data is invalid
        """
        try:
            # Validate inputs
            if not user_id or not isinstance(user_id, str):
                raise ValueError("Invalid user_id")

            if not data_type or not isinstance(data_type, str):
                raise ValueError("Invalid data_type")

            if not content or not isinstance(content, dict):
                raise ValueError("Invalid content")

            # Create data entry
            entry = BehavioralDataEntry(
                user_id=user_id,
                data_type=data_type,
                content=content,
                timestamp=datetime.utcnow(),
                metadata=metadata,
            )

            # Store in user's data list
            self.behavioral_data[user_id].append(entry)

            # Invalidate related cache entries
            self._invalidate_user_cache(user_id)

            # Generate entry ID
            entry_id = f"{user_id}_{data_type}_{int(entry.timestamp.timestamp())}"

            logger.info(f"Stored behavioral data: {data_type} for user {user_id}")
            return entry_id

        except Exception as e:
            logger.error(f"Failed to store behavioral data: {str(e)}")
            raise ValueError(f"Failed to store behavioral data: {str(e)}")

    def retrieve_behavioral_data(
        self,
        user_id: str,
        data_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[BehavioralDataEntry]:
        """
        Retrieve behavioral data for user.

        Args:
            user_id: User identifier
            data_type: Filter by data type (optional)
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            limit: Maximum number of entries to return (optional)

        Returns:
            List of behavioral data entries
        """
        try:
            # Check cache first
            cache_key = (
                f"behavioral_data_{user_id}_{data_type}_{start_date}_{end_date}_{limit}"
            )
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

            # Get user's data
            user_data = self.behavioral_data.get(user_id, [])

            # Apply filters
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

                filtered_data.append(entry)

            # Sort by timestamp (newest first)
            filtered_data.sort(key=lambda x: x.timestamp, reverse=True)

            # Apply limit
            if limit:
                filtered_data = filtered_data[:limit]

            # Cache the result
            self._store_in_cache(cache_key, filtered_data)

            return filtered_data

        except Exception as e:
            logger.error(f"Failed to retrieve behavioral data: {str(e)}")
            return []

    def analyze_behavior_patterns(
        self, user_id: str, analysis_type: str
    ) -> Dict[str, Any]:
        """
        Analyze behavioral patterns for user.

        Args:
            user_id: User identifier
            analysis_type: Type of analysis to perform

        Returns:
            Dict containing analysis results
        """
        try:
            # Check cache first
            cache_key = f"behavior_analysis_{user_id}_{analysis_type}"
            cached_analysis = self._get_from_cache(cache_key)
            if cached_analysis is not None:
                return cached_analysis

            # Get recent behavioral data
            recent_data = self.retrieve_behavioral_data(
                user_id=user_id,
                start_date=datetime.utcnow() - timedelta(days=30),
                limit=100,
            )

            if not recent_data:
                return {"analysis_type": analysis_type, "patterns": [], "insights": []}

            # Perform analysis based on type
            if analysis_type == "motivation_trends":
                analysis = self._analyze_motivation_trends(recent_data)
            elif analysis_type == "habit_consistency":
                analysis = self._analyze_habit_consistency(recent_data)
            elif analysis_type == "goal_progress":
                analysis = self._analyze_goal_progress(recent_data)
            elif analysis_type == "obstacle_patterns":
                analysis = self._analyze_obstacle_patterns(recent_data)
            else:
                analysis = {
                    "analysis_type": analysis_type,
                    "error": "Unknown analysis type",
                }

            # Cache the analysis
            self._store_in_cache(cache_key, analysis)

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze behavior patterns: {str(e)}")
            return {"analysis_type": analysis_type, "error": str(e)}

    def _analyze_motivation_trends(
        self, data: List[BehavioralDataEntry]
    ) -> Dict[str, Any]:
        """Analyze motivation level trends."""
        motivation_scores = []
        dates = []

        for entry in data:
            if entry.data_type == "motivation_assessment":
                score = entry.content.get("motivation_score")
                if score is not None:
                    motivation_scores.append(float(score))
                    dates.append(entry.timestamp)

        if not motivation_scores:
            return {"analysis_type": "motivation_trends", "trend": "insufficient_data"}

        # Calculate trend
        avg_score = sum(motivation_scores) / len(motivation_scores)
        recent_scores = motivation_scores[:5]  # Last 5 scores
        recent_avg = (
            sum(recent_scores) / len(recent_scores) if recent_scores else avg_score
        )

        trend = "stable"
        if recent_avg > avg_score + 0.5:
            trend = "improving"
        elif recent_avg < avg_score - 0.5:
            trend = "declining"

        return {
            "analysis_type": "motivation_trends",
            "trend": trend,
            "average_score": round(avg_score, 2),
            "recent_average": round(recent_avg, 2),
            "total_assessments": len(motivation_scores),
            "date_range": {
                "start": min(dates).isoformat() if dates else None,
                "end": max(dates).isoformat() if dates else None,
            },
        }

    def _analyze_habit_consistency(
        self, data: List[BehavioralDataEntry]
    ) -> Dict[str, Any]:
        """Analyze habit tracking consistency."""
        habit_tracking = defaultdict(list)

        for entry in data:
            if entry.data_type == "habit_tracking":
                habit_name = entry.content.get("habit_name")
                completed = entry.content.get("completed", False)
                if habit_name:
                    habit_tracking[habit_name].append(
                        {"completed": completed, "date": entry.timestamp.date()}
                    )

        if not habit_tracking:
            return {"analysis_type": "habit_consistency", "habits": []}

        habit_analysis = []
        for habit_name, records in habit_tracking.items():
            total_days = len(records)
            completed_days = sum(1 for r in records if r["completed"])
            consistency_rate = completed_days / total_days if total_days > 0 else 0

            # Calculate streak
            current_streak = 0
            for record in sorted(records, key=lambda x: x["date"], reverse=True):
                if record["completed"]:
                    current_streak += 1
                else:
                    break

            habit_analysis.append(
                {
                    "habit_name": habit_name,
                    "consistency_rate": round(consistency_rate, 2),
                    "current_streak": current_streak,
                    "total_days_tracked": total_days,
                    "completed_days": completed_days,
                }
            )

        return {
            "analysis_type": "habit_consistency",
            "habits": habit_analysis,
            "overall_consistency": (
                round(
                    sum(h["consistency_rate"] for h in habit_analysis)
                    / len(habit_analysis),
                    2,
                )
                if habit_analysis
                else 0
            ),
        }

    def _analyze_goal_progress(self, data: List[BehavioralDataEntry]) -> Dict[str, Any]:
        """Analyze goal progress patterns."""
        goal_updates = defaultdict(list)

        for entry in data:
            if entry.data_type == "goal_progress":
                goal_id = entry.content.get("goal_id")
                progress_percentage = entry.content.get("progress_percentage")
                if goal_id and progress_percentage is not None:
                    goal_updates[goal_id].append(
                        {
                            "progress": float(progress_percentage),
                            "date": entry.timestamp,
                        }
                    )

        if not goal_updates:
            return {"analysis_type": "goal_progress", "goals": []}

        goal_analysis = []
        for goal_id, updates in goal_updates.items():
            updates.sort(key=lambda x: x["date"])

            if len(updates) >= 2:
                initial_progress = updates[0]["progress"]
                latest_progress = updates[-1]["progress"]
                progress_change = latest_progress - initial_progress

                # Calculate average weekly progress
                time_span = (updates[-1]["date"] - updates[0]["date"]).days
                weekly_progress = (
                    (progress_change / max(time_span, 1)) * 7 if time_span > 0 else 0
                )
            else:
                latest_progress = updates[0]["progress"] if updates else 0
                progress_change = 0
                weekly_progress = 0

            goal_analysis.append(
                {
                    "goal_id": goal_id,
                    "latest_progress": round(latest_progress, 2),
                    "progress_change": round(progress_change, 2),
                    "weekly_progress_rate": round(weekly_progress, 2),
                    "total_updates": len(updates),
                }
            )

        return {
            "analysis_type": "goal_progress",
            "goals": goal_analysis,
            "active_goals": len(goal_analysis),
        }

    def _analyze_obstacle_patterns(
        self, data: List[BehavioralDataEntry]
    ) -> Dict[str, Any]:
        """Analyze obstacle occurrence patterns."""
        obstacles = defaultdict(int)
        obstacle_dates = defaultdict(list)

        for entry in data:
            if entry.data_type == "obstacle_report":
                obstacle_type = entry.content.get("obstacle_type")
                if obstacle_type:
                    obstacles[obstacle_type] += 1
                    obstacle_dates[obstacle_type].append(entry.timestamp)

        if not obstacles:
            return {"analysis_type": "obstacle_patterns", "patterns": []}

        patterns = []
        for obstacle_type, count in obstacles.items():
            dates = obstacle_dates[obstacle_type]

            # Calculate frequency
            if len(dates) >= 2:
                time_span = (max(dates) - min(dates)).days
                frequency_per_week = (
                    (count / max(time_span, 1)) * 7 if time_span > 0 else count
                )
            else:
                frequency_per_week = count

            patterns.append(
                {
                    "obstacle_type": obstacle_type,
                    "occurrence_count": count,
                    "frequency_per_week": round(frequency_per_week, 2),
                    "last_occurrence": max(dates).isoformat() if dates else None,
                }
            )

        # Sort by frequency
        patterns.sort(key=lambda x: x["occurrence_count"], reverse=True)

        return {
            "analysis_type": "obstacle_patterns",
            "patterns": patterns,
            "total_obstacles": sum(obstacles.values()),
            "unique_obstacle_types": len(obstacles),
        }

    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """
        Update user profile information.

        Args:
            user_id: User identifier
            profile_data: Profile data to update
        """
        try:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {}

            self.user_profiles[user_id].update(profile_data)
            self.user_profiles[user_id]["last_updated"] = datetime.utcnow().isoformat()

            # Invalidate user cache
            self._invalidate_user_cache(user_id)

            logger.info(f"Updated user profile for {user_id}")

        except Exception as e:
            logger.error(f"Failed to update user profile: {str(e)}")
            raise ValueError(f"Failed to update user profile: {str(e)}")

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile information.

        Args:
            user_id: User identifier

        Returns:
            Dict containing user profile data
        """
        return self.user_profiles.get(user_id, {})

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get data from cache if not expired."""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl_seconds:
                return data
            else:
                # Remove expired entry
                del self.cache[key]
        return None

    def _store_in_cache(self, key: str, data: Any):
        """Store data in cache with cleanup if needed."""
        # Clean up cache if it's getting too large
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entries
            sorted_cache = sorted(self.cache.items(), key=lambda x: x[1][1])
            for old_key, _ in sorted_cache[: self.max_cache_size // 4]:
                del self.cache[old_key]

        self.cache[key] = (data, time.time())

    def _invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a user."""
        keys_to_remove = [key for key in self.cache.keys() if user_id in key]
        for key in keys_to_remove:
            del self.cache[key]

    def get_service_status(self) -> Dict[str, Any]:
        """
        Get current service status.

        Returns:
            Dict containing service status information
        """
        total_users = len(self.behavioral_data)
        total_entries = sum(len(entries) for entries in self.behavioral_data.values())

        return {
            "total_users": total_users,
            "total_data_entries": total_entries,
            "cache_size": len(self.cache),
            "cache_hit_rate": "not_tracked",  # Would be implemented with proper metrics
            "service_status": "operational",
        }
