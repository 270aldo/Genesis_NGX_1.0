"""
Security service for BLAZE Elite Training Strategist.
Handles secure processing of athlete data and training information.
"""

import hashlib
import hmac
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from core.logging_config import get_logger
from ..core.exceptions import BlazeTrainingError
from ..core.config import BlazeAgentConfig

logger = get_logger(__name__)


class TrainingSecurityService:
    """
    Security service for training data and athlete information.

    Provides data sanitization, validation, and audit logging
    for sensitive training and performance data.
    """

    def __init__(self, config: BlazeAgentConfig):
        self.config = config
        self._audit_log = []

    def sanitize_athlete_data(self, athlete_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize athlete profile data for secure processing.

        Args:
            athlete_data: Raw athlete profile data

        Returns:
            Sanitized athlete data

        Raises:
            BlazeTrainingError: If data fails security validation
        """
        try:
            sanitized = {}

            # Required fields validation
            required_fields = ["age", "fitness_level", "training_goals"]
            for field in required_fields:
                if field not in athlete_data:
                    raise BlazeTrainingError(f"Missing required field: {field}")

            # Age validation and sanitization
            age = athlete_data.get("age")
            if not isinstance(age, (int, float)) or age < 12 or age > 100:
                raise BlazeTrainingError("Invalid age: must be between 12 and 100")
            sanitized["age"] = int(age)

            # Fitness level validation
            valid_levels = [
                "beginner",
                "intermediate",
                "advanced",
                "elite",
                "professional",
            ]
            fitness_level = athlete_data.get("fitness_level", "").lower()
            if fitness_level not in valid_levels:
                raise BlazeTrainingError(f"Invalid fitness level: {fitness_level}")
            sanitized["fitness_level"] = fitness_level

            # Training goals sanitization
            goals = athlete_data.get("training_goals", [])
            if isinstance(goals, str):
                goals = [goals]
            valid_goals = [
                "strength",
                "power",
                "endurance",
                "hypertrophy",
                "fat_loss",
                "athletic_performance",
                "injury_prevention",
                "mobility",
                "rehabilitation",
            ]
            sanitized_goals = [
                goal.lower() for goal in goals if goal.lower() in valid_goals
            ]
            if not sanitized_goals:
                raise BlazeTrainingError("No valid training goals provided")
            sanitized["training_goals"] = sanitized_goals

            # Optional fields sanitization
            if "weight" in athlete_data:
                weight = athlete_data["weight"]
                if isinstance(weight, (int, float)) and 30 <= weight <= 300:
                    sanitized["weight"] = float(weight)

            if "height" in athlete_data:
                height = athlete_data["height"]
                if isinstance(height, (int, float)) and 100 <= height <= 250:
                    sanitized["height"] = float(height)

            if "injuries" in athlete_data:
                injuries = athlete_data["injuries"]
                if isinstance(injuries, list):
                    sanitized["injuries"] = [
                        str(injury)[:100] for injury in injuries[:10]
                    ]

            if "equipment_access" in athlete_data:
                equipment = athlete_data["equipment_access"]
                if isinstance(equipment, list):
                    sanitized["equipment_access"] = [
                        str(eq)[:50] for eq in equipment[:20]
                    ]

            self._log_audit_event(
                "athlete_data_sanitized", {"fields": list(sanitized.keys())}
            )

            return sanitized

        except Exception as e:
            self._log_audit_event("athlete_data_sanitization_failed", {"error": str(e)})
            if isinstance(e, BlazeTrainingError):
                raise
            raise BlazeTrainingError(f"Data sanitization failed: {str(e)}")

    def validate_training_parameters(
        self, training_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate and sanitize training parameters.

        Args:
            training_params: Training parameters to validate

        Returns:
            Validated training parameters
        """
        validated = {}

        # Duration validation
        if "duration_weeks" in training_params:
            duration = training_params["duration_weeks"]
            if isinstance(duration, (int, float)) and 1 <= duration <= 52:
                validated["duration_weeks"] = int(duration)

        # Sessions per week validation
        if "sessions_per_week" in training_params:
            sessions = training_params["sessions_per_week"]
            if isinstance(sessions, (int, float)) and 1 <= sessions <= 14:
                validated["sessions_per_week"] = int(sessions)

        # Intensity validation
        if "intensity_distribution" in training_params:
            intensity = training_params["intensity_distribution"]
            if isinstance(intensity, str) and intensity in [
                "polarized",
                "pyramidal",
                "threshold",
            ]:
                validated["intensity_distribution"] = intensity

        # Phase validation
        if "training_phase" in training_params:
            phase = training_params["training_phase"]
            valid_phases = [
                "preparation",
                "base_building",
                "build",
                "peak",
                "competition",
                "recovery",
            ]
            if phase in valid_phases:
                validated["training_phase"] = phase

        self._log_audit_event(
            "training_parameters_validated", {"parameters": list(validated.keys())}
        )

        return validated

    def secure_performance_data(
        self, performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Secure and validate performance data.

        Args:
            performance_data: Raw performance data

        Returns:
            Secured performance data
        """
        secured = {}

        # Timestamp validation
        if "timestamp" in performance_data:
            try:
                if isinstance(performance_data["timestamp"], str):
                    timestamp = datetime.fromisoformat(performance_data["timestamp"])
                else:
                    timestamp = performance_data["timestamp"]

                # Ensure timestamp is not in the future
                if timestamp <= datetime.now(timezone.utc):
                    secured["timestamp"] = timestamp.isoformat()
            except (ValueError, TypeError):
                pass

        # Numeric metrics validation
        numeric_fields = ["heart_rate", "power", "speed", "distance", "duration", "rpe"]
        for field in numeric_fields:
            if field in performance_data:
                value = performance_data[field]
                if isinstance(value, (int, float)) and value >= 0:
                    secured[field] = float(value)

        # Exercise name sanitization
        if "exercise" in performance_data:
            exercise = str(performance_data["exercise"])[:100]
            secured["exercise"] = exercise

        # Notes sanitization
        if "notes" in performance_data:
            notes = str(performance_data["notes"])[:500]
            secured["notes"] = notes

        self._log_audit_event(
            "performance_data_secured", {"fields": list(secured.keys())}
        )

        return secured

    def generate_secure_session_id(self, athlete_id: str, timestamp: str) -> str:
        """
        Generate secure session ID for training session tracking.

        Args:
            athlete_id: Athlete identifier
            timestamp: Session timestamp

        Returns:
            Secure session ID
        """
        session_data = f"{athlete_id}:{timestamp}:{datetime.now().isoformat()}"
        session_id = hashlib.sha256(session_data.encode()).hexdigest()[:16]

        self._log_audit_event("session_id_generated", {"athlete_id": athlete_id[:8]})

        return session_id

    def validate_biometric_data(self, biometric_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate biometric data for training integration.

        Args:
            biometric_data: Raw biometric data

        Returns:
            Validated biometric data
        """
        validated = {}

        # Heart rate validation
        if "heart_rate" in biometric_data:
            hr = biometric_data["heart_rate"]
            if isinstance(hr, (int, float)) and 30 <= hr <= 220:
                validated["heart_rate"] = float(hr)

        # HRV validation
        if "hrv" in biometric_data:
            hrv = biometric_data["hrv"]
            if isinstance(hrv, (int, float)) and 0 <= hrv <= 200:
                validated["hrv"] = float(hrv)

        # Sleep score validation
        if "sleep_score" in biometric_data:
            sleep = biometric_data["sleep_score"]
            if isinstance(sleep, (int, float)) and 0 <= sleep <= 100:
                validated["sleep_score"] = float(sleep)

        # Recovery score validation
        if "recovery_score" in biometric_data:
            recovery = biometric_data["recovery_score"]
            if isinstance(recovery, (int, float)) and 0 <= recovery <= 100:
                validated["recovery_score"] = float(recovery)

        self._log_audit_event(
            "biometric_data_validated", {"metrics": list(validated.keys())}
        )

        return validated

    def _log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """Log audit event for security tracking."""
        if self.config.log_training_sessions:
            audit_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "details": details,
                "component": "TrainingSecurityService",
            }
            self._audit_log.append(audit_entry)
            logger.info(f"Audit: {event_type}", extra=audit_entry)

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log entries."""
        return self._audit_log.copy()

    def clear_audit_log(self):
        """Clear audit log entries."""
        self._audit_log.clear()
        logger.info("Audit log cleared")
