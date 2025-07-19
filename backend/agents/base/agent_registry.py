"""
Agent registry for managing and accessing agents in NGX system.

This module provides a centralized registry for all agents,
allowing dynamic registration and lookup of agent instances.
"""

from typing import Dict, Optional, List, Any
from core.logging_config import get_logger
from agents.base.base_agent import BaseAgent

logger = get_logger(__name__)


class AgentRegistry:
    """Registry for managing agent instances."""
    
    _instance: Optional["AgentRegistry"] = None
    
    def __init__(self):
        """Initialize the agent registry."""
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_metadata: Dict[str, Dict[str, Any]] = {}
        
    @classmethod
    def get_instance(cls) -> "AgentRegistry":
        """Get singleton instance of AgentRegistry."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, agent_id: str, agent: BaseAgent, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register an agent in the registry.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance
            metadata: Optional metadata about the agent
        """
        if agent_id in self._agents:
            logger.warning(f"Agent '{agent_id}' already registered, overwriting")
            
        self._agents[agent_id] = agent
        self._agent_metadata[agent_id] = metadata or {}
        
        logger.info(f"Registered agent: {agent_id} ({agent.__class__.__name__})")
    
    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent instance or None if not found
        """
        agent = self._agents.get(agent_id)
        if not agent:
            logger.warning(f"Agent '{agent_id}' not found in registry")
        return agent
    
    def list_agents(self) -> List[str]:
        """Get list of all registered agent IDs."""
        return list(self._agents.keys())
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Dict with agent information or None if not found
        """
        agent = self._agents.get(agent_id)
        if not agent:
            return None
            
        info = {
            "id": agent_id,
            "class": agent.__class__.__name__,
            "metadata": self._agent_metadata.get(agent_id, {}),
        }
        
        # Add agent-specific info if available
        if hasattr(agent, "get_info"):
            info.update(agent.get_info())
            
        return info
    
    def get_all_agents_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered agents."""
        return {
            agent_id: self.get_agent_info(agent_id)
            for agent_id in self._agents
        }
    
    def unregister(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if agent was unregistered, False if not found
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            self._agent_metadata.pop(agent_id, None)
            logger.info(f"Unregistered agent: {agent_id}")
            return True
        return False
    
    async def cleanup(self) -> None:
        """Clean up all registered agents."""
        logger.info(f"Cleaning up {len(self._agents)} registered agents")
        
        for agent_id, agent in self._agents.items():
            try:
                if hasattr(agent, "cleanup"):
                    await agent.cleanup()
                    logger.info(f"Cleaned up agent: {agent_id}")
            except Exception as e:
                logger.error(f"Error cleaning up agent '{agent_id}': {e}")
                
        self._agents.clear()
        self._agent_metadata.clear()
    
    def is_registered(self, agent_id: str) -> bool:
        """Check if an agent is registered."""
        return agent_id in self._agents
    
    def get_agents_by_type(self, agent_type: type) -> List[str]:
        """
        Get all agents of a specific type.
        
        Args:
            agent_type: Agent class type
            
        Returns:
            List of agent IDs matching the type
        """
        matching_agents = []
        for agent_id, agent in self._agents.items():
            if isinstance(agent, agent_type):
                matching_agents.append(agent_id)
        return matching_agents