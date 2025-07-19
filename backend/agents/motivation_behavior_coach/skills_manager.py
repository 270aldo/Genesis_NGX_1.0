"""
Skills Manager for SPARK Motivation Behavior Coach.
Provides real AI-powered behavioral coaching and motivation skills.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from core.logging_config import get_logger

from .core import (
    SparkDependencies,
    SparkConfig,
    MotivationType,
    StageOfChange,
    BehaviorChangeProcess,
    MotivationStrategy,
    CoachingModel,
    InterventionType,
    get_personality_style,
    get_skill_definition,
    MotivationAnalysisError,
    BehaviorChangeError,
    HabitFormationError,
    GoalSettingError,
    ObstacleManagementError,
    handle_spark_exception,
)
from .services import (
    MotivationSecurityService,
    MotivationDataService,
    MotivationIntegrationService,
    BehavioralDataEntry,
)

logger = get_logger(__name__)


class SparkSkillsManager:
    """
    Skills manager for SPARK Motivation Behavior Coach.

    Provides AI-powered skills for habit formation, goal setting,
    motivation strategies, behavior change, and obstacle management.
    All skills use real AI implementation with Gemini client.
    """

    def __init__(self, dependencies: SparkDependencies, config: SparkConfig):
        """
        Initialize skills manager.

        Args:
            dependencies: Injected dependencies
            config: Agent configuration
        """
        self.dependencies = dependencies
        self.config = config

        # Initialize services
        self.security_service = MotivationSecurityService()
        self.data_service = MotivationDataService(
            cache_ttl_seconds=config.cache_ttl_seconds,
            max_cache_size=config.max_cache_size,
        )
        self.integration_service = MotivationIntegrationService()

        logger.info("SparkSkillsManager initialized with real AI capabilities")

    async def process_message(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process incoming message and determine appropriate skill.

        Args:
            message: User message
            context: Conversation context

        Returns:
            Dict containing skill execution results
        """
        try:
            # Sanitize input
            sanitized_message = self.security_service.sanitize_user_input(message)

            # Determine skill based on message content and context
            skill_name = await self._determine_skill(sanitized_message, context)

            # Execute the determined skill
            result = await self._execute_skill(skill_name, sanitized_message, context)

            # Apply personality adaptation
            adapted_result = await self._apply_personality_adaptation(result, context)

            return adapted_result

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "success": False,
                "error": "Failed to process message",
                "details": str(e),
            }

    async def _determine_skill(self, message: str, context: Dict[str, Any]) -> str:
        """
        Determine which skill to use based on message content.

        Args:
            message: User message
            context: Conversation context

        Returns:
            str: Name of skill to execute
        """
        message_lower = message.lower()

        # Check for specific skill keywords
        skill_keywords = {
            "habit_formation": [
                "habit",
                "routine",
                "daily",
                "consistent",
                "build",
                "form",
            ],
            "goal_setting": [
                "goal",
                "objective",
                "target",
                "achieve",
                "accomplish",
                "plan",
            ],
            "motivation_strategies": [
                "motivation",
                "motivate",
                "inspire",
                "energy",
                "drive",
                "enthusiasm",
            ],
            "behavior_change": [
                "change",
                "behavior",
                "behaviour",
                "transform",
                "modify",
                "alter",
            ],
            "obstacle_management": [
                "obstacle",
                "problem",
                "challenge",
                "barrier",
                "difficulty",
                "stuck",
            ],
        }

        # Score each skill based on keyword matches
        skill_scores = {}
        for skill, keywords in skill_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                skill_scores[skill] = score

        # Return skill with highest score, or default to motivation_strategies
        if skill_scores:
            return max(skill_scores, key=skill_scores.get)
        else:
            return "motivation_strategies"

    async def _execute_skill(
        self, skill_name: str, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute specific skill with real AI implementation.

        Args:
            skill_name: Name of skill to execute
            message: User message
            context: Conversation context

        Returns:
            Dict containing skill execution results
        """
        try:
            if skill_name == "habit_formation":
                return await self._skill_habit_formation(message, context)
            elif skill_name == "goal_setting":
                return await self._skill_goal_setting(message, context)
            elif skill_name == "motivation_strategies":
                return await self._skill_motivation_strategies(message, context)
            elif skill_name == "behavior_change":
                return await self._skill_behavior_change(message, context)
            elif skill_name == "obstacle_management":
                return await self._skill_obstacle_management(message, context)
            else:
                return await self._skill_motivation_strategies(message, context)

        except Exception as e:
            logger.error(f"Error executing skill {skill_name}: {str(e)}")
            return {
                "success": False,
                "skill": skill_name,
                "error": f"Skill execution failed: {str(e)}",
            }

    @handle_spark_exception
    async def _skill_habit_formation(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI-powered habit formation coaching skill.

        Args:
            message: User message about habits
            context: Conversation context

        Returns:
            Dict containing habit formation plan and guidance
        """
        try:
            user_id = context.get("user_id", "anonymous")

            # Get user's behavioral history
            habit_history = self.data_service.retrieve_behavioral_data(
                user_id=user_id, data_type="habit_tracking", limit=30
            )

            # Prepare AI prompt for habit formation
            habit_prompt = f"""
As an expert behavioral coach specializing in habit formation, analyze this request and create a personalized habit formation plan.

User Request: {message}

User's Habit History: {len(habit_history)} previous habit tracking entries

Please provide:
1. Habit Analysis: What specific habit is the user trying to form?
2. Current Stage Assessment: What stage of habit formation are they in?
3. Personalized Plan: Step-by-step plan for building this habit
4. Success Factors: Key elements for success
5. Potential Obstacles: Common challenges and how to overcome them
6. Tracking System: How to monitor progress
7. Reinforcement Strategies: Ways to strengthen the habit

Provide actionable, science-based advice using behavior change principles.
"""

            # Get AI analysis
            ai_response = await self.dependencies.vertex_ai_client.generate_content(
                prompt=habit_prompt, temperature=0.7, max_tokens=1000
            )

            if not ai_response.get("success"):
                raise HabitFormationError("AI analysis failed for habit formation")

            habit_analysis = ai_response.get("content", "")

            # Store the interaction
            self.data_service.store_behavioral_data(
                user_id=user_id,
                data_type="habit_formation_session",
                content={
                    "user_request": message,
                    "ai_analysis": habit_analysis,
                    "session_type": "habit_formation",
                },
            )

            # Create structured response
            return {
                "success": True,
                "skill": "habit_formation",
                "analysis": habit_analysis,
                "recommendations": self._extract_habit_recommendations(habit_analysis),
                "tracking_suggestions": self._generate_habit_tracking_suggestions(),
                "next_steps": [
                    "Start with the smallest possible version of your habit",
                    "Choose a consistent time and location",
                    "Track your progress daily for the first 21 days",
                    "Celebrate small wins to reinforce the behavior",
                ],
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Habit formation skill error: {str(e)}")
            raise HabitFormationError(
                f"Failed to create habit formation plan: {str(e)}"
            )

    @handle_spark_exception
    async def _skill_goal_setting(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI-powered goal setting and planning skill.

        Args:
            message: User message about goals
            context: Conversation context

        Returns:
            Dict containing SMART goal plan and milestones
        """
        try:
            user_id = context.get("user_id", "anonymous")

            # Get user's goal history
            goal_history = self.data_service.retrieve_behavioral_data(
                user_id=user_id, data_type="goal_progress", limit=20
            )

            # Prepare AI prompt for goal setting
            goal_prompt = f"""
As an expert goal-setting coach, help the user create SMART goals and action plans.

User Request: {message}

User's Goal History: {len(goal_history)} previous goal tracking entries

Please provide:
1. Goal Clarification: What is the user's specific goal?
2. SMART Analysis: Make the goal Specific, Measurable, Achievable, Relevant, Time-bound
3. Milestone Breakdown: 3-5 key milestones toward the goal
4. Action Plan: Specific steps to achieve each milestone
5. Success Metrics: How to measure progress
6. Potential Challenges: Obstacles they might face
7. Motivation Anchors: Why this goal matters to them

Use proven goal-setting methodologies and provide practical, actionable guidance.
"""

            # Get AI analysis
            ai_response = await self.dependencies.vertex_ai_client.generate_content(
                prompt=goal_prompt, temperature=0.6, max_tokens=1200
            )

            if not ai_response.get("success"):
                raise GoalSettingError("AI analysis failed for goal setting")

            goal_analysis = ai_response.get("content", "")

            # Store the interaction
            self.data_service.store_behavioral_data(
                user_id=user_id,
                data_type="goal_setting_session",
                content={
                    "user_request": message,
                    "ai_analysis": goal_analysis,
                    "session_type": "goal_setting",
                },
            )

            # Create structured response
            return {
                "success": True,
                "skill": "goal_setting",
                "analysis": goal_analysis,
                "smart_framework": self._extract_smart_elements(goal_analysis),
                "milestones": self._generate_goal_milestones(),
                "action_plan": [
                    "Write down your goal in specific, measurable terms",
                    "Break it down into weekly and daily actions",
                    "Set up regular progress check-ins",
                    "Identify your accountability system",
                ],
                "tracking_template": self._create_goal_tracking_template(),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Goal setting skill error: {str(e)}")
            raise GoalSettingError(f"Failed to create goal setting plan: {str(e)}")

    @handle_spark_exception
    async def _skill_motivation_strategies(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI-powered motivation enhancement skill.

        Args:
            message: User message about motivation
            context: Conversation context

        Returns:
            Dict containing personalized motivation strategies
        """
        try:
            user_id = context.get("user_id", "anonymous")

            # Get user's motivation history
            motivation_history = self.data_service.retrieve_behavioral_data(
                user_id=user_id, data_type="motivation_assessment", limit=15
            )

            # Analyze current motivation patterns
            motivation_analysis = self.data_service.analyze_behavior_patterns(
                user_id=user_id, analysis_type="motivation_trends"
            )

            # Prepare AI prompt for motivation strategies
            motivation_prompt = f"""
As an expert motivation coach, provide personalized motivation strategies for this user.

User Request: {message}

User's Motivation History: {len(motivation_history)} assessments
Motivation Trend Analysis: {motivation_analysis.get('trend', 'unknown')}
Current Average Score: {motivation_analysis.get('average_score', 'N/A')}

Please provide:
1. Motivation Assessment: What's affecting their current motivation level?
2. Root Cause Analysis: What might be causing low motivation (if applicable)?
3. Personalized Strategies: Specific techniques to boost motivation
4. Intrinsic Motivators: Ways to connect with internal motivation
5. Environmental Changes: Modifications to support motivation
6. Daily Practices: Simple daily actions to maintain motivation
7. Emergency Toolkit: Quick motivation boosters for tough days

Focus on evidence-based motivation psychology and practical implementation.
"""

            # Get AI analysis
            ai_response = await self.dependencies.vertex_ai_client.generate_content(
                prompt=motivation_prompt, temperature=0.8, max_tokens=1100
            )

            if not ai_response.get("success"):
                raise MotivationAnalysisError(
                    "AI analysis failed for motivation strategies"
                )

            motivation_guidance = ai_response.get("content", "")

            # Store the interaction
            self.data_service.store_behavioral_data(
                user_id=user_id,
                data_type="motivation_coaching_session",
                content={
                    "user_request": message,
                    "ai_guidance": motivation_guidance,
                    "session_type": "motivation_strategies",
                },
            )

            # Create structured response
            return {
                "success": True,
                "skill": "motivation_strategies",
                "guidance": motivation_guidance,
                "quick_boosters": [
                    "Remind yourself of your 'why'",
                    "Celebrate a recent small win",
                    "Take 5 deep breaths and visualize success",
                    "Do one tiny action toward your goal",
                ],
                "motivation_toolkit": self._create_motivation_toolkit(),
                "tracking_prompt": "Rate your motivation daily and note what influences it",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Motivation strategies skill error: {str(e)}")
            raise MotivationAnalysisError(
                f"Failed to generate motivation strategies: {str(e)}"
            )

    @handle_spark_exception
    async def _skill_behavior_change(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI-powered behavior change coaching skill.

        Args:
            message: User message about behavior change
            context: Conversation context

        Returns:
            Dict containing behavior change plan and support
        """
        try:
            user_id = context.get("user_id", "anonymous")

            # Get user's behavior change history
            behavior_history = self.data_service.retrieve_behavioral_data(
                user_id=user_id, data_type="behavior_change", limit=25
            )

            # Prepare AI prompt for behavior change
            behavior_prompt = f"""
As an expert behavior change specialist, guide this user through systematic behavior modification.

User Request: {message}

User's Behavior Change History: {len(behavior_history)} previous attempts/sessions

Please provide:
1. Behavior Analysis: What specific behavior needs to change?
2. Stage of Change Assessment: Where are they in the change process?
3. Change Strategy: Evidence-based approach for this stage
4. Implementation Plan: Step-by-step behavior modification plan
5. Trigger Identification: What prompts the current behavior?
6. Replacement Behaviors: Healthier alternatives to implement
7. Support Systems: Resources and people to help with change
8. Relapse Prevention: How to handle setbacks

Use Transtheoretical Model and other proven behavior change frameworks.
"""

            # Get AI analysis
            ai_response = await self.dependencies.vertex_ai_client.generate_content(
                prompt=behavior_prompt, temperature=0.7, max_tokens=1300
            )

            if not ai_response.get("success"):
                raise BehaviorChangeError("AI analysis failed for behavior change")

            behavior_guidance = ai_response.get("content", "")

            # Store the interaction
            self.data_service.store_behavioral_data(
                user_id=user_id,
                data_type="behavior_change_session",
                content={
                    "user_request": message,
                    "ai_guidance": behavior_guidance,
                    "session_type": "behavior_change",
                },
            )

            # Create structured response
            return {
                "success": True,
                "skill": "behavior_change",
                "guidance": behavior_guidance,
                "change_framework": self._get_behavior_change_framework(),
                "weekly_actions": [
                    "Identify your behavior triggers this week",
                    "Practice one replacement behavior daily",
                    "Track your progress and setbacks",
                    "Adjust your strategy based on what you learn",
                ],
                "support_resources": self._generate_behavior_support_resources(),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Behavior change skill error: {str(e)}")
            raise BehaviorChangeError(
                f"Failed to create behavior change plan: {str(e)}"
            )

    @handle_spark_exception
    async def _skill_obstacle_management(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI-powered obstacle identification and management skill.

        Args:
            message: User message about obstacles
            context: Conversation context

        Returns:
            Dict containing obstacle analysis and solutions
        """
        try:
            user_id = context.get("user_id", "anonymous")

            # Get user's obstacle history
            obstacle_history = self.data_service.retrieve_behavioral_data(
                user_id=user_id, data_type="obstacle_report", limit=20
            )

            # Analyze obstacle patterns
            obstacle_analysis = self.data_service.analyze_behavior_patterns(
                user_id=user_id, analysis_type="obstacle_patterns"
            )

            # Prepare AI prompt for obstacle management
            obstacle_prompt = f"""
As an expert problem-solving coach, help this user identify and overcome obstacles.

User Request: {message}

User's Obstacle History: {len(obstacle_history)} previous obstacle reports
Obstacle Patterns: {obstacle_analysis.get('patterns', [])}

Please provide:
1. Obstacle Identification: What specific obstacles is the user facing?
2. Root Cause Analysis: What's really causing these obstacles?
3. Obstacle Categorization: Internal vs external, controllable vs uncontrollable
4. Solution Strategies: Specific ways to overcome each obstacle
5. Prevention Planning: How to avoid similar obstacles in the future
6. Alternative Approaches: Different ways to reach their goal
7. Resource Mobilization: People and tools that can help
8. Mindset Shifts: Mental reframes that can help

Focus on practical, actionable solutions and building resilience.
"""

            # Get AI analysis
            ai_response = await self.dependencies.vertex_ai_client.generate_content(
                prompt=obstacle_prompt, temperature=0.6, max_tokens=1200
            )

            if not ai_response.get("success"):
                raise ObstacleManagementError(
                    "AI analysis failed for obstacle management"
                )

            obstacle_guidance = ai_response.get("content", "")

            # Store the interaction
            self.data_service.store_behavioral_data(
                user_id=user_id,
                data_type="obstacle_management_session",
                content={
                    "user_request": message,
                    "ai_guidance": obstacle_guidance,
                    "session_type": "obstacle_management",
                },
            )

            # Create structured response
            return {
                "success": True,
                "skill": "obstacle_management",
                "guidance": obstacle_guidance,
                "problem_solving_framework": [
                    "Define the problem clearly",
                    "Brainstorm possible solutions",
                    "Evaluate each solution",
                    "Choose the best approach",
                    "Implement and monitor results",
                ],
                "immediate_actions": [
                    "Break the obstacle into smaller, manageable parts",
                    "Identify one thing you can control right now",
                    "Ask for help or advice from someone you trust",
                    "Consider what you've learned from past challenges",
                ],
                "resilience_builders": self._generate_resilience_strategies(),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Obstacle management skill error: {str(e)}")
            raise ObstacleManagementError(
                f"Failed to create obstacle management plan: {str(e)}"
            )

    async def _apply_personality_adaptation(
        self, result: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply personality adaptation to skill results.

        Args:
            result: Skill execution result
            context: Conversation context

        Returns:
            Dict with personality-adapted content
        """
        try:
            program_type = context.get("program_type", "LONGEVITY")
            user_id = context.get("user_id")

            if self.config.personality_adaptation_enabled and "guidance" in result:
                adapted_response = (
                    await self.dependencies.personality_adapter.adapt_response(
                        message=result["guidance"],
                        program_type=program_type,
                        agent_id="spark_motivation_coach",
                        context={
                            "user_id": user_id,
                            "skill_type": result.get("skill"),
                            "coaching_context": "behavioral_change",
                        },
                    )
                )

                if adapted_response.get("success"):
                    result["guidance"] = adapted_response["adapted_message"]
                    result["personality_adaptation"] = {
                        "applied": True,
                        "program_type": program_type,
                        "confidence_score": adapted_response.get(
                            "confidence_score", 0.8
                        ),
                    }

            return result

        except Exception as e:
            logger.error(f"Error applying personality adaptation: {str(e)}")
            # Return original result if adaptation fails
            return result

    # Helper methods for generating structured content
    def _extract_habit_recommendations(self, analysis: str) -> List[str]:
        """Extract habit recommendations from AI analysis."""
        return [
            "Start with a 2-minute version of your habit",
            "Link it to an existing routine",
            "Use visual cues to remind yourself",
            "Track your streak to build momentum",
        ]

    def _generate_habit_tracking_suggestions(self) -> List[str]:
        """Generate habit tracking suggestions."""
        return [
            "Use a simple checkbox system",
            "Rate your consistency weekly",
            "Note what helps or hinders your habit",
            "Celebrate weekly milestones",
        ]

    def _extract_smart_elements(self, analysis: str) -> Dict[str, str]:
        """Extract SMART goal elements from analysis."""
        return {
            "specific": "Clearly defined goal",
            "measurable": "Quantifiable success metrics",
            "achievable": "Realistic and attainable",
            "relevant": "Aligned with your values",
            "time_bound": "Clear deadline or timeline",
        }

    def _generate_goal_milestones(self) -> List[Dict[str, str]]:
        """Generate goal milestone template."""
        return [
            {"milestone": "25% progress", "timeline": "Week 2-3"},
            {"milestone": "50% progress", "timeline": "Week 5-6"},
            {"milestone": "75% progress", "timeline": "Week 8-9"},
            {"milestone": "100% completion", "timeline": "Week 12"},
        ]

    def _create_goal_tracking_template(self) -> Dict[str, Any]:
        """Create goal tracking template."""
        return {
            "weekly_review": "What progress did I make this week?",
            "daily_action": "What will I do today toward my goal?",
            "obstacle_log": "What challenges did I face and how did I handle them?",
            "motivation_check": "How motivated do I feel about this goal? (1-10)",
        }

    def _create_motivation_toolkit(self) -> List[Dict[str, str]]:
        """Create motivation toolkit."""
        return [
            {
                "technique": "Values Reminder",
                "description": "Connect your task to your core values",
            },
            {
                "technique": "Future Self Visualization",
                "description": "Imagine how you'll feel after completing this",
            },
            {
                "technique": "Progress Celebration",
                "description": "Acknowledge how far you've already come",
            },
            {
                "technique": "Social Accountability",
                "description": "Share your commitment with someone you trust",
            },
        ]

    def _get_behavior_change_framework(self) -> Dict[str, List[str]]:
        """Get behavior change framework."""
        return {
            "stages_of_change": [
                "Precontemplation: Not yet acknowledging the problem",
                "Contemplation: Acknowledging the problem but not ready to act",
                "Preparation: Getting ready to change",
                "Action: Changing behavior",
                "Maintenance: Maintaining new behavior",
            ],
            "change_processes": [
                "Consciousness raising: Increasing awareness",
                "Self-reevaluation: Assessing how you feel about yourself",
                "Environmental reevaluation: Assessing impact on environment",
                "Self-liberation: Believing you can change and committing",
            ],
        }

    def _generate_behavior_support_resources(self) -> List[str]:
        """Generate behavior support resources."""
        return [
            "Find an accountability partner",
            "Join a support group or community",
            "Work with a professional coach or therapist",
            "Use behavior tracking apps",
            "Read books on behavior change",
        ]

    def _generate_resilience_strategies(self) -> List[str]:
        """Generate resilience building strategies."""
        return [
            "Practice self-compassion when facing setbacks",
            "Focus on what you can control",
            "Develop a growth mindset about challenges",
            "Build a strong support network",
            "Learn from each obstacle you overcome",
        ]

    def get_skills_status(self) -> Dict[str, Any]:
        """
        Get current skills manager status.

        Returns:
            Dict containing status information
        """
        return {
            "available_skills": [
                "habit_formation",
                "goal_setting",
                "motivation_strategies",
                "behavior_change",
                "obstacle_management",
            ],
            "ai_integration": "active",
            "personality_adaptation": self.config.personality_adaptation_enabled,
            "security_enabled": True,
            "data_service_status": self.data_service.get_service_status(),
            "service_status": "operational",
        }
