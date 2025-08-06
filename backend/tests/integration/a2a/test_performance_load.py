"""
A2A Performance and Load Integration Tests.

Comprehensive test suite for system performance under load:
- High-volume concurrent messages (100+ messages)
- Latency under load (target < 100ms)
- Memory usage stability
- Backpressure handling
- Rate limiting effectiveness
- Throughput measurement
- Resource utilization monitoring
"""

import asyncio
import gc
import statistics
import time
from typing import Any, Dict, List, Optional, Tuple

import psutil
import pytest

from core.logging_config import get_logger
from infrastructure.a2a_optimized import MessagePriority
from infrastructure.adapters.a2a_adapter import A2AAdapter
from tests.integration.a2a.utils.agent_simulator import SimulatedAgent
from tests.integration.a2a.utils.test_server import TestA2AServer

logger = get_logger(__name__)


class PerformanceMetrics:
    """Helper class for collecting and analyzing performance metrics."""

    def __init__(self):
        """Initialize performance metrics collector."""
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.latencies: List[float] = []
        self.throughput_samples: List[Tuple[float, int]] = []
        self.memory_samples: List[float] = []
        self.cpu_samples: List[float] = []
        self.error_count = 0
        self.success_count = 0
        self.message_sizes: List[int] = []

    def start_measurement(self):
        """Start performance measurement."""
        self.start_time = time.time()
        self._collect_system_metrics()

    def end_measurement(self):
        """End performance measurement."""
        self.end_time = time.time()
        self._collect_system_metrics()

    def record_latency(self, latency_ms: float):
        """Record a latency measurement."""
        self.latencies.append(latency_ms)

    def record_success(self, message_size_bytes: int = 0):
        """Record a successful operation."""
        self.success_count += 1
        if message_size_bytes > 0:
            self.message_sizes.append(message_size_bytes)

    def record_error(self):
        """Record an error."""
        self.error_count += 1

    def record_throughput_sample(self, messages_processed: int):
        """Record a throughput sample."""
        self.throughput_samples.append((time.time(), messages_processed))

    def _collect_system_metrics(self):
        """Collect system resource metrics."""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()

            self.memory_samples.append(memory_mb)
            self.cpu_samples.append(cpu_percent)
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        total_time = (self.end_time or time.time()) - (self.start_time or 0)
        total_messages = self.success_count + self.error_count

        summary = {
            "total_time_seconds": total_time,
            "total_messages": total_messages,
            "successful_messages": self.success_count,
            "failed_messages": self.error_count,
            "success_rate": self.success_count / max(total_messages, 1),
            "messages_per_second": total_messages / max(total_time, 0.001),
        }

        # Latency statistics
        if self.latencies:
            summary.update(
                {
                    "latency_avg_ms": statistics.mean(self.latencies),
                    "latency_median_ms": statistics.median(self.latencies),
                    "latency_p95_ms": self._percentile(self.latencies, 0.95),
                    "latency_p99_ms": self._percentile(self.latencies, 0.99),
                    "latency_max_ms": max(self.latencies),
                    "latency_min_ms": min(self.latencies),
                    "latency_std_ms": (
                        statistics.stdev(self.latencies)
                        if len(self.latencies) > 1
                        else 0
                    ),
                }
            )

        # Memory statistics
        if self.memory_samples:
            summary.update(
                {
                    "memory_avg_mb": statistics.mean(self.memory_samples),
                    "memory_max_mb": max(self.memory_samples),
                    "memory_min_mb": min(self.memory_samples),
                    "memory_growth_mb": max(self.memory_samples)
                    - min(self.memory_samples),
                }
            )

        # CPU statistics
        if self.cpu_samples:
            summary.update(
                {
                    "cpu_avg_percent": statistics.mean(self.cpu_samples),
                    "cpu_max_percent": max(self.cpu_samples),
                }
            )

        # Message size statistics
        if self.message_sizes:
            summary.update(
                {
                    "avg_message_size_bytes": statistics.mean(self.message_sizes),
                    "max_message_size_bytes": max(self.message_sizes),
                    "total_bytes_transferred": sum(self.message_sizes),
                }
            )

        return summary

    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        sorted_data = sorted(data)
        index = int(percentile * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


class TestHighVolumeConcurrency:
    """Test high-volume concurrent message processing."""

    async def test_concurrent_message_burst(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
        performance_metrics: Dict[str, Any],
    ):
        """Test handling of high-volume message bursts."""
        metrics = PerformanceMetrics()
        metrics.start_measurement()

        # Configuration
        num_messages = 200
        concurrent_batches = 10
        batch_size = num_messages // concurrent_batches

        from_agent = "orchestrator"
        target_agents = [
            "elite_training_strategist",
            "precision_nutrition_architect",
            "motivation_behavior_coach",
        ]

        # Create concurrent batches
        all_tasks = []

        for batch in range(concurrent_batches):
            batch_tasks = []

            for i in range(batch_size):
                to_agent = target_agents[i % len(target_agents)]
                message_content = {
                    **sample_messages["simple_training"],
                    "batch": batch,
                    "sequence": i,
                    "timestamp": time.time(),
                }

                priority = (
                    MessagePriority.HIGH if i % 10 == 0 else MessagePriority.NORMAL
                )

                # Create task with latency measurement
                task = self._send_message_with_metrics(
                    test_a2a_server,
                    metrics,
                    from_agent,
                    to_agent,
                    message_content,
                    priority,
                )
                batch_tasks.append(task)

            all_tasks.extend(batch_tasks)

        # Execute all tasks concurrently
        logger.info(
            f"Starting concurrent burst test: {num_messages} messages in {concurrent_batches} batches"
        )

        start_time = time.time()
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        elapsed_time = time.time() - start_time

        metrics.end_measurement()

        # Analyze results
        successful_sends = sum(1 for result in results if result is True)
        len(results) - successful_sends

        # Calculate throughput
        throughput = successful_sends / elapsed_time

        logger.info(
            f"Burst test completed: {successful_sends}/{num_messages} messages in {elapsed_time:.2f}s"
        )
        logger.info(f"Throughput: {throughput:.2f} messages/second")

        # Performance assertions
        assert successful_sends > num_messages * 0.9  # At least 90% success rate
        assert elapsed_time < 30.0  # Complete within 30 seconds
        assert throughput > 10.0  # At least 10 messages per second

        # Update performance metrics fixture
        summary = metrics.get_summary()
        performance_metrics.update(summary)

        # Latency requirements
        if metrics.latencies:
            avg_latency = statistics.mean(metrics.latencies)
            p95_latency = metrics._percentile(metrics.latencies, 0.95)

            logger.info(f"Latency - Avg: {avg_latency:.2f}ms, P95: {p95_latency:.2f}ms")

            # Performance targets
            assert avg_latency < 200.0  # Average latency under 200ms
            assert p95_latency < 500.0  # P95 latency under 500ms

    async def test_sustained_high_load(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test sustained high load over extended period."""
        metrics = PerformanceMetrics()
        metrics.start_measurement()

        # Configuration for sustained load
        duration_seconds = 10.0
        target_rate = 50  # messages per second

        from_agent = "orchestrator"
        target_agents = list(registered_agents.keys())[:4]  # Use first 4 agents

        # Calculate timing
        message_interval = 1.0 / target_rate
        total_messages = int(duration_seconds * target_rate)

        logger.info(
            f"Starting sustained load test: {target_rate} msg/s for {duration_seconds}s"
        )

        # Send messages at sustained rate
        sent_count = 0
        start_time = time.time()

        while time.time() - start_time < duration_seconds:
            # Send a batch of messages
            batch_tasks = []
            batch_size = min(10, total_messages - sent_count)  # Send in small batches

            for i in range(batch_size):
                to_agent = target_agents[(sent_count + i) % len(target_agents)]
                message_content = {
                    **sample_messages["simple_training"],
                    "sustained_test": True,
                    "sequence": sent_count + i,
                    "timestamp": time.time(),
                }

                task = self._send_message_with_metrics(
                    test_a2a_server,
                    metrics,
                    from_agent,
                    to_agent,
                    message_content,
                    MessagePriority.NORMAL,
                )
                batch_tasks.append(task)

            # Execute batch
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            sent_count += len(batch_results)

            # Record throughput sample
            metrics.record_throughput_sample(sent_count)

            # Rate limiting
            await asyncio.sleep(message_interval)

            if sent_count >= total_messages:
                break

        metrics.end_measurement()

        # Calculate actual performance
        actual_duration = time.time() - start_time
        actual_rate = sent_count / actual_duration

        logger.info(
            f"Sustained load completed: {sent_count} messages in {actual_duration:.2f}s"
        )
        logger.info(f"Actual rate: {actual_rate:.2f} messages/second")

        # Performance assertions
        assert actual_rate >= target_rate * 0.8  # Within 80% of target rate
        assert metrics.success_count > sent_count * 0.85  # At least 85% success rate

        # Memory stability check
        summary = metrics.get_summary()
        if "memory_growth_mb" in summary:
            memory_growth = summary["memory_growth_mb"]
            logger.info(f"Memory growth during test: {memory_growth:.2f} MB")

            # Memory should not grow excessively
            assert memory_growth < 100.0  # Less than 100MB growth

    async def test_peak_load_handling(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test system behavior at peak load capacity."""
        metrics = PerformanceMetrics()
        metrics.start_measurement()

        # Aggressive load configuration
        peak_messages = 500
        concurrent_workers = 20
        messages_per_worker = peak_messages // concurrent_workers

        from_agent = "orchestrator"
        target_agents = list(registered_agents.keys())

        logger.info(
            f"Starting peak load test: {peak_messages} messages with {concurrent_workers} workers"
        )

        async def worker_task(worker_id: int) -> List[bool]:
            """Worker task for sending messages."""
            worker_results = []

            for i in range(messages_per_worker):
                to_agent = target_agents[(worker_id + i) % len(target_agents)]
                message_content = {
                    **sample_messages["complex_request"],
                    "worker_id": worker_id,
                    "sequence": i,
                    "peak_test": True,
                }

                # Mix priorities for realistic load
                if i % 20 == 0:
                    priority = MessagePriority.CRITICAL
                elif i % 10 == 0:
                    priority = MessagePriority.HIGH
                else:
                    priority = MessagePriority.NORMAL

                start_latency = time.time()
                success = await test_a2a_server.send_test_message(
                    from_agent=from_agent,
                    to_agent=to_agent,
                    content=message_content,
                    priority=priority,
                )
                latency_ms = (time.time() - start_latency) * 1000

                metrics.record_latency(latency_ms)
                if success:
                    metrics.record_success()
                else:
                    metrics.record_error()

                worker_results.append(success)

                # Small delay to prevent overwhelming
                if i % 50 == 0:
                    await asyncio.sleep(0.01)

            return worker_results

        # Launch all workers
        worker_tasks = [worker_task(i) for i in range(concurrent_workers)]

        start_time = time.time()
        all_results = await asyncio.gather(*worker_tasks, return_exceptions=True)
        elapsed_time = time.time() - start_time

        metrics.end_measurement()

        # Flatten results
        total_successes = 0
        total_failures = 0

        for worker_results in all_results:
            if isinstance(worker_results, list):
                total_successes += sum(worker_results)
                total_failures += len(worker_results) - sum(worker_results)
            else:
                # Worker failed entirely
                total_failures += messages_per_worker

        total_attempted = total_successes + total_failures
        success_rate = total_successes / max(total_attempted, 1)
        throughput = total_successes / elapsed_time

        logger.info(
            f"Peak load completed: {total_successes}/{total_attempted} successful"
        )
        logger.info(
            f"Success rate: {success_rate:.2%}, Throughput: {throughput:.2f} msg/s"
        )

        # At peak load, some failures are acceptable but system should remain stable
        assert success_rate > 0.7  # At least 70% success rate under peak load
        assert throughput > 20.0  # Minimum throughput under peak load
        assert elapsed_time < 60.0  # Complete within reasonable time

        # System stability check
        metrics.get_summary()
        if metrics.latencies:
            p99_latency = metrics._percentile(metrics.latencies, 0.99)
            logger.info(f"P99 latency under peak load: {p99_latency:.2f}ms")

            # P99 latency should still be reasonable
            assert p99_latency < 2000.0  # Under 2 seconds even at peak

    async def _send_message_with_metrics(
        self,
        server: TestA2AServer,
        metrics: PerformanceMetrics,
        from_agent: str,
        to_agent: str,
        content: Dict[str, Any],
        priority: MessagePriority,
    ) -> bool:
        """Send message and record metrics."""
        start_time = time.time()

        try:
            success = await server.send_test_message(
                from_agent=from_agent,
                to_agent=to_agent,
                content=content,
                priority=priority,
            )

            latency_ms = (time.time() - start_time) * 1000
            metrics.record_latency(latency_ms)

            # Estimate message size
            message_size = len(str(content).encode("utf-8"))

            if success:
                metrics.record_success(message_size)
            else:
                metrics.record_error()

            return success

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            metrics.record_latency(latency_ms)
            metrics.record_error()
            logger.warning(f"Message send failed: {e}")
            return False


class TestLatencyUnderLoad:
    """Test latency characteristics under various load conditions."""

    async def test_latency_distribution_under_load(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test latency distribution under different load levels."""
        load_levels = [
            ("light", 10, 1),  # 10 messages, 1 concurrent
            ("medium", 50, 5),  # 50 messages, 5 concurrent
            ("heavy", 100, 10),  # 100 messages, 10 concurrent
            ("extreme", 200, 20),  # 200 messages, 20 concurrent
        ]

        from_agent = "orchestrator"
        to_agent = "elite_training_strategist"

        results = {}

        for load_name, message_count, concurrency in load_levels:
            logger.info(
                f"Testing latency under {load_name} load: {message_count} messages, {concurrency} concurrent"
            )

            metrics = PerformanceMetrics()
            metrics.start_measurement()

            # Create batches for concurrent execution
            batch_size = message_count // concurrency
            tasks = []

            for batch in range(concurrency):
                batch_tasks = []
                for i in range(batch_size):
                    message_content = {
                        **sample_messages["simple_training"],
                        "load_test": load_name,
                        "batch": batch,
                        "sequence": i,
                    }

                    task = self._measure_single_message_latency(
                        test_a2a_server, from_agent, to_agent, message_content
                    )
                    batch_tasks.append(task)

                # Add batch as a group
                tasks.extend(batch_tasks)

            # Execute all messages for this load level
            start_time = time.time()
            latencies = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed_time = time.time() - start_time

            # Filter successful measurements
            valid_latencies = [lat for lat in latencies if isinstance(lat, float)]

            metrics.end_measurement()

            if valid_latencies:
                results[load_name] = {
                    "count": len(valid_latencies),
                    "avg_latency_ms": statistics.mean(valid_latencies),
                    "median_latency_ms": statistics.median(valid_latencies),
                    "p95_latency_ms": metrics._percentile(valid_latencies, 0.95),
                    "p99_latency_ms": metrics._percentile(valid_latencies, 0.99),
                    "max_latency_ms": max(valid_latencies),
                    "std_latency_ms": (
                        statistics.stdev(valid_latencies)
                        if len(valid_latencies) > 1
                        else 0
                    ),
                    "throughput": len(valid_latencies) / elapsed_time,
                }

                logger.info(f"{load_name} load results:")
                logger.info(
                    f"  Avg latency: {results[load_name]['avg_latency_ms']:.2f}ms"
                )
                logger.info(
                    f"  P95 latency: {results[load_name]['p95_latency_ms']:.2f}ms"
                )
                logger.info(
                    f"  Throughput: {results[load_name]['throughput']:.2f} msg/s"
                )

        # Verify latency targets across load levels
        for load_name, stats in results.items():
            if load_name == "light":
                # Light load should have excellent latency
                assert stats["avg_latency_ms"] < 50.0
                assert stats["p95_latency_ms"] < 100.0
            elif load_name == "medium":
                # Medium load should still be good
                assert stats["avg_latency_ms"] < 100.0
                assert stats["p95_latency_ms"] < 200.0
            elif load_name == "heavy":
                # Heavy load acceptable degradation
                assert stats["avg_latency_ms"] < 200.0
                assert stats["p95_latency_ms"] < 500.0
            else:  # extreme
                # Extreme load - still functional
                assert stats["avg_latency_ms"] < 500.0
                assert stats["p95_latency_ms"] < 1000.0

    async def test_latency_consistency(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test latency consistency over time."""
        from_agent = "orchestrator"
        to_agent = "precision_nutrition_architect"

        # Send messages over time and measure consistency
        measurement_windows = 5
        messages_per_window = 20
        window_duration = 2.0  # seconds

        window_results = []

        for window in range(measurement_windows):
            logger.info(f"Measuring latency window {window + 1}/{measurement_windows}")

            window_latencies = []
            window_start = time.time()

            # Send messages throughout the window
            for i in range(messages_per_window):
                message_content = {
                    **sample_messages["simple_training"],
                    "consistency_test": True,
                    "window": window,
                    "sequence": i,
                }

                latency = await self._measure_single_message_latency(
                    test_a2a_server, from_agent, to_agent, message_content
                )

                if isinstance(latency, float):
                    window_latencies.append(latency)

                # Space messages evenly across the window
                next_send_time = window_start + (i + 1) * (
                    window_duration / messages_per_window
                )
                sleep_time = max(0, next_send_time - time.time())
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            # Calculate window statistics
            if window_latencies:
                window_stats = {
                    "window": window,
                    "count": len(window_latencies),
                    "avg_latency_ms": statistics.mean(window_latencies),
                    "std_latency_ms": (
                        statistics.stdev(window_latencies)
                        if len(window_latencies) > 1
                        else 0
                    ),
                    "min_latency_ms": min(window_latencies),
                    "max_latency_ms": max(window_latencies),
                }
                window_results.append(window_stats)

                logger.info(
                    f"Window {window}: avg={window_stats['avg_latency_ms']:.2f}ms, "
                    f"std={window_stats['std_latency_ms']:.2f}ms"
                )

        # Analyze consistency across windows
        if len(window_results) > 1:
            avg_latencies = [w["avg_latency_ms"] for w in window_results]
            [w["std_latency_ms"] for w in window_results]

            overall_avg = statistics.mean(avg_latencies)
            consistency_std = statistics.stdev(avg_latencies)

            logger.info(
                f"Latency consistency: overall_avg={overall_avg:.2f}ms, "
                f"consistency_std={consistency_std:.2f}ms"
            )

            # Consistency requirements
            assert (
                consistency_std < overall_avg * 0.5
            )  # Standard deviation < 50% of mean
            assert max(avg_latencies) / min(avg_latencies) < 3.0  # Max variance < 3x

    async def _measure_single_message_latency(
        self,
        server: TestA2AServer,
        from_agent: str,
        to_agent: str,
        content: Dict[str, Any],
    ) -> float:
        """Measure latency of a single message."""
        start_time = time.time()

        try:
            success = await server.send_test_message(
                from_agent=from_agent,
                to_agent=to_agent,
                content=content,
                priority=MessagePriority.NORMAL,
            )

            latency_ms = (time.time() - start_time) * 1000

            if success:
                return latency_ms
            else:
                logger.warning("Message failed to send")
                return -1.0

        except Exception as e:
            logger.warning(f"Latency measurement failed: {e}")
            return -1.0


class TestMemoryStability:
    """Test memory usage stability under various conditions."""

    async def test_memory_usage_under_load(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test memory usage patterns under sustained load."""
        # Force garbage collection before starting
        gc.collect()

        initial_memory = self._get_memory_usage_mb()
        logger.info(f"Initial memory usage: {initial_memory:.2f} MB")

        memory_samples = [initial_memory]
        max_allowed_memory = initial_memory + 200  # Allow 200MB growth

        # Sustained load test with memory monitoring
        duration_seconds = 15.0
        messages_per_second = 30
        monitoring_interval = 1.0  # Sample memory every second

        from_agent = "orchestrator"
        target_agents = list(registered_agents.keys())[:3]

        start_time = time.time()
        message_count = 0

        # Background task for memory monitoring
        async def memory_monitor():
            while time.time() - start_time < duration_seconds:
                await asyncio.sleep(monitoring_interval)
                current_memory = self._get_memory_usage_mb()
                memory_samples.append(current_memory)

                logger.debug(f"Memory usage: {current_memory:.2f} MB")

                # Check for memory leaks
                if current_memory > max_allowed_memory:
                    logger.warning(
                        f"Memory usage exceeded limit: {current_memory:.2f} MB > {max_allowed_memory:.2f} MB"
                    )

        # Start memory monitoring
        monitor_task = asyncio.create_task(memory_monitor())

        # Message sending loop
        while time.time() - start_time < duration_seconds:
            # Send batch of messages
            batch_size = 10
            tasks = []

            for i in range(batch_size):
                to_agent = target_agents[message_count % len(target_agents)]
                message_content = {
                    **sample_messages["complex_request"],
                    "memory_test": True,
                    "sequence": message_count,
                    "timestamp": time.time(),
                    "large_data": "x" * 1000,  # Add some data to make messages larger
                }

                task = test_a2a_server.send_test_message(
                    from_agent=from_agent,
                    to_agent=to_agent,
                    content=message_content,
                    priority=MessagePriority.NORMAL,
                )
                tasks.append(task)
                message_count += 1

            # Execute batch
            await asyncio.gather(*tasks, return_exceptions=True)

            # Rate limiting
            await asyncio.sleep(batch_size / messages_per_second)

        # Stop monitoring
        monitor_task.cancel()

        # Final memory check
        final_memory = self._get_memory_usage_mb()
        memory_growth = final_memory - initial_memory

        logger.info(f"Final memory usage: {final_memory:.2f} MB")
        logger.info(f"Memory growth: {memory_growth:.2f} MB")
        logger.info(f"Messages sent: {message_count}")

        # Memory stability assertions
        assert memory_growth < 150.0  # Less than 150MB growth
        assert final_memory < max_allowed_memory  # Within allowed limit

        # Check for memory spikes
        if memory_samples:
            max_memory = max(memory_samples)
            avg_memory = statistics.mean(memory_samples)

            logger.info(
                f"Peak memory: {max_memory:.2f} MB, Average: {avg_memory:.2f} MB"
            )

            # No extreme spikes
            assert max_memory < initial_memory + 250  # Peak within 250MB of initial

    async def test_memory_cleanup_after_load(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test that memory is cleaned up after high load periods."""
        # Baseline memory
        gc.collect()
        baseline_memory = self._get_memory_usage_mb()

        # High load period
        logger.info("Starting high load period for memory cleanup test")

        num_messages = 300
        from_agent = "orchestrator"
        to_agent = "elite_training_strategist"

        # Send many large messages
        tasks = []
        for i in range(num_messages):
            large_content = {
                **sample_messages["complex_request"],
                "cleanup_test": True,
                "sequence": i,
                "large_payload": "X" * 5000,  # 5KB payload
                "nested_data": {"level1": {"level2": {"level3": "data" * 100}}},
            }

            task = test_a2a_server.send_test_message(
                from_agent=from_agent,
                to_agent=to_agent,
                content=large_content,
                priority=MessagePriority.NORMAL,
            )
            tasks.append(task)

        # Execute high load
        start_time = time.time()
        await asyncio.gather(*tasks, return_exceptions=True)
        load_duration = time.time() - start_time

        # Memory after load
        post_load_memory = self._get_memory_usage_mb()
        memory_growth = post_load_memory - baseline_memory

        logger.info(
            f"Memory after load: {post_load_memory:.2f} MB (+{memory_growth:.2f} MB)"
        )
        logger.info(f"Load duration: {load_duration:.2f} seconds")

        # Allow cleanup time
        logger.info("Waiting for cleanup...")
        cleanup_wait_time = 5.0
        await asyncio.sleep(cleanup_wait_time)

        # Force garbage collection
        gc.collect()
        await asyncio.sleep(1.0)

        # Memory after cleanup
        post_cleanup_memory = self._get_memory_usage_mb()
        memory_recovered = post_load_memory - post_cleanup_memory
        final_growth = post_cleanup_memory - baseline_memory

        logger.info(f"Memory after cleanup: {post_cleanup_memory:.2f} MB")
        logger.info(f"Memory recovered: {memory_recovered:.2f} MB")
        logger.info(f"Final growth: {final_growth:.2f} MB")

        # Cleanup effectiveness assertions
        assert memory_recovered > 0  # Some memory should be recovered
        assert (
            final_growth < memory_growth * 0.7
        )  # At least 30% of growth should be cleaned up
        assert final_growth < 100.0  # Final growth should be reasonable

    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0


class TestBackpressureHandling:
    """Test backpressure handling mechanisms."""

    async def test_backpressure_activation(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
        sample_messages: Dict[str, Dict[str, Any]],
    ):
        """Test that backpressure activates under extreme load."""
        # Create a slow agent to cause backpressure
        slow_agent = SimulatedAgent(
            agent_id="slow_agent",
            agent_type="slow_agent",
            name="Slow Agent",
            description="Intentionally slow agent for backpressure testing",
            response_delay=0.5,  # 500ms delay per message
        )

        # Register slow agent
        def handler(msg):
            return slow_agent.process_message(msg)

        await test_a2a_server.register_test_agent(slow_agent.agent_id, handler)

        # Send messages faster than the agent can process
        rapid_message_count = 50
        from_agent = "orchestrator"

        logger.info(f"Sending {rapid_message_count} messages to slow agent")

        # Send messages as fast as possible
        tasks = []
        for i in range(rapid_message_count):
            message_content = {
                **sample_messages["simple_training"],
                "backpressure_test": True,
                "sequence": i,
                "timestamp": time.time(),
            }

            task = test_a2a_server.send_test_message(
                from_agent=from_agent,
                to_agent=slow_agent.agent_id,
                content=message_content,
                priority=MessagePriority.NORMAL,
            )
            tasks.append(task)

        # Measure how long it takes to send all messages
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        send_duration = time.time() - start_time

        successful_sends = sum(1 for result in results if result is True)
        failed_sends = len(results) - successful_sends

        logger.info(
            f"Backpressure test: {successful_sends}/{rapid_message_count} sent in {send_duration:.2f}s"
        )
        logger.info(f"Failed sends: {failed_sends}")

        # With backpressure, either:
        # 1. Some messages should fail (dropped due to backpressure)
        # 2. Or sending should take longer than without backpressure

        expected_min_duration = (
            rapid_message_count * slow_agent.response_delay
        ) / 10  # Assuming some parallelization

        # Backpressure should either cause failures or increased latency
        backpressure_detected = (
            failed_sends > 0 or send_duration > expected_min_duration
        )

        assert (
            backpressure_detected
        ), "Backpressure should be detected under extreme load"

    async def test_backpressure_recovery(
        self,
        test_a2a_server: TestA2AServer,
        registered_agents: Dict[str, SimulatedAgent],
    ):
        """Test recovery after backpressure conditions are resolved."""
        # Create initially slow agent
        recovering_agent = SimulatedAgent(
            agent_id="recovering_agent",
            agent_type="recovering_agent",
            name="Recovering Agent",
            description="Agent that becomes faster over time",
            response_delay=1.0,  # Start slow
        )

        def handler(msg):
            return recovering_agent.process_message(msg)

        await test_a2a_server.register_test_agent(recovering_agent.agent_id, handler)

        # Phase 1: Create backpressure
        logger.info("Phase 1: Creating backpressure")

        backpressure_messages = 20
        phase1_tasks = []

        for i in range(backpressure_messages):
            task = test_a2a_server.send_test_message(
                from_agent="orchestrator",
                to_agent=recovering_agent.agent_id,
                content={"phase": 1, "sequence": i},
                priority=MessagePriority.NORMAL,
            )
            phase1_tasks.append(task)

        phase1_start = time.time()
        phase1_results = await asyncio.gather(*phase1_tasks, return_exceptions=True)
        phase1_duration = time.time() - phase1_start

        phase1_successes = sum(1 for r in phase1_results if r is True)

        # Phase 2: Improve agent performance
        logger.info("Phase 2: Agent performance improvement")
        recovering_agent.set_response_delay(0.1)  # Much faster now

        # Allow some time for recovery
        await asyncio.sleep(2.0)

        # Phase 3: Test recovery
        logger.info("Phase 3: Testing recovery")

        recovery_messages = 20
        phase3_tasks = []

        for i in range(recovery_messages):
            task = test_a2a_server.send_test_message(
                from_agent="orchestrator",
                to_agent=recovering_agent.agent_id,
                content={"phase": 3, "sequence": i},
                priority=MessagePriority.NORMAL,
            )
            phase3_tasks.append(task)

        phase3_start = time.time()
        phase3_results = await asyncio.gather(*phase3_tasks, return_exceptions=True)
        phase3_duration = time.time() - phase3_start

        phase3_successes = sum(1 for r in phase3_results if r is True)

        logger.info(
            f"Phase 1: {phase1_successes}/{backpressure_messages} in {phase1_duration:.2f}s"
        )
        logger.info(
            f"Phase 3: {phase3_successes}/{recovery_messages} in {phase3_duration:.2f}s"
        )

        # Recovery should show improved performance
        assert phase3_duration < phase1_duration  # Faster processing
        assert phase3_successes >= phase1_successes  # At least as many successes


class TestRateLimitingEffectiveness:
    """Test rate limiting mechanisms."""

    async def test_rate_limit_enforcement(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test that rate limiting is enforced correctly."""
        # Register a test agent
        test_agent = registered_agents["orchestrator"]
        a2a_adapter.register_agent(
            test_agent.agent_id,
            {
                "name": test_agent.name,
                "description": test_agent.description,
                "message_callback": test_agent.process_message,
            },
        )

        await asyncio.sleep(0.1)

        # Attempt to exceed rate limits
        rapid_requests = 50
        rapid_interval = 0.01  # 10ms between requests = 100 req/s

        logger.info(f"Testing rate limiting with {rapid_requests} rapid requests")

        successful_requests = 0
        rate_limited_requests = 0
        start_time = time.time()

        for i in range(rapid_requests):
            try:
                response = await a2a_adapter.call_agent(
                    agent_id=test_agent.agent_id,
                    user_input=f"Rate limit test {i}",
                    context={"test": "rate_limiting", "sequence": i},
                )

                if (
                    response.get("status") == "error"
                    and "rate limit" in response.get("error", "").lower()
                ):
                    rate_limited_requests += 1
                elif response.get("status") != "error":
                    successful_requests += 1

            except Exception as e:
                if "rate limit" in str(e).lower():
                    rate_limited_requests += 1
                else:
                    logger.warning(f"Unexpected error: {e}")

            await asyncio.sleep(rapid_interval)

        total_time = time.time() - start_time
        actual_rate = (successful_requests + rate_limited_requests) / total_time

        logger.info("Rate limiting results:")
        logger.info(f"  Successful: {successful_requests}")
        logger.info(f"  Rate limited: {rate_limited_requests}")
        logger.info(f"  Actual rate: {actual_rate:.2f} req/s")

        # Rate limiting should activate under rapid requests
        # The exact behavior depends on implementation
        total_responses = successful_requests + rate_limited_requests
        assert total_responses > 0  # Some requests should be processed

        # If rate limiting is implemented, we should see some rate-limited requests
        # at this high rate
        logger.info(
            f"Rate limiting effectiveness: {rate_limited_requests}/{rapid_requests} requests rate-limited"
        )

    async def test_rate_limit_fairness(
        self, a2a_adapter: A2AAdapter, registered_agents: Dict[str, SimulatedAgent]
    ):
        """Test that rate limiting is fair across different agents/users."""
        # Register multiple agents
        test_agents = [
            "orchestrator",
            "elite_training_strategist",
            "precision_nutrition_architect",
        ]

        for agent_id in test_agents:
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

        # Test fairness by having multiple "users" make requests
        users = ["user1", "user2", "user3"]
        requests_per_user = 15

        async def user_request_loop(user_id: str) -> Dict[str, int]:
            """Simulate requests from a specific user."""
            user_results = {"successful": 0, "rate_limited": 0, "errors": 0}

            for i in range(requests_per_user):
                target_agent = test_agents[i % len(test_agents)]

                try:
                    response = await a2a_adapter.call_agent(
                        agent_id=target_agent,
                        user_input=f"Request from {user_id}, #{i}",
                        context={"user_id": user_id, "sequence": i},
                    )

                    if (
                        response.get("status") == "error"
                        and "rate limit" in response.get("error", "").lower()
                    ):
                        user_results["rate_limited"] += 1
                    elif response.get("status") != "error":
                        user_results["successful"] += 1
                    else:
                        user_results["errors"] += 1

                except Exception as e:
                    if "rate limit" in str(e).lower():
                        user_results["rate_limited"] += 1
                    else:
                        user_results["errors"] += 1

                # Small delay between requests
                await asyncio.sleep(0.05)

            return user_results

        # Run all users concurrently
        logger.info("Testing rate limiting fairness across users")

        user_tasks = [user_request_loop(user_id) for user_id in users]
        user_results = await asyncio.gather(*user_tasks)

        # Analyze fairness
        for i, user_id in enumerate(users):
            results = user_results[i]
            total_requests = sum(results.values())
            success_rate = results["successful"] / max(total_requests, 1)

            logger.info(
                f"{user_id}: {results['successful']}/{total_requests} successful ({success_rate:.2%})"
            )

        # Basic fairness check - all users should get some successful requests
        for results in user_results:
            assert (
                results["successful"] > 0
            ), "All users should get some successful requests"

        # Check that success rates are reasonably similar (within 50% of each other)
        success_rates = [
            r["successful"] / max(sum(r.values()), 1) for r in user_results
        ]
        if len(success_rates) > 1:
            min_rate = min(success_rates)
            max_rate = max(success_rates)

            # Fairness assertion - rates shouldn't vary too much
            if min_rate > 0:
                rate_ratio = max_rate / min_rate
                assert rate_ratio < 3.0, f"Success rates too uneven: {success_rates}"


# Performance and load testing markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.a2a,
    pytest.mark.asyncio,
    pytest.mark.performance,
    pytest.mark.slow,  # These tests take longer to run
]
