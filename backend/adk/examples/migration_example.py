"""
Migration Example: Converting an Agent to use ADK
================================================

This example shows how to migrate an existing agent to use the new
formalized ADK framework.
"""

# BEFORE: Old agent implementation
"""
class OldTrainingAgent(BaseNGXAgent, ADKAgent):
    def __init__(self):
        super().__init__(
            agent_id="elite_training_strategist",
            agent_name="Elite Training Strategist",
            agent_type="frontend"
        )
        self.llm_client = VertexAIClient()
        self.redis_client = RedisPoolManager().get_connection()
        # ... lots of initialization code
    
    async def execute(self, request):
        # Manual validation
        if not request.get('prompt'):
            raise ValueError("Prompt is required")
        
        # Manual caching
        cache_key = f"training:{request['user_id']}:{hash(request['prompt'])}"
        cached = await self.redis_client.get(cache_key)
        if cached:
            return cached
        
        # Execute logic
        try:
            result = await self.llm_client.generate(request['prompt'])
            # Manual caching
            await self.redis_client.setex(cache_key, 3600, result)
            return result
        except Exception as e:
            # Manual error handling
            logger.error(f"Error: {str(e)}")
            raise
"""

# AFTER: New ADK-based implementation
from adk.core import BaseADKAgent, AgentRequest, AgentResponse
from adk.toolkit import cache_result
from adk.patterns import circuit_breaker, retry
from pydantic import BaseModel, Field
from typing import Optional, List


class TrainingRequest(BaseModel):
    """Validated request model for training agent."""
    workout_type: str = Field(..., description="Type of workout")
    fitness_level: str = Field(..., description="User's fitness level")
    duration_minutes: int = Field(default=60, ge=15, le=180)
    equipment: List[str] = Field(default_factory=list)
    goals: Optional[List[str]] = None
    restrictions: Optional[List[str]] = None


class TrainingAgent(BaseADKAgent):
    """
    Elite Training Strategist Agent using ADK.
    
    This agent generates personalized workout plans based on user
    preferences, fitness level, and available equipment.
    """
    
    # Agent metadata (required)
    agent_id = "elite_training_strategist"
    agent_name = "Elite Training Strategist" 
    agent_type = "specialist"
    agent_version = "2.0.0"
    agent_description = "Generates personalized, science-based workout plans"
    
    def _initialize_skills(self):
        """Initialize agent-specific skills."""
        # Skills are automatically registered
        from .skills import (
            WorkoutGenerator,
            ExerciseOptimizer,
            ProgressionPlanner
        )
        
        self.register_skill("workout_generator", WorkoutGenerator())
        self.register_skill("exercise_optimizer", ExerciseOptimizer())
        self.register_skill("progression_planner", ProgressionPlanner())
    
    @cache_result(ttl=3600, key_prefix="training")
    @circuit_breaker(failure_threshold=3, recovery_timeout=60)
    @retry(max_attempts=3, backoff_factor=2)
    async def _execute_core(self, request: AgentRequest) -> dict:
        """
        Core execution logic with automatic caching, circuit breaking, and retry.
        
        All the boilerplate is handled by decorators and the base class.
        """
        # Parse and validate training-specific parameters
        training_data = TrainingRequest(**request.metadata)
        
        # Use registered skills
        workout_plan = await self.get_skill("workout_generator").generate(
            workout_type=training_data.workout_type,
            fitness_level=training_data.fitness_level,
            duration=training_data.duration_minutes,
            equipment=training_data.equipment
        )
        
        # Optimize exercises based on user goals
        if training_data.goals:
            workout_plan = await self.get_skill("exercise_optimizer").optimize(
                workout_plan,
                goals=training_data.goals,
                restrictions=training_data.restrictions
            )
        
        # Add progression recommendations
        progression = await self.get_skill("progression_planner").plan(
            current_plan=workout_plan,
            fitness_level=training_data.fitness_level
        )
        
        return {
            "content": workout_plan,
            "metadata": {
                "progression": progression,
                "estimated_calories": self._estimate_calories(workout_plan),
                "difficulty_score": self._calculate_difficulty(workout_plan)
            },
            "tokens_used": 1500  # Example
        }
    
    async def stream_execute(self, request: AgentRequest):
        """
        Streaming implementation for real-time workout generation.
        
        The base class provides the streaming infrastructure.
        """
        training_data = TrainingRequest(**request.metadata)
        
        # Stream workout sections
        async for section in self._generate_workout_stream(training_data):
            yield self.format_stream_chunk(section)
    
    async def _generate_workout_stream(self, training_data: TrainingRequest):
        """Generate workout plan in streamable chunks."""
        # Warm-up section
        yield {
            "section": "warm_up",
            "content": await self._generate_warmup(training_data)
        }
        
        # Main workout
        yield {
            "section": "main_workout",
            "content": await self._generate_main_workout(training_data)
        }
        
        # Cool-down
        yield {
            "section": "cool_down",
            "content": await self._generate_cooldown(training_data)
        }
    
    def _estimate_calories(self, workout_plan: dict) -> int:
        """Estimate calories burned."""
        # Implementation details
        return 300
    
    def _calculate_difficulty(self, workout_plan: dict) -> float:
        """Calculate workout difficulty score."""
        # Implementation details
        return 7.5


# Example usage
async def main():
    """Example of using the new ADK-based agent."""
    
    # Initialize agent (all services are auto-configured)
    agent = TrainingAgent(
        personality_type="prime",  # For executive-focused responses
        max_tokens=2000,
        temperature=0.7
    )
    
    # Create request with automatic validation
    request = AgentRequest(
        prompt="Create a 45-minute HIIT workout for intermediate level",
        user_id="user_123",
        metadata={
            "workout_type": "HIIT",
            "fitness_level": "intermediate",
            "duration_minutes": 45,
            "equipment": ["dumbbells", "resistance_bands"],
            "goals": ["fat_loss", "endurance"],
            "restrictions": ["no_jumping"]
        }
    )
    
    # Execute with all the ADK benefits
    response = await agent.execute(request)
    
    # Response is automatically formatted and validated
    print(f"Success: {response.success}")
    print(f"Workout Plan: {response.content}")
    print(f"Processing Time: {response.processing_time}s")
    
    # Check agent health
    health = await agent.health_check()
    print(f"Agent Health: {health}")
    
    # Get metrics
    metrics = agent.get_metrics()
    print(f"Agent Metrics: {metrics}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


# Benefits of ADK Migration:
# 1. Reduced code by ~60% (from ~400 lines to ~150)
# 2. Automatic caching with decorators
# 3. Built-in circuit breaker for external services
# 4. Automatic retry with exponential backoff
# 5. Standardized request/response validation
# 6. Integrated health checks and metrics
# 7. Consistent error handling
# 8. Easy testing with ADK test utilities