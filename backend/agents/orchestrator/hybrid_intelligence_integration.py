"""
GENESIS NGX Agents - NEXUS Hybrid Intelligence Integration
=========================================================

Integration module for the NEXUS agent (Orchestrator) with the
Hybrid Intelligence Engine. This module provides the most critical
personalization layer as NEXUS coordinates all agent interactions.

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-10
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import logging

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
    HybridIntelligenceRequest,
    HybridIntelligenceResponse,
    UserBiometrics,
    OrchestrationData,
    RoutingDecision,
    AgentCoordinationMode
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NEXUSHybridIntelligenceIntegration:
    """
    Integration layer between NEXUS agent and Hybrid Intelligence Engine
    
    This is the MOST CRITICAL integration as NEXUS coordinates all agent
    interactions and must provide personalized orchestration for optimal
    user experience across all specialized agents.
    
    Features:
    - Personalized intent analysis based on user archetype
    - Intelligent agent routing with archetype consideration
    - Adaptive response synthesis matching user communication style
    - Context-aware conversation flow management
    """
    
    def __init__(self):
        """Initialize NEXUS Hybrid Intelligence Integration"""
        self.engine = HybridIntelligenceEngine()
        self.integration_name = "NEXUS_ORCHESTRATOR_HYBRID_INTELLIGENCE"
        self.version = "1.0.0"
        
        logger.info(f"Initialized {self.integration_name} v{self.version}")
    
    async def personalize_intent_analysis(
        self,
        user_message: str,
        user_profile: Dict[str, Any],
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> PersonalizationResult:
        """
        Personalize intent analysis based on user archetype and physiological state
        
        Args:
            user_message: User's input message
            user_profile: Complete user profile data
            conversation_context: Previous conversation context
            
        Returns:
            PersonalizationResult with personalized intent analysis
        """
        try:
            # Create personalization context for intent analysis
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="orchestrator",
                request_type="intent_analysis",
                session_data={
                    "user_message": user_message,
                    "conversation_context": conversation_context or {},
                    "analysis_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute hybrid intelligence personalization
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            logger.info(f"Intent analysis personalized for user archetype: {result.archetype_adaptation.get('user_archetype', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Error in personalized intent analysis: {e}")
            return self._create_fallback_result(user_message, "intent_analysis")
    
    async def personalize_agent_routing(
        self,
        analyzed_intent: Dict[str, Any],
        user_profile: Dict[str, Any],
        available_agents: List[str]
    ) -> PersonalizationResult:
        """
        Personalize agent routing decisions based on user archetype and needs
        
        Args:
            analyzed_intent: Results from intent analysis
            user_profile: Complete user profile data
            available_agents: List of available specialized agents
            
        Returns:
            PersonalizationResult with personalized routing decisions
        """
        try:
            # Create routing personalization context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="orchestrator",
                request_type="agent_routing",
                session_data={
                    "analyzed_intent": analyzed_intent,
                    "available_agents": available_agents,
                    "routing_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute hybrid intelligence for routing
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            logger.info(f"Agent routing personalized for {len(available_agents)} agents")
            return result
            
        except Exception as e:
            logger.error(f"Error in personalized agent routing: {e}")
            return self._create_fallback_result(analyzed_intent, "agent_routing")
    
    async def personalize_response_synthesis(
        self,
        agent_responses: Dict[str, Any],
        user_profile: Dict[str, Any],
        original_query: str
    ) -> PersonalizationResult:
        """
        Personalize response synthesis to match user communication preferences
        
        Args:
            agent_responses: Responses from specialized agents
            user_profile: Complete user profile data
            original_query: User's original query
            
        Returns:
            PersonalizationResult with personalized synthesis strategy
        """
        try:
            # Create synthesis personalization context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="orchestrator",
                request_type="response_synthesis",
                session_data={
                    "agent_responses": agent_responses,
                    "original_query": original_query,
                    "response_count": len(agent_responses),
                    "synthesis_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute hybrid intelligence for synthesis
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.ADVANCED
            )
            
            logger.info(f"Response synthesis personalized for {len(agent_responses)} agent responses")
            return result
            
        except Exception as e:
            logger.error(f"Error in personalized response synthesis: {e}")
            return self._create_fallback_result(agent_responses, "response_synthesis")
    
    async def personalize_conversation_flow(
        self,
        conversation_history: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        current_context: Dict[str, Any]
    ) -> PersonalizationResult:
        """
        Personalize conversation flow management based on user patterns
        
        Args:
            conversation_history: Previous conversation exchanges
            user_profile: Complete user profile data
            current_context: Current conversation context
            
        Returns:
            PersonalizationResult with personalized flow management
        """
        try:
            # Create flow personalization context
            context = PersonalizationContext(
                user_profile=UserProfile.from_dict(user_profile),
                agent_type="orchestrator",
                request_type="conversation_flow",
                session_data={
                    "conversation_history": conversation_history,
                    "current_context": current_context,
                    "history_length": len(conversation_history),
                    "flow_timestamp": datetime.now().isoformat()
                }
            )
            
            # Execute hybrid intelligence for flow
            result = await self.engine.personalize_for_user(
                context=context,
                mode=PersonalizationMode.STANDARD
            )
            
            logger.info(f"Conversation flow personalized with {len(conversation_history)} history items")
            return result
            
        except Exception as e:
            logger.error(f"Error in personalized conversation flow: {e}")
            return self._create_fallback_result(conversation_history, "conversation_flow")
    
    def extract_archetype_preferences(self, personalization_result: PersonalizationResult) -> Dict[str, Any]:
        """
        Extract archetype-specific preferences for orchestration decisions
        
        Args:
            personalization_result: Result from hybrid intelligence engine
            
        Returns:
            Dict with archetype preferences for orchestration
        """
        try:
            archetype_data = personalization_result.archetype_adaptation
            user_archetype = archetype_data.get('user_archetype', UserArchetype.PRIME)
            
            if user_archetype == UserArchetype.PRIME:
                return {
                    "routing_priority": "efficiency_focused",
                    "response_style": "direct_actionable",
                    "agent_coordination": "parallel_processing",
                    "synthesis_approach": "results_oriented",
                    "communication_tone": "professional_optimized"
                }
            else:  # LONGEVITY
                return {
                    "routing_priority": "holistic_comprehensive",
                    "response_style": "contextual_supportive",
                    "agent_coordination": "sequential_thorough",
                    "synthesis_approach": "wellbeing_focused",
                    "communication_tone": "nurturing_sustainable"
                }
                
        except Exception as e:
            logger.error(f"Error extracting archetype preferences: {e}")
            return self._get_default_preferences()
    
    def apply_physiological_modulation(
        self,
        base_orchestration: Dict[str, Any],
        physiological_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply physiological modulation to orchestration decisions
        
        Args:
            base_orchestration: Base orchestration strategy
            physiological_state: Current physiological markers
            
        Returns:
            Modulated orchestration strategy
        """
        try:
            # Extract key physiological indicators
            stress_level = physiological_state.get('stress_level', 'normal')
            energy_level = physiological_state.get('energy_level', 'normal')
            sleep_quality = physiological_state.get('sleep_quality', 'good')
            recovery_status = physiological_state.get('recovery_status', 'recovered')
            
            modulated = base_orchestration.copy()
            
            # Modulate based on stress level
            if stress_level == 'high':
                modulated['priority_agents'] = ['motivation_behavior_coach', 'wave_performance_analytics']
                modulated['response_urgency'] = 'supportive'
                modulated['synthesis_emphasis'] = 'stress_management'
            
            # Modulate based on energy level
            if energy_level == 'low':
                modulated['agent_count_limit'] = min(modulated.get('agent_count_limit', 3), 2)
                modulated['response_complexity'] = 'simplified'
                modulated['coordination_mode'] = 'energy_conservative'
            
            # Modulate based on recovery status
            if recovery_status == 'needs_recovery':
                modulated['mandatory_agents'] = ['wave_performance_analytics']
                modulated['focus_areas'] = ['recovery', 'rest', 'restoration']
            
            logger.info(f"Applied physiological modulation: stress={stress_level}, energy={energy_level}")
            return modulated
            
        except Exception as e:
            logger.error(f"Error applying physiological modulation: {e}")
            return base_orchestration
    
    def _create_fallback_result(self, data: Any, request_type: str) -> PersonalizationResult:
        """Create fallback result when personalization fails"""
        return PersonalizationResult(
            archetype_adaptation={
                'user_archetype': UserArchetype.PRIME,
                'adaptation_strategy': 'fallback_default',
                'request_type': request_type
            },
            physiological_modulation={
                'modulation_applied': False,
                'fallback_reason': 'personalization_error'
            },
            personalized_content={'original_data': str(data)},
            confidence_score=0.5,
            personalization_metadata={
                'fallback_mode': True,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default orchestration preferences"""
        return {
            "routing_priority": "balanced",
            "response_style": "adaptive",
            "agent_coordination": "optimal",
            "synthesis_approach": "comprehensive",
            "communication_tone": "professional"
        }


# Integration functions for easy usage
async def personalize_orchestration(
    user_message: str,
    user_profile: Dict[str, Any],
    available_agents: List[str],
    conversation_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Complete orchestration personalization workflow
    
    Args:
        user_message: User's input message
        user_profile: Complete user profile
        available_agents: Available specialized agents
        conversation_context: Previous conversation context
        
    Returns:
        Complete personalized orchestration strategy
    """
    integration = NEXUSHybridIntelligenceIntegration()
    
    try:
        # Step 1: Personalize intent analysis
        intent_result = await integration.personalize_intent_analysis(
            user_message, user_profile, conversation_context
        )
        
        # Step 2: Personalize agent routing
        routing_result = await integration.personalize_agent_routing(
            intent_result.personalized_content,
            user_profile,
            available_agents
        )
        
        # Step 3: Extract preferences
        preferences = integration.extract_archetype_preferences(routing_result)
        
        # Step 4: Apply physiological modulation
        physiological_state = user_profile.get('current_biometrics', {})
        final_strategy = integration.apply_physiological_modulation(
            preferences, physiological_state
        )
        
        return {
            'personalized_intent': intent_result.personalized_content,
            'routing_strategy': routing_result.personalized_content,
            'orchestration_preferences': final_strategy,
            'confidence_scores': {
                'intent': intent_result.confidence_score,
                'routing': routing_result.confidence_score
            },
            'metadata': {
                'archetype': routing_result.archetype_adaptation.get('user_archetype'),
                'personalization_timestamp': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in complete orchestration personalization: {e}")
        return {
            'error': str(e),
            'fallback_mode': True,
            'timestamp': datetime.now().isoformat()
        }


# Export the integration class
__all__ = ['NEXUSHybridIntelligenceIntegration', 'personalize_orchestration']