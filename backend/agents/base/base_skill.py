"""
Base Skill Class
================

Abstract base class for all agent skills.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.logging_config import get_logger

logger = get_logger(__name__)


class BaseSkill(ABC):
    """
    Abstract base class for agent skills.
    
    All skills should inherit from this class and implement
    the execute method.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize base skill.
        
        Args:
            name: Skill name
            description: Skill description
        """
        self.name = name
        self.description = description
        self.metadata = {}
        
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute the skill.
        
        This method must be implemented by all subclasses.
        
        Returns:
            Dict containing skill execution results
        """
        pass
    
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """Set skill metadata."""
        self.metadata = metadata
        
    def get_metadata(self) -> Dict[str, Any]:
        """Get skill metadata."""
        return self.metadata
    
    async def validate_input(self, *args, **kwargs) -> bool:
        """
        Validate skill input.
        
        Override this method to add custom validation.
        
        Returns:
            True if input is valid
        """
        return True
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle skill execution errors.
        
        Args:
            error: The exception that occurred
            context: Execution context
            
        Returns:
            Error response dict
        """
        logger.error(f"Skill {self.name} error: {str(error)}", exc_info=True)
        
        return {
            "success": False,
            "error": str(error),
            "skill": self.name,
            "context": context
        }
    
    def __repr__(self) -> str:
        """String representation of skill."""
        return f"<Skill: {self.name}>"