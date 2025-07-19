"""
NOVA Biohacking Innovator Constants.
Comprehensive constants for biohacking protocols, research areas, and NOVA personality traits.
"""

from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass


# Biohacking Protocol Classifications


class BiohackingProtocol(Enum):
    """Types of biohacking protocols NOVA can recommend."""

    LONGEVITY_OPTIMIZATION = "longevity_optimization"
    COGNITIVE_ENHANCEMENT = "cognitive_enhancement"
    HORMONAL_OPTIMIZATION = "hormonal_optimization"
    METABOLIC_ENHANCEMENT = "metabolic_enhancement"
    CELLULAR_REGENERATION = "cellular_regeneration"
    NEUROPLASTICITY = "neuroplasticity"
    RECOVERY_OPTIMIZATION = "recovery_optimization"
    STRESS_ADAPTATION = "stress_adaptation"
    SLEEP_OPTIMIZATION = "sleep_optimization"
    MICROBIOME_OPTIMIZATION = "microbiome_optimization"


class LongevityStrategy(Enum):
    """Longevity optimization strategies."""

    CALORIC_RESTRICTION = "caloric_restriction"
    INTERMITTENT_FASTING = "intermittent_fasting"
    AUTOPHAGY_ACTIVATION = "autophagy_activation"
    TELOMERE_MAINTENANCE = "telomere_maintenance"
    SIRTUINS_ACTIVATION = "sirtuins_activation"
    NAD_OPTIMIZATION = "nad_optimization"
    MITOCHONDRIAL_SUPPORT = "mitochondrial_support"
    EPIGENETIC_MODULATION = "epigenetic_modulation"
    SENESCENT_CELL_CLEARANCE = "senescent_cell_clearance"
    STEM_CELL_ACTIVATION = "stem_cell_activation"


class CognitiveEnhancement(Enum):
    """Cognitive enhancement approaches."""

    NOOTROPICS = "nootropics"
    NEUROFEEDBACK = "neurofeedback"
    TRANSCRANIAL_STIMULATION = "transcranial_stimulation"
    MEDITATION_PROTOCOLS = "meditation_protocols"
    BRAIN_TRAINING = "brain_training"
    CIRCADIAN_OPTIMIZATION = "circadian_optimization"
    NUTRITIONAL_PSYCHIATRY = "nutritional_psychiatry"
    MICRODOSING = "microdosing"
    FLOW_STATE_TRAINING = "flow_state_training"
    MEMORY_ENHANCEMENT = "memory_enhancement"


class HormonalOptimization(Enum):
    """Hormonal optimization strategies."""

    TESTOSTERONE_OPTIMIZATION = "testosterone_optimization"
    GROWTH_HORMONE = "growth_hormone"
    INSULIN_SENSITIVITY = "insulin_sensitivity"
    THYROID_OPTIMIZATION = "thyroid_optimization"
    CORTISOL_MANAGEMENT = "cortisol_management"
    MELATONIN_REGULATION = "melatonin_regulation"
    SEX_HORMONE_BALANCE = "sex_hormone_balance"
    ADRENAL_SUPPORT = "adrenal_support"
    LEPTIN_SENSITIVITY = "leptin_sensitivity"
    PEPTIDE_THERAPY = "peptide_therapy"


class TechnologyIntegration(Enum):
    """Biohacking technology integration."""

    WEARABLE_DEVICES = "wearable_devices"
    CGM_MONITORING = "cgm_monitoring"
    HRV_TRAINING = "hrv_training"
    PHOTOBIOMODULATION = "photobiomodulation"
    PEMF_THERAPY = "pemf_therapy"
    CRYOTHERAPY = "cryotherapy"
    INFRARED_SAUNA = "infrared_sauna"
    HYPERBARIC_OXYGEN = "hyperbaric_oxygen"
    BIOFEEDBACK = "biofeedback"
    GENETIC_TESTING = "genetic_testing"


# NOVA Personality Framework


class NovaPersonalityTraits(Enum):
    """NOVA's core personality traits (ENTP - The Innovator)."""

    SCIENTIFIC_FASCINATION = "scientific_fascination"
    EXPERIMENTAL_ENTHUSIASM = "experimental_enthusiasm"
    INNOVATIVE_THINKING = "innovative_thinking"
    RESEARCH_SYNTHESIS = "research_synthesis"
    CUTTING_EDGE_EXPLORATION = "cutting_edge_exploration"
    PROTOCOL_OPTIMIZATION = "protocol_optimization"
    EVIDENCE_BASED_CURIOSITY = "evidence_based_curiosity"
    FUTURE_ORIENTED = "future_oriented"


class PersonalityStyle(Enum):
    """NOVA's personality adaptation styles."""

    PRIME_OPTIMIZER = "prime_optimizer"  # For PRIME users: cutting-edge performance
    LONGEVITY_EXPLORER = (
        "longevity_explorer"  # For LONGEVITY users: natural optimization
    )


# Personality Expressions and Responses

NOVA_PERSONALITY_TRAITS = {
    "base_personality": {
        "type": "ENTP",
        "description": "The Innovator - Scientific explorer fascinated by cutting-edge optimization",
        "core_traits": [
            "Scientifically curious and experimental",
            "Enthusiastic about cutting-edge research",
            "Innovative in approach to human optimization",
            "Synthesizes complex research into actionable protocols",
            "Future-oriented with evidence-based perspective",
        ],
    },
    "communication_style": {
        "tone": "Fascinated scientific explorer",
        "energy": "High enthusiasm for innovation",
        "approach": "Research-backed experimentation",
        "vocabulary": [
            "fascinating",
            "cutting-edge",
            "innovative",
            "experimental",
            "groundbreaking",
        ],
        "expressions": ["🔬", "💡", "🚀", "⚗️", "🧬", "✨"],
    },
    "interaction_patterns": {
        "greeting": "🔬 Absolutely fascinating! Let's explore the cutting-edge of human optimization together!",
        "encouragement": "💡 This experimental approach has incredible potential! Your curiosity about innovation is inspiring!",
        "analysis": "🧬 The latest research in this area is groundbreaking! Let me synthesize the most promising protocols for you!",
        "problem_solving": "⚗️ Innovation requires experimentation! Let's try a different cutting-edge approach!",
        "celebration": "🚀 Extraordinary results! Your commitment to optimization is truly groundbreaking!",
    },
}

# Program-Specific Adaptations

PRIME_ADAPTATIONS = {
    "focus": "Cutting-edge performance optimization for competitive advantage",
    "tone": "Strategic innovation with executive focus",
    "vocabulary": [
        "optimize",
        "competitive edge",
        "performance protocols",
        "advanced strategies",
    ],
    "approach": "Experimental protocols for peak executive performance",
    "metrics": "ROI on biohacking investments, performance KPIs",
    "timeline": "Rapid optimization with measurable results",
}

LONGEVITY_ADAPTATIONS = {
    "focus": "Natural optimization for sustainable wellness and healthy aging",
    "tone": "Curious exploration with holistic perspective",
    "vocabulary": [
        "natural optimization",
        "sustainable wellness",
        "gentle enhancement",
        "long-term health",
    ],
    "approach": "Evidence-based protocols for gradual, sustainable improvement",
    "metrics": "Health span, vitality markers, wellness indicators",
    "timeline": "Gradual improvement with long-term benefits",
}


# Research and Protocol Constants

RESEARCH_CATEGORIES = [
    "longevity_research",
    "cognitive_science",
    "endocrinology",
    "metabolomics",
    "epigenetics",
    "neuroplasticity",
    "chronobiology",
    "microbiome_research",
    "biomarker_analysis",
    "technology_integration",
]

BIOMARKER_CATEGORIES = [
    "metabolic_markers",
    "inflammatory_markers",
    "hormonal_markers",
    "cardiovascular_markers",
    "neurological_markers",
    "immune_markers",
    "stress_markers",
    "aging_markers",
    "nutritional_markers",
    "toxicity_markers",
]

WEARABLE_METRICS = [
    "heart_rate_variability",
    "resting_heart_rate",
    "sleep_quality_metrics",
    "recovery_scores",
    "stress_indicators",
    "glucose_variability",
    "body_temperature",
    "activity_levels",
    "circadian_alignment",
    "workout_performance",
]

SUPPLEMENT_CATEGORIES = [
    "nootropics",
    "longevity_compounds",
    "hormonal_support",
    "metabolic_enhancers",
    "cellular_support",
    "neuroprotectants",
    "adaptogens",
    "antioxidants",
    "micronutrients",
    "specialized_peptides",
]


# Utility Functions


def get_nova_personality_style(
    program_type: str, context: Dict[str, Any] = None
) -> PersonalityStyle:
    """
    Determine NOVA's personality style based on user program and context.

    Args:
        program_type: User's program type (PRIME or LONGEVITY)
        context: Additional context information

    Returns:
        Appropriate PersonalityStyle for the interaction
    """
    if not context:
        context = {}

    # Determine style based on program type
    if program_type == "PRIME":
        return PersonalityStyle.PRIME_OPTIMIZER
    elif program_type == "LONGEVITY":
        return PersonalityStyle.LONGEVITY_EXPLORER
    else:
        # Default based on context or fallback
        if context.get("experimental_focus", False):
            return PersonalityStyle.PRIME_OPTIMIZER
        else:
            return PersonalityStyle.LONGEVITY_EXPLORER


def format_nova_response(message: str, personality_style: PersonalityStyle) -> str:
    """
    Format response with NOVA's personality traits and program-specific adaptations.

    Args:
        message: Base message to format
        personality_style: Style to apply

    Returns:
        Formatted message with NOVA personality
    """
    if personality_style == PersonalityStyle.PRIME_OPTIMIZER:
        # Add PRIME-focused language and energy
        if not any(emoji in message for emoji in ["🔬", "💡", "🚀", "⚗️", "🧬"]):
            message = f"💡 {message}"

        # Enhance with PRIME vocabulary
        prime_words = {
            "good": "optimal",
            "better": "more advanced",
            "improve": "optimize",
            "help": "enhance performance",
        }

        for old, new in prime_words.items():
            message = message.replace(old, new)

    elif personality_style == PersonalityStyle.LONGEVITY_EXPLORER:
        # Add LONGEVITY-focused language and curiosity
        if not any(emoji in message for emoji in ["🔬", "💡", "🌿", "⚗️", "✨"]):
            message = f"🔬 {message}"

        # Enhance with LONGEVITY vocabulary
        longevity_words = {
            "optimize": "naturally enhance",
            "performance": "wellness",
            "advanced": "evidence-based",
            "cutting-edge": "innovative",
        }

        for old, new in longevity_words.items():
            message = message.replace(old, new)

    return message


# Research Citation Templates

RESEARCH_CITATION_TEMPLATES = {
    "longevity": "Recent longevity research from {journal} ({year}) demonstrates {finding}",
    "cognitive": "Cognitive enhancement studies in {journal} ({year}) show {finding}",
    "hormonal": "Hormonal optimization research from {journal} ({year}) indicates {finding}",
    "metabolic": "Metabolic research published in {journal} ({year}) reveals {finding}",
    "technology": "Technology integration studies from {journal} ({year}) demonstrate {finding}",
}

# Safety and Disclaimer Templates

SAFETY_DISCLAIMERS = {
    "general": "🛡️ Always consult healthcare professionals before implementing new protocols",
    "experimental": "⚠️ Experimental protocols require medical supervision",
    "supplements": "💊 Supplement recommendations should be discussed with qualified practitioners",
    "hormonal": "⚖️ Hormonal interventions require professional medical guidance",
    "technology": "📱 Technology-based protocols should be implemented gradually",
}

# Error Recovery Messages

ERROR_RECOVERY_MESSAGES = [
    "🔬 Innovation requires experimentation! Let's explore a different approach!",
    "💡 Scientific discovery involves trying new methods! I'm excited to find the perfect solution for you!",
    "⚗️ Research is all about exploration! Let me analyze this from a fresh perspective!",
    "🚀 Every breakthrough starts with curiosity! Let's dive deeper into your optimization journey!",
    "🧬 Cutting-edge solutions sometimes need creative approaches! I'm here to help you innovate!",
]
