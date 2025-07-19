"""
Data management service for BLAZE Elite Training Strategist.
Handles training data persistence, retrieval, and analysis.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import json

from core.logging_config import get_logger
from clients.supabase_client import SupabaseClient
from ..core.exceptions import BlazeTrainingError, TrainingProgressTrackingError
from ..core.config import BlazeAgentConfig
from ..core.constants import TrainingPhase, TrainingGoal, AthleteLevel

logger = get_logger(__name__)


class TrainingDataService:
    """
    Data management service for training programs and athlete performance.

    Provides centralized data operations for training plans, progress tracking,
    and performance analytics with efficient caching and retrieval.
    """

    def __init__(self, supabase_client: SupabaseClient, config: BlazeAgentConfig):
        self.supabase = supabase_client
        self.config = config
        self._cache = {}
        self._cache_timestamps = {}

    async def save_training_plan(
        self, athlete_id: str, training_plan: Dict[str, Any]
    ) -> str:
        """
        Save training plan to database.

        Args:
            athlete_id: Unique athlete identifier
            training_plan: Complete training plan data

        Returns:
            Training plan ID

        Raises:
            BlazeTrainingError: If save operation fails
        """
        try:
            plan_data = {
                "athlete_id": athlete_id,
                "plan_data": training_plan,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "duration_weeks": training_plan.get("duration_weeks", 12),
                "training_phase": training_plan.get("training_phase", "preparation"),
                "goals": training_plan.get("training_goals", []),
            }

            result = await self.supabase.insert("training_plans", plan_data)

            if result and len(result) > 0:
                plan_id = result[0]["id"]
                logger.info(f"Training plan saved successfully: {plan_id}")

                # Cache the plan
                cache_key = f"training_plan_{plan_id}"
                self._cache[cache_key] = training_plan
                self._cache_timestamps[cache_key] = datetime.now()

                return plan_id
            else:
                raise BlazeTrainingError(
                    "Failed to save training plan: no result returned"
                )

        except Exception as e:
            logger.error(f"Error saving training plan: {str(e)}")
            raise BlazeTrainingError(f"Failed to save training plan: {str(e)}")

    async def get_training_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve training plan by ID.

        Args:
            plan_id: Training plan identifier

        Returns:
            Training plan data or None if not found
        """
        try:
            # Check cache first
            cache_key = f"training_plan_{plan_id}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]

            result = await self.supabase.select("training_plans", "*", {"id": plan_id})

            if result and len(result) > 0:
                plan_data = result[0]["plan_data"]

                # Update cache
                self._cache[cache_key] = plan_data
                self._cache_timestamps[cache_key] = datetime.now()

                return plan_data

            return None

        except Exception as e:
            logger.error(f"Error retrieving training plan {plan_id}: {str(e)}")
            return None

    async def save_workout_session(
        self, athlete_id: str, session_data: Dict[str, Any]
    ) -> str:
        """
        Save workout session data.

        Args:
            athlete_id: Athlete identifier
            session_data: Workout session details

        Returns:
            Session ID
        """
        try:
            session_record = {
                "athlete_id": athlete_id,
                "session_data": session_data,
                "completed_at": datetime.now().isoformat(),
                "duration_minutes": session_data.get("duration_minutes", 0),
                "exercises_completed": session_data.get("exercises_completed", []),
                "performance_metrics": session_data.get("performance_metrics", {}),
                "rpe": session_data.get("rpe"),
                "notes": session_data.get("notes", ""),
            }

            result = await self.supabase.insert("workout_sessions", session_record)

            if result and len(result) > 0:
                session_id = result[0]["id"]
                logger.info(f"Workout session saved: {session_id}")
                return session_id
            else:
                raise BlazeTrainingError("Failed to save workout session")

        except Exception as e:
            logger.error(f"Error saving workout session: {str(e)}")
            raise BlazeTrainingError(f"Failed to save workout session: {str(e)}")

    async def get_athlete_progress(
        self, athlete_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """
        Get athlete progress data over specified period.

        Args:
            athlete_id: Athlete identifier
            days: Number of days to analyze

        Returns:
            Progress analysis data
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Get workout sessions
            sessions = await self.supabase.select(
                "workout_sessions",
                "*",
                {
                    "athlete_id": athlete_id,
                    "completed_at.gte": start_date.isoformat(),
                    "completed_at.lte": end_date.isoformat(),
                },
            )

            if not sessions:
                return {"sessions": 0, "progress": "insufficient_data"}

            # Analyze progress
            total_sessions = len(sessions)
            total_duration = sum(s.get("duration_minutes", 0) for s in sessions)
            average_rpe = self._calculate_average_rpe(sessions)

            # Calculate trends
            weekly_sessions = self._calculate_weekly_sessions(sessions)
            strength_progress = self._analyze_strength_progress(sessions)

            progress_data = {
                "total_sessions": total_sessions,
                "total_duration_minutes": total_duration,
                "average_duration": (
                    total_duration / total_sessions if total_sessions > 0 else 0
                ),
                "average_rpe": average_rpe,
                "weekly_sessions": weekly_sessions,
                "strength_progress": strength_progress,
                "period_days": days,
                "last_updated": datetime.now().isoformat(),
            }

            return progress_data

        except Exception as e:
            logger.error(f"Error getting athlete progress: {str(e)}")
            raise TrainingProgressTrackingError(f"Failed to analyze progress: {str(e)}")

    async def get_training_history(
        self, athlete_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get athlete training history.

        Args:
            athlete_id: Athlete identifier
            limit: Maximum number of sessions to return

        Returns:
            List of training sessions
        """
        try:
            sessions = await self.supabase.select(
                "workout_sessions",
                "*",
                {"athlete_id": athlete_id},
                order_by="completed_at.desc",
                limit=limit,
            )

            return sessions or []

        except Exception as e:
            logger.error(f"Error getting training history: {str(e)}")
            return []

    async def update_athlete_profile(
        self, athlete_id: str, profile_updates: Dict[str, Any]
    ) -> bool:
        """
        Update athlete profile data.

        Args:
            athlete_id: Athlete identifier
            profile_updates: Fields to update

        Returns:
            Success status
        """
        try:
            update_data = {
                **profile_updates,
                "updated_at": datetime.now().isoformat(),
            }

            result = await self.supabase.update(
                "athlete_profiles", update_data, {"id": athlete_id}
            )

            if result:
                logger.info(f"Athlete profile updated: {athlete_id}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Error updating athlete profile: {str(e)}")
            return False

    async def get_performance_metrics(
        self, athlete_id: str, exercise: str, days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Get performance metrics for specific exercise.

        Args:
            athlete_id: Athlete identifier
            exercise: Exercise name
            days: Analysis period in days

        Returns:
            Performance metrics over time
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            sessions = await self.supabase.select(
                "workout_sessions",
                "*",
                {
                    "athlete_id": athlete_id,
                    "completed_at.gte": start_date.isoformat(),
                },
            )

            # Filter sessions with the specific exercise
            exercise_metrics = []
            for session in sessions or []:
                exercises = session.get("exercises_completed", [])
                for ex in exercises:
                    if ex.get("name", "").lower() == exercise.lower():
                        exercise_metrics.append(
                            {
                                "date": session["completed_at"],
                                "weight": ex.get("weight"),
                                "reps": ex.get("reps"),
                                "sets": ex.get("sets"),
                                "volume": ex.get("volume"),
                                "rpe": ex.get("rpe"),
                            }
                        )

            return exercise_metrics

        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return []

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self._cache or cache_key not in self._cache_timestamps:
            return False

        cache_age = datetime.now() - self._cache_timestamps[cache_key]
        return cache_age.total_seconds() < self.config.cache_ttl_seconds

    def _calculate_average_rpe(self, sessions: List[Dict[str, Any]]) -> Optional[float]:
        """Calculate average RPE from sessions."""
        rpes = [s.get("rpe") for s in sessions if s.get("rpe") is not None]
        return sum(rpes) / len(rpes) if rpes else None

    def _calculate_weekly_sessions(self, sessions: List[Dict[str, Any]]) -> List[int]:
        """Calculate sessions per week trend."""
        # Group sessions by week and count
        weekly_counts = {}
        for session in sessions:
            try:
                date = datetime.fromisoformat(session["completed_at"])
                week_key = date.strftime("%Y-W%U")
                weekly_counts[week_key] = weekly_counts.get(week_key, 0) + 1
            except (ValueError, KeyError):
                continue

        return list(weekly_counts.values())

    def _analyze_strength_progress(
        self, sessions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze strength progression trends."""
        # Track key compound movements
        key_exercises = ["squat", "deadlift", "bench_press", "overhead_press"]
        progress = {}

        for exercise in key_exercises:
            exercise_data = []
            for session in sessions:
                exercises = session.get("exercises_completed", [])
                for ex in exercises:
                    if exercise in ex.get("name", "").lower():
                        if ex.get("weight") and ex.get("reps"):
                            exercise_data.append(
                                {
                                    "date": session["completed_at"],
                                    "weight": ex["weight"],
                                    "reps": ex["reps"],
                                    "estimated_1rm": ex["weight"]
                                    * (1 + ex["reps"] / 30),
                                }
                            )

            if exercise_data:
                # Sort by date and calculate trend
                exercise_data.sort(key=lambda x: x["date"])
                latest_1rm = exercise_data[-1]["estimated_1rm"]
                initial_1rm = exercise_data[0]["estimated_1rm"]
                progress[exercise] = {
                    "improvement_percentage": ((latest_1rm - initial_1rm) / initial_1rm)
                    * 100,
                    "sessions_tracked": len(exercise_data),
                    "latest_estimated_1rm": latest_1rm,
                }

        return progress

    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Training data cache cleared")
