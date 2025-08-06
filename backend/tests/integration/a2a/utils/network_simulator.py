"""
Network Simulator for A2A integration testing.

Simulates various network conditions including:
- Network latency
- Packet loss
- Connection drops
- Bandwidth limitations
- Network partitions
"""

import asyncio
import random
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from core.logging_config import get_logger

logger = get_logger(__name__)


class NetworkCondition(Enum):
    """Network condition types."""

    PERFECT = "perfect"
    GOOD = "good"
    POOR = "poor"
    UNSTABLE = "unstable"
    OFFLINE = "offline"


class NetworkSimulator:
    """
    Simulates various network conditions for testing.

    Features:
    - Latency injection
    - Packet loss simulation
    - Connection drops
    - Bandwidth throttling
    - Network partition simulation
    """

    def __init__(self):
        """Initialize network simulator."""
        self.active_conditions: Dict[str, NetworkCondition] = {}
        self.latency_ms = 0.0
        self.packet_loss_rate = 0.0
        self.connection_drops: List[datetime] = []
        self.bandwidth_limit_kbps = 0  # 0 = unlimited
        self.partition_groups: Dict[str, List[str]] = {}
        self.message_delays: Dict[str, float] = {}
        self.intercepted_messages: List[Dict[str, Any]] = []

        # Predefined network conditions
        self.conditions = {
            NetworkCondition.PERFECT: {
                "latency_ms": 0,
                "packet_loss_rate": 0.0,
                "jitter_ms": 0,
                "drop_rate": 0.0,
            },
            NetworkCondition.GOOD: {
                "latency_ms": 20,
                "packet_loss_rate": 0.001,
                "jitter_ms": 5,
                "drop_rate": 0.0,
            },
            NetworkCondition.POOR: {
                "latency_ms": 200,
                "packet_loss_rate": 0.05,
                "jitter_ms": 50,
                "drop_rate": 0.01,
            },
            NetworkCondition.UNSTABLE: {
                "latency_ms": 100,
                "packet_loss_rate": 0.10,
                "jitter_ms": 100,
                "drop_rate": 0.05,
            },
            NetworkCondition.OFFLINE: {
                "latency_ms": 0,
                "packet_loss_rate": 1.0,
                "jitter_ms": 0,
                "drop_rate": 1.0,
            },
        }

    def set_network_condition(
        self, condition: NetworkCondition, agent_id: Optional[str] = None
    ):
        """
        Set network condition for specific agent or globally.

        Args:
            condition: Network condition to apply
            agent_id: Specific agent ID, or None for global
        """
        key = agent_id or "global"
        self.active_conditions[key] = condition

        if agent_id is None:
            # Apply global settings
            config = self.conditions[condition]
            self.latency_ms = config["latency_ms"]
            self.packet_loss_rate = config["packet_loss_rate"]

        logger.info(f"Network condition set to {condition.value} for {key}")

    async def simulate_latency(self, base_latency_ms: float = 0) -> float:
        """
        Simulate network latency with jitter.

        Args:
            base_latency_ms: Base latency to add to

        Returns:
            Total latency in milliseconds
        """
        total_latency = base_latency_ms + self.latency_ms

        # Add jitter (random variation)
        if total_latency > 0:
            jitter = random.uniform(-total_latency * 0.2, total_latency * 0.2)
            total_latency = max(0, total_latency + jitter)

        if total_latency > 0:
            await asyncio.sleep(total_latency / 1000.0)

        return total_latency

    def should_drop_packet(self, agent_id: Optional[str] = None) -> bool:
        """
        Determine if a packet should be dropped.

        Args:
            agent_id: Agent ID for agent-specific conditions

        Returns:
            True if packet should be dropped
        """
        # Check agent-specific condition first
        if agent_id and agent_id in self.active_conditions:
            condition = self.active_conditions[agent_id]
            config = self.conditions[condition]
            return random.random() < config["packet_loss_rate"]

        # Use global condition
        return random.random() < self.packet_loss_rate

    def should_drop_connection(self, agent_id: Optional[str] = None) -> bool:
        """
        Determine if a connection should be dropped.

        Args:
            agent_id: Agent ID for agent-specific conditions

        Returns:
            True if connection should be dropped
        """
        # Check agent-specific condition
        if agent_id and agent_id in self.active_conditions:
            condition = self.active_conditions[agent_id]
            config = self.conditions[condition]
            return random.random() < config["drop_rate"]

        # Check global offline condition
        if "global" in self.active_conditions:
            condition = self.active_conditions["global"]
            if condition == NetworkCondition.OFFLINE:
                return True

        return False

    async def simulate_message_delay(self, message: Dict[str, Any]) -> bool:
        """
        Simulate message transmission with network conditions.

        Args:
            message: Message to simulate transmission for

        Returns:
            True if message should be delivered, False if dropped
        """
        from_agent = message.get("from")
        to_agent = message.get("to")

        # Check if message should be dropped
        if self.should_drop_packet(from_agent) or self.should_drop_packet(to_agent):
            logger.debug(f"Packet dropped: {from_agent} -> {to_agent}")
            return False

        # Check for network partition
        if self.is_partitioned(from_agent, to_agent):
            logger.debug(f"Network partition blocks: {from_agent} -> {to_agent}")
            return False

        # Simulate latency
        latency = await self.simulate_latency()
        if latency > 0:
            logger.debug(
                f"Network latency: {latency:.2f}ms for {from_agent} -> {to_agent}"
            )

        # Store message for analysis
        self.intercepted_messages.append(
            {
                "message": message,
                "timestamp": datetime.now(),
                "latency_ms": latency,
                "delivered": True,
            }
        )

        return True

    def create_network_partition(self, group1: List[str], group2: List[str]):
        """
        Create a network partition between two groups of agents.

        Args:
            group1: First group of agent IDs
            group2: Second group of agent IDs
        """
        partition_id = f"partition_{len(self.partition_groups)}"
        self.partition_groups[partition_id] = {
            "group1": group1,
            "group2": group2,
            "created_at": datetime.now(),
        }

        logger.info(f"Network partition created: {group1} | {group2}")

    def heal_network_partition(self, partition_id: Optional[str] = None):
        """
        Heal network partitions.

        Args:
            partition_id: Specific partition to heal, or None for all
        """
        if partition_id:
            if partition_id in self.partition_groups:
                del self.partition_groups[partition_id]
                logger.info(f"Network partition healed: {partition_id}")
        else:
            self.partition_groups.clear()
            logger.info("All network partitions healed")

    def is_partitioned(self, agent1: str, agent2: str) -> bool:
        """
        Check if two agents are partitioned.

        Args:
            agent1: First agent ID
            agent2: Second agent ID

        Returns:
            True if agents are in different partitions
        """
        for partition in self.partition_groups.values():
            group1 = partition["group1"]
            group2 = partition["group2"]

            # Check if agents are in different groups
            if (agent1 in group1 and agent2 in group2) or (
                agent1 in group2 and agent2 in group1
            ):
                return True

        return False

    @asynccontextmanager
    async def temporary_condition(
        self,
        condition: NetworkCondition,
        duration_ms: float,
        agent_id: Optional[str] = None,
    ):
        """
        Apply a temporary network condition.

        Args:
            condition: Network condition to apply
            duration_ms: Duration in milliseconds
            agent_id: Specific agent or None for global
        """
        # Store original condition
        key = agent_id or "global"
        original_condition = self.active_conditions.get(key)

        # Apply temporary condition
        self.set_network_condition(condition, agent_id)

        try:
            # Wait for duration
            await asyncio.sleep(duration_ms / 1000.0)
            yield
        finally:
            # Restore original condition
            if original_condition:
                self.set_network_condition(original_condition, agent_id)
            else:
                # Remove condition
                if key in self.active_conditions:
                    del self.active_conditions[key]
                if agent_id is None:
                    self.reset_global_conditions()

    def simulate_connection_drop(self, agent_id: str):
        """
        Simulate a connection drop for an agent.

        Args:
            agent_id: Agent ID to drop connection for
        """
        self.connection_drops.append(datetime.now())
        logger.info(f"Simulated connection drop for {agent_id}")

    def get_connection_drops(self, since: Optional[datetime] = None) -> List[datetime]:
        """
        Get connection drops since a specific time.

        Args:
            since: Only return drops after this time

        Returns:
            List of connection drop timestamps
        """
        if since:
            return [drop for drop in self.connection_drops if drop >= since]
        return self.connection_drops.copy()

    def reset_global_conditions(self):
        """Reset global network conditions to perfect."""
        self.latency_ms = 0.0
        self.packet_loss_rate = 0.0
        self.bandwidth_limit_kbps = 0
        if "global" in self.active_conditions:
            del self.active_conditions["global"]

    def reset_all_conditions(self):
        """Reset all network conditions and clear history."""
        self.active_conditions.clear()
        self.partition_groups.clear()
        self.connection_drops.clear()
        self.intercepted_messages.clear()
        self.message_delays.clear()
        self.reset_global_conditions()
        logger.info("All network conditions reset")

    def get_network_stats(self) -> Dict[str, Any]:
        """
        Get network simulation statistics.

        Returns:
            Dictionary with network stats
        """
        total_messages = len(self.intercepted_messages)
        delivered_messages = sum(
            1 for msg in self.intercepted_messages if msg["delivered"]
        )

        if total_messages > 0:
            delivery_rate = delivered_messages / total_messages
            avg_latency = (
                sum(msg["latency_ms"] for msg in self.intercepted_messages)
                / total_messages
            )
            max_latency = max(
                (msg["latency_ms"] for msg in self.intercepted_messages), default=0
            )
        else:
            delivery_rate = 1.0
            avg_latency = 0.0
            max_latency = 0.0

        return {
            "total_messages": total_messages,
            "delivered_messages": delivered_messages,
            "delivery_rate": delivery_rate,
            "average_latency_ms": avg_latency,
            "max_latency_ms": max_latency,
            "connection_drops": len(self.connection_drops),
            "active_partitions": len(self.partition_groups),
            "active_conditions": len(self.active_conditions),
        }


class NetworkFailureScenario:
    """Predefined network failure scenarios for testing."""

    @staticmethod
    async def simulate_rolling_restart(
        simulator: NetworkSimulator,
        agents: List[str],
        restart_duration_ms: float = 5000,
    ):
        """
        Simulate rolling restart of agents.

        Args:
            simulator: Network simulator instance
            agents: List of agent IDs
            restart_duration_ms: Duration each agent is offline
        """
        for agent in agents:
            logger.info(f"Simulating restart for {agent}")
            simulator.set_network_condition(NetworkCondition.OFFLINE, agent)
            await asyncio.sleep(restart_duration_ms / 1000.0)
            simulator.set_network_condition(NetworkCondition.PERFECT, agent)
            await asyncio.sleep(0.5)  # Brief pause between restarts

    @staticmethod
    async def simulate_network_degradation(
        simulator: NetworkSimulator, duration_ms: float = 10000
    ):
        """
        Simulate gradual network degradation.

        Args:
            simulator: Network simulator instance
            duration_ms: Total duration of degradation
        """
        conditions = [
            NetworkCondition.GOOD,
            NetworkCondition.POOR,
            NetworkCondition.UNSTABLE,
            NetworkCondition.POOR,
            NetworkCondition.GOOD,
        ]

        step_duration = duration_ms / len(conditions)

        for condition in conditions:
            simulator.set_network_condition(condition)
            await asyncio.sleep(step_duration / 1000.0)

        # Restore to perfect
        simulator.set_network_condition(NetworkCondition.PERFECT)

    @staticmethod
    async def simulate_network_split_brain(
        simulator: NetworkSimulator,
        group1: List[str],
        group2: List[str],
        duration_ms: float = 5000,
    ):
        """
        Simulate split-brain network partition.

        Args:
            simulator: Network simulator instance
            group1: First group of agents
            group2: Second group of agents
            duration_ms: Duration of partition
        """
        simulator.create_network_partition(group1, group2)
        logger.info(f"Network split-brain: {group1} | {group2}")

        await asyncio.sleep(duration_ms / 1000.0)

        simulator.heal_network_partition()
        logger.info("Network split-brain healed")

    @staticmethod
    async def simulate_cascading_failures(
        simulator: NetworkSimulator, agents: List[str], failure_probability: float = 0.3
    ):
        """
        Simulate cascading failures across agents.

        Args:
            simulator: Network simulator instance
            agents: List of agent IDs
            failure_probability: Probability of each subsequent failure
        """
        failed_agents = []

        for i, agent in enumerate(agents):
            # Each failure increases probability of next failure
            current_probability = failure_probability * (1 + i * 0.2)

            if random.random() < current_probability:
                simulator.set_network_condition(NetworkCondition.OFFLINE, agent)
                failed_agents.append(agent)
                logger.info(f"Cascading failure: {agent} offline")

                # Brief delay between failures
                await asyncio.sleep(random.uniform(0.5, 2.0))

        # Gradual recovery
        for agent in failed_agents:
            await asyncio.sleep(random.uniform(2.0, 5.0))
            simulator.set_network_condition(NetworkCondition.PERFECT, agent)
            logger.info(f"Recovery: {agent} back online")


# Test helper functions
async def with_network_conditions(
    simulator: NetworkSimulator,
    condition: NetworkCondition,
    test_func: Callable,
    *args,
    **kwargs,
):
    """
    Run a test function with specific network conditions.

    Args:
        simulator: Network simulator instance
        condition: Network condition to apply
        test_func: Test function to run
        *args, **kwargs: Arguments for test function
    """
    original_conditions = simulator.active_conditions.copy()

    try:
        simulator.set_network_condition(condition)
        return await test_func(*args, **kwargs)
    finally:
        # Restore original conditions
        simulator.active_conditions = original_conditions


def create_test_network_simulator() -> NetworkSimulator:
    """Create a network simulator configured for testing."""
    simulator = NetworkSimulator()
    logger.info("Test network simulator created")
    return simulator
