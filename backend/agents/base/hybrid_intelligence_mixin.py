"""
GENESIS NGX Agents - Hybrid Intelligence Mixin
==============================================

Base mixin class that provides Hybrid Intelligence integration for all NGX agents.
This mixin replaces the PersonalityAdapter with the revolutionary two-layer
personalization system across all agents.

Features:
- Automatic integration with Hybrid Intelligence Engine
- Agent-specific adaptation mappings
- Consistent personalization API
- Backward compatibility support

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-09
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import logging
from abc import abstractmethod

# Import hybrid intelligence components
from core.hybrid_intelligence import (
    HybridIntelligenceEngine,
    UserProfile,
    PersonalizationContext,
    PersonalizationResult,
    UserArchetype,
    PersonalizationMode
)

# Import data models
from core.hybrid_intelligence.models import (
    UserProfileData,
    PersonalizationContextData,
    UserBiometrics,
    WorkoutData,
    FitnessLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridIntelligenceMixin:
    """
    Mixin class that provides Hybrid Intelligence capabilities to any NGX agent.
    
    This mixin should be added to the agent's inheritance chain to enable
    two-layer personalization (archetype + physiological modulation).
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize hybrid intelligence components"""
        super().__init__(*args, **kwargs)
        
        # Initialize Hybrid Intelligence Engine (singleton pattern)
        self._hybrid_engine = None
        self._hybrid_enabled = kwargs.get('hybrid_intelligence_enabled', True)
        
        # Agent-specific configurations (to be overridden by each agent)
        self._agent_adaptations = self._get_agent_adaptations()
        
        logger.info(f"Hybrid Intelligence Mixin initialized for {self.__class__.__name__}")
    
    @property
    def hybrid_engine(self) -> HybridIntelligenceEngine:
        """Lazy initialization of Hybrid Intelligence Engine"""
        if self._hybrid_engine is None:
            self._hybrid_engine = HybridIntelligenceEngine()
            logger.info(f"Hybrid Intelligence Engine initialized for {self.AGENT_ID}")
        return self._hybrid_engine
    
    @abstractmethod
    def _get_agent_adaptations(self) -> Dict[str, Any]:
        """
        Get agent-specific adaptation configurations.
        
        Each agent must override this to provide their specific adaptations.
        
        Returns:
            Dictionary with agent-specific adaptation mappings
        """
        # Default adaptations - should be overridden
        return {
            "communication_styles": {
                "direct_performance": "professional_direct",
                "supportive_educational": "encouraging_supportive"
            },
            "content_focus": {
                "prime": ["efficiency", "optimization", "results"],
                "longevity": ["sustainability", "health", "balance"]
            },
            "intensity_mappings": {
                "high": 0.8,
                "moderate": 0.6,
                "low": 0.4
            }
        }
    
    async def personalize_response(self,
                                 user_data: Dict[str, Any],
                                 request_type: str,
                                 request_content: str,
                                 session_context: Optional[Dict[str, Any]] = None,
                                 mode: PersonalizationMode = PersonalizationMode.ADVANCED) -> Dict[str, Any]:
        """
        Main method to get personalized response using Hybrid Intelligence.
        
        Args:
            user_data: User profile and biometric data
            request_type: Type of request for this agent
            request_content: Specific content of the request
            session_context: Current session context
            mode: Personalization mode (BASIC, ADVANCED, EXPERT)
            
        Returns:
            Personalized response with adaptations applied
        """
        
        if not self._hybrid_enabled:
            # Fallback to basic personalization if disabled
            return await self._basic_personalization(user_data, request_type, request_content)
        
        try:
            # Transform user data to hybrid intelligence format
            user_profile = await self._transform_user_data(user_data)
            
            # Create personalization context
            context = PersonalizationContext(
                user_profile=user_profile,
                agent_type=self.AGENT_ID,
                request_type=request_type,
                request_content=request_content,
                session_context=session_context or {}
            )
            
            # Get personalization from hybrid engine
            personalization_result = await self.hybrid_engine.personalize_for_user(
                context=context,
                mode=mode
            )
            
            # Apply agent-specific personalization
            personalized_response = await self._apply_agent_personalization(
                personalization_result,
                request_type,
                request_content
            )
            
            logger.info(f"{self.AGENT_ID} personalization complete. Confidence: {personalization_result.confidence_score:.2f}")
            
            return personalized_response
            
        except Exception as e:
            logger.error(f"{self.AGENT_ID} personalization failed: {str(e)}")
            # Return fallback response
            return await self._generate_fallback_response(request_type, request_content)
    
    async def _transform_user_data(self, user_data: Dict[str, Any]) -> UserProfile:
        """
        Transform user data to UserProfile format.
        
        Can be overridden by agents for custom transformations.
        """
        
        # Extract basic profile data
        archetype = UserArchetype.PRIME if user_data.get("archetype", "prime") == "prime" else UserArchetype.LONGEVITY
        
        # Create UserProfile
        user_profile = UserProfile(
            user_id=user_data.get("user_id", "unknown"),
            archetype=archetype,
            age=user_data.get("age", 30),
            gender=user_data.get("gender", "unknown"),
            
            # Fitness and health data
            fitness_level=user_data.get("fitness_level", "intermediate"),
            injury_history=user_data.get("injury_history", []),
            current_medications=user_data.get("medications", []),
            
            # Biometric data
            sleep_quality=user_data.get("sleep_quality"),
            stress_level=user_data.get("stress_level"),
            energy_level=user_data.get("energy_level"),
            
            # Activity data
            recent_workouts=user_data.get("recent_workouts", []),
            
            # Constraints
            time_constraints=user_data.get("time_constraints", {}),
            equipment_access=user_data.get("equipment_access", []),
            dietary_restrictions=user_data.get("dietary_restrictions", []),
            
            # Preferences
            preference_scores=user_data.get("preference_scores", {}),
            interaction_history=user_data.get("interaction_history", [])
        )
        
        return user_profile
    
    async def _apply_agent_personalization(self,
                                         personalization_result: PersonalizationResult,
                                         request_type: str,
                                         request_content: str) -> Dict[str, Any]:
        """
        Apply agent-specific personalization to the result.
        
        Should be overridden by each agent for custom adaptations.
        """
        
        # Extract personalization components
        combined_recs = personalization_result.combined_recommendations
        
        # Build personalized response
        personalized_response = {
            "personalization_applied": True,
            "confidence_score": personalization_result.confidence_score,
            "explanation": personalization_result.explanation,
            
            # Communication adaptations
            "communication_style": await self._adapt_communication_style(combined_recs),
            
            # Content adaptations
            "content_adaptations": await self._adapt_content_delivery(combined_recs),
            
            # Agent-specific adaptations
            "agent_adaptations": await self._get_agent_specific_adaptations(combined_recs),
            
            # Timing recommendations
            "timing_recommendations": combined_recs.get("timing_adaptations", {}),
            
            # Metadata
            "personalization_metadata": combined_recs["personalization_metadata"]
        }
        
        return personalized_response
    
    async def _adapt_communication_style(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt communication style based on personalization"""
        
        base_style = combined_recs["communication_adaptations"]["style"]
        intensity = combined_recs["communication_adaptations"]["intensity"]
        
        # Map to agent-specific communication styles
        agent_style = self._agent_adaptations["communication_styles"].get(
            base_style, "professional_direct"
        )
        
        return {
            "style": agent_style,
            "intensity_level": intensity,
            "safety_emphasis": combined_recs["communication_adaptations"]["safety_emphasis"],
            "agent_specific": {
                "tone": self._get_agent_tone(base_style, intensity),
                "detail_level": self._get_detail_level(base_style),
                "motivation_approach": self._get_motivation_approach(base_style)
            }
        }
    
    async def _adapt_content_delivery(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content delivery based on personalization"""
        
        content_adaptations = combined_recs["content_adaptations"]
        
        return {
            "complexity_level": content_adaptations.get("complexity_adjustment", "moderate"),
            "delivery_style": content_adaptations["delivery_style"],
            "focus_areas": content_adaptations["focus_prioritization"],
            "agent_specific": await self._get_agent_content_preferences(content_adaptations)
        }
    
    @abstractmethod
    async def _get_agent_specific_adaptations(self, combined_recs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get agent-specific adaptations.
        
        Each agent MUST override this method to provide their specific adaptations.
        """
        raise NotImplementedError("Each agent must implement _get_agent_specific_adaptations")
    
    def _get_agent_tone(self, base_style: str, intensity: float) -> str:
        """Get agent-appropriate tone based on style and intensity"""
        if base_style == "direct_performance":
            return "assertive" if intensity > 0.7 else "confident"
        elif base_style == "supportive_educational":
            return "nurturing" if intensity < 0.5 else "encouraging"
        else:
            return "professional"
    
    def _get_detail_level(self, base_style: str) -> str:
        """Get appropriate detail level based on communication style"""
        if base_style == "direct_performance":
            return "concise"
        elif base_style == "supportive_educational":
            return "comprehensive"
        else:
            return "moderate"
    
    def _get_motivation_approach(self, base_style: str) -> str:
        """Get motivation approach based on communication style"""
        if base_style == "direct_performance":
            return "achievement_focused"
        elif base_style == "supportive_educational":
            return "progress_focused"
        else:
            return "balanced"
    
    async def _get_agent_content_preferences(self, content_adaptations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get agent-specific content preferences.
        
        Can be overridden by agents for custom preferences.
        """
        return {
            "format_preferences": ["structured", "visual", "interactive"],
            "example_types": ["practical", "scientific", "experiential"],
            "reference_style": "evidence_based"
        }
    
    async def _basic_personalization(self, user_data: Dict[str, Any], 
                                   request_type: str, 
                                   request_content: str) -> Dict[str, Any]:
        """Basic personalization fallback when hybrid intelligence is disabled"""
        
        archetype = user_data.get("archetype", "prime")
        
        return {
            "personalization_applied": False,
            "fallback_mode": True,
            "basic_adaptations": {
                "archetype": archetype,
                "communication_style": "direct" if archetype == "prime" else "supportive",
                "intensity": "moderate"
            },
            "message": "Using basic personalization mode"
        }
    
    async def _generate_fallback_response(self, request_type: str, request_content: str) -> Dict[str, Any]:
        """Generate fallback response if personalization fails"""
        
        return {
            "personalization_applied": False,
            "error_fallback": True,
            "communication_style": {
                "style": "professional_neutral",
                "intensity_level": 0.7
            },
            "content_adaptations": {
                "complexity_level": "moderate",
                "delivery_style": "standard"
            },
            "message": f"Using standard {self.AGENT_ID} configuration"
        }
    
    async def provide_personalization_feedback(self,
                                             session_id: str,
                                             user_feedback: Dict[str, Any]):
        """
        Provide feedback to the hybrid intelligence engine for learning.
        
        Args:
            session_id: Session identifier
            user_feedback: User feedback data
        """
        
        try:
            # This would ideally retrieve the stored context and result
            # For now, we log the feedback
            logger.info(f"{self.AGENT_ID} received feedback for session {session_id}: {user_feedback}")
            
            # In a complete implementation, this would:
            # 1. Retrieve stored context and result from session
            # 2. Call hybrid_engine.learning_engine.learn_from_interaction
            
        except Exception as e:
            logger.error(f"Error processing feedback for {self.AGENT_ID}: {str(e)}")
    
    def get_personalization_confidence(self) -> float:
        """Get current personalization confidence level"""
        # This could track rolling average of confidence scores
        return 0.85  # Placeholder
    
    def is_hybrid_intelligence_enabled(self) -> bool:
        """Check if hybrid intelligence is enabled for this agent"""
        return self._hybrid_enabled
    
    def enable_hybrid_intelligence(self):
        """Enable hybrid intelligence for this agent"""
        self._hybrid_enabled = True
        logger.info(f"Hybrid Intelligence enabled for {self.AGENT_ID}")
    
    def disable_hybrid_intelligence(self):
        """Disable hybrid intelligence (use fallback personalization)"""
        self._hybrid_enabled = False
        logger.info(f"Hybrid Intelligence disabled for {self.AGENT_ID}")


# Export the mixin
__all__ = ["HybridIntelligenceMixin"]