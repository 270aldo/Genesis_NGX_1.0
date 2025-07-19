"""
Training Plan Generation Skill
==============================

Generates personalized training plans using AI and sports science principles.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from core.logging_config import get_logger
from clients.vertex_ai.client import VertexAIClient
from agents.elite_training_strategist.services.training_data_service import TrainingDataService

logger = get_logger(__name__)


class TrainingPlanGenerationSkill:
    """Skill for generating personalized training plans."""
    
    def __init__(
        self,
        vertex_client: VertexAIClient,
        data_service: TrainingDataService
    ):
        """Initialize skill with required services."""
        self.vertex_client = vertex_client
        self.data_service = data_service
        self.templates = self._load_training_templates()
    
    async def execute(
        self,
        request: str,
        user_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a personalized training plan.
        
        Args:
            request: User's training request
            user_data: User profile and fitness data
            preferences: Training preferences
            
        Returns:
            Generated training plan
        """
        try:
            # Analyze user profile
            profile_analysis = self._analyze_user_profile(user_data)
            
            # Select appropriate template
            template = self._select_template(profile_analysis, preferences)
            
            # Generate plan structure
            plan_structure = await self._generate_plan_structure(
                profile_analysis,
                template,
                request
            )
            
            # Fill in exercise details
            detailed_plan = await self._add_exercise_details(plan_structure, user_data)
            
            # Add progression scheme
            final_plan = self._add_progression_scheme(detailed_plan, profile_analysis)
            
            # Save to database
            plan_id = await self.data_service.save_training_plan(
                user_data.get("user_id"),
                final_plan
            )
            
            return {
                "success": True,
                "plan_id": plan_id,
                "training_plan": final_plan,
                "confidence": 0.95,
                "notes": self._generate_plan_notes(profile_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error generating training plan: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": self._get_fallback_plan(user_data)
            }
    
    def _analyze_user_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user profile to determine training needs."""
        return {
            "fitness_level": self._calculate_fitness_level(user_data),
            "training_age": self._calculate_training_age(user_data),
            "recovery_capacity": self._assess_recovery_capacity(user_data),
            "injury_risk": self._assess_injury_risk(user_data),
            "goals_priority": self._prioritize_goals(user_data.get("goals", [])),
            "time_availability": user_data.get("training_days", 3)
        }
    
    def _calculate_fitness_level(self, user_data: Dict[str, Any]) -> str:
        """Calculate overall fitness level."""
        # Simplified logic - in production would use more sophisticated analysis
        strength_metrics = user_data.get("strength_metrics", {})
        endurance_metrics = user_data.get("endurance_metrics", {})
        
        if not strength_metrics and not endurance_metrics:
            return "beginner"
        
        # Example: Check key lifts relative to body weight
        body_weight = user_data.get("weight", 70)
        squat_ratio = strength_metrics.get("squat", 0) / body_weight
        
        if squat_ratio < 1.0:
            return "beginner"
        elif squat_ratio < 1.5:
            return "intermediate"
        elif squat_ratio < 2.0:
            return "advanced"
        else:
            return "elite"
    
    def _calculate_training_age(self, user_data: Dict[str, Any]) -> int:
        """Calculate training age in years."""
        start_date = user_data.get("training_start_date")
        if not start_date:
            return 0
        
        try:
            start = datetime.fromisoformat(start_date)
            return (datetime.now() - start).days // 365
        except:
            return 0
    
    def _assess_recovery_capacity(self, user_data: Dict[str, Any]) -> str:
        """Assess user's recovery capacity."""
        age = user_data.get("age", 30)
        sleep_quality = user_data.get("sleep_quality", 0.7)
        stress_level = user_data.get("stress_level", 0.5)
        
        # Simple scoring
        recovery_score = 1.0
        recovery_score *= (1.0 - (age - 20) * 0.01)  # Age factor
        recovery_score *= sleep_quality
        recovery_score *= (1.0 - stress_level)
        
        if recovery_score > 0.8:
            return "excellent"
        elif recovery_score > 0.6:
            return "good"
        elif recovery_score > 0.4:
            return "moderate"
        else:
            return "poor"
    
    def _assess_injury_risk(self, user_data: Dict[str, Any]) -> float:
        """Assess injury risk score (0-1)."""
        risk_score = 0.0
        
        # Previous injuries
        injury_history = user_data.get("injury_history", [])
        risk_score += min(len(injury_history) * 0.1, 0.3)
        
        # Age factor
        age = user_data.get("age", 30)
        if age > 40:
            risk_score += 0.1
        if age > 50:
            risk_score += 0.1
        
        # Training load
        weekly_hours = user_data.get("weekly_training_hours", 5)
        if weekly_hours > 10:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _prioritize_goals(self, goals: List[str]) -> List[str]:
        """Prioritize training goals."""
        # Goal priority mapping
        priority_map = {
            "strength": 1,
            "muscle_gain": 2,
            "fat_loss": 3,
            "endurance": 4,
            "athletic_performance": 1,
            "general_fitness": 5
        }
        
        return sorted(goals, key=lambda g: priority_map.get(g, 10))
    
    def _select_template(
        self,
        profile: Dict[str, Any],
        preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select appropriate training template."""
        fitness_level = profile["fitness_level"]
        primary_goal = profile["goals_priority"][0] if profile["goals_priority"] else "general_fitness"
        
        # Template selection logic
        template_key = f"{primary_goal}_{fitness_level}"
        
        # Fallback to closest match
        if template_key not in self.templates:
            if primary_goal in ["strength", "muscle_gain"]:
                template_key = f"strength_{fitness_level}"
            else:
                template_key = f"general_{fitness_level}"
        
        template = self.templates.get(template_key, self.templates["general_intermediate"])
        
        # Apply preferences
        if preferences:
            if "training_days" in preferences:
                template["frequency"] = preferences["training_days"]
            if "session_duration" in preferences:
                template["session_duration"] = preferences["session_duration"]
        
        return template
    
    async def _generate_plan_structure(
        self,
        profile: Dict[str, Any],
        template: Dict[str, Any],
        request: str
    ) -> Dict[str, Any]:
        """Generate the plan structure using AI."""
        prompt = f"""Create a {template['duration_weeks']}-week training plan structure.

Profile:
- Fitness Level: {profile['fitness_level']}
- Goals: {profile['goals_priority']}
- Available Days: {profile['time_availability']}
- Recovery Capacity: {profile['recovery_capacity']}

Template Guidelines:
- Training Frequency: {template['frequency']} days/week
- Phase Progression: {template.get('phase_progression', [])}
- Primary Exercises: {template.get('primary_exercises', [])}

Special Request: {request}

Provide a week-by-week overview with:
1. Training phase
2. Volume progression
3. Intensity targets
4. Key focuses"""
        
        response = await self.vertex_client.generate_content(prompt)
        
        # Parse response into structured format
        return self._parse_plan_structure(response.get("text", ""))
    
    def _parse_plan_structure(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured plan format."""
        # Simplified parsing - in production would use more robust parsing
        lines = ai_response.strip().split('\n')
        
        plan_structure = {
            "weeks": [],
            "phases": [],
            "progression": {}
        }
        
        current_week = None
        for line in lines:
            if "Week" in line:
                week_num = self._extract_number(line)
                current_week = {
                    "week": week_num,
                    "phase": "",
                    "volume": "",
                    "intensity": "",
                    "focus": []
                }
                plan_structure["weeks"].append(current_week)
            elif current_week and "Phase:" in line:
                current_week["phase"] = line.split("Phase:")[1].strip()
            elif current_week and "Volume:" in line:
                current_week["volume"] = line.split("Volume:")[1].strip()
            elif current_week and "Intensity:" in line:
                current_week["intensity"] = line.split("Intensity:")[1].strip()
        
        return plan_structure
    
    def _extract_number(self, text: str) -> int:
        """Extract number from text."""
        import re
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 1
    
    async def _add_exercise_details(
        self,
        plan_structure: Dict[str, Any],
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add detailed exercise prescriptions to plan."""
        detailed_plan = plan_structure.copy()
        detailed_plan["workouts"] = []
        
        # Generate workouts for first 4 weeks as example
        for week in plan_structure["weeks"][:4]:
            week_workouts = await self._generate_week_workouts(
                week,
                user_data,
                plan_structure
            )
            detailed_plan["workouts"].extend(week_workouts)
        
        return detailed_plan
    
    async def _generate_week_workouts(
        self,
        week: Dict[str, Any],
        user_data: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate specific workouts for a week."""
        workouts = []
        
        # Example: 3 workouts per week
        for day in range(1, 4):
            workout = {
                "week": week["week"],
                "day": day,
                "name": f"Week {week['week']} Day {day}",
                "exercises": await self._select_exercises(week, day, user_data),
                "warmup": self._generate_warmup(day),
                "cooldown": self._generate_cooldown(day),
                "notes": f"Focus on {week.get('focus', ['form'])[0]}"
            }
            workouts.append(workout)
        
        return workouts
    
    async def _select_exercises(
        self,
        week: Dict[str, Any],
        day: int,
        user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Select appropriate exercises for a workout."""
        # Simplified exercise selection
        if day == 1:  # Upper body
            exercises = [
                {"name": "Bench Press", "sets": 4, "reps": "8-10", "rest": "2-3 min"},
                {"name": "Pull-ups", "sets": 3, "reps": "6-12", "rest": "2 min"},
                {"name": "Shoulder Press", "sets": 3, "reps": "10-12", "rest": "90 sec"},
                {"name": "Row", "sets": 3, "reps": "10-12", "rest": "90 sec"}
            ]
        elif day == 2:  # Lower body
            exercises = [
                {"name": "Squat", "sets": 4, "reps": "6-8", "rest": "3 min"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "8-10", "rest": "2 min"},
                {"name": "Leg Press", "sets": 3, "reps": "12-15", "rest": "90 sec"},
                {"name": "Calf Raises", "sets": 3, "reps": "15-20", "rest": "60 sec"}
            ]
        else:  # Full body
            exercises = [
                {"name": "Deadlift", "sets": 3, "reps": "5-6", "rest": "3-4 min"},
                {"name": "Dips", "sets": 3, "reps": "8-12", "rest": "2 min"},
                {"name": "Front Squat", "sets": 3, "reps": "8-10", "rest": "2 min"},
                {"name": "Face Pulls", "sets": 3, "reps": "15-20", "rest": "60 sec"}
            ]
        
        # Adjust based on week's intensity
        intensity = week.get("intensity", "moderate")
        if intensity == "high":
            for ex in exercises:
                ex["reps"] = ex["reps"].split("-")[0]  # Use lower rep range
        
        return exercises
    
    def _generate_warmup(self, day: int) -> Dict[str, Any]:
        """Generate warmup routine."""
        return {
            "duration": "10-15 minutes",
            "components": [
                {"name": "General Cardio", "duration": "5 min", "intensity": "light"},
                {"name": "Dynamic Stretching", "duration": "5 min", "focus": "target muscles"},
                {"name": "Activation Exercises", "duration": "5 min", "sets": "2-3"}
            ]
        }
    
    def _generate_cooldown(self, day: int) -> Dict[str, Any]:
        """Generate cooldown routine."""
        return {
            "duration": "10-15 minutes",
            "components": [
                {"name": "Light Cardio", "duration": "5 min", "intensity": "very light"},
                {"name": "Static Stretching", "duration": "5-10 min", "hold": "30 sec"},
                {"name": "Foam Rolling", "duration": "5 min", "focus": "worked muscles"}
            ]
        }
    
    def _add_progression_scheme(
        self,
        plan: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add progression guidelines to plan."""
        plan["progression"] = {
            "weekly_volume_increase": self._calculate_volume_progression(profile),
            "intensity_progression": self._calculate_intensity_progression(profile),
            "deload_frequency": self._calculate_deload_frequency(profile),
            "adjustment_criteria": {
                "increase_load": "Complete all sets with 2 reps in reserve",
                "maintain_load": "Complete all sets with 0-1 reps in reserve",
                "decrease_load": "Unable to complete prescribed sets/reps"
            }
        }
        
        return plan
    
    def _calculate_volume_progression(self, profile: Dict[str, Any]) -> float:
        """Calculate appropriate volume progression rate."""
        base_progression = 0.05  # 5% base
        
        # Adjust based on profile
        if profile["fitness_level"] == "beginner":
            base_progression = 0.10  # 10% for beginners
        elif profile["fitness_level"] == "elite":
            base_progression = 0.025  # 2.5% for elite
        
        # Adjust for recovery capacity
        if profile["recovery_capacity"] == "excellent":
            base_progression *= 1.2
        elif profile["recovery_capacity"] == "poor":
            base_progression *= 0.6
        
        return min(base_progression, 0.15)  # Cap at 15%
    
    def _calculate_intensity_progression(self, profile: Dict[str, Any]) -> str:
        """Calculate intensity progression strategy."""
        if profile["training_age"] < 1:
            return "linear"  # Simple linear progression
        elif profile["training_age"] < 3:
            return "wave"  # Wave loading
        else:
            return "block"  # Block periodization
    
    def _calculate_deload_frequency(self, profile: Dict[str, Any]) -> int:
        """Calculate deload frequency in weeks."""
        base_frequency = 4  # Every 4 weeks
        
        if profile["recovery_capacity"] == "poor":
            base_frequency = 3
        elif profile["recovery_capacity"] == "excellent" and profile["training_age"] < 2:
            base_frequency = 5
        
        return base_frequency
    
    def _generate_plan_notes(self, profile: Dict[str, Any]) -> List[str]:
        """Generate important notes for the plan."""
        notes = []
        
        if profile["injury_risk"] > 0.6:
            notes.append("⚠️ Higher injury risk detected - prioritize form and recovery")
        
        if profile["recovery_capacity"] == "poor":
            notes.append("💤 Focus on sleep quality and stress management for better results")
        
        if profile["fitness_level"] == "beginner":
            notes.append("🎯 Master movement patterns before increasing load")
        
        notes.append("📊 Track your progress weekly and adjust as needed")
        
        return notes
    
    def _get_fallback_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a simple fallback plan if AI generation fails."""
        return {
            "name": "Basic Training Plan",
            "duration_weeks": 4,
            "frequency": 3,
            "workouts": [
                {
                    "day": "Monday",
                    "focus": "Upper Body",
                    "exercises": ["Push-ups", "Pull-ups", "Rows", "Shoulder Press"]
                },
                {
                    "day": "Wednesday",
                    "focus": "Lower Body",
                    "exercises": ["Squats", "Lunges", "Deadlifts", "Calf Raises"]
                },
                {
                    "day": "Friday",
                    "focus": "Full Body",
                    "exercises": ["Burpees", "Kettlebell Swings", "Planks", "Mountain Climbers"]
                }
            ],
            "notes": ["Start with bodyweight or light weights", "Focus on form", "Progress gradually"]
        }
    
    def _load_training_templates(self) -> Dict[str, Any]:
        """Load training templates."""
        # Import from config
        from agents.elite_training_strategist.config import TRAINING_TEMPLATES
        return TRAINING_TEMPLATES
    
    async def get_exercise_data(self, exercise_name: str) -> Dict[str, Any]:
        """Get detailed exercise data (used for caching)."""
        from agents.elite_training_strategist.config import DEFAULT_EXERCISES
        
        if exercise_name in DEFAULT_EXERCISES:
            return DEFAULT_EXERCISES[exercise_name]
        
        # Generate using AI if not in database
        prompt = f"Provide technical details for the {exercise_name} exercise including muscle groups, difficulty (1-5), and equipment options."
        
        response = await self.vertex_client.generate_content(prompt, temperature=0.3)
        
        # Parse and return
        return {
            "name": exercise_name,
            "category": "compound",  # Default
            "muscle_groups": ["multiple"],  # Would parse from response
            "equipment": ["various"],  # Would parse from response
            "difficulty": 3  # Default medium
        }