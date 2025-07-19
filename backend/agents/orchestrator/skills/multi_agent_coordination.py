"""
Multi-Agent Coordination Skill
==============================

Coordinates execution across multiple agents with different strategies.
"""

from typing import Dict, Any, List, Optional, Tuple
import asyncio
from datetime import datetime
import json

from agents.base.base_skill import BaseSkill
from core.logging_config import get_logger
from core.circuit_breaker import CircuitBreaker

logger = get_logger(__name__)


class MultiAgentCoordinationSkill(BaseSkill):
    """Skill for coordinating multiple agent executions."""
    
    def __init__(
        self,
        a2a_adapter,
        max_concurrent_agents: int = 5,
        timeout_per_agent: int = 30
    ):
        super().__init__(
            name="multi_agent_coordination",
            description="Coordinates execution across multiple specialized agents"
        )
        self.a2a_adapter = a2a_adapter
        self.max_concurrent_agents = max_concurrent_agents
        self.timeout_per_agent = timeout_per_agent
        self.circuit_breakers = {}  # Per-agent circuit breakers
    
    async def execute(
        self,
        agents_to_call: List[Dict[str, Any]],
        original_request: str,
        routing_strategy: str = "parallel",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute multi-agent coordination.
        
        Args:
            agents_to_call: List of agent configurations
            original_request: The original user request
            routing_strategy: "parallel", "sequential", or "priority"
            context: Additional context
            
        Returns:
            Coordination results with all agent responses
        """
        try:
            start_time = datetime.now()
            
            # Validate agents
            valid_agents = self._validate_agents(agents_to_call)
            if not valid_agents:
                return {
                    "success": False,
                    "error": "No valid agents to coordinate"
                }
            
            # Execute based on strategy
            if routing_strategy == "parallel":
                results = await self._parallel_execution(valid_agents, original_request, context)
            elif routing_strategy == "sequential":
                results = await self._sequential_execution(valid_agents, original_request, context)
            elif routing_strategy == "priority":
                results = await self._priority_execution(valid_agents, original_request, context)
            else:
                # Default to parallel
                results = await self._parallel_execution(valid_agents, original_request, context)
            
            # Process results
            successful_responses = {
                agent_id: response
                for agent_id, response in results.items()
                if response.get("success", False)
            }
            
            failed_agents = {
                agent_id: response.get("error", "Unknown error")
                for agent_id, response in results.items()
                if not response.get("success", False)
            }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": len(successful_responses) > 0,
                "responses": successful_responses,
                "failed_agents": failed_agents,
                "metadata": {
                    "strategy": routing_strategy,
                    "total_agents": len(valid_agents),
                    "successful_agents": len(successful_responses),
                    "failed_agents": len(failed_agents),
                    "execution_time": execution_time,
                    "agents_called": [agent["agent_id"] for agent in valid_agents]
                }
            }
            
        except Exception as e:
            logger.error(f"Multi-agent coordination failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "responses": {}
            }
    
    def _validate_agents(self, agents_to_call: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate agent configurations."""
        valid_agents = []
        
        for agent_config in agents_to_call:
            if not agent_config.get("agent_id"):
                continue
                
            # Add defaults if missing
            if "priority" not in agent_config:
                agent_config["priority"] = 3
            if "specific_request" not in agent_config:
                agent_config["specific_request"] = agent_config.get("request", "")
                
            valid_agents.append(agent_config)
        
        return valid_agents
    
    async def _parallel_execution(
        self,
        agents: List[Dict[str, Any]],
        original_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute agents in parallel."""
        tasks = []
        
        # Respect max concurrent limit
        semaphore = asyncio.Semaphore(self.max_concurrent_agents)
        
        async def call_with_semaphore(agent_config):
            async with semaphore:
                return await self._call_single_agent(
                    agent_config,
                    original_request,
                    context
                )
        
        # Create tasks for all agents
        for agent_config in agents:
            task = asyncio.create_task(call_with_semaphore(agent_config))
            tasks.append((agent_config["agent_id"], task))
        
        # Wait for all tasks with timeout
        results = {}
        for agent_id, task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=self.timeout_per_agent)
                results[agent_id] = result
            except asyncio.TimeoutError:
                logger.warning(f"Agent {agent_id} timed out")
                results[agent_id] = {
                    "success": False,
                    "error": "Request timed out"
                }
            except Exception as e:
                logger.error(f"Agent {agent_id} failed: {str(e)}")
                results[agent_id] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    async def _sequential_execution(
        self,
        agents: List[Dict[str, Any]],
        original_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute agents sequentially, passing results forward."""
        results = {}
        accumulated_context = context.copy() if context else {}
        
        for agent_config in agents:
            # Add previous results to context
            if results:
                accumulated_context["previous_agent_results"] = results
            
            # Call agent
            result = await self._call_single_agent(
                agent_config,
                original_request,
                accumulated_context
            )
            
            results[agent_config["agent_id"]] = result
            
            # Stop on critical failure if configured
            if not result.get("success") and agent_config.get("critical", False):
                logger.warning(f"Critical agent {agent_config['agent_id']} failed, stopping sequence")
                break
            
            # Extract insights for next agent
            if result.get("success") and result.get("response"):
                accumulated_context[f"{agent_config['agent_id']}_insights"] = (
                    self._extract_insights(result["response"])
                )
        
        return results
    
    async def _priority_execution(
        self,
        agents: List[Dict[str, Any]],
        original_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute agents by priority groups."""
        # Group agents by priority
        priority_groups = {}
        for agent in agents:
            priority = agent.get("priority", 3)
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(agent)
        
        # Execute groups in order
        all_results = {}
        accumulated_context = context.copy() if context else {}
        
        for priority in sorted(priority_groups.keys()):
            group_agents = priority_groups[priority]
            
            # Execute group in parallel
            group_results = await self._parallel_execution(
                group_agents,
                original_request,
                accumulated_context
            )
            
            all_results.update(group_results)
            
            # Add high-priority results to context for lower priority agents
            if priority <= 2:  # High priority
                for agent_id, result in group_results.items():
                    if result.get("success"):
                        accumulated_context[f"priority_{priority}_{agent_id}"] = (
                            self._extract_insights(result.get("response", {}))
                        )
        
        return all_results
    
    async def _call_single_agent(
        self,
        agent_config: Dict[str, Any],
        original_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call a single agent with circuit breaker protection."""
        agent_id = agent_config["agent_id"]
        
        # Get or create circuit breaker for this agent
        if agent_id not in self.circuit_breakers:
            self.circuit_breakers[agent_id] = CircuitBreaker(
                failure_threshold=3,
                recovery_timeout=60,
                expected_exception=Exception
            )
        
        circuit_breaker = self.circuit_breakers[agent_id]
        
        try:
            # Check circuit breaker
            if not circuit_breaker.call_allowed():
                return {
                    "success": False,
                    "error": "Agent temporarily unavailable (circuit breaker open)"
                }
            
            # Prepare request
            specific_request = agent_config.get("specific_request") or original_request
            
            # Build agent context
            agent_context = {
                "original_request": original_request,
                "routing_metadata": {
                    "priority": agent_config.get("priority", 3),
                    "expected_output": agent_config.get("expected_output", "general response")
                }
            }
            
            if context:
                agent_context.update(context)
            
            # Call agent via A2A
            response = await self.a2a_adapter.call_agent(
                agent_id=agent_id,
                task_input={
                    "request": specific_request,
                    "context": agent_context
                },
                timeout=self.timeout_per_agent
            )
            
            # Record success
            circuit_breaker.record_success()
            
            # Process response
            if response.get("status") == "completed":
                return {
                    "success": True,
                    "response": response.get("output", {}),
                    "metadata": {
                        "execution_time": response.get("execution_time"),
                        "model_used": response.get("metadata", {}).get("model")
                    }
                }
            else:
                circuit_breaker.record_failure()
                return {
                    "success": False,
                    "error": response.get("error", "Agent execution failed")
                }
                
        except Exception as e:
            circuit_breaker.record_failure()
            logger.error(f"Error calling agent {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_insights(self, response: Any) -> Dict[str, Any]:
        """Extract key insights from agent response for context passing."""
        insights = {}
        
        if isinstance(response, dict):
            # Extract specific fields that might be useful
            for key in ["recommendations", "analysis", "key_points", "summary", "plan"]:
                if key in response:
                    insights[key] = response[key]
            
            # Extract metrics if present
            if "metrics" in response:
                insights["metrics"] = response["metrics"]
            
            # Extract any structured data
            for key, value in response.items():
                if isinstance(value, (list, dict)) and key not in insights:
                    insights[key] = value
        
        elif isinstance(response, str):
            # For text responses, just note it exists
            insights["text_response"] = response[:200] + "..." if len(response) > 200 else response
        
        return insights
    
    def get_circuit_breaker_status(self) -> Dict[str, str]:
        """Get status of all circuit breakers."""
        status = {}
        for agent_id, cb in self.circuit_breakers.items():
            if cb.current_state == cb.State.CLOSED:
                status[agent_id] = "healthy"
            elif cb.current_state == cb.State.OPEN:
                status[agent_id] = "unavailable"
            else:
                status[agent_id] = "recovering"
        return status