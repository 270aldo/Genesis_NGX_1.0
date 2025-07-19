"""
Skills Manager for Precision Nutrition Architect Agent.
Implements real AI-powered nutrition analysis and meal planning using Gemini.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from core.personality.personality_adapter import PersonalityAdapter
from clients.vertex_ai.client import VertexAIClient

from .core.dependencies import NutritionAgentDependencies
from .core.exceptions import (
    MealPlanningError,
    BiomarkerAnalysisError,
    SupplementationError,
    FoodAnalysisError,
    ValidationError,
)
from .core.constants import (
    DietType,
    ActivityLevel,
    HealthGoal,
    ACTIVITY_MULTIPLIERS,
    BIOMARKER_OPTIMAL_RANGES,
)
from .sage_vision_optimization import SageEnhancedVisionMixin

logger = logging.getLogger(__name__)


class NutritionSkillsManager(SageEnhancedVisionMixin):
    """
    Manages all nutrition-related skills with real AI implementation.
    Delegates to specialized skill handlers while maintaining unified interface.
    NOW WITH ENHANCED VISION CAPABILITIES via SageEnhancedVisionMixin.
    """

    def __init__(self, dependencies: NutritionAgentDependencies):
        """Initialize skills manager with dependencies."""
        self.deps = dependencies
        self.personality_adapter = dependencies.personality_adapter
        self.vertex_ai_client = getattr(dependencies, "vertex_ai_client", None)

        # Initialize enhanced vision capabilities from mixin
        self.init_enhanced_nutrition_vision_capabilities()

        # Skill registry mapping - UPDATED with enhanced vision skills
        self.skills = {
            # Original skills (implemented)
            "create_meal_plan": self._skill_create_meal_plan,
            "analyze_nutrition_image": self._skill_analyze_nutrition_image,
            "assess_biomarkers": self._skill_assess_biomarkers,
            "recommend_supplements": self._skill_recommend_supplements,
            "optimize_macros": self._skill_optimize_macros,
            # NEW: Enhanced vision skills from SageEnhancedVisionMixin
            "analyze_nutrition_image_enhanced": self._skill_analyze_nutrition_image_enhanced,
            "analyze_nutrition_label_advanced": self._skill_analyze_nutrition_label_advanced,
            "analyze_prepared_meal_comprehensive": self._skill_analyze_prepared_meal_comprehensive,
            "recognize_foods_multimodal": self._skill_recognize_foods_multimodal,
            "estimate_portions_3d": self._skill_estimate_portions_3d,
            "analyze_food_freshness": self._skill_analyze_food_freshness,
            "predict_glycemic_impact": self._skill_predict_glycemic_impact,
            "track_nutrition_progress": self._skill_track_nutrition_progress,
            "generate_nutrition_insights": self._skill_generate_nutrition_insights,
            "analyze_meal_balance": self._skill_analyze_meal_balance,
            "detect_nutritional_deficiencies": self._skill_detect_nutritional_deficiencies,
        }

    async def process_message(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process incoming message and route to appropriate skill.

        Args:
            message: User message
            context: Conversation context

        Returns:
            Skill execution result
        """
        try:
            # Determine skill needed
            skill_name = await self._determine_skill(message, context)

            # Execute skill
            if skill_name in self.skills:
                result = await self._execute_skill(skill_name, message, context)

                # Apply personality adaptation
                if self.personality_adapter:
                    adapted_result = await self._apply_personality_adaptation(
                        result, context
                    )
                    return adapted_result

                return result
            else:
                return self._create_error_response(
                    "Unknown skill requested", skill_name=skill_name
                )

        except Exception as e:
            logger.error(f"Skill processing failed: {e}")
            return self._create_error_response(str(e))

    async def _determine_skill(self, message: str, context: Dict[str, Any]) -> str:
        """Determine which skill to use based on message analysis."""
        # Use Gemini to analyze intent
        prompt = f"""
        Analyze this nutrition-related message and determine the appropriate skill:
        
        Message: "{message}"
        Context: {json.dumps(context, indent=2)}
        
        Available skills:
        - create_meal_plan: Generate personalized meal plans
        - analyze_nutrition_image: Analyze food photos for nutrition content
        - assess_biomarkers: Interpret biomarker test results
        - recommend_supplements: Suggest targeted supplementation
        - optimize_macros: Optimize macronutrient ratios
        - plan_chrono_nutrition: Create meal timing strategies
        - analyze_food_trends: Analyze eating patterns over time
        - generate_shopping_list: Create shopping lists from meal plans
        
        Enhanced Vision Skills:
        - analyze_nutrition_image_enhanced: Advanced multimodal food analysis with AI
        - recognize_foods_multimodal: Identify 1000+ foods with computer vision
        - estimate_portions_3d: 3D volumetric portion estimation
        - analyze_food_freshness: Food quality and freshness analysis
        - predict_glycemic_impact: Personalized glycemic impact prediction
        - track_nutrition_progress: Temporal nutrition progress tracking
        - generate_nutrition_insights: AI-powered personalized insights
        - analyze_meal_balance: Complete meal nutritional balance
        - detect_nutritional_deficiencies: Visual deficiency detection
        
        Return only the skill name that best matches the request.
        """

        try:
            if self.vertex_ai_client:
                response = await self.vertex_ai_client.generate_content_async(prompt)
                skill_name = response.strip().lower()
                return skill_name if skill_name in self.skills else "create_meal_plan"
            else:
                # Fallback to simple keyword matching
                return self._fallback_skill_determination(message)

        except Exception as e:
            logger.warning(f"Skill determination failed, using fallback: {e}")
            return self._fallback_skill_determination(message)

    def _fallback_skill_determination(self, message: str) -> str:
        """Fallback skill determination using keywords."""
        message_lower = message.lower()

        # Enhanced vision skills keywords
        if any(
            word in message_lower
            for word in ["enhanced", "advanced", "detailed", "ai analysis"]
        ):
            if any(word in message_lower for word in ["photo", "image", "picture"]):
                return "analyze_nutrition_image_enhanced"
            return "analyze_nutrition_image_enhanced"
        elif any(
            word in message_lower
            for word in ["recognize", "identify", "detect food", "what food"]
        ):
            return "recognize_foods_multimodal"
        elif any(
            word in message_lower for word in ["portion", "serving", "how much", "size"]
        ):
            return "estimate_portions_3d"
        elif any(
            word in message_lower for word in ["fresh", "quality", "spoiled", "ripe"]
        ):
            return "analyze_food_freshness"
        elif any(
            word in message_lower
            for word in ["blood sugar", "glucose", "glycemic", "diabetes"]
        ):
            return "predict_glycemic_impact"
        elif any(
            word in message_lower
            for word in ["progress", "track", "history", "over time"]
        ):
            return "track_nutrition_progress"
        elif any(
            word in message_lower for word in ["insight", "recommendation", "advice"]
        ):
            return "generate_nutrition_insights"
        elif any(
            word in message_lower for word in ["balance", "balanced", "complete meal"]
        ):
            return "analyze_meal_balance"
        elif any(
            word in message_lower
            for word in ["deficiency", "lacking", "missing nutrients"]
        ):
            return "detect_nutritional_deficiencies"

        # Original skills keywords
        elif any(word in message_lower for word in ["meal plan", "meals", "diet"]):
            return "create_meal_plan"
        elif any(word in message_lower for word in ["photo", "image", "picture"]):
            return "analyze_nutrition_image_enhanced"  # Default to enhanced version
        elif any(word in message_lower for word in ["biomarker", "blood test", "lab"]):
            return "assess_biomarkers"
        elif any(
            word in message_lower for word in ["supplement", "vitamin", "mineral"]
        ):
            return "recommend_supplements"
        elif any(word in message_lower for word in ["macro", "protein", "carb"]):
            return "optimize_macros"
        elif any(word in message_lower for word in ["timing", "when to eat"]):
            return "plan_chrono_nutrition"
        elif any(word in message_lower for word in ["shopping", "grocery", "buy"]):
            return "generate_shopping_list"
        else:
            return "create_meal_plan"

    async def _execute_skill(
        self, skill_name: str, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute specific skill handler."""
        skill_handler = self.skills[skill_name]
        return await skill_handler(message, context)

    async def _skill_create_meal_plan(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create personalized meal plan using AI analysis."""
        try:
            # Extract user preferences and goals
            user_data = self._extract_user_data(context)

            # Calculate nutritional targets
            targets = await self._calculate_nutrition_targets(user_data)

            # Generate meal plan with Gemini
            prompt = f"""
            Create a personalized meal plan based on:
            
            User Request: {message}
            User Profile: {json.dumps(user_data, indent=2)}
            Nutrition Targets: {json.dumps(targets, indent=2)}
            
            Create a 7-day meal plan that:
            1. Meets the nutrition targets
            2. Considers dietary restrictions and preferences
            3. Provides variety and balance
            4. Includes practical meal prep suggestions
            
            Format as structured JSON with meals for each day.
            """

            if self.vertex_ai_client:
                ai_response = await self.vertex_ai_client.generate_content_async(prompt)
                meal_plan = self._parse_meal_plan_response(ai_response)
            else:
                meal_plan = self._generate_fallback_meal_plan(targets, user_data)

            # Validate meal plan
            validation_result = await self._validate_meal_plan(meal_plan, targets)

            return {
                "skill": "create_meal_plan",
                "success": True,
                "meal_plan": meal_plan,
                "targets": targets,
                "validation": validation_result,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Meal planning failed: {e}")
            raise MealPlanningError(f"Failed to create meal plan: {e}")

    async def _skill_analyze_nutrition_image(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze food image for nutritional content."""
        try:
            # Extract image from context
            image_data = context.get("image_data")
            if not image_data:
                raise FoodAnalysisError(
                    "No image provided for analysis", reason="missing_image"
                )

            # Use Gemini vision for food analysis
            prompt = f"""
            Analyze this food image and provide:
            
            User Query: {message}
            
            1. Identify all food items visible
            2. Estimate portion sizes using visual references
            3. Calculate nutritional breakdown (calories, macros, key micros)
            4. Assess overall nutritional quality (score 1-10)
            5. Provide improvement suggestions
            
            Return structured data with detailed nutrition analysis.
            """

            if self.vertex_ai_client and hasattr(
                self.vertex_ai_client, "analyze_image"
            ):
                analysis = await self.vertex_ai_client.analyze_image(image_data, prompt)
                nutrition_data = self._parse_image_analysis(analysis)
            else:
                nutrition_data = self._generate_fallback_image_analysis()

            return {
                "skill": "analyze_nutrition_image",
                "success": True,
                "analysis": nutrition_data,
                "confidence_score": nutrition_data.get("confidence", 0.85),
                "analyzed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise FoodAnalysisError(f"Failed to analyze food image: {e}")

    async def _skill_assess_biomarkers(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess biomarker results and provide nutrition recommendations."""
        try:
            # Extract biomarker data
            biomarkers = context.get("biomarkers", {})
            if not biomarkers:
                # Try to extract from message
                biomarkers = self._extract_biomarkers_from_message(message)

            if not biomarkers:
                raise BiomarkerAnalysisError("No biomarker data provided")

            # Analyze with Gemini
            prompt = f"""
            Analyze these biomarker results and provide nutrition recommendations:
            
            Biomarkers: {json.dumps(biomarkers, indent=2)}
            User Query: {message}
            Reference Ranges: {json.dumps(BIOMARKER_OPTIMAL_RANGES, indent=2)}
            
            Provide:
            1. Assessment of each biomarker (optimal/suboptimal/concerning)
            2. Nutritional deficiencies or excesses indicated
            3. Specific dietary recommendations
            4. Supplement suggestions if appropriate
            5. Timeline for improvement expectations
            6. Follow-up testing recommendations
            
            Focus on actionable nutrition interventions.
            """

            if self.vertex_ai_client:
                analysis = await self.vertex_ai_client.generate_content_async(prompt)
                assessment = self._parse_biomarker_assessment(analysis)
            else:
                assessment = self._generate_fallback_biomarker_assessment(biomarkers)

            return {
                "skill": "assess_biomarkers",
                "success": True,
                "biomarkers": biomarkers,
                "assessment": assessment,
                "priority_actions": assessment.get("priority_actions", []),
                "assessed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Biomarker assessment failed: {e}")
            raise BiomarkerAnalysisError(f"Failed to assess biomarkers: {e}")

    async def _skill_recommend_supplements(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recommend targeted supplementation based on needs analysis."""
        try:
            # Gather data for supplement recommendations
            user_data = self._extract_user_data(context)
            biomarkers = context.get("biomarkers", {})
            dietary_intake = context.get("recent_nutrition", {})

            # Analyze supplement needs with AI
            prompt = f"""
            Recommend supplements based on comprehensive analysis:
            
            User Query: {message}
            User Profile: {json.dumps(user_data, indent=2)}
            Biomarkers: {json.dumps(biomarkers, indent=2)}
            Recent Nutrition: {json.dumps(dietary_intake, indent=2)}
            
            Provide evidence-based supplement recommendations:
            1. Identify specific deficiencies or optimization opportunities
            2. Recommend appropriate supplements with dosages
            3. Consider interactions between supplements
            4. Prioritize by importance (critical/beneficial/optional)
            5. Suggest timing and duration
            6. Include safety considerations
            
            Only recommend supplements with scientific backing.
            """

            if self.vertex_ai_client:
                response = await self.vertex_ai_client.generate_content_async(prompt)
                recommendations = self._parse_supplement_recommendations(response)
            else:
                recommendations = self._generate_fallback_supplement_recs(user_data)

            # Validate safety and interactions
            safety_check = await self._validate_supplement_safety(recommendations)

            return {
                "skill": "recommend_supplements",
                "success": True,
                "recommendations": recommendations,
                "safety_analysis": safety_check,
                "total_cost_estimate": self._estimate_supplement_cost(recommendations),
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Supplement recommendation failed: {e}")
            raise SupplementationError(f"Failed to recommend supplements: {e}")

    async def _skill_optimize_macros(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize macronutrient ratios for specific goals."""
        try:
            user_data = self._extract_user_data(context)
            current_intake = context.get("current_macros", {})
            goals = user_data.get("goals", [])

            # AI-powered macro optimization
            prompt = f"""
            Optimize macronutrient distribution for this user:
            
            User Request: {message}
            Current Goals: {goals}
            Current Intake: {json.dumps(current_intake, indent=2)}
            User Profile: {json.dumps(user_data, indent=2)}
            
            Provide optimized macro distribution:
            1. Calculate ideal protein requirements
            2. Determine optimal carbohydrate intake and timing
            3. Set appropriate fat intake for hormonal health
            4. Consider activity level and training schedule
            5. Provide specific gram targets and percentages
            6. Include meal-by-meal distribution suggestions
            
            Base recommendations on current sports nutrition science.
            """

            if self.vertex_ai_client:
                response = await self.vertex_ai_client.generate_content_async(prompt)
                optimization = self._parse_macro_optimization(response)
            else:
                optimization = self._generate_fallback_macro_plan(user_data)

            return {
                "skill": "optimize_macros",
                "success": True,
                "current_macros": current_intake,
                "optimized_macros": optimization,
                "improvement_areas": optimization.get("improvements", []),
                "implementation_tips": optimization.get("tips", []),
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Macro optimization failed: {e}")
            raise MealPlanningError(f"Failed to optimize macros: {e}")

    # Helper methods
    def _extract_user_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user profile data from context."""
        return {
            "age": context.get("age", 30),
            "gender": context.get("gender", "unknown"),
            "weight": context.get("weight", 70),
            "height": context.get("height", 170),
            "activity_level": context.get("activity_level", "moderately_active"),
            "goals": context.get("goals", ["general_health"]),
            "dietary_restrictions": context.get("dietary_restrictions", []),
            "preferences": context.get("food_preferences", {}),
            "program_type": context.get("program_type", "LONGEVITY"),
        }

    async def _calculate_nutrition_targets(
        self, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate personalized nutrition targets."""
        # Basic metabolic rate calculation (Mifflin-St Jeor)
        weight = user_data.get("weight", 70)
        height = user_data.get("height", 170)
        age = user_data.get("age", 30)
        gender = user_data.get("gender", "unknown")

        if gender.lower() == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        # Apply activity multiplier
        activity_level = user_data.get("activity_level", "moderately_active")
        multiplier = ACTIVITY_MULTIPLIERS.get(ActivityLevel(activity_level), 1.55)

        total_calories = bmr * multiplier

        # Macro distribution based on goals
        goals = user_data.get("goals", ["general_health"])
        if "weight_loss" in goals:
            total_calories *= 0.85  # 15% deficit
            protein_pct, carb_pct, fat_pct = 0.35, 0.30, 0.35
        elif "muscle_gain" in goals:
            total_calories *= 1.15  # 15% surplus
            protein_pct, carb_pct, fat_pct = 0.30, 0.40, 0.30
        else:
            protein_pct, carb_pct, fat_pct = 0.25, 0.45, 0.30

        return {
            "calories": round(total_calories),
            "protein_g": round((total_calories * protein_pct) / 4),
            "carbs_g": round((total_calories * carb_pct) / 4),
            "fat_g": round((total_calories * fat_pct) / 9),
            "fiber_g": round(total_calories / 100 * 1.4),  # 14g per 1000 calories
            "protein_pct": protein_pct,
            "carbs_pct": carb_pct,
            "fat_pct": fat_pct,
        }

    def _parse_meal_plan_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI-generated meal plan response."""
        try:
            # Try to extract JSON from response
            start_idx = ai_response.find("{")
            end_idx = ai_response.rfind("}") + 1

            if start_idx != -1 and end_idx != 0:
                json_str = ai_response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: create structured meal plan from text
                return self._create_structured_meal_plan_from_text(ai_response)

        except Exception as e:
            logger.warning(f"Failed to parse meal plan response: {e}")
            return self._generate_fallback_meal_plan({}, {})

    async def _apply_personality_adaptation(
        self, result: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply personality adaptation to skill results."""
        try:
            program_type = context.get("program_type", "LONGEVITY")

            if self.personality_adapter:
                # Adapt the response content
                if "meal_plan" in result:
                    adapted_content = await self.personality_adapter.adapt_response(
                        json.dumps(result["meal_plan"]), program_type, "sage"
                    )
                    result["meal_plan"]["adapted_presentation"] = adapted_content

                # Add program-specific messaging
                result["personality_context"] = {
                    "program_type": program_type,
                    "tone": "strategic" if program_type == "PRIME" else "nurturing",
                    "focus": "optimization" if program_type == "PRIME" else "wellness",
                }

            return result

        except Exception as e:
            logger.warning(f"Personality adaptation failed: {e}")
            return result

    def _create_error_response(self, error_message: str, **kwargs) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "success": False,
            "error": error_message,
            "error_details": kwargs,
            "timestamp": datetime.now().isoformat(),
        }

    # Additional fallback methods would be implemented here...
    def _generate_fallback_meal_plan(
        self, targets: Dict[str, Any], user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate basic meal plan when AI is unavailable."""
        return {
            "plan_type": "fallback_basic",
            "duration_days": 7,
            "daily_template": {
                "breakfast": {"calories": targets.get("calories", 2000) * 0.25},
                "lunch": {"calories": targets.get("calories", 2000) * 0.35},
                "dinner": {"calories": targets.get("calories", 2000) * 0.30},
                "snacks": {"calories": targets.get("calories", 2000) * 0.10},
            },
        }
