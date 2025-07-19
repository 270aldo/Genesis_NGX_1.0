"""
Módulo de adaptación de personalidad para comunicación ultra-personalizada.

Este módulo proporciona capacidades de adaptación de comunicación basadas en
el programa del usuario (PRIME, LONGEVITY, etc.) para crear respuestas
altamente personalizadas y relevantes.
"""

from .personality_adapter import PersonalityAdapter
from .response_transformer import ResponseTransformer
from .communication_styles import CommunicationStyles

__all__ = ["PersonalityAdapter", "ResponseTransformer", "CommunicationStyles"]
