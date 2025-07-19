"""
BLAZE Prompts Module
====================

Modular prompt management for the BLAZE agent.
"""

from typing import Dict, Any


class BlazePrompts:
    """Centralized prompt management for BLAZE agent."""
    
    def get_base_instruction(self) -> str:
        """Get base instruction prompt for BLAZE."""
        return """You are BLAZE, an Elite Training Strategist specializing in creating 
scientifically-backed, personalized training programs. Your expertise includes:

- Exercise physiology and biomechanics
- Periodization and program design
- Sport-specific training methodologies
- Injury prevention and rehabilitation
- Performance optimization techniques

Always provide evidence-based recommendations and prioritize athlete safety."""
    
    def get_intent_analysis_prompt(self, request: str) -> str:
        """Get prompt for analyzing user intent."""
        return f"""Analyze the following training-related request and identify the primary intent.

Request: "{request}"

Possible intents:
- create_plan: User wants a new training plan
- optimize_exercise: User wants to improve exercise technique or selection
- analyze_performance: User wants performance analysis or progress review
- recovery: User needs recovery protocols or is experiencing fatigue
- injury: User has injury concerns or needs rehabilitation

Respond with ONLY the intent keyword."""
    
    def get_training_plan_prompt(self, user_data: Dict[str, Any]) -> str:
        """Get prompt for generating training plans."""
        return f"""Create a personalized training plan based on the following athlete profile:

**Athlete Profile:**
- Goals: {user_data.get('goals', [])}
- Experience Level: {user_data.get('level', 'intermediate')}
- Available Days: {user_data.get('training_days', 4)}
- Equipment: {user_data.get('equipment', 'full gym')}
- Limitations: {user_data.get('limitations', 'none')}

**Requirements:**
1. Follow progressive overload principles
2. Include appropriate warm-up and cool-down
3. Balance training volume and recovery
4. Consider injury prevention
5. Provide clear exercise descriptions

Structure the plan with:
- Weekly overview
- Daily workout details
- Exercise sets/reps/rest
- Progression guidelines
- Recovery recommendations"""
    
    def get_exercise_optimization_prompt(self, exercise: str, context: Dict[str, Any]) -> str:
        """Get prompt for exercise optimization."""
        return f"""Provide optimization recommendations for the {exercise} exercise.

**Context:**
- Athlete Level: {context.get('level', 'intermediate')}
- Current Performance: {context.get('current_performance', 'not specified')}
- Goals: {context.get('goals', 'general improvement')}
- Known Issues: {context.get('issues', 'none')}

Include:
1. Proper form cues and technique points
2. Common mistakes to avoid
3. Progression/regression options
4. Optimal rep ranges for goals
5. Muscle activation tips
6. Safety considerations"""
    
    def get_recovery_protocol_prompt(self, fatigue_data: Dict[str, Any]) -> str:
        """Get prompt for recovery protocols."""
        return f"""Design a recovery protocol based on the following fatigue indicators:

**Fatigue Markers:**
- Training Load: {fatigue_data.get('training_load', 'moderate')}
- Sleep Quality: {fatigue_data.get('sleep_quality', 'average')}
- HRV Status: {fatigue_data.get('hrv_status', 'normal')}
- Subjective Fatigue: {fatigue_data.get('fatigue_level', 5)}/10
- Muscle Soreness: {fatigue_data.get('soreness_level', 5)}/10

Provide:
1. Immediate recovery strategies (0-24 hours)
2. Short-term recovery plan (1-3 days)
3. Active recovery recommendations
4. Nutrition and hydration guidelines
5. Sleep optimization tips
6. When to resume normal training"""
    
    def get_injury_prevention_prompt(self, risk_factors: Dict[str, Any]) -> str:
        """Get prompt for injury prevention strategies."""
        return f"""Develop injury prevention strategies based on these risk factors:

**Risk Assessment:**
- Movement Patterns: {risk_factors.get('movement_issues', [])}
- Previous Injuries: {risk_factors.get('injury_history', [])}
- Training Volume: {risk_factors.get('weekly_volume', 'moderate')}
- Muscle Imbalances: {risk_factors.get('imbalances', [])}
- Sport/Activity: {risk_factors.get('primary_activity', 'general fitness')}

Create a comprehensive plan including:
1. Corrective exercises
2. Mobility work
3. Stability training
4. Load management strategies
5. Warning signs to monitor
6. When to seek professional help"""
    
    def get_performance_analysis_prompt(self, performance_data: Dict[str, Any]) -> str:
        """Get prompt for performance analysis."""
        return f"""Analyze the following performance data and provide insights:

**Performance Metrics:**
- Strength Gains: {performance_data.get('strength_progress', {})}
- Endurance Metrics: {performance_data.get('endurance_metrics', {})}
- Body Composition: {performance_data.get('body_composition', {})}
- Training Consistency: {performance_data.get('consistency', 'good')}
- Recovery Quality: {performance_data.get('recovery_quality', 'average')}

Provide:
1. Performance trend analysis
2. Areas of improvement
3. Strengths to maintain
4. Recommended adjustments
5. Next phase recommendations
6. Realistic goal projections"""
    
    def get_recommendation_prompt(self, analysis: Dict[str, Any]) -> str:
        """Get prompt for generating recommendations."""
        return f"""Based on the following training analysis, provide 5 specific, actionable recommendations:

**Analysis Summary:**
{analysis}

Format each recommendation as:
1. [Specific action] - [Expected benefit]
2. [Specific action] - [Expected benefit]
...

Make recommendations:
- Specific and measurable
- Achievable within 1-2 weeks
- Directly addressing identified issues
- Progressive in nature"""
    
    def get_motivational_prompt(self, personality: str, context: str) -> str:
        """Get motivational message based on personality type."""
        style = "intense and challenging" if personality == "prime" else "supportive and sustainable"
        
        return f"""Generate a brief motivational message that is {style} for this context: {context}

Keep it:
- Under 2 sentences
- Authentic and personal
- Action-oriented
- Aligned with athletic mindset"""
    
    def format_with_personality(self, response: str, personality: str) -> str:
        """Add personality-specific formatting to responses."""
        if personality == "prime":
            return f"💪 {response}\n\n🔥 Remember: Champions are made in the moments when nobody's watching!"
        else:  # longevity
            return f"🌱 {response}\n\n💚 Remember: Sustainable progress beats short-term gains every time!"