"""
Test A2A Server for isolated integration testing.

Provides an isolated A2A server instance that doesn't interfere
with production or development servers.
"""

import asyncio
import socket
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Set

from core.logging_config import get_logger
from infrastructure.a2a_optimized import A2AServer, MessagePriority

logger = get_logger(__name__)


def get_free_port() -> int:
    """Get a free port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


class TestA2AServer:
    """
    Isolated A2A server for integration testing.

    Features:
    - Dynamic port allocation
    - No persistence
    - Detailed logging
    - Test metrics collection
    - Clean shutdown
    """

    def __init__(self, host: str = "127.0.0.1", port: Optional[int] = None):
        """
        Initialize test A2A server.

        Args:
            host: Host to bind to (default: localhost)
            port: Port to use (default: auto-select free port)
        """
        self.host = host
        self.port = port or get_free_port()
        self.server: Optional[A2AServer] = None
        self.registered_agents: Set[str] = set()
        self.message_count = 0
        self.error_count = 0
        self.start_time: Optional[datetime] = None
        self.metrics: Dict[str, Any] = {
            "messages_sent": 0,
            "messages_failed": 0,
            "agents_registered": 0,
            "agents_disconnected": 0,
            "average_latency_ms": 0,
            "max_latency_ms": 0,
            "total_bytes_transferred": 0,
        }

        logger.info(f"Test A2A Server initialized on {self.host}:{self.port}")

    async def start(self) -> None:
        """Start the test server."""
        try:
            # Create server instance with test configuration
            self.server = A2AServer(
                max_queue_size=1000,  # Smaller queue for testing
                message_timeout=30.0,  # 30 second timeout for tests
                circuit_breaker_threshold=5,  # Limited for testing
                circuit_breaker_timeout=30,  # 30 second recovery timeout
            )

            # Start the server
            await self.server.start()
            self.start_time = datetime.now()
            logger.info(f"Test A2A Server started on {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to start test server: {e}")
            raise

    async def stop(self) -> None:
        """Stop the test server and clean up resources."""
        if self.server:
            try:
                await self.server.stop()
                logger.info("Test A2A Server stopped")

                # Log final metrics
                if self.start_time:
                    runtime = (datetime.now() - self.start_time).total_seconds()
                    logger.info(f"Test server ran for {runtime:.2f} seconds")
                    logger.info(f"Final metrics: {self.metrics}")

            except Exception as e:
                logger.error(f"Error stopping test server: {e}")

    async def register_test_agent(self, agent_id: str, handler=None) -> bool:
        """
        Register a test agent with the server.

        Args:
            agent_id: Unique agent identifier
            handler: Optional message handler function

        Returns:
            bool: True if registration successful
        """
        if not handler:
            # Default test handler that just logs messages
            async def default_handler(message: Dict[str, Any]) -> None:
                logger.debug(f"Test agent {agent_id} received: {message}")

            handler = default_handler

        try:
            await self.server.register_agent(agent_id, handler)
            self.registered_agents.add(agent_id)
            self.metrics["agents_registered"] += 1
            logger.info(f"Test agent {agent_id} registered")
            return True

        except Exception as e:
            logger.error(f"Failed to register test agent {agent_id}: {e}")
            return False

    async def send_test_message(
        self,
        from_agent: str,
        to_agent: str,
        content: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> bool:
        """
        Send a test message between agents.

        Args:
            from_agent: Sender agent ID
            to_agent: Recipient agent ID
            content: Message content
            priority: Message priority

        Returns:
            bool: True if message sent successfully
        """
        try:
            message_id = str(uuid.uuid4())
            message = {
                "id": message_id,
                "from": from_agent,
                "to": to_agent,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "priority": priority.value,
            }

            start_time = datetime.now()
            success = await self.server.send_message(
                from_agent_id=from_agent,
                to_agent_id=to_agent,
                message=message,
                priority=priority,
            )

            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            if success:
                self.message_count += 1
                self.metrics["messages_sent"] += 1
                self.metrics["max_latency_ms"] = max(
                    self.metrics["max_latency_ms"], latency_ms
                )
                # Update average latency
                total_latency = self.metrics["average_latency_ms"] * (
                    self.message_count - 1
                )
                self.metrics["average_latency_ms"] = (
                    total_latency + latency_ms
                ) / self.message_count

                logger.debug(
                    f"Test message sent: {from_agent} -> {to_agent} ({latency_ms:.2f}ms)"
                )
            else:
                self.error_count += 1
                self.metrics["messages_failed"] += 1
                logger.warning(
                    f"Failed to send test message: {from_agent} -> {to_agent}"
                )

            return success

        except Exception as e:
            logger.error(f"Error sending test message: {e}")
            self.error_count += 1
            self.metrics["messages_failed"] += 1
            return False

    async def get_metrics(self) -> Dict[str, Any]:
        """Get current server metrics."""
        metrics = self.metrics.copy()

        # Add server stats if available
        if self.server:
            server_stats = await self.server.get_stats()
            metrics.update({"server_" + k: v for k, v in server_stats.items()})

        # Add runtime
        if self.start_time:
            metrics["runtime_seconds"] = (
                datetime.now() - self.start_time
            ).total_seconds()

        return metrics

    async def wait_for_agents(
        self, agent_ids: list[str], timeout: float = 10.0
    ) -> bool:
        """
        Wait for specific agents to be registered.

        Args:
            agent_ids: List of agent IDs to wait for
            timeout: Maximum time to wait

        Returns:
            bool: True if all agents registered within timeout
        """
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout:
            if all(aid in self.registered_agents for aid in agent_ids):
                return True
            await asyncio.sleep(0.1)

        missing = [aid for aid in agent_ids if aid not in self.registered_agents]
        logger.warning(f"Timeout waiting for agents: {missing}")
        return False

    async def simulate_network_delay(self, delay_ms: float):
        """Simulate network delay for testing."""
        if self.server and hasattr(self.server, "_add_network_delay"):
            await self.server._add_network_delay(delay_ms / 1000.0)

    async def simulate_agent_disconnect(self, agent_id: str):
        """Simulate an agent disconnection."""
        if agent_id in self.registered_agents:
            await self.server.unregister_agent(agent_id)
            self.registered_agents.remove(agent_id)
            self.metrics["agents_disconnected"] += 1
            logger.info(f"Simulated disconnect for agent {agent_id}")

    def reset_metrics(self):
        """Reset all metrics for a new test run."""
        self.message_count = 0
        self.error_count = 0
        self.metrics = {
            "messages_sent": 0,
            "messages_failed": 0,
            "agents_registered": 0,
            "agents_disconnected": 0,
            "average_latency_ms": 0,
            "max_latency_ms": 0,
            "total_bytes_transferred": 0,
        }
        logger.info("Test server metrics reset")
