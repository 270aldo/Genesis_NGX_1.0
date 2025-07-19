"""
Adherence Monitoring Service - NGX Agents Advanced AI
Real-time monitoring and intervention system for user adherence.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from .adherence_prediction_engine import (
    AdherencePredictionEngine,
    AdherenceMetrics,
    AdherencePrediction,
    AdherenceRiskLevel,
    AdherenceTrigger,
)
from clients.vertex_ai.vertex_ai_client import VertexAIClient
from core.redis_pool import get_redis_client
from core.telemetry import trace_async
from tasks.critical import send_adherence_alert

logger = logging.getLogger(__name__)


class InterventionType(Enum):
    """Types of adherence interventions."""

    AUTOMATED_MESSAGE = "automated_message"
    PUSH_NOTIFICATION = "push_notification"
    AGENT_OUTREACH = "agent_outreach"
    PROTOCOL_ADJUSTMENT = "protocol_adjustment"
    GOAL_SIMPLIFICATION = "goal_simplification"
    SOCIAL_SUPPORT = "social_support"
    CONTENT_PERSONALIZATION = "content_personalization"
    GAMIFICATION_BOOST = "gamification_boost"


@dataclass
class InterventionResult:
    """Result of an adherence intervention."""

    intervention_id: str
    user_id: str
    intervention_type: InterventionType
    executed_at: datetime
    success: bool
    user_response: Optional[str]
    adherence_impact: Optional[float]  # Change in adherence probability
    next_intervention_delay_hours: int


class AdherenceMonitoringService:
    """
    Real-time adherence monitoring with proactive interventions.
    Continuously monitors user behavior and triggers interventions based on predictions.
    """

    def __init__(self, vertex_ai_client: Optional[VertexAIClient] = None):
        """Initialize the adherence monitoring service."""
        self.prediction_engine = AdherencePredictionEngine(vertex_ai_client)
        self.vertex_ai_client = vertex_ai_client or VertexAIClient()
        self.redis_client = get_redis_client()

        # Monitoring thresholds
        self.alert_thresholds = {
            AdherenceRiskLevel.VERY_HIGH: 0.1,  # Alert if probability drops below 10%
            AdherenceRiskLevel.HIGH: 0.2,  # Alert if probability drops below 20%
            AdherenceRiskLevel.MODERATE: 0.35,  # Alert if probability drops below 35%
        }

        # Intervention cooldowns (hours)
        self.intervention_cooldowns = {
            InterventionType.AUTOMATED_MESSAGE: 24,
            InterventionType.PUSH_NOTIFICATION: 12,
            InterventionType.AGENT_OUTREACH: 72,
            InterventionType.PROTOCOL_ADJUSTMENT: 168,  # 1 week
            InterventionType.GOAL_SIMPLIFICATION: 336,  # 2 weeks
        }

        logger.info("Adherence monitoring service initialized")

    @trace_async("adherence_monitoring")
    async def monitor_user_adherence(
        self,
        user_id: str,
        current_metrics: AdherenceMetrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Monitor user adherence and trigger interventions if needed.

        Args:
            user_id: User identifier
            current_metrics: Current adherence metrics
            context: Additional context

        Returns:
            Monitoring result with any interventions triggered
        """
        try:
            # Get historical data
            historical_data = await self._get_historical_data(user_id)

            # Generate prediction
            prediction = await self.prediction_engine.predict_adherence(
                user_id, current_metrics, historical_data, context
            )

            # Check for risk escalation
            risk_change = await self._check_risk_escalation(user_id, prediction)

            # Determine if intervention is needed
            intervention_needed = await self._assess_intervention_need(
                prediction, risk_change, context
            )

            interventions_triggered = []

            if intervention_needed:
                # Select and execute interventions
                interventions = await self._select_interventions(
                    prediction, current_metrics, context
                )

                for intervention in interventions:
                    result = await self._execute_intervention(
                        user_id, intervention, prediction
                    )
                    interventions_triggered.append(result)

            # Update monitoring state
            await self._update_monitoring_state(
                user_id, prediction, interventions_triggered
            )

            # Schedule next monitoring
            await self._schedule_next_monitoring(user_id, prediction.risk_level)

            return {
                "user_id": user_id,
                "prediction": prediction,
                "risk_change": risk_change,
                "intervention_needed": intervention_needed,
                "interventions_triggered": interventions_triggered,
                "next_monitoring": prediction.monitoring_frequency,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Adherence monitoring failed for user {user_id}: {e}")
            raise

    async def _get_historical_data(self, user_id: str) -> Dict[str, Any]:
        """Retrieve historical adherence data for user."""
        try:
            # Try to get from cache first
            cache_key = f"adherence_history:{user_id}"
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                return json.loads(cached_data)

            # If no cache, return empty dict (would typically fetch from database)
            return {}

        except Exception as e:
            logger.warning(f"Failed to retrieve historical data for {user_id}: {e}")
            return {}

    async def _check_risk_escalation(
        self, user_id: str, current_prediction: AdherencePrediction
    ) -> Dict[str, Any]:
        """Check if adherence risk has escalated since last prediction."""
        try:
            # Get previous prediction
            previous_prediction = await self.prediction_engine.get_cached_prediction(
                user_id
            )

            if not previous_prediction:
                return {
                    "escalated": False,
                    "risk_change": "unknown",
                    "probability_change": 0.0,
                }

            # Calculate changes
            probability_change = (
                current_prediction.adherence_probability
                - previous_prediction.adherence_probability
            )

            risk_levels = [level.value for level in AdherenceRiskLevel]
            previous_risk_index = risk_levels.index(
                previous_prediction.risk_level.value
            )
            current_risk_index = risk_levels.index(current_prediction.risk_level.value)

            risk_escalated = current_risk_index > previous_risk_index
            risk_improved = current_risk_index < previous_risk_index

            return {
                "escalated": risk_escalated,
                "improved": risk_improved,
                "risk_change": (
                    "escalated"
                    if risk_escalated
                    else "improved" if risk_improved else "stable"
                ),
                "probability_change": probability_change,
                "previous_risk": previous_prediction.risk_level.value,
                "current_risk": current_prediction.risk_level.value,
            }

        except Exception as e:
            logger.warning(f"Risk escalation check failed for {user_id}: {e}")
            return {
                "escalated": False,
                "risk_change": "unknown",
                "probability_change": 0.0,
            }

    async def _assess_intervention_need(
        self,
        prediction: AdherencePrediction,
        risk_change: Dict[str, Any],
        context: Optional[Dict[str, Any]],
    ) -> bool:
        """Assess whether intervention is needed based on prediction and risk change."""

        # Immediate intervention for very high risk
        if prediction.risk_level == AdherenceRiskLevel.VERY_HIGH:
            return True

        # Intervention if risk escalated
        if risk_change.get("escalated", False):
            return True

        # Intervention if probability dropped significantly
        if risk_change.get("probability_change", 0) < -0.15:
            return True

        # Intervention if critical triggers detected
        critical_triggers = [
            AdherenceTrigger.HEALTH_CONCERN,
            AdherenceTrigger.LIFE_EVENT,
            AdherenceTrigger.MOTIVATION_DROP,
        ]

        if any(
            trigger in critical_triggers for trigger in prediction.triggers_detected
        ):
            return True

        # Intervention if within critical window for high/moderate risk
        if prediction.risk_level in [
            AdherenceRiskLevel.HIGH,
            AdherenceRiskLevel.MODERATE,
        ]:
            if prediction.critical_intervention_window_days <= 3:
                return True

        # Intervention if user requested help (from context)
        if context and context.get("help_requested", False):
            return True

        return False

    async def _select_interventions(
        self,
        prediction: AdherencePrediction,
        metrics: AdherenceMetrics,
        context: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Select appropriate interventions based on prediction and context."""

        selected_interventions = []

        # Use AI to recommend interventions
        prompt = f"""
        Recommend adherence interventions for this user situation:
        
        Risk Level: {prediction.risk_level.value}
        Adherence Probability: {prediction.adherence_probability:.2f}
        Risk Factors: {prediction.primary_risk_factors}
        Triggers: [trigger.value for trigger in prediction.triggers_detected]
        Critical Window: {prediction.critical_intervention_window_days} days
        
        Current Metrics:
        - Daily engagement: {metrics.daily_app_usage_minutes} minutes
        - Weekly active days: {metrics.weekly_active_days}
        - Progress satisfaction: {metrics.progress_satisfaction_score}/10
        - Goal completion: {metrics.goal_completion_rate:.2f}
        
        Available intervention types:
        - automated_message: Personalized motivational message
        - push_notification: Gentle reminder or encouragement
        - agent_outreach: Personal contact from specialist agent
        - protocol_adjustment: Modify workout/nutrition protocol
        - goal_simplification: Reduce complexity and focus
        - social_support: Connect with community or partner
        - content_personalization: Adjust content to preferences
        - gamification_boost: Add challenges or rewards
        
        Select 1-3 most effective interventions for this situation.
        Return as JSON array with intervention_type and reasoning.
        """

        try:
            if self.vertex_ai_client:
                response = await self.vertex_ai_client.generate_content_async(prompt)
                ai_interventions = json.loads(response)

                # Validate and format interventions
                for intervention in ai_interventions:
                    if intervention.get("intervention_type") in [
                        t.value for t in InterventionType
                    ]:
                        selected_interventions.append(
                            {
                                "type": InterventionType(
                                    intervention["intervention_type"]
                                ),
                                "reasoning": intervention.get("reasoning", ""),
                                "priority": self._determine_intervention_priority(
                                    intervention["intervention_type"],
                                    prediction.risk_level,
                                ),
                            }
                        )

        except Exception as e:
            logger.warning(f"AI intervention selection failed: {e}")
            # Fallback to rule-based selection
            selected_interventions = self._fallback_intervention_selection(
                prediction, metrics
            )

        # Sort by priority and limit to top 3
        selected_interventions.sort(key=lambda x: x["priority"], reverse=True)
        return selected_interventions[:3]

    def _fallback_intervention_selection(
        self, prediction: AdherencePrediction, metrics: AdherenceMetrics
    ) -> List[Dict[str, Any]]:
        """Fallback rule-based intervention selection."""
        interventions = []

        # High risk = immediate outreach
        if prediction.risk_level in [
            AdherenceRiskLevel.HIGH,
            AdherenceRiskLevel.VERY_HIGH,
        ]:
            interventions.append(
                {
                    "type": InterventionType.AGENT_OUTREACH,
                    "reasoning": "High risk requires personal intervention",
                    "priority": 10,
                }
            )

        # Low engagement = push notifications
        if metrics.daily_app_usage_minutes < 15:
            interventions.append(
                {
                    "type": InterventionType.PUSH_NOTIFICATION,
                    "reasoning": "Low engagement needs gentle reminders",
                    "priority": 7,
                }
            )

        # Low satisfaction = goal simplification
        if metrics.progress_satisfaction_score < 6:
            interventions.append(
                {
                    "type": InterventionType.GOAL_SIMPLIFICATION,
                    "reasoning": "Low satisfaction indicates complexity overload",
                    "priority": 8,
                }
            )

        # Plateau trigger = protocol adjustment
        if AdherenceTrigger.PLATEAU in prediction.triggers_detected:
            interventions.append(
                {
                    "type": InterventionType.PROTOCOL_ADJUSTMENT,
                    "reasoning": "Plateau requires protocol refresh",
                    "priority": 9,
                }
            )

        return interventions

    def _determine_intervention_priority(
        self, intervention_type: str, risk_level: AdherenceRiskLevel
    ) -> int:
        """Determine intervention priority based on type and risk level."""
        base_priorities = {
            "agent_outreach": 9,
            "protocol_adjustment": 8,
            "goal_simplification": 7,
            "automated_message": 6,
            "social_support": 6,
            "content_personalization": 5,
            "push_notification": 4,
            "gamification_boost": 3,
        }

        priority = base_priorities.get(intervention_type, 5)

        # Boost priority for high risk
        if risk_level in [AdherenceRiskLevel.HIGH, AdherenceRiskLevel.VERY_HIGH]:
            priority += 2

        return min(10, priority)

    async def _execute_intervention(
        self,
        user_id: str,
        intervention: Dict[str, Any],
        prediction: AdherencePrediction,
    ) -> InterventionResult:
        """Execute a specific intervention."""

        intervention_type = intervention["type"]
        intervention_id = (
            f"{user_id}_{intervention_type.value}_{int(datetime.now().timestamp())}"
        )

        try:
            # Check cooldown
            if await self._is_on_cooldown(user_id, intervention_type):
                return InterventionResult(
                    intervention_id=intervention_id,
                    user_id=user_id,
                    intervention_type=intervention_type,
                    executed_at=datetime.now(),
                    success=False,
                    user_response="Skipped due to cooldown",
                    adherence_impact=None,
                    next_intervention_delay_hours=self.intervention_cooldowns[
                        intervention_type
                    ],
                )

            # Execute intervention based on type
            success = False
            user_response = None

            if intervention_type == InterventionType.AUTOMATED_MESSAGE:
                success, user_response = await self._send_automated_message(
                    user_id, intervention, prediction
                )
            elif intervention_type == InterventionType.PUSH_NOTIFICATION:
                success, user_response = await self._send_push_notification(
                    user_id, intervention, prediction
                )
            elif intervention_type == InterventionType.AGENT_OUTREACH:
                success, user_response = await self._trigger_agent_outreach(
                    user_id, intervention, prediction
                )
            elif intervention_type == InterventionType.PROTOCOL_ADJUSTMENT:
                success, user_response = await self._adjust_protocol(
                    user_id, intervention, prediction
                )
            elif intervention_type == InterventionType.GOAL_SIMPLIFICATION:
                success, user_response = await self._simplify_goals(
                    user_id, intervention, prediction
                )
            # Add other intervention types...

            # Record intervention
            await self._record_intervention(
                user_id, intervention_type, success, user_response
            )

            # Set cooldown
            await self._set_intervention_cooldown(user_id, intervention_type)

            return InterventionResult(
                intervention_id=intervention_id,
                user_id=user_id,
                intervention_type=intervention_type,
                executed_at=datetime.now(),
                success=success,
                user_response=user_response,
                adherence_impact=None,  # Will be calculated later
                next_intervention_delay_hours=self.intervention_cooldowns[
                    intervention_type
                ],
            )

        except Exception as e:
            logger.error(f"Intervention execution failed: {e}")
            return InterventionResult(
                intervention_id=intervention_id,
                user_id=user_id,
                intervention_type=intervention_type,
                executed_at=datetime.now(),
                success=False,
                user_response=f"Error: {str(e)}",
                adherence_impact=None,
                next_intervention_delay_hours=24,
            )

    async def _is_on_cooldown(
        self, user_id: str, intervention_type: InterventionType
    ) -> bool:
        """Check if intervention type is on cooldown for user."""
        try:
            cooldown_key = f"intervention_cooldown:{user_id}:{intervention_type.value}"
            cooldown_data = await self.redis_client.get(cooldown_key)
            return cooldown_data is not None
        except Exception as e:
            logger.warning(f"Cooldown check failed: {e}")
            return False

    async def _set_intervention_cooldown(
        self, user_id: str, intervention_type: InterventionType
    ) -> None:
        """Set cooldown for intervention type."""
        try:
            cooldown_key = f"intervention_cooldown:{user_id}:{intervention_type.value}"
            cooldown_hours = self.intervention_cooldowns[intervention_type]
            await self.redis_client.setex(
                cooldown_key, timedelta(hours=cooldown_hours).total_seconds(), "active"
            )
        except Exception as e:
            logger.warning(f"Setting cooldown failed: {e}")

    async def _send_automated_message(
        self,
        user_id: str,
        intervention: Dict[str, Any],
        prediction: AdherencePrediction,
    ) -> Tuple[bool, Optional[str]]:
        """Send personalized automated message."""

        # Generate personalized message using AI
        prompt = f"""
        Create a personalized motivational message for this user:
        
        Risk Level: {prediction.risk_level.value}
        Risk Factors: {prediction.primary_risk_factors}
        Protective Factors: {prediction.protective_factors}
        Intervention Reasoning: {intervention.get('reasoning', '')}
        
        Message should:
        - Be encouraging and supportive
        - Address specific risk factors
        - Highlight their strengths
        - Provide actionable next steps
        - Be 2-3 sentences maximum
        - Match their personality profile (if available)
        
        Return only the message text.
        """

        try:
            if self.vertex_ai_client:
                message = await self.vertex_ai_client.generate_content_async(prompt)

                # Send message (would integrate with messaging service)
                # For now, just log it
                logger.info(f"Sending automated message to {user_id}: {message}")

                # Simulate successful sending
                return True, "Message sent successfully"
        except Exception as e:
            logger.error(f"Automated message failed: {e}")
            return False, f"Failed to send message: {e}"

    async def _send_push_notification(
        self,
        user_id: str,
        intervention: Dict[str, Any],
        prediction: AdherencePrediction,
    ) -> Tuple[bool, Optional[str]]:
        """Send push notification."""

        # Generate notification based on risk factors
        notification_templates = {
            "low_engagement": "We miss you! Your progress is waiting for just 15 minutes today 💪",
            "plateau": "Time to shake things up! New challenges await in your program 🔥",
            "motivation_drop": "Remember why you started. Every small step counts! 🌟",
            "consistency": "Consistency is key! Let's keep that momentum going today 🚀",
        }

        # Select template based on primary risk factor
        primary_risk = (
            prediction.primary_risk_factors[0]
            if prediction.primary_risk_factors
            else ""
        )

        if "engagement" in primary_risk.lower():
            notification = notification_templates["low_engagement"]
        elif "plateau" in primary_risk.lower():
            notification = notification_templates["plateau"]
        elif "satisfaction" in primary_risk.lower():
            notification = notification_templates["motivation_drop"]
        else:
            notification = notification_templates["consistency"]

        try:
            # Send push notification (would integrate with FCM/APNs)
            logger.info(f"Sending push notification to {user_id}: {notification}")

            # Simulate successful sending
            return True, "Push notification sent"
        except Exception as e:
            logger.error(f"Push notification failed: {e}")
            return False, f"Failed to send notification: {e}"

    async def _trigger_agent_outreach(
        self,
        user_id: str,
        intervention: Dict[str, Any],
        prediction: AdherencePrediction,
    ) -> Tuple[bool, Optional[str]]:
        """Trigger personal outreach from appropriate agent."""

        try:
            # Determine which agent should reach out based on risk factors
            agent_assignment = await self._determine_outreach_agent(
                prediction.primary_risk_factors, prediction.triggers_detected
            )

            # Create outreach task
            outreach_data = {
                "user_id": user_id,
                "agent_id": agent_assignment["agent_id"],
                "priority": (
                    "high"
                    if prediction.risk_level == AdherenceRiskLevel.VERY_HIGH
                    else "medium"
                ),
                "context": {
                    "risk_level": prediction.risk_level.value,
                    "risk_factors": prediction.primary_risk_factors,
                    "triggers": [t.value for t in prediction.triggers_detected],
                    "intervention_reasoning": intervention.get("reasoning", ""),
                },
                "suggested_approach": agent_assignment["approach"],
                "timeline": (
                    "within_24_hours"
                    if prediction.risk_level == AdherenceRiskLevel.VERY_HIGH
                    else "within_48_hours"
                ),
            }

            # Send to agent outreach queue (would integrate with task queue)
            await send_adherence_alert.delay(outreach_data)

            logger.info(
                f"Agent outreach triggered for {user_id} via {agent_assignment['agent_id']}"
            )

            return True, f"Outreach scheduled with {agent_assignment['agent_id']}"

        except Exception as e:
            logger.error(f"Agent outreach failed: {e}")
            return False, f"Failed to schedule outreach: {e}"

    async def _determine_outreach_agent(
        self, risk_factors: List[str], triggers: List[AdherenceTrigger]
    ) -> Dict[str, Any]:
        """Determine which agent should handle outreach."""

        # Agent specialization mapping
        agent_specializations = {
            "motivation": {
                "agent_id": "spark_motivation_coach",
                "approach": "motivational_coaching",
            },
            "training": {
                "agent_id": "blaze_training_strategist",
                "approach": "program_adjustment",
            },
            "nutrition": {
                "agent_id": "sage_nutrition_architect",
                "approach": "nutrition_optimization",
            },
            "progress": {
                "agent_id": "stella_progress_tracker",
                "approach": "progress_celebration",
            },
            "support": {
                "agent_id": "aura_client_success",
                "approach": "supportive_guidance",
            },
            "general": {
                "agent_id": "nexus_orchestrator",
                "approach": "comprehensive_review",
            },
        }

        # Determine category based on risk factors and triggers
        if any(
            "motivation" in factor.lower() or "satisfaction" in factor.lower()
            for factor in risk_factors
        ):
            return agent_specializations["motivation"]
        elif any(
            "training" in factor.lower() or "exercise" in factor.lower()
            for factor in risk_factors
        ):
            return agent_specializations["training"]
        elif any(
            "nutrition" in factor.lower() or "meal" in factor.lower()
            for factor in risk_factors
        ):
            return agent_specializations["nutrition"]
        elif any(
            "progress" in factor.lower() or "plateau" in factor.lower()
            for factor in risk_factors
        ):
            return agent_specializations["progress"]
        elif any(
            "support" in factor.lower() or "social" in factor.lower()
            for factor in risk_factors
        ):
            return agent_specializations["support"]
        else:
            return agent_specializations["general"]

    async def _adjust_protocol(
        self,
        user_id: str,
        intervention: Dict[str, Any],
        prediction: AdherencePrediction,
    ) -> Tuple[bool, Optional[str]]:
        """Adjust user's protocol based on adherence issues."""

        try:
            # Create protocol adjustment recommendations
            adjustments = {
                "simplify_workouts": (
                    True
                    if "complexity" in str(prediction.primary_risk_factors)
                    else False
                ),
                "reduce_frequency": (
                    True if "time" in str(prediction.primary_risk_factors) else False
                ),
                "add_variety": (
                    True
                    if AdherenceTrigger.PLATEAU in prediction.triggers_detected
                    else False
                ),
                "focus_areas": self._identify_focus_areas(
                    prediction.primary_risk_factors
                ),
                "reasoning": intervention.get("reasoning", ""),
            }

            # Store adjustment request for agents to process
            adjustment_key = f"protocol_adjustment:{user_id}"
            await self.redis_client.setex(
                adjustment_key,
                timedelta(days=7).total_seconds(),
                json.dumps(adjustments, default=str),
            )

            logger.info(f"Protocol adjustment queued for {user_id}: {adjustments}")

            return True, "Protocol adjustment queued for review"

        except Exception as e:
            logger.error(f"Protocol adjustment failed: {e}")
            return False, f"Failed to adjust protocol: {e}"

    async def _simplify_goals(
        self,
        user_id: str,
        intervention: Dict[str, Any],
        prediction: AdherencePrediction,
    ) -> Tuple[bool, Optional[str]]:
        """Simplify user's goals to improve adherence."""

        try:
            # Create goal simplification recommendations
            simplifications = {
                "reduce_goal_count": True,
                "focus_on_habits": True,
                "lower_intensity": (
                    True
                    if "overwhelmed" in str(prediction.primary_risk_factors)
                    else False
                ),
                "extend_timeline": (
                    True
                    if "pressure" in str(prediction.primary_risk_factors)
                    else False
                ),
                "priority_goals": self._identify_priority_goals(
                    prediction.protective_factors
                ),
                "reasoning": intervention.get("reasoning", ""),
            }

            # Store simplification request
            simplification_key = f"goal_simplification:{user_id}"
            await self.redis_client.setex(
                simplification_key,
                timedelta(days=14).total_seconds(),
                json.dumps(simplifications, default=str),
            )

            logger.info(f"Goal simplification queued for {user_id}: {simplifications}")

            return True, "Goal simplification queued for review"

        except Exception as e:
            logger.error(f"Goal simplification failed: {e}")
            return False, f"Failed to simplify goals: {e}"

    def _identify_focus_areas(self, risk_factors: List[str]) -> List[str]:
        """Identify focus areas based on risk factors."""
        focus_areas = []

        for factor in risk_factors:
            if "engagement" in factor.lower():
                focus_areas.append("increase_engagement")
            elif "consistency" in factor.lower():
                focus_areas.append("build_habits")
            elif "progress" in factor.lower():
                focus_areas.append("quick_wins")
            elif "satisfaction" in factor.lower():
                focus_areas.append("enjoyment")
            elif "support" in factor.lower():
                focus_areas.append("community")

        return focus_areas[:3]  # Top 3 focus areas

    def _identify_priority_goals(self, protective_factors: List[str]) -> List[str]:
        """Identify priority goals based on protective factors."""
        priority_goals = []

        for factor in protective_factors:
            if "engagement" in factor.lower():
                priority_goals.append("maintain_routine")
            elif "consistency" in factor.lower():
                priority_goals.append("streak_building")
            elif "satisfaction" in factor.lower():
                priority_goals.append("progress_tracking")
            elif "achievement" in factor.lower():
                priority_goals.append("milestone_celebration")

        return priority_goals[:2]  # Top 2 priority goals

    async def _record_intervention(
        self,
        user_id: str,
        intervention_type: InterventionType,
        success: bool,
        response: Optional[str],
    ) -> None:
        """Record intervention for analytics and learning."""
        try:
            intervention_record = {
                "user_id": user_id,
                "intervention_type": intervention_type.value,
                "executed_at": datetime.now().isoformat(),
                "success": success,
                "response": response,
            }

            # Store in intervention history
            history_key = f"intervention_history:{user_id}"
            await self.redis_client.lpush(
                history_key, json.dumps(intervention_record, default=str)
            )

            # Keep only last 50 interventions
            await self.redis_client.ltrim(history_key, 0, 49)

        except Exception as e:
            logger.warning(f"Failed to record intervention: {e}")

    async def _update_monitoring_state(
        self,
        user_id: str,
        prediction: AdherencePrediction,
        interventions: List[InterventionResult],
    ) -> None:
        """Update monitoring state for user."""
        try:
            monitoring_state = {
                "user_id": user_id,
                "last_prediction": asdict(prediction),
                "last_monitored": datetime.now().isoformat(),
                "interventions_count": len(interventions),
                "risk_trend": await self._calculate_risk_trend(user_id),
                "next_monitoring_due": (
                    datetime.now()
                    + self._get_monitoring_interval(prediction.monitoring_frequency)
                ).isoformat(),
            }

            # Store monitoring state
            state_key = f"monitoring_state:{user_id}"
            await self.redis_client.setex(
                state_key,
                timedelta(days=30).total_seconds(),
                json.dumps(monitoring_state, default=str),
            )

        except Exception as e:
            logger.warning(f"Failed to update monitoring state: {e}")

    def _get_monitoring_interval(self, frequency: str) -> timedelta:
        """Convert monitoring frequency to timedelta."""
        intervals = {
            "daily": timedelta(days=1),
            "every_2_days": timedelta(days=2),
            "weekly": timedelta(weeks=1),
            "bi_weekly": timedelta(weeks=2),
            "monthly": timedelta(days=30),
        }
        return intervals.get(frequency, timedelta(days=7))

    async def _calculate_risk_trend(self, user_id: str) -> str:
        """Calculate risk trend over time."""
        try:
            # Get recent predictions from cache
            # This would typically analyze a series of predictions
            # For now, return "stable" as placeholder
            return "stable"
        except Exception as e:
            logger.warning(f"Risk trend calculation failed: {e}")
            return "unknown"

    async def _schedule_next_monitoring(
        self, user_id: str, risk_level: AdherenceRiskLevel
    ) -> None:
        """Schedule next monitoring check."""
        try:
            # Calculate next monitoring time based on risk level
            next_check = datetime.now() + self._get_monitoring_interval(
                self._determine_monitoring_frequency(risk_level)
            )

            # Schedule monitoring task (would integrate with task scheduler)
            monitoring_task = {
                "user_id": user_id,
                "scheduled_for": next_check.isoformat(),
                "risk_level": risk_level.value,
            }

            # Store scheduled task
            schedule_key = f"scheduled_monitoring:{next_check.strftime('%Y%m%d')}"
            await self.redis_client.lpush(
                schedule_key, json.dumps(monitoring_task, default=str)
            )

            logger.debug(f"Next monitoring scheduled for {user_id} at {next_check}")

        except Exception as e:
            logger.warning(f"Failed to schedule next monitoring: {e}")

    def _determine_monitoring_frequency(self, risk_level: AdherenceRiskLevel) -> str:
        """Determine monitoring frequency based on risk level."""
        frequencies = {
            AdherenceRiskLevel.VERY_HIGH: "daily",
            AdherenceRiskLevel.HIGH: "every_2_days",
            AdherenceRiskLevel.MODERATE: "weekly",
            AdherenceRiskLevel.LOW: "bi_weekly",
            AdherenceRiskLevel.VERY_LOW: "monthly",
        }
        return frequencies[risk_level]
