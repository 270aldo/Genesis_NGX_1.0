"""
Dependency injection container for BLAZE Elite Training Strategist.
Provides centralized access to all external services and configurations.
"""

from dataclasses import dataclass
from typing import Optional

from clients.vertex_ai.client import VertexAIClient
from clients.supabase_client import SupabaseClient
from tools.mcp_toolkit import MCPToolkit
from services.program_classification_service import ProgramClassificationService
from core.personality.personality_adapter import PersonalityAdapter

# Import training-specific skills
from agents.skills.audio_voice_skills import (
    WorkoutVoiceGuideSkill,
    VoiceCommandSkill,
    AudioFeedbackSkill,
)

from agents.elite_training_strategist.advanced_training_skills import (
    AdvancedTrainingPlanSkill,
    IntelligentNutritionIntegrationSkill,
    AIProgressAnalysisSkill,
    AdaptiveTrainingSkill,
)


@dataclass
class BlazeAgentDependencies:
    """
    Dependency container for BLAZE Elite Training Strategist.

    Provides access to all external services, AI models, and specialized skills
    needed for elite training program generation and athlete performance optimization.
    """

    # Core AI and Data Services
    vertex_ai_client: VertexAIClient
    supabase_client: SupabaseClient
    mcp_toolkit: MCPToolkit
    program_classification_service: ProgramClassificationService
    personality_adapter: PersonalityAdapter

    # Audio and Voice Skills
    workout_voice_guide_skill: WorkoutVoiceGuideSkill
    voice_command_skill: VoiceCommandSkill
    audio_feedback_skill: AudioFeedbackSkill

    # Advanced Training Skills (transferred from Gemini)
    advanced_training_plan_skill: AdvancedTrainingPlanSkill
    intelligent_nutrition_skill: IntelligentNutritionIntegrationSkill
    ai_progress_analysis_skill: AIProgressAnalysisSkill
    adaptive_training_skill: AdaptiveTrainingSkill

    @classmethod
    def create_default(
        cls, mcp_toolkit: Optional[MCPToolkit] = None
    ) -> "BlazeAgentDependencies":
        """
        Create dependencies with default implementations.

        Args:
            mcp_toolkit: Optional MCP toolkit, creates default if None

        Returns:
            Configured dependency container
        """
        vertex_ai_client = VertexAIClient()

        return cls(
            # Core AI and Data Services
            vertex_ai_client=vertex_ai_client,
            supabase_client=SupabaseClient(),
            mcp_toolkit=mcp_toolkit or MCPToolkit(),
            program_classification_service=ProgramClassificationService(vertex_ai_client),
            personality_adapter=PersonalityAdapter(),
            # Audio and Voice Skills
            workout_voice_guide_skill=WorkoutVoiceGuideSkill(),
            voice_command_skill=VoiceCommandSkill(),
            audio_feedback_skill=AudioFeedbackSkill(),
            # Advanced Training Skills
            advanced_training_plan_skill=AdvancedTrainingPlanSkill(),
            intelligent_nutrition_skill=IntelligentNutritionIntegrationSkill(),
            ai_progress_analysis_skill=AIProgressAnalysisSkill(),
            adaptive_training_skill=AdaptiveTrainingSkill(),
        )
