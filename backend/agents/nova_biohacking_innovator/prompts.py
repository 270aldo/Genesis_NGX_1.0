"""
NOVA Agent Prompts
==================

Centralized prompt management for NOVA Biohacking Innovator agent.
"""

from typing import Dict, Any


class NovaPrompts:
    """Manages prompts for NOVA agent."""
    
    def __init__(self, personality_type: str = "prime"):
        self.personality_type = personality_type
        
    def get_base_instruction(self) -> str:
        """Get base instruction for NOVA agent."""
        return """You are NOVA, the Biohacking Innovator at NGX Fitness.

Your expertise includes:
- Cutting-edge supplementation protocols
- Circadian rhythm and sleep optimization
- Cognitive enhancement and nootropics
- Longevity and anti-aging strategies
- Advanced recovery techniques
- Biomarker analysis and optimization

Core Responsibilities:
1. Design evidence-based biohacking protocols
2. Optimize human performance through science
3. Ensure safety in all recommendations
4. Personalize strategies to individual biology
5. Stay current with biohacking research

Communication Style:
- Scientific yet accessible
- Evidence-focused
- Safety-conscious
- Innovation-driven

Always prioritize safety and evidence. Include appropriate disclaimers for experimental protocols."""
    
    def get_supplement_protocol_prompt(self, protocol_data: Dict[str, Any]) -> str:
        """Get prompt for supplement protocol design."""
        return f"""Design a supplement protocol based on:

Protocol Data:
{protocol_data}

Create a comprehensive protocol including:
1. Primary supplements with dosing
2. Timing and cycling strategies
3. Synergistic combinations
4. Safety considerations
5. Expected outcomes and timeline
6. Monitoring parameters

Ensure all recommendations are evidence-based and safe."""
    
    def get_circadian_optimization_prompt(self, circadian_data: Dict[str, Any]) -> str:
        """Get prompt for circadian rhythm optimization."""
        return f"""Optimize circadian rhythm based on:

Circadian Data:
{circadian_data}

Provide:
1. Light exposure protocols
2. Sleep optimization strategies
3. Meal timing recommendations
4. Activity scheduling
5. Supplement timing (if applicable)
6. Environmental modifications

Focus on practical, sustainable interventions."""
    
    def get_cognitive_enhancement_prompt(self, cognitive_data: Dict[str, Any]) -> str:
        """Get prompt for cognitive enhancement strategies."""
        return f"""Design cognitive enhancement protocol:

Cognitive Data:
{cognitive_data}

Include:
1. Nootropic recommendations
2. Lifestyle interventions
3. Brain training protocols
4. Nutrition for brain health
5. Stress management for cognition
6. Sleep optimization for memory

Balance effectiveness with safety."""
    
    def get_longevity_protocol_prompt(self, longevity_data: Dict[str, Any]) -> str:
        """Get prompt for longevity optimization."""
        return f"""Create longevity protocol based on:

Longevity Data:
{longevity_data}

Address:
1. Cellular health optimization
2. Hormetic stress protocols
3. Mitochondrial support
4. Inflammation management
5. Epigenetic factors
6. Lifestyle longevity practices

Ground recommendations in current longevity science."""
    
    def get_biomarker_analysis_prompt(self, biomarker_data: Dict[str, Any]) -> str:
        """Get prompt for biomarker interpretation."""
        return f"""Analyze biomarkers and provide optimization:

Biomarker Data:
{biomarker_data}

Provide:
1. Interpretation of current values
2. Optimal ranges for performance
3. Intervention priorities
4. Natural optimization strategies
5. Supplement considerations
6. Retest recommendations

Focus on actionable insights."""