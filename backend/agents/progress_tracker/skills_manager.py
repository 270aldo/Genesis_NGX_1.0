"""
STELLA Progress Tracker Skills Manager.
Real AI-powered progress tracking skills with STELLA personality integration.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import re

from .core import (
    StellaDependencies,
    StellaConfig,
    ProgressMetricType,
    AchievementCategory,
    VisualizationType,
    AnalysisType,
    MilestoneType,
    PersonalityStyle,
    get_stella_personality_style,
    format_stella_response,
    STELLA_PERSONALITY_TRAITS,
    StellaBaseError,
    ProgressAnalysisError,
    VisualizationError,
    MilestoneTrackingError,
    handle_stella_exception,
)
from .services import (
    ProgressSecurityService,
    ProgressDataService,
    ProgressIntegrationService,
)


class StellaSkillsManager:
    """
    STELLA Progress Tracker Skills Manager with real AI implementation.
    Manages all progress tracking skills with enthusiastic STELLA personality.
    """

    def __init__(self, dependencies: StellaDependencies, config: StellaConfig):
        """
        Initialize STELLA skills manager.

        Args:
            dependencies: Injected dependencies
            config: STELLA configuration
        """
        self.dependencies = dependencies
        self.config = config

        # Initialize services
        self.security_service = ProgressSecurityService()
        self.data_service = ProgressDataService(
            cache_ttl_seconds=config.cache_ttl_seconds,
            max_cache_size=config.max_cache_size,
        )
        self.integration_service = ProgressIntegrationService()

        # Skills registry
        self.skills = {
            # Core progress tracking skills
            "analyze_progress": self._skill_analyze_progress,
            "visualize_progress": self._skill_visualize_progress,
            "compare_progress": self._skill_compare_progress,
            "analyze_body_progress": self._skill_analyze_body_progress,
            "generate_progress_visualization": self._skill_generate_progress_visualization,
            # STELLA conversation skills
            "progress_celebration": self._skill_progress_celebration_conversation,
            "milestone_analysis": self._skill_milestone_analysis_conversation,
            "goal_adjustment": self._skill_goal_adjustment_conversation,
            "motivational_checkin": self._skill_motivational_checkin_conversation,
            "achievement_reflection": self._skill_achievement_reflection_conversation,
        }

        # Performance tracking
        self.skill_usage_stats = {}
        self.skill_performance_metrics = {}

    @handle_stella_exception
    async def process_message(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process user message and route to appropriate skill.

        Args:
            message: User message
            context: Conversation context

        Returns:
            Skill execution result with STELLA personality
        """
        # Sanitize input
        clean_message = self.security_service.sanitize_user_input(message)

        # Determine appropriate skill
        skill_name = await self._determine_skill(clean_message, context)

        # Execute skill
        skill_result = await self._execute_skill(skill_name, clean_message, context)

        # Apply STELLA personality adaptation
        enhanced_result = await self._apply_stella_personality(skill_result, context)

        # Store interaction data
        await self._store_interaction_data(clean_message, enhanced_result, context)

        return enhanced_result

    async def _determine_skill(self, message: str, context: Dict[str, Any]) -> str:
        """
        Determine which skill to use based on message content.

        Args:
            message: User message
            context: Context information

        Returns:
            Skill name to execute
        """
        message_lower = message.lower()

        # Progress analysis keywords
        if any(
            keyword in message_lower
            for keyword in [
                "analyze",
                "analysis",
                "progress",
                "trend",
                "improvement",
                "results",
            ]
        ):
            return "analyze_progress"

        # Visualization keywords
        if any(
            keyword in message_lower
            for keyword in ["chart", "graph", "visualize", "show", "display", "plot"]
        ):
            return "visualize_progress"

        # Comparison keywords
        if any(
            keyword in message_lower
            for keyword in [
                "compare",
                "comparison",
                "vs",
                "versus",
                "before",
                "after",
                "difference",
            ]
        ):
            return "compare_progress"

        # Body analysis keywords
        if any(
            keyword in message_lower
            for keyword in [
                "body",
                "physique",
                "measurements",
                "photos",
                "pictures",
                "image",
            ]
        ):
            return "analyze_body_progress"

        # Celebration keywords
        if any(
            keyword in message_lower
            for keyword in [
                "celebrate",
                "achievement",
                "milestone",
                "success",
                "accomplished",
            ]
        ):
            return "progress_celebration"

        # Goal adjustment keywords
        if any(
            keyword in message_lower
            for keyword in ["goal", "target", "adjust", "change", "modify", "update"]
        ):
            return "goal_adjustment"

        # Motivational check-in keywords
        if any(
            keyword in message_lower
            for keyword in [
                "motivation",
                "motivated",
                "encourage",
                "support",
                "help",
                "struggling",
            ]
        ):
            return "motivational_checkin"

        # Default to general progress analysis
        return "analyze_progress"

    async def _execute_skill(
        self, skill_name: str, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the specified skill.

        Args:
            skill_name: Name of skill to execute
            message: User message
            context: Context information

        Returns:
            Skill execution result
        """
        if skill_name not in self.skills:
            raise StellaBaseError(f"Unknown skill: {skill_name}")

        # Track skill usage
        self.skill_usage_stats[skill_name] = (
            self.skill_usage_stats.get(skill_name, 0) + 1
        )

        # Execute skill
        start_time = datetime.utcnow()
        try:
            result = await self.skills[skill_name](message, context)

            # Track performance
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_skill_performance(skill_name, execution_time, True)

            return result

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_skill_performance(skill_name, execution_time, False)
            raise

    @handle_stella_exception
    async def _skill_analyze_progress(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze user progress with real AI insights.

        Args:
            message: User message requesting analysis
            context: User context and preferences

        Returns:
            Progress analysis with STELLA enthusiasm
        """
        user_id = context.get("user_id", "unknown")

        # Get progress data
        progress_data = self.data_service.retrieve_progress_data(
            user_id=user_id,
            start_date=datetime.utcnow() - timedelta(days=90),
            limit=100,
        )

        if not progress_data:
            return {
                "success": True,
                "skill": "analyze_progress",
                "guidance": "I'd love to analyze your progress, but I don't see any data yet! Let's start tracking your amazing journey together! 🌟",
                "recommendations": [
                    "Start logging your workouts and measurements",
                    "Take progress photos to track visual changes",
                    "Set some exciting goals we can work toward together!",
                ],
                "next_steps": ["Begin your progress tracking journey today!"],
            }

        # Prepare AI analysis prompt
        analysis_prompt = f"""
        As STELLA, an enthusiastic ESFJ progress tracker, analyze this fitness journey with excitement and detailed insights.
        
        User Request: {message}
        
        Progress Data Summary:
        - Total entries: {len(progress_data)}
        - Date range: {progress_data[-1].timestamp.strftime('%Y-%m-%d')} to {progress_data[0].timestamp.strftime('%Y-%m-%d')}
        - Data types: {list(set(entry.data_type for entry in progress_data))}
        
        Provide enthusiastic analysis covering:
        1. Overall Progress Assessment
        2. Key Trends and Patterns  
        3. Standout Achievements
        4. Areas of Improvement
        5. Personalized Recommendations
        6. Celebration of Wins
        
        Be encouraging, detailed, and celebrate every victory - big or small!
        """

        # Get AI analysis
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            analysis_prompt
        )

        if not ai_response.get("success"):
            raise ProgressAnalysisError("Failed to generate AI analysis")

        ai_content = ai_response.get("content", "")

        # Perform quantitative analysis
        quantitative_analysis = self.data_service.analyze_progress_patterns(
            user_id, "overall_progress"
        )

        return {
            "success": True,
            "skill": "analyze_progress",
            "analysis": ai_content,
            "quantitative_metrics": quantitative_analysis,
            "data_summary": {
                "total_entries": len(progress_data),
                "tracking_consistency": self._calculate_tracking_consistency(
                    progress_data
                ),
                "active_metrics": list(set(entry.data_type for entry in progress_data)),
            },
            "recommendations": self._extract_recommendations_from_ai(ai_content),
            "achievements_detected": self._detect_achievements(progress_data),
            "next_steps": [
                "Continue your amazing tracking consistency!",
                "Focus on the improvement areas we identified",
                "Celebrate your progress wins!",
            ],
        }

    @handle_stella_exception
    async def _skill_visualize_progress(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create progress visualizations with STELLA excitement.

        Args:
            message: Visualization request
            context: User context

        Returns:
            Visualization results with STELLA enthusiasm
        """
        user_id = context.get("user_id", "unknown")

        # Determine visualization type from message
        viz_type = self._determine_visualization_type(message)

        # Get relevant data
        progress_data = self.data_service.retrieve_progress_data(
            user_id=user_id, start_date=datetime.utcnow() - timedelta(days=60), limit=50
        )

        if not progress_data:
            return {
                "success": True,
                "skill": "visualize_progress",
                "guidance": "I'm so excited to create amazing charts for you! But first, let's get some data to visualize! 📊✨",
                "suggestions": [
                    "Log a few workouts to see strength progressions",
                    "Track your weight to see trends over time",
                    "Record measurements for body composition changes",
                ],
                "visualization_ready": False,
            }

        # Create AI-enhanced visualization prompt
        viz_prompt = f"""
        As STELLA, create an enthusiastic description for a {viz_type.value} visualization showing user progress.
        
        User Request: {message}
        Data Available: {len(progress_data)} entries
        Metrics: {list(set(entry.data_type for entry in progress_data))}
        
        Describe what the visualization shows and highlight exciting trends, patterns, and achievements.
        Be specific about what makes this progress amazing and worth celebrating!
        """

        # Get AI description
        ai_response = await self.dependencies.vertex_ai_client.generate_content(viz_prompt)

        if not ai_response.get("success"):
            raise VisualizationError("Failed to generate visualization description")

        # Generate visualization data
        viz_data = self._prepare_visualization_data(progress_data, viz_type)

        return {
            "success": True,
            "skill": "visualize_progress",
            "visualization": {
                "type": viz_type.value,
                "data": viz_data,
                "config": self.config.get_visualization_config(),
                "description": ai_response.get("content", ""),
                "title": f"Your Amazing {viz_type.value.replace('_', ' ').title()} Progress!",
            },
            "insights": self._generate_visualization_insights(viz_data, viz_type),
            "celebration_points": self._identify_celebration_points(viz_data),
            "sharing_ready": True,
        }

    @handle_stella_exception
    async def _skill_compare_progress(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare progress between different time periods.

        Args:
            message: Comparison request
            context: User context

        Returns:
            Progress comparison with STELLA insights
        """
        user_id = context.get("user_id", "unknown")

        # Parse comparison periods from message
        periods = self._parse_comparison_periods(message)

        # Get data for both periods
        current_data = self.data_service.retrieve_progress_data(
            user_id=user_id,
            start_date=periods["current"]["start"],
            end_date=periods["current"]["end"],
        )

        previous_data = self.data_service.retrieve_progress_data(
            user_id=user_id,
            start_date=periods["previous"]["start"],
            end_date=periods["previous"]["end"],
        )

        if not current_data or not previous_data:
            return {
                "success": True,
                "skill": "compare_progress",
                "guidance": "I need more data to do an exciting comparison! Let's build up your progress history together! 📈",
                "suggestions": [
                    "Keep tracking consistently for better comparisons",
                    "Set up regular check-ins to compare weekly/monthly progress",
                    "Focus on one metric at a time for clearer comparisons",
                ],
                "comparison_ready": False,
            }

        # Create AI comparison prompt
        comparison_prompt = f"""
        As STELLA, enthusiastically compare these two progress periods for the user.
        
        User Request: {message}
        
        Current Period ({periods["current"]["start"].strftime('%Y-%m-%d')} to {periods["current"]["end"].strftime('%Y-%m-%d')}):
        - {len(current_data)} entries
        
        Previous Period ({periods["previous"]["start"].strftime('%Y-%m-%d')} to {periods["previous"]["end"].strftime('%Y-%m-%d')}):
        - {len(previous_data)} entries
        
        Provide an exciting comparison highlighting:
        1. Key improvements and wins
        2. Areas of growth and development
        3. Consistency changes
        4. Achievement milestones reached
        5. Motivational insights for continued progress
        
        Celebrate every positive change and provide encouraging perspective on any challenges!
        """

        # Get AI comparison
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            comparison_prompt
        )

        if not ai_response.get("success"):
            return {"success": False, "error": "Failed to generate comparison analysis"}

        # Calculate quantitative comparisons
        metrics_comparison = self._calculate_metrics_comparison(
            current_data, previous_data
        )

        return {
            "success": True,
            "skill": "compare_progress",
            "comparison_analysis": ai_response.get("content", ""),
            "periods": {
                "current": {
                    "label": f"{periods['current']['start'].strftime('%b %d')} - {periods['current']['end'].strftime('%b %d')}",
                    "entries": len(current_data),
                },
                "previous": {
                    "label": f"{periods['previous']['start'].strftime('%b %d')} - {periods['previous']['end'].strftime('%b %d')}",
                    "entries": len(previous_data),
                },
            },
            "metrics_comparison": metrics_comparison,
            "improvement_highlights": self._identify_improvements(metrics_comparison),
            "celebration_worthy": self._identify_celebration_worthy_changes(
                metrics_comparison
            ),
            "next_focus_areas": self._suggest_next_focus_areas(metrics_comparison),
        }

    @handle_stella_exception
    async def _skill_analyze_body_progress(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze body progress using vision AI.

        Args:
            message: Body analysis request
            context: User context including image data

        Returns:
            Body progress analysis with STELLA encouragement
        """
        user_id = context.get("user_id", "unknown")

        # Check for image data in context
        image_data = context.get("image_url") or context.get("image_data")

        if not image_data:
            return {
                "success": True,
                "skill": "analyze_body_progress",
                "guidance": "I'm excited to help analyze your body progress! Please upload a photo so I can give you amazing insights! 📸✨",
                "instructions": [
                    "Take a clear, well-lit photo in workout clothes",
                    "Use the same pose and angle for consistency",
                    "Compare with previous photos for best results",
                ],
                "image_required": True,
            }

        # Prepare vision analysis prompt
        vision_prompt = f"""
        As STELLA, analyze this body progress photo with enthusiasm and encouragement.
        
        User Request: {message}
        
        Provide detailed analysis of:
        1. Visible progress and improvements
        2. Body composition changes
        3. Posture and form improvements
        4. Overall transformation highlights
        5. Encouraging observations and celebrations
        
        Be supportive, positive, and focus on celebrating every improvement!
        Focus on health and fitness progress, not appearance judgments.
        """

        # Analyze image with vision AI
        vision_result = await self.dependencies.vision_processor.analyze_image(
            image_data, analysis_type="body_progress"
        )

        if not vision_result.get("success"):
            return {
                "success": False,
                "error": "Unable to analyze image at this time",
                "suggestions": [
                    "Try a clearer, well-lit photo",
                    "Ensure the image is in a supported format",
                    "Check your internet connection and try again",
                ],
            }

        # Get AI interpretation of vision results
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            f"{vision_prompt}\n\nVision Analysis Results: {vision_result.get('analysis', '')}"
        )

        # Store body progress data
        body_data_entry = {
            "analysis_type": "body_progress",
            "vision_results": vision_result.get("analysis", {}),
            "ai_interpretation": ai_response.get("content", ""),
            "image_metadata": context.get("image_metadata", {}),
        }

        self.data_service.store_progress_data(
            user_id=user_id, data_type="body_analysis", content=body_data_entry
        )

        return {
            "success": True,
            "skill": "analyze_body_progress",
            "analysis": ai_response.get("content", ""),
            "vision_insights": vision_result.get("analysis", {}),
            "progress_highlights": self._extract_body_progress_highlights(
                vision_result
            ),
            "measurements_detected": vision_result.get("measurements", {}),
            "comparison_suggestions": [
                "Take monthly progress photos for comparison",
                "Use the same lighting and pose each time",
                "Combine with body measurements for complete tracking",
            ],
            "celebration_points": self._identify_body_progress_celebrations(
                vision_result
            ),
        }

    @handle_stella_exception
    async def _skill_progress_celebration_conversation(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        STELLA's enthusiastic progress celebration conversation.

        Args:
            message: User's achievement or milestone mention
            context: User context

        Returns:
            Enthusiastic celebration with STELLA personality
        """
        user_id = context.get("user_id", "unknown")

        # Get recent achievements
        recent_progress = self.data_service.retrieve_progress_data(
            user_id=user_id, start_date=datetime.utcnow() - timedelta(days=7), limit=20
        )

        # Create celebration prompt with STELLA's enthusiastic personality
        celebration_prompt = f"""
        As STELLA, respond with maximum enthusiasm and celebration! You're an ESFJ who LOVES celebrating others' achievements!
        
        User Achievement: {message}
        
        Recent Progress Context: {len(recent_progress)} entries this week
        
        Respond with:
        1. Genuine excitement and celebration (use exclamation points!)
        2. Specific acknowledgment of their achievement
        3. Recognition of the effort it took
        4. Encouragement for continued progress
        5. Next milestone suggestions
        
        Be warm, enthusiastic, and make them feel absolutely amazing about their progress!
        Use STELLA's personality traits: supportive, detail-oriented, celebratory, encouraging.
        """

        # Get AI celebration response
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            celebration_prompt
        )

        if not ai_response.get("success"):
            # Fallback celebration response
            celebration_text = "🎉 WOW! That's absolutely incredible! I'm so proud of your amazing progress! Every step you take is building toward something fantastic! Keep up the outstanding work! 🌟"
        else:
            celebration_text = ai_response.get("content", "")

        # Detect what type of achievement this is
        achievement_type = self._classify_achievement_type(message)

        # Generate celebration badges/rewards
        celebration_rewards = self._generate_celebration_rewards(
            achievement_type, context
        )

        return {
            "success": True,
            "skill": "progress_celebration",
            "celebration_message": celebration_text,
            "achievement_type": achievement_type,
            "celebration_level": "high",
            "rewards": celebration_rewards,
            "sharing_message": self._create_sharing_message(message, achievement_type),
            "next_milestones": self._suggest_next_milestones(achievement_type, context),
            "motivational_boost": [
                "You're absolutely crushing your goals!",
                "This momentum is incredible - keep it going!",
                "I believe in your continued success!",
            ],
        }

    @handle_stella_exception
    async def _skill_milestone_analysis_conversation(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze and celebrate milestone progress with STELLA enthusiasm.

        Args:
            message: Milestone-related message
            context: User context

        Returns:
            Milestone analysis with celebration
        """
        user_id = context.get("user_id", "unknown")

        # Get comprehensive progress data
        progress_data = self.data_service.retrieve_progress_data(
            user_id=user_id,
            start_date=datetime.utcnow() - timedelta(days=180),  # 6 months
        )

        # Analyze milestone progress
        milestone_analysis = self.data_service.analyze_progress_patterns(
            user_id, "milestone_progress"
        )

        # Create STELLA milestone analysis prompt
        milestone_prompt = f"""
        As STELLA, analyze milestones with excitement and detailed insights!
        
        User Message: {message}
        Progress Data: {len(progress_data)} entries over 6 months
        Milestone Analysis: {milestone_analysis}
        
        Provide enthusiastic analysis of:
        1. Milestones achieved and celebration
        2. Progress patterns and trends
        3. Consistency achievements
        4. Goal progression analysis
        5. Future milestone predictions
        6. Motivational insights
        
        Be encouraging about progress made and exciting about future potential!
        """

        # Get AI milestone analysis
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            milestone_prompt
        )

        if not ai_response.get("success"):
            raise MilestoneTrackingError("Failed to generate milestone analysis")

        # Calculate milestone metrics
        milestone_metrics = self._calculate_milestone_metrics(progress_data)

        return {
            "success": True,
            "skill": "milestone_analysis",
            "analysis": ai_response.get("content", ""),
            "milestone_metrics": milestone_metrics,
            "achievements_summary": milestone_analysis,
            "progress_timeline": self._create_progress_timeline(progress_data),
            "upcoming_milestones": self._predict_upcoming_milestones(
                progress_data, context
            ),
            "celebration_highlights": self._identify_milestone_celebrations(
                milestone_metrics
            ),
            "motivation_message": "Your milestone journey is absolutely inspiring! Every goal you reach opens the door to even more amazing achievements! 🎯✨",
        }

    @handle_stella_exception
    async def _skill_motivational_checkin_conversation(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        STELLA's supportive motivational check-in conversation.

        Args:
            message: User's motivational need or struggle
            context: User context

        Returns:
            Motivational support with STELLA warmth
        """
        user_id = context.get("user_id", "unknown")

        # Analyze recent activity for context
        recent_activity = self.data_service.retrieve_progress_data(
            user_id=user_id, start_date=datetime.utcnow() - timedelta(days=14), limit=30
        )

        # Get consistency analysis
        consistency_analysis = self.data_service.analyze_progress_patterns(
            user_id, "consistency_analysis"
        )

        # Create motivational prompt with STELLA's supportive nature
        motivation_prompt = f"""
        As STELLA, provide warm, supportive motivation! You're an ESFJ who genuinely cares about helping others succeed.
        
        User Message: {message}
        Recent Activity: {len(recent_activity)} entries in past 2 weeks
        Consistency Level: {consistency_analysis.get('consistency_level', 'unknown')}
        
        Provide supportive response with:
        1. Acknowledgment of their feelings/struggles
        2. Recognition of their efforts and progress
        3. Practical motivation strategies
        4. Reminder of their capabilities and past wins
        5. Encouraging next steps
        6. Belief in their continued success
        
        Be warm, understanding, and genuinely encouraging. Focus on their strengths and potential!
        """

        # Get AI motivational response
        ai_response = await self.dependencies.vertex_ai_client.generate_content(
            motivation_prompt
        )

        if not ai_response.get("success"):
            # Fallback motivational response
            motivation_text = "I believe in you completely! Every challenge you face is making you stronger. You've overcome obstacles before, and I know you'll conquer this too! Let's take it one step at a time together! 💪✨"
        else:
            motivation_text = ai_response.get("content", "")

        # Generate personalized motivation strategies
        motivation_strategies = self._generate_motivation_strategies(
            consistency_analysis, context
        )

        # Create motivational action plan
        action_plan = self._create_motivational_action_plan(recent_activity, context)

        return {
            "success": True,
            "skill": "motivational_checkin",
            "motivation_message": motivation_text,
            "personal_strategies": motivation_strategies,
            "action_plan": action_plan,
            "progress_reminders": self._create_progress_reminders(recent_activity),
            "strength_affirmations": [
                "You have the strength to overcome any challenge",
                "Every step forward is a victory worth celebrating",
                "Your commitment to growth is truly inspiring",
                "Progress isn't always linear, and that's perfectly okay",
            ],
            "next_check_in": "I'll check in with you soon! Remember, I'm here to support your amazing journey! 🌟",
        }

    # Helper methods for skill processing
    def _calculate_tracking_consistency(self, progress_data: List) -> float:
        """Calculate tracking consistency percentage."""
        if not progress_data:
            return 0.0

        # Group by day
        tracking_days = set(entry.timestamp.date() for entry in progress_data)
        total_days = (datetime.utcnow().date() - min(tracking_days)).days + 1

        return (len(tracking_days) / total_days) * 100 if total_days > 0 else 0.0

    def _extract_recommendations_from_ai(self, ai_content: str) -> List[str]:
        """Extract actionable recommendations from AI response."""
        # Simple pattern matching for recommendations
        recommendations = []
        lines = ai_content.split("\n")

        for line in lines:
            line = line.strip()
            if any(
                keyword in line.lower()
                for keyword in ["recommend", "suggest", "try", "focus on", "consider"]
            ):
                # Clean up the line and add as recommendation
                clean_line = re.sub(r"^[\d\.\-\*\s]+", "", line).strip()
                if clean_line and len(clean_line) > 10:
                    recommendations.append(clean_line)

        return recommendations[:5]  # Limit to top 5 recommendations

    def _detect_achievements(self, progress_data: List) -> List[Dict[str, Any]]:
        """Detect achievements from progress data."""
        achievements = []

        # Simple achievement detection
        if len(progress_data) >= 7:
            achievements.append(
                {
                    "type": "consistency",
                    "title": "Week Warrior!",
                    "description": "Tracked progress for 7+ days",
                }
            )

        if len(progress_data) >= 30:
            achievements.append(
                {
                    "type": "consistency",
                    "title": "Monthly Master!",
                    "description": "Tracked progress for 30+ days",
                }
            )

        return achievements

    def _determine_visualization_type(self, message: str) -> VisualizationType:
        """Determine visualization type from message."""
        message_lower = message.lower()

        if any(keyword in message_lower for keyword in ["line", "trend", "over time"]):
            return VisualizationType.LINE_CHART
        elif any(
            keyword in message_lower for keyword in ["bar", "compare", "comparison"]
        ):
            return VisualizationType.BAR_CHART
        elif any(
            keyword in message_lower for keyword in ["progress bar", "percentage"]
        ):
            return VisualizationType.PROGRESS_BAR
        elif any(
            keyword in message_lower for keyword in ["heatmap", "calendar", "daily"]
        ):
            return VisualizationType.HEATMAP
        else:
            return VisualizationType.LINE_CHART  # Default

    def _prepare_visualization_data(
        self, progress_data: List, viz_type: VisualizationType
    ) -> Dict[str, Any]:
        """Prepare data for visualization."""
        # Group data by type and date
        data_by_type = {}
        for entry in progress_data:
            if entry.data_type not in data_by_type:
                data_by_type[entry.data_type] = []

            data_by_type[entry.data_type].append(
                {
                    "date": entry.timestamp.isoformat(),
                    "value": entry.content.get("weight", entry.content.get("value", 0)),
                    "entry": entry.content,
                }
            )

        return {
            "data_series": data_by_type,
            "total_points": len(progress_data),
            "date_range": {
                "start": min(entry.timestamp for entry in progress_data).isoformat(),
                "end": max(entry.timestamp for entry in progress_data).isoformat(),
            },
        }

    def _generate_visualization_insights(
        self, viz_data: Dict[str, Any], viz_type: VisualizationType
    ) -> List[str]:
        """Generate insights from visualization data."""
        insights = []

        data_series = viz_data.get("data_series", {})
        for data_type, points in data_series.items():
            if len(points) >= 2:
                start_value = points[0]["value"]
                end_value = points[-1]["value"]
                change = end_value - start_value

                if abs(change) > 0.1:
                    direction = "increased" if change > 0 else "decreased"
                    insights.append(
                        f"Your {data_type} has {direction} by {abs(change):.1f} over this period!"
                    )

        return insights

    def _identify_celebration_points(self, viz_data: Dict[str, Any]) -> List[str]:
        """Identify points worth celebrating in visualization."""
        celebrations = []

        total_points = viz_data.get("total_points", 0)
        if total_points >= 10:
            celebrations.append(f"Amazing consistency with {total_points} data points!")

        data_series = viz_data.get("data_series", {})
        if len(data_series) >= 3:
            celebrations.append("Fantastic multi-metric tracking!")

        return celebrations

    def _parse_comparison_periods(self, message: str) -> Dict[str, Dict[str, datetime]]:
        """Parse comparison periods from message."""
        # Default to last 30 days vs previous 30 days
        current_end = datetime.utcnow()
        current_start = current_end - timedelta(days=30)
        previous_end = current_start
        previous_start = previous_end - timedelta(days=30)

        return {
            "current": {"start": current_start, "end": current_end},
            "previous": {"start": previous_start, "end": previous_end},
        }

    def _calculate_metrics_comparison(
        self, current_data: List, previous_data: List
    ) -> Dict[str, Any]:
        """Calculate quantitative comparison between periods."""
        comparison = {}

        # Basic comparison
        comparison["data_points"] = {
            "current": len(current_data),
            "previous": len(previous_data),
            "change": len(current_data) - len(previous_data),
        }

        # Activity comparison
        current_days = set(entry.timestamp.date() for entry in current_data)
        previous_days = set(entry.timestamp.date() for entry in previous_data)

        comparison["active_days"] = {
            "current": len(current_days),
            "previous": len(previous_days),
            "change": len(current_days) - len(previous_days),
        }

        return comparison

    def _identify_improvements(self, metrics_comparison: Dict[str, Any]) -> List[str]:
        """Identify improvements from metrics comparison."""
        improvements = []

        data_change = metrics_comparison.get("data_points", {}).get("change", 0)
        if data_change > 0:
            improvements.append(
                f"Increased tracking frequency by {data_change} entries!"
            )

        days_change = metrics_comparison.get("active_days", {}).get("change", 0)
        if days_change > 0:
            improvements.append(
                f"More consistent tracking with {days_change} additional active days!"
            )

        return improvements

    def _identify_celebration_worthy_changes(
        self, metrics_comparison: Dict[str, Any]
    ) -> List[str]:
        """Identify changes worth celebrating."""
        celebrations = []

        # Any positive change is worth celebrating with STELLA!
        if metrics_comparison.get("data_points", {}).get("change", 0) >= 0:
            celebrations.append("Maintained or improved tracking consistency!")

        if metrics_comparison.get("active_days", {}).get("change", 0) >= 0:
            celebrations.append("Sustained active engagement with progress tracking!")

        return celebrations

    def _suggest_next_focus_areas(
        self, metrics_comparison: Dict[str, Any]
    ) -> List[str]:
        """Suggest next areas to focus on."""
        suggestions = []

        data_change = metrics_comparison.get("data_points", {}).get("change", 0)
        if data_change < 0:
            suggestions.append("Let's work on maintaining consistent daily tracking")

        suggestions.append("Consider adding new metrics to track holistic progress")
        suggestions.append("Set weekly mini-goals to maintain momentum")

        return suggestions

    async def _apply_stella_personality(
        self, skill_result: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply STELLA personality adaptation to skill result."""
        program_type = context.get("program_type", "LONGEVITY")
        personality_style = get_stella_personality_style(program_type, context)

        if not self.config.personality_adaptation_enabled:
            return skill_result

        try:
            # Get personality adaptation
            adaptation_result = (
                await self.dependencies.personality_adapter.adapt_response(
                    message=skill_result.get(
                        "analysis", skill_result.get("guidance", "")
                    ),
                    target_personality="ESFJ",  # STELLA's personality type
                    program_type=program_type,
                    context=context,
                )
            )

            if adaptation_result.get("success"):
                # Apply personality adaptation to appropriate fields
                for field in [
                    "guidance",
                    "analysis",
                    "celebration_message",
                    "motivation_message",
                ]:
                    if field in skill_result:
                        skill_result[field] = format_stella_response(
                            adaptation_result.get(
                                "adapted_message", skill_result[field]
                            ),
                            personality_style,
                        )

                # Add personality metadata
                skill_result["personality_adaptation"] = {
                    "applied": True,
                    "personality_type": "ESFJ",
                    "style": personality_style.value,
                    "program_type": program_type,
                    "confidence_score": adaptation_result.get("confidence_score", 0.8),
                }
            else:
                skill_result["personality_adaptation"] = {
                    "applied": False,
                    "error": adaptation_result.get("error", "Adaptation failed"),
                }

        except Exception as e:
            skill_result["personality_adaptation"] = {
                "applied": False,
                "error": f"Personality adaptation error: {str(e)}",
            }

        return skill_result

    async def _store_interaction_data(
        self, message: str, result: Dict[str, Any], context: Dict[str, Any]
    ):
        """Store interaction data for learning and improvement."""
        user_id = context.get("user_id", "unknown")

        interaction_data = {
            "user_message": message,
            "skill_used": result.get("skill", "unknown"),
            "success": result.get("success", False),
            "session_id": context.get("session_id"),
            "personality_adapted": result.get("personality_adaptation", {}).get(
                "applied", False
            ),
        }

        try:
            self.data_service.store_progress_data(
                user_id=user_id,
                data_type="stella_interaction",
                content=interaction_data,
            )
        except Exception:
            # Log storage failure but don't break the main flow
            pass

    def _update_skill_performance(
        self, skill_name: str, execution_time: float, success: bool
    ):
        """Update skill performance metrics."""
        if skill_name not in self.skill_performance_metrics:
            self.skill_performance_metrics[skill_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "total_time": 0.0,
                "average_time": 0.0,
            }

        metrics = self.skill_performance_metrics[skill_name]
        metrics["total_calls"] += 1
        metrics["total_time"] += execution_time
        metrics["average_time"] = metrics["total_time"] / metrics["total_calls"]

        if success:
            metrics["successful_calls"] += 1

    def get_skills_status(self) -> Dict[str, Any]:
        """Get skills manager status and performance metrics."""
        return {
            "available_skills": list(self.skills.keys()),
            "skill_usage_stats": self.skill_usage_stats,
            "skill_performance": self.skill_performance_metrics,
            "ai_integration": "gemini_real_implementation",
            "personality_adaptation": self.config.personality_adaptation_enabled,
            "service_status": "operational",
            "total_skills": len(self.skills),
            "personality_type": "ESFJ_STELLA",
        }

    # Additional helper methods for specific functionality
    def _classify_achievement_type(self, message: str) -> str:
        """Classify the type of achievement mentioned."""
        message_lower = message.lower()

        if any(
            keyword in message_lower for keyword in ["weight", "lost", "pounds", "kg"]
        ):
            return "weight_achievement"
        elif any(
            keyword in message_lower
            for keyword in ["strength", "lift", "pr", "personal record"]
        ):
            return "strength_achievement"
        elif any(
            keyword in message_lower
            for keyword in ["consistency", "streak", "daily", "every day"]
        ):
            return "consistency_achievement"
        elif any(
            keyword in message_lower
            for keyword in ["goal", "target", "milestone", "completed"]
        ):
            return "goal_achievement"
        else:
            return "general_achievement"

    def _generate_celebration_rewards(
        self, achievement_type: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate celebration rewards based on achievement type."""
        rewards = {
            "badges": [],
            "points": 0,
            "level_up": False,
            "special_recognition": "",
        }

        if achievement_type == "weight_achievement":
            rewards["badges"].append("🏆 Weight Goal Crusher")
            rewards["points"] = 50
            rewards["special_recognition"] = (
                "Outstanding dedication to your health journey!"
            )

        elif achievement_type == "strength_achievement":
            rewards["badges"].append("💪 Strength Superstar")
            rewards["points"] = 40
            rewards["special_recognition"] = (
                "Your strength gains are absolutely incredible!"
            )

        elif achievement_type == "consistency_achievement":
            rewards["badges"].append("🔥 Consistency Champion")
            rewards["points"] = 60
            rewards["special_recognition"] = (
                "Your consistency is the key to long-term success!"
            )

        return rewards

    def _create_sharing_message(self, achievement: str, achievement_type: str) -> str:
        """Create a shareable message for the achievement."""
        return f"🎉 Just achieved: {achievement}! So proud of this progress! #FitnessJourney #ProgressWithSTELLA"

    def _suggest_next_milestones(
        self, achievement_type: str, context: Dict[str, Any]
    ) -> List[str]:
        """Suggest next milestones based on current achievement."""
        suggestions = []

        if achievement_type == "weight_achievement":
            suggestions.extend(
                [
                    "Set a new weight goal to keep momentum going",
                    "Focus on body composition improvements",
                    "Add strength training to maintain muscle",
                ]
            )

        elif achievement_type == "consistency_achievement":
            suggestions.extend(
                [
                    "Extend your streak for even more amazing results",
                    "Add a new healthy habit to your routine",
                    "Help inspire others with your consistency!",
                ]
            )

        return suggestions[:3]  # Return top 3 suggestions
