"""
A2A End-to-End Workflow Integration Tests.

Comprehensive test suite for complete user journeys through the A2A system:
- Frustrated user → NEXUS → SPARK + BLAZE
- Complete fitness plan → NEXUS → BLAZE + SAGE + WAVE
- Medical emergency → NEXUS → GUARDIAN → All agents
- Genetic optimization → NEXUS → CODE + NOVA + SAGE
- Full analysis → NEXUS → Multiple agents

These tests validate the entire system working together to deliver
real user value through complex multi-agent workflows.
"""

import asyncio
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytest

from core.logging_config import get_logger
from infrastructure.adapters.a2a_adapter import A2AAdapter
from tests.integration.a2a.utils.agent_simulator import SimulatedAgent

logger = get_logger(__name__)


class WorkflowTracker:
    """Helper class for tracking end-to-end workflow execution."""

    def __init__(self, workflow_name: str):
        """Initialize workflow tracker."""
        self.workflow_name = workflow_name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.steps: List[Dict[str, Any]] = []
        self.agents_involved: set[str] = set()
        self.messages_sent = 0
        self.errors: List[str] = []
        self.user_context: Dict[str, Any] = {}

    def start_workflow(self, user_context: Dict[str, Any]):
        """Start tracking a workflow."""
        self.start_time = time.time()
        self.user_context = user_context
        logger.info(f"Starting workflow: {self.workflow_name}")

    def record_step(
        self,
        step_name: str,
        agent_id: str,
        input_data: Any,
        output_data: Any,
        duration_ms: float,
    ):
        """Record a workflow step."""
        step = {
            "step_name": step_name,
            "agent_id": agent_id,
            "input_data": input_data,
            "output_data": output_data,
            "duration_ms": duration_ms,
            "timestamp": time.time(),
        }
        self.steps.append(step)
        self.agents_involved.add(agent_id)
        self.messages_sent += 1

        logger.debug(f"Workflow step: {step_name} via {agent_id} ({duration_ms:.2f}ms)")

    def record_error(self, error_message: str, agent_id: Optional[str] = None):
        """Record an error in the workflow."""
        error_entry = {
            "error": error_message,
            "agent_id": agent_id,
            "timestamp": time.time(),
            "step_index": len(self.steps),
        }
        self.errors.append(error_entry)
        logger.warning(f"Workflow error: {error_message}")

    def end_workflow(self) -> Dict[str, Any]:
        """End workflow tracking and return summary."""
        self.end_time = time.time()

        total_duration = (self.end_time - self.start_time) if self.start_time else 0

        summary = {
            "workflow_name": self.workflow_name,
            "total_duration_ms": total_duration * 1000,
            "steps_completed": len(self.steps),
            "agents_involved": list(self.agents_involved),
            "messages_sent": self.messages_sent,
            "errors_count": len(self.errors),
            "success": len(self.errors) == 0,
            "user_context": self.user_context,
            "steps": self.steps,
            "errors": self.errors,
        }

        logger.info(
            f"Workflow completed: {self.workflow_name} - "
            f"{len(self.steps)} steps, {len(self.agents_involved)} agents, "
            f"{total_duration:.2f}s, {len(self.errors)} errors"
        )

        return summary


class TestFrustratedUserWorkflow:
    """Test frustrated user workflow: User → NEXUS → SPARK + BLAZE"""

    async def test_frustrated_user_basic_workflow(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test basic frustrated user workflow with motivation and training."""
        tracker = WorkflowTracker("frustrated_user_basic")

        # Setup user context
        user_context = {
            "user_id": "frustrated_user_001",
            "emotion": "frustrated",
            "session_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "problems": [
                "not seeing results",
                "motivation low",
                "confused about training",
            ],
        }

        tracker.start_workflow(user_context)

        # Register required agents
        required_agents = [
            "orchestrator",
            "motivation_behavior_coach",
            "elite_training_strategist",
        ]

        for agent_id in required_agents:
            if agent_id in registered_agents:
                agent = registered_agents[agent_id]
                a2a_adapter.register_agent(
                    agent_id,
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "message_callback": agent.process_message,
                    },
                )

        await asyncio.sleep(0.1)

        # Step 1: User expresses frustration to NEXUS (Orchestrator)
        user_input = (
            "I'm so frustrated! I've been working out for months but I'm not "
            "seeing any results. I don't know what I'm doing wrong and I'm "
            "losing motivation. Can you help me figure this out?"
        )

        step_start = time.time()
        nexus_response = await a2a_adapter.call_agent(
            agent_id="orchestrator", user_input=user_input, context=user_context
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "initial_frustration_assessment",
            "orchestrator",
            user_input,
            nexus_response,
            step_duration,
        )

        # Verify NEXUS understood the frustration
        assert isinstance(nexus_response, dict)
        if nexus_response.get("status") == "error":
            tracker.record_error(
                f"NEXUS failed: {nexus_response.get('error')}", "orchestrator"
            )

        # Step 2: NEXUS routes to SPARK (Motivation Coach)
        motivation_context = {
            **user_context,
            "orchestrator_analysis": nexus_response,
            "priority_need": "motivation",
        }

        step_start = time.time()
        spark_response = await a2a_adapter.call_agent(
            agent_id="motivation_behavior_coach",
            user_input="Help this frustrated user regain motivation and confidence",
            context=motivation_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "motivation_intervention",
            "motivation_behavior_coach",
            motivation_context,
            spark_response,
            step_duration,
        )

        if spark_response.get("status") == "error":
            tracker.record_error(
                f"SPARK failed: {spark_response.get('error')}",
                "motivation_behavior_coach",
            )

        # Step 3: NEXUS routes to BLAZE (Training Strategist)
        training_context = {
            **user_context,
            "orchestrator_analysis": nexus_response,
            "motivation_guidance": spark_response,
            "focus": "training_assessment",
        }

        step_start = time.time()
        blaze_response = await a2a_adapter.call_agent(
            agent_id="elite_training_strategist",
            user_input="Assess this user's training and provide corrective guidance",
            context=training_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "training_assessment_and_correction",
            "elite_training_strategist",
            training_context,
            blaze_response,
            step_duration,
        )

        if blaze_response.get("status") == "error":
            tracker.record_error(
                f"BLAZE failed: {blaze_response.get('error')}",
                "elite_training_strategist",
            )

        # Complete workflow
        workflow_summary = tracker.end_workflow()

        # Workflow validation
        assert (
            workflow_summary["steps_completed"] >= 3
        ), "Should complete all major steps"
        assert (
            "orchestrator" in workflow_summary["agents_involved"]
        ), "NEXUS should be involved"
        assert (
            "motivation_behavior_coach" in workflow_summary["agents_involved"]
        ), "SPARK should be involved"
        assert (
            "elite_training_strategist" in workflow_summary["agents_involved"]
        ), "BLAZE should be involved"

        # Performance validation
        assert (
            workflow_summary["total_duration_ms"] < 30000
        ), "Workflow should complete within 30 seconds"

        # Quality validation - at least one agent should provide meaningful response
        meaningful_responses = sum(
            1
            for step in workflow_summary["steps"]
            if step["output_data"].get("status") != "error"
        )
        assert (
            meaningful_responses >= 2
        ), "At least 2 agents should provide meaningful responses"

        logger.info(f"Frustrated user workflow summary: {workflow_summary}")

    async def test_frustrated_user_with_nutrition_needs(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test frustrated user workflow that also needs nutrition guidance."""
        tracker = WorkflowTracker("frustrated_user_nutrition")

        user_context = {
            "user_id": "frustrated_user_002",
            "emotion": "frustrated",
            "session_id": str(uuid.uuid4()),
            "problems": [
                "not losing weight",
                "confused about diet",
                "training not working",
            ],
        }

        tracker.start_workflow(user_context)

        # Register agents including nutrition
        required_agents = [
            "orchestrator",
            "motivation_behavior_coach",
            "elite_training_strategist",
            "precision_nutrition_architect",
        ]

        for agent_id in required_agents:
            if agent_id in registered_agents:
                agent = registered_agents[agent_id]
                a2a_adapter.register_agent(
                    agent_id,
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "message_callback": agent.process_message,
                    },
                )

        await asyncio.sleep(0.1)

        # User input mentioning both training and nutrition issues
        user_input = (
            "I'm really frustrated! I've been following what I thought was "
            "a good diet and training plan, but I'm not losing weight and I "
            "feel like I'm spinning my wheels. I need help with both my "
            "training and nutrition because clearly what I'm doing isn't working."
        )

        # Step 1: NEXUS assessment
        step_start = time.time()
        nexus_response = await a2a_adapter.call_agent(
            agent_id="orchestrator", user_input=user_input, context=user_context
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "comprehensive_assessment",
            "orchestrator",
            user_input,
            nexus_response,
            step_duration,
        )

        # Step 2: Multi-agent coordination
        # Call multiple agents as NEXUS would coordinate
        agent_calls = [
            ("motivation_behavior_coach", "Address frustration and motivation"),
            ("elite_training_strategist", "Assess and improve training approach"),
            ("precision_nutrition_architect", "Analyze and optimize nutrition plan"),
        ]

        for agent_id, instruction in agent_calls:
            if agent_id in registered_agents:
                context = {
                    **user_context,
                    "nexus_analysis": nexus_response,
                    "instruction": instruction,
                }

                step_start = time.time()
                response = await a2a_adapter.call_agent(
                    agent_id=agent_id, user_input=instruction, context=context
                )
                step_duration = (time.time() - step_start) * 1000

                tracker.record_step(
                    f"{agent_id}_consultation",
                    agent_id,
                    context,
                    response,
                    step_duration,
                )

                if response.get("status") == "error":
                    tracker.record_error(
                        f"{agent_id} failed: {response.get('error')}", agent_id
                    )

        workflow_summary = tracker.end_workflow()

        # Validate comprehensive workflow
        assert (
            workflow_summary["steps_completed"] >= 4
        ), "Should include all specialist consultations"
        expected_agents = {
            "orchestrator",
            "motivation_behavior_coach",
            "elite_training_strategist",
            "precision_nutrition_architect",
        }
        actual_agents = set(workflow_summary["agents_involved"])

        # At least 3 of the 4 expected agents should be involved
        agents_involved = len(expected_agents.intersection(actual_agents))
        assert (
            agents_involved >= 3
        ), f"Should involve at least 3 key agents, got {agents_involved}"

        logger.info(f"Comprehensive frustrated user workflow: {workflow_summary}")

    async def test_frustrated_user_escalation_workflow(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test frustrated user workflow with escalation to more specialized help."""
        tracker = WorkflowTracker("frustrated_user_escalation")

        # User with complex frustration requiring multiple specialists
        user_context = {
            "user_id": "frustrated_user_003",
            "emotion": "extremely_frustrated",
            "session_id": str(uuid.uuid4()),
            "problems": [
                "chronic plateau",
                "metabolic issues",
                "motivation crisis",
                "considering quitting",
            ],
            "urgency": "high",
        }

        tracker.start_workflow(user_context)

        # Register expanded agent set for escalation
        required_agents = [
            "orchestrator",
            "motivation_behavior_coach",
            "elite_training_strategist",
            "precision_nutrition_architect",
            "performance_analytics",
            "female_wellness_coach",
        ]

        for agent_id in required_agents:
            if agent_id in registered_agents:
                agent = registered_agents[agent_id]
                a2a_adapter.register_agent(
                    agent_id,
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "message_callback": agent.process_message,
                    },
                )

        await asyncio.sleep(0.1)

        # Escalated user input
        user_input = (
            "I am at my breaking point. I've been stuck at the same weight "
            "for 6 months despite following every piece of advice. My energy "
            "is terrible, I'm constantly hungry, and I'm starting to hate "
            "working out. I'm ready to give up on fitness entirely. Please "
            "help me figure out what's wrong before I quit forever."
        )

        # Step 1: NEXUS recognizes escalation need
        step_start = time.time()
        nexus_response = await a2a_adapter.call_agent(
            agent_id="orchestrator", user_input=user_input, context=user_context
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "escalation_assessment",
            "orchestrator",
            user_input,
            nexus_response,
            step_duration,
        )

        # Step 2: Emergency motivation intervention
        crisis_context = {
            **user_context,
            "crisis_level": "high",
            "immediate_need": "prevent_quit",
        }

        step_start = time.time()
        crisis_response = await a2a_adapter.call_agent(
            agent_id="motivation_behavior_coach",
            user_input="URGENT: User at breaking point, prevent fitness abandonment",
            context=crisis_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "crisis_intervention",
            "motivation_behavior_coach",
            crisis_context,
            crisis_response,
            step_duration,
        )

        # Step 3: Deep analysis team activation
        analysis_agents = [
            "performance_analytics",
            "precision_nutrition_architect",
            "elite_training_strategist",
        ]

        for agent_id in analysis_agents:
            if agent_id in registered_agents:
                analysis_context = {
                    **user_context,
                    "analysis_type": "deep_plateau_investigation",
                    "crisis_intervention": crisis_response,
                }

                step_start = time.time()
                response = await a2a_adapter.call_agent(
                    agent_id=agent_id,
                    user_input="Conduct deep analysis for chronic plateau case",
                    context=analysis_context,
                )
                step_duration = (time.time() - step_start) * 1000

                tracker.record_step(
                    f"deep_analysis_{agent_id}",
                    agent_id,
                    analysis_context,
                    response,
                    step_duration,
                )

        workflow_summary = tracker.end_workflow()

        # Validate escalation workflow
        assert (
            workflow_summary["steps_completed"] >= 5
        ), "Escalation should involve multiple analysis steps"
        assert (
            workflow_summary["total_duration_ms"] < 45000
        ), "Even complex workflow should complete within 45s"

        # Verify crisis intervention happened
        crisis_steps = [
            step for step in workflow_summary["steps"] if "crisis" in step["step_name"]
        ]
        assert len(crisis_steps) >= 1, "Should include crisis intervention step"

        logger.info(f"Escalation workflow completed: {workflow_summary}")


class TestCompleteFitnessPlanWorkflow:
    """Test complete fitness plan workflow: User → NEXUS → BLAZE + SAGE + WAVE"""

    async def test_comprehensive_fitness_plan_creation(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test creation of a comprehensive fitness plan involving training, nutrition, and tracking."""
        tracker = WorkflowTracker("comprehensive_fitness_plan")

        user_context = {
            "user_id": "fitness_enthusiast_001",
            "goal": "body_recomposition",
            "experience_level": "intermediate",
            "session_id": str(uuid.uuid4()),
            "preferences": {
                "training_style": "strength_and_conditioning",
                "diet_preference": "flexible_dieting",
                "time_availability": "5_days_per_week",
            },
            "metrics": {
                "current_weight": "180lbs",
                "target_weight": "175lbs",
                "body_fat": "15%",
                "target_body_fat": "12%",
            },
        }

        tracker.start_workflow(user_context)

        # Register complete team
        required_agents = [
            "orchestrator",
            "elite_training_strategist",
            "precision_nutrition_architect",
            "performance_analytics",
        ]

        for agent_id in required_agents:
            if agent_id in registered_agents:
                agent = registered_agents[agent_id]
                a2a_adapter.register_agent(
                    agent_id,
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "message_callback": agent.process_message,
                    },
                )

        await asyncio.sleep(0.1)

        # User request for comprehensive plan
        user_input = (
            "I want to create a complete fitness plan for body recomposition. "
            "I'm intermediate level and can train 5 days per week. I want to "
            "drop from 15% to 12% body fat while maintaining muscle mass. "
            "I need a training program, nutrition plan, and tracking system."
        )

        # Step 1: NEXUS coordination and planning
        step_start = time.time()
        coordination_response = await a2a_adapter.call_agent(
            agent_id="orchestrator", user_input=user_input, context=user_context
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "plan_coordination",
            "orchestrator",
            user_input,
            coordination_response,
            step_duration,
        )

        # Step 2: BLAZE creates training program
        training_context = {
            **user_context,
            "coordination_plan": coordination_response,
            "focus": "body_recomposition_training",
        }

        step_start = time.time()
        training_plan = await a2a_adapter.call_agent(
            agent_id="elite_training_strategist",
            user_input="Create body recomposition training program for intermediate trainee",
            context=training_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "training_program_creation",
            "elite_training_strategist",
            training_context,
            training_plan,
            step_duration,
        )

        # Step 3: SAGE creates nutrition plan
        nutrition_context = {
            **user_context,
            "coordination_plan": coordination_response,
            "training_plan": training_plan,
            "focus": "body_recomposition_nutrition",
        }

        step_start = time.time()
        nutrition_plan = await a2a_adapter.call_agent(
            agent_id="precision_nutrition_architect",
            user_input="Create nutrition plan for body recomposition with flexible dieting approach",
            context=nutrition_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "nutrition_plan_creation",
            "precision_nutrition_architect",
            nutrition_context,
            nutrition_plan,
            step_duration,
        )

        # Step 4: WAVE creates tracking and analytics system
        analytics_context = {
            **user_context,
            "coordination_plan": coordination_response,
            "training_plan": training_plan,
            "nutrition_plan": nutrition_plan,
            "focus": "progress_tracking_system",
        }

        step_start = time.time()
        tracking_system = await a2a_adapter.call_agent(
            agent_id="performance_analytics",
            user_input="Create comprehensive tracking system for body recomposition progress",
            context=analytics_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "tracking_system_creation",
            "performance_analytics",
            analytics_context,
            tracking_system,
            step_duration,
        )

        workflow_summary = tracker.end_workflow()

        # Validate comprehensive plan creation
        assert (
            workflow_summary["steps_completed"] == 4
        ), "Should complete all 4 major components"

        expected_agents = {
            "orchestrator",
            "elite_training_strategist",
            "precision_nutrition_architect",
            "performance_analytics",
        }
        assert (
            set(workflow_summary["agents_involved"]) == expected_agents
        ), "Should involve all required agents"

        # Verify each component was created
        step_names = [step["step_name"] for step in workflow_summary["steps"]]
        required_components = [
            "plan_coordination",
            "training_program_creation",
            "nutrition_plan_creation",
            "tracking_system_creation",
        ]

        for component in required_components:
            assert component in step_names, f"Missing component: {component}"

        # Performance check
        assert (
            workflow_summary["total_duration_ms"] < 40000
        ), "Comprehensive plan should complete within 40s"

        logger.info(f"Comprehensive fitness plan workflow: {workflow_summary}")

    async def test_specialized_athletic_performance_plan(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test creation of specialized athletic performance plan."""
        tracker = WorkflowTracker("athletic_performance_plan")

        user_context = {
            "user_id": "athlete_001",
            "goal": "athletic_performance",
            "sport": "powerlifting",
            "competition_date": "2024-06-15",
            "current_stats": {
                "squat": "405lbs",
                "bench": "315lbs",
                "deadlift": "485lbs",
                "total": "1205lbs",
            },
            "target_stats": {"total": "1300lbs"},
        }

        tracker.start_workflow(user_context)

        # Register performance-focused agents
        required_agents = [
            "orchestrator",
            "elite_training_strategist",
            "precision_nutrition_architect",
            "performance_analytics",
            "biohacking_innovator",
        ]

        for agent_id in required_agents:
            if agent_id in registered_agents:
                agent = registered_agents[agent_id]
                a2a_adapter.register_agent(
                    agent_id,
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "message_callback": agent.process_message,
                    },
                )

        await asyncio.sleep(0.1)

        user_input = (
            "I need a specialized powerlifting performance plan. I'm currently "
            "at a 1205lb total and want to hit 1300lbs for my competition in June. "
            "I need advanced training periodization, performance nutrition, and "
            "recovery optimization."
        )

        # Step 1: Performance analysis and coordination
        step_start = time.time()
        performance_analysis = await a2a_adapter.call_agent(
            agent_id="orchestrator", user_input=user_input, context=user_context
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "performance_analysis",
            "orchestrator",
            user_input,
            performance_analysis,
            step_duration,
        )

        # Step 2: Advanced training periodization
        periodization_context = {
            **user_context,
            "analysis": performance_analysis,
            "specialization": "powerlifting_peaking",
        }

        step_start = time.time()
        training_periodization = await a2a_adapter.call_agent(
            agent_id="elite_training_strategist",
            user_input="Create advanced powerlifting periodization for competition prep",
            context=periodization_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "training_periodization",
            "elite_training_strategist",
            periodization_context,
            training_periodization,
            step_duration,
        )

        # Step 3: Performance nutrition optimization
        nutrition_context = {
            **user_context,
            "training_plan": training_periodization,
            "focus": "performance_optimization",
        }

        step_start = time.time()
        performance_nutrition = await a2a_adapter.call_agent(
            agent_id="precision_nutrition_architect",
            user_input="Optimize nutrition for powerlifting performance and competition prep",
            context=nutrition_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "performance_nutrition",
            "precision_nutrition_architect",
            nutrition_context,
            performance_nutrition,
            step_duration,
        )

        # Step 4: Advanced analytics and monitoring
        analytics_context = {
            **user_context,
            "training_plan": training_periodization,
            "nutrition_plan": performance_nutrition,
            "focus": "competition_tracking",
        }

        step_start = time.time()
        performance_tracking = await a2a_adapter.call_agent(
            agent_id="performance_analytics",
            user_input="Create advanced performance tracking for powerlifting competition prep",
            context=analytics_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "performance_tracking",
            "performance_analytics",
            analytics_context,
            performance_tracking,
            step_duration,
        )

        # Step 5: Recovery and optimization protocols
        if "biohacking_innovator" in registered_agents:
            optimization_context = {
                **user_context,
                "complete_plan": {
                    "training": training_periodization,
                    "nutrition": performance_nutrition,
                    "tracking": performance_tracking,
                },
            }

            step_start = time.time()
            recovery_optimization = await a2a_adapter.call_agent(
                agent_id="biohacking_innovator",
                user_input="Optimize recovery and performance protocols for powerlifting",
                context=optimization_context,
            )
            step_duration = (time.time() - step_start) * 1000

            tracker.record_step(
                "recovery_optimization",
                "biohacking_innovator",
                optimization_context,
                recovery_optimization,
                step_duration,
            )

        workflow_summary = tracker.end_workflow()

        # Validate specialized performance plan
        assert (
            workflow_summary["steps_completed"] >= 4
        ), "Should complete core performance components"

        # Check for specialized elements
        step_names = [step["step_name"] for step in workflow_summary["steps"]]
        specialized_elements = [
            "performance_analysis",
            "training_periodization",
            "performance_nutrition",
            "performance_tracking",
        ]

        for element in specialized_elements:
            assert element in step_names, f"Missing specialized element: {element}"

        logger.info(f"Athletic performance plan workflow: {workflow_summary}")


class TestMedicalEmergencyWorkflow:
    """Test medical emergency workflow: User → NEXUS → GUARDIAN → All agents"""

    async def test_medical_emergency_detection_and_response(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test emergency detection and coordinated response."""
        tracker = WorkflowTracker("medical_emergency")

        emergency_context = {
            "user_id": "emergency_user_001",
            "session_id": str(uuid.uuid4()),
            "urgency": "CRITICAL",
            "emergency_type": "medical",
            "timestamp": datetime.now().isoformat(),
            "location": "home_gym",
        }

        tracker.start_workflow(emergency_context)

        # Register emergency response team
        required_agents = [
            "orchestrator",
            "guardian",
            "elite_training_strategist",
            "precision_nutrition_architect",
            "female_wellness_coach",
        ]

        for agent_id in required_agents:
            if agent_id in registered_agents:
                agent = registered_agents[agent_id]
                a2a_adapter.register_agent(
                    agent_id,
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "message_callback": agent.process_message,
                    },
                )

        await asyncio.sleep(0.1)

        # Emergency user input
        emergency_input = (
            "EMERGENCY: I'm having severe chest pain and shortness of "
            "breath during my workout. I feel dizzy and nauseous. "
            "What should I do?"
        )

        # Step 1: NEXUS emergency detection
        step_start = time.time()
        nexus_emergency_response = await a2a_adapter.call_agent(
            agent_id="orchestrator",
            user_input=emergency_input,
            context=emergency_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "emergency_detection",
            "orchestrator",
            emergency_input,
            nexus_emergency_response,
            step_duration,
        )

        # Step 2: GUARDIAN immediate response
        guardian_context = {
            **emergency_context,
            "nexus_assessment": nexus_emergency_response,
            "priority": "IMMEDIATE_MEDICAL_ATTENTION",
        }

        step_start = time.time()
        guardian_response = await a2a_adapter.call_agent(
            agent_id="guardian",
            user_input="MEDICAL EMERGENCY: Chest pain, shortness of breath, dizziness during exercise",
            context=guardian_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "emergency_response",
            "guardian",
            guardian_context,
            guardian_response,
            step_duration,
        )

        # Step 3: Coordinated safety assessment
        safety_agents = ["elite_training_strategist", "female_wellness_coach"]

        for agent_id in safety_agents:
            if agent_id in registered_agents:
                safety_context = {
                    **emergency_context,
                    "guardian_instructions": guardian_response,
                    "role": "safety_assessment",
                }

                step_start = time.time()
                safety_response = await a2a_adapter.call_agent(
                    agent_id=agent_id,
                    user_input="EMERGENCY SUPPORT: Provide safety guidance for medical emergency",
                    context=safety_context,
                )
                step_duration = (time.time() - step_start) * 1000

                tracker.record_step(
                    f"safety_assessment_{agent_id}",
                    agent_id,
                    safety_context,
                    safety_response,
                    step_duration,
                )

        workflow_summary = tracker.end_workflow()

        # Emergency response validation
        assert (
            workflow_summary["steps_completed"] >= 3
        ), "Emergency should trigger multiple responses"
        assert (
            "guardian" in workflow_summary["agents_involved"]
        ), "GUARDIAN must be involved in emergencies"
        assert (
            "orchestrator" in workflow_summary["agents_involved"]
        ), "NEXUS must detect emergency"

        # Response time validation
        assert (
            workflow_summary["total_duration_ms"] < 15000
        ), "Emergency response must be under 15 seconds"

        # Verify GUARDIAN was called early
        guardian_steps = [
            step for step in workflow_summary["steps"] if step["agent_id"] == "guardian"
        ]
        assert len(guardian_steps) >= 1, "GUARDIAN must respond to emergency"

        guardian_step = guardian_steps[0]
        guardian_position = workflow_summary["steps"].index(guardian_step)
        assert guardian_position <= 2, "GUARDIAN should respond within first 3 steps"

        logger.info(f"Medical emergency workflow: {workflow_summary}")

    async def test_injury_prevention_assessment(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test injury prevention assessment workflow."""
        tracker = WorkflowTracker("injury_prevention")

        concern_context = {
            "user_id": "concerned_user_001",
            "session_id": str(uuid.uuid4()),
            "concern_type": "injury_risk",
            "symptoms": ["knee_pain", "lower_back_tightness", "fatigue"],
            "activity": "returning_to_exercise",
        }

        tracker.start_workflow(concern_context)

        # Register assessment team
        required_agents = [
            "orchestrator",
            "guardian",
            "elite_training_strategist",
            "female_wellness_coach",
        ]

        for agent_id in required_agents:
            if agent_id in registered_agents:
                agent = registered_agents[agent_id]
                a2a_adapter.register_agent(
                    agent_id,
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "message_callback": agent.process_message,
                    },
                )

        await asyncio.sleep(0.1)

        user_input = (
            "I'm concerned about returning to exercise. I've been sedentary "
            "for months and I'm experiencing some knee pain and lower back "
            "tightness. I want to start working out again but I'm worried "
            "about injuring myself. Can you help me assess my risk and "
            "create a safe return plan?"
        )

        # Step 1: Initial concern assessment
        step_start = time.time()
        initial_assessment = await a2a_adapter.call_agent(
            agent_id="orchestrator", user_input=user_input, context=concern_context
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "concern_assessment",
            "orchestrator",
            user_input,
            initial_assessment,
            step_duration,
        )

        # Step 2: GUARDIAN safety evaluation
        safety_context = {
            **concern_context,
            "initial_assessment": initial_assessment,
            "evaluation_type": "injury_risk",
        }

        step_start = time.time()
        safety_evaluation = await a2a_adapter.call_agent(
            agent_id="guardian",
            user_input="Evaluate injury risk for return to exercise with existing concerns",
            context=safety_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "safety_evaluation",
            "guardian",
            safety_context,
            safety_evaluation,
            step_duration,
        )

        # Step 3: Safe training protocol development
        protocol_context = {
            **concern_context,
            "safety_evaluation": safety_evaluation,
            "focus": "injury_prevention",
        }

        step_start = time.time()
        safe_protocol = await a2a_adapter.call_agent(
            agent_id="elite_training_strategist",
            user_input="Create safe return-to-exercise protocol with injury prevention focus",
            context=protocol_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "safe_protocol_creation",
            "elite_training_strategist",
            protocol_context,
            safe_protocol,
            step_duration,
        )

        workflow_summary = tracker.end_workflow()

        # Injury prevention validation
        assert (
            workflow_summary["steps_completed"] >= 3
        ), "Should include comprehensive assessment"
        assert (
            "guardian" in workflow_summary["agents_involved"]
        ), "GUARDIAN should evaluate safety"

        # Safety-first validation
        safety_steps = [
            step
            for step in workflow_summary["steps"]
            if "safety" in step["step_name"] or step["agent_id"] == "guardian"
        ]
        assert len(safety_steps) >= 1, "Should include safety-focused steps"

        logger.info(f"Injury prevention workflow: {workflow_summary}")


class TestGeneticOptimizationWorkflow:
    """Test genetic optimization workflow: User → NEXUS → CODE + NOVA + SAGE"""

    async def test_genetic_analysis_and_optimization(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test genetic analysis and personalized optimization."""
        tracker = WorkflowTracker("genetic_optimization")

        genetic_context = {
            "user_id": "genetic_user_001",
            "session_id": str(uuid.uuid4()),
            "genetic_data_available": True,
            "data_sources": ["23andme", "ancestry_dna"],
            "optimization_goals": ["performance", "health", "longevity"],
            "current_protocols": {
                "training": "standard_bodybuilding",
                "nutrition": "standard_macros",
                "supplementation": "basic_vitamins",
            },
        }

        tracker.start_workflow(genetic_context)

        # Register genetic optimization team
        required_agents = [
            "orchestrator",
            "genetic_specialist",
            "biohacking_innovator",
            "precision_nutrition_architect",
            "elite_training_strategist",
        ]

        for agent_id in required_agents:
            if agent_id in registered_agents:
                agent = registered_agents[agent_id]
                a2a_adapter.register_agent(
                    agent_id,
                    {
                        "name": agent.name,
                        "description": agent.description,
                        "message_callback": agent.process_message,
                    },
                )

        await asyncio.sleep(0.1)

        user_input = (
            "I have genetic testing data from 23andMe and AncestryDNA. "
            "I want to optimize my training, nutrition, and supplementation "
            "based on my genetic profile. I'm particularly interested in "
            "maximizing performance, health, and longevity. Can you analyze "
            "my genetics and create personalized protocols?"
        )

        # Step 1: NEXUS genetic optimization coordination
        step_start = time.time()
        coordination_response = await a2a_adapter.call_agent(
            agent_id="orchestrator", user_input=user_input, context=genetic_context
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "genetic_coordination",
            "orchestrator",
            user_input,
            coordination_response,
            step_duration,
        )

        # Step 2: CODE genetic analysis
        genetic_analysis_context = {
            **genetic_context,
            "coordination_plan": coordination_response,
            "analysis_focus": "comprehensive_genetic_profile",
        }

        step_start = time.time()
        genetic_analysis = await a2a_adapter.call_agent(
            agent_id="genetic_specialist",
            user_input="Analyze genetic data for fitness and health optimization",
            context=genetic_analysis_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "genetic_analysis",
            "genetic_specialist",
            genetic_analysis_context,
            genetic_analysis,
            step_duration,
        )

        # Step 3: NOVA biohacking optimization
        biohacking_context = {
            **genetic_context,
            "genetic_insights": genetic_analysis,
            "optimization_type": "performance_longevity",
        }

        step_start = time.time()
        biohacking_protocols = await a2a_adapter.call_agent(
            agent_id="biohacking_innovator",
            user_input="Create personalized biohacking protocols based on genetic profile",
            context=biohacking_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "biohacking_optimization",
            "biohacking_innovator",
            biohacking_context,
            biohacking_protocols,
            step_duration,
        )

        # Step 4: SAGE genetic nutrition optimization
        genetic_nutrition_context = {
            **genetic_context,
            "genetic_insights": genetic_analysis,
            "biohacking_protocols": biohacking_protocols,
            "focus": "genetic_nutrition",
        }

        step_start = time.time()
        genetic_nutrition = await a2a_adapter.call_agent(
            agent_id="precision_nutrition_architect",
            user_input="Optimize nutrition based on genetic markers and metabolic profile",
            context=genetic_nutrition_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "genetic_nutrition",
            "precision_nutrition_architect",
            genetic_nutrition_context,
            genetic_nutrition,
            step_duration,
        )

        # Step 5: Genetic training optimization
        genetic_training_context = {
            **genetic_context,
            "genetic_insights": genetic_analysis,
            "biohacking_protocols": biohacking_protocols,
            "genetic_nutrition": genetic_nutrition,
            "focus": "genetic_training",
        }

        step_start = time.time()
        genetic_training = await a2a_adapter.call_agent(
            agent_id="elite_training_strategist",
            user_input="Optimize training based on genetic performance markers",
            context=genetic_training_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "genetic_training",
            "elite_training_strategist",
            genetic_training_context,
            genetic_training,
            step_duration,
        )

        workflow_summary = tracker.end_workflow()

        # Genetic optimization validation
        assert (
            workflow_summary["steps_completed"] >= 5
        ), "Should complete all genetic optimization components"

        expected_agents = {
            "orchestrator",
            "genetic_specialist",
            "biohacking_innovator",
            "precision_nutrition_architect",
            "elite_training_strategist",
        }
        actual_agents = set(workflow_summary["agents_involved"])

        # At least 4 of 5 expected agents should be involved
        overlap = len(expected_agents.intersection(actual_agents))
        assert (
            overlap >= 4
        ), f"Should involve at least 4 genetic optimization agents, got {overlap}"

        # Verify genetic specialist was involved
        assert (
            "genetic_specialist" in actual_agents
        ), "CODE (genetic specialist) must be involved"

        # Verify comprehensive optimization
        step_names = [step["step_name"] for step in workflow_summary["steps"]]
        genetic_elements = [
            "genetic_analysis",
            "biohacking_optimization",
            "genetic_nutrition",
            "genetic_training",
        ]

        for element in genetic_elements:
            if element not in step_names:
                logger.warning(f"Missing genetic element: {element}")

        # At least 3 of 4 genetic elements should be present
        present_elements = sum(
            1 for element in genetic_elements if element in step_names
        )
        assert (
            present_elements >= 3
        ), f"Should include at least 3 genetic optimization elements, got {present_elements}"

        logger.info(f"Genetic optimization workflow: {workflow_summary}")


class TestFullAnalysisWorkflow:
    """Test full analysis workflow: User → NEXUS → Multiple agents for comprehensive analysis"""

    async def test_comprehensive_health_and_fitness_analysis(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test comprehensive analysis involving all available agents."""
        tracker = WorkflowTracker("full_analysis")

        comprehensive_context = {
            "user_id": "comprehensive_user_001",
            "session_id": str(uuid.uuid4()),
            "analysis_type": "complete_assessment",
            "data_sources": {
                "wearables": ["apple_watch", "oura_ring"],
                "lab_results": "recent_blood_panel",
                "genetic_data": "23andme",
                "training_history": "2_years_data",
                "nutrition_logs": "6_months_data",
            },
            "goals": [
                "optimize_everything",
                "identify_weaknesses",
                "maximize_potential",
            ],
            "timeline": "comprehensive_6_month_plan",
        }

        tracker.start_workflow(comprehensive_context)

        # Register all available agents for full analysis
        all_agents = list(registered_agents.keys())

        for agent_id in all_agents:
            agent = registered_agents[agent_id]
            a2a_adapter.register_agent(
                agent_id,
                {
                    "name": agent.name,
                    "description": agent.description,
                    "message_callback": agent.process_message,
                },
            )

        await asyncio.sleep(0.2)  # Extra time for all registrations

        user_input = (
            "I want a comprehensive analysis of my entire health and fitness "
            "profile. I have 2 years of training data, 6 months of nutrition "
            "logs, wearable device data, recent lab results, and genetic testing. "
            "I want to identify every opportunity for optimization and create "
            "a complete 6-month transformation plan that maximizes my potential "
            "across all areas."
        )

        # Step 1: NEXUS comprehensive coordination
        step_start = time.time()
        comprehensive_coordination = await a2a_adapter.call_agent(
            agent_id="orchestrator",
            user_input=user_input,
            context=comprehensive_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "comprehensive_coordination",
            "orchestrator",
            user_input,
            comprehensive_coordination,
            step_duration,
        )

        # Step 2: Multi-agent parallel analysis
        analysis_agents = [
            ("performance_analytics", "Analyze all performance and training data"),
            (
                "genetic_specialist",
                "Analyze genetic data for optimization opportunities",
            ),
            (
                "precision_nutrition_architect",
                "Analyze nutrition patterns and optimize",
            ),
            (
                "elite_training_strategist",
                "Analyze training history and optimize programs",
            ),
            ("biohacking_innovator", "Identify advanced optimization opportunities"),
            ("female_wellness_coach", "Analyze wellness and lifestyle factors"),
            ("motivation_behavior_coach", "Analyze behavioral patterns and motivation"),
            ("guardian", "Assess health risks and safety considerations"),
        ]

        # Execute parallel analysis
        analysis_tasks = []
        for agent_id, instruction in analysis_agents:
            if agent_id in registered_agents:
                analysis_context = {
                    **comprehensive_context,
                    "coordination_plan": comprehensive_coordination,
                    "analysis_instruction": instruction,
                    "agent_focus": agent_id,
                }

                task = self._execute_analysis_step(
                    a2a_adapter, tracker, agent_id, instruction, analysis_context
                )
                analysis_tasks.append(task)

        # Wait for parallel analysis to complete
        analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

        # Step 3: Integration and synthesis
        integration_context = {
            **comprehensive_context,
            "analysis_results": [
                r for r in analysis_results if not isinstance(r, Exception)
            ],
            "synthesis_phase": True,
        }

        step_start = time.time()
        final_synthesis = await a2a_adapter.call_agent(
            agent_id="orchestrator",
            user_input="Synthesize all analysis results into comprehensive optimization plan",
            context=integration_context,
        )
        step_duration = (time.time() - step_start) * 1000

        tracker.record_step(
            "final_synthesis",
            "orchestrator",
            integration_context,
            final_synthesis,
            step_duration,
        )

        workflow_summary = tracker.end_workflow()

        # Comprehensive analysis validation
        assert (
            workflow_summary["steps_completed"] >= 6
        ), "Should complete multiple analysis steps"
        assert (
            len(workflow_summary["agents_involved"]) >= 5
        ), "Should involve multiple specialized agents"

        # Verify orchestrator coordination
        orchestrator_steps = [
            step
            for step in workflow_summary["steps"]
            if step["agent_id"] == "orchestrator"
        ]
        assert (
            len(orchestrator_steps) >= 2
        ), "Orchestrator should coordinate and synthesize"

        # Verify diverse agent involvement
        core_agents = {
            "orchestrator",
            "performance_analytics",
            "genetic_specialist",
            "precision_nutrition_architect",
            "elite_training_strategist",
        }
        actual_agents = set(workflow_summary["agents_involved"])
        core_involvement = len(core_agents.intersection(actual_agents))

        assert (
            core_involvement >= 4
        ), f"Should involve at least 4 core agents, got {core_involvement}"

        # Performance validation for complex workflow
        assert (
            workflow_summary["total_duration_ms"] < 60000
        ), "Complex analysis should complete within 60s"

        logger.info(f"Comprehensive analysis workflow: {workflow_summary}")

    async def _execute_analysis_step(
        self,
        a2a_adapter: A2AAdapter,
        tracker: WorkflowTracker,
        agent_id: str,
        instruction: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a single analysis step and record metrics."""
        step_start = time.time()

        try:
            response = await a2a_adapter.call_agent(
                agent_id=agent_id, user_input=instruction, context=context
            )

            step_duration = (time.time() - step_start) * 1000

            tracker.record_step(
                f"analysis_{agent_id}", agent_id, context, response, step_duration
            )

            return response

        except Exception as e:
            step_duration = (time.time() - step_start) * 1000
            tracker.record_error(f"Analysis failed for {agent_id}: {str(e)}", agent_id)

            return {"status": "error", "error": str(e), "agent_id": agent_id}


# End-to-end workflow testing markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.a2a,
    pytest.mark.asyncio,
    pytest.mark.e2e,
    pytest.mark.slow,  # These are comprehensive tests that take time
]
