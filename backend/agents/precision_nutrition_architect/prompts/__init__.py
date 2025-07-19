"""
SAGE Prompts Module
===================

Modular prompt management for the SAGE agent.
"""

from typing import Dict, Any


class SagePrompts:
    """Centralized prompt management for SAGE agent."""
    
    def get_base_instruction(self) -> str:
        """Get base instruction prompt for SAGE."""
        return """You are SAGE, a Precision Nutrition Architect specializing in creating 
evidence-based, personalized nutrition strategies. Your expertise includes:

- Nutrigenomics and personalized nutrition
- Chrononutrition and meal timing optimization
- Biomarker analysis and interpretation
- Supplement stacking and optimization
- Metabolic health and optimization
- Food sensitivity and allergen management

Always provide scientifically-backed recommendations and include appropriate disclaimers 
when discussing medical conditions or supplements."""
    
    def get_meal_plan_prompt(self, user_data: Dict[str, Any]) -> str:
        """Get prompt for generating meal plans."""
        return f"""Create a personalized meal plan based on the following profile:

**User Profile:**
- Goals: {user_data.get('goals', [])}
- Dietary Preferences: {user_data.get('dietary_preferences', 'omnivore')}
- Caloric Needs: {user_data.get('tdee', 2000)} kcal
- Macro Split: {user_data.get('macro_split', {'protein': 30, 'carbs': 40, 'fats': 30})}%
- Allergies/Intolerances: {user_data.get('allergies', 'none')}
- Activity Level: {user_data.get('activity_level', 'moderate')}

**Requirements:**
1. Meet macro and calorie targets
2. Include variety and micronutrient density
3. Consider meal timing for optimal metabolism
4. Provide practical, accessible food options
5. Include prep tips and alternatives

Structure the plan with:
- Daily meal breakdown
- Specific portions and measurements
- Macro breakdown per meal
- Timing recommendations
- Shopping list"""
    
    def get_supplement_recommendation_prompt(self, biomarkers: Dict[str, Any], goals: list) -> str:
        """Get prompt for supplement recommendations."""
        return f"""Analyze the following biomarkers and recommend a supplement protocol:

**Biomarkers:**
{self._format_biomarkers(biomarkers)}

**Health Goals:**
{', '.join(goals)}

Provide recommendations including:
1. Priority supplements based on deficiencies
2. Optimal dosages and forms
3. Timing and absorption optimization
4. Potential interactions to avoid
5. Duration of supplementation
6. Retest timeline

Include safety disclaimers and advise consulting healthcare providers."""
    
    def get_biomarker_analysis_prompt(self, biomarkers: Dict[str, Any]) -> str:
        """Get prompt for biomarker analysis."""
        return f"""Analyze the following biomarker results:

**Lab Results:**
{self._format_biomarkers(biomarkers)}

Provide:
1. Interpretation of each marker
2. Optimal vs current ranges
3. Health implications
4. Nutritional interventions
5. Lifestyle recommendations
6. Priority areas for improvement

Use evidence-based reference ranges and cite concerns that require medical attention."""
    
    def get_chrononutrition_prompt(self, schedule: Dict[str, Any], circadian_type: str) -> str:
        """Get prompt for chrononutrition planning."""
        return f"""Design a chrononutrition protocol based on:

**Schedule:**
- Wake time: {schedule.get('wake_time', '7:00 AM')}
- Sleep time: {schedule.get('sleep_time', '11:00 PM')}
- Work schedule: {schedule.get('work_schedule', '9-5')}
- Workout time: {schedule.get('workout_time', 'evening')}

**Circadian Type:** {circadian_type}

Create a timing strategy that:
1. Optimizes metabolism and energy
2. Supports circadian rhythm
3. Enhances workout performance
4. Improves sleep quality
5. Manages hunger and cravings

Include specific meal timing, macronutrient distribution across the day, and fasting windows if beneficial."""
    
    def get_food_image_analysis_prompt(self) -> str:
        """Get prompt for food image analysis."""
        return """Analyze this food image and provide:

1. Identified foods and estimated portions
2. Approximate macronutrient breakdown
3. Estimated calorie content
4. Nutritional highlights
5. Potential allergens
6. Healthier alternatives or improvements

Be conservative with estimates and provide ranges when uncertain."""
    
    def _format_biomarkers(self, biomarkers: Dict[str, Any]) -> str:
        """Format biomarkers for prompt."""
        formatted = []
        for marker, value in biomarkers.items():
            if isinstance(value, dict):
                formatted.append(f"- {marker}: {value.get('value')} {value.get('unit', '')}")
            else:
                formatted.append(f"- {marker}: {value}")
        return '\n'.join(formatted)
    
    def format_with_personality(self, response: str, personality: str) -> str:
        """Add personality-specific formatting to responses."""
        if personality == "prime":
            return f"💪 {response}\n\n🔥 Remember: Optimal nutrition fuels peak performance!"
        else:  # longevity
            return f"🌱 {response}\n\n💚 Remember: Sustainable nutrition is the foundation of longevity!"