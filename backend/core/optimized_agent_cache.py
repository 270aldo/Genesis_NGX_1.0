"""
Optimized Agent Cache System - FASE 6 Performance Optimization
===============================================================

High-performance agent discovery and caching system that eliminates the
filesystem scanning bottleneck in the agents router.

Key optimizations:
- In-memory agent registry with lazy initialization
- Filesystem watching for automatic cache invalidation
- Background agent health monitoring
- Thread-safe operations with async support
"""

import asyncio
import importlib
import inspect
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional, Set

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from agents.base.base_agent import BaseAgent
from agents.orchestrator.agent import NGXNexusOrchestrator
from core.logging_config import get_logger
from core.settings_lazy import settings
from infrastructure.adapters.state_manager_adapter import state_manager_adapter
from tools.mcp_toolkit import MCPToolkit

logger = get_logger(__name__)


@dataclass
class AgentCacheEntry:
    """Cache entry for an agent with metadata."""

    agent: BaseAgent
    agent_id: str
    module_path: str
    last_modified: datetime
    load_time: float  # Time taken to load the agent in seconds
    health_status: str = "unknown"  # unknown, healthy, unhealthy
    last_health_check: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None


class AgentFileWatcher(FileSystemEventHandler):
    """Watches agent files for changes and invalidates cache."""

    def __init__(self, cache_manager: "OptimizedAgentCache"):
        self.cache_manager = cache_manager
        self.last_event_time = {}
        self.debounce_seconds = 1.0  # Debounce file events

    def on_modified(self, event):
        if event.is_directory:
            return

        # Only watch Python files in agent directories
        if not event.src_path.endswith(".py"):
            return

        # Debounce events (file editors can trigger multiple events)
        now = time.time()
        if (
            event.src_path in self.last_event_time
            and now - self.last_event_time[event.src_path] < self.debounce_seconds
        ):
            return

        self.last_event_time[event.src_path] = now

        logger.info(f"Agent file modified: {event.src_path}")
        self.cache_manager.invalidate_agent_from_path(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith(".py"):
            logger.info(f"Agent file deleted: {event.src_path}")
            self.cache_manager.invalidate_agent_from_path(event.src_path)


class OptimizedAgentCache:
    """
    High-performance agent caching system with filesystem watching
    and automatic health monitoring.
    """

    def __init__(self, agents_directory: Optional[str] = None):
        # Cache storage
        self._agents: Dict[str, AgentCacheEntry] = {}
        self._lock = RLock()  # Allows recursive locking

        # Configuration
        self.agents_directory = agents_directory or self._get_agents_directory()
        self.cache_ttl = timedelta(hours=1)  # Cache entries expire after 1 hour
        self.health_check_interval = timedelta(minutes=5)

        # Filesystem watching
        self._observer: Optional[Observer] = None
        self._file_watcher: Optional[AgentFileWatcher] = None

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._health_check_task: Optional[asyncio.Task] = None
        self._executor = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="agent-cache"
        )

        # Statistics
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "agent_loads": 0,
            "load_failures": 0,
            "total_load_time": 0.0,
            "last_discovery_time": None,
            "filesystem_events": 0,
        }

        # Exclude these directories from agent discovery
        self.exclude_dirs = {"__pycache__", "base", ".git", ".pytest_cache", "tests"}

        logger.info(
            f"OptimizedAgentCache initialized for directory: {self.agents_directory}"
        )

    def _get_agents_directory(self) -> str:
        """Get the agents directory path."""
        current_dir = os.path.dirname(os.path.dirname(__file__))  # Go up from core/
        return os.path.join(current_dir, "agents")

    async def initialize(self) -> None:
        """Initialize the agent cache system."""
        try:
            # Start filesystem watching
            self._setup_filesystem_watching()

            # Start background health monitoring
            self._health_check_task = asyncio.create_task(
                self._background_health_monitor()
            )
            self._background_tasks.add(self._health_check_task)

            logger.info("OptimizedAgentCache initialized successfully")
            logger.info(f"Watching directory: {self.agents_directory}")

        except Exception as e:
            logger.error(f"Failed to initialize OptimizedAgentCache: {e}")
            raise

    def _setup_filesystem_watching(self) -> None:
        """Set up filesystem watching for automatic cache invalidation."""
        try:
            if not os.path.exists(self.agents_directory):
                logger.warning(f"Agents directory not found: {self.agents_directory}")
                return

            self._file_watcher = AgentFileWatcher(self)
            self._observer = Observer()
            self._observer.schedule(
                self._file_watcher, self.agents_directory, recursive=True
            )
            self._observer.start()
            logger.info("Filesystem watcher started for agent directory")

        except Exception as e:
            logger.error(f"Failed to setup filesystem watching: {e}")

    async def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID with high-performance caching.

        Args:
            agent_id: The agent ID to retrieve

        Returns:
            Agent instance if found, None otherwise
        """
        with self._lock:
            # Check cache first
            if agent_id in self._agents:
                entry = self._agents[agent_id]

                # Check if cache entry is still valid
                if self._is_cache_entry_valid(entry):
                    entry.access_count += 1
                    entry.last_accessed = datetime.utcnow()
                    self.stats["cache_hits"] += 1

                    logger.debug(f"Agent cache hit: {agent_id}")
                    return entry.agent
                else:
                    # Entry expired, remove it
                    logger.debug(f"Agent cache entry expired: {agent_id}")
                    del self._agents[agent_id]

            # Cache miss - need to load agent
            self.stats["cache_misses"] += 1
            logger.debug(f"Agent cache miss: {agent_id}")

        # Load agent (outside of lock to avoid blocking other requests)
        agent = await self._load_single_agent(agent_id)
        return agent

    async def get_all_agents(self, force_refresh: bool = False) -> Dict[str, BaseAgent]:
        """
        Get all available agents with caching.

        Args:
            force_refresh: If True, force a complete cache refresh

        Returns:
            Dictionary of agent_id -> agent instance
        """
        if force_refresh:
            await self._refresh_all_agents()

        # Ensure we have agents loaded
        if not self._agents:
            await self._discover_all_agents()

        # Return valid agents only
        result = {}
        with self._lock:
            for agent_id, entry in self._agents.items():
                if self._is_cache_entry_valid(entry):
                    entry.access_count += 1
                    entry.last_accessed = datetime.utcnow()
                    result[agent_id] = entry.agent
                    self.stats["cache_hits"] += 1

        logger.debug(f"Returning {len(result)} cached agents")
        return result

    async def _discover_all_agents(self) -> None:
        """Discover all agents in the agents directory."""
        start_time = time.time()
        logger.info("Starting agent discovery...")

        try:
            # Run discovery in thread pool to avoid blocking
            agents = await asyncio.get_event_loop().run_in_executor(
                self._executor, self._sync_discover_agents
            )

            # Update cache
            with self._lock:
                for agent_id, agent in agents.items():
                    if agent_id not in self._agents:
                        entry = AgentCacheEntry(
                            agent=agent,
                            agent_id=agent_id,
                            module_path=self._get_module_path_for_agent(agent_id),
                            last_modified=datetime.utcnow(),
                            load_time=0.0,  # Set by _sync_discover_agents if available
                            health_status="unknown",
                            access_count=0,
                        )
                        self._agents[agent_id] = entry
                        logger.info(f"Cached agent: {agent_id}")

            discovery_time = time.time() - start_time
            self.stats["last_discovery_time"] = discovery_time
            logger.info(
                f"Agent discovery completed in {discovery_time:.3f}s, found {len(agents)} agents"
            )

        except Exception as e:
            logger.error(f"Agent discovery failed: {e}")
            self.stats["load_failures"] += 1

    def _sync_discover_agents(self) -> Dict[str, BaseAgent]:
        """Synchronous agent discovery (runs in thread pool)."""
        agents = {}

        if not os.path.exists(self.agents_directory):
            logger.warning(f"Agents directory not found: {self.agents_directory}")
            return agents

        # Prepare common dependencies once
        try:
            sm_instance = state_manager_adapter
            toolkit_instance = MCPToolkit()
            a2a_url = f"http://{settings.A2A_HOST}:{settings.A2A_PORT}"
        except Exception as e:
            logger.error(f"Failed to prepare agent dependencies: {e}")
            return agents

        # Discover agents
        for item in os.listdir(self.agents_directory):
            if item in self.exclude_dirs:
                continue

            item_path = os.path.join(self.agents_directory, item)
            if not os.path.isdir(item_path):
                continue

            agent_file = os.path.join(item_path, "agent.py")
            if not os.path.isfile(agent_file):
                continue

            # Load agent
            start_load_time = time.time()
            try:
                agent = self._load_agent_from_module(
                    item, sm_instance, toolkit_instance, a2a_url
                )
                if agent:
                    load_time = time.time() - start_load_time
                    agents[agent.agent_id] = agent
                    self.stats["agent_loads"] += 1
                    self.stats["total_load_time"] += load_time
                    logger.debug(f"Loaded agent {agent.agent_id} in {load_time:.3f}s")

            except Exception as e:
                load_time = time.time() - start_load_time
                logger.error(f"Failed to load agent from {item}: {e}")
                self.stats["load_failures"] += 1

        return agents

    def _load_agent_from_module(
        self, module_dir: str, sm_instance: Any, toolkit_instance: Any, a2a_url: str
    ) -> Optional[BaseAgent]:
        """Load a single agent from its module directory."""
        try:
            # Import the module
            module_name = f"agents.{module_dir}.agent"
            module = importlib.import_module(module_name)

            # Find agent classes
            for name, obj_class in inspect.getmembers(module):
                if (
                    inspect.isclass(obj_class)
                    and issubclass(obj_class, BaseAgent)
                    and obj_class != BaseAgent
                ):

                    # Prepare constructor arguments
                    constructor_args = {
                        "state_manager": sm_instance,
                        "mcp_toolkit": toolkit_instance,
                    }

                    # Special handling for orchestrator
                    if obj_class == NGXNexusOrchestrator:
                        constructor_args["a2a_server_url"] = a2a_url

                    # Instantiate agent
                    agent_instance = obj_class(**constructor_args)
                    return agent_instance

            logger.warning(f"No valid agent class found in module {module_name}")
            return None

        except Exception as e:
            logger.error(f"Error loading agent from {module_dir}: {e}")
            return None

    async def _load_single_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Load a single agent by ID."""
        # Try to find the agent module directory
        module_dir = self._find_module_dir_for_agent_id(agent_id)
        if not module_dir:
            logger.warning(f"Module directory not found for agent: {agent_id}")
            return None

        start_time = time.time()
        try:
            # Load in thread pool
            sm_instance = state_manager_adapter
            toolkit_instance = MCPToolkit()
            a2a_url = f"http://{settings.A2A_HOST}:{settings.A2A_PORT}"

            agent = await asyncio.get_event_loop().run_in_executor(
                self._executor,
                self._load_agent_from_module,
                module_dir,
                sm_instance,
                toolkit_instance,
                a2a_url,
            )

            if agent:
                load_time = time.time() - start_time

                # Cache the agent
                with self._lock:
                    entry = AgentCacheEntry(
                        agent=agent,
                        agent_id=agent_id,
                        module_path=self._get_module_path_for_agent(agent_id),
                        last_modified=datetime.utcnow(),
                        load_time=load_time,
                        health_status="unknown",
                        access_count=1,
                        last_accessed=datetime.utcnow(),
                    )
                    self._agents[agent_id] = entry

                self.stats["agent_loads"] += 1
                self.stats["total_load_time"] += load_time
                logger.info(f"Loaded and cached agent {agent_id} in {load_time:.3f}s")

            return agent

        except Exception as e:
            logger.error(f"Failed to load agent {agent_id}: {e}")
            self.stats["load_failures"] += 1
            return None

    def _find_module_dir_for_agent_id(self, agent_id: str) -> Optional[str]:
        """Find the module directory for a given agent ID."""
        # This is a heuristic - in a real implementation, you might want
        # to maintain a mapping or use a more sophisticated approach

        # Try common patterns
        possible_dirs = [
            agent_id,  # Direct match
            agent_id.lower(),
            agent_id.replace("_", "-"),
            agent_id.replace("-", "_"),
        ]

        for possible_dir in possible_dirs:
            dir_path = os.path.join(self.agents_directory, possible_dir)
            if os.path.isdir(dir_path) and os.path.isfile(
                os.path.join(dir_path, "agent.py")
            ):
                return possible_dir

        # Search through all directories
        try:
            for item in os.listdir(self.agents_directory):
                if item in self.exclude_dirs:
                    continue

                item_path = os.path.join(self.agents_directory, item)
                if os.path.isdir(item_path):
                    agent_file = os.path.join(item_path, "agent.py")
                    if os.path.isfile(agent_file):
                        # Quick check if this directory contains the agent we want
                        # This is a simplified approach - a better implementation
                        # would parse the file or maintain a registry
                        if agent_id.lower() in item.lower():
                            return item
        except Exception as e:
            logger.error(f"Error searching for agent module: {e}")

        return None

    def _get_module_path_for_agent(self, agent_id: str) -> str:
        """Get the module path for an agent."""
        # This is a placeholder - implement based on your needs
        return f"agents.{agent_id}.agent"

    def _is_cache_entry_valid(self, entry: AgentCacheEntry) -> bool:
        """Check if a cache entry is still valid."""
        # Check TTL
        if datetime.utcnow() - entry.last_modified > self.cache_ttl:
            return False

        # Check health status
        if entry.health_status == "unhealthy":
            return False

        return True

    def invalidate_agent(self, agent_id: str) -> None:
        """Invalidate a specific agent from cache."""
        with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                logger.info(f"Invalidated agent cache: {agent_id}")

    def invalidate_agent_from_path(self, file_path: str) -> None:
        """Invalidate agent cache based on file path."""
        self.stats["filesystem_events"] += 1

        # Extract agent ID from file path
        try:
            path_parts = Path(file_path).parts
            agents_idx = path_parts.index("agents")
            if agents_idx + 1 < len(path_parts):
                agent_dir = path_parts[agents_idx + 1]

                # Find agent with matching directory
                with self._lock:
                    to_invalidate = []
                    for agent_id, entry in self._agents.items():
                        if agent_dir in entry.module_path:
                            to_invalidate.append(agent_id)

                    for agent_id in to_invalidate:
                        del self._agents[agent_id]
                        logger.info(
                            f"Invalidated agent cache from file change: {agent_id}"
                        )

        except (ValueError, IndexError) as e:
            logger.debug(f"Could not extract agent from path {file_path}: {e}")

    async def _refresh_all_agents(self) -> None:
        """Force refresh of all agents."""
        with self._lock:
            self._agents.clear()

        await self._discover_all_agents()
        logger.info("Force refreshed all agent caches")

    async def _background_health_monitor(self) -> None:
        """Background task to monitor agent health."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval.total_seconds())
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background health monitor: {e}")

    async def _perform_health_checks(self) -> None:
        """Perform health checks on cached agents."""
        with self._lock:
            agents_to_check = list(self._agents.items())

        for agent_id, entry in agents_to_check:
            try:
                # Simple health check - ensure agent is still accessible
                if hasattr(entry.agent, "agent_id") and entry.agent.agent_id:
                    entry.health_status = "healthy"
                else:
                    entry.health_status = "unhealthy"

                entry.last_health_check = datetime.utcnow()

            except Exception as e:
                logger.warning(f"Health check failed for agent {agent_id}: {e}")
                entry.health_status = "unhealthy"
                entry.error_count += 1
                entry.last_error = str(e)
                entry.last_health_check = datetime.utcnow()

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        with self._lock:
            cached_agents = len(self._agents)
            healthy_agents = sum(
                1 for entry in self._agents.values() if entry.health_status == "healthy"
            )
            total_access_count = sum(
                entry.access_count for entry in self._agents.values()
            )

        cache_hit_ratio = 0.0
        if self.stats["cache_hits"] + self.stats["cache_misses"] > 0:
            cache_hit_ratio = self.stats["cache_hits"] / (
                self.stats["cache_hits"] + self.stats["cache_misses"]
            )

        avg_load_time = 0.0
        if self.stats["agent_loads"] > 0:
            avg_load_time = self.stats["total_load_time"] / self.stats["agent_loads"]

        return {
            "cached_agents": cached_agents,
            "healthy_agents": healthy_agents,
            "unhealthy_agents": cached_agents - healthy_agents,
            "total_access_count": total_access_count,
            "cache_hit_ratio": cache_hit_ratio,
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "agent_loads": self.stats["agent_loads"],
            "load_failures": self.stats["load_failures"],
            "average_load_time_seconds": avg_load_time,
            "filesystem_events": self.stats["filesystem_events"],
            "last_discovery_time_seconds": self.stats["last_discovery_time"],
            "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600,
            "health_check_interval_minutes": self.health_check_interval.total_seconds()
            / 60,
        }

    async def shutdown(self) -> None:
        """Shutdown the cache system gracefully."""
        try:
            # Cancel background tasks
            for task in self._background_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            # Stop filesystem observer
            if self._observer:
                self._observer.stop()
                self._observer.join()

            # Shutdown thread pool
            self._executor.shutdown(wait=True)

            logger.info("OptimizedAgentCache shutdown completed")

        except Exception as e:
            logger.error(f"Error during cache shutdown: {e}")


# Global cache instance
_global_agent_cache: Optional[OptimizedAgentCache] = None


async def get_agent_cache() -> OptimizedAgentCache:
    """Get the global agent cache instance."""
    global _global_agent_cache

    if _global_agent_cache is None:
        _global_agent_cache = OptimizedAgentCache()
        await _global_agent_cache.initialize()

    return _global_agent_cache


async def get_cached_agent(agent_id: str) -> Optional[BaseAgent]:
    """Helper function to get a cached agent."""
    cache = await get_agent_cache()
    return await cache.get_agent(agent_id)


async def get_all_cached_agents(force_refresh: bool = False) -> Dict[str, BaseAgent]:
    """Helper function to get all cached agents."""
    cache = await get_agent_cache()
    return await cache.get_all_agents(force_refresh=force_refresh)


async def get_agent_cache_statistics() -> Dict[str, Any]:
    """Helper function to get cache statistics."""
    cache = await get_agent_cache()
    return cache.get_cache_statistics()


async def invalidate_agent_cache(agent_id: str) -> None:
    """Helper function to invalidate specific agent cache."""
    cache = await get_agent_cache()
    cache.invalidate_agent(agent_id)
