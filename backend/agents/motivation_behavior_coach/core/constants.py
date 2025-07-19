"""
Constants and enums for SPARK Motivation Behavior Coach.
Centralized definition of behavioral change models, motivation strategies, and coaching frameworks.
"""

from enum import Enum, IntEnum
from typing import Dict, List, Set, Any
from dataclasses import dataclass


# ===============================================================================
# MOTIVATION AND BEHAVIOR CHANGE MODELS
# ===============================================================================


class MotivationType(Enum):
    """Types of motivation based on Self-Determination Theory."""

    INTRINSIC = "intrinsic"  # Internal satisfaction and enjoyment
    EXTRINSIC = "extrinsic"  # External rewards and consequences
    IDENTIFIED = "identified"  # Personal importance and value
    INTROJECTED = "introjected"  # Ego involvement and internal pressure
    AMOTIVATION = "amotivation"  # Lack of motivation or intention


class StageOfChange(Enum):
    """Stages from Transtheoretical Model (Prochaska & DiClemente)."""

    PRECONTEMPLATION = "precontemplation"  # Not considering change
    CONTEMPLATION = "contemplation"  # Considering change within 6 months
    PREPARATION = "preparation"  # Planning to change within 30 days
    ACTION = "action"  # Actively making changes (0-6 months)
    MAINTENANCE = "maintenance"  # Sustaining change (6+ months)
    RELAPSE = "relapse"  # Return to previous behavior


class BehaviorChangeProcess(Enum):
    """Processes of change from Transtheoretical Model."""

    # Cognitive processes
    CONSCIOUSNESS_RAISING = "consciousness_raising"
    DRAMATIC_RELIEF = "dramatic_relief"
    ENVIRONMENTAL_REEVALUATION = "environmental_reevaluation"
    SELF_REEVALUATION = "self_reevaluation"
    SOCIAL_LIBERATION = "social_liberation"

    # Behavioral processes
    COUNTERCONDITIONING = "counterconditioning"
    HELPING_RELATIONSHIPS = "helping_relationships"
    REINFORCEMENT_MANAGEMENT = "reinforcement_management"
    SELF_LIBERATION = "self_liberation"
    STIMULUS_CONTROL = "stimulus_control"


class HabitLoopComponent(Enum):
    """Components of the habit loop (Charles Duhigg)."""

    CUE = "cue"  # Environmental trigger
    ROUTINE = "routine"  # Behavioral response
    REWARD = "reward"  # Neurological reward
    CRAVING = "craving"  # Anticipation of reward


class MotivationStrategy(Enum):
    """Evidence-based motivation strategies."""

    GOAL_SETTING = "goal_setting"
    PROGRESS_MONITORING = "progress_monitoring"
    SOCIAL_SUPPORT = "social_support"
    SELF_EFFICACY_BUILDING = "self_efficacy_building"
    VALUE_CLARIFICATION = "value_clarification"
    REWARD_SYSTEMS = "reward_systems"
    VISUALIZATION = "visualization"
    IMPLEMENTATION_INTENTIONS = "implementation_intentions"
    ACCOUNTABILITY_PARTNERSHIPS = "accountability_partnerships"
    HABIT_STACKING = "habit_stacking"
    ENVIRONMENTAL_DESIGN = "environmental_design"
    CELEBRATION_RITUALS = "celebration_rituals"


# ===============================================================================
# COACHING AND INTERVENTION FRAMEWORKS
# ===============================================================================


class CoachingModel(Enum):
    """Coaching models and frameworks."""

    GROW = "grow"  # Goal, Reality, Options, Will
    CLEAR = "clear"  # Contract, Listen, Explore, Action, Review
    ACHIEVE = (
        "achieve"  # Assess, Creative, Hone, Initiate, Evaluate, Vigorous, Excellence
    )
    FUEL = "fuel"  # Frame, Understand, Explore, Layout
    OSKAR = "oskar"  # Outcome, Scaling, Know-how, Affirm, Review


class InterventionType(Enum):
    """Types of behavioral interventions."""

    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    MINDFULNESS_BASED = "mindfulness_based"
    MOTIVATIONAL_INTERVIEWING = "motivational_interviewing"
    ACCEPTANCE_COMMITMENT = "acceptance_commitment"
    SOLUTION_FOCUSED = "solution_focused"
    STRENGTHS_BASED = "strengths_based"
    NARRATIVE_THERAPY = "narrative_therapy"
    POSITIVE_PSYCHOLOGY = "positive_psychology"


class CommunicationStyle(Enum):
    """Communication styles for different contexts."""

    DIRECTIVE = "directive"  # Clear instructions and guidance
    SUPPORTIVE = "supportive"  # Encouragement and emotional support
    COLLABORATIVE = "collaborative"  # Partnership and joint problem-solving
    CHALLENGING = "challenging"  # Confronting and pushing boundaries
    REFLECTIVE = "reflective"  # Mirroring and clarifying
    SOCRATIC = "socratic"  # Questions that lead to self-discovery


# ===============================================================================
# ASSESSMENT AND MEASUREMENT
# ===============================================================================


class AssessmentDomain(Enum):
    """Domains for behavioral assessment."""

    MOTIVATION_LEVEL = "motivation_level"
    SELF_EFFICACY = "self_efficacy"
    STAGE_OF_CHANGE = "stage_of_change"
    HABIT_STRENGTH = "habit_strength"
    GOAL_PROGRESS = "goal_progress"
    OBSTACLE_SEVERITY = "obstacle_severity"
    SUPPORT_SYSTEM = "support_system"
    STRESS_LEVEL = "stress_level"
    CONFIDENCE_LEVEL = "confidence_level"
    COMMITMENT_LEVEL = "commitment_level"


class MeasurementScale(IntEnum):
    """Standard measurement scales for assessments."""

    MIN_SCORE = 1
    LOW_THRESHOLD = 3
    MEDIUM_THRESHOLD = 5
    HIGH_THRESHOLD = 7
    MAX_SCORE = 10


class ProgressIndicator(Enum):
    """Indicators of progress in behavior change."""

    IMPROVED_MOTIVATION = "improved_motivation"
    INCREASED_FREQUENCY = "increased_frequency"
    REDUCED_RESISTANCE = "reduced_resistance"
    ENHANCED_CONFIDENCE = "enhanced_confidence"
    BETTER_CONSISTENCY = "better_consistency"
    FASTER_RECOVERY = "faster_recovery"
    STRONGER_HABITS = "stronger_habits"
    CLEARER_VALUES = "clearer_values"


# ===============================================================================
# PERSONALITY ADAPTATION CONSTANTS
# ===============================================================================


class ProgramType(Enum):
    """NGX program types for personality adaptation."""

    PRIME = "PRIME"  # Executive performance optimization
    LONGEVITY = "LONGEVITY"  # Long-term wellness and prevention


@dataclass
class PersonalityStyle:
    """Personality adaptation style configuration."""

    tone: str
    language_complexity: str
    focus_areas: List[str]
    communication_preferences: List[str]
    motivation_triggers: List[str]
    success_metrics: List[str]


# Program-specific personality styles
PRIME_PERSONALITY_STYLE = PersonalityStyle(
    tone="strategic_executive",
    language_complexity="technical_strategic",
    focus_areas=[
        "performance_optimization",
        "competitive_advantage",
        "efficiency_maximization",
        "strategic_goal_achievement",
        "executive_productivity",
    ],
    communication_preferences=[
        "direct_actionable",
        "data_driven",
        "results_focused",
        "time_efficient",
        "strategic_context",
    ],
    motivation_triggers=[
        "achievement_recognition",
        "competitive_advantage",
        "performance_metrics",
        "leadership_impact",
        "strategic_success",
    ],
    success_metrics=[
        "performance_kpis",
        "productivity_gains",
        "goal_achievement_rate",
        "efficiency_improvements",
        "competitive_positioning",
    ],
)

LONGEVITY_PERSONALITY_STYLE = PersonalityStyle(
    tone="consultive_educational",
    language_complexity="clear_explanatory",
    focus_areas=[
        "sustainable_habits",
        "long_term_wellness",
        "gradual_improvement",
        "life_balance",
        "preventive_care",
    ],
    communication_preferences=[
        "supportive_encouraging",
        "educational_informative",
        "gradual_progressive",
        "holistic_balanced",
        "wellness_focused",
    ],
    motivation_triggers=[
        "health_improvements",
        "quality_of_life",
        "family_wellbeing",
        "longevity_goals",
        "sustainable_progress",
    ],
    success_metrics=[
        "health_markers",
        "habit_consistency",
        "wellbeing_scores",
        "lifestyle_balance",
        "preventive_measures",
    ],
)


# ===============================================================================
# SKILL AND CAPABILITY CONSTANTS
# ===============================================================================


class SkillCategory(Enum):
    """Categories of SPARK skills."""

    HABIT_FORMATION = "habit_formation"
    GOAL_SETTING = "goal_setting"
    MOTIVATION_STRATEGIES = "motivation_strategies"
    BEHAVIOR_CHANGE = "behavior_change"
    OBSTACLE_MANAGEMENT = "obstacle_management"
    CONVERSATIONAL = "conversational"
    ASSESSMENT = "assessment"
    INTERVENTION = "intervention"


SKILL_DEFINITIONS = {
    "habit_formation": {
        "description": "Design and implement sustainable habit formation plans",
        "input_schema": "HabitFormationInput",
        "output_schema": "HabitFormationOutput",
        "ai_enabled": True,
        "complexity_level": "medium",
        "estimated_duration_minutes": 15,
    },
    "goal_setting": {
        "description": "Create SMART goals with actionable milestones",
        "input_schema": "GoalSettingInput",
        "output_schema": "GoalSettingOutput",
        "ai_enabled": True,
        "complexity_level": "medium",
        "estimated_duration_minutes": 12,
    },
    "motivation_strategies": {
        "description": "Develop personalized motivation enhancement strategies",
        "input_schema": "MotivationStrategiesInput",
        "output_schema": "MotivationStrategiesOutput",
        "ai_enabled": True,
        "complexity_level": "high",
        "estimated_duration_minutes": 18,
    },
    "behavior_change": {
        "description": "Guide through systematic behavior change processes",
        "input_schema": "BehaviorChangeInput",
        "output_schema": "BehaviorChangeOutput",
        "ai_enabled": True,
        "complexity_level": "high",
        "estimated_duration_minutes": 20,
    },
    "obstacle_management": {
        "description": "Identify and develop solutions for behavioral obstacles",
        "input_schema": "ObstacleManagementInput",
        "output_schema": "ObstacleManagementOutput",
        "ai_enabled": True,
        "complexity_level": "medium",
        "estimated_duration_minutes": 14,
    },
}


# ===============================================================================
# CONVERSATION AND INTERACTION CONSTANTS
# ===============================================================================


class ConversationContext(Enum):
    """Contexts for conversational interactions."""

    INITIAL_CONSULTATION = "initial_consultation"
    PROGRESS_CHECK_IN = "progress_check_in"
    OBSTACLE_DISCUSSION = "obstacle_discussion"
    MOTIVATION_BOOST = "motivation_boost"
    GOAL_REVIEW = "goal_review"
    HABIT_REINFORCEMENT = "habit_reinforcement"
    CELEBRATION = "celebration"
    COURSE_CORRECTION = "course_correction"


CONVERSATIONAL_PROMPTS = {
    "habit_formation_coaching": {
        "opening": "Let's explore how to build lasting habits that align with your goals.",
        "assessment": "Tell me about your current habits and what you'd like to change.",
        "strategy": "Based on your situation, here's a personalized approach...",
        "reinforcement": "Remember, small consistent actions create lasting change.",
    },
    "mindset_transformation": {
        "opening": "Your mindset is the foundation of all lasting change.",
        "exploration": "What beliefs about yourself might be holding you back?",
        "reframing": "Let's look at this challenge from a different perspective...",
        "empowerment": "You have the power to reshape your thinking patterns.",
    },
    "goal_setting_dialogue": {
        "opening": "Great goals are the bridge between dreams and reality.",
        "clarification": "Help me understand what success looks like for you.",
        "planning": "Let's break this down into achievable steps...",
        "commitment": "What will keep you motivated when things get tough?",
    },
    "behavioral_change_support": {
        "opening": "Change is a journey, and every step counts.",
        "assessment": "Where are you in your change journey right now?",
        "guidance": "Here's what typically works best at your stage...",
        "encouragement": "Progress isn't always linear, and that's perfectly normal.",
    },
    "confidence_building": {
        "opening": "Confidence grows through action and self-compassion.",
        "reflection": "What past successes can remind you of your capabilities?",
        "affirmation": "You've overcome challenges before, and you can do it again.",
        "action": "What's one small step you can take today to build momentum?",
    },
}


# ===============================================================================
# ERROR HANDLING AND VALIDATION
# ===============================================================================

ERROR_MESSAGES = {
    "motivation_analysis_failed": "Unable to analyze motivation patterns. Please try again with more specific information.",
    "habit_formation_invalid": "The habit formation plan contains invalid parameters. Please review your inputs.",
    "goal_setting_incomplete": "Goal setting requires more detailed information to create an effective plan.",
    "behavior_change_unsupported": "The requested behavior change is not supported by current evidence-based methods.",
    "obstacle_identification_failed": "Unable to identify specific obstacles. Please provide more context about your challenges.",
    "personality_adaptation_error": "Error adapting communication style. Using default approach.",
    "ai_analysis_timeout": "AI analysis is taking longer than expected. Please try again.",
    "external_service_unavailable": "External service temporarily unavailable. Some features may be limited.",
    "data_validation_failed": "Input data validation failed. Please check your information and try again.",
    "insufficient_context": "Insufficient context provided for personalized recommendations.",
}


# ===============================================================================
# PERFORMANCE AND OPTIMIZATION
# ===============================================================================

PERFORMANCE_THRESHOLDS = {
    "max_response_time_ms": 30000,  # 30 seconds
    "target_response_time_ms": 15000,  # 15 seconds
    "cache_ttl_seconds": 3600,  # 1 hour
    "max_cache_entries": 1000,
    "batch_processing_size": 50,
    "concurrent_requests_limit": 10,
    "retry_attempts": 3,
    "retry_delay_ms": 1000,
    "health_check_interval_ms": 60000,  # 1 minute
}


# ===============================================================================
# INTEGRATION AND EXTERNAL SERVICES
# ===============================================================================

EXTERNAL_SERVICES = {
    "gemini_ai": {
        "endpoint": "generative-ai",
        "model": "gemini-pro",
        "timeout_seconds": 25,
        "retry_attempts": 2,
    },
    "personality_adapter": {
        "service": "personality_adaptation",
        "timeout_seconds": 5,
        "cache_enabled": True,
    },
    "program_classification": {
        "service": "program_classification",
        "timeout_seconds": 3,
        "cache_enabled": True,
    },
}


# ===============================================================================
# UTILITY FUNCTIONS
# ===============================================================================


def get_personality_style(program_type: str) -> PersonalityStyle:
    """Get personality style configuration for program type."""
    if program_type == ProgramType.PRIME.value:
        return PRIME_PERSONALITY_STYLE
    elif program_type == ProgramType.LONGEVITY.value:
        return LONGEVITY_PERSONALITY_STYLE
    else:
        return LONGEVITY_PERSONALITY_STYLE  # Default to LONGEVITY


def get_skill_definition(skill_name: str) -> Dict[str, Any]:
    """Get skill definition by name."""
    return SKILL_DEFINITIONS.get(skill_name, {})


def get_conversational_prompts(context: str) -> Dict[str, str]:
    """Get conversational prompts for specific context."""
    return CONVERSATIONAL_PROMPTS.get(context, {})


def validate_motivation_score(score: float) -> bool:
    """Validate motivation score is within acceptable range."""
    return MeasurementScale.MIN_SCORE <= score <= MeasurementScale.MAX_SCORE


def get_stage_recommendations(stage: StageOfChange) -> List[str]:
    """Get recommended interventions for stage of change."""
    recommendations = {
        StageOfChange.PRECONTEMPLATION: [
            "consciousness_raising",
            "dramatic_relief",
            "environmental_reevaluation",
        ],
        StageOfChange.CONTEMPLATION: [
            "self_reevaluation",
            "social_liberation",
            "consciousness_raising",
        ],
        StageOfChange.PREPARATION: [
            "self_liberation",
            "helping_relationships",
            "stimulus_control",
        ],
        StageOfChange.ACTION: [
            "reinforcement_management",
            "helping_relationships",
            "counterconditioning",
            "stimulus_control",
        ],
        StageOfChange.MAINTENANCE: [
            "reinforcement_management",
            "stimulus_control",
            "helping_relationships",
        ],
        StageOfChange.RELAPSE: [
            "consciousness_raising",
            "dramatic_relief",
            "self_reevaluation",
        ],
    }
    return recommendations.get(stage, [])
