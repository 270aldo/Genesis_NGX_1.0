"""
NGX Agents Skills Module
========================

This module contains specialized skills that can be mixed into NGX agents
to provide advanced capabilities.
"""

from .collaboration_skills import (
    CollaborationMixin,
    CollaborationMode,
    InteractionStyle,
    CollaborationContext,
    CollaborationTurn,
    CollaborationOrchestrator
)

from .collaboration_intelligence import (
    CollaborationIntelligence,
    CollaborationSuggestion,
    CollaborationTrigger,
    CollaborationUrgency,
    DomainProfile
)

from .advanced_vision_skills import *
from .audio_voice_skills import *  
from .document_analysis_skills import *
from .visualization_skills import *

__all__ = [
    # Collaboration capabilities
    'CollaborationMixin',
    'CollaborationMode', 
    'InteractionStyle',
    'CollaborationContext',
    'CollaborationTurn',
    'CollaborationOrchestrator',
    
    # Collaboration intelligence
    'CollaborationIntelligence',
    'CollaborationSuggestion',
    'CollaborationTrigger',
    'CollaborationUrgency',
    'DomainProfile',
    
    # Other skills (from existing modules)
    # Note: Import all from other skill modules
]