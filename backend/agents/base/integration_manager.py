"""
GENESIS NGX Agents - Hybrid Intelligence Integration Manager
===========================================================

Central manager for coordinating Hybrid Intelligence integrations across
all NGX agents. This module provides unified access and management of
agent-specific personalizations.

Features:
- Centralized agent integration registry
- Unified personalization API
- Cross-agent consistency management
- Performance monitoring and optimization

Author: Claude AI Assistant
Version: 1.0.0
Created: 2025-01-09
"""

import asyncio
from typing import Dict, List, Optional, Any, Type
from datetime import datetime
import json
import logging
from enum import Enum

# Import hybrid intelligence components
from core.hybrid_intelligence import (
    HybridIntelligenceEngine,
    UserProfile,
    PersonalizationContext,
    PersonalizationResult,
    UserArchetype,
    PersonalizationMode
)

# Import agent integrations
from agents.elite_training_strategist.hybrid_intelligence_integration import BLAZEHybridIntelligenceIntegration
from agents.precision_nutrition_architect.hybrid_intelligence_integration import SAGEHybridIntelligenceIntegration
from agents.volt_biometrics_insight_engine.hybrid_intelligence_integration import VOLTHybridIntelligenceIntegration
from agents.wave_performance_analytics.hybrid_intelligence_integration import WAVEHybridIntelligenceIntegration
from agents.nova_biohacking_innovator.hybrid_intelligence_integration import NOVAHybridIntelligenceIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Enum for NGX agent types"""
    ORCHESTRATOR = "orchestrator"
    BLAZE = "elite_training_strategist"
    SAGE = "precision_nutrition_architect"
    VOLT = "volt_biometrics_insight_engine"
    WAVE = "wave_performance_analytics"
    NOVA = "nova_biohacking_innovator"
    MOTIVATION = "motivation_behavior_coach"
    PROGRESS = "progress_tracker"
    RECOVERY = "recovery_corrective"
    CLIENT_SUCCESS = "client_success_liaison"
    FEMALE_WELLNESS = "female_wellness_coach"


class HybridIntelligenceIntegrationManager:
    """
    Central manager for Hybrid Intelligence integrations across all NGX agents.
    
    This manager provides:
    - Unified personalization API for all agents
    - Integration registry and lifecycle management
    - Cross-agent consistency and coordination
    - Performance monitoring and optimization
    """
    
    def __init__(self):
        self.hybrid_engine = HybridIntelligenceEngine()
        self.agent_integrations: Dict[str, Any] = {}
        self.integration_registry: Dict[str, Type] = {}
        self.performance_metrics: Dict[str, Any] = {}
        
        # Initialize integration registry
        self._initialize_integration_registry()
        
        # Initialize agent integrations
        self._initialize_agent_integrations()
        
        logger.info("Hybrid Intelligence Integration Manager initialized")
    
    def _initialize_integration_registry(self):
        """Initialize the registry of agent integration classes"""
        
        self.integration_registry = {
            AgentType.BLAZE: BLAZEHybridIntelligenceIntegration,
            AgentType.SAGE: SAGEHybridIntelligenceIntegration,
            AgentType.VOLT: VOLTHybridIntelligenceIntegration,
            AgentType.WAVE: WAVEHybridIntelligenceIntegration,
            AgentType.NOVA: NOVAHybridIntelligenceIntegration,
            # Additional integrations will be added as they're implemented
        }
        
        logger.info(f"Integration registry initialized with {len(self.integration_registry)} agent types")
    
    def _initialize_agent_integrations(self):
        """Initialize agent integration instances"""
        
        for agent_type, integration_class in self.integration_registry.items():
            try:
                self.agent_integrations[agent_type] = integration_class()
                logger.info(f"Initialized integration for {agent_type}")
            except Exception as e:
                logger.error(f"Failed to initialize integration for {agent_type}: {str(e)}")
    
    async def personalize_for_agent(self,
                                  agent_type: str,
                                  user_data: Dict[str, Any],
                                  request_type: str,
                                  request_content: str,
                                  session_context: Optional[Dict[str, Any]] = None,
                                  mode: PersonalizationMode = PersonalizationMode.ADVANCED) -> Dict[str, Any]:
        """
        Main method to get personalized response for any NGX agent.
        
        Args:
            agent_type: Type of agent (BLAZE, SAGE, VOLT, etc.)
            user_data: User profile and biometric data
            request_type: Type of request for the agent
            request_content: Specific content of the request
            session_context: Current session context
            mode: Personalization mode
            
        Returns:
            Personalized response with agent-specific adaptations
        """
        
        start_time = datetime.now()
        
        try:
            # Validate agent type
            if agent_type not in self.agent_integrations:
                logger.warning(f"Agent type {agent_type} not found in integrations. Using fallback.")
                return await self._fallback_personalization(agent_type, user_data, request_type, request_content)
            
            # Get agent integration
            agent_integration = self.agent_integrations[agent_type]
            
            # Perform personalization
            result = await agent_integration.personalize_response(
                user_data=user_data,
                request_type=request_type,
                request_content=request_content,
                session_context=session_context,
                mode=mode
            )
            
            # Track performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self._track_performance_metrics(agent_type, processing_time, result)
            
            # Add manager metadata
            result["integration_manager"] = {
                "agent_type": agent_type,
                "processing_time_seconds": processing_time,
                "timestamp": start_time.isoformat(),
                "manager_version": "1.0.0"
            }
            
            logger.info(f"Personalization completed for {agent_type} in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Personalization failed for {agent_type}: {str(e)}")
            return await self._fallback_personalization(agent_type, user_data, request_type, request_content)
    
    async def _fallback_personalization(self,
                                      agent_type: str,
                                      user_data: Dict[str, Any],
                                      request_type: str,
                                      request_content: str) -> Dict[str, Any]:
        """Fallback personalization when agent integration is not available"""
        
        archetype = user_data.get("archetype", "prime")
        
        return {
            "personalization_applied": False,
            "fallback_mode": True,
            "agent_type": agent_type,
            "basic_adaptations": {
                "archetype": archetype,
                "communication_style": "direct" if archetype == "prime" else "supportive",
                "intensity": "moderate",
                "approach": "standard"
            },
            "message": f"Using fallback personalization for {agent_type}",
            "integration_manager": {
                "fallback_reason": "agent_integration_unavailable",
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def _track_performance_metrics(self,
                                       agent_type: str,
                                       processing_time: float,
                                       result: Dict[str, Any]):
        """Track performance metrics for monitoring and optimization"""
        
        if agent_type not in self.performance_metrics:
            self.performance_metrics[agent_type] = {
                "total_requests": 0,
                "total_processing_time": 0.0,
                "average_processing_time": 0.0,
                "success_count": 0,
                "failure_count": 0,
                "confidence_scores": []
            }
        
        metrics = self.performance_metrics[agent_type]
        metrics["total_requests"] += 1
        metrics["total_processing_time"] += processing_time
        metrics["average_processing_time"] = metrics["total_processing_time"] / metrics["total_requests"]
        
        if result.get("personalization_applied", False):
            metrics["success_count"] += 1
            if "confidence_score" in result:
                metrics["confidence_scores"].append(result["confidence_score"])
        else:
            metrics["failure_count"] += 1
    
    def get_agent_performance_metrics(self, agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics for agents"""
        
        if agent_type:
            return self.performance_metrics.get(agent_type, {})
        
        return self.performance_metrics
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent integrations"""
        
        return list(self.agent_integrations.keys())
    
    def is_agent_available(self, agent_type: str) -> bool:
        """Check if an agent integration is available"""
        
        return agent_type in self.agent_integrations
    
    async def bulk_personalization(self,
                                 requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform bulk personalization for multiple agent requests.
        
        Args:
            requests: List of personalization requests, each containing:
                - agent_type
                - user_data
                - request_type
                - request_content
                - session_context (optional)
                - mode (optional)
                
        Returns:
            List of personalization results
        """
        
        tasks = []
        
        for request in requests:
            task = self.personalize_for_agent(
                agent_type=request["agent_type"],
                user_data=request["user_data"],
                request_type=request["request_type"],
                request_content=request["request_content"],
                session_context=request.get("session_context"),
                mode=PersonalizationMode(request.get("mode", "advanced"))
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Bulk personalization failed for request {i}: {str(result)}")
                processed_results.append({
                    "error": True,
                    "message": str(result),
                    "request_index": i
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def cross_agent_consistency_check(self,
                                          user_data: Dict[str, Any],
                                          agent_types: List[str]) -> Dict[str, Any]:
        """
        Check consistency of personalization across multiple agents.
        
        This ensures that different agents provide consistent archetype-based
        adaptations for the same user.
        """
        
        consistency_check = {
            "user_archetype": user_data.get("archetype", "unknown"),
            "agents_checked": agent_types,
            "consistency_score": 0.0,
            "inconsistencies": [],
            "recommendations": []
        }
        
        # Get base personalization for each agent
        personalizations = {}
        for agent_type in agent_types:
            if self.is_agent_available(agent_type):
                result = await self.personalize_for_agent(
                    agent_type=agent_type,
                    user_data=user_data,
                    request_type="consistency_check",
                    request_content="Check personalization consistency"
                )
                personalizations[agent_type] = result
        
        # Analyze consistency
        if len(personalizations) > 1:
            consistency_analysis = self._analyze_consistency(personalizations)
            consistency_check.update(consistency_analysis)
        
        return consistency_check
    
    def _analyze_consistency(self, personalizations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze consistency across agent personalizations"""
        
        # Extract key personalization attributes
        attributes_to_check = [
            "communication_style",
            "intensity_level",
            "archetype_alignment"
        ]
        
        inconsistencies = []
        total_checks = 0
        consistent_checks = 0
        
        # Compare each attribute across agents
        for attr in attributes_to_check:
            attr_values = {}
            
            for agent_type, personalization in personalizations.items():
                # Extract attribute value (simplified extraction)
                value = self._extract_attribute_value(personalization, attr)
                if value:
                    attr_values[agent_type] = value
            
            # Check consistency
            if len(set(attr_values.values())) > 1:
                inconsistencies.append({
                    "attribute": attr,
                    "agent_values": attr_values,
                    "issue": "inconsistent_values"
                })
            else:
                consistent_checks += 1
            
            total_checks += 1
        
        consistency_score = consistent_checks / total_checks if total_checks > 0 else 0.0
        
        return {
            "consistency_score": consistency_score,
            "inconsistencies": inconsistencies,
            "recommendations": self._generate_consistency_recommendations(inconsistencies)
        }
    
    def _extract_attribute_value(self, personalization: Dict[str, Any], attribute: str) -> Optional[str]:
        """Extract attribute value from personalization result"""
        
        # Simplified extraction logic - would be more sophisticated in practice
        if attribute == "communication_style":
            return personalization.get("communication_style", {}).get("style")
        elif attribute == "intensity_level":
            return personalization.get("communication_style", {}).get("intensity_level")
        elif attribute == "archetype_alignment":
            return personalization.get("personalization_metadata", {}).get("archetype")
        
        return None
    
    def _generate_consistency_recommendations(self, inconsistencies: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for fixing consistency issues"""
        
        recommendations = []
        
        for inconsistency in inconsistencies:
            attr = inconsistency["attribute"]
            recommendations.append(f"Review {attr} mapping across agents for consistency")
        
        if inconsistencies:
            recommendations.append("Consider updating agent adaptation configurations")
            recommendations.append("Verify archetype mappings are aligned across integrations")
        
        return recommendations
    
    async def update_agent_integration(self, agent_type: str, integration_instance: Any):
        """Update an agent integration instance"""
        
        if agent_type in self.integration_registry:
            self.agent_integrations[agent_type] = integration_instance
            logger.info(f"Updated integration for {agent_type}")
        else:
            logger.warning(f"Agent type {agent_type} not found in registry")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get overall integration status"""
        
        return {
            "total_agents": len(self.integration_registry),
            "active_integrations": len(self.agent_integrations),
            "available_agents": list(self.agent_integrations.keys()),
            "pending_integrations": [
                agent for agent in self.integration_registry.keys() 
                if agent not in self.agent_integrations
            ],
            "performance_summary": self._get_performance_summary()
        }
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all agents"""
        
        total_requests = sum(metrics.get("total_requests", 0) for metrics in self.performance_metrics.values())
        total_successes = sum(metrics.get("success_count", 0) for metrics in self.performance_metrics.values())
        
        avg_processing_times = [
            metrics.get("average_processing_time", 0) 
            for metrics in self.performance_metrics.values()
            if metrics.get("average_processing_time", 0) > 0
        ]
        
        return {
            "total_requests": total_requests,
            "success_rate": total_successes / total_requests if total_requests > 0 else 0.0,
            "average_processing_time": sum(avg_processing_times) / len(avg_processing_times) if avg_processing_times else 0.0,
            "agents_with_metrics": len(self.performance_metrics)
        }


# Singleton instance
_integration_manager = None


def get_integration_manager() -> HybridIntelligenceIntegrationManager:
    """Get singleton instance of the integration manager"""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = HybridIntelligenceIntegrationManager()
    return _integration_manager


# Export classes and functions
__all__ = [
    "HybridIntelligenceIntegrationManager",
    "AgentType",
    "get_integration_manager"
]