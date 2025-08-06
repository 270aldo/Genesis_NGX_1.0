"""
Agent Simulator for A2A integration testing.

Simulates agent behavior without requiring actual AI models or complex logic.
"""

import asyncio
import json
import random
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from core.logging_config import get_logger

logger = get_logger(__name__)


class SimulatedAgent:
    """
    Simulates an agent for testing purposes.

    Features:
    - Predefined responses
    - Configurable delays
    - Error simulation
    - Response validation
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        name: str,
        description: str,
        response_delay: float = 0.1,
        error_rate: float = 0.0,
    ):
        """
        Initialize simulated agent.

        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (e.g., 'orchestrator', 'elite_training')
            name: Agent display name
            description: Agent description
            response_delay: Simulated processing delay in seconds
            error_rate: Probability of simulating an error (0.0-1.0)
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.response_delay = response_delay
        self.error_rate = error_rate
        self.message_count = 0
        self.error_count = 0
        self.responses = self._initialize_responses()
        self.custom_handlers: Dict[str, Callable] = {}

    def _initialize_responses(self) -> Dict[str, Any]:
        """Initialize agent-specific response templates."""
        responses = {
            "orchestrator": {
                "default": "I'll coordinate the appropriate agents to help you.",
                "routing": {
                    "training": ["elite_training_strategist"],
                    "nutrition": ["precision_nutrition_architect"],
                    "both": [
                        "elite_training_strategist",
                        "precision_nutrition_architect",
                    ],
                    "health": ["genetic_specialist", "biohacking_innovator"],
                    "motivation": ["motivation_behavior_coach"],
                },
            },
            "elite_training_strategist": {
                "default": "Here's your personalized training plan.",
                "plans": [
                    "Week 1: Foundation building with 3x/week full body workouts",
                    "Focus on compound movements: squats, deadlifts, bench press",
                    "Progressive overload: increase weight by 5% weekly",
                ],
            },
            "precision_nutrition_architect": {
                "default": "I've analyzed your nutritional needs.",
                "recommendations": [
                    "Daily protein: 1.6-2.2g per kg body weight",
                    "Meal timing: 3-4 hours between meals",
                    "Hydration: 35-40ml per kg body weight",
                ],
            },
            "motivation_behavior_coach": {
                "default": "I understand you're feeling frustrated. Let's work through this together.",
                "strategies": [
                    "Set small, achievable daily goals",
                    "Track your progress visually",
                    "Celebrate small wins consistently",
                ],
            },
            "genetic_specialist": {
                "default": "Based on genetic analysis, here are your insights.",
                "insights": [
                    "ACTN3 variant suggests good power/speed potential",
                    "Consider higher protein intake based on metabolism",
                    "Recovery may take longer - plan rest days accordingly",
                ],
            },
        }

        # Return agent-specific responses or generic ones
        return responses.get(
            self.agent_type,
            {
                "default": f"Response from {self.name}",
                "data": {"agent_id": self.agent_id, "type": self.agent_type},
            },
        )

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message and generate a response.

        Args:
            message: Incoming message dictionary

        Returns:
            Response dictionary
        """
        self.message_count += 1
        start_time = datetime.now()

        # Simulate processing delay
        await asyncio.sleep(self.response_delay)

        # Simulate random errors
        if random.random() < self.error_rate:
            self.error_count += 1
            logger.warning(f"Simulated error in {self.agent_id}")
            return {
                "status": "error",
                "error": f"Simulated error in {self.agent_id}",
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
            }

        # Check for custom handler
        user_input = message.get("user_input", "").lower()
        for keyword, handler in self.custom_handlers.items():
            if keyword in user_input:
                response_content = (
                    await handler(message)
                    if asyncio.iscoroutinefunction(handler)
                    else handler(message)
                )
                return self._format_response(response_content, start_time)

        # Generate response based on agent type
        if self.agent_type == "orchestrator":
            response_content = self._generate_orchestrator_response(message)
        else:
            response_content = self._generate_agent_response(message)

        return self._format_response(response_content, start_time)

    def _generate_orchestrator_response(
        self, message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate orchestrator-specific response."""
        user_input = message.get("user_input", "").lower()

        # Determine which agents to route to
        agents_to_call = []
        if "training" in user_input or "exercise" in user_input:
            agents_to_call.extend(self.responses["routing"]["training"])
        if "nutrition" in user_input or "diet" in user_input:
            agents_to_call.extend(self.responses["routing"]["nutrition"])
        if "genetic" in user_input or "dna" in user_input:
            agents_to_call.extend(self.responses["routing"]["health"])
        if "motivat" in user_input or "frustrat" in user_input:
            agents_to_call.extend(self.responses["routing"]["motivation"])

        if not agents_to_call:
            agents_to_call = ["elite_training_strategist"]  # Default

        return {
            "content": self.responses["default"],
            "agents_to_call": list(set(agents_to_call)),  # Remove duplicates
            "routing_decision": {
                "confidence": 0.85,
                "reasoning": f"Detected keywords related to {', '.join(agents_to_call)}",
            },
        }

    def _generate_agent_response(self, message: Dict[str, Any]) -> Any:
        """Generate agent-specific response."""
        # Return appropriate response based on agent type
        response_data = {
            "content": self.responses.get("default", f"Response from {self.name}")
        }

        # Add agent-specific data
        if "plans" in self.responses:
            response_data["training_plan"] = self.responses["plans"]
        elif "recommendations" in self.responses:
            response_data["nutrition_advice"] = self.responses["recommendations"]
        elif "strategies" in self.responses:
            response_data["motivation_tips"] = self.responses["strategies"]
        elif "insights" in self.responses:
            response_data["genetic_insights"] = self.responses["insights"]

        return response_data

    def _format_response(self, content: Any, start_time: datetime) -> Dict[str, Any]:
        """Format the response with metadata."""
        processing_time = (datetime.now() - start_time).total_seconds()

        return {
            "status": "success",
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "agent_type": self.agent_type,
            "content": content if isinstance(content, str) else json.dumps(content),
            "response_data": (
                content if isinstance(content, dict) else {"text": content}
            ),
            "metadata": {
                "processing_time": processing_time,
                "message_count": self.message_count,
                "timestamp": datetime.now().isoformat(),
            },
        }

    def add_custom_handler(self, keyword: str, handler: Callable):
        """Add a custom response handler for specific keywords."""
        self.custom_handlers[keyword] = handler
        logger.debug(f"Added custom handler for '{keyword}' in {self.agent_id}")

    def set_error_rate(self, rate: float):
        """Update error simulation rate."""
        self.error_rate = max(0.0, min(1.0, rate))

    def set_response_delay(self, delay: float):
        """Update response delay."""
        self.response_delay = max(0.0, delay)

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "messages_processed": self.message_count,
            "errors_simulated": self.error_count,
            "error_rate": self.error_rate,
            "average_delay": self.response_delay,
        }


class AgentSimulator:
    """
    Manager for multiple simulated agents.
    """

    def __init__(self):
        """Initialize agent simulator."""
        self.agents: Dict[str, SimulatedAgent] = {}
        self._initialize_default_agents()

    def _initialize_default_agents(self):
        """Initialize the standard GENESIS agents."""
        default_agents = [
            (
                "orchestrator",
                "orchestrator",
                "NEXUS Orchestrator",
                "Coordinates all agents",
            ),
            (
                "elite_training_strategist",
                "elite_training_strategist",
                "BLAZE Elite Training",
                "Training plans",
            ),
            (
                "precision_nutrition_architect",
                "precision_nutrition_architect",
                "SAGE Nutrition",
                "Nutrition guidance",
            ),
            (
                "motivation_behavior_coach",
                "motivation_behavior_coach",
                "SPARK Motivation",
                "Behavioral coaching",
            ),
            (
                "genetic_specialist",
                "genetic_specialist",
                "CODE Genetic",
                "Genetic insights",
            ),
            (
                "performance_analytics",
                "performance_analytics",
                "WAVE Analytics",
                "Performance tracking",
            ),
            (
                "female_wellness_coach",
                "female_wellness_coach",
                "LUNA Wellness",
                "Female health",
            ),
            (
                "progress_tracker",
                "progress_tracker",
                "STELLA Progress",
                "Progress monitoring",
            ),
            (
                "biohacking_innovator",
                "biohacking_innovator",
                "NOVA Biohacking",
                "Optimization protocols",
            ),
            ("guardian", "guardian", "GUARDIAN Security", "Security and compliance"),
            ("node", "node", "NODE Integration", "System integration"),
        ]

        for agent_id, agent_type, name, desc in default_agents:
            self.add_agent(
                SimulatedAgent(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    name=name,
                    description=desc,
                    response_delay=random.uniform(0.05, 0.15),  # 50-150ms
                )
            )

    def add_agent(self, agent: SimulatedAgent):
        """Add a simulated agent."""
        self.agents[agent.agent_id] = agent
        logger.info(f"Added simulated agent: {agent.agent_id}")

    def get_agent(self, agent_id: str) -> Optional[SimulatedAgent]:
        """Get a specific agent."""
        return self.agents.get(agent_id)

    def set_global_error_rate(self, rate: float):
        """Set error rate for all agents."""
        for agent in self.agents.values():
            agent.set_error_rate(rate)

    def set_global_delay(self, delay: float):
        """Set response delay for all agents."""
        for agent in self.agents.values():
            agent.set_response_delay(delay)

    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all agents."""
        return {agent_id: agent.get_stats() for agent_id, agent in self.agents.items()}

    async def register_all_with_server(self, test_server):
        """Register all simulated agents with a test server."""
        for agent in self.agents.values():

            def handler(msg, a=agent):
                return a.process_message(msg)

            await test_server.register_test_agent(agent.agent_id, handler)

        logger.info(f"Registered {len(self.agents)} simulated agents with test server")
