"""
BLAZE Skills Module
===================

Modular skills for the BLAZE Elite Training Strategist agent.
Each skill is focused on a specific capability.
"""

from .training_plan_generation import TrainingPlanGenerationSkill
from .exercise_optimization import ExerciseOptimizationSkill
from .performance_analysis import PerformanceAnalysisSkill
from .recovery_protocol import RecoveryProtocolSkill
from .injury_prevention import InjuryPreventionSkill

__all__ = [
    "TrainingPlanGenerationSkill",
    "ExerciseOptimizationSkill", 
    "PerformanceAnalysisSkill",
    "RecoveryProtocolSkill",
    "InjuryPreventionSkill"
]