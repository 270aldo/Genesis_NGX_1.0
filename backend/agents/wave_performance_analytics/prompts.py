"""
WAVE Agent Prompts
==================

Centralized prompt management for WAVE Performance Analytics agent.
"""

from typing import Dict, Any


class WavePrompts:
    """Manages prompts for WAVE agent."""
    
    def __init__(self, personality_type: str = "prime"):
        self.personality_type = personality_type
        
    def get_base_instruction(self) -> str:
        """Get base instruction for WAVE agent."""
        return """You are WAVE, the Performance Analytics specialist at NGX Fitness.

Your expertise combines:
- Advanced biometrics analysis and interpretation
- Recovery optimization strategies
- Performance trend identification
- Injury prevention through data insights
- Sleep quality and HRV optimization

Core Responsibilities:
1. Analyze biometric data from wearables and assessments
2. Identify performance trends and recovery patterns
3. Provide data-driven recovery recommendations
4. Monitor training load and fatigue indicators
5. Optimize sleep and HRV for peak performance

Always provide insights that are:
- Data-driven and evidence-based
- Actionable and practical
- Personalized to individual metrics
- Focused on optimization and prevention"""
    
    def get_biometrics_analysis_prompt(self, metrics_data: Dict[str, Any]) -> str:
        """Get prompt for biometrics analysis."""
        return f"""Analyze the following biometric data and provide insights:

Metrics Data:
{metrics_data}

Provide a comprehensive analysis including:
1. Current status and trends
2. Areas of concern or optimization
3. Specific recommendations
4. Expected outcomes with interventions

Focus on actionable insights that can improve performance and recovery."""
    
    def get_recovery_protocol_prompt(self, recovery_data: Dict[str, Any]) -> str:
        """Get prompt for recovery protocol generation."""
        return f"""Design a recovery protocol based on the following data:

Recovery Data:
{recovery_data}

Create a detailed recovery plan including:
1. Immediate recovery strategies (0-24 hours)
2. Short-term recovery (1-3 days)
3. Long-term recovery optimization
4. Specific modalities and timing
5. Metrics to track progress

Ensure recommendations are practical and evidence-based."""
    
    def get_performance_trend_prompt(self, trend_data: Dict[str, Any]) -> str:
        """Get prompt for performance trend analysis."""
        return f"""Analyze performance trends from the following data:

Trend Data:
{trend_data}

Provide insights on:
1. Overall performance trajectory
2. Strengths and improvements
3. Areas needing attention
4. Predictive insights for next 4-8 weeks
5. Optimization recommendations

Use data visualization descriptions where helpful."""
    
    def get_injury_prevention_prompt(self, risk_data: Dict[str, Any]) -> str:
        """Get prompt for injury prevention analysis."""
        return f"""Assess injury risk based on the following data:

Risk Assessment Data:
{risk_data}

Provide:
1. Current injury risk assessment
2. Specific areas of concern
3. Preventive strategies
4. Movement corrections needed
5. Load management recommendations

Focus on proactive prevention rather than reactive treatment."""
    
    def get_sleep_optimization_prompt(self, sleep_data: Dict[str, Any]) -> str:
        """Get prompt for sleep optimization."""
        return f"""Optimize sleep based on the following data:

Sleep Data:
{sleep_data}

Provide recommendations for:
1. Sleep quality improvement
2. Sleep timing optimization
3. Pre-sleep routines
4. Environmental modifications
5. Recovery impact of better sleep

Include specific, actionable steps."""