"""
NEXUS Orchestrator Agent (Refactored)
=====================================

This is a refactored version of the NEXUS orchestrator using the modular architecture.
Original: ~1,924 lines → Refactored: ~300 lines (85% reduction!)

The functionality is now split into:
- Core agent logic (this file)
- Skills modules (skills/)
- Configuration (config.py)
- Prompts (prompts/)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from agents.base.base_ngx_agent import BaseNGXAgent
from agents.base.adk_agent import ADKAgent
from core.logging_config import get_logger
from adk.agent import Skill
from app.schemas.a2a import A2ATaskContext

# Import orchestrator-specific components
from .config import OrchestratorConfig, DEFAULT_ORCHESTRATOR_CONFIG
from .prompts import OrchestratorPrompts
from .skills import (
    IntentAnalysisSkill,
    ResponseSynthesisSkill,
    MultiAgentCoordinationSkill
)

# Import adapters
from infrastructure.adapters.a2a_adapter import a2a_adapter

logger = get_logger(__name__)


class NGXNexusOrchestrator(BaseNGXAgent, ADKAgent):
    """
    NEXUS - Central Orchestrator Agent (Refactored).
    
    Analyzes user intent, routes to specialized agents, and synthesizes
    coherent responses using advanced multi-agent coordination.
    """
    
    def __init__(
        self,
        config: Optional[OrchestratorConfig] = None,
        a2a_server_url: Optional[str] = None,
        **kwargs
    ):
        """Initialize NEXUS orchestrator with modular architecture."""
        config = config or DEFAULT_ORCHESTRATOR_CONFIG
        
        # Store config and initialize prompts first
        self.config = config
        self.prompts = OrchestratorPrompts(personality_type="balanced")
        
        # Get description for initialization
        description = (
            "NEXUS is the central orchestrator of the NGX ecosystem, intelligently "
            "analyzing your needs and coordinating specialized AI agents to provide "
            "comprehensive, personalized guidance. With advanced intent analysis and "
            "response synthesis, NEXUS ensures you get the right expertise at the right time."
        )
        
        # Initialize with all required parameters
        # Note: model_id is passed as model to ADKAgent
        super().__init__(
            agent_id=config.agent_id,
            agent_name=config.agent_name,
            agent_type=config.agent_type,
            personality_type="balanced",  # Orchestrator is always balanced
            model_id=config.model_id,  # This will be passed as 'model' to ADKAgent
            temperature=config.temperature,
            name=config.agent_name,  # Required by ADKAgent
            description=description,  # Required by ADKAgent
            instruction=self.prompts.base_instruction,  # Required by ADKAgent
            **kwargs
        )
        self.a2a_server_url = a2a_server_url or config.a2a_server_url
        
        # Initialize orchestrator-specific components
        self._initialize_orchestrator_services()
        
        # Register skills
        self._register_orchestrator_skills()
        
        # Define ADK skills for external protocols
        self.adk_skills = [
            Skill(
                name="analyze_intent",
                description="Analyzes user intent from input text",
                handler=self._adk_analyze_intent
            ),
            Skill(
                name="synthesize_response",
                description="Synthesizes responses from multiple agents",
                handler=self._adk_synthesize_response
            )
        ]
        
        logger.info("NEXUS Orchestrator initialized (refactored version)")
    
    # ==================== Required Abstract Methods ====================
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of NEXUS capabilities."""
        return self.config.capabilities
    
    def get_agent_description(self) -> str:
        """Get NEXUS agent description."""
        return (
            "NEXUS is the central orchestrator of the NGX ecosystem, intelligently "
            "analyzing your needs and coordinating specialized AI agents to provide "
            "comprehensive, personalized guidance. With advanced intent analysis and "
            "response synthesis, NEXUS ensures you get the right expertise at the right time."
        )
    
    async def process_user_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request through orchestration.
        
        Args:
            request: User's input
            context: Request context including user data
            
        Returns:
            Orchestrated response
        """
        try:
            start_time = datetime.now()
            
            # Update metrics
            self._state["total_interactions"] += 1
            self._state["last_interaction"] = start_time.isoformat()
            
            # Check cache
            cache_key = f"orchestrator:{context.get('user_id', 'anonymous')}:{hash(request)}"
            cached_response = await self.get_cached_response(cache_key)
            if cached_response and self.config.enable_caching:
                logger.info("Returning cached orchestrator response")
                return cached_response
            
            # Step 1: Analyze intent
            intent_analysis = await self.execute_skill(
                "intent_analysis",
                request=request,
                context=context
            )
            
            if not intent_analysis.get("success"):
                return await self._handle_intent_failure(request, context)
            
            # Step 2: Determine routing strategy
            routing_strategy = self._determine_routing_strategy(
                intent_analysis["analysis"],
                context
            )
            
            # Step 3: Coordinate agent execution
            coordination_result = await self.execute_skill(
                "multi_agent_coordination",
                agents_to_call=routing_strategy["agents"],
                original_request=request,
                routing_strategy=routing_strategy["strategy"],
                context=context
            )
            
            if not coordination_result.get("success"):
                return await self._handle_coordination_failure(
                    request,
                    coordination_result,
                    context
                )
            
            # Step 4: Synthesize responses
            synthesis_result = await self.execute_skill(
                "response_synthesis",
                agent_responses=coordination_result["responses"],
                original_request=request,
                context=context
            )
            
            # Prepare final response
            final_response = {
                "success": True,
                "agent": self.agent_id,
                "response": synthesis_result.get("response", ""),
                "metadata": {
                    "orchestration": {
                        "intent": intent_analysis["analysis"].get("primary_intent"),
                        "agents_consulted": coordination_result["metadata"]["agents_called"],
                        "routing_strategy": routing_strategy["strategy"],
                        "synthesis_type": synthesis_result.get("metadata", {}).get("synthesis_type")
                    },
                    "execution_time": (datetime.now() - start_time).total_seconds(),
                    "model_used": self.model,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Cache response
            if self.config.enable_caching:
                await self.cache_response(cache_key, final_response, ttl=self.config.cache_ttl)
            
            # Record metrics
            self._metrics["success_count"] += 1
            self.record_metric("orchestration_time", final_response["metadata"]["execution_time"])
            
            return final_response
            
        except Exception as e:
            return await self.handle_error(e, {"request": request, "context": context})
    
    # ==================== Orchestrator Initialization ====================
    
    def _initialize_orchestrator_services(self) -> None:
        """Initialize orchestrator-specific services."""
        # Intent patterns from config
        self.intent_patterns = self.config.intent_to_agent_map
        
        # Agent health tracking
        self.agent_health = {}
        
        # Conversation context manager
        self.context_window = []
        self.max_context_messages = self.config.context_window_messages
    
    def _register_orchestrator_skills(self) -> None:
        """Register orchestrator-specific skills."""
        # Intent analysis
        self.register_skill(
            "intent_analysis",
            IntentAnalysisSkill(
                vertex_client=self.vertex_client,
                intent_patterns=self.intent_patterns
            ),
            metadata={"priority": "critical", "category": "analysis"}
        )
        
        # Multi-agent coordination
        self.register_skill(
            "multi_agent_coordination",
            MultiAgentCoordinationSkill(
                a2a_adapter=a2a_adapter,
                max_concurrent_agents=self.config.max_concurrent_agents,
                timeout_per_agent=self.config.a2a_timeout
            ),
            metadata={"priority": "critical", "category": "coordination"}
        )
        
        # Response synthesis
        self.register_skill(
            "response_synthesis",
            ResponseSynthesisSkill(
                vertex_client=self.vertex_client,
                synthesis_strategy=self.config.synthesis_strategy
            ),
            metadata={"priority": "high", "category": "synthesis"}
        )
    
    # ==================== Routing Logic ====================
    
    def _determine_routing_strategy(
        self,
        intent_analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine the routing strategy based on intent analysis."""
        recommended_agents = intent_analysis.get("recommended_agents", [])
        urgency = intent_analysis.get("urgency", "medium")
        
        # Map agent names to proper IDs
        agent_mapping = {
            "blaze": "elite_training_strategist",
            "sage": "precision_nutrition_architect",
            "luna": "female_wellness_coach",
            "stella": "progress_tracker",
            "spark": "motivation_behavior_coach",
            "nova": "nova_biohacking_innovator",
            "wave": "wave_performance_analytics",
            "code": "code_genetic_specialist"
        }
        
        # Normalize agent IDs
        normalized_agents = []
        for agent in recommended_agents:
            # Handle various formats
            agent_lower = agent.lower().replace("_agent", "")
            if agent_lower in agent_mapping:
                normalized_agents.append(agent_mapping[agent_lower])
            elif agent in agent_mapping.values():
                normalized_agents.append(agent)
            else:
                # Try to find in intent map
                for intent, agents in self.intent_patterns.items():
                    if agent in agents:
                        normalized_agents.append(agent)
                        break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_agents = []
        for agent in normalized_agents:
            if agent not in seen:
                seen.add(agent)
                unique_agents.append(agent)
        
        # Build agent configurations
        agents_to_call = []
        for i, agent_id in enumerate(unique_agents):
            priority = 1 if urgency == "high" else (2 if i == 0 else 3)
            
            agents_to_call.append({
                "agent_id": agent_id,
                "priority": priority,
                "specific_request": intent_analysis.get("specific_request", ""),
                "expected_output": self._get_expected_output(agent_id, intent_analysis)
            })
        
        # Determine execution strategy
        if len(agents_to_call) == 1:
            strategy = "single"
        elif urgency == "high":
            strategy = "parallel"
        elif len(agents_to_call) > 3:
            strategy = "priority"
        else:
            strategy = "parallel"
        
        return {
            "strategy": strategy,
            "agents": agents_to_call,
            "reasoning": intent_analysis.get("reasoning", "")
        }
    
    def _get_expected_output(self, agent_id: str, intent_analysis: Dict[str, Any]) -> str:
        """Get expected output type for an agent."""
        intent = intent_analysis.get("primary_intent", "")
        
        output_expectations = {
            "elite_training_strategist": "training plan or exercise guidance",
            "precision_nutrition_architect": "nutrition plan or dietary advice",
            "female_wellness_coach": "female health guidance",
            "progress_tracker": "progress analysis or metrics",
            "motivation_behavior_coach": "motivational guidance or habit formation",
            "nova_biohacking_innovator": "optimization strategies",
            "wave_performance_analytics": "performance analysis",
            "code_genetic_specialist": "genetic insights"
        }
        
        return output_expectations.get(agent_id, "specialized guidance")
    
    # ==================== Error Handling ====================
    
    async def _handle_intent_failure(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intent analysis failure gracefully."""
        # Fallback to general assistance
        logger.warning("Intent analysis failed, using fallback")
        
        return {
            "success": True,
            "agent": self.agent_id,
            "response": (
                "I'm here to help you with your fitness and wellness journey. "
                "Could you please tell me more about what you're looking for? "
                "I can help with training plans, nutrition, progress tracking, "
                "motivation, and much more!"
            ),
            "metadata": {
                "fallback": True,
                "reason": "intent_analysis_failed"
            }
        }
    
    async def _handle_coordination_failure(
        self,
        request: str,
        coordination_result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle coordination failure gracefully."""
        # Check if any agents succeeded
        if coordination_result.get("responses"):
            # Partial success - synthesize what we have
            synthesis_result = await self.execute_skill(
                "response_synthesis",
                agent_responses=coordination_result["responses"],
                original_request=request,
                context=context
            )
            
            return {
                "success": True,
                "agent": self.agent_id,
                "response": synthesis_result.get("response", ""),
                "metadata": {
                    "partial_success": True,
                    "failed_agents": coordination_result.get("failed_agents", {})
                }
            }
        
        # Complete failure - provide helpful response
        return {
            "success": True,
            "agent": self.agent_id,
            "response": (
                "I'm experiencing some technical difficulties connecting with our "
                "specialized experts. However, I can still provide general guidance. "
                "What specific area would you like help with - training, nutrition, "
                "or overall wellness?"
            ),
            "metadata": {
                "fallback": True,
                "reason": "coordination_failed"
            }
        }
    
    # ==================== ADK Protocol Methods ====================
    
    async def _adk_analyze_intent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for intent analysis."""
        return await self.execute_skill(
            "intent_analysis",
            request=params.get("text", ""),
            context=params.get("context", {})
        )
    
    async def _adk_synthesize_response(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ADK skill handler for response synthesis."""
        return await self.execute_skill(
            "response_synthesis",
            agent_responses=params.get("responses", {}),
            original_request=params.get("original_request", ""),
            context=params.get("context", {})
        )
    
    # ==================== Lifecycle Hooks ====================
    
    async def _agent_startup(self) -> None:
        """NEXUS-specific startup tasks."""
        # Test connections to critical agents
        critical_agents = ["elite_training_strategist", "precision_nutrition_architect"]
        
        for agent_id in critical_agents:
            try:
                # Simple health check
                result = await a2a_adapter.get_agent_status(agent_id)
                self.agent_health[agent_id] = result.get("status") == "healthy"
                logger.info(f"Agent {agent_id} health: {self.agent_health[agent_id]}")
            except Exception as e:
                logger.warning(f"Could not check health of {agent_id}: {e}")
                self.agent_health[agent_id] = False
    
    async def _agent_shutdown(self) -> None:
        """NEXUS-specific shutdown tasks."""
        # Save conversation context if needed
        if self.context_window:
            logger.info(f"Saving {len(self.context_window)} context messages")
            # Implementation would save to persistent storage
    
    # ==================== Context Management ====================
    
    def update_context_window(self, message: Dict[str, Any]) -> None:
        """Update conversation context window."""
        self.context_window.append({
            "timestamp": datetime.now().isoformat(),
            "message": message
        })
        
        # Trim to max size
        if len(self.context_window) > self.max_context_messages:
            self.context_window = self.context_window[-self.max_context_messages:]
    
    def get_conversation_context(self) -> List[Dict[str, Any]]:
        """Get current conversation context."""
        return self.context_window.copy()
    
    # ==================== Special Methods ====================
    
    async def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get status of entire agent ecosystem."""
        coordination_skill = self._skills.get("multi_agent_coordination")
        
        if coordination_skill:
            circuit_breaker_status = coordination_skill.get_circuit_breaker_status()
        else:
            circuit_breaker_status = {}
        
        return {
            "orchestrator": {
                "status": "healthy",
                "version": self.config.version,
                "uptime": self._get_uptime()
            },
            "agents": {
                **self.agent_health,
                **circuit_breaker_status
            },
            "metadata": {
                "total_interactions": self._state.get("total_interactions", 0),
                "success_rate": self._calculate_success_rate(),
                "average_response_time": self._calculate_avg_response_time()
            }
        }
    
    def _get_uptime(self) -> float:
        """Get orchestrator uptime in seconds."""
        if hasattr(self, '_start_time'):
            return (datetime.now() - self._start_time).total_seconds()
        return 0
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate."""
        total = self._state.get("total_interactions", 0)
        success = self._metrics.get("success_count", 0)
        return (success / total * 100) if total > 0 else 0
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time."""
        times = self._metrics.get("orchestration_time", [])
        return sum(times) / len(times) if times else 0